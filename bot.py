import os, re, threading
from flask import Flask
import telebot
from PIL import Image, ImageDraw, ImageFont
import pytesseract

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None
app = Flask(__name__)

BOOKMAKERS = ["hollywood","betway","1xbet","sportingbet","bet365","supabets","playabets","world sports"]

def create_win_poster(amount_text, bookmaker, games):
    W,H=1080,1080
    img=Image.new('RGB',(W,H),color=(15,15,15))
    draw=ImageDraw.Draw(img)
    draw.rectangle([20,20,W-20,H-20],outline=(255,215,0),width=8)
    try:
        fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",90)
        fm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",50)
        fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",35)
        fh=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",110)
    except:
        fb=fm=fs=fh=ImageFont.load_default()
    draw.text((W//2,180),"WON!",fill=(255,215,0),font=fb,anchor="mm")
    draw.text((W//2,330),amount_text,fill=(255,255,255),font=fh,anchor="mm")
    draw.text((W//2,470),f"{bookmaker}",fill=(200,200,200),font=fm,anchor="mm")
    y=550
    for g in games[:3]:
        draw.text((W//2,y),f"{g[0].strip()} vs {g[2].strip()}",fill=(255,255,255),font=fm,anchor="mm")
        y+=60
    draw.text((W//2,850),"Ticket Scanner Robot",fill=(255,215,0),font=fs,anchor="mm")
    draw.text((W//2,900),"bot-0818277662.onrender.com",fill=(120,120,120),font=fs,anchor="mm")
    img.save("win_poster.jpg")
    return "win_poster.jpg"

@app.route("/")
def home():
    return "Ticket Scanner LIVE - All outlets - 1+4"

@bot.message_handler(content_types=['photo'])
def scan(message):
    file_info=bot.get_file(message.photo[-1].file_id)
    data=bot.download_file(file_info.file_path)
    open("ticket.jpg","wb").write(data)
    text=pytesseract.image_to_string(Image.open("ticket.jpg"))
    low=text.lower()
    bookmaker="BETTING"
    for b in BOOKMAKERS:
        if b in low:
            bookmaker=b.upper()
            break
    games=re.findall(r'([A-Za-z ]+)\s*(?:vs|v|-)\s*([A-Za-z ]+)',text)
    # Fix tuple handling
    games_fixed=[]
    for g in re.finditer(r'([A-Za-z ]+)\s*(?:vs|v|-)\s*([A-Za-z ]+)',text):
        games_fixed.append((g.group(1), "", g.group(2)))
    games=games_fixed
    amounts=re.findall(r'R\s?(\d+\.?\d*)',text)
    amount_text=f"R{amounts[-1]}" if amounts else "R WIN"
    stake=re.findall(r'R\s?(\d+)',text)
    stake_val=int(stake[0]) if stake else 50
    is_win = any(k in low for k in ["won","payout","paid","withdraw"])
    if is_win:
        poster=create_win_poster(amount_text,bookmaker,games)
        bot.send_photo(message.chat.id,open(poster,'rb'),caption=f"🔥 {bookmaker} {amount_text} WON! Poster ready for status.")
    else:
        cashout = stake_val * 4.2
        msg=f"🏦 {bookmaker}\n🎫 {len(games)} games found\n"
        for g in games[:3]:
            msg+=f"- {g[0].strip()} vs {g[2].strip()}\n"
        msg+=f"\n💡 WHAT IF CASHOUT:\nIf you cashed out at 85' you would have R{cashout:.0f} not R0.\nNext time cash early!"
        bot.reply_to(message,msg)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m,"⚽ Universal Ticket Scanner\nSend ANY betting ticket photo\nI scan ALL outlets and tell WON/LOST + Poster + Cashout lesson")

if __name__=="__main__":
    if bot:
        threading.Thread(target=lambda:bot.infinity_polling(),daemon=True).start()
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",10000)))
