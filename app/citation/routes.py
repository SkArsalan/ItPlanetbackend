from flask import request, jsonify
from flask_login import login_required
from app import db
from app.citation import citation
from app.models import Quotation, QuotationItem
from datetime import datetime, timezone

@citation.route('/add-citation', methods=['POST'])
@login_required
def save_citation():
    try:
        data = request.json
        
        customer_name = data.get('CustomerName')
        quotation_date = data.get('quotationDate', datetime.now(timezone.utc))
        quotation_number = data.get('quotationNumber')
        mobile_number = data.get('mobileNumber')
        categories = data.get('categories')
        products = data.get('products',[])
        total = data.get('totalPrice')
        created_by = data.get('createdBy')
        location = data.get('location')
        
        if not customer_name or not mobile_number or not categories:
            return jsonify({'message': 'Missing fields'}), 400
        
        quotation = Quotation(
            customer_name = customer_name,
            quotation_date = quotation_date,
            quotation_number = quotation_number,
            mobile_number = mobile_number,
            categories=categories,
            total = total,
            created_by=created_by,
            location = location
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
        print(f"Unexpected error in save-quotation: {e}")
        return jsonify({"error": f"Internal server error {e}"}), 500