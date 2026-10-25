# -*- coding: utf-8 -*-
"""
ربات تلگرام ثبت‌نام و یوزردِهی خودکار سرور تیم‌تاک کافه دوستی
"""

import os
import sys
import time
import json
import socket
import secrets
import string
import random
import sqlite3
import threading
import urllib.request
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

# ----------------- تنظیمات اصلی -----------------
BOT_TOKEN = "8873777481:AAGD4DjF9AebcYqfZen8sUpbxu2wA8pZXqk"
ADMIN_CHAT_ID = 8834927594  # پشتیبانی کافه دوستی (@Pkaafehdoosti)
CHANNEL_USERNAME = "@kaafehdoosti"
CHANNEL_LINK = "https://t.me/kaafehdoosti"

# تنظیمات سرور تیم‌تاک کافه دوستی
TT_HOST = "kaafehdoosti.ir"
TT_PORT = 10333
TT_ADMIN_USER = "kaafehdoostibot"
TT_ADMIN_PASS = "asdfghjkl1234lkjhgfdsa4321qwwq"
TT_NICKNAME = "ربات یوزر دهی"

# دسترسی‌های کاربر تیم‌تاک:
# بدون ورود هم‌زمان (Multi-login) و بدون ساخت کانال موقت (Temporary channel)
# 0x00C17602 = 12678658
TT_USER_RIGHTS = 12678658

# کلید کاوه‌نگار (به محض احراز هویت در این متغیر قرار می‌گیرد)
KAVENEGAR_API_KEY = ""

# متن کامل قوانین سرور کافه دوستی
RULES_TEXT = """به نام خداوند متعال ✨

🌙 خوش آمدید به کافه دوستی

اینجا جایی است که صدای خنده ها بلندتر از سکوت است و هر گوشه اش بوی رفاقت تازه ای می دهد. کافه دوستی تنها یک سرور نیست؛ قرار هر شب ماست. محفلی گرم که برای لحظه هایی شاد، بی تکلف و به یادماندنی ساخته شده است. وقتی وارد می شوید، بدانید که به جمعی قدم گذاشته اید که ارزشش را احترام، اعتماد و صفای میان اعضایش می سازد. 🤍

پیش از هر چیز، برای اینکه این فضای دلنشین برای همه دلپذیر بماند، رعایت چند نکته بر ما و شما لازم است. لطفاً با دقت مطالعه کنید و بدانید که پذیرش این قوانین، شرط حضور در کافه دوستی است.

🎧 توجه: این سرور برای اوقاتی شاد و مفرح میان دوستان ساخته شده است؛ پس هنگام حضور در سرور، استفاده از هندزفری الزامی است.

---

📜 قوانین سرور کافه دوستی

۱. عضویت در کانال تلگرامی «کافه دوستی» برای همه کاربران الزامی است. اگر کسی عضو کانال نشود، یوزر او ساخته نمی شود و اگر کانال را ترک کند، یوزرش از سرور حذف می شود.
📌 نکته: کسی که یوزرش از سرور حذف شود، تا سه ماه امکان بازگشت به سرور را ندارد.

۲. هنگام پخش یک ترک، قطع کردن Audio Box حتی به شوخی، تخلف شمرده می شود. همچنین جست و جوی مطالب غیراخلاقی در Audio Player ممنوع است؛ در این مورد کاربر تا دو بار اخطار می گیرد و بار سوم یوزرش به مدت یک هفته از کافه دوستی محروم می شود. اگر این تخلف بیش از سه بار دیده شود، یوزر او از سرور حذف می گردد.

۳. ضبط صدا در هر شرایطی برای کاربران ممنوع است؛ مگر برنامه هایی که عوامل و صدابردارانشان را مدیران تعیین کرده باشند. در غیر این صورت، کاربر از کافه دوستی حذف می شود.

۴. نام مستعار شما همان نامی است که برای نخستین بار با آن وارد کافه دوستی می شوید؛ پس تغییر پیوسته نام مستعار تخلف است و اگر این تغییر باعث آزار دیگری شود، با شما برخورد خواهد شد.

۵. احترام به یکدیگر در این سرور ضروری است و توهین به شخصیت و مذهب افراد تخلف شمرده می شود؛ بار اول تذکر، بار دوم یوزر شما به مدت ۲۴ ساعت بن می شود و در صورت تکرار برای بار سوم، یوزر شما از کافه دوستی حذف می گردد. با کسی هم که به حقوق دیگران احترام نگذارد، تیم مدیریت برخورد می کند و یوزر او را ۴۸ ساعت از سرور محروم می سازد.
📌 نکته: تیم مدیریت این سرور هیچ مسئولیتی در قبال روابط کاربران با یکدیگر ندارد و هر مشکل، بحث یا درگیری بر عهده خود کاربران است. همچنین مدیریت در برابر بحث و جدال یا خصومت شخصی ای که از پیش میان کاربران بوده و به سرور کشیده شده، هیچ مسئولیتی نمی پذیرد.

۶. اگر کاربری مایل به چت خصوصی یا گفت و گو در کانال های خصوصی نیست، لطفاً به این کار اصرار نکنید.

۷. اگر کاربری از کافه دوستی یوزر بگیرد و تا دو ماه در سرور دیده نشود، از کافه دوستی حذف می شود. همچنین کسی که چند بار وارد سرور می شود، باید دست کم یک بار با افراد حاضر در جمع گفت و گو کند.

۸. هیچ یک از مدیران مجموعه در قبال اتاق ها و کانال های خصوصی مسئولیتی ندارند.

۹. هرگونه بحث سیاسی ممنوع است.
⚠️ تبصره: هرگونه استاتوس انقلابی و غیرانقلابی هم اکیداً ممنوع است. در صورت تخلف، یوزر کاربر بار اول ۴۸ ساعت بن می شود و اگر بیش از یک بار دیده شود، یوزر او حذف می گردد.

۱۰. در نظر داشته باشید که قوانین هر چند ماه یک بار به روزرسانی می شود؛ پس اگر ایده، پیشنهاد یا انتقادی دارید، آن را با مدیریت کافه دوستی در میان بگذارید.

---

📢 کانال اطلاع رسانی
🔗 https://t.me/kaafehdoosti
🔗 https://splus.ir/Kafeh_doosti

---

🌿 به امید روزهای شاد و مفرح
کافه دوستی؛ جایی که هر شب، خاطره ای تازه ساخته می شود. ☕️🤍"""

