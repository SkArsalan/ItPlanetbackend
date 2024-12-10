from flask import request, jsonify
from flask_login import login_required
from app import db
from app.sales import sales
from app.models import Invoice, InvoiceItem
from app.inventory.routes import update_stock_internal, get_item_id_by_name
from datetime import datetime, timezone
import requests

@sales.route('/save-invoice', methods=['POST'])
@login_required
def save_invoice():
    try:
        data = request.json

        # Extract Invoice Details
        client_name = data.get('clientName')
        invoice_date = data.get('invoiceDate', datetime.now(timezone.utc))
        invoice_number = data.get('invoiceNumber')
        mobile_number = data.get('MobileNumber')
        items = data.get('items', [])
        total = float(data.get('total', 0))  # Ensure total is a float
        paid = float(data.get('paid', 0))  # Amount already paid
        created_by = data.get('createdBy', 'Admin')  # Default to 'Admin' if not provided
        due = total - paid  # Calculate due amount
        payment_status = "Paid" if due <= 0 else "Pending"  # Set payment status

        # Create an Invoice instance
        invoice = Invoice(
            client_name=client_name,
            invoice_date=invoice_date,
            invoice_number=invoice_number,
            mobile_number=mobile_number,
            total=total,
            paid=paid,
            due=due,
            payment_status=payment_status,
            created_by=created_by
        )
        db.session.add(invoice)
        db.session.commit()  # Save the invoice to get its ID

        # Process Items in Invoice
        for item in items:
            qty = int(item['qty'])  # Ensure quantity is an integer
            price = float(item['price'])  # Ensure price is a float
            subtotal = float(item['subtotal'])  # Ensure subtotal is a float

            # Find the item_id by item_name
            item_id, category = get_item_id_by_name(item['item_name'])
            if not item_id:
                return jsonify({"error": f"Item with name '{item['item_name']}' not found in inventory"}), 400

            # Create an InvoiceItem instance
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item_id,
                item_name=item['item_name'],
                description=item.get('description', ''),
                category=category,
                qty=qty,
                price=price,
                subtotal=subtotal,
                date=invoice_date
            )
            db.session.add(invoice_item)

            # Update Stock
            stock_result, status_code = update_stock_internal(
                item_id=item_id, item_name=item['item_name'], quantity_sold=qty
            )
            if status_code != 200:
                db.session.rollback()
                return jsonify({"error": stock_result['error']}), status_code

        db.session.commit()  # Commit all changes

        return jsonify({"message": "Invoice saved successfully"}), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of any errors
        print(f"Unexpected error in save-invoice: {e}")
        return jsonify({"error": "Internal server error"}), 500
