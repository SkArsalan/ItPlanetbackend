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

# @inventory.route('/update-stock', methods=['PUT'])
# @login_required
# def update_stock():
#     try:
#         data = request.get_json()
#         if not data:
#             print("No data received in the request")
#             return jsonify({"error": "Invalid JSON payload"}), 400

#         item_name = data.get("itemName")
#         quantity_sold = data.get("quantitySold")

#         # Validate fields
#         if not item_name or quantity_sold is None:
#             print(f"Invalid fields: {data}")
#             return jsonify({"error": "Missing 'itemName' or 'quantitySold'"}), 400

#         if not isinstance(quantity_sold, int) or quantity_sold <= 0:
#             print(f"Invalid quantitySold: {quantity_sold}")
#             return jsonify({"error": "'quantitySold' must be a positive integer"}), 400

#         # Fetch the item from the database
#         item = Inventory.query.filter_by(product_name=item_name).first()
#         if not item:
#             print(f"Item not found: {item_name}")
#             return jsonify({"error": f"Item '{item_name}' not found"}), 404

#         # Check stock availability
#         if item.quantity < quantity_sold:
#             print(f"Insufficient stock for {item_name}: {item.quantity} available, {quantity_sold} requested")
#             return jsonify({"error": "Insufficient stock"}), 400

#         # Deduct stock
#         item.quantity -= quantity_sold
#         db.session.commit()

#         return jsonify({"message": "Stock updated successfully", "newStock": item.quantity}), 200

#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return jsonify({"error": "Internal server error"}), 500


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

@inventory.route('/list/<string:location>', methods=['GET'])
@login_required
def list_inventory(location):

    # Retrieve inventory items filtered by location
    items = Inventory.query.filter_by(location=location).all()

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
        for item in items if item.quantity > 0
    ]

    return jsonify({'inventory': inventory_list}), 200

def update_stock_internal(item_id=None, item_name=None, quantity_sold=None):
    """
    Updates the stock for a given item directly in the database.

    Args:
        item_id (int): ID of the item to update.
        item_name (str): Name of the item to update.
        quantity_sold (int): Quantity to deduct from stock.

    Returns:
        dict: A result dictionary with "success" or "error".
    """
    try:
        # Ensure at least one of item_id or item_name is provided
        if not item_id and not item_name:
            return {"error": "Either item_id or item_name must be provided"}, 400

        # Fetch the item based on item_id or item_name
        item = None
        if item_id:
            item = Inventory.query.filter_by(id=item_id).first()
        if not item and item_name:
            item = Inventory.query.filter_by(product_name=item_name).first()

        if not item:
            return {"error": f"Item '{item_name or item_id}' not found"}, 404

        # Check stock availability
        if item.quantity < quantity_sold:
            return {"error": "Insufficient stock"}, 400

        # Deduct stock
        item.quantity -= quantity_sold
        db.session.add(item)
        db.session.commit()

        return {"success": f"Stock updated for '{item_name or item_id}'", "newStock": item.quantity}, 200
    except Exception as e:
        print(f"Error in update_stock_internal: {e}")
        return {"error": "Internal server error"}, 500

def get_item_id_by_name(item_name):
    """
    Finds the item ID based on the item name from the inventory.
    
    Args:
        item_name (str): The name of the item to find.
    
    Returns:
        int: The item ID if found, None otherwise.
    """
    try:
        # Query the Inventory table to find the item by name
        item = Inventory.query.filter_by(product_name=item_name).first()
        if item:
            return item.id, item.categories
        else:
            return None
    except Exception as e:
        print(f"Error finding item by name: {e}")
        return None