# ----------------- پایگاه داده -----------------
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_database.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            step TEXT,
            persian_name TEXT,
            username TEXT,
            phone TEXT,
            sms_code TEXT,
            voice_file_id TEXT,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT step, persian_name, username, phone, sms_code, voice_file_id, password FROM users WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "step": row[0],
            "persian_name": row[1],
            "username": row[2],
            "phone": row[3],
            "sms_code": row[4],
            "voice_file_id": row[5],
            "password": row[6]
        }
    return None

def set_user(chat_id, **kwargs):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    user = get_user(chat_id)
    if not user:
        c.execute("INSERT INTO users (chat_id, step) VALUES (?, ?)", (chat_id, kwargs.get("step", "IDLE")))
    for k, v in kwargs.items():
        c.execute(f"UPDATE users SET {k}=? WHERE chat_id=?", (v, chat_id))
    conn.commit()
    conn.close()

# ----------------- تبدیل نام فارسی به فینگلیش -----------------
PERSIAN_TO_EN = {
    'آ': 'a', 'ا': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's',
    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z',
    'ر': 'r', 'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
    'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': '', 'غ': 'gh', 'ف': 'f',
    'ق': 'gh', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'و': 'o', 'ه': 'h', 'ی': 'i', 'ي': 'i', 'ئ': '', 'ء': '',
    'ة': 'eh', 'ك': 'k'
}

