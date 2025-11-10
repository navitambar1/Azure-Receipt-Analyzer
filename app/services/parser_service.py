import re
from app.services.date_formatter_service import format_receipt_date

def extract_fields(result, image_url=None):
    try:
        analyze = result.get("analyzeResult", {})
        documents = analyze.get("documents", [])

        if documents:
            doc = documents[0]
            fields = doc.get("fields", {})
            vendor = fields.get("MerchantName", {}).get("valueString", "")
            date = fields.get("TransactionDate", {}).get("valueDate", "")
            total = fields.get("Total", {}).get("valueNumber", 0.0)
            items = fields.get("Items", {}).get("valueArray", [])

            line_items = []
            for item in items: 
                i = item.get("valueObject", {})
                name = i.get("Description", {}).get("valueString", "")
                qty = i.get("Quantity", {}).get("valueNumber", 1)
                unit = i.get("UnitPrice", {}).get("valueNumber", i.get("TotalPrice", {}).get("valueNumber", 0.0))
                total_price = i.get("TotalPrice", {}).get("valueNumber", unit * qty)
                if name:
                    line_items.append({
                        "Item_Name": name.strip(),
                        "Quantity": qty,
                        "Unit_Price": unit,
                        "Total_Price": total_price
                    })

            category = "Food" if any(x in vendor.lower() for x in ["grill", "food", "cafe", "pub", "restaurant", "bar"]) else "Others"
            return {
                "Vendor_Name": vendor,
                "Receipt_Date": format_receipt_date(date),
                "Total_Amount": total,
                "Category": category,
                "Line_Items": line_items,
                "Processed_Status": "Processed",
                "Receipt_Image": image_url
            }

        raw_text = []
        for page in analyze.get("readResults", []):
            for line in page.get("lines", []):
                raw_text.append(line.get("text", ""))
        extracted_text = "\n".join(raw_text) or result.get("Extracted_Text", "")
        lines = [l.strip() for l in extracted_text.split("\n") if l.strip()]

        vendor_candidates = []
        for l in lines[:5]:
            if re.search(r"(Table|Check|Trans|#|Serv|Server)", l, re.IGNORECASE):
                break
            vendor_candidates.append(l)
        vendor = " ".join(vendor_candidates).strip()

        date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", extracted_text)
        date = date_match.group(1) if date_match else ""

        subtotal_match = re.search(r"(?:Subtotal|Net\s*Total|Sub\s*Total)[:\s]*\$?\s*([\d,.]+)", extracted_text, re.IGNORECASE)
        tax_match = re.search(r"(?:GST|Tax|Sales\s*Tax|VAT)[:\s]*\$?\s*([\d,.]+)", extracted_text, re.IGNORECASE)
        total_match = re.search(r"(?:Total|Amount\s*Due|Grand\s*Total)[:\s]*\$?\s*([\d,.]+)", extracted_text, re.IGNORECASE)

        subtotal = float(subtotal_match.group(1).replace(",", "")) if subtotal_match else 0.0
        tax = float(tax_match.group(1).replace(",", "")) if tax_match else 0.0
        total = float(total_match.group(1).replace(",", "")) if total_match else round(subtotal + tax, 2)

        item_pattern = re.compile(
            r"(?P<qty>\d{1,3})\s+(?P<desc>[A-Za-z0-9\(\)\s\.\-/&]+?)\s+\$?\s*(?P<price>\d+\.\d{2})",
            re.IGNORECASE
        )

        line_items = []
        for match in item_pattern.finditer(extracted_text):
            desc = match.group("desc").strip()
            if re.search(r"(total|tax|gst|subtotal|amount)", desc, re.IGNORECASE):
                continue
            qty = int(match.group("qty"))
            price = float(match.group("price"))
            total_price = round(qty * price, 2)
            line_items.append({
                "Item_Name": desc,
                "Quantity": qty,
                "Unit_Price": price,
                "Total_Price": total_price
            })

        if not line_items:
            simple_pattern = re.compile(r"([A-Za-z].+?)\s+\$?(\d+\.\d{2})")
            for m in simple_pattern.finditer(extracted_text):
                desc, price = m.groups()
                if re.search(r"(total|tax|gst|amount)", desc, re.IGNORECASE):
                    continue
                line_items.append({
                    "Item_Name": desc.strip(),
                    "Quantity": 1,
                    "Unit_Price": float(price),
                    "Total_Price": float(price)
                })

        unique_items = []
        seen = set()
        for i in line_items:
            if i["Item_Name"].lower() not in seen:
                unique_items.append(i)
                seen.add(i["Item_Name"].lower())

        category = "Food" if any(x in extracted_text.lower() for x in ["burger", "grill", "pub", "restaurant", "cafe", "food", "bar"]) else "Others"

        final_result = {
            "Agent_Name": "Test_Agent",
            "Vendor_Name": vendor,
            "Receipt_Date": format_receipt_date(date),
            "Subtotal": subtotal,
            "Tax": tax,
            "Total_Amount": subtotal + tax,
            "Category": category,
            "Line_Items": unique_items,
            "Processed_Status": "Processed",
            "Receipt_Image": image_url
        }
        return final_result

    except Exception as e:
        return {"error": str(e)}
