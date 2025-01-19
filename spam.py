import requests
from difflib import SequenceMatcher
from urllib.parse import urlparse

# Trusted payment domains list
TRUSTED_DOMAINS = [
    "paypal.com", "razorpay.com", "payoneer.com", "stripe.com", "squareup.com",
    "venmo.com", "zellepay.com", "adyen.com", "authorize.net", "skrill.com",
    "2checkout.com", "alipay.com", "wepay.com", "klarna.com", "afterpay.com",
    "google.com/pay", "apple.com/apple-pay", "cash.app", "revolut.com",
    "transferwise.com", "paytm.com", "phonepe.com", "billdesk.com", "instamojo.com",
    "ccavenue.com", "worldpay.com", "braintreepayments.com", "dwolla.com",
    "bluepay.com", "payza.com", "checkout.com", "qiwi.com", "yandex.com",
    "mercadopago.com", "pagseguro.uol.com.br", "payu.com", "trustly.com", "sezzle.com",
    "shopify.com/payments", "fastspring.com", "flutterwave.com", "moneris.com",
    "ipay88.com", "shopeepay.com", "payline.com", "payplug.com", "coinbase.com",
    "binance.com", "blockchain.com", "bitpay.com", "cryptopay.me", "paxful.com",
]

# Function to check URL with VirusTotal
def check_virustotal(url, api_key):
    api_url = "https://www.virustotal.com/vtapi/v2/url/report"
    params = {"apikey": api_key, "resource": url}
    try:
        response = requests.get(api_url, params=params)
        result = response.json()
        if response.status_code == 200 and "positives" in result and "total" in result:
            return {
                "source": "VirusTotal",
                "positives": result["positives"],
                "total": result["total"],
                "url": url,
            }
        else:
            return {"source": "VirusTotal", "error": result.get("verbose_msg", "Unknown error")}
    except Exception as e:
        return {"source": "VirusTotal", "error": str(e)}

# Function to check URL with Google Safe Browsing
def check_google_safe_browsing(url, api_key):
    api_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    headers = {"Content-Type": "application/json"}
    payload = {
        "client": {"clientId": "your_client_id", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, params={"key": api_key})
        result = response.json()
        if response.status_code == 200:
            if "matches" in result:
                return {"source": "Google Safe Browsing", "threats": result["matches"]}
            else:
                return {"source": "Google Safe Browsing", "threats": []}
        else:
            return {"source": "Google Safe Browsing", "error": result.get("error", {}).get("message", "Unknown error")}
    except Exception as e:
        return {"source": "Google Safe Browsing", "error": str(e)}

# Function to check for typo-squatted domains
def is_typo_squatted(url, trusted_domains):
    domain = urlparse(url).netloc
    for trusted in trusted_domains:
        similarity = SequenceMatcher(None, domain, trusted).ratio()
        if similarity > 0.8: 
            print(f"⚠️ Possible typo-squatted domain detected: {domain} (similar to {trusted})")
            return True
    return False

# Main function to check URL with both APIs and heuristic
def check_url(url):
    vt_api_key = "3a68df74b219bbc45d96a3cedf81ee6863a9ff3edd570f748098d343fa16b681"
    gsb_api_key = "**************"  # hidden due to security reasons

    print(f"🔗 Checking URL: {url}")

    # Check for typo-squatted domains
    if is_typo_squatted(url, TRUSTED_DOMAINS):
        print(f"❌ The URL '{url}' is potentially a SPAM! (Typo-Squatting)")
        return

    # VirusTotal result
    vt_result = check_virustotal(url, vt_api_key)
    vt_is_malicious = False
    if "error" not in vt_result:
        print(f"🚨 Malicious detections: {vt_result['positives']}/{vt_result['total']}")
        if vt_result["positives"] > 0:
            vt_is_malicious = True
    else:
        print(f"Error: {vt_result['error']}")

    # Google Safe Browsing result
    gsb_result = check_google_safe_browsing(url, gsb_api_key)
    gsb_is_malicious = False
    if "error" not in gsb_result:
        if gsb_result["threats"]:
            print("🚨 Threats found")
        else:
            print("✅ No threats detected.")
    else:
        print(f"[Google Safe Browsing] Error: {gsb_result['error']}")

    if vt_is_malicious or gsb_is_malicious:
        print(f"❌ The URL '{url}' is a SPAM!")
    else:
        print(f"✅ The URL '{url}' is SAFE.")

if __name__ == "__main__":
    url = input("Enter the URL to check: ")
    check_url(url)