SPECIAL_NAMES = {
    'امید': 'omid', 'علی': 'ali', 'رضا': 'reza', 'محمد': 'mohammad',
    'حسین': 'hossein', 'مهدی': 'mehdi', 'حسن': 'hasan', 'امیر': 'amir',
    'علیرضا': 'alireza', 'محمدرضا': 'mohammadreza', 'فاطمه': 'fatemeh',
    'زهرا': 'zahra', 'مریم': 'maryam', 'سارا': 'sara', 'یلدا': 'yalda',
    'امیری': 'amiri', 'علیایی': 'oliaiy', 'عُلیائی': 'oliaiy',
    'محمدی': 'mohammadi', 'رضایی': 'rezaei', 'حسینی': 'hosseini',
    'کاظمی': 'kazemi', 'صادقی': 'sadeghi'
}

def persian_to_english(text):
    words = text.strip().split()
    en_words = []
    for w in words:
        clean_w = w.replace('‌', '').replace('\u200c', '') # remove zero-width non-joiner
        if clean_w in SPECIAL_NAMES:
            en_words.append(SPECIAL_NAMES[clean_w])
        else:
            res = ""
            for ch in clean_w:
                res += PERSIAN_TO_EN.get(ch, ch)
            en_words.append(res)
    username = " ".join(en_words).lower()
    # فقط حروف انگلیسی و فاصله
    username = "".join(c for c in username if c.isalpha() or c == ' ')
    # حذف فاصله‌های اضافی
    username = " ".join(username.split())
    return username.strip()

