from flask import request, jsonify
from flask_login import login_required
from app import db
from app.sales import sales
from app.models import Inventory,Invoice, InvoiceItem
from app.inventory.routes import update_stock_internal, get_item_by_id
from datetime import datetime, timezone


# @sales.route('/save-invoice', methods=['POST'])
# @login_required
# def save_invoice():
#     try:
#         data = request.json

#         # Extract Invoice Details
#         customer_name = data.get('customer_name')
#         invoice_date = data.get('invoiceDate', datetime.now(timezone.utc))
#         invoice_number = data.get('invoiceNumber')
#         mobile_number = data.get('MobileNumber')
#         items = data.get('items', [])
#         total = float(data.get('total', 0))  # Ensure total is a float
#         paid = float(data.get('paid', 0))  # Amount already paid
#         created_by = data.get('createdBy', 'Admin')  # Default to 'Admin' if not provided
#         due = total - paid  # Calculate due amount
#         payment_status = "Paid" if due <= 0 else "Pending" # Set payment status
#         location = data.get('location')

#         # Create an Invoice instance
#         invoice = Invoice(
#             customer_name=customer_name,
#             invoice_date=invoice_date,
#             invoice_number=invoice_number,
#             mobile_number=mobile_number,
#             total=total,
#             paid=paid,
#             due=due,
#             payment_status=payment_status,
#             created_by=created_by,
#             location=location
#         )
#         db.session.add(invoice)
#         db.session.commit()  # Save the invoice to get its ID

#         # Process Items in Invoice
#         for item in items:
#             qty = int(item['qty'])  # Ensure quantity is an integer
#             selling_price = float(item['selling_price'])  # Ensure price is a float
#             subtotal = float(item['subtotal'])  # Ensure subtotal is a float

#             # Find the category by item ID
#             categories = get_item_by_id(item['item_id'])
#             if not categories:
#                 return jsonify({"error": f"Item with ID '{item['item_id']}' not found in inventory"}), 400

#             # Fetch the inventory item to get purchase price
#             inventory_item = Inventory.query.get(item['item_id'])
#             if not inventory_item:
#                 return jsonify({"error": f"Inventory item with ID {item['item_id']} not found"}), 400

#             # Create an InvoiceItem instance
#             invoice_item = InvoiceItem(
#                 invoice_id=invoice.id,
#                 item_id=item['item_id'],
#                 item_name=item['item_name'],
#                 description=item.get('description', ''),
#                 categories=categories,
#                 quantity=qty,
#                 selling_price=selling_price,
#                 subtotal=subtotal,
#                 profit=0.0,  # Initialize profit to 0 (it will be updated below)
#                 date=invoice_date
#             )

#             # Set the profit for this item
#             invoice_item.set_profit()  # Calculate and set profit before committing

#             db.session.add(invoice_item)

#             # Update Stock
#             stock_result, status_code = update_stock_internal(
#                 item_id=item['item_id'], quantity_sold=qty
#             )
#             if status_code != 200:
#                 db.session.rollback()
#                 return jsonify({"error": stock_result['error']}), status_code

#         db.session.commit()  # Commit all changes

#         return jsonify({"message": "Invoice saved successfully"}), 201

#     except Exception as e:
#         db.session.rollback()  # Rollback in case of any errors
#         print(f"Unexpected error in save-invoice: {e}")
#         return jsonify({"error": "Internal server error"}), 500

