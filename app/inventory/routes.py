
from flask import request, jsonify, abort
from flask_login import login_required
from app import db
from app.inventory import inventory
from app.models import Inventory
from datetime import datetime, timezone


def get_item_or_404(item_id):
    item = Inventory.query.get_or_404(item_id)
    return item


def get_inventory_list(location, categories):
    # Start filtering by location
    query = Inventory.query.filter_by(location=location)
    
    # If categories is provided, filter by categories as well
    if categories:
        query = query.filter_by(categories=categories)
    
    # Filter by quantity > 0
    query = query.filter(Inventory.quantity > 0)
    
    # Execute the query and return the results
    return query.all()


@inventory.route('/add', methods=['POST'])
@login_required
def add_inventory():
    data = request.get_json()
    required_fields = ['product_name', 'selling_price', 'quantity']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'message': 'Missing required field'}), 400

    inventory_date = data.get('date', datetime.now(timezone.utc))

    item = Inventory(
        product_name=data['product_name'],
        description=data.get('description'),
        purchase_price=data.get('purchase_price'),
        selling_price=data['selling_price'],
        quantity=data['quantity'],
        location=data.get('location'),
        status=data.get('status'),
        categories=data.get('categories'),
        date=inventory_date
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': 'Item added successfully'}), 201


@inventory.route('/update/<int:item_id>', methods=['PUT'])
@login_required
def update_inventory(item_id):
    data = request.get_json()
    item = get_item_or_404(item_id)

    for field, value in data.items():
        if value is not None:
            setattr(item, field, value)

    db.session.commit()
    return jsonify({'message': 'Item updated successfully'}), 200


@inventory.route('/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory(item_id):
    item = get_item_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'}), 200


@inventory.route('/item/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    item = get_item_or_404(item_id)
    item_data = {
        "product_name": item.product_name,
        "description": item.description,
        "selling_price": item.selling_price,
        "quantity": item.quantity,
        "location": item.location,
        "status": item.status,
        "categories": item.categories,
        "purchase_price": item.purchase_price
    }
    return jsonify(item_data), 200

@inventory.route('/list/<string:location>', methods=['GET'])
@inventory.route('/list/<string:location>/<string:categories>', methods=['GET'])
@login_required
def list_inventory(location, categories=None):
    
    items = get_inventory_list(location, categories)
    inventory_list = [
        {
            "id": item.id,
            "product_name": item.product_name,
            "description": item.description,
            "purchase_price": item.purchase_price,
            "selling_price": item.selling_price,
            "quantity": item.quantity,
            "location": item.location,
            "status": item.status,
            "categories": item.categories,
        }
        for item in items
    ]
    return jsonify({'inventory': inventory_list}), 200


def update_stock_internal(item_id, quantity_sold):
    """
    Updates the stock for a given item directly in the database.
    """
    try:
        if item_id is None or quantity_sold is None or quantity_sold <= 0:
            abort(400, description="Invalid item_id or quantity_sold")

        item = Inventory.query.get_or_404(item_id)
        if item.quantity < quantity_sold:
            abort(400, description="Insufficient stock")

        item.quantity -= quantity_sold
        db.session.commit()

        return {"success": f"Stock updated for item ID '{item_id}'", "newStock": item.quantity}, 200
    except Exception as e:
        print(f"Error in update_stock_internal: {e}")
        abort(500, description="Internal server error")


def get_item_by_id(item_id):
    """
    Finds the category of an item by its ID from the inventory.
    """
    try:
        item = Inventory.query.get(item_id)
        return item.categories if item else None
    except Exception as e:
        print(f"Error finding item by ID: {e}")
        return None