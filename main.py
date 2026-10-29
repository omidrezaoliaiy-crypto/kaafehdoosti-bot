# -*- coding: utf-8 -*-
"""
ربات دو پلتفرمه تلگرام و سروش پلاس برای ثبت‌نام، احراز هویت و یوزردِهی خودکار سرور تیم‌تاک کافه دوستی
"""

import os
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

import sys
import time
import json
import re
import socket
import secrets
import string
import random
import sqlite3
import threading
import urllib.request
import urllib.parse
import urllib.error
import ctypes

# تنظیم اوپنر بدون پروکسی برای اطمینان از اتصال پایدار
try:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    urllib.request.install_opener(opener)
except Exception:
    pass

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

# ----------------- تنظیمات اصلی تلگرام و سروش پلاس -----------------
BOT_TOKEN = "8873777481:AAGD4DjF9AebcYqfZen8sUpbxu2wA8pZXqk"
ADMIN_CHAT_ID = 8834927594  # پشتیبانی کافه دوستی (@Pkaafehdoosti)
CHANNEL_USERNAME = "@kaafehdoosti"
CHANNEL_LINK = "https://t.me/kaafehdoosti"

# تنظیمات ربات سروش پلاس کافه دوستی
SPLUS_TOKEN = "70705855:MthyAyaCzFaoIqe6_qBvCzaMcfbWrlptaLU"
SPLUS_CHANNEL_USERNAME = "@Kafeh_doosti"
SPLUS_CHANNEL_LINK = "https://splus.ir/Kafeh_doosti"
SPLUS_ADMIN_CHAT_ID = 70365151

# تنظیمات سرور تیم‌تاک کافه دوستی
TT_HOST = "185.26.33.57"
TT_PORT = 10333
TT_ADMIN_USER = "kaafehdoostibot"
TT_ADMIN_PASS = "asdfghjkl1234lkjhgfdsa4321qwwq"
TT_NICKNAME = "ربات یوزر دهی"

# تنظیمات ربات ناظر سرور (حضور دائم و بدون قطعی در سرور)
TT_NAZER_USER = "kaafeh_nazer"
TT_NAZER_PASS = "SecureNazerPass998877"
TT_NAZER_NICKNAME = "ربات ناظر"

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

۱. عضویت در کانال تلگرامی و سروش «کافه دوستی» برای کاربران الزامی است. اگر کسی عضو کانال نشود، یوزر او ساخته نمی شود و اگر کانال را ترک کند، یوزرش از سرور حذف می شود.
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

📢 کانال های اطلاع رسانی:
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
    # کاربران تلگرام
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
    # کاربران سروش پلاس
    c.execute('''
        CREATE TABLE IF NOT EXISTS splus_users (
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
    # رصد فعالیت سرور تیم‌تاک
    c.execute('''
        CREATE TABLE IF NOT EXISTS tt_activity (
            username TEXT PRIMARY KEY,
            note TEXT,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- متدهای دیتابیس تلگرام ---
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

def get_user_by_phone(phone):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT chat_id, step, persian_name, username, password FROM users WHERE phone=?", (phone,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "chat_id": row[0],
            "step": row[1],
            "persian_name": row[2],
            "username": row[3],
            "password": row[4]
        }
    return None

# --- متدهای دیتابیس سروش پلاس ---
def get_splus_user(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT step, persian_name, username, phone, sms_code, voice_file_id, password FROM splus_users WHERE chat_id=?", (chat_id,))
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

def set_splus_user(chat_id, **kwargs):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    user = get_splus_user(chat_id)
    if not user:
        c.execute("INSERT INTO splus_users (chat_id, step) VALUES (?, ?)", (chat_id, kwargs.get("step", "IDLE")))
    for k, v in kwargs.items():
        c.execute(f"UPDATE splus_users SET {k}=? WHERE chat_id=?", (v, chat_id))
    conn.commit()
    conn.close()

def get_splus_user_by_phone(phone):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT chat_id, step, persian_name, username, password FROM splus_users WHERE phone=?", (phone,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "chat_id": row[0],
            "step": row[1],
            "persian_name": row[2],
            "username": row[3],
            "password": row[4]
        }
    return None

# ----------------- کش و بررسی حساب‌های موجود در تیم‌تاک (ضد تکرار) -----------------
TT_CACHE = {"time": 0, "usernames": set(), "phones": set()}

def extract_iranian_phone(text):
    if not text:
        return None
    fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    clean = text.translate(fa_to_en).replace("+98", "0").replace(" ", "").replace("-", "")
    matches = re.findall(r'09\d{9}', clean)
    if matches:
        return matches[0]
    matches9 = re.findall(r'(?<!\d)9\d{9}(?!\d)', clean)
    if matches9:
        return "0" + matches9[0]
    return None

def get_tt_existing_cached():
    global TT_CACHE
    if time.time() - TT_CACHE["time"] < 180 and TT_CACHE["usernames"]:
        return TT_CACHE["usernames"], TT_CACHE["phones"]
    
    usernames = set()
    phones = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((TT_HOST, TT_PORT))
        s.recv(4096)
        cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="بررسی لیست کاربران" protocol="5.13" clientname="TeamTalk5"\r\n'
        s.sendall(cmd.encode('utf-8'))
        
        time.sleep(1.5)
        while True:
            try:
                data = s.recv(8192)
                if not data:
                    break
            except socket.timeout:
                break
                
        s.sendall(b'listaccounts\r\n')
        time.sleep(1)
        resp_list = b""
        while True:
            try:
                chunk = s.recv(8192)
                if not chunk:
                    break
                resp_list += chunk
            except socket.timeout:
                break
        s.close()
        
        text = resp_list.decode('utf-8', errors='ignore')
        for line in text.splitlines():
            if "useraccount" in line:
                u_m = re.search(r'username="([^"]+)"', line)
                n_m = re.search(r'note="([^"]*)"', line)
                if u_m:
                    u = u_m.group(1).strip().lower()
                    usernames.add(u)
                    note_str = n_m.group(1) if n_m else ""
                    if n_m:
                        p = extract_iranian_phone(note_str)
                        if p:
                            phones.add(p)
                    update_tt_last_seen(u, note=note_str)
                            
        TT_CACHE["time"] = time.time()
        TT_CACHE["usernames"] = usernames
        TT_CACHE["phones"] = phones
    except Exception as e:
        print(f"Error fetching TT accounts: {e}", flush=True)
        
    return TT_CACHE["usernames"], TT_CACHE["phones"]

# ----------------- رصد فعالیت، لاگین و حذف خودکار یوزرهای ۲ ماه غایب -----------------
PROTECTED_USERS = {"admin", "kaafehdoostibot", "kaafeh_nazer", "music player", "hivaplayer", "audio player", "omid.o", "yalda"}

def update_tt_last_seen(username, note=None):
    if not username:
        return
    username = username.strip().lower()
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if note:
            c.execute("""
                INSERT INTO tt_activity (username, note, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(username) DO UPDATE SET last_seen=CURRENT_TIMESTAMP, note=?
            """, (username, note, note))
        else:
            c.execute("""
                INSERT INTO tt_activity (username, last_seen)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(username) DO UPDATE SET last_seen=CURRENT_TIMESTAMP
            """, (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def delete_tt_account_server(username):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((TT_HOST, TT_PORT))
        s.recv(4096)
        cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="پاکسازی کاربر غایب" protocol="5.13" clientname="TeamTalk5"\r\n'
        s.sendall(cmd.encode('utf-8'))
        time.sleep(1)
        s.recv(8192)
        
        del_cmd = f'delaccount username="{username}"\r\n'
        s.sendall(del_cmd.encode('utf-8'))
        time.sleep(1)
        s.sendall(b'saveconfig\r\n')
        time.sleep(0.5)
        s.close()
        
        if username.lower() in TT_CACHE["usernames"]:
            TT_CACHE["usernames"].remove(username.lower())
        return True
    except Exception as e:
        print(f"Error deleting account {username}: {e}", flush=True)
        return False

def cleanup_inactive_users():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT username, note, last_seen FROM tt_activity WHERE last_seen < datetime('now', '-60 days')")
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            username, note, last_seen = row
            if username.lower() in PROTECTED_USERS:
                continue
            
            ok = delete_tt_account_server(username)
            if ok:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM tt_activity WHERE username=?", (username,))
                c.execute("UPDATE users SET step='DELETED_INACTIVE' WHERE LOWER(username)=?", (username.lower(),))
                c.execute("UPDATE splus_users SET step='DELETED_INACTIVE' WHERE LOWER(username)=?", (username.lower(),))
                conn.commit()
                conn.close()
                
                report = (
                    "🗑 گزارش پاکسازی خودکار سرور کافه دوستی:\n\n"
                    f"کاربر «{username}» به دلیل عدم لاگین و حضور در سرور به مدت ۲ ماه (۶۰ روز)، طبق قانون شماره ۷ سرور به صورت خودکار حذف شد.\n\n"
                    f"اطلاعات ثبت‌شده: {note if note else 'ندارد'}"
                )
                send_message(ADMIN_CHAT_ID, report)
    except Exception as e:
        print(f"Error in cleanup_inactive_users: {e}", flush=True)

def run_inactivity_checker():
    time.sleep(120)
    while True:
        try:
            cleanup_inactive_users()
        except Exception:
            pass
        time.sleep(86400) # هر ۲۴ ساعت یک بار بررسی می‌کند

def monitor_teamtalk_activity():
    """ربات ناظر جهت حضور دائم و بدون قطعی در سرور، پینگ خودکار و ثبت لاگین کاربران در کانال مدیریت (chanid=28)"""
    time.sleep(5)
    print("شروع به کار ربات ناظر کافه دوستی در کانال مدیریت...", flush=True)
    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect((TT_HOST, TT_PORT))
            s.recv(4096)
            login_cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="{TT_NAZER_NICKNAME}" protocol="5.13" clientname="TeamTalk5"\r\n'
            s.sendall(login_cmd.encode('utf-8'))
            time.sleep(1)
            # پیوستن مستقیم به کانال مدیریت کافه دوستی (chanid=28) با پسورد 12123123
            s.sendall(b'join chanid=28 password="12123123"\r\n')
            
            last_ping = time.time()
            buffer = ""
            
            while True:
                now = time.time()
                if now - last_ping >= 20:
                    try:
                        s.sendall(b'ping\r\n')
                        last_ping = now
                    except Exception:
                        break
                
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        print("اتصال ربات ناظر قطع شد؛ تلاش مجدد...", flush=True)
                        break
                    buffer += chunk.decode('utf-8', errors='ignore')
                    while '\r\n' in buffer:
                        line, buffer = buffer.split('\r\n', 1)
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith("ping"):
                            try:
                                s.sendall(b'pong\r\n')
                                last_ping = time.time()
                            except Exception:
                                pass
                        elif "removeuser" in line:
                            # اگر ربات رادیو در حال کار از سرور خارج شد یا کیک شد، ربات ناظر فوراً مطلع می‌شود
                            b = global_radio_bot
                            if b and getattr(b, "connected", False) and (time.time() - getattr(b, "created_at", 0) > 30):
                                my_uid = getattr(b, "my_user_id", -99)
                                if (my_uid > 0 and f"userid={my_uid}" in line) or "radio kaafehdoosti" in line:
                                    print("[Watchdog Event] ربات ناظر خروج آنی ربات رادیو را ثبت کرد. دستور بازگشت فوری صادر شد.", flush=True)
                                    if not getattr(b, "restart_requested", False):
                                        b.persist_state()
                                        b.restart_requested = True
                        elif "loggedin" in line or "adduser" in line or "updateuser" in line:
                            u_m = re.search(r'username="([^"]+)"', line)
                            if u_m:
                                u_name = u_m.group(1).strip().lower()
                                update_tt_last_seen(u_name)
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"خطا در ربات ناظر: {e}. اتصال مجدد ۵ ثانیه دیگر...", flush=True)
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        time.sleep(5)

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
    'امیری': 'amiri', 'علیایی': 'oliaiy', 'عُلیائی': 'oliaiy', 'عُلیایی': 'oliaiy',
    'محمدی': 'mohammadi', 'رضایی': 'rezaei', 'حسینی': 'hosseini',
    'کاظمی': 'kazemi', 'صادقی': 'sadeghi', 'سعید': 'saeed', 'وحید': 'vahid',
    'مجید': 'majid', 'حمید': 'hamid', 'نوید': 'navid', 'پیمان': 'peyman',
    'سامان': 'saman', 'کامران': 'kamran', 'آرش': 'arash', 'سروش': 'soroush',
    'نیما': 'nima', 'سینا': 'sina', 'پویا': 'pouya', 'میلاد': 'milad',
    'فرزاد': 'farzad', 'فرهاد': 'farhad', 'مبین': 'mobin', 'متین': 'matin',
    'آرمین': 'armin', 'احسان': 'ehsan', 'عرفان': 'erfan', 'پریسا': 'parisa',
    'نگین': 'negin', 'نازنین': 'nazanin', 'نرگس': 'narges', 'بهار': 'bahar',
    'نگار': 'negar', 'سپیده': 'sepideh', 'آرزو': 'arezoo', 'شیدا': 'sheyda',
    'الهام': 'elham', 'نیلوفر': 'niloufar', 'امیرعلی': 'amirali', 'امیرحسین': 'amirhossein',
    'امیرمحمد': 'amirmohammad', 'امیررضا': 'amirreza', 'امیرعباس': 'amirabbas',
    'امیرمهدی': 'amirmehdi', 'محمدحسین': 'mohammadhossein', 'محمدعلی': 'mohammadali',
    'محمدامین': 'mohammadamin', 'محمدجواد': 'mohammadjavad', 'محمدصادق': 'mohammadsadegh',
    'محمدحسن': 'mohammadhasan', 'احمدرضا': 'ahmadreza', 'حمیدرضا': 'hamidreza',
    'غلامرضا': 'gholamreza', 'عبدالرضا': 'abdolreza', 'امیدرضا': 'omidreza',
    'سید': 'seyed', 'سیده': 'seyedeh', 'میر': 'mir', 'احمد': 'ahmad',
    'محمود': 'mahmoud', 'مصطفی': 'mostafa', 'مرتضی': 'morteza', 'مجتبی': 'mojtaba',
    'عباس': 'abbas', 'ابوالفضل': 'abolfazl', 'بهنام': 'behnam', 'بهروز': 'behrooz',
    'بهمن': 'bahman', 'بابک': 'babak', 'بردیا': 'bardia', 'کیان': 'kian',
    'کیارش': 'kiarash', 'سهراب': 'sohrab', 'سام': 'sam', 'داریوش': 'dariush',
    'کوروش': 'kourosh', 'شهروز': 'shahrooz', 'شاهرخ': 'shahrokh', 'شهرام': 'shahram',
    'شهاب': 'shahab', 'اشکان': 'ashkan', 'فرشید': 'farshid', 'فرید': 'farid',
    'امیرحسام': 'amirhesam', 'حسام': 'hesam', 'دانیال': 'danial', 'رویا': 'roya',
    'مینا': 'mina', 'سمیرا': 'samira', 'سمانه': 'samaneh', 'سوسن': 'sousan',
    'شیما': 'shima', 'مونا': 'mona', 'مهسا': 'mahsa', 'مهتاب': 'mahtab',
    'مهدیه': 'mahdieh', 'زهره': 'zohreh', 'محدثه': 'mohaddeseh',
    'ستایش': 'setayesh', 'سوگند': 'sogand', 'عسل': 'asal', 'غزل': 'ghazal',
    'ترانه': 'taraneh', 'باران': 'baran', 'آیدا': 'ayda', 'آتنا': 'atena',
    'ریحانه': 'reyhaneh', 'رستم': 'rostam', 'رستمی': 'rostami', 'نادری': 'naderi',
    'عباسی': 'abbasi', 'موسوی': 'mousavi', 'کریمی': 'karimi', 'جعفری': 'jafari',
    'قاسمی': 'ghasemi', 'مرادی': 'moradi', 'ابراهیمی': 'ebrahimi', 'رحیمی': 'rahimi',
    'مطهری': 'motahari', 'حیدری': 'heidari', 'نجفی': 'najafi', 'احمدی': 'ahmadi',
    'باقری': 'bagheri', 'هاشمی': 'hashemi', 'طاهری': 'taheri', 'اسدی': 'asadi',
    'نوروزی': 'norouzi', 'صالحی': 'salehi', 'فلاح': 'fallah', 'اکبری': 'akbari',
    'شریفی': 'sharifi', 'قنبری': 'ghanbari', 'خسروی': 'khosravi', 'سلیمانی': 'soleimani',
    'خدادادی': 'khodadadi', 'دهقان': 'dehghan', 'عسگری': 'asgari', 'عزیزی': 'azizi',
    'فرهادی': 'farhadi', 'میرزایی': 'mirzaei'
}

def transliterate_word(w):
    clean_w = re.sub(r'[\u064B-\u065F\u0670]', '', w)
    clean_w = clean_w.replace('‌', '').replace('‌', '').strip()
    if clean_w in SPECIAL_NAMES:
        return SPECIAL_NAMES[clean_w]
    res = ""
    for ch in clean_w:
        res += PERSIAN_TO_EN.get(ch, ch)
    res = "".join(c for c in res.lower() if c.isalpha())
    return res

def persian_to_english(text):
    words = text.strip().split()
    if not words:
        return "user"
    en_words = [transliterate_word(w) for w in words if transliterate_word(w)]
    if not en_words:
        return "user"
    if len(en_words) == 1:
        return en_words[0]
    
    first_name = "".join(en_words[:-1])
    last_name_initial = en_words[-1][0] if en_words[-1] else ""
    if last_name_initial:
        username = f"{first_name}.{last_name_initial}"
    else:
        username = first_name
    return username.strip().lower()

# ----------------- سیستم دریافت مستقیم آخرین نسخه تیم‌تاک از سایت رسمی -----------------
TEAMTALK_CACHE = {
    "win_link": "https://bearware.dk/teamtalk/v5.23/TeamTalk_v5.23_Setup.exe",
    "time": 0
}

def get_latest_teamtalk_win_link():
    global TEAMTALK_CACHE
    if time.time() - TEAMTALK_CACHE["time"] < 3600 and TEAMTALK_CACHE["win_link"]:
        return TEAMTALK_CACHE["win_link"]
    try:
        url = "https://bearware.dk/?page_id=353"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'https?://bearware\.dk/teamtalk/[a-zA-Z0-9\._/]+Setup\.exe', html, re.I)
            if matches:
                TEAMTALK_CACHE["win_link"] = matches[0]
                TEAMTALK_CACHE["time"] = time.time()
    except Exception as e:
        print(f"Error fetching latest win link: {e}", flush=True)
    return TEAMTALK_CACHE["win_link"]

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

def send_voice_file(chat_id, filename, file_bytes, caption=None, reply_markup=None):
    boundary = "----WebKitFormBoundary" + secrets.token_hex(8)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
    if caption:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
    if reply_markup:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="reply_markup"\r\n\r\n{json.dumps(reply_markup)}\r\n'.encode('utf-8'))
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="voice"; filename="{filename}"\r\n'.encode())
    body.extend(b'Content-Type: audio/ogg\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f"--{boundary}--\r\n".encode())
    
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error sending voice file to Telegram: {e}", flush=True)
        # در صورت بروز مشکل در فرمت ogg، به صورت سند صوتی ارسال می‌شود
        return send_document_file(chat_id, filename, file_bytes, caption=caption, reply_markup=reply_markup)

def send_document_file(chat_id, filename, file_bytes, caption=None, reply_markup=None):
    boundary = "----WebKitFormBoundary" + secrets.token_hex(8)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
    if caption:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
    if reply_markup:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="reply_markup"\r\n\r\n{json.dumps(reply_markup)}\r\n'.encode('utf-8'))
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode())
    body.extend(b'Content-Type: application/octet-stream\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f"--{boundary}--\r\n".encode())
    
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error sending document: {e}", flush=True)
        return None

# بررسی عضویت در کانال تلگرامی کافه دوستی
def is_channel_member(user_id):
    res = tg_request("getChatMember", {"chat_id": CHANNEL_USERNAME, "user_id": user_id})
    if res and res.get("ok"):
        status = res.get("result", {}).get("status")
        return status in ["creator", "administrator", "member", "restricted"]
    return False

# ----------------- سروش پلاس ای‌پی‌آی -----------------
def splus_request(method, data=None, timeout=15):
    url = f"https://api.splus.ir/bot{SPLUS_TOKEN}/{method}"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"SPLUS API Error ({method}): {e}", flush=True)
        return None

