from flask import request, jsonify
from flask_login import login_required
from app import db
from app.purchase import purchase
from app.models import Purchase,PurchaseItem
from datetime import datetime, timezone

@purchase.route('/add-purchase', methods=['POST'])
@login_required
def save_purchase():
    try:
        data = request.json
        
        supplier_name = data.get('supplier_name')
        purchase_date = data.get('purchase_date')
        purchase_number = data.get('purchase_number')
        mobile_number = data.get('mobile_number')
        products = data.get('products', [])
        total = data.get('total_price')
        paid = data.get('paid')
        created_by = data.get('created_by')
        location = data.get('location')
        
        if not supplier_name or not mobile_number:
            return jsonify({'message': 'Missing fields'}), 400
        
        # Convert 'total' and 'paid' to float to avoid type mismatch
        total = float(total) if total is not None else 0.0
        paid = float(paid) if paid is not None else 0.0
        
        # Calculate due amount
        due = total - paid
        payment_status = "Paid" if due <= 0 else "Pending"
        purchase = Purchase(
            supplier_name = supplier_name,
            purchase_date = purchase_date,
            purchase_number = purchase_number,
            mobile_number = mobile_number,
            total = total,
            paid = paid,
            payment_status = "Paid" if due <= 0 else "Pending",
            due = due,
            created_by = created_by,
            location = location
        )
        db.session.add(purchase)
        db.session.commit()
        
        for product in products:
            qty = int(product['qty'])
            price = float(product['price'])
            sub_total = float(product['sub_total'])
            
            purchase_item = PurchaseItem(
                purchase_id = purchase.id,
                product_name=product['name'],
                description=product['description'],
                quantity=qty,
                price=price,
                sub_total=sub_total,
                date = purchase_date,
                purchase_number=purchase_number
            )
            db.session.add(purchase_item)
        db.session.commit()
        return jsonify({"message": "Purchase saved successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error in save-quotation: {e}")
        return jsonify({"error": f"Internal server error {e}"}), 500


@purchase.route('/purchase-list', methods=['GET'])
@login_required
def purchase_list():
    try:
        purchases = Purchase.query.filter_by().all()
        if not purchases:
            return jsonify({"message": "No Purchase Available"}), 404
        
        purchases_list = [
            {
                "id": purchase.id,
                "supplier_name": purchase.supplier_name,
                "purchase_date": purchase.purchase_date,
                "purchase_number": purchase.purchase_number,
                "total": purchase.total,
                "paid": purchase.paid,
                "due": purchase.due,
                "payment_status": purchase.payment_status,
                "created_by": purchase.created_by
            }
            for purchase in purchases
        ]
        return jsonify({"purchase": purchases_list}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
    
@purchase.route('/due-purchase-payments/<int:id>', methods=['GET'])
@login_required
def due_purchase_payments(id):
    try:
        purchase_dues = Purchase.query.filter_by(id=id).first()
        response = purchase_dues.due
        print(response)
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": "An error occurred",
            "details": str(e)
        }), 500
        
@purchase.route('/update-due-purchase-payments/<int:id>', methods=['PUT'])
@login_required
def update_due_purchase_payments(id):
    try:
        data = request.get_json()
        print(data)
        purchase = Purchase.query.filter_by(id=id).first()
        
        if not purchase:
            return jsonify({"error": "Invoice not found"}), 404
        
        if data['due'] == 0:
            purchase.payment_status = "Paid"  # Corrected 'payemnt_status'
            purchase.paid += data['paid']
            purchase.due = data['due']
        else:
            purchase.due = data['due']
            purchase.paid += data['paid']
        
        db.session.commit()  # Don't forget to commit the changes to the DB
        return jsonify({"message": "Purchase Payments updated successfully"}), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred",
            "details": str(e)
        }), 500
        
@purchase.route('/purchase-details/<int:id>', methods=['GET'])
# @login_required
def purchase_details(id):
    try:
        # Fetch the quotation detail by ID
        purchase_detail = Purchase.query.filter_by(id=id).first()
        if not purchase_detail:
            return jsonify({"message": "No Purchase found"}), 404

        # Fetch all the items associated with the quotation
        purchase_product_detail = PurchaseItem.query.filter_by(purchase_id=id).all()

        # Format the data for the response
        products = [
            {
                "id": item.id,
                "product_name": item.product_name,
                "description": item.description,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.sub_total,  # Calculate subtotal dynamically
            }
            for item in purchase_product_detail
        ]

        # Build the response object
        response = {
            "supplier_name": purchase_detail.supplier_name,
            "purchase_number": purchase_detail.purchase_number,
            "mobile_number": purchase_detail.mobile_number,
            "date": purchase_detail.purchase_date,
            "products": products,
            "total": purchase_detail.total,
            "paid": purchase_detail.paid,
            "created_by": purchase_detail.created_by
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred",
            "details": str(e)
        }), 500
        
@purchase.route('/delete-purchase/<int:id>', methods=['DELETE'])
@login_required
def delete_purchase(id):
    try:
        purchase = Purchase.query.get_or_404(id)
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({'message': 'Purchase deleted successfully'}), 200
    except Exception as e:
        return jsonify({
            "error": "An error occurred",
            "details": str(e)
        }), 500