# ----------------- تلگرام ای‌پی‌آی -----------------
def tg_request(method, data=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    headers = {"Content-Type": "application/json"}
    try:
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Telegram API Error ({method}): {e}", flush=True)
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return tg_request("sendMessage", payload)

def forward_message(chat_id, from_chat_id, message_id):
    payload = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    return tg_request("forwardMessage", payload)

def send_voice(chat_id, voice_file_id, caption=None, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "voice": voice_file_id
    }
    if caption:
        payload["caption"] = caption
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return tg_request("sendVoice", payload)

def send_document_file(chat_id, filename, file_bytes, caption=None):
    boundary = "----WebKitFormBoundary" + secrets.token_hex(8)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
    if caption:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode())
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode())
    body.extend(b'Content-Type: application/octet-stream\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f"--{boundary}--\r\n".encode())
    
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error sending document: {e}", flush=True)
        return None

# بررسی عضویت در کانال کافه دوستی
def is_channel_member(user_id):
    res = tg_request("getChatMember", {"chat_id": CHANNEL_USERNAME, "user_id": user_id})
    if res and res.get("ok"):
        status = res.get("result", {}).get("status")
        return status in ["creator", "administrator", "member", "restricted"]
    return False

# ----------------- ارسال پیامک با کاوه‌نگار -----------------
def send_sms_otp(phone, code):
    if not KAVENEGAR_API_KEY:
        print(f"[TEST MODE] SMS not configured. Code for {phone} is: {code}", flush=True)
        return True, "کد در حالت آزمایشی تولید شد."
    
    try:
        url = f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json"
        params = urllib.parse.urlencode({
            "receptor": phone,
            "token": code,
            "template": "verify"
        })
        full_url = f"{url}?{params}"
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("return", {}).get("status") == 200:
                return True, "پیامک با موفقیت ارسال شد."
            else:
                return False, data.get("return", {}).get("message", "خطا در ارسال پیامک")
    except Exception as e:
        return False, str(e)

# ----------------- ایجاد حساب در تیم‌تاک -----------------
def create_teamtalk_account(username, password, phone):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((TT_HOST, TT_PORT))
        s.recv(4096) # banner
        
        # لاگین ربات ادمین با نام مستعار «ربات یوزر دهی»
        login_cmd = f'login username="{TT_ADMIN_USER}" password="{TT_ADMIN_PASS}" nickname="{TT_NICKNAME}" protocol="5.13" clientname="TeamTalk5"\r\n'
        s.sendall(login_cmd.encode('utf-8'))
        time.sleep(1)
        resp = s.recv(8192).decode('utf-8', errors='ignore')
        if "accepted" not in resp:
            s.close()
            return False, "عدم پذیرش ورود ادمین ربات به سرور تیم‌تاک"
        
        # ساخت اکانت جدید:
        # ۱. دسترسی بدون لاگین چندباره و بدون ساخت کانال موقت (TT_USER_RIGHTS)
        # ۲. ثبت شماره موبایل در بخش توضیحات (note="{phone}")
        # ۳. محدودیت ارسال ۱۰ پیام در یک دقیقه (cmdflood=[10,60000])
        cmd_new = f'newaccount username="{username}" password="{password}" note="{phone}" usertype=1 userrights={TT_USER_RIGHTS} cmdflood=[10,60000]\r\n'
        s.sendall(cmd_new.encode('utf-8'))
        time.sleep(1)
        
        # ذخیره تغییرات در دیتابیس سرور
        s.sendall(b'saveconfig\r\n')
        time.sleep(0.5)
        s.close()
        return True, "حساب کاربری با موفقیت در تیم‌تاک ساخته شد."
    except Exception as e:
        return False, str(e)

# ----------------- ساخت فایل tt -----------------
def generate_tt_file_bytes(username, password, nickname):
    content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE teamtalk>
<teamtalk version="5.0">
 <host>
  <name>کافه دوستی</name>
  <address>{TT_HOST}</address>
  <tcpport>{TT_PORT}</tcpport>
  <udpport>{TT_PORT}</udpport>
  <encrypted>false</encrypted>
  <auth>
   <username>{username}</username>
   <password>{password}</password>
  </auth>
  <clientsetup>
   <nickname>{nickname}</nickname>
  </clientsetup>
 </host>
</teamtalk>
'''
    return content.encode('utf-8')

# ----------------- مدیریت پیام‌های کاربران -----------------
def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    voice = msg.get("voice")
    user = get_user(chat_id)
    
    if text == "/start":
        set_user(chat_id, step="IDLE")
        keyboard = {
            "inline_keyboard": [
                [{"text": "ورود به کافه دوستی و دریافت حساب ☕️✨", "callback_data": "start_register"}]
            ]
        }
        welcome_text = (
            "هر جا که کلمات از سر مهر جاری شوند و دل‌ها بی‌نقاب کنار هم بنشینند، همان‌جا زندگی واقعی جریان دارد.\n\n"
            "به کافه دوستی خوش آمدید؛ سرپناهی از جنس صدا، ترانه و هم‌نشینی، برای کسانی که ارزش یک گفت‌وگوی زلال و از ته‌دل را می‌دانند. حضور شما در این فضا برای ما اتفاقی ارزشمند است و مشتاق شنیدن صدایتان در این جمع هستیم.\n\n"
            "برای دریافت کلید ورود به سرور و پیوستن به خانواده کافه دوستی، کافی است روی دکمه زیر کلیک کنید."
        )
        send_message(chat_id, welcome_text, keyboard)
        return
    
    if not user:
        set_user(chat_id, step="IDLE")
        return
    
    step = user["step"]
    
    if step == "WAIT_NAME":
        if not text:
            send_message(chat_id, "لطفا نام و نام خانوادگی خود را به صورت متنی و فارسی ارسال کنید:")
            return
        persian_name = text
        username = persian_to_english(persian_name)
        set_user(chat_id, step="WAIT_PHONE", persian_name=persian_name, username=username)
        msg_text = (
            f"نام فارسی شما: {persian_name}\n"
            f"نام کاربری انگلیسی پیشنهادی شما: {username}\n\n"
            "حالا لطفا شماره موبایل خود را به صورت ۱۱ رقمی (مانند: ۰۹۱۲۳۴۵۶۷۸۹) وارد کنید:"
        )
        send_message(chat_id, msg_text)
        return
    
    if step == "WAIT_PHONE":
        clean_phone = text.replace("+98", "0").replace("0098", "0").replace(" ", "").replace("-", "")
        fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
        clean_phone = clean_phone.translate(fa_to_en)
        if clean_phone.startswith("98"):
            clean_phone = "0" + clean_phone[2:]
        elif clean_phone.startswith("9") and len(clean_phone) == 10:
            clean_phone = "0" + clean_phone
        
        if not (clean_phone.startswith("09") and len(clean_phone) == 11 and clean_phone.isdigit()):
            send_message(chat_id, "شماره موبایل وارد شده صحیح نیست. لطفا یک شماره معتبر ۱۱ رقمی مانند ۰۹۱۲۳۴۵۶۷۸۹ وارد کنید:")
            return
        
        set_user(chat_id, step="WAIT_VOICE", phone=clean_phone)
        voice_prompt = (
            f"شماره موبایل شما ({clean_phone}) با موفقیت ثبت شد ✅\n\n"
            "مرحله پایانی (ویس معرفی):\n"
            "لطفا یک پیام صوتی (ویس) درون تلگرام ضبط و ارسال کنید و در آن موارد زیر را بگویید:\n"
            "۱. نام و نام خانوادگی\n"
            "۲. محل سکونت (شهر یا استان)\n"
            "۳. سن\n"
            "۴. وضعیت تاهل\n\n"
            "منتظر ارسال ویس شما هستیم..."
        )
        send_message(chat_id, voice_prompt)
        return
    
    if step == "WAIT_CODE":
        set_user(chat_id, step="WAIT_VOICE")
        voice_prompt = (
            "شماره موبایل شما با موفقیت ثبت شد ✅\n\n"
            "مرحله پایانی (ویس معرفی):\n"
            "لطفا یک پیام صوتی (ویس) درون تلگرام ضبط و ارسال کنید و در آن موارد زیر را بگویید:\n"
            "۱. نام و نام خانوادگی\n"
            "۲. محل سکونت (شهر یا استان)\n"
            "۳. سن\n"
            "۴. وضعیت تاهل\n\n"
            "منتظر ارسال ویس شما هستیم..."
        )
        send_message(chat_id, voice_prompt)
        return
    
    if step == "WAIT_VOICE":
        if not voice:
            send_message(chat_id, "لطفا فقط پیام صوتی (ویس) ارسال بفرمایید:")
            return
        
        voice_file_id = voice["file_id"]
        set_user(chat_id, step="PENDING_ADMIN", voice_file_id=voice_file_id)
        
        send_message(chat_id, "ویس و پرونده معرفی شما با موفقیت دریافت شد ✅\nاطلاعات شما برای مدیریت سرور کافه دوستی ارسال گردید. به محض بررسی و تایید، نتیجه به شما اعلام خواهد شد.")
        
        user_info = get_user(chat_id)
        tg_user = msg.get("from", {})
        tg_username = f"@{tg_user.get('username')}" if tg_user.get('username') else "بدون آیدی"
        
        caption = (
            "🔔 درخواست عضویت و حساب جدید در کافه دوستی:\n\n"
            f"👤 نام فارسی: {user_info['persian_name']}\n"
            f"🔤 نام کاربری انگلیسی پیشنهادی: {user_info['username']}\n"
            f"📱 شماره موبایل: {user_info['phone']}\n"
            f"💬 کاربر تلگرام: {tg_username} (شناسه: {chat_id})\n\n"
            "لطفا ویس بالا را گوش دهید و تصمیم‌گیری کنید:"
        )
        
        admin_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "تایید و ساخت یوزر ✅", "callback_data": f"approve_{chat_id}"},
                    {"text": "رد درخواست ❌", "callback_data": f"reject_{chat_id}"}
                ]
            ]
        }
        send_voice(ADMIN_CHAT_ID, voice_file_id, caption=caption, reply_markup=admin_keyboard)
        return

# ----------------- مدیریت دکمه‌های شیشه‌ای -----------------
def handle_callback_query(cq):
    cq_id = cq["id"]
    from_user = cq["from"]["id"]
    data = cq.get("data", "")
    msg = cq.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    message_id = msg.get("message_id")
    
    tg_request("answerCallbackQuery", {"callback_query_id": cq_id})
    
    if data in ["start_register", "check_join"]:
        # بررسی عضویت اجباری در کانال
        if not is_channel_member(from_user):
            join_keyboard = {
                "inline_keyboard": [
                    [{"text": "عضویت در کانال کافه دوستی 📢", "url": CHANNEL_LINK}],
                    [{"text": "عضو شدم / بررسی عضویت 🔄", "callback_data": "check_join"}]
                ]
            }
            send_message(
                from_user,
                "⚠️ طبق قوانین کافه دوستی، برای ثبت‌نام و دریافت حساب کاربری، ابتدا باید عضو کانال تلگرامی کافه دوستی شوید.\n\n"
                "لطفا از طریق دکمه زیر در کانال عضو شوید و سپس دکمه «عضو شدم / بررسی عضویت» را بزنید:",
                join_keyboard
            )
            return
        
        # اگر عضو کانال بود، ورود به مرحله نام
        set_user(from_user, step="WAIT_NAME")
        send_message(from_user, "عضویت شما در کانال کافه دوستی تایید شد ✅\n\nلطفا نام و نام خانوادگی خود را به زبان فارسی (مانند: امید علیایی) بنویسید و ارسال کنید:")
        return
    
    # دستورات مخصوص مدیر
    if data.startswith("approve_"):
        target_chat_id = int(data.split("_")[1])
        user_info = get_user(target_chat_id)
        if not user_info:
            send_message(ADMIN_CHAT_ID, "اطلاعات کاربر یافت نشد.")
            return
        
        if user_info.get("step") == "COMPLETED":
            tg_request("answerCallbackQuery", {
                "callback_query_id": cq_id,
                "text": "این کاربر قبلاً تایید و یوزرش ساخته شده است.",
                "show_alert": True
            })
            tg_request("editMessageReplyMarkup", {
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": {"inline_keyboard": []}
            })
            return
        
        chars = string.ascii_letters + string.digits
        password_30 = ''.join(secrets.choice(chars) for _ in range(30))
        username = user_info["username"]
        phone = user_info["phone"]
        
        # ساخت اکانت در تیم‌تاک همراه با شماره در توضیحات و محدودیت پیام
        ok, res = create_teamtalk_account(username, password_30, phone)
        if not ok:
            send_message(ADMIN_CHAT_ID, f"خطا در ساخت اکانت در سرور تیم‌تاک:\n{res}")
            return
        
        set_user(target_chat_id, step="COMPLETED", password=password_30)
        
        # به‌روزرسانی پیام ویس در پیوی مدیر و حذف کامل دکمه‌های تایید و رد
        updated_caption = (
            "🔔 درخواست عضویت در کافه دوستی:\n\n"
            f"👤 نام فارسی: {user_info['persian_name']}\n"
            f"🔤 نام کاربری: {username}\n"
            f"📱 شماره موبایل: {phone}\n\n"
            "وضعیت: تایید شد و یوزر در سرور ساخته شد ✅"
        )
        tg_request("editMessageCaption", {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": updated_caption,
            "reply_markup": {"inline_keyboard": []}
        })
        
        # ارسال گزینه‌های دریافت حساب برای کاربر
        delivery_keyboard = {
            "inline_keyboard": [
                [{"text": "دریافت فایل آماده ورود (فایل TT) 📁", "callback_data": f"get_tt_{target_chat_id}"}],
                [{"text": "دریافت مشخصات به صورت متن 📝", "callback_data": f"get_txt_{target_chat_id}"}],
                [{"text": "دریافت هر دو حالت (متن و فایل) ✨", "callback_data": f"get_both_{target_chat_id}"}]
            ]
        }
        congrats_text = (
            "🎉 تبریک! حساب کاربری شما در سرور تیم‌تاک کافه دوستی ساخته شد.\n\n"
            "مایلید اطلاعات ورود چگونه برای شما ارسال شود؟"
        )
        send_message(target_chat_id, congrats_text, delivery_keyboard)
        return
    
    if data.startswith("reject_"):
        target_chat_id = int(data.split("_")[1])
        user_info = get_user(target_chat_id)
        if user_info and user_info.get("step") in ["COMPLETED", "REJECTED"]:
            tg_request("answerCallbackQuery", {
                "callback_query_id": cq_id,
                "text": "تکلیف این درخواست قبلاً مشخص شده است.",
                "show_alert": True
            })
            tg_request("editMessageReplyMarkup", {
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": {"inline_keyboard": []}
            })
            return
        
        persian_name = user_info['persian_name'] if user_info else 'کاربر'
        set_user(target_chat_id, step="REJECTED")
        
        # به‌روزرسانی پیام ویس در پیوی مدیر و حذف کامل دکمه‌ها
        updated_caption = (
            "🔔 درخواست عضویت در کافه دوستی:\n\n"
            f"👤 نام فارسی: {persian_name}\n\n"
            "وضعیت: این درخواست توسط مدیریت رد شد ❌"
        )
        tg_request("editMessageCaption", {
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": updated_caption,
            "reply_markup": {"inline_keyboard": []}
        })
        
        send_message(target_chat_id, "متاسفانه درخواست عضویت شما در سرور کافه دوستی توسط مدیریت تایید نشد.")
        return
    
    # دکمه‌های تحویل اکانت به کاربر
    if data.startswith("get_tt_") or data.startswith("get_txt_") or data.startswith("get_both_"):
        # حذف دکمه‌های انتخاب پس از کلیک برای تمیز ماندن چت کاربر
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        
        target_chat_id = int(data.split("_")[-1])
        user_info = get_user(target_chat_id)
        if not user_info or not user_info["password"]:
            send_message(target_chat_id, "خطا در بازیابی اطلاعات حساب.")
            return
        
        username = user_info["username"]
        password = user_info["password"]
        persian_name = user_info["persian_name"]
        
        txt_info = (
            "مشخصات اتصال به سرور کافه دوستی:\n\n"
            f"آدرس سرور: {TT_HOST}\n"
            f"پورت: {TT_PORT}\n"
            f"نام کاربری: {username}\n"
            f"رمز عبور: {password}\n\n"
            "به کافه دوستی خوش آمدید!"
        )
        
        if "txt" in data or "both" in data:
            send_message(target_chat_id, txt_info)
        
        if "tt" in data or "both" in data:
            tt_bytes = generate_tt_file_bytes(username, password, persian_name)
            filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
            send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        # ارسال متن کامل قوانین سرور به محض دریافت یوزر
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        send_message(target_chat_id, rules_header + RULES_TEXT)
        return

# ----------------- سرور سلامت برای رندر (Health Check) -----------------
import http.server
import socketserver

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("ربات کافه دوستی به صورت ۲۴ ساعته در حال کار است.".encode('utf-8'))
        def log_message(self, format, *args):
            pass
    try:
        with socketserver.TCPServer(("", port), HealthHandler) as httpd:
            print(f"سرور سلامت روی پورت {port} فعال شد.", flush=True)
            httpd.serve_forever()
    except Exception as e:
        print(f"خطای سرور سلامت: {e}", flush=True)

threading.Thread(target=run_health_server, daemon=True).start()

# ----------------- سیستم بیدار نگه‌داشتن سرور (Keep-Alive Ping) -----------------
def keep_alive_worker():
    time.sleep(60)
    while True:
        try:
            req = urllib.request.Request("https://kaafehdoosti-bot.onrender.com", headers={'User-Agent': 'KeepAlivePing/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                pass
        except Exception:
            pass
        time.sleep(600)  # هر ۱۰ دقیقه یک پینگ ارسال می‌کند تا سرور رندر به خواب نرود

threading.Thread(target=keep_alive_worker, daemon=True).start()

# ----------------- حلقه اصلی دریافت پیام‌ها -----------------
def run_bot():
    print("ربات نسخه ۲ با موفقیت فعال شد و آماده دریافت پیام است...", flush=True)
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("ok"):
                    for item in data.get("result", []):
                        offset = item["update_id"] + 1
                        if "message" in item:
                            handle_message(item["message"])
                        elif "callback_query" in item:
                            handle_callback_query(item["callback_query"])
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    run_bot()