def splus_send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return splus_request("sendMessage", payload)

def splus_download_file_bytes(file_id):
    try:
        res = splus_request("getFile", {"file_id": file_id})
        if res and res.get("ok"):
            file_path = res["result"].get("file_path")
            if file_path:
                dl_url = f"https://api.splus.ir/file/bot{SPLUS_TOKEN}/{file_path}"
                req = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=25) as resp:
                    return resp.read()
    except Exception as e:
        print(f"Error downloading file from SPLUS: {e}", flush=True)
    return None

def splus_send_document_file(chat_id, filename, file_bytes, caption=None, reply_markup=None):
    boundary = "----WebKitFormBoundary" + secrets.token_hex(8)
    url = f"https://api.splus.ir/bot{SPLUS_TOKEN}/sendDocument"
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
    if caption:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
    if reply_markup:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="reply_markup"\r\n\r\n{json.dumps(reply_markup)}\r\n'.encode('utf-8'))
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode())
    body.extend(b'Content-Type: application/octet-stream\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f"--{boundary}--\r\n".encode())
    
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error sending document to SPLUS: {e}", flush=True)
        return None

def splus_send_voice_file(chat_id, filename, file_bytes, caption=None, reply_markup=None):
    boundary = "----WebKitFormBoundary" + secrets.token_hex(8)
    url = f"https://api.splus.ir/bot{SPLUS_TOKEN}/sendVoice"
    
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode())
    if caption:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
    if reply_markup:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="reply_markup"\r\n\r\n{json.dumps(reply_markup)}\r\n'.encode('utf-8'))
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="voice"; filename="{filename}"\r\n'.encode())
    body.extend(b'Content-Type: audio/ogg\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')
    body.extend(f"--{boundary}--\r\n".encode())
    
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error sending voice to SPLUS: {e}", flush=True)
        # Fallback to document
        try:
            return splus_send_document_file(chat_id, filename, file_bytes, caption=caption, reply_markup=reply_markup)
        except Exception as e2:
            print(f"Fallback sendDocument to SPLUS error: {e2}", flush=True)
            return None

# بررسی عضویت در کانال سروش کافه دوستی
def is_splus_channel_member(user_id):
    if user_id == SPLUS_ADMIN_CHAT_ID:
        return True
    try:
        res = splus_request("getChatMember", {"chat_id": SPLUS_CHANNEL_USERNAME, "user_id": user_id}, timeout=3)
        if res and res.get("ok"):
            status = res.get("result", {}).get("status")
            return status in ["creator", "administrator", "member", "restricted"]
    except Exception as e:
        print(f"SPLUS getChatMember error: {e}", flush=True)
    return True

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
        s.recv(4096)
        
        login_cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="ساخت حساب کاربری" protocol="5.13" clientname="TeamTalk5"\r\n'
        s.sendall(login_cmd.encode('utf-8'))
        time.sleep(1)
        resp = s.recv(8192).decode('utf-8', errors='ignore')
        if "accepted" not in resp:
            s.close()
            return False, "عدم پذیرش ورود ادمین ربات به سرور تیم‌تاک"
        
        cmd_new = f'newaccount username="{username}" password="{password}" note="{phone}" usertype=1 userrights={TT_USER_RIGHTS} initchan="/" cmdflood=[10,60000]\r\n'
        s.sendall(cmd_new.encode('utf-8'))
        time.sleep(1)
        
        s.sendall(b'saveconfig\r\n')
        time.sleep(0.5)
        s.close()
        
        TT_CACHE["usernames"].add(username.lower())
        if phone:
            TT_CACHE["phones"].add(phone)
            
        return True, "حساب کاربری با موفقیت در تیم‌تاک ساخته شد."
    except Exception as e:
        return False, str(e)

# ----------------- بازیابی و به‌روزرسانی حساب کاربری تیم‌تاک -----------------
def reset_teamtalk_account(username, password, phone=""):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((TT_HOST, TT_PORT))
        s.recv(4096)
        login_cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="بازیابی رمز کاربر" protocol="5.13" clientname="TeamTalk5"\r\n'
        s.sendall(login_cmd.encode('utf-8'))
        time.sleep(1)
        s.recv(8192)
        
        del_cmd = f'delaccount username="{username}"\r\n'
        s.sendall(del_cmd.encode('utf-8'))
        time.sleep(0.5)
        
        cmd_new = f'newaccount username="{username}" password="{password}" note="{phone}" usertype=1 userrights={TT_USER_RIGHTS} initchan="/" cmdflood=[10,60000]\r\n'
        s.sendall(cmd_new.encode('utf-8'))
        time.sleep(0.5)
        
        s.sendall(b'saveconfig\r\n')
        time.sleep(0.5)
        s.close()
        
        TT_CACHE["usernames"].add(username.lower())
        if phone:
            TT_CACHE["phones"].add(phone)
        return True
    except Exception as e:
        print(f"Error resetting TT account {username}: {e}", flush=True)
        return False

def find_existing_account(search_query):
    query = search_query.strip()
    if not query:
        return None
    
    fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    clean_p = query.translate(fa_to_en).replace("+98", "0").replace(" ", "").replace("-", "")
    phone_candidate = None
    if clean_p.startswith("98"):
        phone_candidate = "0" + clean_p[2:]
    elif clean_p.startswith("9") and len(clean_p) == 10:
        phone_candidate = "0" + clean_p
    elif clean_p.startswith("09") and len(clean_p) == 11 and clean_p.isdigit():
        phone_candidate = clean_p
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if phone_candidate:
        c.execute("SELECT username, phone, persian_name, password FROM users WHERE phone=?", (phone_candidate,))
        row = c.fetchone()
        if row:
            conn.close()
            return {"username": row[0], "phone": row[1], "persian_name": row[2], "password": row[3]}
            
        c.execute("SELECT username, phone, persian_name, password FROM splus_users WHERE phone=?", (phone_candidate,))
        row_sp = c.fetchone()
        if row_sp:
            conn.close()
            return {"username": row_sp[0], "phone": row_sp[1], "persian_name": row_sp[2], "password": row_sp[3]}
            
        c.execute("SELECT username, note FROM tt_activity WHERE note LIKE ?", (f"%{phone_candidate}%",))
        row_act = c.fetchone()
        if row_act:
            conn.close()
            return {"username": row_act[0], "phone": phone_candidate, "persian_name": "", "password": ""}
            
    c.execute("SELECT username, phone, persian_name, password FROM users WHERE LOWER(username)=?", (query.lower(),))
    row = c.fetchone()
    if row:
        conn.close()
        return {"username": row[0], "phone": row[1], "persian_name": row[2], "password": row[3]}
        
    c.execute("SELECT username, phone, persian_name, password FROM splus_users WHERE LOWER(username)=?", (query.lower(),))
    row_sp = c.fetchone()
    if row_sp:
        conn.close()
        return {"username": row_sp[0], "phone": row_sp[1], "persian_name": row_sp[2], "password": row_sp[3]}
        
    c.execute("SELECT username, note FROM tt_activity WHERE LOWER(username)=?", (query.lower(),))
    row_act = c.fetchone()
    if row_act:
        conn.close()
        note_p = extract_iranian_phone(row_act[1]) if row_act[1] else ""
        return {"username": row_act[0], "phone": note_p, "persian_name": "", "password": ""}
        
    conn.close()
    
    u_set, p_set = get_tt_existing_cached()
    if query.lower() in u_set:
        return {"username": query.lower(), "phone": "", "persian_name": "", "password": ""}
    if phone_candidate and phone_candidate in p_set:
        return {"username": "", "phone": phone_candidate, "persian_name": "", "password": ""}
        
    return None

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
  <join>
   <channel>/</channel>
  </join>
  <clientsetup>
   <nickname>{nickname}</nickname>
  </clientsetup>
 </host>
