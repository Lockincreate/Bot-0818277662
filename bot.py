from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# REMEMBER CUSTOMER
sessions = {}

# REPLIES
MENU = """Hello! Welcome to 1Data by Hello Data SA™ - founder: sss™

R5 is R5 ✅ - No extra fees!

⚡ Electricity - Reply 1
💧 Water (eThekwini) - Reply 2
📱 Airtime - Reply 3
📊 Data Domination - Reply 4
🏪 Shop Bulk - Reply 5
📄 Manual Paper - Reply 6

Send your meter number & amount to start!

We're online 24/7!

1Data by Hello Data SA™ - founder: sss™
R5 is R5 - IT IS WHAT IT IS ✅"""

REPLIES = {
"elec_meter": "⚡ Electricity - All SA - sss™\nSend your meter number (11 digits)\nEx: 070123456789\n\nR5 is R5 ✅",
"water_meter": "💧 Water - eThekwini / Durban\nSend meter number + Amount\nEx: 0123456789 R100\n\nR5 is R5 ✅",
"data_menu": "📱 DOMINATION DATA - sss™\nWhy Pay More?\n\nMTN 1GB R85 → Our R45\nMTN 5GB R299 → Our R120\nVoda 10GB R529 → Our R160\n20GB R799 → Our R240\n\nSend: Phone + Package\nEx: 0812345678 1GB R45\nEx: 0812345678 5GB R120\n\nR5 is R5 ✅",
"shop": "🏪 SHOP / SPAZA WHOLESALE - sss™\nOur R45 → Sell R55 Profit R10\nOur R120 → Sell R149 Profit R29\nOur R160 → Sell R199 Profit R39\nOur R240 → Sell R279 Profit R39\n\nStill cheaper than MTN!\nBulk:\n100+ = R2 off\n500+ = R4 off\n1000+ = R6 off\n\nSend bulk order: Ex: 100x 1GB\n\n📄 Manual paper voucher ALLOWED - hand-held YES!\nTymeBank 0818277662\nR5 is R5 ✅"
}

