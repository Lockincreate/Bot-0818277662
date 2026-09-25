import os, requests, json
from flask import Flask, request, jsonify

app = Flask(__name__)

SIMCLOUD_API_KEY = "04d58c97f6421349456c61070959c4b870184ed38a11340dbd45385edbb3f1dd"
SIMCLOUD_BASE = "https://simcloud.co.za/api"

def buy_data(network, phone, bundle):
    url = f"{SIMCLOUD_BASE}/data_recharge.php"
    payload = {
        "api_key": SIMCLOUD_API_KEY,
        "network": network.lower(),
        "phone": phone,
        "bundle": bundle,
        "reference": "0818277662"
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def buy_airtime(network, phone, amount):
    url = f"{SIMCLOUD_BASE}/airtime_recharge.php"
    payload = {
        "api_key": SIMCLOUD_API_KEY,
        "network": network.lower(),
        "phone": phone,
        "amount": amount
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_balance():
    url = f"{SIMCLOUD_BASE}/balance.php"
    try:
        r = requests.get(url, params={"api_key": SIMCLOUD_API_KEY}, timeout=15)
        return r.text
    except Exception as e:
        return str(e)

@app.route("/", methods=["GET"])
def home():
    bal = check_balance()
    return f"0818277662 BOT LIVE - Balance: {bal}"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge", "OK")

    data = request.json
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        sender = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except:
        return jsonify({"status": "ok"})

    m = msg.lower()
    if "balance" in m:
        reply = f"Balance: {check_balance()}"
    elif "telkom" in m or "mtn" in m or "vodacom" in m or "cellc" in m:
        parts = m.split()
        net = parts[0]
        phone = parts[1] if len(parts)>1 else sender
        bundle = parts[2] if len(parts)>2 else "1000"
        result = buy_data(net, phone, bundle)
        reply = f"Order {net} {phone} {bundle}: {json.dumps(result)}"
    else:
        reply = "Welcome! Send:\ntelkom 0812345678 1gb\nmtn 0812345678 500mb\nvodacom 0812345678 R20"

    # SEND REPLY VIA WHATSAPP API HERE
    print(reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
