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

@quotation.route('/quotation-list/<string:location>')
@login_required
def quotation_list(location):
    try:
        quotations = Quotation.query.filter_by(location=location).all()
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