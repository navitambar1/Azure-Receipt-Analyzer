import requests, time
from app.utils.config import get_env

AZURE_ENDPOINT = get_env("AZURE_ENDPOINT")
AZURE_KEY = get_env("AZURE_KEY")

def analyze_receipt(image_url):
    try:
        analyze_url = f"{AZURE_ENDPOINT}/formrecognizer/v2.1/prebuilt/receipt/analyze?includeTextDetails=true"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_KEY,
            "Content-Type": "application/json"
        }

        payload = {"url": image_url}
        response = requests.post(analyze_url, headers=headers, json=payload)

        if response.status_code != 202:
            return {"error": f"Failed to start analysis", "details": response.text}

        result_url = response.headers.get("Operation-Location")
        if not result_url:
            return {"error": "Missing Operation-Location in response"}

        for _ in range(10):  
            time.sleep(2)
            result_response = requests.get(result_url, headers={"Ocp-Apim-Subscription-Key": AZURE_KEY})
            result_json = result_response.json()
            status = result_json.get("status")

            if status == "succeeded":
                return result_json
            elif status == "failed":
                return {"error": "Analysis failed", "details": result_json}

        return {"error": "Timeout waiting for Azure analysis"}

    except Exception as e:
        return {"error": str(e)}