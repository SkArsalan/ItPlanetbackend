from flask import request, jsonify
from flask_login import login_required
from app import db
from app.quotation import quotation
from app.models import Quotation, QuotationItem
from datetime import datetime, timezone

@quotation.route('/add-quotation', methods=['POST'])
@login_required
def add_quotation():
    try:
        data = request.json
        print(data)
        #Extract quotation Details
        customer_name = data.get('CustomerName')
        quotation_number = data.get('quotationNumber')
        mobile_number = data.get('mobileNumber')
        quotation_date = data.get('quotationDate')
        categories = data.get('categories')
        products = data.get('products', [])
        total = data.get('totalPrice')
        created_by = data.get('createdBy')
        location = data.get('location')
        
        if not customer_name or not mobile_number or not categories:
            return jsonify({'message': 'Missing fields'}), 400
        #Create an Quotation instance
        quotation = Quotation(
            customer_name=customer_name,
            quotation_number=quotation_number,
            categories=categories,
            mobile_number=mobile_number,
            quotation_date=quotation_date,
            total=total,
            created_by=created_by,
            location=location
        )
        db.session.add(quotation)
        db.session.commit()
        
        for product in products:
            qty = int(product['qty'])
            price = float(product['price'])
            sub_total = float(product['sub_total'])
            
            quotation_item = QuotationItem(
                quotation_id =quotation.id,
                product_name=product['name'],
                description=product['description'],
                quantity=qty,
                price=price,
                sub_total=sub_total,
                date=quotation_date,
                quotation_number=quotation_number
            )
            db.session.add(quotation_item)
        db.session.commit()
        return jsonify({"message": "Quotation save successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@quotation.route('/quotation-list/<string:location>/<string:categories>')
@login_required
def quotation_list(location, categories):
    try:
        quotations = Quotation.query.filter_by(location=location, categories=categories).all()
        if not quotations:
            return jsonify({"message": "No Quotations"}), 404
        
        quotations_list = [{
            "id" : element.id,
            "customer_name": element.customer_name,
            "quotation_number": element.quotation_number,
            "mobile_number": element.mobile_number,
            "quotation_date": element.quotation_date,
            "total" : element.total,
            "created_by": element.created_by
        }
        for element in quotations
        ]
        return jsonify({"quotation": quotations_list}), 200
    
    except Exception as e:
        return jsonify({
            "error" :"An error occurred", "details": str(e)
        }), 500
        
@quotation.route('/quotation-details/<int:id>', methods=['GET'])
@login_required
def quotation_details(id):
    try:
        # Fetch the quotation detail by ID
        quotation_detail = Quotation.query.filter_by(id=id).first()
        if not quotation_detail:
            return jsonify({"message": "No Quotation found"}), 404

        # Fetch all the items associated with the quotation
        quotation_product_detail = QuotationItem.query.filter_by(quotation_id=id).all()

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
            for item in quotation_product_detail
        ]

        # Build the response object
        response = {
            "customer_name": quotation_detail.customer_name,
            "quotation_number": quotation_detail.quotation_number,
            "mobile_number": quotation_detail.mobile_number,
            "date": quotation_detail.quotation_date,
            "products": products,
            "total": quotation_detail.total,
            "created_by": quotation_detail.created_by
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred",
            "details": str(e)
        }), 500

@quotation.route('/delete-quotation/<int:id>', methods=['DELETE'])
@login_required
def delete_quotation(id):
    quotation = Quotation.query.get_or_404(id)
    db.session.delete(quotation)
    db.session.commit()
    return jsonify({'message': 'Quotation deleted successfully'}), 200