def get_reply(from_id, text_raw):
    text = text_raw.strip().lower()
    raw = text_raw.strip()

    if from_id not in sessions:
        sessions[from_id] = {"step":"menu","meter":None,"amount":None,"phone":None}

    s = sessions[from_id]

    # FIND NUMBERS
    meter_match = re.search(r'\d{11,13}', raw)
    phone_match = re.search(r'0\d{9}', raw)
    amount_match = re.search(r'r?\s*(\d+)', raw, re.I)
    gb_match = re.search(r'\d+gb', raw, re.I)

    # === STEP: MENU ===
    if s["step"] == "menu":
        if text == "1" or "electric" in text or (meter_match and not phone_match):
            # if they sent meter directly
            if meter_match:
                s["meter"] = meter_match.group(0)
                s["step"] = "elec_amount"
                return f"✅ Meter saved: {s['meter']}\n\nHow much electricity?\nReply: R50 / R100 / R200 / R500\nEx: R200\nR5 is R5 ✅ - sss™"
            else:
                s["step"] = "elec_meter"
                return REPLIES["elec_meter"]
        elif text == "2" or "water" in text:
            s["step"] = "water_meter"
            return REPLIES["water_meter"]
        elif text == "3" or text == "4" or "data" in text or "airtime" in text or phone_match:
            if phone_match:
                s["phone"] = phone_match.group(0)
                s["step"] = "pay"
                amt = amount_match.group(0) if amount_match else ""
                gb = gb_match.group(0) if gb_match else ""
                return f"📱 Got: {s['phone']} {gb} {amt}\n\n💳 Pay:\nTymeBank: 0818277662\nRef: {s['phone']}\n\nSend POP after payment - loads in 2 mins!\nR5 is R5 ✅"
            s["step"] = "data_phone"
            return REPLIES["data_menu"]
        elif text == "5" or "shop" in text or "spaza" in text or "bulk" in text:
            s["step"] = "shop"
            return REPLIES["shop"]
        elif text == "6" or "paper" in text or "manual" in text:
            s["step"] = "shop"
            return REPLIES["shop"] + "\n\n📄 VOUCHER TEMPLATE:\n1Data - sss™\nDate: ___\nPhone: 0__ ___ ____\nPackage: __GB R__\nPIN: ____\nR5 is R5 ✅"
        else:
            return MENU

    # === ELECTRICITY FLOW ===
    elif s["step"] == "elec_meter":
        if meter_match:
            s["meter"] = meter_match.group(0)
            s["step"] = "elec_amount"
            return f"✅ Meter saved: {s['meter']}\n\nHow much?\nSend R50 / R100 / R200 / R500\n\nEx: R200"
        else:
            return "❌ Invalid meter. Send 11 digits\nEx: 070123456789"

    elif s["step"] == "elec_amount":
        if amount_match:
            s["amount"] = amount_match.group(1)
            s["step"] = "pay"
            return f"⚡ ORDER READY - sss™\nMeter: {s['meter']}\nAmount: R{s['amount']}\n\n💳 Pay here:\nTymeBank: 0818277662\nRef: {s['meter']}\n\nSend POP after payment - token in 2 mins!\n\nR5 is R5 - IT IS WHAT IT IS ✅"
        else:
            return "Send amount like: R200\nHow much you want?"

    # === DATA FLOW ===
    elif s["step"] == "data_phone":
        if phone_match:
            s["phone"] = phone_match.group(0)
            s["step"] = "pay"
            amt = amount_match.group(0) if amount_match else "R45"
            gb = gb_match.group(0) if gb_match else "1GB"
            return f"📱 Got: {s['phone']} {gb} {amt}\n\n💳 Pay:\nTymeBank: 0818277662\nRef: {s['phone']}\n\nSend POP - Data loads after payment!\n\nDOMINATION: 1GB R45 vs R85\nR5 is R5 ✅ - sss™"
        else:
            return "Send phone + package\nEx: 0812345678 1GB R45"

    # === WATER ===
    elif s["step"] == "water_meter":
        if meter_match and amount_match:
            s["meter"] = meter_match.group(0)
            s["amount"] = amount_match.group(1)
            s["step"] = "pay"
            return f"💧 Water Order:\nMeter: {s['meter']}\nAmount: R{s['amount']}\n\n💳 Pay:\nTymeBank: 0818277662\nRef: {s['meter']}\n\nSend POP!\nR5 is R5 ✅"
        else:
            return "Send: Meter + Amount\nEx: 0123456789 R100"

    # === PAY ===
    elif s["step"] == "pay":
        if "pop" in text or "pay" in text or "proof" in text or "sent" in text:
            reply = f"🙏 POP received! Checking...\n\nYour {s.get('meter') or s.get('phone')} will be loaded in 2 mins!\n\nThanks for choosing 1Data by Hello Data SA™! 🙏\nR5 is R5 - IT IS WHAT IT IS ✅\nFounder: sss™\nSave my number!\n\nNeed another? Reply MENU"
            s["step"] = "menu"
            s["meter"] = None
            s["amount"] = None
            return reply
        else:
            # if they start new order while in pay step
            s["step"] = "menu"
            return get_reply(from_id, text_raw)

    # fallback
    s["step"] = "menu"
    return MENU

@app.route('/')
def home():
    return "1Data Bot 0818277662 - sss™ - R5 is R5 - ONLINE ✅"

@app.route('/webhook', methods=['GET'])
def verify():
    # For WhatsApp verification
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == 'sss08182':
        return challenge, 200
    return "Verify token sss08182", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    try:
        # Try to get WhatsApp Cloud API format
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])
        if messages:
            from_id = messages[0].get('from')
            text = messages[0].get('text', {}).get('body', '')
        else:
            # Fallback for testing: {from, message}
            from_id = data.get('from', 'test_user')
            text = data.get('message', '')

        reply_text = get_reply(from_id, text)

        # TODO: Send reply via WhatsApp API here
        # requests.post(f"https://graph.facebook.com/v18.0/YOUR_PHONE_ID/messages", headers=..., json={"messaging_product":"whatsapp","to":from_id,"text":{"body":reply_text}})

        print(f"[{from_id}] {text} -> {reply_text[:60]}")
        return jsonify({"reply": reply_text, "to": from_id})
    except Exception as e:
        print(f"Error: {e} data: {data}")
        return jsonify({"reply": MENU})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
