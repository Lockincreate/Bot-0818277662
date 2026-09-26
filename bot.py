from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re

app = Flask(__name__)

sessions = {}

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

R5 is R5 - IT IS WHAT IT IS ✅"""

REPLIES = {
"elec_meter": "⚡ Electricity - All SA - sss™\nSend your meter number (11 digits)\nEx: 070123456789\n\nR5 is R5 ✅",
"water_meter": "💧 Water - eThekwini / Durban\nSend meter number + Amount\nEx: 0123456789 R100\n\nR5 is R5 ✅",
"data_menu": "📱 DOMINATION DATA - sss™\nWhy Pay More?\n\nMTN 1GB R85 → Our R45\nMTN 5GB R299 → Our R120\nVoda 10GB R529 → Our R160\n20GB R799 → Our R240\n\nSend: Phone + Package\nEx: 0812345678 1GB R45\n\nR5 is R5 ✅",
"shop": "🏪 SHOP / SPAZA WHOLESALE - sss™\nOur R45 → Sell R55 Profit R10\nOur R120 → Sell R149 Profit R29\nOur R160 → Sell R199 Profit R39\n\nStill cheaper than MTN!\nBulk: 100+ = R2 off 500+ = R4 off 1000+ = R6 off\n\n📄 Manual paper voucher ALLOWED!\nTymeBank 0818277662\nR5 is R5 ✅"
}

def get_reply(from_id, text_raw):
    text = text_raw.strip().lower()
    raw = text_raw.strip()
    if from_id not in sessions:
        sessions[from_id] = {"step":"menu","meter":None,"amount":None,"phone":None}
    s = sessions[from_id]

    meter_match = re.search(r'\d{11,13}', raw)
    phone_match = re.search(r'0\d{9}', raw)
    amount_match = re.search(r'r?\s*(\d+)', raw, re.I)
    gb_match = re.search(r'\d+gb', raw, re.I)

    if s["step"] == "menu":
        if text == "1" or "electric" in text or (meter_match and not phone_match):
            if meter_match:
                s["meter"] = meter_match.group(0)
                s["step"] = "elec_amount"
                return f"✅ Meter saved: {s['meter']}\n\nHow much?\nReply: R50 / R100 / R200\nR5 is R5 ✅ - sss™"
            else:
                s["step"] = "elec_meter"
                return REPLIES["elec_meter"]
        elif text == "2" or "water" in text:
            s["step"] = "water_meter"
            return REPLIES["water_meter"]
        elif text in ["3","4"] or "data" in text or "airtime" in text or phone_match:
            if phone_match:
                s["phone"] = phone_match.group(0)
                s["step"] = "pay"
                amt = amount_match.group(0) if amount_match else ""
                gb = gb_match.group(0) if gb_match else ""
                return f"📱 Got: {s['phone']} {gb} {amt}\n\n💳 Pay: TymeBank 0818277662 Ref: {s['phone']}\nSend POP after payment!\nR5 is R5 ✅"
            s["step"] = "data_phone"
            return REPLIES["data_menu"]
        elif text == "5" or "shop" in text or "bulk" in text:
            s["step"] = "shop"
            return REPLIES["shop"]
        elif text == "6" or "paper" in text or "manual" in text:
            return REPLIES["shop"] + "\n\n📄 VOUCHER: 1Data - sss™ Date:___ Phone:0__ Package:__GB R__ PIN:____"
        else:
            return MENU

    elif s["step"] == "elec_meter":
        if meter_match:
            s["meter"] = meter_match.group(0)
            s["step"] = "elec_amount"
            return f"✅ Meter saved: {s['meter']}\nHow much? Send R50 / R100 / R200"
        else:
            return "❌ Invalid meter. Send 11 digits Ex: 070123456789"
    elif s["step"] == "elec_amount":
        if amount_match:
            s["amount"] = amount_match.group(1)
            s["step"] = "pay"
            return f"⚡ ORDER READY\nMeter: {s['meter']}\nAmount: R{s['amount']}\n\n💳 Pay: TymeBank 0818277662 Ref: {s['meter']}\nSend POP - token in 2 mins!\nR5 is R5 ✅"
        else:
            return "Send amount like: R200"
    elif s["step"] == "data_phone":
        if phone_match:
            s["phone"] = phone_match.group(0)
            s["step"] = "pay"
            return f"📱 Got: {s['phone']}\n💳 Pay: TymeBank 0818277662 Ref: {s['phone']}\nSend POP!\nR5 is R5 ✅"
        else:
            return "Send phone + package Ex: 0812345678 1GB R45"
    elif s["step"] == "water_meter":
        if meter_match and amount_match:
            s["meter"] = meter_match.group(0)
            s["amount"] = amount_match.group(1)
            s["step"] = "pay"
            return f"💧 Water Order Meter:{s['meter']} Amount:R{s['amount']}\n💳 TymeBank 0818277662 Ref:{s['meter']}\nSend POP! R5 is R5 ✅"
        else:
            return "Send: Meter + Amount Ex: 0123456789 R100"
    elif s["step"] == "pay":
        if "pop" in text or "pay" in text or "sent" in text:
            reply = f"🙏 POP received! Checking... {s.get('meter') or s.get('phone')} will be loaded in 2 mins! Thanks! Reply MENU"
            s["step"] = "menu"
            return reply
        else:
            s["step"] = "menu"
            return get_reply(from_id, text_raw)
    s["step"] = "menu"
    return MENU

@app.route("/", methods=['GET','POST'])
def whatsapp():
    if request.method == 'GET':
        return "1Data Bot 0818277662 - sss™ - ONLINE ✅", 200

    # TWILIO sends form data
    from_id = request.values.get('From','test')
    body = request.values.get('Body','')
    
    reply_text = get_reply(from_id, body)
    
    resp = MessagingResponse()
    resp.message(reply_text)
    return str(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