</teamtalk>
'''
    return content.encode('utf-8')

# ==============================================================================
# ========================= بخش ۱: پیام‌ها و دکمه‌های تلگرام =========================
# ==============================================================================

def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    voice = msg.get("voice")
    user = get_user(chat_id)
    
    # دستور دریافت مستقیم لینک دانلود تیم‌تاک
    if text.lower() in ["/download", "دانلود", "دانلود تیمتاک", "دانلود تیم‌تاک", "تیمتاک", "download"]:
        dl_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود نسخه ویندوز (Windows) 💻", "callback_data": "dl_win"}],
                [{"text": "دانلود نسخه اندروید (Android) 📱", "callback_data": "dl_android"}],
                [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
            ]
        }
        dl_text = (
            "📥 دریافت آخرین نسخه رسمی نرم‌افزار تیم‌تاک:\n\n"
            "لطفاً سیستم‌عامل دستگاه خود را انتخاب کنید تا لینک مستقیم از سایت رسمی تیم‌تاک (BearWare) برای شما ارسال شود:"
        )
        send_message(chat_id, dl_text, dl_keyboard)
        return
    
    # دستور شروع فرآیند بازیابی حساب کاربری
    if text.lower() in ["/recover", "بازیابی", "بازیابی حساب", "بازیابی اکانت", "recover"]:
        set_user(chat_id, step="RECOVER_WAIT_INPUT")
        recovery_text = (
            "🔄 بازیابی حساب کاربری در کافه دوستی:\n\n"
            "مرحله اول:\n"
            "لطفاً نام کاربری (یوزرنیم) یا شماره موبایلی که قبلاً با آن در سرور حساب داشته‌اید را ارسال کنید:"
        )
        cancel_keyboard = {
            "inline_keyboard": [
                [{"text": "انصراف و بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
            ]
        }
        send_message(chat_id, recovery_text, cancel_keyboard)
        return
    
    if text == "/start":
        user_info = get_user(chat_id)
        if user_info and user_info.get("step") == "COMPLETED" and user_info.get("username"):
            keyboard = {
                "inline_keyboard": [
                    [{"text": "دریافت مجدد مشخصات حساب کاربری 📝", "callback_data": f"resend_{chat_id}"}],
                    [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "start_recover"}],
                    [{"text": "دانلود نرم‌افزار تیم‌تاک (اندروید و ویندوز) 📥", "callback_data": "dl_menu"}]
                ]
            }
            welcome_text = (
                "سلام و درود به شما رفیق باصفا ☕️✨\n\n"
                "شما قبلاً حساب کاربری اختصاصی خود را در سرور کافه دوستی دریافت کرده‌اید و هر کاربر تنها مجاز به داشتن یک حساب است.\n\n"
                f"نام کاربری شما: {user_info['username']}\n\n"
                "اگر مشخصات ورود، رمز عبور یا فایل اتصال را فراموش کرده‌اید، می‌توانید از طریق دکمه‌های زیر آن را دریافت نمایید."
            )
            send_message(chat_id, welcome_text, keyboard)
            
            admin_alert = (
                "🔔 گزارش هوشمند ربات کافه دوستی:\n\n"
                "⚠️ استارت مجدد در تلگرام توسط کاربر دارای اکانت!\n"
                f"👤 نام: {user_info.get('persian_name', 'نامشخص')}\n"
                f"🔤 نام کاربری: {user_info.get('username')}\n"
                f"📱 شماره تلفن: {user_info.get('phone', 'ندارد')}\n"
                f"💬 شناسه تلگرام: {chat_id}\n\n"
                "وضعیت: ربات از ثبت‌نام مجدد جلوگیری کرد."
            )
            send_message(ADMIN_CHAT_ID, admin_alert)
            return

        set_user(chat_id, step="IDLE")
        keyboard = {
            "inline_keyboard": [
                [{"text": "ورود به کافه دوستی و دریافت حساب ☕️✨", "callback_data": "start_register"}],
                [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "start_recover"}],
                [{"text": "دانلود نرم‌افزار تیم‌تاک (اندروید و ویندوز) 📥", "callback_data": "dl_menu"}]
            ]
        }
        welcome_text = (
            "هر جا که کلمات از سر مهر جاری شوند و دل‌ها بی‌نقاب کنار هم بنشینند، همان‌جا زندگی واقعی جریان دارد.\n\n"
            "به کافه دوستی خوش آمدید؛ سرپناهی از جنس صدا، ترانه و هم‌نشینی، برای کسانی که ارزش یک گفت‌وگوی زلال و از ته‌دل را می‌دانند. حضور شما در این فضا برای ما اتفاقی ارزشمند است و مشتاق شنیدن صدایتان در این جمع هستیم.\n\n"
            "برای دریافت کلید ورود به سرور یا بازیابی حساب، از دکمه‌های زیر استفاده کنید."
        )
        send_message(chat_id, welcome_text, keyboard)
        return
    
    if not user:
        set_user(chat_id, step="IDLE")
        return
    
    step = user["step"]

    if step == "RECOVER_WAIT_INPUT":
        if text in ["/start", "انصراف", "بازگشت", "منو"]:
            set_user(chat_id, step="IDLE")
            send_message(chat_id, "فرآیند بازیابی حساب لغو شد.")
            return
            
        acc = find_existing_account(text)
        if not acc or not acc.get("username"):
            not_found_kb = {
                "inline_keyboard": [
                    [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
                ]
            }
            send_message(
                chat_id,
                "⚠️ حسابی با این نام کاربری یا شماره موبایل در سرور کافه دوستی یافت نشد.\n\n"
                "لطفاً در نوشتن مشخصات دقت فرمایید و مجدداً ارسال کنید، یا برای ثبت‌نام حساب جدید از دکمه زیر به منوی اصلی بازگردید:",
                not_found_kb
            )
            return

        target_uname = acc["username"]
        target_phone = acc.get("phone", "")
        target_pname = acc.get("persian_name", "")
        
        set_user(chat_id, 
                 step="RECOVER_WAIT_VOICE", 
                 username=target_uname, 
                 phone=target_phone if target_phone else "",
                 persian_name=target_pname if target_pname else "")
        
        send_message(chat_id, f"✅ حساب کاربری «{target_uname}» در سرور کافه دوستی شناسایی شد.")
        time.sleep(0.5)
        step2_text = (
            "مرحله دوم (ارسال ویس درخواست بازیابی):\n"
            "لطفاً یک پیام صوتی (ویس) درون تلگرام ضبط و ارسال کنید و در آن موارد زیر را بگویید:\n"
            "۱. خودتان را کامل معرفی کنید (نام و نام خانوادگی، شهر و سن)\n"
            f"۲. صراحتاً اعلام کنید که درخواست بازیابی حساب کاربری «{target_uname}» را دارید.\n\n"
            "منتظر ارسال ویس شما هستیم..."
        )
        send_message(chat_id, step2_text)
        return

    if step == "RECOVER_WAIT_VOICE":
        if not voice:
            send_message(chat_id, "لطفاً درخواست بازیابی خود را به صورت پیام صوتی (ویس) در تلگرام ارسال فرمایید:")
            return
            
        voice_file_id = voice["file_id"]
        set_user(chat_id, step="RECOVER_WAIT_ADMIN", voice_file_id=voice_file_id)
        
        send_message(chat_id, "درخواست بازیابی حساب شما به همراه ویس دریافت شد ✅")
        time.sleep(0.5)
        send_message(chat_id, "اطلاعات برای مدیریت سرور کافه دوستی ارسال شد. پس از بررسی و تایید توسط مدیریت، مشخصات جدید و قوانین سرور در همین‌جا برای شما ارسال خواهد شد.")
        
        tg_user = msg.get("from", {})
        tg_uname = f"@{tg_user.get('username')}" if tg_user.get("username") else "بدون آیدی"
        target_uname = user.get("username", "نامشخص")
        target_phone = user.get("phone", "ثبت‌نشده")
        target_pname = user.get("persian_name", "نامشخص")
        
        admin_caption = (
            "🔄 درخواست بازیابی حساب کاربری در کافه دوستی (تلگرام):\n\n"
            f"🔤 نام کاربری تیم‌تاک: {target_uname}\n"
            f"📱 شماره تلفن: {target_phone if target_phone else 'ثبت‌نشده'}\n"
            f"👤 نام فارسی: {target_pname if target_pname else 'نامشخص'}\n"
            f"🆔 آیدی تلگرام: {tg_uname}\n"
            f"🔢 شناسه عددی تلگرام: {chat_id}\n\n"
            "لطفاً ویس ارسالی را گوش دهید و تصمیم‌گیری فرمایید:"
        )
        admin_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "تایید بازیابی و تحویل حساب ✅", "callback_data": f"app_rec_{chat_id}"},
                    {"text": "رد درخواست بازیابی ❌", "callback_data": f"rej_rec_{chat_id}"}
                ]
            ]
        }
        send_voice(ADMIN_CHAT_ID, voice_file_id, caption=admin_caption, reply_markup=admin_keyboard)
        return

    if step == "WAIT_NAME":
        if not text:
            send_message(chat_id, "لطفا نام و نام خانوادگی خود را به صورت متنی و فارسی ارسال کنید:")
            return
        persian_name = text
        username = persian_to_english(persian_name)
        
        u_set, p_set = get_tt_existing_cached()
        if username in u_set:
            dup_kb = {
                "inline_keyboard": [
                    [{"text": "بازیابی این حساب کاربری 🔄", "callback_data": "start_recover"}],
                    [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
                ]
            }
            dup_msg = (
                f"⚠️ کاربری با نام کاربری «{username}» از قبل در سرور کافه دوستی ثبت شده و دارای حساب فعال است.\n\n"
                "راهنمای بازیابی حساب:\n"
                "اگر این حساب متعلق به خود شماست و رمز عبور یا اطلاعات ورود را فراموش کرده‌اید، نیازی به ثبت‌نام مجدد ندارید؛ لطفاً دکمه «بازیابی این حساب کاربری» زیر را لمس کنید تا از طریق بخش بازیابی، حساب خود را تحویل بگیرید.\n\n"
                "در صورتی هم که این حساب متعلق به شما نیست و نام شما مشابه است، لطفاً نام خود را به همراه پسوند یا به صورت کامل‌تر بنویسید و ارسال کنید:"
            )
            send_message(chat_id, dup_msg, dup_kb)
            
            existing_acc = find_existing_account(username)
            existing_phone = existing_acc.get("phone", "ثبت‌نشده") if existing_acc else "ثبت‌نشده"
            existing_pname = existing_acc.get("persian_name", "") if existing_acc else ""
            pname_info = f" (صاحب حساب: {existing_pname})" if existing_pname else ""
            
            tg_user = msg.get("from", {})
            tg_username = f"@{tg_user.get('username')}" if tg_user.get('username') else "بدون آیدی"
            
            admin_alert = (
                "🔔 گزارش هوشمند ربات کافه دوستی:\n\n"
                "⚠️ تلاش برای ثبت‌نام با نام موجود در سرور (تلگرام)!\n"
                f"🔤 نام کاربری موجود در تیم‌تاک: {username}{pname_info}\n"
                f"📱 شماره تلفن صاحب حساب: {existing_phone}\n"
                f"👤 نام فارسی متقاضی جدید: {persian_name}\n"
                f"🆔 آیدی تلگرام: {tg_username}\n"
                f"🔢 شناسه عددی تلگرام: {chat_id}\n\n"
                "وضعیت: از ایجاد یوزر تکراری جلوگیری شد."
            )
            send_message(ADMIN_CHAT_ID, admin_alert)
            splus_send_message(SPLUS_ADMIN_CHAT_ID, admin_alert)
            return

        set_user(chat_id, step="WAIT_PHONE", persian_name=persian_name, username=username)
        confirm_name_msg = (
            f"نام فارسی شما: {persian_name}\n"
            f"نام کاربری انگلیسی پیشنهادی شما: {username} ✅"
        )
        send_message(chat_id, confirm_name_msg)
        time.sleep(0.5)
        send_message(chat_id, "حالا لطفاً شماره موبایل خود را به صورت ۱۱ رقمی (مانند: ۰۹۱۲۳۴۵۶۷۸۹) وارد کنید:")
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
        
        # بررسی عدم تکراری بودن شماره تلفن (در سرور تیم‌تاک، دیتابیس تلگرام و سروش)
        u_set, p_set = get_tt_existing_cached()
        db_user = get_user_by_phone(clean_phone)
        sp_user = get_splus_user_by_phone(clean_phone)
        
        if clean_phone in p_set or (db_user and db_user.get("step") == "COMPLETED" and db_user.get("chat_id") != chat_id) or (sp_user and sp_user.get("step") == "COMPLETED"):
            dup_kb = {
                "inline_keyboard": [
                    [{"text": "بازیابی این حساب کاربری 🔄", "callback_data": "start_recover"}],
                    [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
                ]
            }
            dup_msg = (
                f"⚠️ شماره موبایل «{clean_phone}» قبلاً در سرور کافه دوستی ثبت شده و دارای حساب کاربری فعال است.\n\n"
                "طبق قوانین سرور، هر کاربر تنها مجاز به داشتن یک حساب است و امکان ساخت حساب مجدد یا تکراری وجود ندارد.\n\n"
                "راهنمای بازیابی حساب:\n"
                "اگر این شماره متعلق به خود شماست و قبلاً در سرور حساب داشته‌اید، لطفاً با لمس دکمه «بازیابی این حساب کاربری» زیر اقدام کنید تا با ارسال ویس معرفی، مشخصات جدید حساب پس از تایید مدیریت برای شما ارسال شود."
            )
            send_message(chat_id, dup_msg, dup_kb)
            
            existing_acc = find_existing_account(clean_phone)
            existing_tt_user = existing_acc.get("username", "یافت نشد") if existing_acc else "یافت نشد"
            existing_name = existing_acc.get("persian_name", "") if existing_acc else ""
            name_info = f" (به نام: {existing_name})" if existing_name else ""
            
            tg_user = msg.get("from", {})
            tg_username = f"@{tg_user.get('username')}" if tg_user.get('username') else "بدون آیدی"
            
            admin_alert = (
                "🔔 گزارش هوشمند ربات کافه دوستی:\n\n"
                "⚠️ تلاش برای ثبت‌نام با شماره تکراری در تلگرام!\n"
                f"📱 شماره تلفن واردشده: {clean_phone}\n"
                f"🔤 نام کاربری موجود در تیم‌تاک: {existing_tt_user}{name_info}\n"
                f"👤 نام فارسی متقاضی جدید: {user.get('persian_name', 'نامشخص')}\n"
                f"🆔 آیدی تلگرام: {tg_username}\n"
                f"🔢 شناسه عددی تلگرام: {chat_id}\n\n"
                "وضعیت: این شماره از قبل دارای اکانت در سرور است و درخواست مسدود شد."
            )
            send_message(ADMIN_CHAT_ID, admin_alert)
            splus_send_message(SPLUS_ADMIN_CHAT_ID, admin_alert)
            return
        
        set_user(chat_id, step="WAIT_VOICE", phone=clean_phone)
        send_message(chat_id, f"شماره موبایل شما ({clean_phone}) با موفقیت ثبت شد ✅")
        time.sleep(0.5)
        voice_prompt = (
            "مرحله پایانی (ویس معرفی):\n"
            "لطفاً یک پیام صوتی (ویس) درون تلگرام ضبط و ارسال کنید و در آن موارد زیر را بگویید:\n"
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
        
        send_message(chat_id, "ویس و پرونده معرفی شما با موفقیت دریافت شد ✅")
        time.sleep(0.5)
        send_message(chat_id, "اطلاعات شما برای مدیریت سرور کافه دوستی ارسال گردید. به محض بررسی و تایید توسط مدیریت، نتیجه در همین‌جا به شما اعلام خواهد شد.")
        
        user_info = get_user(chat_id)
        tg_user = msg.get("from", {})
        tg_username = f"@{tg_user.get('username')}" if tg_user.get('username') else "بدون آیدی"
        
        caption = (
            "🔔 درخواست عضویت و حساب جدید در کافه دوستی (تلگرام):\n\n"
            f"👤 نام فارسی: {user_info['persian_name']}\n"
            f"🔤 نام کاربری انگلیسی پیشنهادی: {user_info['username']}\n"
            f"📱 شماره موبایل: {user_info['phone']}\n"
            f"🆔 آیدی تلگرام: {tg_username}\n"
            f"🔢 شناسه عددی تلگرام: {chat_id}\n\n"
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

def handle_callback_query(cq):
    cq_id = cq["id"]
    from_user = cq["from"]["id"]
    data = cq.get("data", "")
    msg = cq.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    message_id = msg.get("message_id")
    
    tg_request("answerCallbackQuery", {"callback_query_id": cq_id})
    
    # منوی دانلود تیم‌تاک
    if data == "dl_menu":
        dl_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود نسخه ویندوز (Windows) 💻", "callback_data": "dl_win"}],
                [{"text": "دانلود نسخه اندروید (Android) 📱", "callback_data": "dl_android"}],
                [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
            ]
        }
        dl_text = (
            "📥 دریافت آخرین نسخه رسمی نرم‌افزار تیم‌تاک:\n\n"
            "لطفاً سیستم‌عامل دستگاه خود را انتخاب کنید تا لینک مستقیم از سایت رسمی تیم‌تاک (BearWare) برای شما ارسال شود:"
        )
        send_message(from_user, dl_text, dl_keyboard)
        return

    if data == "dl_win":
        win_link = get_latest_teamtalk_win_link()
        win_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود مستقیم نسخه ویندوز 📥", "url": win_link}],
                [{"text": "بازگشت به منوی دانلود 🔙", "callback_data": "dl_menu"}]
            ]
        }
        msg_str = (
            "💻 دانلود آخرین نسخه رسمی تیم‌تاک برای ویندوز (Windows):\n\n"
            "لینک دانلود مستقیم و رسمی از سرور اصلی تیم‌تاک (BearWare):\n"
            f"{win_link}\n\n"
            "پس از دانلود، فایل نصبی را اجرا کرده و مراحل نصب را انجام دهید."
        )
        send_message(from_user, msg_str, win_keyboard)
        return

    if data == "dl_android":
        android_play_link = "https://play.google.com/store/apps/details?id=dk.bearware.gui"
        android_apk_link = "https://d.apkpure.com/b/APK/dk.bearware.gui?version=latest"
        android_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود از گوگل‌پلی (سایت رسمی تیم‌تاک) 🌐", "url": android_play_link}],
                [{"text": "دانلود مستقیم فایل نصبی (APK) 📥", "url": android_apk_link}],
                [{"text": "بازگشت به منوی دانلود 🔙", "callback_data": "dl_menu"}]
            ]
        }
        msg_str = (
            "📱 دانلود آخرین نسخه رسمی تیم‌تاک برای اندروید (Android):\n\n"
            "۱. لینک رسمی تیم‌تاک در فروشگاه گوگل‌پلی (سایت اصلی تیم‌تاک):\n"
            f"{android_play_link}\n\n"
            "۲. لینک دانلود مستقیم فایل نصبی (APK) در صورت عدم دسترسی به گوگل‌پلی:\n"
            f"{android_apk_link}\n\n"
            "با لمس هر یک از دکمه‌های زیر، برنامه به طور مستقیم دانلود خواهد شد."
        )
        send_message(from_user, msg_str, android_keyboard)
        return

    if data == "back_to_main":
        user_info = get_user(from_user)
        if user_info and user_info.get("step") == "COMPLETED" and user_info.get("username"):
            keyboard = {
                "inline_keyboard": [
                    [{"text": "دریافت مجدد مشخصات حساب کاربری 📝", "callback_data": f"resend_{from_user}"}],
                    [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "start_recover"}],
                    [{"text": "دانلود نرم‌افزار تیم‌تاک (اندروید و ویندوز) 📥", "callback_data": "dl_menu"}]
                ]
            }
            welcome_text = (
                "سلام و درود به شما رفیق باصفا ☕️✨\n\n"
                f"نام کاربری شما در سرور کافه دوستی: {user_info['username']}\n\n"
                "از طریق دکمه‌های زیر می‌توانید مشخصات، بازیابی یا نرم‌افزار را دریافت نمایید."
            )
            send_message(from_user, welcome_text, keyboard)
            return
        else:
            keyboard = {
                "inline_keyboard": [
                    [{"text": "ورود به کافه دوستی و دریافت حساب ☕️✨", "callback_data": "start_register"}],
                    [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "start_recover"}],
                    [{"text": "دانلود نرم‌افزار تیم‌تاک (اندروید و ویندوز) 📥", "callback_data": "dl_menu"}]
                ]
            }
            welcome_text = (
                "به کافه دوستی خوش آمدید ☕️✨\n\n"
                "برای دریافت حساب کاربری، بازیابی حساب یا دانلود برنامه از دکمه‌های زیر استفاده کنید:"
            )
            send_message(from_user, welcome_text, keyboard)
            return

    # شروع فرآیند بازیابی حساب در تلگرام
    if data == "start_recover":
        set_user(from_user, step="RECOVER_WAIT_INPUT")
        recovery_text = (
            "🔄 بازیابی حساب کاربری در کافه دوستی:\n\n"
            "مرحله اول:\n"
            "لطفاً نام کاربری (یوزرنیم) یا شماره موبایلی که قبلاً با آن در سرور حساب داشته‌اید را ارسال کنید:"
        )
        cancel_keyboard = {
            "inline_keyboard": [
                [{"text": "انصراف و بازگشت به منوی اصلی 🔙", "callback_data": "back_to_main"}]
            ]
        }
        send_message(from_user, recovery_text, cancel_keyboard)
        return

    if data in ["start_register", "check_join"]:
        user_info = get_user(from_user)
        if user_info and user_info.get("step") == "COMPLETED" and user_info.get("username"):
            resend_keyboard = {
                "inline_keyboard": [
                    [{"text": "دریافت مجدد مشخصات حساب 📝", "callback_data": f"resend_{from_user}"}],
                    [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "start_recover"}],
                    [{"text": "دانلود نرم‌افزار تیم‌تاک 📥", "callback_data": "dl_menu"}]
                ]
            }
            send_message(
                from_user,
                "⚠️ شما قبلاً حساب کاربری خود را در سرور کافه دوستی دریافت کرده‌اید و هر کاربر تنها مجاز به داشتن یک حساب است.\n\n"
                f"نام کاربری شما: {user_info['username']}\n\n"
                "اگر مشخصات ورود یا رمز خود را فراموش کرده‌اید، می‌توانید از طریق دکمه «بازیابی حساب کاربری» زیر اقدام فرمایید:\n"
                "@pkaafehdoosti",
                resend_keyboard
            )
            return

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
        
        set_user(from_user, step="WAIT_NAME")
        send_message(from_user, "عضویت شما در کانال کافه دوستی تایید شد ✅")
        time.sleep(0.5)
        send_message(from_user, "لطفاً نام و نام خانوادگی خود را به زبان فارسی (مانند: امید علیایی) بنویسید و ارسال کنید:")
        return

    # ارسال مجدد مشخصات به کاربر تلگرام
    if data.startswith("resend_"):
        target_chat_id = int(data.split("_")[1])
        user_info = get_user(target_chat_id)
        if user_info and user_info.get("password"):
            delivery_keyboard = {
                "inline_keyboard": [
                    [{"text": "دریافت فایل آماده ورود (فایل TT) 📁", "callback_data": f"get_tt_{target_chat_id}"}],
                    [{"text": "دریافت مشخصات به صورت متن 📝", "callback_data": f"get_txt_{target_chat_id}"}],
                    [{"text": "دریافت هر دو حالت (متن و فایل) ✨", "callback_data": f"get_both_{target_chat_id}"}]
                ]
            }
            send_message(target_chat_id, "اطلاعات ورود خود را چگونه مایلید دریافت کنید؟", delivery_keyboard)
            return
    
    # ----------------- تایید / رد درخواست‌های تلگرام توسط مدیر -----------------
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
        
        ok, res = create_teamtalk_account(username, password_30, phone)
        if not ok:
            send_message(ADMIN_CHAT_ID, f"خطا در ساخت اکانت در سرور تیم‌تاک:\n{res}")
            return
        
        set_user(target_chat_id, step="COMPLETED", password=password_30)
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"✅ تایید شد: حساب کاربری «{user_info['persian_name']}» (نام کاربری: {username} | تلفن: {phone}) با موفقیت ساخته شد.")
        
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
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"❌ رد شد: درخواست عضویت تلگرام برای «{persian_name}» (نام کاربری پیشنهادی: {user_info.get('username', '')}) توسط مدیریت رد شد.")
        
        rejection_msg = (
            "درود و احترام؛\n\n"
            "ضمن قدردانی از ابراز لطف و همراهی شما با مجموعه کافه دوستی، به اطلاع می‌رسانیم که پس از بررسی تیم مدیریت، متاسفانه در حال حاضر امکان تایید درخواست عضویت شما وجود ندارد.\n\n"
            "با آرزوی بهروزی، شادکامی و موفقیت روزافزون برای شما. 🌸"
        )
        send_message(target_chat_id, rejection_msg)
        return

    # تایید بازیابی تلگرام توسط مدیر
    if data.startswith("app_rec_") and not data.startswith("app_rec_sp_"):
        target_chat_id = int(data.split("_")[-1])
        user_info = get_user(target_chat_id)
        if not user_info:
            send_message(ADMIN_CHAT_ID, "اطلاعات کاربر یافت نشد.")
            return
            
        username = user_info["username"]
        phone = user_info.get("phone", "")
        persian_name = user_info.get("persian_name", "")
        
        chars = string.ascii_letters + string.digits
        password_30 = ''.join(secrets.choice(chars) for _ in range(30))
        
        ok = reset_teamtalk_account(username, password_30, phone)
        if not ok:
            send_message(ADMIN_CHAT_ID, f"خطا در بازیابی اکانت {username} در سرور تیم‌تاک.")
            return
            
        set_user(target_chat_id, step="COMPLETED", password=password_30)
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"✅ تایید شد: بازیابی حساب کاربری تلگرام برای «{username}» (نام: {persian_name} | تلفن: {phone if phone else 'ثبت‌نشده'}) انجام و مشخصات جدید ارسال شد.")
        
        send_message(target_chat_id, "🎉 تبریک! درخواست بازیابی حساب کاربری شما توسط مدیریت تایید شد.\n\nمشخصات اتصال جدید شما به سرور کافه دوستی:")
        send_message(target_chat_id, f"مشخصات سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
        send_message(target_chat_id, f"نام کاربری شما:\n{username}")
        send_message(target_chat_id, f"رمز عبور جدید شما:\n{password_30}")
        
        tt_bytes = generate_tt_file_bytes(username, password_30, persian_name if persian_name else username)
        filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
        send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        send_message(target_chat_id, rules_header + RULES_TEXT)
        return

    # رد درخواست بازیابی تلگرام توسط مدیر
    if data.startswith("rej_rec_") and not data.startswith("rej_rec_sp_"):
        target_chat_id = int(data.split("_")[-1])
        user_info = get_user(target_chat_id)
        uname = user_info.get("username", str(target_chat_id)) if user_info else str(target_chat_id)
        set_user(target_chat_id, step="REJECTED")
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"❌ رد شد: درخواست بازیابی حساب کاربری تلگرام برای «{uname}» توسط مدیریت رد شد.")
        
        rejection_msg = (
            "درود و احترام؛\n\n"
            "ضمن قدردانی از همراهی شما، به اطلاع می‌رسانیم که پس از بررسی تیم مدیریت کافه دوستی، متاسفانه درخواست بازیابی حساب کاربری شما تایید نشد.\n\n"
            "با آرزوی موفقیت و بهروزی برای شما. 🌸"
        )
        send_message(target_chat_id, rejection_msg)
        return
    
    # ----------------- تایید / رد درخواست‌های سروش پلاس توسط مدیر -----------------
    if data.startswith("app_sp_"):
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        if not user_info:
            send_message(ADMIN_CHAT_ID, "اطلاعات کاربر در سروش یافت نشد.")
            return
        
        if user_info.get("step") == "COMPLETED":
            tg_request("answerCallbackQuery", {
                "callback_query_id": cq_id,
                "text": "این کاربر سروش قبلاً تایید و یوزرش ساخته شده است.",
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
        phone = user_info.get("phone", "")
        persian_name = user_info.get("persian_name", username)
        
        ok, res = create_teamtalk_account(username, password_30, phone)
        if not ok:
            send_message(ADMIN_CHAT_ID, f"خطا در ساخت اکانت سرور تیم‌تاک برای کاربر سروش:\n{res}")
            return
            
        set_splus_user(target_chat_id, step="COMPLETED", password=password_30)
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"✅ تایید شد: حساب کاربری متقاضی سروش «{persian_name}» (نام کاربری: {username} | تلفن: {phone}) ساخته و در سروش ارسال شد.")
        
        # ارسال مشخصات، فایل tt و قوانین به کاربر در سروش
        splus_send_message(target_chat_id, "🎉 تبریک! حساب کاربری شما در سرور تیم‌تاک کافه دوستی توسط مدیریت تایید و ساخته شد.")
        splus_send_message(target_chat_id, f"مشخصات اتصال به سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
        splus_send_message(target_chat_id, f"نام کاربری شما:\n{username}")
        splus_send_message(target_chat_id, f"رمز عبور اختصاصی شما:\n{password_30}")
        
        tt_bytes = generate_tt_file_bytes(username, password_30, persian_name)
        filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
        splus_send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        splus_send_message(target_chat_id, rules_header + RULES_TEXT)
        splus_send_message(SPLUS_ADMIN_CHAT_ID, f"🔔 گزارش مدیریت:\nدرخواست عضویت سروش برای «{username}» توسط شما از طریق تلگرام تایید و ساخته شد ✅")
        return

    if data.startswith("rej_sp_"):
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        persian_name = user_info['persian_name'] if user_info else 'کاربر'
        set_splus_user(target_chat_id, step="REJECTED")
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"❌ رد شد: درخواست عضویت متقاضی سروش «{persian_name}» (شناسه: {target_chat_id}) توسط مدیریت رد شد.")
        
        rejection_msg = (
            "درود و احترام؛\n\n"
            "ضمن قدردانی از ابراز لطف و همراهی شما با مجموعه کافه دوستی، به اطلاع می‌رسانیم که پس از بررسی تیم مدیریت، متاسفانه در حال حاضر امکان تایید درخواست عضویت شما وجود ندارد.\n\n"
            "با آرزوی بهروزی، شادکامی و موفقیت روزافزون برای شما. 🌸"
        )
        splus_send_message(target_chat_id, rejection_msg)
        splus_send_message(SPLUS_ADMIN_CHAT_ID, f"🔔 گزارش مدیریت:\nدرخواست عضویت سروش برای «{persian_name}» توسط شما از طریق تلگرام رد شد ❌")
        return

    # تایید بازیابی سروش پلاس توسط مدیر
    if data.startswith("app_rec_sp_"):
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        if not user_info:
            send_message(ADMIN_CHAT_ID, "اطلاعات کاربر سروش یافت نشد.")
            return
            
        username = user_info["username"]
        phone = user_info.get("phone", "")
        persian_name = user_info.get("persian_name", "")
        
        chars = string.ascii_letters + string.digits
        password_30 = ''.join(secrets.choice(chars) for _ in range(30))
        
        ok = reset_teamtalk_account(username, password_30, phone)
        if not ok:
            send_message(ADMIN_CHAT_ID, f"خطا در بازیابی اکانت سروش {username} در سرور تیم‌تاک.")
            return
            
        set_splus_user(target_chat_id, step="COMPLETED", password=password_30)
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"✅ تایید شد: بازیابی حساب کاربری متقاضی سروش «{username}» (نام: {persian_name}) تایید و مشخصات در سروش تحویل داده شد.")
        
        splus_send_message(target_chat_id, "🎉 تبریک! درخواست بازیابی حساب کاربری شما توسط مدیریت تایید شد.\n\nمشخصات اتصال جدید شما به سرور کافه دوستی:")
        splus_send_message(target_chat_id, f"مشخصات سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
        splus_send_message(target_chat_id, f"نام کاربری شما:\n{username}")
        splus_send_message(target_chat_id, f"رمز عبور جدید شما:\n{password_30}")
        
        tt_bytes = generate_tt_file_bytes(username, password_30, persian_name if persian_name else username)
        filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
        splus_send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        splus_send_message(target_chat_id, rules_header + RULES_TEXT)
        splus_send_message(SPLUS_ADMIN_CHAT_ID, f"🔔 گزارش مدیریت:\nدرخواست عضویت سروش برای «{username}» توسط شما از طریق تلگرام تایید و ساخته شد ✅")
        return

    # رد درخواست بازیابی سروش پلاس توسط مدیر
    if data.startswith("rej_rec_sp_"):
        target_chat_id = int(data.split("_")[-1])
        set_splus_user(target_chat_id, step="REJECTED")
        
        # پاک نشدن اطلاعات روی ویس: فقط حذف دکمه‌ها و ارسال پیام وضعیت جداگانه
        tg_request("editMessageReplyMarkup", {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": []}
        })
        send_message(ADMIN_CHAT_ID, f"❌ رد شد: درخواست بازیابی متقاضی سروش (شناسه: {target_chat_id}) توسط مدیریت رد شد.")
        
        rejection_msg = (
            "درود و احترام؛\n\n"
            "ضمن قدردانی از همراهی شما، به اطلاع می‌رسانیم که پس از بررسی تیم مدیریت کافه دوستی، متاسفانه درخواست بازیابی حساب کاربری شما تایید نشد.\n\n"
            "با آرزوی موفقیت و بهروزی برای شما. 🌸"
        )
        splus_send_message(target_chat_id, rejection_msg)
        splus_send_message(SPLUS_ADMIN_CHAT_ID, "🔔 گزارش مدیریت:\nدرخواست بازیابی متقاضی سروش توسط شما از طریق تلگرام رد شد ❌")
        return

    # دکمه‌های تحویل اکانت به کاربر تلگرام
    if data.startswith("get_tt_") or data.startswith("get_txt_") or data.startswith("get_both_"):
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
        
        if "txt" in data or "both" in data:
            send_message(target_chat_id, f"مشخصات اتصال به سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
            send_message(target_chat_id, f"نام کاربری شما:\n{username}")
            send_message(target_chat_id, f"رمز عبور شما:\n{password}")
        
        if "tt" in data or "both" in data:
            tt_bytes = generate_tt_file_bytes(username, password, persian_name)
            filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
            send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        send_message(target_chat_id, rules_header + RULES_TEXT)
        return

# ==============================================================================
# ========================= بخش ۲: پیام‌ها و دکمه‌های سروش پلاس =========================
# ==============================================================================

def send_splus_main_menu(chat_id):
    user_info = get_splus_user(chat_id)
    if user_info and user_info.get("step") == "COMPLETED" and user_info.get("username"):
        keyboard = {
            "inline_keyboard": [
                [{"text": "دریافت مجدد مشخصات حساب کاربری 📝", "callback_data": f"sp_resend_{chat_id}"}],
                [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "sp_start_recover"}],
                [{"text": "دانلود نرم‌افزار تیم‌تاک (اندروید و ویندوز) 📥", "callback_data": "sp_dl_menu"}]
            ]
        }
        welcome_text = (
            "سلام و درود به شما رفیق باصفا ☕️✨\n\n"
            "شما قبلاً حساب کاربری اختصاصی خود را در سرور کافه دوستی دریافت کرده‌اید و هر کاربر تنها مجاز به داشتن یک حساب است.\n\n"
            f"نام کاربری شما: {user_info['username']}\n\n"
            "اگر مشخصات ورود، رمز عبور یا فایل اتصال را فراموش کرده‌اید، می‌توانید از طریق دکمه‌های زیر آن را دریافت نمایید."
        )
        splus_send_message(chat_id, welcome_text, keyboard)
        return

    set_splus_user(chat_id, step="IDLE")
    keyboard = {
        "inline_keyboard": [
            [{"text": "ورود به کافه دوستی و دریافت حساب ☕️✨", "callback_data": "sp_start_register"}],
            [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "sp_start_recover"}],
            [{"text": "دانلود نرم‌افزار تیم‌تاک (اندروید و ویندوز) 📥", "callback_data": "sp_dl_menu"}]
        ]
    }
    welcome_text = (
        "هر جا که کلمات از سر مهر جاری شوند و دل‌ها بی‌نقاب کنار هم بنشینند، همان‌جا زندگی واقعی جریان دارد.\n\n"
        "به کافه دوستی خوش آمدید؛ سرپناهی از جنس صدا، ترانه و هم‌نشینی، برای کسانی که ارزش یک گفت‌وگوی زلال و از ته‌دل را می‌دانند. حضور شما در این فضا برای ما اتفاقی ارزشمند است و مشتاق شنیدن صدایتان در این جمع هستیم.\n\n"
        "برای دریافت کلید ورود به سرور یا بازیابی حساب، از دکمه‌های زیر استفاده کنید."
    )
    splus_send_message(chat_id, welcome_text, keyboard)

def handle_splus_message(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    voice = msg.get("voice") or msg.get("audio")
    user = get_splus_user(chat_id)
    
    if chat_id == SPLUS_ADMIN_CHAT_ID and text.lower() in ["/reset", "ریست", "حذف"]:
        set_splus_user(chat_id, step="IDLE", username="", phone="", password="", persian_name="", voice_file_id="")
        splus_send_message(chat_id, "وضعیت حساب کاربری شما در سروش ریست شد. اکنون می‌توانید مراحل را به صورت کامل و از ابتدا تست نمایید.")
        send_splus_main_menu(chat_id)
        return
    
    # دستور دریافت لینک مستقیم دانلود
    if text.lower() in ["/download", "دانلود", "دانلود تیمتاک", "دانلود تیم‌تاک", "تیمتاک", "download"]:
        dl_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود نسخه ویندوز (Windows) 💻", "callback_data": "sp_dl_win"}],
                [{"text": "دانلود نسخه اندروید (Android) 📱", "callback_data": "sp_dl_android"}],
                [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
            ]
        }
        dl_text = (
            "📥 دریافت آخرین نسخه رسمی نرم‌افزار تیم‌تاک:\n\n"
            "لطفاً سیستم‌عامل دستگاه خود را انتخاب کنید تا لینک مستقیم از سایت رسمی تیم‌تاک (BearWare) برای شما ارسال شود:"
        )
        splus_send_message(chat_id, dl_text, dl_keyboard)
        return

    # دستور شروع فرآیند بازیابی حساب
    if text.lower() in ["/recover", "بازیابی", "بازیابی حساب", "بازیابی اکانت", "recover"]:
        set_splus_user(chat_id, step="RECOVER_WAIT_INPUT")
        recovery_text = (
            "🔄 بازیابی حساب کاربری در کافه دوستی:\n\n"
            "مرحله اول:\n"
            "لطفاً نام کاربری (یوزرنیم) یا شماره موبایلی که قبلاً با آن در سرور حساب داشته‌اید را ارسال کنید:"
        )
        cancel_keyboard = {
            "inline_keyboard": [
                [{"text": "انصراف و بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
            ]
        }
        splus_send_message(chat_id, recovery_text, cancel_keyboard)
        return
        
    if text == "/start" or text == "شروع":
        send_splus_main_menu(chat_id)
        return
        
    if not user:
        set_splus_user(chat_id, step="IDLE")
        send_splus_main_menu(chat_id)
        return
        
    step = user["step"]

    # مرحله اول بازیابی در سروش: دریافت یوزرنیم یا شماره موبایل
    if step == "RECOVER_WAIT_INPUT":
        if text in ["/start", "انصراف", "بازگشت", "منو"]:
            set_splus_user(chat_id, step="IDLE")
            splus_send_message(chat_id, "فرآیند بازیابی حساب لغو شد.")
            send_splus_main_menu(chat_id)
            return
            
        acc = find_existing_account(text)
        if not acc or not acc.get("username"):
            not_found_kb = {
                "inline_keyboard": [
                    [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
                ]
            }
            splus_send_message(
                chat_id,
                "⚠️ حسابی با این نام کاربری یا شماره موبایل در سرور کافه دوستی یافت نشد.\n\n"
                "لطفاً در نوشتن مشخصات دقت فرمایید و مجدداً ارسال کنید، یا برای ثبت‌نام حساب جدید از دکمه زیر به منوی اصلی بازگردید:",
                not_found_kb
            )
            return

        target_uname = acc["username"]
        target_phone = acc.get("phone", "")
        target_pname = acc.get("persian_name", "")
        
        set_splus_user(chat_id, 
                       step="RECOVER_WAIT_VOICE", 
                       username=target_uname, 
                       phone=target_phone if target_phone else "",
                       persian_name=target_pname if target_pname else "")
        
        splus_send_message(chat_id, f"✅ حساب کاربری «{target_uname}» در سرور کافه دوستی شناسایی شد.")
        time.sleep(0.5)
        step2_text = (
            "مرحله دوم (ارسال ویس درخواست بازیابی):\n"
            "لطفاً یک پیام صوتی (ویس) درون سروش ضبط و ارسال کنید و در آن موارد زیر را بگویید:\n"
            "۱. خودتان را کامل معرفی کنید (نام و نام خانوادگی، شهر و سن)\n"
            f"۲. صراحتاً اعلام کنید که درخواست بازیابی حساب کاربری «{target_uname}» را دارید.\n\n"
            "منتظر ارسال ویس شما هستیم..."
        )
        splus_send_message(chat_id, step2_text)
        return

    # مرحله دوم بازیابی در سروش: دریافت ویس و ارسال به تلگرام ادمین
    if step == "RECOVER_WAIT_VOICE":
        if not voice:
            splus_send_message(chat_id, "لطفاً درخواست بازیابی خود را به صورت پیام صوتی (ویس) در سروش ارسال فرمایید:")
            return
            
        voice_file_id = voice["file_id"]
        set_splus_user(chat_id, step="RECOVER_WAIT_ADMIN", voice_file_id=voice_file_id)
        
        splus_send_message(chat_id, "درخواست بازیابی حساب شما به همراه ویس دریافت شد ✅")
        time.sleep(0.5)
        splus_send_message(chat_id, "اطلاعات برای مدیریت سرور کافه دوستی ارسال شد. پس از بررسی و تایید توسط مدیریت، مشخصات جدید و قوانین سرور در همین‌جا برای شما ارسال خواهد شد.")
        
        target_uname = user.get("username", "نامشخص")
        target_phone = user.get("phone", "ثبت‌نشده")
        target_pname = user.get("persian_name", "نامشخص")
        sp_user = msg.get("from", {})
        sp_username = f"@{sp_user.get('username')}" if sp_user.get('username') else "بدون آیدی"
        
        admin_caption = (
            "🔄 درخواست بازیابی حساب کاربری از طریق سروش پلاس 📱:\n\n"
            f"🔤 نام کاربری تیم‌تاک: {target_uname}\n"
            f"📱 شماره تلفن: {target_phone if target_phone else 'ثبت‌نشده'}\n"
            f"👤 نام فارسی: {target_pname if target_pname else 'نامشخص'}\n"
            f"🆔 آیدی سروش متقاضی: {sp_username}\n"
            f"🔢 شناسه سروش متقاضی: {chat_id}\n\n"
            "لطفاً ویس ارسالی را گوش دهید و تصمیم‌گیری فرمایید:"
        )
        admin_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "تایید بازیابی در سروش ✅", "callback_data": f"app_rec_sp_{chat_id}"},
                    {"text": "رد درخواست بازیابی سروش ❌", "callback_data": f"rej_rec_sp_{chat_id}"}
                ]
            ]
        }
        
        voice_bytes = splus_download_file_bytes(voice_file_id)
        if voice_bytes:
            send_voice_file(ADMIN_CHAT_ID, f"splus_rec_{chat_id}.ogg", voice_bytes, caption=admin_caption, reply_markup=admin_keyboard)
            splus_send_voice_file(SPLUS_ADMIN_CHAT_ID, f"splus_rec_{chat_id}.ogg", voice_bytes, caption=admin_caption, reply_markup=admin_keyboard)
        else:
            send_message(ADMIN_CHAT_ID, admin_caption + "\n\n(خطا در دانلود ویس کاربر از سروش)", admin_keyboard)
            splus_send_message(SPLUS_ADMIN_CHAT_ID, admin_caption + "\n\n(خطا در دانلود ویس کاربر از سروش)", admin_keyboard)
        return

    # ثبت نام در سروش: دریافت نام فارسی
    if step == "WAIT_NAME":
        if not text:
            splus_send_message(chat_id, "لطفا نام و نام خانوادگی خود را به صورت متنی و فارسی ارسال کنید:")
            return
        persian_name = text
        username = persian_to_english(persian_name)
        
        u_set, p_set = get_tt_existing_cached()
        if username in u_set:
            dup_kb = {
                "inline_keyboard": [
                    [{"text": "بازیابی این حساب کاربری 🔄", "callback_data": "sp_start_recover"}],
                    [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
                ]
            }
            dup_msg = (
                f"⚠️ کاربری با نام کاربری «{username}» از قبل در سرور کافه دوستی ثبت شده و دارای حساب فعال است.\n\n"
                "راهنمای بازیابی حساب:\n"
                "اگر این حساب متعلق به خود شماست و رمز عبور یا اطلاعات ورود را فراموش کرده‌اید، نیازی به ثبت‌نام مجدد ندارید؛ لطفاً دکمه «بازیابی این حساب کاربری» زیر را لمس فرمایید تا از طریق بخش بازیابی، حساب خود را تحویل بگیرید.\n\n"
                "در صورتی که این حساب متعلق به شما نیست و نام شما مشابه است، لطفاً نام خود را به همراه پسوند یا به صورت کامل‌تر بنویسید و ارسال کنید:"
            )
            splus_send_message(chat_id, dup_msg, dup_kb)
            
            existing_acc = find_existing_account(username)
            existing_phone = existing_acc.get("phone", "ثبت‌نشده") if existing_acc else "ثبت‌نشده"
            existing_pname = existing_acc.get("persian_name", "") if existing_acc else ""
            pname_info = f" (صاحب حساب: {existing_pname})" if existing_pname else ""
            
            sp_user = msg.get("from", {})
            sp_username = f"@{sp_user.get('username')}" if sp_user.get('username') else "بدون آیدی"
            
            admin_alert = (
                "🔔 گزارش هوشمند ربات کافه دوستی:\n\n"
                "⚠️ تلاش برای ثبت‌نام با نام موجود در سرور (سروش)!\n"
                f"🔤 نام کاربری موجود در تیم‌تاک: {username}{pname_info}\n"
                f"📱 شماره تلفن صاحب حساب: {existing_phone}\n"
                f"👤 نام فارسی متقاضی جدید: {persian_name}\n"
                f"🆔 آیدی سروش متقاضی: {sp_username}\n"
                f"🔢 شناسه سروش متقاضی: {chat_id}\n\n"
                "وضعیت: از ایجاد یوزر تکراری جلوگیری شد."
            )
            send_message(ADMIN_CHAT_ID, admin_alert)
            splus_send_message(SPLUS_ADMIN_CHAT_ID, admin_alert)
            return

        set_splus_user(chat_id, step="WAIT_PHONE", persian_name=persian_name, username=username)
        confirm_name_msg = (
            f"نام فارسی شما: {persian_name}\n"
            f"نام کاربری انگلیسی پیشنهادی شما: {username} ✅"
        )
        splus_send_message(chat_id, confirm_name_msg)
        time.sleep(0.5)
        splus_send_message(chat_id, "حالا لطفاً شماره موبایل خود را به صورت ۱۱ رقمی (مانند: ۰۹۱۲۳۴۵۶۷۸۹) وارد کنید:")
        return
        
    # ثبت نام در سروش: دریافت شماره موبایل
    if step == "WAIT_PHONE":
        clean_phone = text.replace("+98", "0").replace("0098", "0").replace(" ", "").replace("-", "")
        fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
        clean_phone = clean_phone.translate(fa_to_en)
        if clean_phone.startswith("98"):
            clean_phone = "0" + clean_phone[2:]
        elif clean_phone.startswith("9") and len(clean_phone) == 10:
            clean_phone = "0" + clean_phone
        
        if not (clean_phone.startswith("09") and len(clean_phone) == 11 and clean_phone.isdigit()):
            splus_send_message(chat_id, "شماره موبایل وارد شده صحیح نیست. لطفا یک شماره معتبر ۱۱ رقمی مانند ۰۹۱۲۳۴۵۶۷۸۹ وارد کنید:")
            return
        
        u_set, p_set = get_tt_existing_cached()
        db_user = get_user_by_phone(clean_phone)
        sp_user = get_splus_user_by_phone(clean_phone)
        
        if clean_phone in p_set or (db_user and db_user.get("step") == "COMPLETED") or (sp_user and sp_user.get("step") == "COMPLETED" and sp_user.get("chat_id") != chat_id):
            dup_kb = {
                "inline_keyboard": [
                    [{"text": "بازیابی این حساب کاربری 🔄", "callback_data": "sp_start_recover"}],
                    [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
                ]
            }
            dup_msg = (
                f"⚠️ شماره موبایل «{clean_phone}» قبلاً در سرور کافه دوستی ثبت شده و دارای حساب کاربری فعال است.\n\n"
                "طبق قوانین سرور، هر کاربر تنها مجاز به داشتن یک حساب است و امکان ساخت حساب مجدد یا تکراری وجود ندارد.\n\n"
                "راهنمای بازیابی حساب:\n"
                "اگر این شماره متعلق به خود شماست و قبلاً در سرور حساب داشته‌اید، لطفاً با لمس دکمه «بازیابی این حساب کاربری» زیر اقدام کنید تا با ارسال ویس معرفی، مشخصات جدید حساب پس از بررسی مدیریت برای شما ارسال شود."
            )
            splus_send_message(chat_id, dup_msg, dup_kb)
            
            existing_acc = find_existing_account(clean_phone)
            existing_tt_user = existing_acc.get("username", "یافت نشد") if existing_acc else "یافت نشد"
            existing_name = existing_acc.get("persian_name", "") if existing_acc else ""
            name_info = f" (به نام: {existing_name})" if existing_name else ""
            
            sp_user = msg.get("from", {})
            sp_username = f"@{sp_user.get('username')}" if sp_user.get('username') else "بدون آیدی"
            
            admin_alert = (
                "🔔 گزارش هوشمند ربات کافه دوستی:\n\n"
                "⚠️ تلاش برای ثبت‌نام با شماره تکراری از طریق سروش پلاس!\n"
                f"📱 شماره تلفن واردشده: {clean_phone}\n"
                f"🔤 نام کاربری موجود در تیم‌تاک: {existing_tt_user}{name_info}\n"
                f"👤 نام فارسی متقاضی جدید: {user.get('persian_name', 'نامشخص')}\n"
                f"🆔 آیدی سروش متقاضی: {sp_username}\n"
                f"🔢 شناسه سروش متقاضی: {chat_id}\n\n"
                "وضعیت: این شماره از قبل دارای اکانت در سرور است و درخواست مسدود شد."
            )
            send_message(ADMIN_CHAT_ID, admin_alert)
            splus_send_message(SPLUS_ADMIN_CHAT_ID, admin_alert)
            return
        
        set_splus_user(chat_id, step="WAIT_VOICE", phone=clean_phone)
        splus_send_message(chat_id, f"شماره موبایل شما ({clean_phone}) با موفقیت ثبت شد ✅")
        time.sleep(0.5)
        voice_prompt = (
            "مرحله پایانی (ویس معرفی):\n"
            "لطفاً یک پیام صوتی (ویس) درون سروش ضبط و ارسال کنید و در آن موارد زیر را بگویید:\n"
            "۱. نام و نام خانوادگی\n"
            "۲. محل سکونت (شهر یا استان)\n"
            "۳. سن\n"
            "۴. وضعیت تاهل\n\n"
            "منتظر ارسال ویس شما هستیم..."
        )
        splus_send_message(chat_id, voice_prompt)
        return

    # ثبت نام در سروش: دریافت ویس و ارسال به تلگرام ادمین
    if step == "WAIT_VOICE":
        if not voice:
            splus_send_message(chat_id, "لطفا فقط پیام صوتی (ویس) ارسال بفرمایید:")
            return
        
        voice_file_id = voice["file_id"]
        set_splus_user(chat_id, step="PENDING_ADMIN", voice_file_id=voice_file_id)
        
        splus_send_message(chat_id, "ویس و پرونده معرفی شما با موفقیت دریافت شد ✅")
        time.sleep(0.5)
        splus_send_message(chat_id, "اطلاعات شما برای مدیریت سرور کافه دوستی ارسال گردید. به محض بررسی و تایید توسط مدیریت، نتیجه در همین‌جا به شما اعلام خواهد شد.")
        
        user_info = get_splus_user(chat_id)
        sp_user = msg.get("from", {})
        sp_username = f"@{sp_user.get('username')}" if sp_user.get('username') else "بدون آیدی"
        
        caption = (
            "🔔 درخواست عضویت و حساب جدید از طریق سروش پلاس 📱:\n\n"
            f"👤 نام فارسی: {user_info['persian_name']}\n"
            f"🔤 نام کاربری انگلیسی پیشنهادی: {user_info['username']}\n"
            f"📱 شماره موبایل: {user_info['phone']}\n"
            f"🆔 آیدی سروش: {sp_username}\n"
            f"🔢 شناسه سروش متقاضی: {chat_id}\n\n"
            "لطفا ویس بالا را گوش دهید و تصمیم‌گیری کنید:"
        )
        
        admin_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "تایید و ساخت یوزر در سروش ✅", "callback_data": f"app_sp_{chat_id}"},
                    {"text": "رد درخواست سروش ❌", "callback_data": f"rej_sp_{chat_id}"}
                ]
            ]
        }
        
        voice_bytes = splus_download_file_bytes(voice_file_id)
        if voice_bytes:
            send_voice_file(ADMIN_CHAT_ID, f"splus_new_{chat_id}.ogg", voice_bytes, caption=caption, reply_markup=admin_keyboard)
            splus_send_voice_file(SPLUS_ADMIN_CHAT_ID, f"splus_new_{chat_id}.ogg", voice_bytes, caption=caption, reply_markup=admin_keyboard)
        else:
            send_message(ADMIN_CHAT_ID, caption + "\n\n(خطا در دانلود ویس کاربر از سروش)", admin_keyboard)
            splus_send_message(SPLUS_ADMIN_CHAT_ID, caption + "\n\n(خطا در دانلود ویس کاربر از سروش)", admin_keyboard)
        return

def handle_splus_callback_query(cq):
    cq_id = cq["id"]
    from_user = cq["from"]["id"]
    data = cq.get("data", "")
    
    splus_request("answerCallbackQuery", {"callback_query_id": cq_id})
    
    # تایید درخواست عضویت سروش پلاس توسط مدیر در سروش
    if data.startswith("app_sp_"):
        if from_user != SPLUS_ADMIN_CHAT_ID:
            return
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        if not user_info:
            splus_send_message(SPLUS_ADMIN_CHAT_ID, "اطلاعات کاربر در سروش یافت نشد.")
            return
        
        if user_info.get("step") == "COMPLETED":
            splus_send_message(SPLUS_ADMIN_CHAT_ID, "⚠️ این کاربر سروش قبلاً تایید و حسابش ساخته شده است.")
            return
        
        chars = string.ascii_letters + string.digits
        password_30 = ''.join(secrets.choice(chars) for _ in range(30))
        username = user_info["username"]
        phone = user_info.get("phone", "")
        persian_name = user_info.get("persian_name", username)
        
        ok, res = create_teamtalk_account(username, password_30, phone)
        if not ok:
            splus_send_message(SPLUS_ADMIN_CHAT_ID, f"❌ خطا در ساخت اکانت سرور تیم‌تاک برای کاربر سروش:\n{res}")
            return
            
        set_splus_user(target_chat_id, step="COMPLETED", password=password_30)
        
        splus_send_message(SPLUS_ADMIN_CHAT_ID, f"✅ حساب کاربری «{username}» (نام: {persian_name}) با موفقیت در تیم‌تاک ساخته شد و مشخصات در سروش برای متقاضی ارسال گردید.")
        send_message(ADMIN_CHAT_ID, f"🔔 گزارش مدیریت:\nدرخواست عضویت سروش برای «{username}» توسط شما از طریق سروش تایید و تحویل شد ✅")
        
        # ارسال مشخصات، فایل tt و قوانین به کاربر در سروش
        splus_send_message(target_chat_id, "🎉 تبریک! حساب کاربری شما در سرور تیم‌تاک کافه دوستی توسط مدیریت تایید و ساخته شد.")
        splus_send_message(target_chat_id, f"مشخصات اتصال به سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
        splus_send_message(target_chat_id, f"نام کاربری شما:\n{username}")
        splus_send_message(target_chat_id, f"رمز عبور اختصاصی شما:\n{password_30}")
        
        tt_bytes = generate_tt_file_bytes(username, password_30, persian_name)
        filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
        splus_send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        splus_send_message(target_chat_id, rules_header + RULES_TEXT)
        return

    # رد درخواست عضویت سروش پلاس توسط مدیر در سروش
    if data.startswith("rej_sp_"):
        if from_user != SPLUS_ADMIN_CHAT_ID:
            return
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        persian_name = user_info['persian_name'] if user_info else 'کاربر'
        set_splus_user(target_chat_id, step="REJECTED")
        
        splus_send_message(SPLUS_ADMIN_CHAT_ID, f"❌ درخواست عضویت متقاضی سروش ({persian_name}) رد شد.")
        send_message(ADMIN_CHAT_ID, f"🔔 گزارش مدیریت:\nدرخواست عضویت سروش برای «{persian_name}» توسط شما از طریق سروش رد شد ❌")
        
        rejection_msg = (
            "درود و احترام؛\n\n"
            "ضمن قدردانی از ابراز لطف و همراهی شما با مجموعه کافه دوستی، به اطلاع می‌رسانیم که پس از بررسی تیم مدیریت، متاسفانه در حال حاضر امکان تایید درخواست عضویت شما وجود ندارد.\n\n"
            "با آرزوی بهروزی، شادکامی و موفقیت روزافزون برای شما. 🌸"
        )
        splus_send_message(target_chat_id, rejection_msg)
        return

    # تایید بازیابی سروش پلاس توسط مدیر در سروش
    if data.startswith("app_rec_sp_"):
        if from_user != SPLUS_ADMIN_CHAT_ID:
            return
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        if not user_info:
            splus_send_message(SPLUS_ADMIN_CHAT_ID, "اطلاعات کاربر سروش یافت نشد.")
            return
            
        username = user_info["username"]
        phone = user_info.get("phone", "")
        persian_name = user_info.get("persian_name", "")
        
        chars = string.ascii_letters + string.digits
        password_30 = ''.join(secrets.choice(chars) for _ in range(30))
        
        ok = reset_teamtalk_account(username, password_30, phone)
        if not ok:
            splus_send_message(SPLUS_ADMIN_CHAT_ID, f"❌ خطا در بازیابی اکانت سروش {username} در سرور تیم‌تاک.")
            return
            
        set_splus_user(target_chat_id, step="COMPLETED", password=password_30)
        
        splus_send_message(SPLUS_ADMIN_CHAT_ID, f"✅ بازیابی حساب «{username}» انجام و مشخصات جدید در سروش برای متقاضی ارسال شد.")
        send_message(ADMIN_CHAT_ID, f"🔔 گزارش مدیریت:\nدرخواست بازیابی سروش برای «{username}» توسط شما از طریق سروش تایید شد ✅")
        
        splus_send_message(target_chat_id, "🎉 تبریک! درخواست بازیابی حساب کاربری شما توسط مدیریت تایید شد.\n\nمشخصات اتصال جدید شما به سرور کافه دوستی:")
        splus_send_message(target_chat_id, f"مشخصات سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
        splus_send_message(target_chat_id, f"نام کاربری شما:\n{username}")
        splus_send_message(target_chat_id, f"رمز عبور جدید شما:\n{password_30}")
        
        tt_bytes = generate_tt_file_bytes(username, password_30, persian_name if persian_name else username)
        filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
        splus_send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی. کافی است روی فایل کلیک کنید تا متصل شوید.")
        
        rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
        splus_send_message(target_chat_id, rules_header + RULES_TEXT)
        return

    # رد درخواست بازیابی سروش پلاس توسط مدیر در سروش
    if data.startswith("rej_rec_sp_"):
        if from_user != SPLUS_ADMIN_CHAT_ID:
            return
        target_chat_id = int(data.split("_")[-1])
        set_splus_user(target_chat_id, step="REJECTED")
        
        splus_send_message(SPLUS_ADMIN_CHAT_ID, "❌ درخواست بازیابی متقاضی سروش رد شد.")
        send_message(ADMIN_CHAT_ID, "🔔 گزارش مدیریت:\nدرخواست بازیابی متقاضی سروش توسط شما از طریق سروش رد شد ❌")
        
        rejection_msg = (
            "درود و احترام؛\n\n"
            "درخواست بازیابی حساب کاربری شما پس از بررسی توسط مدیریت سرور کافه دوستی، مورد تایید قرار نگرفت.\n\n"
            "با آرزوی بهترین‌ها برای شما. 🌸"
        )
        splus_send_message(target_chat_id, rejection_msg)
        return

    if data == "sp_dl_menu":
        dl_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود نسخه ویندوز (Windows) 💻", "callback_data": "sp_dl_win"}],
                [{"text": "دانلود نسخه اندروید (Android) 📱", "callback_data": "sp_dl_android"}],
                [{"text": "بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
            ]
        }
        dl_text = (
            "📥 دریافت آخرین نسخه رسمی نرم‌افزار تیم‌تاک:\n\n"
            "لطفاً سیستم‌عامل دستگاه خود را انتخاب کنید تا لینک مستقیم از سایت رسمی تیم‌تاک (BearWare) برای شما ارسال شود:"
        )
        splus_send_message(from_user, dl_text, dl_keyboard)
        return

    if data == "sp_dl_win":
        win_link = get_latest_teamtalk_win_link()
        win_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود مستقیم نسخه ویندوز 📥", "url": win_link}],
                [{"text": "بازگشت به منوی دانلود 🔙", "callback_data": "sp_dl_menu"}]
            ]
        }
        msg_str = (
            "💻 دانلود آخرین نسخه رسمی تیم‌تاک برای ویندوز (Windows):\n\n"
            "لینک دانلود مستقیم و رسمی از سرور اصلی تیم‌تاک (BearWare):\n"
            f"{win_link}\n\n"
            "پس از دانلود، فایل نصبی را اجرا کرده و مراحل نصب را انجام دهید."
        )
        splus_send_message(from_user, msg_str, win_keyboard)
        return

    if data == "sp_dl_android":
        android_play_link = "https://play.google.com/store/apps/details?id=dk.bearware.gui"
        android_apk_link = "https://d.apkpure.com/b/APK/dk.bearware.gui?version=latest"
        android_keyboard = {
            "inline_keyboard": [
                [{"text": "دانلود از گوگل‌پلی (سایت رسمی تیم‌تاک) 🌐", "url": android_play_link}],
                [{"text": "دانلود مستقیم فایل نصبی (APK) 📥", "url": android_apk_link}],
                [{"text": "بازگشت به منوی دانلود 🔙", "callback_data": "sp_dl_menu"}]
            ]
        }
        msg_str = (
            "📱 دانلود آخرین نسخه رسمی تیم‌تاک برای اندروید (Android):\n\n"
            "۱. لینک رسمی تیم‌تاک در فروشگاه گوگل‌پلی (سایت اصلی تیم‌تاک):\n"
            f"{android_play_link}\n\n"
            "۲. لینک دانلود مستقیم فایل نصبی (APK) در صورت عدم دسترسی به گوگل‌پلی:\n"
            f"{android_apk_link}\n\n"
            "با لمس هر یک از دکمه‌های زیر، برنامه به طور مستقیم دانلود خواهد شد."
        )
        splus_send_message(from_user, msg_str, android_keyboard)
        return

    if data == "sp_back_to_main":
        send_splus_main_menu(from_user)
        return

    if data == "sp_start_recover":
        set_splus_user(from_user, step="RECOVER_WAIT_INPUT")
        recovery_text = (
            "🔄 بازیابی حساب کاربری در کافه دوستی:\n\n"
            "مرحله اول:\n"
            "لطفاً نام کاربری (یوزرنیم) یا شماره موبایلی که قبلاً با آن در سرور حساب داشته‌اید را ارسال کنید:"
        )
        cancel_keyboard = {
            "inline_keyboard": [
                [{"text": "انصراف و بازگشت به منوی اصلی 🔙", "callback_data": "sp_back_to_main"}]
            ]
        }
        splus_send_message(from_user, recovery_text, cancel_keyboard)
        return

    if data == "sp_start_register":
        user_info = get_splus_user(from_user)
        if user_info and user_info.get("step") == "COMPLETED" and user_info.get("username"):
            sp_resend_kb = {
                "inline_keyboard": [
                    [{"text": "دریافت مجدد مشخصات حساب 📝", "callback_data": f"sp_resend_{from_user}"}],
                    [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "sp_start_recover"}],
                    [{"text": "دانلود نرم‌افزار تیم‌تاک 📥", "callback_data": "sp_dl_menu"}]
                ]
            }
            splus_send_message(
                from_user,
                "⚠️ شما قبلاً حساب کاربری خود را در سرور کافه دوستی دریافت کرده‌اید و هر کاربر تنها مجاز به داشتن یک حساب است.\n\n"
                f"نام کاربری شما: {user_info['username']}\n\n"
                "اگر اطلاعات ورود یا رمز خود را فراموش کرده‌اید، می‌توانید از طریق دکمه‌های زیر مشخصات خود را مجدداً دریافت کرده یا درخواست بازیابی ثبت نمایید:",
                sp_resend_kb
            )
            return

        join_keyboard = {
            "inline_keyboard": [
                [{"text": "عضویت در کانال سروش کافه دوستی 📢", "url": SPLUS_CHANNEL_LINK}],
                [{"text": "عضو شدم / ادامه ثبت‌نام 🔄", "callback_data": "sp_check_join"}]
            ]
        }
        splus_send_message(
            from_user,
            "⚠️ طبق قوانین کافه دوستی، برای ثبت‌نام و دریافت حساب کاربری، ابتدا باید عضو کانال سروش کافه دوستی شوید.\n\n"
            f"لینک کانال رسمی:\n{SPLUS_CHANNEL_LINK}\n\n"
            "لطفاً ابتدا وارد کانال شده و دکمه پیوستن (عضویت) را لمس کنید، سپس دکمه «عضو شدم / ادامه ثبت‌نام» را بزنید:",
            join_keyboard
        )
        return

    if data == "sp_check_join":
        user_info = get_splus_user(from_user)
        if user_info and user_info.get("step") == "COMPLETED" and user_info.get("username"):
            sp_resend_kb = {
                "inline_keyboard": [
                    [{"text": "دریافت مجدد مشخصات حساب 📝", "callback_data": f"sp_resend_{from_user}"}],
                    [{"text": "بازیابی حساب کاربری 🔄", "callback_data": "sp_start_recover"}],
                    [{"text": "دانلود نرم‌افزار تیم‌تاک 📥", "callback_data": "sp_dl_menu"}]
                ]
            }
            splus_send_message(
                from_user,
                "⚠️ شما قبلاً حساب کاربری خود را در سرور کافه دوستی دریافت کرده‌اید و هر کاربر تنها مجاز به داشتن یک حساب است.\n\n"
                f"نام کاربری شما: {user_info['username']}\n\n"
                "اگر اطلاعات ورود یا رمز خود را فراموش کرده‌اید، می‌توانید از طریق دکمه‌های زیر مشخصات خود را مجدداً دریافت کرده یا درخواست بازیابی ثبت نمایید:",
                sp_resend_kb
            )
            return
        
        set_splus_user(from_user, step="WAIT_NAME")
        splus_send_message(from_user, "عضویت شما در کانال کافه دوستی تایید شد ✅")
        time.sleep(0.5)
        splus_send_message(from_user, "لطفاً نام و نام خانوادگی خود را به زبان فارسی (مانند: امید علیایی) بنویسید و ارسال کنید:")
        return

    # ارسال مجدد مشخصات به کاربر سروش
    if data.startswith("sp_resend_"):
        target_chat_id = int(data.split("_")[-1])
        user_info = get_splus_user(target_chat_id)
        if user_info and user_info.get("password"):
            username = user_info["username"]
            password = user_info["password"]
            persian_name = user_info["persian_name"]
            
            splus_send_message(target_chat_id, f"مشخصات اتصال به سرور کافه دوستی ☕️\n\nآدرس سرور:\n{TT_HOST}\nپورت:\n{TT_PORT}")
            splus_send_message(target_chat_id, f"نام کاربری شما:\n{username}")
            splus_send_message(target_chat_id, f"رمز عبور شما:\n{password}")
            
            tt_bytes = generate_tt_file_bytes(username, password, persian_name)
            filename = f"KaafehDoosti_{username.replace(' ', '_')}.tt"
            splus_send_document_file(target_chat_id, filename, tt_bytes, caption="فایل اتصال آماده تیم‌تاک کافه دوستی.")
            
            rules_header = "📜 قوانین حضور در سرور کافه دوستی:\n(لطفا با دقت مطالعه کنید؛ رعایت این موارد شرط حضور در سرور است)\n\n"
            splus_send_message(target_chat_id, rules_header + RULES_TEXT)
            return

# ----------------- سرور سلامت برای رندر (Health Check) -----------------
import http.server
import socketserver

def ensure_linux_tt_sdk():
    if sys.platform == "win32":
        return True, "Windows"
    so_path = "libTeamTalk5.so"
    if os.path.exists(so_path) and os.path.getsize(so_path) > 1000000:
        return True, "Already extracted"
    url = "https://bearware.dk/teamtalk/v5.13/teamtalk-v5.13-ubuntu22-x86_64.tgz"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
        import tarfile, io
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            for m in tar.getmembers():
                if m.name.endswith("libTeamTalk5.so"):
                    f = tar.extractfile(m)
                    with open(so_path, "wb") as out:
                        out.write(f.read())
                    return True, f"Extracted libTeamTalk5.so: {os.path.getsize(so_path)} bytes"
        return False, "libTeamTalk5.so not found in tar"
    except Exception as e:
        return False, f"Download failed: {e}"


# ----------------- بارگذاری SDK تیم‌تاک و راه‌اندازی رادیو کافه دوستی -----------------
ensure_linux_tt_sdk()
if sys.platform == "win32":
    sys.path.insert(0, r"C:\Users\Lenovo\.gemini\antigravity\scratch\TeamTalkPy")
else:
    sys.path.insert(0, os.getcwd())

try:
    import TeamTalk5
except Exception as e:
    print(f"[Radio] Error importing TeamTalk5: {e}", flush=True)

RADIO_TT_HOST = "185.26.33.57"
RADIO_TT_PORT = 10333
RADIO_TT_USER = "radio kaafehdoosti"
RADIO_TT_PASS = "radio_kaafeh_123456789_doosti"
RADIO_TT_NICK = "radio kaafehdoosti"
RADIO_CHAN_ID = 2
RADIO_ADMINS = {"omid.o", "yalda", "admin", "kaafehdoostibot", "omid"}

RADIO_TG_TOKEN = "8600063713:AAGxU2xoECq5u1FjdOIgAA1PPdHBSXnZIt8"
RADIO_TG_CHANNEL = "@raaduokaafehdoosti"
RADIO_CACHE_DIR = os.path.join(os.getcwd(), "music_cache")
BASE_TRACK_CATALOG = [{'msg_id': 2, 'title': '99883435', 'performer': '<unknown>', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADAmrh6ZpUMSFpSAqKpUCPZfDsNDC2AAJlIQACYHYJUx7jpPRoHV2FPQQ'}, {'msg_id': 3, 'title': 'Aroos Shomali', 'performer': 'Ebi Aali @Raz-Music.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADA2rh6oU8_xDsnBp2MVd7-PXsBQ84AAJmIQACYHYJU4QYFZMdM9k7PQQ'}, {'msg_id': 4, 'title': 'Gheyrati', 'performer': 'Savash', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADBGrh6oZ0RzXv220sH80s3uIR70wOAAJnIQACYHYJU8Bgpm6mPc7sPQQ'}, {'msg_id': 5, 'title': 'Roya', 'performer': 'Savash', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADBWrh6pQOffKhu7fsLc6FuytI-_7tAAJoIQACYHYJU5xAqA1LwD2JPQQ'}, {'msg_id': 6, 'title': 'Joonami ~ TajMusics.com ', 'performer': 'Novan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADBmrh6pWyWor4uQu9sai_9mJgO0NsAAJtIQACYHYJU_JMmp8h2jc5PQQ'}, {'msg_id': 7, 'title': 'Refigh موزیکدل', 'performer': 'Milad Rastaad موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADB2rh6pdxFdGSSfxpFlK0BbquNV_ZAAJyIQACYHYJU0u8-R7M0F0dPQQ'}, {'msg_id': 8, 'title': 'Delam Tangete', 'performer': 'Sina Derakhshande', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADCGrh6p8S9UXA7vdjzEd2s-Ld7a3wAAK_GgAC-20BU2ABr3mb7ogPPQQ'}, {'msg_id': 9, 'title': 'Nagam Barat', 'performer': 'Babak Jahanbakhsh', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADCWrh6qgenVBzjOqwHfGbPQhYGm6JAAL1CQACLJa4UljOAbStJxUHPQQ'}, {'msg_id': 10, 'title': 'Kharabemoon Kard', 'performer': 'Mojtaba Dorbidi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADCmrh6q4jJ016HwbRCeRtXCXgnUt9AAJKCgACTCtQUeEoaJDL-ylUPQQ'}, {'msg_id': 11, 'title': 'Bahooneh', 'performer': 'Mehdi Moghaddam', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADC2rh6q_nrQTcBjq0HzhcN3fEkYPSAAK7BwACrINZUWdCLD9YexswPQQ'}, {'msg_id': 12, 'title': 'Man Chi', 'performer': 'Misagh Raad', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADDGrh6rOqt-3hVaklcFNqaxaunn_HAAKbBwAClYxIUYwgAAExzL-VqD0E'}, {'msg_id': 13, 'title': 'Dametam Garm (Live Version)', 'performer': 'Puzzle Band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADDWrh6sFE3IrUne-Fp7b3fSYaLYJ4AAJkBwACMQNYUSXgoQu0Zg4lPQQ'}, {'msg_id': 14, 'title': 'Ashti', 'performer': 'Mohammad Lotfi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADDmrh6sLb3b_9sBwDH1HkHmW1lr_eAAI4CQACPH5QUZWjM7NbQ6pePQQ'}, {'msg_id': 15, 'title': 'Chatr', 'performer': 'Saman Jalili', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADD2rh6sMWmoRwDepddJjtavtCWtf1AAI1BwACTIfYUA2xbk9EBAj2PQQ'}, {'msg_id': 16, 'title': 'Shab Bekheir', 'performer': 'Kamran Molaei', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADEGrhadOcqby-sJMgeQxNUQHfglQbAAK7IAACb7f5UsuBkYIT8uLOPQQ'}, {'msg_id': 17, 'title': 'To Doost Dashti', 'performer': 'Ali Abdolmaleki', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADEWrhaizkMsU5fdqfDB1491LrLu9pAAIUHwACDbkJU82VTcvkPVJfPQQ'}, {'msg_id': 18, 'title': 'Mishe Bargardi Khoone', 'performer': 'Ashvan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADEmrhap5sUfe89M1TTmouluBp8nQ9AAL8HwACk6zwUm-wnppxuGIiPQQ'}, {'msg_id': 19, 'title': 'Ma 2 Ta', 'performer': '2Yar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADE2rha4nUQ0pVlBg-18hWLRSYGhG-AAIKHAAC4IvQUl_sQ13UvAcaPQQ'}, {'msg_id': 20, 'title': '[Be Shab Nareside Chera Deltange Cheshat Shudam] ~[SevilMusic.Com]~', 'performer': '[Shayan Yo]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFGrheHq_xW2p4PH23kYN9pa0BGOlAAJJHgACWQEIU6lp5lkqcFnTPQQ'}, {'msg_id': 21, 'title': 'Yadet Nemiyad  | UpTune.ir', 'performer': 'Persian Remix  | آپ تیون', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFWrheHqfCAs4JOSMbT5I7P3ubkTGAAJKHgACWQEIU2z3T66agi8IPQQ'}, {'msg_id': 22, 'title': '2026_@Remix_song_rap-_I69OrwUBcg.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFmrheHrbUEY2zDgda_WRLjNvwzXUAAJLHgACWQEIU9fffYNPEOz7PQQ'}, {'msg_id': 29, 'title': 'Dashi', 'performer': 'Shahin Najafi & Erfan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADHWrhkZtGXkFarSb_-K7lfWI2AqjpAAITIAACj0kJU_NcIkBwG4s2PQQ'}, {'msg_id': 30, 'title': 'Jigar Tala ~ Musics-Fa.Com', 'performer': '2Yar ~ Musics-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADHmrhk6Z3LXP_NhABOufq07JE53qlAAIVIAACj0kJU553Tj5nsne5PQQ'}, {'msg_id': 31, 'title': 'Injoori Nemishe', 'performer': 'Ali Montazeri', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADH2rhlXUqzBHdrEsRqsrLo1dUmAitAAIYIAACj0kJU4wiwRshhb9VPQQ'}, {'msg_id': 32, 'title': 'Koodeta', 'performer': 'Bijan Yaar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADIGrhlZjP-9rU44VsD7nrZAtQ7BEcAAIZIAACj0kJUyxP4lr9-zDYPQQ'}, {'msg_id': 33, 'title': 'Haydeh & chavoshi', 'performer': '@MusiceMeee', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADIWrhlokK3PSExPrpNAnXPqWAg8tiAAIbIAACj0kJU-J4tFFv11qKPQQ'}, {'msg_id': 34, 'title': 'Siroos Pishghadam Delbar Delbar', 'performer': 'اینستاگرام: soonami_mp3', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADImrhl-t_A5LwqW0VSATd_5QxFxbwAAIcIAACj0kJUxTq8TR2Y1qMPQQ'}, {'msg_id': 35, 'title': 'Majnoonetam ~ UpMusic', 'performer': 'Soheil Mehrzadegan ~ UpMusic', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADI2rhl-tXS55J9NFakkAqNOgEjs3RAAIdIAACj0kJU8eEoWz0SeHOPQQ'}, {'msg_id': 36, 'title': 'Edame Nemidam', 'performer': 'Yousef Zamani', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJGrhmDYbDQVMHv2DzTdDFj3OwWq4AAIeIAACj0kJUxUpSMcYrooUPQQ'}, {'msg_id': 37, 'title': 'Amin-Habibi-Bi-Gharar-(New-Version)(Happy-Song.Ir)', 'performer': 'Amin-Habibi-Bi-Gharar-(New-Version)(Happy-Song.Ir)', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJWrhmDY_9nTxbjMTvJPacFjBir9pAAIfIAACj0kJU2Anplo2-k7UPQQ'}, {'msg_id': 38, 'title': 'Shaparak', 'performer': 'Ikan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJmrhmGBozTOEuJvLrV7-yFJ8AAFL5wACICAAAo9JCVM-LCoTCeGzoj0E'}, {'msg_id': 39, 'title': 'Kojaei Alan', 'performer': 'Hossein Montazeri', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJ2rhmGAvMFaSP1yOmH0bjyBbmKxAAAIiIAACj0kJUxZhMVEo5GQaPQQ'}, {'msg_id': 40, 'title': 'Kabootar', 'performer': 'Sina Parsian @RozMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADKGrhmVvIWtIpiZju7Jx1JWcXeVzJAAIkIAACj0kJU2EgZF9HYk-uPQQ'}, {'msg_id': 41, 'title': 'Azizi ( ahaang.com )', 'performer': 'Alireza Talischi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADKWrhmVuMV82N8bx4qD5hV2496od_AAIlIAACj0kJU3UdFAKT7sPFPQQ'}, {'msg_id': 42, 'title': 'Labato Zhel Bezanam topsongs.ir', 'performer': 'topsongs.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADKmrhms2sm-fMdoip9dqxn5iDRqs9AAImIAACj0kJU1pUu33Vzk6yPQQ'}, {'msg_id': 43, 'title': 'Phobia', 'performer': 'Armin Zarei @RozMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADK2rhms1nDhNKhp14ajIOm-9KzUZXAAIoIAACj0kJU2Dtq5zt2l5RPQQ'}, {'msg_id': 44, 'title': 'Zang Bezani', 'performer': 'Mohsen Ebrahimzadeh', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADLGrhms0nSBioXTV5BtbS25KX4mHOAAIpIAACj0kJU6DdDsMVp1GmPQQ'}, {'msg_id': 45, 'title': 'Ye Ja To Delet (320).mp3', 'performer': '', 'file_id': 'BQACAgQAAyEFAAMBBZ8iywADLWrhm3e8Vfu18m5ZHT6WI4dwIXH7AAIsIAACj0kJU5pZ7ScIufpcPQQ'}, {'msg_id': 46, 'title': '4 Divari ~ Music-Fa.Com', 'performer': 'Mohammad Moharami ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADLmrhm-v7kSDz2j-DazET-kxYAAG93AACLiAAAo9JCVNzWjFD7AnuQT0E'}, {'msg_id': 47, 'title': 'Dino Donya موزیکدل', 'performer': 'Ahoora موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADL2rhm-sYg6LoMWQDEAWS75XsigdCAAIvIAACj0kJU1GwgJZqH453PQQ'}, {'msg_id': 48, 'title': 'Bedon Man Koja Mikhay Beri ~ TajMusics.Com ', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADMGrhm-sjZWZONz3q4nCn_5NIKyigAAIwIAACj0kJU5byF1NshYs9PQQ'}, {'msg_id': 49, 'title': 'Shab Ahangi ~ Music-Fa.Com', 'performer': 'Masoud Sadeghloo ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADMWrhm-vQl56nsR-KDWLJOEgamugnAAIxIAACj0kJU9bor4EaY0-QPQQ'}, {'msg_id': 50, 'title': 'Mehdi Ahmadvand - Cheshmat (320).mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADMmrhnThakBvpdRLk9E_2buQNORRWAAI0IAACj0kJU-OTSfEzkXM5PQQ'}, {'msg_id': 51, 'title': 'Sare To [SultanMusic.IR]', 'performer': 'Shayan Yo', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADM2rhnTha99MjLaaLq6kM436J_403AAI1IAACj0kJU0wbxy6qN2UKPQQ'}, {'msg_id': 52, 'title': 'Naser Pourkaram - Khabar Nadari.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADNGrhnTieXHCpXdZ-CUhDlBkvCqkZAAI2IAACj0kJU6FWC3ANWxG1PQQ'}, {'msg_id': 53, 'title': '[Bala Mala Ey Tala Tala] ~[SevilMusic.Com]~', 'performer': '[Unknown Artist]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADNWrhng9FOD-GCk8V1iUAAe3QPNaBYAACOCAAAo9JCVOsJYk18AnYfz0E'}, {'msg_id': 54, 'title': 'Vay Az Dastet', 'performer': 'Meysam Ebrahimi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADNmrhuqRp_GXgZNL6RLk2IDBXXyG5AALCIQACQaDQUkIewAEQCMo4PQQ'}]

os.makedirs(RADIO_CACHE_DIR, exist_ok=True)

global_radio_bot = None

def get_radio_status():
    global global_radio_bot
    if not global_radio_bot:
        return "ربات رادیو کافه دوستی در حال راه‌اندازی است..."
    b = global_radio_bot
    flags = 0
    try:
        flags = b.getFlags()
    except Exception:
        pass
    lines = [
        f"لاگ رویدادها: {' | '.join(b.diag[-8:]) if getattr(b, 'diag', None) else 'هیچ'}",
        f"فلگ کلاینت: {hex(flags)}",
        f"وضعیت اتصال: {'متصل به سرور' if b.connected else 'قطع از سرور'}",
        f"ورود به حساب رادیو: {'موفق' if b.logged_in else 'ناموفق'}",
        f"حضور در اتاق ۲ (رادیو کافه دوستی): {'بله' if b.joined else 'خیر'}",
        f"وضعیت پخش موزیک: {'در حال پخش' if b.is_streaming else 'متوقف'}",
        f"وضعیت تایتل: {'مخفی' if getattr(b, 'title_hidden', False) else 'نمایان'}",
        f"میزان صدا: {b.volume_percent} درصد",
        f"تعداد آهنگ‌های موجود: {len(b.playlist)} قطعه",
    ]
    if b.current_track:
        next_idx = b.get_next_track_index(b.current_index) if b.playlist else 0
        next_track = b.playlist[next_idx] if b.playlist else {}
        lines.append(f"قطعه فعلی ({b.current_index + 1}/{len(b.playlist)}): {b.current_track.get('title')}")
        lines.append(f"قطعه بعدی: {next_track.get('title', 'ندارد')}")
    else:
        lines.append("قطعه فعلی: آهنگی در حال پخش نیست")
    return "\n".join(lines)

RADIO_STATE_FILE = os.path.join(os.getcwd(), "radio_state.json")
SAVED_RADIO_VOLUME = 25

def save_persistent_config(key, value):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS radio_settings (key TEXT PRIMARY KEY, val TEXT)")
        c.execute("INSERT OR REPLACE INTO radio_settings (key, val) VALUES (?, ?)", (str(key), str(value)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Radio] save_persistent_config err: {e}", flush=True)

def load_persistent_config(key, default=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS radio_settings (key TEXT PRIMARY KEY, val TEXT)")
        c.execute("SELECT val FROM radio_settings WHERE key=?", (str(key),))
        row = c.fetchone()
        conn.close()
        if row and row[0] is not None:
            return row[0]
    except Exception as e:
        print(f"[Radio] load_persistent_config err: {e}", flush=True)
    return default

def load_saved_radio_state():
    global SAVED_RADIO_VOLUME
    db_vol = load_persistent_config("volume_percent", None)
    if db_vol is not None:
        try:
            SAVED_RADIO_VOLUME = int(db_vol)
        except Exception:
            pass

    defaults = {
        "volume_percent": SAVED_RADIO_VOLUME,
        "title_hidden": False,
        "last_track_name": "Milad Rastaad موزیکدل - Refigh موزیکدل",
        "current_index": 5,
        "playback_pos_sec": 0.0
    }
    if os.path.exists(RADIO_STATE_FILE):
        try:
            with open(RADIO_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
                if "volume_percent" in data:
                    SAVED_RADIO_VOLUME = data["volume_percent"]
                print(f"[Radio] Loaded state: {defaults}", flush=True)
        except Exception as e:
            print(f"[Radio] Load state err: {e}", flush=True)
    return defaults

def save_radio_state(state):
    def _do_write():
        try:
            tmp_path = RADIO_STATE_FILE + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush()
            if os.path.exists(tmp_path):
                os.replace(tmp_path, RADIO_STATE_FILE)
        except Exception as e:
            print(f"[Radio] Save state err: {e}", flush=True)
    threading.Thread(target=_do_write, daemon=True).start()

class VoicePlayer:
    def __init__(self, bot):
        self.bot = bot
        self.stop_event = threading.Event()
        self.thread = None
        self.sample_rate = 48000
        self.channels = 2
        self.current_pos = 0

    def play(self, track_path, start_sec=0.0):
        self.stop()
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._play_worker, args=(track_path, start_sec), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive() and self.thread != threading.current_thread():
            self.thread.join(timeout=0.8)
        try:
            self.bot.insertAudioBlock(None)
        except Exception:
            pass

    def _play_worker(self, track_path, start_sec=0.0):
        try:
            # 1. Inspect channel codec to match channels and sample rate
            chan_ch = 2
            chan_sr = 48000
            try:
                chan = self.bot.getChannel(RADIO_CHAN_ID)
                if getattr(chan.audiocodec, "nCodec", None) == TeamTalk5.Codec.OPUS_CODEC:
                    c_ch = getattr(chan.audiocodec.opus, "nChannels", 2)
                    c_sr = getattr(chan.audiocodec.opus, "nSampleRate", 48000)
                    if c_ch in (1, 2):
                        chan_ch = c_ch
                    if c_sr in (8000, 16000, 24000, 48000):
                        chan_sr = c_sr
            except Exception as e:
                print(f"[Radio] Channel codec inspect err: {e}", flush=True)

            self.channels = chan_ch
            self.sample_rate = chan_sr

            # 2. Decode track to PCM matching channel parameters
            raw_pcm = None
            try:
                import miniaudio
                decoded = miniaudio.decode_file(
                    track_path,
                    output_format=miniaudio.SampleFormat.SIGNED16,
                    nchannels=self.channels,
                    sample_rate=self.sample_rate
                )
                raw_pcm = decoded.samples.tobytes()
            except Exception as e:
                print(f"[Radio] miniaudio decode err: {e}", flush=True)

            if not raw_pcm:
                try:
                    import subprocess
                    cmd = ["ffmpeg", "-v", "quiet", "-i", track_path, "-f", "s16le", "-ar", str(self.sample_rate), "-ac", str(self.channels), "-"]
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    raw_pcm = proc.stdout.read()
                except Exception as e:
                    print(f"[Radio] ffmpeg decode err: {e}", flush=True)

            min_chunk = int(self.sample_rate * 0.02) * self.channels * 2
            if not raw_pcm or len(raw_pcm) < min_chunk:
                print("[Radio] Direct Voice: Could not decode to PCM. Fallback to media file stream...", flush=True)
                self.bot.stream_media_file_fallback(track_path)
                return

            print(f"[Radio] Direct Voice transmission started: {os.path.basename(track_path)} ({len(raw_pcm)} bytes PCM, {self.channels}ch, {self.sample_rate}Hz)", flush=True)
            self.bot.diag.append("VOICE_TX_START")

            # 3. CRITICAL: Make sure voice transmission from microphone device is OFF
            # Per TeamTalk C-API: If CLIENT_TX_VOICE is active, TT_InsertAudioBlock() will fail.
            try:
                self.bot.enableVoiceTransmission(False)
            except Exception as e:
                print(f"[Radio] enableVoiceTransmission(False) err: {e}", flush=True)

            self.bot.is_streaming = True
            self.bot.update_player_title()

            samples_per_frame = int(self.sample_rate * 0.02)  # 960 for 20ms at 48kHz
            chunk_size = samples_per_frame * self.channels * 2
            total_len = len(raw_pcm)
            
            # Resume from start_sec if provided
            start_pos = int(start_sec * self.sample_rate) * self.channels * 2
            start_pos = (start_pos // chunk_size) * chunk_size
            if 0 < start_pos < total_len - (chunk_size * 50):
                pos = start_pos
                sample_index = int(start_sec * self.sample_rate)
                print(f"[Radio] Resuming playback of {os.path.basename(track_path)} from {start_sec:.1f}s (byte {pos}/{total_len})", flush=True)
            else:
                pos = 0
                sample_index = 0
            
            self.current_pos = pos

            buf_type = ctypes.c_byte * chunk_size
            ab = TeamTalk5.AudioBlock()
            ab.nStreamID = 1
            ab.nSampleRate = self.sample_rate
            ab.nChannels = self.channels
            ab.nSamples = samples_per_frame
            ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE

            # Disable DSP preprocessing (denoiser and AGC) so music fidelity is 100% natural
            try:
                dsp = TeamTalk5.SpeexDSP()
                dsp.bEnableAGC = False
                dsp.bEnableDenoise = False
                dsp.bEnableEchoCancellation = False
                dsp.nGainLevel = int(max(0, min(150, getattr(self.bot, "volume_percent", 100))) / 100.0 * 1000)
                TeamTalk5._SetSoundInputPreprocess(self.bot._tt, ctypes.byref(dsp))
            except Exception:
                pass

            # Pre-buffer 5 frames (100ms) to ensure jitter buffer is never starved
            for _ in range(5):
                if pos < total_len and not self.stop_event.is_set():
                    chunk = raw_pcm[pos:pos + chunk_size]
                    pos += chunk_size
                    self.current_pos = pos
                    if len(chunk) < chunk_size:
                        chunk += bytes(chunk_size - len(chunk))
                    
                    cur_vol = getattr(self.bot, "volume_percent", 100)
                    if cur_vol != 100:
                        try:
                            import audioop
                            chunk = audioop.mul(chunk, 2, max(0.0, min(1.5, cur_vol / 100.0)))
                        except Exception:
                            pass

                    raw_buf = buf_type.from_buffer_copy(chunk)
                    ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
                    ab.uSampleIndex = sample_index
                    sample_index += samples_per_frame
                    self.bot.insertAudioBlock(ab)

            first_logged = False
            failed_inserts = 0
            chunks_since_save = 0
            
            # Accurate drift-compensated clock for crystal-clear, uninterrupted voice transmission
            clock_start = time.perf_counter()
            frame_idx = 0

            while pos < total_len and not self.stop_event.is_set():
                chunk = raw_pcm[pos:pos + chunk_size]
                pos += chunk_size
                self.current_pos = pos

                # Direct C-level sample scaling matching active volume setting with zero CPU overhead
                cur_vol = getattr(self.bot, "volume_percent", 100)
                if cur_vol != 100:
                    try:
                        import audioop
                        chunk = audioop.mul(chunk, 2, max(0.0, min(1.5, cur_vol / 100.0)))
                    except Exception:
                        pass

                chunks_since_save += 1
                if chunks_since_save >= 250:  # Save position every 5.0s (asynchronously, zero disk latency)
                    chunks_since_save = 0
                    sec = pos / (self.sample_rate * self.channels * 2)
                    self.bot.current_playback_sec = sec
                    self.bot.resume_pos_sec = sec
                    self.bot.persist_state()

                if len(chunk) < chunk_size:
                    chunk += bytes(chunk_size - len(chunk))

                raw_buf = buf_type.from_buffer_copy(chunk)
                ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
                ab.uSampleIndex = sample_index
                sample_index += samples_per_frame

                ins_ok = self.bot.insertAudioBlock(ab)
                if not first_logged:
                    self.bot.diag.append(f"FIRST_INS:{ins_ok}")
                    first_logged = True

                if not ins_ok:
                    failed_inserts += 1
                    time.sleep(0.010)
                    if failed_inserts >= 30:
                        print(f"[Radio] insertAudioBlock rejected {failed_inserts} times. Fallback...", flush=True)
                        self.bot.diag.append("INS_FAIL_FALLBACK")
                        self.bot.stream_media_file_fallback(track_path)
                        return
                else:
                    failed_inserts = 0

                frame_idx += 1
                target_time = clock_start + (frame_idx * 0.020)
                now = time.perf_counter()
                sleep_sec = target_time - now
                if sleep_sec > 0.001:
                    time.sleep(sleep_sec)
                elif sleep_sec < -0.2:
                    # Resynchronize clock if OS stalled
                    clock_start = time.perf_counter()
                    frame_idx = 0

            # End audio block transmission session cleanly
            try:
                self.bot.insertAudioBlock(None)
            except Exception:
                pass

            if self.stop_event.is_set():
                sec = pos / (self.sample_rate * self.channels * 2)
                self.bot.current_playback_sec = sec
                self.bot.resume_pos_sec = sec
                self.bot.persist_state()
                print(f"[Radio] Playback paused/interrupted at {sec:.1f}s - position preserved.", flush=True)
            else:
                print("[Radio] Direct Voice track finished. Resetting position and playing next...", flush=True)
                self.bot.current_playback_sec = 0.0
                self.bot.resume_pos_sec = 0.0
                self.bot.persist_state()
                self.bot.is_streaming = False
                self.bot.last_track_finish_at = time.time()
                threading.Thread(target=self.bot.play_next, daemon=True).start()

        except Exception as e:
            print(f"[Radio] Direct Voice runtime error: {e}", flush=True)
            self.bot.diag.append(f"VOICE_ERR:{e}")
            try:
                self.bot.insertAudioBlock(None)
            except Exception:
                pass
            if not self.stop_event.is_set():
                threading.Thread(target=self.bot.play_next, daemon=True).start()

class RadioMusicBot(TeamTalk5.TeamTalk if 'TeamTalk5' in globals() else object):
    def __init__(self):
        super().__init__()
        self.connected = False
        self.logged_in = False
        self.joined = False
        self.playlist = []
        
        saved = load_saved_radio_state()
        self.volume_percent = saved.get("volume_percent", 25)
        self.title_hidden = saved.get("title_hidden", False)
        self.last_track_name = saved.get("last_track_name", "")
        self.saved_current_index = saved.get("current_index", 0)
        self.current_index = self.saved_current_index
        self.current_playback_sec = saved.get("playback_pos_sec", 0.0)
        self.resume_pos_sec = self.current_playback_sec
        self.created_at = time.time()
        self.last_connected_at = 0
        
        self.is_streaming = False
        self.current_track = None
        self.last_update_id = 0
        self.restart_requested = False
        self.lock = threading.RLock()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.diag = []
        self.voice_player = VoicePlayer(self)

    def persist_state(self):
        try:
            cur_sec = getattr(self, "current_playback_sec", 0.0)
            if hasattr(self, "voice_player") and getattr(self.voice_player, "current_pos", 0) > 0:
                cur_sec = self.voice_player.current_pos / (self.voice_player.sample_rate * self.voice_player.channels * 2)
                self.current_playback_sec = cur_sec
            vol = getattr(self, "volume_percent", SAVED_RADIO_VOLUME)
            state = {
                "volume_percent": vol,
                "title_hidden": self.title_hidden,
                "current_index": self.current_index,
                "last_track_name": self.current_track.get("title", "") if self.current_track else self.last_track_name,
                "playback_pos_sec": round(cur_sec, 2)
            }
            save_persistent_config("volume_percent", vol)
            save_radio_state(state)
        except Exception as e:
            print(f"[Radio] persist_state err: {e}", flush=True)

    def restore_track_index(self):
        with self.lock:
            if not self.playlist:
                return
            # اگر در حال پخش است، هرگز نباید ایندکس قطعه در حال خواندن تغییر کند
            if getattr(self, "is_streaming", False) and getattr(self, "current_track", None):
                for idx, t in enumerate(self.playlist):
                    if t.get("path") == self.current_track.get("path"):
                        self.current_index = idx
                        return
            if self.last_track_name:
                for idx, t in enumerate(self.playlist):
                    if t.get("title") == self.last_track_name:
                        self.current_index = idx
                        print(f"[Radio] Restored track to index {idx} ({self.last_track_name})", flush=True)
                        return
            if 0 <= self.saved_current_index < len(self.playlist):
                self.current_index = self.saved_current_index
                print(f"[Radio] Restored track to saved index {self.current_index}", flush=True)

    def apply_current_volume(self):
        try:
            percent = getattr(self, "volume_percent", 25)
            gain = int(max(0, min(150, percent)) / 100.0 * 1000)
            if hasattr(self, "_tt") and self._tt:
                TeamTalk5._SetSoundInputGainLevel(self._tt, gain)
            print(f"[Radio] apply_current_volume: {percent}% (gain: {gain})", flush=True)
            self.diag.append(f"VOL_SET:{percent}:{gain}")
        except Exception as e:
            print(f"[Radio] apply_current_volume err: {e}", flush=True)

    @staticmethod
    def get_playback_sequence(n):
        if n <= 1:
            return [0] if n == 1 else []
        evens = [i for i in range(0, n, 2)]
        odds = [i for i in range(1, n, 2)]
        return evens + list(reversed(odds))

    def get_next_track_index(self, from_index=None):
        with self.lock:
            n = len(self.playlist)
            if n <= 1:
                return 0
            curr = self.current_index if from_index is None else from_index
            seq = self.get_playback_sequence(n)
            if curr in seq:
                pos = seq.index(curr)
                return seq[(pos + 1) % n]
            return seq[0]

    def get_prev_track_index(self, from_index=None):
        with self.lock:
            n = len(self.playlist)
            if n <= 1:
                return 0
            curr = self.current_index if from_index is None else from_index
            seq = self.get_playback_sequence(n)
            if curr in seq:
                pos = seq.index(curr)
                return seq[(pos - 1) % n]
            return seq[0]

    def tg_api(self, method, params=None):
        url = f"https://api.telegram.org/bot{RADIO_TG_TOKEN}/{method}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with self.opener.open(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print(f"[Radio] TG API {method} error: {e}", flush=True)
            return {}

    def download_tg_file(self, file_id, dest_path):
        try:
            finfo = self.tg_api("getFile", {"file_id": file_id})
            if not finfo.get("ok"):
                return False
            file_path = finfo["result"]["file_path"]
            download_url = f"https://api.telegram.org/file/bot{RADIO_TG_TOKEN}/{file_path}"
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with self.opener.open(req, timeout=60) as resp, open(dest_path, "wb") as f:
                f.write(resp.read())
            return True
        except Exception as e:
            print(f"[Radio] Download error: {e}", flush=True)
            return False

    def sync_telegram_playlist(self):
        # 1. Download and ensure all catalog tracks are available
        for item in BASE_TRACK_CATALOG:
            mid = item.get("msg_id", 0)
            fid = item.get("file_id")
            title = item.get("title") or f"track_{mid}"
            performer = item.get("performer") or ""
            clean_title = "".join(c for c in title if c.isalnum() or c in " ._-()").strip()
            if not clean_title.endswith(".mp3"):
                clean_title += ".mp3"
            dest_filename = f"{mid}_{clean_title}"
            dest_path = os.path.join(RADIO_CACHE_DIR, dest_filename)
            display_name = f"{performer} - {title}".strip(" -")
            track_info = {"msg_id": mid, "title": display_name, "path": dest_path}

            if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
                print(f"[Radio] Downloading catalog track: {display_name}", flush=True)
                if self.download_tg_file(fid, dest_path):
                    with self.lock:
                        if not any(x["path"] == dest_path for x in self.playlist):
                            self.playlist.append(track_info)
                            print(f"[Radio] Catalog track ready: {display_name} ({len(self.playlist)} tracks)", flush=True)
                            if self.joined and not self.is_streaming:
                                threading.Thread(target=self.play_track, args=(self.current_index,), daemon=True).start()
            else:
                with self.lock:
                    if not any(t["path"] == dest_path for t in self.playlist):
                        self.playlist.append(track_info)
                        if self.joined and not self.is_streaming:
                            threading.Thread(target=self.play_track, args=(self.current_index,), daemon=True).start()

        # 2. Check getUpdates for any brand new tracks posted by users
        try:
            updates = self.tg_api("getUpdates", {"limit": 50})
            added_any = False
            max_uid = 0
            for u in updates.get("result", []):
                uid = u.get("update_id", 0)
                if uid > max_uid:
                    max_uid = uid
                cp = u.get("channel_post") or u.get("message")
                if not cp:
                    continue
                audio = cp.get("audio") or cp.get("voice") or cp.get("document")
                if not audio:
                    continue
                file_id = audio.get("file_id")
                title = audio.get("title") or audio.get("file_name") or f"track_{cp['message_id']}"
                performer = audio.get("performer") or ""
                clean_title = "".join(c for c in title if c.isalnum() or c in " ._-()").strip()
                if not clean_title.endswith(".mp3"):
                    clean_title += ".mp3"
                dest_filename = f"{cp['message_id']}_{clean_title}"
                dest_path = os.path.join(RADIO_CACHE_DIR, dest_filename)
                display_name = f"{performer} - {title}".strip(" -")
                track_info = {"msg_id": cp["message_id"], "title": display_name, "path": dest_path}

                if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
                    print(f"[Radio] Downloading new user track: {display_name}", flush=True)
                    if self.download_tg_file(file_id, dest_path):
                        with self.lock:
                            if not any(x["path"] == dest_path for x in self.playlist):
                                self.playlist.append(track_info)
                                added_any = True
                                print(f"[Radio] Added user track: {display_name}", flush=True)
                                if self.joined and not self.is_streaming:
                                    threading.Thread(target=self.play_track, args=(self.current_index,), daemon=True).start()
                else:
                    with self.lock:
                        if not any(t["path"] == dest_path for t in self.playlist):
                            self.playlist.append(track_info)
                            added_any = True

            if max_uid > 0:
                self.tg_api("getUpdates", {"offset": max_uid + 1})

            if added_any and self.joined:
                self.update_player_title()
        except Exception as e:
            print(f"[Radio] getUpdates poll err: {e}", flush=True)

    def load_existing_cache(self):
        if not os.path.exists(RADIO_CACHE_DIR):
            return
        files = sorted(os.listdir(RADIO_CACHE_DIR))
        for fname in files:
            if fname.lower().endswith((".mp3", ".m4a", ".ogg", ".wav")):
                path = os.path.join(RADIO_CACHE_DIR, fname)
                title = os.path.splitext(fname)[0]
                if "_" in title:
                    title = title.split("_", 1)[1]
                with self.lock:
                    if not any(t["path"] == path for t in self.playlist):
                        self.playlist.append({
                            "title": title,
                            "path": path
                        })
        print(f"[Radio] Loaded {len(self.playlist)} tracks from cache.", flush=True)
        self.restore_track_index()

    def update_player_title(self):
        with self.lock:
            if not self.playlist:
                curr_title = "در انتظار موزیک"
                next_title = "ندارد"
            else:
                idx = self.current_index % len(self.playlist)
                curr_track = self.playlist[idx]
                curr_title = curr_track.get("title", f"قطعه {idx + 1}")
                next_idx = self.get_next_track_index(idx)
                next_track = self.playlist[next_idx]
                next_title = next_track.get("title", f"قطعه {next_idx + 1}")

        if getattr(self, "title_hidden", False):
            status_text = ""
        else:
            status_text = f"در حال پخش: {curr_title} | بعدی: {next_title}"

        print(f"[Radio] Updating player title: {status_text}", flush=True)
        try:
            self.doChangeStatus(0, status_text)
            self.diag.append(f"TITLE:{'HIDDEN' if getattr(self, 'title_hidden', False) else curr_title[:8]}")
        except Exception as e:
            print(f"[Radio] doChangeStatus error: {e}", flush=True)

    def send_chat(self, text):
        if not self.joined:
            return
        try:
            msgs = TeamTalk5.buildTextMessage(text, TeamTalk5.TextMsgType.MSGTYPE_CHANNEL, nChannelID=RADIO_CHAN_ID)
            for m in msgs:
                self.doTextMessage(m)
        except Exception as e:
            print(f"[Radio] send_chat error: {e}", flush=True)

    def play_track(self, index, start_sec=None):
        with self.lock:
            if not self.playlist:
                return
            new_idx = index % len(self.playlist)
            if new_idx != self.current_index:
                start_sec = 0.0
                self.resume_pos_sec = 0.0
                self.current_playback_sec = 0.0
            
            self.current_index = new_idx
            track = self.playlist[self.current_index]
            self.current_track = track

            if start_sec is None:
                start_sec = getattr(self, "resume_pos_sec", 0.0)
            
            self.current_playback_sec = start_sec
            self.persist_state()

        self.apply_current_volume()
        print(f"[Radio] Playing direct voice [{self.current_index + 1}/{len(self.playlist)}]: {track['title']} (from {start_sec:.1f}s)", flush=True)
        try:
            self.stop_all_playback()
            time.sleep(0.2)
            self.voice_player.play(track["path"], start_sec=start_sec)
        except Exception as e:
            print(f"[Radio] Playback launch error: {e}", flush=True)
            self.diag.append(f"PLAY_ERR:{type(e).__name__}")

    def stop_all_playback(self):
        try:
            self.voice_player.stop()
        except Exception:
            pass
        try:
            self.stopStreamingMediaFileToChannel()
        except Exception:
            pass
        try:
            self.enableVoiceTransmission(False)
        except Exception:
            pass
        self.is_streaming = False

    def stream_media_file_fallback(self, track_path):
        try:
            ok = self.startStreamingMediaFileToChannel(track_path, None)
            self.diag.append(f"FALLBACK_STR:{ok}")
            if ok:
                self.is_streaming = True
                self.update_player_title()
            else:
                time.sleep(2)
                self.play_next()
        except Exception as e:
            print(f"[Radio] stream_media_file_fallback err: {e}", flush=True)
            self.play_next()

    def play_next(self, admin_name=None):
        if not self.playlist:
            return
        next_idx = self.get_next_track_index()
        self.resume_pos_sec = 0.0
        self.play_track(next_idx, start_sec=0.0)

    def play_prev(self, admin_name=None):
        if not self.playlist:
            return
        prev_idx = self.get_prev_track_index()
        self.resume_pos_sec = 0.0
        self.play_track(prev_idx, start_sec=0.0)

    def set_volume(self, percent, admin_name=None):
        global SAVED_RADIO_VOLUME
        percent = max(0, min(150, percent))
        self.volume_percent = percent
        SAVED_RADIO_VOLUME = percent
        save_persistent_config("volume_percent", percent)
        self.persist_state()
        self.apply_current_volume()
        
        msg = f"🔊 بلندی صدای رادیو روی {percent}٪ تنظیم شد و به صورت دائم ذخیره گردید."
        if admin_name:
            msg += f" (توسط {admin_name})"
        self.send_chat(msg)

    def schedule_file_auto_delete(self, chan_id, file_id, file_name, delay_sec=240):
        def _delete_worker():
            print(f"[Radio] Auto-delete countdown started: '{file_name}' (ID: {file_id}) will be deleted in {delay_sec}s", flush=True)
            time.sleep(delay_sec)
            try:
                print(f"[Radio] Deleting expired file '{file_name}' (ID: {file_id})...", flush=True)
                self.doDeleteFile(chan_id, file_id)
                self.send_chat(f"🗑 فایل موقت «{file_name}» پس از پایان مهلت ۴ دقیقه‌ای دانلود، با موفقیت از روم پاکسازی شد.")
            except Exception as e:
                print(f"[Radio] doDeleteFile error: {e}", flush=True)
        threading.Thread(target=_delete_worker, daemon=True).start()

    def cleanup_old_channel_files(self):
        try:
            files = self.getChannelFiles(RADIO_CHAN_ID)
            for rf in files:
                owner = TeamTalk5.ttstr(rf.szUsername).strip()
                if owner in [RADIO_TT_USER, RADIO_TT_NICK, ""] or not owner:
                    fid = rf.nFileID
                    fname = TeamTalk5.ttstr(rf.szFileName)
                    print(f"[Radio] Auto-cleaning stale file on join: {fname} (ID {fid})", flush=True)
                    self.doDeleteFile(RADIO_CHAN_ID, fid)
        except Exception as e:
            print(f"[Radio] cleanup_old_channel_files error: {e}", flush=True)

    def upload_current_to_channel(self, requester_name):
        if not self.current_track or not os.path.exists(self.current_track["path"]):
            self.send_chat("❌ در حال حاضر آهنگی در حال پخش نیست.")
            return
        track = self.current_track
        try:
            print(f"[Radio] Uploading {track['path']} to room for {requester_name}...", flush=True)
            self.send_chat(f"⏳ در حال آپلود فایل «{track['title']}» در بخش فایل‌های روم برای {requester_name} (مهلت دانلود: ۴ دقیقه)...")
            self.doSendFile(RADIO_CHAN_ID, track["path"])
        except Exception as e:
            print(f"[Radio] doSendFile error: {e}", flush=True)
            self.send_chat(f"❌ خطا در قرار دادن فایل آهنگ: {e}")

    def onCmdError(self, nSource, clienterrormsg):
        try:
            n_err = getattr(clienterrormsg, "nErrorNo", getattr(clienterrormsg, "nError", 0))
            err_msg = TeamTalk5.ttstr(clienterrormsg.szErrorMsg)
            self.diag.append(f"CMD_ERR:{nSource}:{n_err}:{err_msg}")
            print(f"[Radio] CMD ERROR (src {nSource}): {n_err} - {err_msg}", flush=True)
            if "already in channel" in err_msg.lower() or n_err == 1016:
                self.joined = True
        except Exception as e:
            print(f"[Radio] onCmdError handler err: {e}", flush=True)

    def onCmdSuccess(self, nSource):
        self.diag.append(f"CMD_OK:{nSource}")
        print(f"[Radio] CMD SUCCESS (src {nSource})", flush=True)

    def onCmdProcessing(self, nSource, bCompleted):
        pass

    def onConnectSuccess(self):
        self.diag.append("CON_SUCCESS")
        print("[Radio] Connected to TeamTalk server!", flush=True)
        self.connected = True
        self.last_connected_at = time.time()
        cmd_id = self.doLogin(RADIO_TT_NICK, RADIO_TT_USER, RADIO_TT_PASS, "TeamTalk5")
        self.diag.append(f"LOGIN_CMD:{cmd_id}")

    def onConnectFailed(self):
        self.diag.append("CON_FAILED")
        print("[Radio] Connect failed! Recreating instance...", flush=True)
        self.connected = False
        self.persist_state()
        self.restart_requested = True

    def onConnectionLost(self):
        self.diag.append("CON_LOST")
        print("[Radio] Connection lost! Preserving playback position and recreating instance...", flush=True)
        self.persist_state()
        self.connected = False
        self.logged_in = False
        self.joined = False
        self.is_streaming = False
        self.restart_requested = True

    def onCmdMyselfLoggedIn(self, my_id, user_account):
        self.diag.append(f"LOGGED_IN:{my_id}")
        print(f"[Radio] Logged in! MyID: {my_id}", flush=True)
        self.logged_in = True
        self.my_user_id = my_id
        self.apply_current_volume()
        self.doChangeNickname(RADIO_TT_NICK)
        
        my_chan = 0
        try:
            u = self.getUser(my_id)
            if u:
                my_chan = u.nChannelID
        except Exception:
            pass
            
        if my_chan == RADIO_CHAN_ID:
            print(f"[Radio] Already in channel {RADIO_CHAN_ID} via initchan!", flush=True)
            self.joined = True
            self.cleanup_old_channel_files()
            self.restore_track_index()
            self.update_player_title()
            if self.playlist and not self.is_streaming:
                start_at = getattr(self, "resume_pos_sec", 0.0)
                threading.Thread(target=self.play_track, args=(self.current_index, start_at), daemon=True).start()
        else:
            res = self.doJoinChannelByID(RADIO_CHAN_ID, "")
            self.diag.append(f"JOIN_CMD:{res}")

    def onCmdUserJoinedChannel(self, user):
        my_id = getattr(self, "my_user_id", self.getMyUserID())
        self.diag.append(f"JOIN:{user.nUserID}:{user.nChannelID}")
        if user.nUserID == my_id and user.nChannelID == RADIO_CHAN_ID:
            print(f"[Radio] Joined channel {user.nChannelID} successfully!", flush=True)
            self.joined = True
            self.apply_current_volume()
            self.cleanup_old_channel_files()
            self.restore_track_index()
            self.update_player_title()
            if self.playlist and not self.is_streaming:
                start_at = getattr(self, "resume_pos_sec", 0.0)
                print(f"[Radio] Auto-resuming track {self.current_index + 1} at {start_at:.1f}s", flush=True)
                threading.Thread(target=self.play_track, args=(self.current_index, start_at), daemon=True).start()

    def onCmdMyselfKickedFromChannel(self, nSource, user):
        print("[Radio] Bot left or kicked. Preserving position and rejoining...", flush=True)
        self.joined = False
        self.persist_state()
        time.sleep(2)
        self.doJoinChannelByID(RADIO_CHAN_ID, "")

    def onStreamMediaFile(self, mediafileinfo):
        status = getattr(mediafileinfo, "nStatus", -1)
        self.diag.append(f"MFS:{status}")
        if status in [TeamTalk5.MediaFileStatus.MFS_FINISHED, TeamTalk5.MediaFileStatus.MFS_ERROR, TeamTalk5.MediaFileStatus.MFS_ABORTED]:
            print(f"[Radio] Track ended (status {status}). Playing next...", flush=True)
            self.is_streaming = False
            threading.Thread(target=self.play_next, daemon=True).start()

    def onCmdFileNew(self, remotefile):
        if remotefile.nChannelID == RADIO_CHAN_ID:
            fname = TeamTalk5.ttstr(remotefile.szFileName)
            owner = TeamTalk5.ttstr(remotefile.szUsername).strip()
            fid = remotefile.nFileID
            chid = remotefile.nChannelID
            print(f"[Radio] File ready in room: {fname} (ID {fid}, Owner: {owner})", flush=True)
            if owner in [RADIO_TT_USER, RADIO_TT_NICK, ""] or not owner:
                self.send_chat(f"✅ فایل «{fname}» در بخش فایل‌های روم قرار گرفت. این فایل به مدت ۴ دقیقه برای دانلود در دسترس است و پس از آن خودکار حذف خواهد شد.")
                self.schedule_file_auto_delete(chid, fid, fname, delay_sec=240)
            else:
                self.send_chat(f"✅ فایل «{fname}» در بخش فایل‌های روم قرار گرفت.")

    def onCmdUserTextMessage(self, textmessage):
        sender = TeamTalk5.ttstr(textmessage.szFromUsername).strip()
        sender_lower = sender.lower()
        msg_text = TeamTalk5.ttstr(textmessage.szMessage).strip().lower()
        
        print(f"[Radio] Chat from [{sender}]: {msg_text}", flush=True)
        
        if msg_text in ["dl", "دانلود"]:
            threading.Thread(target=self.upload_current_to_channel, args=(sender,), daemon=True).start()
            return
            
        is_admin = (sender_lower in RADIO_ADMINS)
        if not is_admin:
            try:
                user = self.getUser(textmessage.nFromUserID)
                if user and (getattr(user, "uUserType", 0) & 3 != 0):
                    is_admin = True
                elif hasattr(self, "_tt") and self._tt:
                    is_admin = bool(TeamTalk5._IsChannelOperator(self._tt, RADIO_CHAN_ID, textmessage.nFromUserID))
            except Exception:
                pass

        if is_admin:
            if msg_text in ["n", "next", "بعدی"]:
                threading.Thread(target=self.play_next, args=(sender,), daemon=True).start()
            elif msg_text in ["b", "prev", "back", "قبلی"]:
                threading.Thread(target=self.play_prev, args=(sender,), daemon=True).start()
            elif any(msg_text.startswith(p) for p in ["v", "vol", "volume", "صدا"]):
                part = msg_text
                for prefix in ["volume", "vol", "صدا", "v"]:
                    if part.startswith(prefix):
                        part = part[len(prefix):].strip()
                        break
                persian_digits = "۰۱۲۳۴۵۶۷۸۹"
                arabic_digits = "٠١٢٣٤٥٦٧٨٩"
                for i in range(10):
                    part = part.replace(persian_digits[i], str(i)).replace(arabic_digits[i], str(i))
                part = part.replace("%", "").strip()
                if part.isdigit():
                    vol = int(part)
                    self.set_volume(vol, sender)
            elif msg_text in ["h", "تایتل", "hide"]:
                self.title_hidden = not self.title_hidden
                self.persist_state()
                self.update_player_title()
                if self.title_hidden:
                    self.send_chat("🙈 تایتل پلیر مخفی شد.")
                else:
                    self.send_chat("👁 تایتل پلیر نمایش داده شد.")
            elif msg_text in ["rc", "reconnect", "restart", "ریستارت"]:
                self.send_chat("🔄 ربات در حال راه‌اندازی مجدد و ورود دوباره است (موقعیت آهنگ حفظ می‌شود)...")
                self.persist_state()
                self.restart_requested = True
            elif msg_text in ["rc full", "rc proc", "reboot"]:
                self.send_chat("🔄 در حال راه‌اندازی کامل پروسه سرور...")
                time.sleep(1)
                os._exit(0)
            elif msg_text in ["help", "راهنما"]:
                help_text = (
                    "📋 راهنمای دستورات رادیو کافه دوستی:\n"
                    "• دستور dl یا دانلود: قرار دادن آهنگ فعلی در فایل‌های کانال (همه کاربران)\n"
                    "• دستور n یا بعدی: پخش آهنگ بعدی (مدیران)\n"
                    "• دستور b یا قبلی: پخش آهنگ قبلی (مدیران)\n"
                    "• دستور v با عدد (مثل v 80): تنظیم بلندی صدا (مدیران)\n"
                    "• دستور h: مخفی کردن یا نمایش مجدد تایتل پلیر (مدیران)\n"
                    "• دستور rc: راه‌اندازی مجدد و خروج و ورود دوباره ربات (مدیران)"
                )
                self.send_chat(help_text)

def radio_telegram_sync_worker(bot):
    while not getattr(bot, "restart_requested", False):
        try:
            bot.sync_telegram_playlist()
        except Exception as e:
            print(f"[Radio] Sync error: {e}", flush=True)
        time.sleep(15)

def start_radio_worker():
    global global_radio_bot
    print("شروع سرویس رادیو کافه دوستی...", flush=True)
    ensure_linux_tt_sdk()
    while True:
        try:
            bot = RadioMusicBot()
            global_radio_bot = bot
            bot.load_existing_cache()
            # Start telegram sync in background so connect() starts immediately without delay
            threading.Thread(target=radio_telegram_sync_worker, args=(bot,), daemon=True).start()
            
            last_connect_attempt = 0
            while not getattr(bot, "restart_requested", False):
                try:
                    flags = bot.getFlags()
                    is_connecting_or_connected = (flags & (0x00002000 | 0x00004000)) != 0
                    if not is_connecting_or_connected and (time.time() - last_connect_attempt > 5):
                        last_connect_attempt = time.time()
                        print(f"[Radio] Connecting to {RADIO_TT_HOST}:{RADIO_TT_PORT} (TCP-tunneled audio)...", flush=True)
                        bot.diag.append("DO_CONNECT")
                        # Setting nUdpPort=0 routes audio cleanly over TCP with 0% packet loss
                        res = bot.connect(RADIO_TT_HOST, RADIO_TT_PORT, RADIO_TT_PORT, 0, 0, False)
                        bot.diag.append(f"CONN_RES:{res}")
                        print(f"[Radio] connect() called, returned: {res}", flush=True)
                        if not res:
                            print("[Radio] connect() returned 0 (instance closed). Recreating bot...", flush=True)
                            bot.persist_state()
                            bot.restart_requested = True
                            break
                    bot.runEventLoop(20)
                except Exception as e:
                    bot.diag.append(f"EXC:{type(e).__name__}:{e}")
                    print(f"[Radio] Loop err: {e}", flush=True)
                    time.sleep(1)

            print("[Radio] Restart requested. Disconnecting and restarting bot instance...", flush=True)
            try:
                bot.stop_all_playback()
                time.sleep(0.5)
                bot.disconnect()
                time.sleep(2)
            except Exception as e:
                print(f"[Radio] Disconnect err during restart: {e}", flush=True)

        except Exception as e:
            print(f"[Radio] Fatal error in start_radio_worker: {e}", flush=True)
            time.sleep(3)

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            import ctypes
            if self.path == "/restart_radio":
                b = global_radio_bot
                if b:
                    b.persist_state()
                    b.restart_requested = True
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Radio restart requested")
                return
            if self.path == "/reboot_process":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Rebooting process...")
                import threading
                threading.Thread(target=lambda: (time.sleep(0.5), os._exit(0)), daemon=True).start()
                return
            if self.path == "/probe_voice":
                b = global_radio_bot
                if not b:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"No bot")
                    return
                try:
                    chan = b.getChannel(RADIO_CHAN_ID)
                    codec_type = getattr(chan.audiocodec, "nCodec", -1)
                    opus_sr = 0
                    opus_ch = 0
                    opus_br = 0
                    if codec_type == TeamTalk5.Codec.OPUS_CODEC:
                        opus_sr = getattr(chan.audiocodec.opus, "nSampleRate", 0)
                        opus_ch = getattr(chan.audiocodec.opus, "nChannels", 0)
                        opus_br = getattr(chan.audiocodec.opus, "nBitRate", 0)
                    res = {
                        "flags": hex(b.getFlags()),
                        "chan_codec": codec_type,
                        "opus_sr": opus_sr,
                        "opus_ch": opus_ch,
                        "opus_br": opus_br,
                        "diag": b.diag[-10:],
                        "is_streaming": b.is_streaming,
                    }
                    
                    # Test insertAudioBlock with enableVoiceTransmission(False)
                    b.enableVoiceTransmission(False)
                    time.sleep(0.05)
                    res["flags_after_tx_false"] = hex(b.getFlags())
                    
                    # Test stereo 960 (3840 bytes)
                    raw_data_s = bytes(3840)
                    buf_s = (ctypes.c_byte * 3840).from_buffer_copy(raw_data_s)
                    ab_s = TeamTalk5.AudioBlock()
                    ab_s.nStreamID = 1
                    ab_s.nSampleRate = 48000
                    ab_s.nChannels = 2
                    ab_s.nSamples = 960
                    ab_s.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
                    ab_s.lpRawAudio = ctypes.cast(buf_s, ctypes.c_void_p)
                    res["ins_stereo_960"] = b.insertAudioBlock(ab_s)
                    
                    # Test mono 960 (1920 bytes)
                    raw_data_m = bytes(1920)
                    buf_m = (ctypes.c_byte * 1920).from_buffer_copy(raw_data_m)
                    ab_m = TeamTalk5.AudioBlock()
                    ab_m.nStreamID = 1
                    ab_m.nSampleRate = 48000
                    ab_m.nChannels = 1
                    ab_m.nSamples = 960
                    ab_m.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
                    ab_m.lpRawAudio = ctypes.cast(buf_m, ctypes.c_void_p)
                    res["ins_mono_960"] = b.insertAudioBlock(ab_m)
                    
                    b.insertAudioBlock(None)
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(res, ensure_ascii=False, indent=2).encode('utf-8'))
                    return
                except Exception as e:
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(f"Probe err: {e}".encode('utf-8'))
                    return
            if self.path == "/radio_status":
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(get_radio_status().encode('utf-8'))
                return
            if self.path == "/test_tt_sdk":
                ok, msg = ensure_linux_tt_sdk()
                load_msg = ""
                if ok:
                    try:
                        import ctypes
                        dll = ctypes.cdll.LoadLibrary("./libTeamTalk5.so")
                        dll.TT_InitTeamTalkPoll.restype = ctypes.c_void_p
                        res = dll.TT_InitTeamTalkPoll()
                        load_msg = f"SUCCESS! TTInstance: {res}"
                        dll.TT_CloseTeamTalk.argtypes = [ctypes.c_void_p]
                        dll.TT_CloseTeamTalk(res)
                    except Exception as e:
                        load_msg = f"Load failed: {e}"
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Ensure: {ok} ({msg})\nLoad: {load_msg}".encode('utf-8'))
                return
            if self.path == "/server_info":
                b = global_radio_bot
                if not b or not b.connected:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Bot not connected")
                    return
                try:
                    chans = []
                    for cid in range(1, 40):
                        try:
                            c = b.getChannel(cid)
                            if c.nChannelID == cid:
                                chans.append({
                                    "nChannelID": c.nChannelID,
                                    "nParentID": c.nParentID,
                                    "szName": TeamTalk5.ttstr(c.szName),
                                    "szTopic": TeamTalk5.ttstr(c.szTopic),
                                    "uChannelType": c.uChannelType,
                                    "nDiskQuota": c.nDiskQuota,
                                    "nMaxUsers": c.nMaxUsers,
                                })
                        except Exception:
                            pass
                    users_raw = b.getServerUsers()
                    users = []
                    for u in users_raw:
                        users.append({
                            "nUserID": u.nUserID,
                            "szNickname": TeamTalk5.ttstr(u.szNickname),
                            "szUsername": TeamTalk5.ttstr(u.szUsername),
                            "nChannelID": u.nChannelID,
                        })
                    res_data = {"channels": chans, "users": users}
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(res_data, ensure_ascii=False, indent=2).encode('utf-8'))
                    return
                except Exception as e:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(f"Err: {e}".encode('utf-8'))
                    return
            if self.path == "/test_splus":
                url = f"https://api.splus.ir/bot{SPLUS_TOKEN}/getMe"
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        res = resp.read().decode('utf-8')
                        self.send_response(200)
                        self.send_header("Content-type", "text/plain; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(f"SPLUS OK: {res}".encode('utf-8'))
                except Exception as e:
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(f"SPLUS ERR: {e}".encode('utf-8'))
                return
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("ربات کافه دوستی به صورت ۲۴ ساعته در تلگرام و سروش فعال است.".encode('utf-8'))
        def log_message(self, format, *args):
            pass
    try:
        with socketserver.TCPServer(("", port), HealthHandler) as httpd:
            print(f"سرور سلامت روی پورت {port} فعال شد.", flush=True)
            httpd.serve_forever()
    except Exception as e:
        print(f"خطای سرور سلامت: {e}", flush=True)

threading.Thread(target=run_health_server, daemon=True).start()

# ----------------- سیستم دیده‌بان و پایش خودکار ربات ناظر (Watchdog Engine) -----------------
def run_supervisor_watchdog():
    """حلقه پایش و دیده‌بان خودکار ربات ناظر (Watchdog)
    به طور پیوسته وضعیت ربات‌های ثبت شده را پایش کرده و در صورت خروج یا قطعی،
    بلافاصله و به صورت کاملاً خودکار و بدون ارسال پیام اضافه آن‌ها را به سرور بازمی‌گرداند."""
    print("دیده‌بان خودکار ربات ناظر (Watchdog Engine) فعال شد و در حال پایش ربات‌هاست...", flush=True)
    time.sleep(15)  # مهلت اولیه برای راه‌اندازی کامل سرویس‌ها
    while True:
        try:
            b = global_radio_bot
            if b:
                age = time.time() - getattr(b, "created_at", 0)
                # مهلت ۳۰ ثانیه‌ای برای استارتاپ اولیه ربات جهت اتصال خودکار
                if age > 30:
                    try:
                        flags = b.getFlags()
                    except Exception:
                        flags = 0

                    is_connected = (flags & 0x00004000) != 0

                    if not is_connected:
                        # اگر پس از مهلت اولیه یا پس از قطعی، هنوز وصل نشده
                        if not getattr(b, "restart_requested", False):
                            print("[Watchdog] ربات ناظر عدم اتصال رادیو را تایید کرد. احیای خودکار...", flush=True)
                            b.persist_state()
                            b.restart_requested = True
                    elif not getattr(b, "joined", False):
                        # متصل است ولی در اتاق ۲ نیست -> دستور ورود فوری صادر می‌کند
                        try:
                            b.doJoinChannelByID(RADIO_CHAN_ID, "")
                        except Exception:
                            pass
                    elif getattr(b, "playlist", None) and not getattr(b, "is_streaming", False) and (time.time() - getattr(b, "last_track_finish_at", 0) > 5):
                        # در اتاق است ولی موزیک متوقف مانده -> پخش را ادامه می‌دهد
                        try:
                            threading.Thread(target=b.play_track, args=(b.current_index,), daemon=True).start()
                        except Exception:
                            pass
        except Exception as e:
            print(f"[Watchdog] Error in supervisor watchdog: {e}", flush=True)

        time.sleep(15)

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
threading.Thread(target=get_tt_existing_cached, daemon=True).start()
threading.Thread(target=run_inactivity_checker, daemon=True).start()
threading.Thread(target=monitor_teamtalk_activity, daemon=True).start()
threading.Thread(target=start_radio_worker, daemon=True).start()
threading.Thread(target=run_supervisor_watchdog, daemon=True).start()

# ----------------- حلقه دریافت پیام‌های سروش پلاس -----------------
def run_soroush_bot():
    print("ربات سروش پلاس کافه دوستی فعال شد و آماده دریافت پیام است...", flush=True)
    offset = None
    while True:
        try:
            url = f"https://api.splus.ir/bot{SPLUS_TOKEN}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("ok"):
                    for item in data.get("result", []):
                        offset = item["update_id"] + 1
                        if "message" in item:
                            handle_splus_message(item["message"])
                        elif "callback_query" in item:
                            handle_splus_callback_query(item["callback_query"])
        except Exception as e:
            time.sleep(3)

threading.Thread(target=run_soroush_bot, daemon=True).start()

# ----------------- حلقه اصلی دریافت پیام‌های تلگرام -----------------
def run_bot():
    print("ربات تلگرام کافه دوستی فعال شد و آماده دریافت پیام است...", flush=True)
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=30"
            if offset:
                url += f"&offset={offset}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=45) as resp:
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
