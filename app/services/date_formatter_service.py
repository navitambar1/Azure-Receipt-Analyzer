from datetime import datetime

def format_receipt_date(date_str):
    """
    Convert dates like '5/1/2025', '2025-05-01', or '05/01/25'
    into '01-May-2025' for Zoho Creator compatibility.
    """
    if not date_str:
        return ""

    date_formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%y", "%d-%m-%Y"]
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%d-%b-%Y")
        except ValueError:
            continue

    return date_str