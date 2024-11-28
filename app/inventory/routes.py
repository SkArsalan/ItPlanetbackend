from flask import request, jsonify
from flask_login import login_required
from app import db
from app.inventory import inventory
from app.models import Inventory


@inventory.route('/add', methods=['POST'])
@login_required  # Use Flask-Login for session-based authentication
def add_inventory():
    data = request.get_json()
    product_name = data.get('product_name')
    description = data.get('description')
    quantity = data.get('quantity')
    status = data.get('status')
    price = data.get('price')
    categories = data.get('categories')
    location = data.get('location')

    # Validation
    if not product_name or not price or quantity is None:
        return jsonify({'message': 'Missing fields'}), 400

    # Create and add new inventory item
    item = Inventory(
        product_name=product_name,
        description=description,
        price=price,
        quantity=quantity,
        location=location,
        status=status,
        categories=categories,
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': "Item added successfully"}), 201


@inventory.route('/update/<int:item_id>', methods=['PUT'])
@login_required  # Use Flask-Login for session-based authentication
def update_inventory(item_id):
    data = request.get_json()

    # Retrieve inventory item
    item = Inventory.query.get_or_404(item_id)

    # Update fields if provided in the request, else keep existing value
    item.product_name = data.get('product_name', item.product_name)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    item.quantity = data.get('quantity', item.quantity)
    item.location = data.get('location', item.location)
    item.status = data.get('status', item.status)
    item.categories = data.get('categories', item.categories)

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'Item updated successfully'}), 200


@inventory.route('/delete/<int:item_id>', methods=['DELETE'])
@login_required  # Use Flask-Login for session-based authentication
def delete_inventory(item_id):
    # Retrieve inventory item
    item = Inventory.query.get_or_404(item_id)

    # Delete the item from the database
    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Item deleted successfully'}), 200

@inventory.route('/item/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    #Retrive inventory item
    item = Inventory.query.get_or_404(item_id)
    
    product_name = item.product_name
    description = item.description
    price = item.price
    quantity = item.quantity
    location = item.location
    status = item.status
    categories = item.categories
    
    return jsonify({"product_name":product_name, "description":description, "price":price, 
                    "quantity":quantity, "location":location, "status":status, "categories":categories}), 200

@inventory.route('/list', methods=['GET'])
@login_required  # Use Flask-Login for session-based authentication
def list_inventory():
    # Retrieve all inventory items
    items = Inventory.query.all()

    # Create a list of dictionaries to represent each item
    inventory_list = [
        {
            "id": item.id,
            "product_name": item.product_name,
            "description": item.description,
            "price": item.price,
            "quantity": item.quantity,
            "location": item.location,
            "status": item.status,
            "categories": item.categories,
        }
        for item in items
    ]

    # Return the list of inventory items in JSON format
    return jsonify({'inventory': inventory_list}), 200
