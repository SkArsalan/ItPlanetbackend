from flask import request, jsonify
from flask_login import login_required
from app import db
from app.section import section
from app.models import Section

@section.route('/get-sections', methods=['GET'])
@login_required
def get_sections():
    try:
        pages = Section.query.all()
        if not pages:
            return jsonify({"message": "no sections"}), 404
        
        pages_list = [
            {
                "id": element.id,
                "categories": element.categories,
            }
            for element in pages
        ]
        return jsonify({"pages": pages_list}), 200
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500