@sales.route('/save-invoice', methods=['POST'])
@login_required
def save_invoice():
    try:
        data = request.json

        # Extract Invoice Details
        customer_name = data.get('customer_name')
        invoice_date = data.get('invoiceDate', datetime.now(timezone.utc))
        invoice_number = data.get('invoiceNumber')
        mobile_number = data.get('MobileNumber')
        items = data.get('items', [])
        total = float(data.get('total', 0))  # Ensure total is a float
        paid = float(data.get('paid', 0))  # Amount already paid
        created_by = data.get('createdBy', 'Admin')  # Default to 'Admin' if not provided
        due = total - paid  # Calculate due amount
        payment_status = "Paid" if due <= 0 else "Pending"  # Set payment status
        location = data.get('location')

        # Create an Invoice instance (do not commit yet)
        invoice = Invoice(
            customer_name=customer_name,
            invoice_date=invoice_date,
            invoice_number=invoice_number,
            mobile_number=mobile_number,
            total=total,
            paid=paid,
            due=due,
            payment_status=payment_status,
            created_by=created_by,
            location=location
        )

        # Add the invoice to the session
        db.session.add(invoice)
        db.session.commit()  # Commit the invoice to generate its ID

        # Process Items in Invoice
        invoice_items = []
        for item in items:
            qty = int(item['qty'])  # Ensure quantity is an integer
            selling_price = float(item['selling_price'])  # Ensure price is a float
            subtotal = float(item['subtotal'])  # Ensure subtotal is a float

            # Find the category by item ID
            categories = get_item_by_id(item['item_id'])
            if not categories:
                return jsonify({"error": f"Item with ID '{item['item_id']}' not found in inventory"}), 400

            # Fetch the inventory item to get purchase price
            inventory_item = Inventory.query.get(item['item_id'])
            if not inventory_item:
                return jsonify({"error": f"Inventory item with ID {item['item_id']} not found"}), 400

            # Create an InvoiceItem instance, using the generated invoice ID
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,  # Now the invoice ID is valid
                item_id=item['item_id'],
                item_name=item['item_name'],
                description=item.get('description', ''),
                categories=categories,
                quantity=qty,
                selling_price=selling_price,
                subtotal=subtotal,
                profit=0.0,  # Initialize profit to 0 (it will be updated below)
                date=invoice_date
            )

            # Set the profit for this item
            invoice_item.set_profit()  # Calculate and set profit before adding

            invoice_items.append(invoice_item)

            # Update Stock
            stock_result, status_code = update_stock_internal(
                item_id=item['item_id'], quantity_sold=qty
            )
            if status_code != 200:
                # Rollback the transaction if stock update fails
                db.session.rollback()  # Ensure the invoice is also rolled back
                return jsonify({"error": stock_result['error']}), status_code

        # Add invoice items to the session after committing the invoice
        db.session.add_all(invoice_items)

        # Commit the entire transaction (invoice and items) in one go
        db.session.commit()

        return jsonify({"message": "Invoice saved successfully"}), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of any errors
        print(f"Unexpected error in save-invoice: {e}")
        return jsonify({"error": "Internal server error"}), 500



@sales.route('/invoice-list', methods=['GET'])
@login_required
def invoice_list():
    try:
        invoices = Invoice.query.filter_by().all()
        if not invoices:
            return jsonify({"message": "No invoices"}), 404

        invoices_list = [
            {
                "id": invoice.id,
                "client_name": invoice.customer_name,
                "invoice_date": invoice.invoice_date,
                "invoice_number": invoice.invoice_number,
                "total": invoice.total,
                "paid": invoice.paid,
                "due": invoice.due,
                "payment_status": invoice.payment_status,
                "created_by": invoice.created_by
            }
            for invoice in invoices
        ]
        return jsonify({"invoice": invoices_list}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@sales.route('/invoice-details/<int:id>', methods=['GET'])
@login_required
def invoice_details(id):
    try:
        # Fetch the quotation detail by ID
        invoice_detail = Invoice.query.filter_by(id=id).first()
        if not invoice_detail:
            return jsonify({"message": "No invoice found"}), 404

        # Fetch all the items associated with the quotation
        invoice_product_detail = InvoiceItem.query.filter_by(invoice_id=id).all()

        # Format the data for the response
        products = [
            {
                "id": item.id,
                "product_name": item.item_name,
                "description": item.description,
                "quantity": item.quantity,
                "price": item.selling_price,
                "subtotal": item.subtotal,  # Calculate subtotal dynamically
            }
            for item in invoice_product_detail
        ]

        # Build the response object
        response = {
            "customer_name": invoice_detail.customer_name,
            "invoice_number": invoice_detail.invoice_number,
            "mobile_number": invoice_detail.mobile_number,
            "date": invoice_detail.invoice_date,
            "products": products,
            "total": invoice_detail.total,
            "paid": invoice_detail.paid,
            "created_by": invoice_detail.created_by
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred",
            "details": str(e)
        }), 500