from flask import Blueprint, jsonify, request
from app.services import zoho_service, azure_service, parser_service, zoho_workdrive

receipts_bp = Blueprint("receipts", __name__)

@receipts_bp.route("/analyze", methods=["POST"])
def analyze_receipt():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        image_url = None
        if "resource_id" in data:
            resource_id = data["resource_id"]
            download_link = zoho_workdrive.create_zoho_workdrive_link(resource_id)
            if not download_link:
                return jsonify({"error": "Failed to get WorkDrive download link"}), 500
            image_url = download_link
        elif "image_url" in data:
            image_url = data["image_url"]

        else:
            return jsonify({"error": "Either 'image_url' or 'resource_id' must be provided."}), 400

        azure_result = azure_service.analyze_receipt(image_url)
        if "error" in azure_result:
            return jsonify({
                "error": "Azure analysis failed",
                "details": azure_result.get("details", azure_result)
            }), 502

        parsed_data = parser_service.extract_fields(azure_result, image_url)
        if "error" in parsed_data:
            return jsonify({
                "error": "Parsing failed",
                "details": parsed_data.get("error")
            }), 500

        required_fields = ["Vendor_Name", "Total_Amount", "Receipt_Date"]
        empty_fields = [f for f in required_fields if not parsed_data.get(f)]

        if not parsed_data or all(value in [None, "", 0, [], {}] for value in parsed_data.values()) or empty_fields:
            return jsonify({
                "error": "No valid receipt details detected in the image.",
                "details": f"Missing or empty fields: {', '.join(empty_fields) if empty_fields else 'No valid data found'}"
            }), 400
        print("Parsed Data:", parsed_data)

        status_code, zoho_response = zoho_service.create_record(parsed_data)
        if status_code != 200 or "error" in zoho_response:
            return jsonify({
                "error": "Failed to push record to Zoho Creator",
                "details": zoho_response
            }), 500

        return jsonify({
            "message": "Receipt processed successfully",
            # "download_link": image_url,
            # "parsed_data": parsed_data,
            "zoho_response": zoho_response
        }), 200

    except Exception as e:
        print("Error in /analyze route:", str(e))
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500
