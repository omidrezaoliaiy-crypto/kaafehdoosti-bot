import base64 as _b64
TELEGRAM_API_BASE = "https://tg.kaafehdoosti.ir"
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
import http.server
import socketserver

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

# ----------------- سرور سلامت و مانیتورینگ Render (شروع سریع در خطوط آغازین) -----------------
def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            import ctypes
            if self.path == "/restart_radio":
                b = globals().get("global_radio_bot")
                if b:
                    try:
                        b.persist_state()
                    except Exception:
                        pass
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
                b = globals().get("global_radio_bot")
                if not b:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"No bot")
                    return
                try:
                    chan_id = globals().get("RADIO_CHAN_ID", 2)
                    tt5 = globals().get("TeamTalk5")
                    chan = b.getChannel(chan_id)
                    codec_type = getattr(chan.audiocodec, "nCodec", -1)
                    opus_sr = 0
                    opus_ch = 0
                    opus_br = 0
                    if tt5 and codec_type == tt5.Codec.OPUS_CODEC:
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
                status_func = globals().get("get_radio_status")
                msg = status_func() if status_func else "در حال راه‌اندازی..."
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(msg.encode('utf-8'))
                return
            if self.path == "/nostalgia_status":
                status_func = globals().get("get_nostalgia_status")
                msg = status_func() if status_func else "در حال راه‌اندازی نستالژی پلیر..."
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(msg.encode('utf-8'))
                return
            if self.path == "/restart_nostalgia":
                b = globals().get("global_nostalgia_bot")
                if b:
                    try:
                        b.persist_state()
                    except Exception:
                        pass
                    b.restart_requested = True
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Nostalgia restart requested")
                return
            if self.path == "/debug_test":
                res = {}
                try:
                    import miniaudio
                    res["miniaudio"] = "OK"
                except Exception as e:
                    res["miniaudio"] = f"FAIL: {e}"
                
                try:
                    res["radio_cache"] = os.listdir(globals().get("RADIO_CACHE_DIR", "music_cache"))
                except Exception as e:
                    res["radio_cache"] = f"ERR: {e}"

                try:
                    res["nostalgia_cache"] = os.listdir(globals().get("NOSTALGIA_CACHE_DIR", "music_cache_nostalgia"))
                except Exception as e:
                    res["nostalgia_cache"] = f"ERR: {e}"

                try:
                    import resource
                    mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    res["memory_mb"] = round(mem_kb / 1024.0, 1)
                except Exception:
                    pass
                nb = globals().get("global_nostalgia_bot")
                if nb:
                    res["nostalgia_bot"] = {
                        "connected": nb.connected,
                        "logged_in": nb.logged_in,
                        "joined": nb.joined,
                        "is_streaming": nb.is_streaming,
                        "current_index": nb.current_index,
                        "current_track": nb.current_track,
                        "playlist_len": len(nb.playlist),
                        "diag": nb.diag[-15:],
                        "vp_thread_alive": bool(nb.voice_player.thread and nb.voice_player.thread.is_alive()),
                        "vp_pos": getattr(nb.voice_player, "current_pos", 0)
                    }

                rb = globals().get("global_radio_bot")
                if rb:
                    res["radio_bot"] = {
                        "connected": rb.connected,
                        "logged_in": rb.logged_in,
                        "joined": rb.joined,
                        "is_streaming": rb.is_streaming,
                        "current_index": rb.current_index,
                        "current_track": rb.current_track,
                        "playlist_len": len(rb.playlist),
                        "diag": rb.diag[-15:],
                        "vp_thread_alive": bool(rb.voice_player.thread and rb.voice_player.thread.is_alive()),
                        "vp_pos": getattr(rb.voice_player, "current_pos", 0)
                    }

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False, indent=2).encode('utf-8'))
                return
            if self.path == "/probe_nostalgia":
                b = globals().get("global_nostalgia_bot")
                if not b:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"No nostalgia bot")
                    return
                try:
                    chan_id = getattr(b, "chan_id", 5)
                    tt5 = globals().get("TeamTalk5")
                    chan = b.getChannel(chan_id)
                    codec_type = getattr(chan.audiocodec, "nCodec", -1)
                    opus_sr = 0
                    opus_ch = 0
                    opus_br = 0
                    if tt5 and codec_type == tt5.Codec.OPUS_CODEC:
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
            if self.path == "/test_tt_sdk":
                ensure_func = globals().get("ensure_linux_tt_sdk")
                ok, msg = ensure_func() if ensure_func else (False, "Not defined yet")
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
                b = globals().get("global_radio_bot")
                if not b or not getattr(b, "connected", False):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Bot not connected")
                    return
                try:
                    tt5 = globals().get("TeamTalk5")
                    chans = []
                    for cid in range(1, 40):
                        try:
                            c = b.getChannel(cid)
                            if c.nChannelID == cid:
                                chans.append({
                                    "nChannelID": c.nChannelID,
                                    "nParentID": c.nParentID,
                                    "szName": tt5.ttstr(c.szName) if tt5 else str(c.szName),
                                    "szTopic": tt5.ttstr(c.szTopic) if tt5 else str(c.szTopic),
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
                            "szNickname": tt5.ttstr(u.szNickname) if tt5 else str(u.szNickname),
                            "szUsername": tt5.ttstr(u.szUsername) if tt5 else str(u.szUsername),
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

# ----------------- سیستم ضد خواب خودکار Render (Anti-Sleep Self-Ping) -----------------
def render_anti_sleep():
    time.sleep(20)
    app_url = os.environ.get("RENDER_EXTERNAL_URL", "https://kaafehdoosti-bot.onrender.com")
    while True:
        try:
            req = urllib.request.Request(f"{app_url}/health", headers={"User-Agent": "AntiSleep-SelfPing/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                pass
        except Exception:
            pass
        time.sleep(240)

threading.Thread(target=render_anti_sleep, daemon=True).start()


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
CUSTOM_CLIENT_NAME = "اختصاصی کافه دوستی o❤️y"

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
        cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="بررسی لیست کاربران" protocol="5.13" clientname="{CUSTOM_CLIENT_NAME}"\r\n'
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
        cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="پاکسازی کاربر غایب" protocol="5.13" clientname="{CUSTOM_CLIENT_NAME}"\r\n'
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

supervisor_socket = None
supervisor_socket_lock = threading.Lock()

def supervisor_update_account_note(username, note_content):
    global supervisor_socket
    if supervisor_socket:
        try:
            with supervisor_socket_lock:
                update_cmd = f'updateaccount username="{username}" note="{note_content}"\r\n'.encode('utf-8')
                supervisor_socket.sendall(update_cmd)
        except Exception:
            pass

def supervisor_update_radio_note(note_content):
    supervisor_update_account_note("radio kaafehdoosti", note_content)

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
            login_cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="{TT_NAZER_NICKNAME}" protocol="5.13" clientname="{CUSTOM_CLIENT_NAME}"\r\n'
            s.sendall(login_cmd.encode('utf-8'))
            time.sleep(1)
            # پیوستن مستقیم به کانال مدیریت کافه دوستی (chanid=28) با پسورد 12123123
            s.sendall(b'join chanid=28 password="12123123"\r\n')
            
            global supervisor_socket
            with supervisor_socket_lock:
                supervisor_socket = s

            last_ping = time.time()
            last_radio_sync = 0
            last_synced_state_radio = ""
            last_synced_state_nostalgia = ""
            buffer = ""
            global supervisor_radio_userid, supervisor_nostalgia_userid
            supervisor_radio_userid = None
            supervisor_nostalgia_userid = None
            
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
                            uid_m = re.search(r'userid=(\d+)', line)
                            del_uid = int(uid_m.group(1)) if uid_m else -99
                            b = globals().get("global_radio_bot")
                            b_uid = getattr(b, "my_user_id", -99) if b else -99
                            nb = globals().get("global_nostalgia_bot")
                            nb_uid = getattr(nb, "my_user_id", -99) if nb else -99
                            
                            is_radio = False
                            if del_uid > 0 and (del_uid == b_uid or del_uid == supervisor_radio_userid):
                                is_radio = True
                            elif "radio kaafehdoosti" in line:
                                is_radio = True

                            is_nostalgia = False
                            if del_uid > 0 and (del_uid == nb_uid or del_uid == supervisor_nostalgia_userid):
                                is_nostalgia = True
                            elif "nostalgia player" in line:
                                is_nostalgia = True

                            if is_radio:
                                print(f"[Watchdog Event] خروج موقت ربات رادیو (uid={del_uid}) ثبت شد.", flush=True)
                                supervisor_radio_userid = None
                                try:
                                    ensure_radio_worker_alive()
                                except Exception:
                                    pass

                            if is_nostalgia:
                                print(f"[Watchdog Event] خروج موقت نستالژی پلیر (uid={del_uid}) ثبت شد.", flush=True)
                                supervisor_nostalgia_userid = None
                                try:
                                    ensure_nostalgia_worker_alive()
                                except Exception:
                                    pass

                        elif "loggedin" in line or "adduser" in line or "updateuser" in line:
                            u_m = re.search(r'username="([^"]+)"', line)
                            if u_m:
                                u_name = u_m.group(1).strip().lower()
                                update_tt_last_seen(u_name)
                                if "radio kaafehdoosti" in u_name:
                                    uid_m = re.search(r'userid=(\d+)', line)
                                    if uid_m:
                                        supervisor_radio_userid = int(uid_m.group(1))
                                elif "nostalgia player" in u_name:
                                    uid_m = re.search(r'userid=(\d+)', line)
                                    if uid_m:
                                        supervisor_nostalgia_userid = int(uid_m.group(1))

                except socket.timeout:
                    continue
        except Exception as e:
            print(f"خطا در ربات ناظر: {e}. اتصال مجدد ۵ ثانیه دیگر...", flush=True)
        finally:
            with supervisor_socket_lock:
                supervisor_socket = None
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
    url = f"{TELEGRAM_API_BASE}/bot{BOT_TOKEN}/{method}"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
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
    url = f"{TELEGRAM_API_BASE}/bot{BOT_TOKEN}/sendVoice"
    
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
    url = f"{TELEGRAM_API_BASE}/bot{BOT_TOKEN}/sendDocument"
    
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
        
        login_cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="ساخت حساب کاربری" protocol="5.13" clientname="{CUSTOM_CLIENT_NAME}"\r\n'
        s.sendall(login_cmd.encode('utf-8'))
        time.sleep(1)
        resp = s.recv(8192).decode('utf-8', errors='ignore')
        if "accepted" not in resp:
            s.close()
            return False, "عدم پذیرش ورود ادمین ربات به سرور تیم‌تاک"
        
        cmd_new = f'newaccount username="{username}" password="{password}" note="{phone}" usertype=1 userrights={TT_USER_RIGHTS} initchan="/" cmdflood=[30,60000]\r\n'
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
        login_cmd = f'login username="{TT_NAZER_USER}" password="{TT_NAZER_PASS}" nickname="بازیابی رمز کاربر" protocol="5.13" clientname="{CUSTOM_CLIENT_NAME}"\r\n'
        s.sendall(login_cmd.encode('utf-8'))
        time.sleep(1)
        s.recv(8192)
        
        del_cmd = f'delaccount username="{username}"\r\n'
        s.sendall(del_cmd.encode('utf-8'))
        time.sleep(0.5)
        
        cmd_new = f'newaccount username="{username}" password="{password}" note="{phone}" usertype=1 userrights={TT_USER_RIGHTS} initchan="/" cmdflood=[30,60000]\r\n'
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
    if not (os.path.exists(so_path) and os.path.getsize(so_path) > 1000000):
        url = "https://bearware.dk/teamtalk/v5.13/teamtalk-v5.13-ubuntu22-x86_64.tgz"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
            import tarfile, io
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
                found = False
                for m in tar.getmembers():
                    if m.name.endswith("libTeamTalk5.so"):
                        f = tar.extractfile(m)
                        with open(so_path, "wb") as out:
                            out.write(f.read())
                        found = True
                        break
                if not found:
                    return False, "libTeamTalk5.so not found in tar"
        except Exception as e:
            return False, f"Download failed: {e}"

    try:
        if os.path.exists(so_path):
            with open(so_path, "r+b") as f:
                so_data = f.read()
                modified = False
                if b"5.13.0.5114" in so_data:
                    so_data = so_data.replace(b"5.13.0.5114", b"\x00" * 11)
                    modified = True
                p1_old = bytes.fromhex("ba0b000000488d3591e0ef00")
                p1_new = bytes.fromhex("ba00000000488d3591e0ef00")
                if p1_old in so_data:
                    so_data = so_data.replace(p1_old, p1_new)
                    modified = True
                p2_old = bytes.fromhex("ba0b000000488d358c92ea00")
                p2_new = bytes.fromhex("ba00000000488d358c92ea00")
                if p2_old in so_data:
                    so_data = so_data.replace(p2_old, p2_new)
                    modified = True
                if modified:
                    f.seek(0)
                    f.write(so_data)
                    f.truncate()
                    print("[SDK] Successfully patched libTeamTalk5.so to remove version string!", flush=True)
    except Exception as e:
        print(f"[SDK] Patch warning: {e}", flush=True)

    return True, f"Ready libTeamTalk5.so: {os.path.getsize(so_path)} bytes"


# ----------------- بارگذاری SDK تیم‌تاک و راه‌اندازی رادیو کافه دوستی -----------------
ensure_linux_tt_sdk()
base_tt_dir = os.path.dirname(os.path.abspath(__file__))
if base_tt_dir not in sys.path:
    sys.path.insert(0, base_tt_dir)
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())
if sys.platform == "win32":
    if os.path.exists(r"C:\Program Files\TeamTalk5"):
        try:
            os.add_dll_directory(r"C:\Program Files\TeamTalk5")
        except Exception:
            pass
    if os.path.exists(base_tt_dir):
        try:
            os.add_dll_directory(base_tt_dir)
        except Exception:
            pass

try:
    import TeamTalk5
except Exception as e:
    print(f"[Radio] Error importing TeamTalk5: {e}", flush=True)

import os
import sys
import json
import time
import threading
import sqlite3
import ctypes
import re
import urllib.request
import urllib.parse
import urllib.error

SHARED_TT_HOST = "185.26.33.57"
SHARED_TT_PORT = 10333
RADIO_ADMINS = {"omid.o", "yalda", "admin", "kaafehdoostibot", "omid"}

# ----------------- تنظیمات رادیو کافه دوستی (کانال ۲) -----------------
RADIO_TT_HOST = SHARED_TT_HOST
RADIO_TT_PORT = SHARED_TT_PORT
RADIO_TT_USER = "radio kaafehdoosti"
RADIO_TT_PASS = "radio_kaafeh_123456789_doosti"
RADIO_TT_NICK = "radio kaafehdoosti"
RADIO_CHAN_ID = 2

RADIO_TG_TOKEN = _b64.b64decode("ODYwMDA2MzcxMzpBQUd4VTJ4b0VDcTV1MUZqZE9JZ0FBMVBQZEhCU1huWkl0OA==").decode()
RADIO_TG_CHANNEL = "@raaduokaafehdoosti"
RADIO_CACHE_DIR = r"C:\KaafehDoostiBot\music_cache"
RADIO_STATE_FILE = r"C:\KaafehDoostiBot\radio_state.json"
BASE_TRACK_CATALOG = [{'msg_id': 2, 'title': '99883435', 'performer': '<unknown>', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADAmroqpiLI8qLGqrPO-bCwJcjSAABlQACZSEAAmB2CVMe46T0aB1dhT0E'}, {'msg_id': 3, 'title': 'Aroos Shomali', 'performer': 'Ebi Aali @Raz-Music.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADA2roqyZ4roxj2IvKEBbGcCCwquydAAJmIQACYHYJU4QYFZMdM9k7PQQ'}, {'msg_id': 4, 'title': 'Gheyrati', 'performer': 'Savash', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADBGroqyjTixuzEXu3OX8l6C1aCKNTAAJnIQACYHYJU8Bgpm6mPc7sPQQ'}, {'msg_id': 5, 'title': 'Roya', 'performer': 'Savash', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADBWroqykvK_7sU7wFXSJMmXF8oqUbAAJoIQACYHYJU5xAqA1LwD2JPQQ'}, {'msg_id': 6, 'title': 'Joonami ~ TajMusics.com ', 'performer': 'Novan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADBmroqypgBhbLU4m2XvT9WeXMBes0AAJtIQACYHYJU_JMmp8h2jc5PQQ'}, {'msg_id': 7, 'title': 'Refigh موزیکدل', 'performer': 'Milad Rastaad موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADB2roqy3-aub5y4uOtj2J--vWiDV_AAJyIQACYHYJU0u8-R7M0F0dPQQ'}, {'msg_id': 8, 'title': 'Delam Tangete', 'performer': 'Sina Derakhshande', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADCGroqy_1l2YejrGYfmLwjW8SGWCUAAK_GgAC-20BU2ABr3mb7ogPPQQ'}, {'msg_id': 9, 'title': 'Nagam Barat', 'performer': 'Babak Jahanbakhsh', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADCWroqzFfSM-5eYffXaTpkZThtrWvAAL1CQACLJa4UljOAbStJxUHPQQ'}, {'msg_id': 10, 'title': 'Kharabemoon Kard', 'performer': 'Mojtaba Dorbidi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADCmroqzOn6v6hVNb_B8dbC0Wm_c56AAJKCgACTCtQUeEoaJDL-ylUPQQ'}, {'msg_id': 11, 'title': 'Bahooneh', 'performer': 'Mehdi Moghaddam', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADC2roqzQkaNF44FaCdc5whHi4eXICAAK7BwACrINZUWdCLD9YexswPQQ'}, {'msg_id': 12, 'title': 'Man Chi', 'performer': 'Misagh Raad', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADDGroqzZHdZW9-Vqmu85cUcjfyyoRAAKbBwAClYxIUYwgAAExzL-VqD0E'}, {'msg_id': 13, 'title': 'Dametam Garm (Live Version)', 'performer': 'Puzzle Band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADDWroqzcPqSGnTcHYQ71JVW_Ex0-zAAJkBwACMQNYUSXgoQu0Zg4lPQQ'}, {'msg_id': 14, 'title': 'Ashti', 'performer': 'Mohammad Lotfi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADDmroqznZOhil8Xkm6a7AuvcpAwbRAAI4CQACPH5QUZWjM7NbQ6pePQQ'}, {'msg_id': 15, 'title': 'Chatr', 'performer': 'Saman Jalili', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADD2roqzsYzWO91DsoriBWmxXoL5TPAAI1BwACTIfYUA2xbk9EBAj2PQQ'}, {'msg_id': 16, 'title': 'Shab Bekheir', 'performer': 'Kamran Molaei', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADEGroqz29LhCCJifrcUdGsH5CQBtiAAK7IAACb7f5UsuBkYIT8uLOPQQ'}, {'msg_id': 17, 'title': 'To Doost Dashti', 'performer': 'Ali Abdolmaleki', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADEWroqz4eX8nCIMYq2KWN0LYrQzB6AAIUHwACDbkJU82VTcvkPVJfPQQ'}, {'msg_id': 18, 'title': 'Mishe Bargardi Khoone', 'performer': 'Ashvan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADEmroq0DlNX-jKJKl7wrmyNw6vgABuQAC_B8AApOs8FJvsJ6acbhiIj0E'}, {'msg_id': 19, 'title': 'Ma 2 Ta', 'performer': '2Yar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADE2roq0F_kO6Ah9Kbj-aE_RgPC51KAAIKHAAC4IvQUl_sQ13UvAcaPQQ'}, {'msg_id': 20, 'title': '[Be Shab Nareside Chera Deltange Cheshat Shudam] ~[SevilMusic.Com]~', 'performer': '[Shayan Yo]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFGroq0JUxW4VAjAiN6u3tirasXYEAAJJHgACWQEIU6lp5lkqcFnTPQQ'}, {'msg_id': 21, 'title': 'Yadet Nemiyad  | UpTune.ir', 'performer': 'Persian Remix  | آپ تیون', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFWroq0UklSviKSLXfqOX0Plx1AwrAAJKHgACWQEIU2z3T66agi8IPQQ'}, {'msg_id': 22, 'title': '2026_@Remix_song_rap-_I69OrwUBcg.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFmroq0eKcmjrvPsHQfLeZQ9ySCa4AAJLHgACWQEIU9fffYNPEOz7PQQ'}, {'msg_id': 23, 'title': '[Be Shab Nareside Chera Deltange Cheshat Shudam] ~[SevilMusic.Com]~', 'performer': '[Shayan Yo]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFGroq0JUxW4VAjAiN6u3tirasXYEAAJJHgACWQEIU6lp5lkqcFnTPQQ'}, {'msg_id': 24, 'title': 'Yadet Nemiyad  | UpTune.ir', 'performer': 'Persian Remix  | آپ تیون', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFWroq0UklSviKSLXfqOX0Plx1AwrAAJKHgACWQEIU2z3T66agi8IPQQ'}, {'msg_id': 25, 'title': '2026_@Remix_song_rap-_I69OrwUBcg.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFmroq0eKcmjrvPsHQfLeZQ9ySCa4AAJLHgACWQEIU9fffYNPEOz7PQQ'}, {'msg_id': 26, 'title': '[Be Shab Nareside Chera Deltange Cheshat Shudam] ~[SevilMusic.Com]~', 'performer': '[Shayan Yo]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFGroq0JUxW4VAjAiN6u3tirasXYEAAJJHgACWQEIU6lp5lkqcFnTPQQ'}, {'msg_id': 27, 'title': 'Yadet Nemiyad  | UpTune.ir', 'performer': 'Persian Remix  | آپ تیون', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFWroq0UklSviKSLXfqOX0Plx1AwrAAJKHgACWQEIU2z3T66agi8IPQQ'}, {'msg_id': 28, 'title': '2026_@Remix_song_rap-_I69OrwUBcg.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADFmroq0eKcmjrvPsHQfLeZQ9ySCa4AAJLHgACWQEIU9fffYNPEOz7PQQ'}, {'msg_id': 29, 'title': 'Dashi', 'performer': 'Shahin Najafi & Erfan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADHWroq1Mj3eeeY_qWrA39RTk6MXDrAAITIAACj0kJU_NcIkBwG4s2PQQ'}, {'msg_id': 30, 'title': 'Jigar Tala ~ Musics-Fa.Com', 'performer': '2Yar ~ Musics-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADHmroq1Qz5EmRtSVajEGe8HN9YZR3AAIVIAACj0kJU553Tj5nsne5PQQ'}, {'msg_id': 31, 'title': 'Injoori Nemishe', 'performer': 'Ali Montazeri', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADH2roq1esnuTeL8nRzzy7S0hDXcLMAAIYIAACj0kJU4wiwRshhb9VPQQ'}, {'msg_id': 32, 'title': 'Koodeta', 'performer': 'Bijan Yaar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADIGroq1mvT7Dbm37zhyDBawmxCz7aAAIZIAACj0kJUyxP4lr9-zDYPQQ'}, {'msg_id': 33, 'title': 'Haydeh & chavoshi', 'performer': '@MusiceMeee', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADIWroq1uMrp6Xp9TAaqTPqBVjjaJeAAIbIAACj0kJU-J4tFFv11qKPQQ'}, {'msg_id': 34, 'title': 'Siroos Pishghadam Delbar Delbar', 'performer': 'اینستاگرام: soonami_mp3', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADImroq10ij_NPzBXREXYFvWklpH5yAAIcIAACj0kJUxTq8TR2Y1qMPQQ'}, {'msg_id': 35, 'title': 'Majnoonetam ~ UpMusic', 'performer': 'Soheil Mehrzadegan ~ UpMusic', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADI2roq17JNhkEJmcF6pFWIYG1UC8fAAIdIAACj0kJU8eEoWz0SeHOPQQ'}, {'msg_id': 36, 'title': 'Edame Nemidam', 'performer': 'Yousef Zamani', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJGroq2ArqMJR5EvRp3O5WV7LU9XAAAIeIAACj0kJUxUpSMcYrooUPQQ'}, {'msg_id': 37, 'title': 'Amin-Habibi-Bi-Gharar-(New-Version)(Happy-Song.Ir)', 'performer': 'Amin-Habibi-Bi-Gharar-(New-Version)(Happy-Song.Ir)', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJWroq2IGgaCJrPq9hbwp7ZSLMu9nAAIfIAACj0kJU2Anplo2-k7UPQQ'}, {'msg_id': 38, 'title': 'Shaparak', 'performer': 'Ikan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJmroq2RX-j5DmGYHUK3f5p2g9GnHAAIgIAACj0kJUz4sKhMJ4bOiPQQ'}, {'msg_id': 39, 'title': 'Kojaei Alan', 'performer': 'Hossein Montazeri', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADJ2roq2blSglqYCVeDTOVAs5F_uF6AAIiIAACj0kJUxZhMVEo5GQaPQQ'}, {'msg_id': 40, 'title': 'Kabootar', 'performer': 'Sina Parsian @RozMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADKGroq2foQ_YOdOv7ROg2jVOb9BngAAIkIAACj0kJU2EgZF9HYk-uPQQ'}, {'msg_id': 41, 'title': 'Azizi ( ahaang.com )', 'performer': 'Alireza Talischi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADKWroq2lW1w3txL73MAPbmOWOz_yvAAIlIAACj0kJU3UdFAKT7sPFPQQ'}, {'msg_id': 42, 'title': 'Labato Zhel Bezanam topsongs.ir', 'performer': 'topsongs.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADKmroq2vFSYHaQ2oraUOM2zSQJ9BMAAImIAACj0kJU1pUu33Vzk6yPQQ'}, {'msg_id': 43, 'title': 'Phobia', 'performer': 'Armin Zarei @RozMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADK2roq20Jj3NQn6jHXzg6cMD835bkAAIoIAACj0kJU2Dtq5zt2l5RPQQ'}, {'msg_id': 44, 'title': 'Zang Bezani', 'performer': 'Mohsen Ebrahimzadeh', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADLGroq2-_YY25MHIt3NZBe-vgDVwxAAIpIAACj0kJU6DdDsMVp1GmPQQ'}, {'msg_id': 45, 'title': 'Ye Ja To Delet (320).mp3', 'performer': '', 'file_id': 'BQACAgQAAyEFAAMBBZ8iywADLWroq3AaFass7Tbd5PIa_LaTGFZoAAIsIAACj0kJU5pZ7ScIufpcPQQ'}, {'msg_id': 46, 'title': '4 Divari ~ Music-Fa.Com', 'performer': 'Mohammad Moharami ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADLmroq3JletTdICC-6f0Kz2eS0vUAAy4gAAKPSQlTc1oxQ-wJ7kE9BA'}, {'msg_id': 47, 'title': 'Dino Donya موزیکدل', 'performer': 'Ahoora موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADL2roq3SnaBgzJvdgdwTQhVS5RjbnAAIvIAACj0kJU1GwgJZqH453PQQ'}, {'msg_id': 48, 'title': 'Bedon Man Koja Mikhay Beri ~ TajMusics.Com ', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADMGroq3buTjG3OqdzEuiPpCyu7XCxAAIwIAACj0kJU5byF1NshYs9PQQ'}, {'msg_id': 49, 'title': 'Shab Ahangi ~ Music-Fa.Com', 'performer': 'Masoud Sadeghloo ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADMWroq3eEKlm41pe-u5m-9oJkPJe8AAIxIAACj0kJU9bor4EaY0-QPQQ'}, {'msg_id': 50, 'title': 'Mehdi Ahmadvand - Cheshmat (320).mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADMmroq3mxofAL3uxjSsvNUdMBUuewAAI0IAACj0kJU-OTSfEzkXM5PQQ'}, {'msg_id': 51, 'title': 'Sare To [SultanMusic.IR]', 'performer': 'Shayan Yo', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADM2roq3uRE_z2bK8EnezaHeohdjruAAI1IAACj0kJU0wbxy6qN2UKPQQ'}, {'msg_id': 52, 'title': 'Naser Pourkaram - Khabar Nadari.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADNGroq3wNsShkUD82dNaCjU-WX9CLAAI2IAACj0kJU6FWC3ANWxG1PQQ'}, {'msg_id': 53, 'title': '[Bala Mala Ey Tala Tala] ~[SevilMusic.Com]~', 'performer': '[Unknown Artist]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADNWroq34vGPTXzoMjI2FPmxUfTYI0AAI4IAACj0kJU6wliTXwCdh_PQQ'}, {'msg_id': 54, 'title': 'Vay Az Dastet', 'performer': 'Meysam Ebrahimi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADNmroqiuaR-MRpV4omo2Nt1eFWNqYAALCIQACQaDQUkIewAEQCMo4PQQ'}, {'msg_id': 111, 'title': 'Dotayi', 'performer': 'Shahab Ramezan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADb2ri4xHKcPoSYasnXfDQxSOSlFLtAALUHQAC3IewUhu_MU4umVHgPQQ'}, {'msg_id': 112, 'title': 'Harshab Harshab', 'performer': 'Reza Shiri', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADcGri43dQDaGZN3sB3YoRyD511ANxAAJmHgACmCKoUu_LkkKiwFx6PQQ'}, {'msg_id': 113, 'title': 'Gole Hayahoo', 'performer': 'Fereydoun Asraei', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADcWrjKjpIM2F8MHgrUif6M47aOTM3AAKdHAACO5EZU4QUBDGVoz5qPQQ'}, {'msg_id': 114, 'title': 'Sharmande ~ UpMusic', 'performer': 'Majid Kharatha ~ UpMusic', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADcmrjKjpwz-ZqTWO_Cpq0hkf1WxxMAAKcHAACO5EZUwU16bqpBueaPQQ'}, {'msg_id': 115, 'title': 'key', 'performer': 'javan-musics.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADc2rjKjpPWr3H606W6b0i9mHa7KoqAAKeHAACO5EZUyY4eB9PnP8aPQQ'}, {'msg_id': 116, 'title': 'Behesht', 'performer': 'Amir Tataloo', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADdGrjKjqJbHandOqLV2e9adND3fehAAKfHAACO5EZU-B2yFwmrUnrPQQ'}, {'msg_id': 117, 'title': 'Dokhtare Haji (Ft Fedi)', 'performer': 'Talk Down | MusicGraphy.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADdWrjLJyakBso0bLiVV1m8nLf7iU_AAKkHAACO5EZUwd4qF0FzdqIPQQ'}, {'msg_id': 118, 'title': 'Ghaf', 'performer': 'Alireza Talischi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADdmrjLJxoAl9QFNo1e9ekhFn0ez-xAAKlHAACO5EZUy6QtRVTqlrYPQQ'}, {'msg_id': 119, 'title': 'Lalaei ~ Music-Fa.Com', 'performer': 'Ehsan Daryadel ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADd2rjLJyKJ-Pe6UynI5E0M0Jx4Na8AAKmHAACO5EZU003x3si2RYuPQQ'}, {'msg_id': 120, 'title': 'Arosak [SultanMusic.IR]', 'performer': '[SultanMusic.IR]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADeGrjLJycVN7Xj0DCIxwLspvqsRY5AAKpHAACO5EZUxcFYUQaHt3SPQQ'}, {'msg_id': 121, 'title': 'Adamak ', 'performer': 'Amir Khoshnegar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADeWrjLJwzVwyc78HDwZdiLRrMnHviAAKoHAACO5EZU2Hvkf9fAz1rPQQ'}, {'msg_id': 122, 'title': 'Begoo Binam', 'performer': 'Armin Zareei', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADemrjLJxok47Ds_LQ0r81Q03hl--fAAKrHAACO5EZU-vyF_ixWySEPQQ'}, {'msg_id': 123, 'title': 'Nostalgia ( GandomMusic.ir )', 'performer': 'Armin Zarei', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADe2rjLJxucwcYQnDmBbgKRP2sszohAAKsHAACO5EZU90S_jKOBssxPQQ'}, {'msg_id': 124, 'title': 'Sormeh [ موزیک لازم ] ', 'performer': 'Erfan Aren [ Musiclazem.iR ]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADfGrjLJxgythRdBGOe4mbdED6sT_3AAKwHAACO5EZU_ZgEpBH5N-0PQQ'}, {'msg_id': 125, 'title': 'Zire Baroon 2', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADfWrjLJx95KAjOrKQDJYRB6HLne74AAKqHAACO5EZUz-H8d8Gj4E1PQQ'}, {'msg_id': 126, 'title': 'mahe.delam.:MusicsPlus.ir:.', 'performer': 'hoorosh.band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADfmrjLJx4raeVqmgHOHJDnkTaJXhLAAKuHAACO5EZU4cp5RzUEPFePQQ'}, {'msg_id': 127, 'title': 'Delbar Maghror', 'performer': 'Hossein Parsa', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADf2rjLPzS5LftYqJpUC6vnqRi-woDAAKtHAACO5EZU-AwQvyou6nIPQQ'}, {'msg_id': 128, 'title': 'Parishab', 'performer': 'TabaMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADgGrjLPxCJs03Pggkn4jdmlIGmXxDAAKvHAACO5EZU3Bu7r7D02RlPQQ'}, {'msg_id': 129, 'title': 'Gole Shaghayegh', 'performer': 'Mehrad Jam ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADgWrjLPxHvNT-z7Mj_FKcyGySX9srAAK6HAACO5EZU4z94U73Q7XpPQQ'}, {'msg_id': 130, 'title': 'Ki Mese Mane ~ Music-Fa.Com', 'performer': 'Meysam Ebrahimi ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADgmrjLPwlkssJUQ8uLTcDLzQEkaPjAAKxHAACO5EZU3_VsI9r3FGMPQQ'}, {'msg_id': 131, 'title': 'Pantomim ~ Music-Fa.Com', 'performer': 'Mohsen Ebrahimzadeh ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADg2rjLPxBb7SPNFMC3ckDAAHOT0lusgACshwAAjuRGVOUI_Upy-pFwz0E'}, {'msg_id': 132, 'title': 'Ye Lahze [SultanMusic.IR]', 'performer': '[SultanMusic.IR]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADhGrjLPwxs8Tn6oExkiurmD4MpdaHAAKzHAACO5EZUxA1mcsTTZsLPQQ'}, {'msg_id': 133, 'title': 'Hakem 2', 'performer': 'Omid Oghabi | موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADhWrjLPx4ydMhkBfjVRG8r7Vym5k_AAK5HAACO5EZU0McUSA-OdRqPQQ'}, {'msg_id': 134, 'title': 'Eshgh Esmesh Rooshe', 'performer': 'سخاموزیک', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADhmrjLPzsUYbRtm1PIKoFiAMfykQMAAK2HAACO5EZU1erSvUOWRk5PQQ'}, {'msg_id': 135, 'title': '#DjSonami - remix Arash & Masih _ 100 Rishteri -09191278825', 'performer': '@djsonami 09191278825', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADh2rjLPyRNvde3s_RF4WB3_qocWiEAAK3HAACO5EZU9LDjAzXi98GPQQ'}, {'msg_id': 136, 'title': 'Negar', 'performer': 'Reza Bahram ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADiGrjLPyOCc2TZPPy0Qc4HKtdVk_JAAK4HAACO5EZU3ElVlNLsAbPPQQ'}, {'msg_id': 137, 'title': 'Tehran Tokyo ~ [MusicW.IR]', 'performer': '[MusicW.IR]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADiWrjLPx_heRw-cCXfFXWlgUWZbAyAAK7HAACO5EZU0UWoUXueHvwPQQ'}, {'msg_id': 138, 'title': 'Che Pesari [Baritm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADimrjLfd6MaSRgHGz5I6DJyPC82VgAAK_HAACO5EZU0BSd-y4WafLPQQ'}, {'msg_id': 139, 'title': 'Nabashe Ro Dastet', 'performer': 'Satin | PopMelody.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADi2rjLfeTSxOKhEIvGG25rd2x-KchAALDHAACO5EZU3F0Hf0iS4w7PQQ'}, {'msg_id': 140, 'title': '1a to-kio-1(silamusic.ir).mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADjGrjLfeTZBGz2f44ZAzQ1OeJ4uNZAALAHAACO5EZU_uq3tCBOjkKPQQ'}, {'msg_id': 141, 'title': 'Tak Khal ', 'performer': 'X Band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADjWrjLfdXPbKb2GWeHEDqLImMzo0VAALBHAACO5EZU4ixAVIZKSzUPQQ'}, {'msg_id': 142, 'title': 'Masalan ~ Music-Fa.Com', 'performer': 'Zanco ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADjmrjLfcr6tqWhhD6Wc4g9WzapqMoAALCHAACO5EZUxXFaILSeML_PQQ'}, {'msg_id': 143, 'title': 'Bemoon Vasam [Baritm.Com]', 'performer': 'Ali Parsa', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADj2rjLfeJbJAC35UDSIeKLXxXOBYEAALGHAACO5EZUy5VqzzRn-onPQQ'}, {'msg_id': 144, 'title': 'Gole Man ~ Music-Fa.Com', 'performer': 'Amir Rashvand ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADkGrjLfcmKsUxHBSiB26OqxdVPu5BAALJHAACO5EZU0eEwkI3dnVEPQQ'}, {'msg_id': 145, 'title': 'Asabi ', 'performer': 'Amir Khoshnegar Ft Omid Motlagh', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADkWrjLfeHgMJyhFMgAdY9ixfAWvYWAALHHAACO5EZU2R59N1C6kisPQQ'}, {'msg_id': 146, 'title': 'Chete [BaRitm.Com]', 'performer': 'Armin 2AFM', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADkmrjLfdMvzmjCuZ4KHCoSDQwkes0AALIHAACO5EZU9BzIbSCkF3PPQQ'}, {'msg_id': 147, 'title': 'Khandehato Ghorbon ~ Music-Fa.Com', 'performer': 'Aron Afshar ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADk2rjLfeUii-CUWUJwz0ShHtlCjhgAALKHAACO5EZU9TE3rjPIdyYPQQ'}, {'msg_id': 148, 'title': 'Maryam', 'performer': 'Artin Shahvaran - Download1Music.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADlGrjLjYKjrtCx29iX8QHlM5j5DqVAALLHAACO5EZU5cEvl1r9XXiPQQ'}, {'msg_id': 149, 'title': 'Payatam Man(www.Next1.ir)', 'performer': 'Asef Aria', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADlWrjLjb427w9rZYBgjIttov3IAeVAALMHAACO5EZU_wFhvsYe9aMPQQ'}, {'msg_id': 150, 'title': '1b Alireza Talischi Ay Dele Khodam (320).mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADlmrjLjZ88i6SjiPPC3FCTyrir40TAALNHAACO5EZU97BMrUizLb7PQQ'}, {'msg_id': 151, 'title': 'Aroome Jonam ', 'performer': 'Amir Khoshnegar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADl2rjLjaWUD0N_36EWf6-K9NpReeFAALOHAACO5EZU13nD6tQwEbmPQQ'}, {'msg_id': 152, 'title': 'Ensiye', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADmGrjLjYHLdE7F2nxPgJz9A1TBWd1AALPHAACO5EZU6wspiHTq8muPQQ'}, {'msg_id': 153, 'title': 'Ashegham Kardi', 'performer': 'Hoorosh Band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADmWrjLjbces9rH0zyoSaUfL7r2dRMAALQHAACO5EZUxSB6hHi_fqNPQQ'}, {'msg_id': 154, 'title': 'Shiko Pik', 'performer': 'Mehrad Jam ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADmmrjLjYopC5jC6cqDiV5_Dj9PklaAALRHAACO5EZU4mtuzjQZLBUPQQ'}, {'msg_id': 155, 'title': 'Hakem', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADm2rjLjbAsJvOjHrcZJO3GUZtIOH6AALSHAACO5EZUzfJyHD3hnBpPQQ'}, {'msg_id': 156, 'title': 'Age Khakam', 'performer': 'RozMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADnGrjLjYxB3G7VgH5T3VKqob-1n7GAALUHAACO5EZU1J6g4_iLe10PQQ'}, {'msg_id': 157, 'title': 'Kash', 'performer': 'Reza Bahram ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADnWrjLjZ1lhLYWOTlP6rxYrsB1YBbAALTHAACO5EZU-95X6BR-I2QPQQ'}, {'msg_id': 158, 'title': 'Delamo Bordi', 'performer': 'Mehrad Jam ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADnmrjLtjRb5xwbtprrV5DvS8RluZfAALbHAACO5EZU_cqb6s9l4ZiPQQ'}, {'msg_id': 159, 'title': 'Cheshmoon Siah ', 'performer': 'Satin', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADn2rjLtib7hmVUpZYT1BWVNEWBRc-AALZHAACO5EZU4BMysVT3IFZPQQ'}, {'msg_id': 160, 'title': 'Ba Delbari V Bi Delbari ', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADoGrjLtiA2GOvfKejvjPSnd8ycuTBAALaHAACO5EZU1eHEDWzKoGXPQQ'}, {'msg_id': 161, 'title': 'Aghaye Ghazi ~ Music-Fa.Com', 'performer': 'Bardia ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADoWrjLtgCr41XGhZJmxWc4QSMjGJeAALcHAACO5EZUz52j0XxujV1PQQ'}, {'msg_id': 162, 'title': 'Motebaher ~ Music-Fa.Com', 'performer': 'Bardia ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADomrjLtgAAcWqrpp3hSSuGpUt-K0fWAAC3xwAAjuRGVOwBQH5IZn6KD0E'}, {'msg_id': 163, 'title': 'Ghafas ', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADo2rjLtiKF_oS6T47AAE6i7W1E2VBzAAC3RwAAjuRGVMi2D4pvmJxzz0E'}, {'msg_id': 164, 'title': 'Daste Dele Man Roo Shode ', 'performer': 'Satin', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADpGrjLtg_nrawC28sqmPrhNdDlB2oAALgHAACO5EZU8vAE4YTcNm7PQQ'}, {'msg_id': 165, 'title': 'Tagh Taagh', 'performer': 'Rashan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADpWrjLtiguwIAAduLC6mR2N-PhUjzQgAC4RwAAjuRGVPaM2VDr-b0hT0E'}, {'msg_id': 166, 'title': 'Dige Barnagard ', 'performer': 'Amir Khoshnegar', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADpmrjLth4Q4P1pkpC7WajG2bE9BpEAALiHAACO5EZU-XqpUWdvBdfPQQ'}, {'msg_id': 167, 'title': 'Tarafdarame ~ Music-Fa.Com', 'performer': 'Armin Zarei ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADp2rjLtg2DE588sU3OjrbCNElw_jIAALjHAACO5EZU2TJ7pPfmcDqPQQ'}, {'msg_id': 168, 'title': 'Mah Pishooni', 'performer': 'Hoorosh Band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADqGrjLxWHXnd40HldWzWioZ4biJdaAALkHAACO5EZU8AUVdSxXiNsPQQ'}, {'msg_id': 169, 'title': 'DiDi', 'performer': 'Mehraad Jam', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADqWrjLxUF2C4mRBBzUEyhZaSzxIrGAALlHAACO5EZUzzcxEY1220CPQQ'}, {'msg_id': 170, 'title': 'Zaraban ', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADqmrjLxV57xdTB2DR-giWA6ZzQ-CKAALmHAACO5EZU4wby1buDhMOPQQ'}, {'msg_id': 171, 'title': 'Gole Eshgh [Baritm.Com]', 'performer': 'Reza Bahram', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADq2rjLxVGq3pTDaSRTD3EZLfiQh1NAALnHAACO5EZU61-fha2TjIQPQQ'}, {'msg_id': 172, 'title': 'Doctor', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADrGrjLxVPGFjezLrIlq43GUCsjnNTAALoHAACO5EZU3xCitSjIfQdPQQ'}, {'msg_id': 173, 'title': 'Dokhtare Khejalati Remix', 'performer': 'MusiceMan.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADrWrjLxXNIj3Vwzmp5WNpXlc5ZBi5AALpHAACO5EZU-VH2CHyUJvTPQQ'}, {'msg_id': 174, 'title': 'Bottle', 'performer': 'Talk Down & Fedi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADrmrjLxUvtpNVEi4E7Od4KlkFU8-AAALqHAACO5EZU7AVEtMaGj5yPQQ'}, {'msg_id': 175, 'title': 'Ghorbonet Besham', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADr2rjLxULB2YPKv7YCs31OwpNYdhTAALrHAACO5EZU50k-r9wT1stPQQ'}, {'msg_id': 176, 'title': 'Mohsen-Ebrahimzadeh-Hanoozam-Remix', 'performer': '[ blogmusic.ir ]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADsGrjMAwtFzftmIk256_oWlPaezBoAALsHAACO5EZU9sFijlqs-FfPQQ'}, {'msg_id': 177, 'title': 'Nazre Cheshat', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADsWrjMAxX_RQ5bKHTX3U6LTFDzxmzAALtHAACO5EZU114E7p5_eo9PQQ'}, {'msg_id': 178, 'title': 'Saaghiya [BaRitm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADsmrjMAz0wg8xYqJ5N8OHE58tG1vFAALuHAACO5EZU2MjcQ9qFpQiPQQ'}, {'msg_id': 179, 'title': 'Toonesti Eshgham ', 'performer': 'Satin', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADs2rjMAxf2HNyclgRb3Q68_qMc33tAALwHAACO5EZUxz0yzRyOfCkPQQ'}, {'msg_id': 180, 'title': 'Koochamoon ~ Music-Fa.Com', 'performer': 'Ehsan Daryadel ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADtGrjMAxV0Mx1coPGnKh7D2QaoGJ7AALyHAACO5EZU7QhIARpB8J0PQQ'}, {'msg_id': 181, 'title': 'Delam Mikhad', 'performer': 'Emo Band | موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADtWrjMAyuha4My_XZuG2b2JFRuw3vAALzHAACO5EZU1SHzLizSwNTPQQ'}, {'msg_id': 182, 'title': 'Robabe', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADtmrjMAzr0evWdLMOx_vqQyhZrGl2AAL0HAACO5EZU2v6YsqAf19kPQQ'}, {'msg_id': 183, 'title': 'Ghamet Nabashe', 'performer': 'Mehrad Jam ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADt2rjMAyYkrtlpafM2Q6O0x8DqGRjAAL1HAACO5EZU8jJNshLuCr8PQQ'}, {'msg_id': 184, 'title': 'Shah Delam', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADuGrjMAw7RaQmj4ifCmh5H2TZ1UsuAAL3HAACO5EZU4KAhvRPxv2bPQQ'}, {'msg_id': 185, 'title': 'Noosh [BaRitm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADuWrjMAyYJElfGdN99f3TMBzAp-37AAL4HAACO5EZU9ryobOpbY8ZPQQ'}, {'msg_id': 186, 'title': 'Delbare Khosh Maharat ~ Musico.IR', 'performer': 'Farzad Farokh ~ Musico.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADumrjMA1l3_ME-Z4erXOsk7tT83uRAAL2HAACO5EZU-ha_B0-6LLDPQQ'}, {'msg_id': 187, 'title': 'Jazab  ~ UpMusic', 'performer': 'Farzad Farzin ~ UpMusic', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADu2rjMA2dvMc601rpdFvUp7KGl9NdAAL5HAACO5EZU7Vk50hcfFC5PQQ'}, {'msg_id': 188, 'title': 'Mohsen-Ebrahimzadeh-Hanoozam-Remix', 'performer': '[ blogmusic.ir ]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADsGrjMAwtFzftmIk256_oWlPaezBoAALsHAACO5EZU9sFijlqs-FfPQQ'}, {'msg_id': 189, 'title': 'Nazre Cheshat', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADsWrjMAxX_RQ5bKHTX3U6LTFDzxmzAALtHAACO5EZU114E7p5_eo9PQQ'}, {'msg_id': 190, 'title': 'Saaghiya [BaRitm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADsmrjMAz0wg8xYqJ5N8OHE58tG1vFAALuHAACO5EZU2MjcQ9qFpQiPQQ'}, {'msg_id': 191, 'title': 'Toonesti Eshgham ', 'performer': 'Satin', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADs2rjMAxf2HNyclgRb3Q68_qMc33tAALwHAACO5EZUxz0yzRyOfCkPQQ'}, {'msg_id': 192, 'title': 'Koochamoon ~ Music-Fa.Com', 'performer': 'Ehsan Daryadel ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADtGrjMAxV0Mx1coPGnKh7D2QaoGJ7AALyHAACO5EZU7QhIARpB8J0PQQ'}, {'msg_id': 193, 'title': 'Delam Mikhad', 'performer': 'Emo Band | موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADtWrjMAyuha4My_XZuG2b2JFRuw3vAALzHAACO5EZU1SHzLizSwNTPQQ'}, {'msg_id': 194, 'title': 'Robabe', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADtmrjMAzr0evWdLMOx_vqQyhZrGl2AAL0HAACO5EZU2v6YsqAf19kPQQ'}, {'msg_id': 195, 'title': 'Ghamet Nabashe', 'performer': 'Mehrad Jam ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADt2rjMAyYkrtlpafM2Q6O0x8DqGRjAAL1HAACO5EZU8jJNshLuCr8PQQ'}, {'msg_id': 196, 'title': 'Shah Delam', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADuGrjMAw7RaQmj4ifCmh5H2TZ1UsuAAL3HAACO5EZU4KAhvRPxv2bPQQ'}, {'msg_id': 197, 'title': 'Noosh [BaRitm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADuWrjMAyYJElfGdN99f3TMBzAp-37AAL4HAACO5EZU9ryobOpbY8ZPQQ'}, {'msg_id': 198, 'title': 'Delbare Khosh Maharat ~ Musico.IR', 'performer': 'Farzad Farokh ~ Musico.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADumrjMA1l3_ME-Z4erXOsk7tT83uRAAL2HAACO5EZU-ha_B0-6LLDPQQ'}, {'msg_id': 199, 'title': 'Jazab  ~ UpMusic', 'performer': 'Farzad Farzin ~ UpMusic', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADu2rjMA2dvMc601rpdFvUp7KGl9NdAAL5HAACO5EZU7Vk50hcfFC5PQQ'}, {'msg_id': 200, 'title': '1khalvatidashtam.mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADyGrjMEhA6nj_K8N941DnUvOC8AdNAAL6HAACO5EZUyfkIIHvVRmhPQQ'}, {'msg_id': 201, 'title': 'Del', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADyWrjMEi-bVs7MvqRIH8D9CCS3BbiAAL7HAACO5EZUyihr438gEdxPQQ'}, {'msg_id': 202, 'title': 'Gentleman [Baritm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADymrjMEiZ1TqmRp095fwWKpU1FmIEAAL8HAACO5EZU3v-5Nd_QSgpPQQ'}, {'msg_id': 203, 'title': 'Aziz joon ', 'performer': 'Satin', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADy2rjMEieKwJDDWJMDmEtFYkh1Lz9AAL9HAACO5EZUxbZvTV5WFMKPQQ'}, {'msg_id': 204, 'title': 'Golpari Joon', 'performer': 'Dj AlirezA', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADzGrjMEjBFAl-pg5NOvEBF8K9XlsVAAL-HAACO5EZU_1mGpXtTHO8PQQ'}, {'msg_id': 205, 'title': 'Leyli - MusicDel.ir', 'performer': 'Omid Oghabi | موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADzWrjMEh-QCe1qnEGd_0FuivVjyyQAAL_HAACO5EZU5-OW5uP_GGWPQQ'}, {'msg_id': 206, 'title': 'WwW.IRahang.IR ایران آهنگ.دانلود آهنگ شاد عروسی', 'performer': 'WwW.IRahang.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADzmrjMEiSAuDXfT6QM_W9RAr7G3mAAAMdAAI7kRlTQeGGFYhs-bg9BA'}, {'msg_id': 207, 'title': 'Ta abad(mostafa momeni) (MusicsFarsi.com)', 'performer': 'musicsfarsi.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywADz2rjMEgVBAkO0eQ8PEla57Vo0xN-AAIBHQACO5EZU3hvlFbV5ml5PQQ'}, {'msg_id': 208, 'title': 'Khosham Miad', 'performer': 'Hamid Hiraad ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD0GrjMEg875LplhXOZArDscZn4rBIAAICHQACO5EZUyybZ7rWwULDPQQ'}, {'msg_id': 209, 'title': 'Mesle Man Bash', 'performer': 'Hoorosh Band', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD0WrjMEgWHUd3M6O5VAft5oleMc2UAAIDHQACO5EZU7ibbzwD0yLWPQQ'}, {'msg_id': 210, 'title': 'Shomal', 'performer': 'Omid Oghabi', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD0mrjMFFmsOcsUFWGKhqCMN_dDBIKAAIEHQACO5EZUyV4Dh25jQdFPQQ'}, {'msg_id': 211, 'title': 'Harfet Harfe Mane', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD02rjMFHXJRsWWwY-lQvveKT7zsFtAAIFHQACO5EZUy5VmYHTm8aVPQQ'}, {'msg_id': 212, 'title': 'Khalegh', 'performer': 'Dj AlirezA', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD1GrjMHv4qGeMn2lZZT4v1yIPSGc-AAIHHQACO5EZU4LSsVClrJiSPQQ'}, {'msg_id': 213, 'title': 'Rotab Rotab', 'performer': 'Hamed Pahlan', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD1WrjMHuqovOCdut5V51H9bxQknsfAAIGHQACO5EZU-_E5PBiKeHYPQQ'}, {'msg_id': 214, 'title': 'Shakhe Nabat ~ Music-Fa.Com', 'performer': 'Masih And Arash ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD1mrjMHtsREjoniIZeJmWSAUuYxI-AAIJHQACO5EZUyLMbC7zi5J3PQQ'}, {'msg_id': 215, 'title': 'zade baroon(Shahreahang.com)', 'performer': 'masoud sadeghloo', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD12rjMHse65P-7EWcqqGZwm-WwUTVAAIIHQACO5EZU1W9U5hwjVm5PQQ'}, {'msg_id': 216, 'title': 'Shomal', 'performer': 'Mehrad Jam ::Alvandmusic::', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD2GrjMHv_4b1tx-tEmLIr4F_ZmFeaAAIKHQACO5EZU9BDZ2xNEddePQQ'}, {'msg_id': 217, 'title': 'Aslan Mage Mishe ~ Music-Fa.Com', 'performer': 'Mehrzad Amirkhani ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD2WrjMJj5mnD73Cpx_O0DihOFgC0HAAILHQACO5EZUzu8VCKinrhOPQQ'}, {'msg_id': 218, 'title': 'Salamati', 'performer': 'Meysam Ebrahimi | Bia4Music', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD2mrjMJgwERXCFLCSsLIz86NncI1RAAIMHQACO5EZU0UW2yWqb-HwPQQ'}, {'msg_id': 219, 'title': '1Mohsen Yeganeh - Sokoot( 320).mp3', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD22rjMJhvRgZ4lq8P1DJwZQPMzMfMAAINHQACO5EZU4xOnKUhi2tKPQQ'}, {'msg_id': 220, 'title': 'Almas ', 'performer': 'Mohsen Aghakhani', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD3GrjMJgNalmEX2yqbo8RdTGVdjmOAAIOHQACO5EZU4UPJyzVYUEZPQQ'}, {'msg_id': 221, 'title': 'Moo Chatri', 'performer': 'Edvin', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD3WrjMJg5Ec3eRtC34ssTl1lhUHLkAAIPHQACO5EZU0O_MadlZEqtPQQ'}, {'msg_id': 222, 'title': 'Dele Ashegh ~ UpMusic', 'performer': 'Morteza Ashrafi ~ UpMusic', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD3mrjMJiHG6hopoE2kC3n1eDntT_hAAIQHQACO5EZU3S5jamTIQ8RPQQ'}, {'msg_id': 227, 'title': 'Naze Shastam', 'performer': 'Armin 2AFM', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD32rjMKjqCugJAoCsbmSHyCM-S5EXAAIRHQACO5EZU76MX1JZbx-KPQQ'}, {'msg_id': 228, 'title': 'Allah', 'performer': 'Omid Oghabi | موزیکدل', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD4GrjMKgUkQABi76E0otsk9CsM03YEgACEh0AAjuRGVO_98c2rUFwED0E'}, {'msg_id': 229, 'title': 'Nazre Cheshat ~ Music-Fa.Com', 'performer': 'Omid Oghabi ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD4WrjMKiKI3Z2ioAVyXKnRSzGyyitAAITHQACO5EZU2fB76TAavwXPQQ'}, {'msg_id': 230, 'title': 'Ghayegh ~ Music-Fa.Com', 'performer': 'Pirbod ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD4mrjMKhfq6OL96FbdOvs8pNI4cayAAIUHQACO5EZU1hiHVdtZuiMPQQ'}, {'msg_id': 231, 'title': 'Remix Aref Gole Goldoone Man', 'performer': 'DJ ALIREZA عارف گل گلدونه ریمیکس', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD52rjMPMNrYXHy5du-zktldn0MzFQAAIWHQACO5EZU8W2nC3mpXg1PQQ'}, {'msg_id': 232, 'title': 'To Palange Mani ~ Music-Fa.Com', 'performer': 'Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD6GrjMPNzJiKIXykBzOC6GWP-IO7IAAIXHQACO5EZUwgt6u0T9pXpPQQ'}, {'msg_id': 233, 'title': 'Eshgho Gonah', 'performer': 'Reza Bahram', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD6WrjMUHO8JsP1prus81FxNTk1kOZAAIYHQACO5EZU5fY34fUbxpsPQQ'}, {'msg_id': 234, 'title': 'asghar-agha', 'performer': 'musicgoogle.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD6mrjMUGdMqOSrKy7zTI0sUMqTL6hAAIZHQACO5EZU_wKMJd8pFwFPQQ'}, {'msg_id': 235, 'title': 'Ostad [BaRitm.Com]', 'performer': 'Sasy', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD62rjMUG6I1VscDyWH2dmEiEJfK8CAAIaHQACO5EZU13BR06nxBV7PQQ'}, {'msg_id': 236, 'title': 'Deldar [Baritm.Com]', 'performer': 'Sina Derakhshande', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD7GrjMUHGHuBg316eFFo3KYouOWvnAAIbHQACO5EZU0h3WLEGfD2KPQQ'}, {'msg_id': 237, 'title': 'Tala FaFaMusic.ir', 'performer': '', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD7WrjMUHs7XTyCJVg0eIJ3hiegJQrAAIcHQACO5EZU8N-cm4HfHp6PQQ'}, {'msg_id': 238, 'title': 'Delbar Remix [SultanMusic.IR]', 'performer': '[SultanMusic.IR]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD7mrjMUE2GBYtBS-dghvoDqkozFm_AAIdHQACO5EZU7X69N7QzIimPQQ'}, {'msg_id': 239, 'title': 'Azabam Nade (Ft Milad Kiani) [BaRitm.Com]', 'performer': 'Alishmas', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD72rjMUGUZoaj3NpaUg_JGwlbRrA6AAIeHQACO5EZUwNiUEpXpdDUPQQ'}, {'msg_id': 240, 'title': 'Marge eshgh (MusicsFarsi.com)', 'performer': 'musicsfarsi.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD8GrjMWhB9u2x5X13vUW1hPkGsimRAAIfHQACO5EZU0pMjC1DakXvPQQ'}, {'msg_id': 241, 'title': 'mehdi_saadati_hanooz_baramazizi', 'performer': '..:: beratomusic.ir ::..', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD8WrjMWjz_jz3Be5EenYC7TFtogpvAAIgHQACO5EZU6ahdA2D-fSQPQQ'}, {'msg_id': 242, 'title': 'Shomare Jadidam ~ Music-Fa.Com', 'performer': 'Armin Zarei ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD8mrjMo6dNsyC-uNCVwJoa3OCKZ9qAAIhHQACO5EZUxsqcAX06KX6PQQ'}, {'msg_id': 243, 'title': 'ریمیکس من دلم تنگه یه زنگته', 'performer': 'کانال تلگرام SHOTI_ORG@', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD82rjMo5UKQJWKUwvWpty4iGXuvljAAIiHQACO5EZUx7qFTFU8MMTPQQ'}, {'msg_id': 244, 'title': 'Behtar Az Mane ~ Music-Fa.Com', 'performer': 'Ali Yasini ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD9GrjMo4t2xgWiFQOc4CzxpPw7_sGAAIjHQACO5EZUxjZaisjFbTBPQQ'}, {'msg_id': 245, 'title': 'Bamaze ', 'performer': 'Amin Ara Ft Amirhossein Farahmand', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD9WrjMo63PwR4RbfJqF1sbHIF4irVAAIkHQACO5EZU0X55d9tBKeLPQQ'}, {'msg_id': 246, 'title': 'Espand Dood Konam ~ Musico.IR', 'performer': 'Artin Gharibi ~ Musico.IR', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD9mrjMo6QYLwuvkEokC4HFfg8fdj7AAIlHQACO5EZUzUo4cOMZRLQPQQ'}, {'msg_id': 247, 'title': 'Naz Nakon NazNakon_(www.NewSong.ir)', 'performer': 'Kouros_(wWw.NewSong.ir)', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD92rjMo6tRKQ1MvnAHiS0ce02H15iAAImHQACO5EZUwABv_YPgyyn1T0E'}, {'msg_id': 248, 'title': 'Leili [SultanMusic.IR]', 'performer': '[SultanMusic.IR]', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD-GrjMo67LWXsa4qjrE9RkRVM3juDAAInHQACO5EZU_QT6Y5cl8BYPQQ'}, {'msg_id': 249, 'title': 'Chale Roo Goonat ~ Music-Fa.Com', 'performer': 'Shahin Banan ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD-WrjMo4IRPGwH_CZmSI6b7si4NMBAAIoHQACO5EZU7XNdaRqZ67GPQQ'}, {'msg_id': 250, 'title': 'Gol Pari Joonam ~ Music-Fa.Com', 'performer': 'Morteza Javan ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD-mrjMo5epFcIAAGnFC6nUBmlxYB0EwACKR0AAjuRGVN0WDpWESA2cT0E'}, {'msg_id': 251, 'title': 'New Face ', 'performer': 'Behroz Sektor', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD-2rjMo5SU4NvZEwwy40fUU_vZcU-AAIqHQACO5EZU4LVxSeuS8pOPQQ'}, {'msg_id': 252, 'title': 'Chips (Remix)~GuitarMusic', 'performer': 'Donya', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD_GrjMvfb_e215c2kZMLma8ir5yrAAAIrHQACO5EZU_rCHDkEkUflPQQ'}, {'msg_id': 253, 'title': 'Shab Ke Shod', 'performer': 'Hamid Hiraad', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD_WrjMvd1Ve3aj2it2vmCfhjm7JZYAAIsHQACO5EZUyCkAwhvJxxEPQQ'}, {'msg_id': 254, 'title': 'Giso-Kamand-AI', 'performer': 'Mahasti', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD_mrjM75SzoA_SVUWa4XSljP6oLjuAAItHQACO5EZU7ZTppyoUxo2PQQ'}, {'msg_id': 255, 'title': 'Bitab', 'performer': 'Hamid Hiraad', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywAD_2rjM76mmPkYdebpxt77YPyHY1fKAAIuHQACO5EZU_YEk0ybYlrHPQQ'}, {'msg_id': 256, 'title': 'Dafi Surprise (Ft Fedi)', 'performer': 'Talk Down | Roadmusic.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQABauMzvlKpsdveKPE6fVUVYp2Zbp0AAi8dAAI7kRlT70rtlUL2DMs9BA'}, {'msg_id': 257, 'title': 'Che Konam (Ahangha.Net)', 'performer': 'Arash', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQFq4zO-iTsZ85M1DfhUSKEPpO92zQACMB0AAjuRGVORmvxcemJlCT0E'}, {'msg_id': 258, 'title': 'Leyla ~ Music-Fa.Com', 'performer': 'Eljan ~ Music-Fa.Com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQJq4zQ_-ZArnyBHX8xqreUKzJoXqgACMR0AAjuRGVN-zjW3iT-CXD0E'}, {'msg_id': 259, 'title': 'Bottle', 'performer': 'Talk Down & Fedi | Roadmusic.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQNq4zQ_EL1-dS_mqMLubCQcHBhtDAACNB0AAjuRGVMQ3GJKilbhZT0E'}, {'msg_id': 260, 'title': 'Delamo Bordi', 'performer': 'Dj AlirezA', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQRq4zQ_kX--DA72dG03xyZLDb90ZgACMx0AAjuRGVPKzKXnKa8gUj0E'}, {'msg_id': 261, 'title': 'Ey Vay', 'performer': 'Dj AlirezA', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQVq4zSOlCm0AvfiZgt46_8QGcc-SwACNR0AAjuRGVMaR_UQ6Gv5aT0E'}, {'msg_id': 262, 'title': 'Yar', 'performer': 'Hamid Hiraad', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQZq4zSO5P8ygnr1SGJBRnHKDU8B-wACMh0AAjuRGVMNtlthgIO8LT0E'}, {'msg_id': 263, 'title': 'Cappuccino', 'performer': 'Mehraad Jam', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQdq4zSOz4RAP3aAPCUSqDM0vqcjXQACNh0AAjuRGVPVOvIwbi4b4D0E'}, {'msg_id': 264, 'title': 'Nazanin Naz Nakon', 'performer': 'Dj AlirezA', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQhq4zSO-d3snfLntLem6QAB81UtZ70AAjcdAAI7kRlT9Hci4F8bnZg9BA'}, {'msg_id': 265, 'title': 'Mashooghe', 'performer': 'Hamid Hiraad', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQlq4zSOYP-a6Khm5a4iTvqA_s28AwACOB0AAjuRGVPsXygAAWiuPXU9BA'}, {'msg_id': 266, 'title': 'Remix Kalmast – Shabe Yalda -Apmusic.ir', 'performer': 'Remix Kalmast – Shabe Yalda -Apmusic.ir', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQpq4zSOnpA2R_PigT__yQMxYYn-JwACOR0AAjuRGVMizQi45XQXAT0E'}, {'msg_id': 267, 'title': 'Tannaz [BaRitm.Com]', 'performer': 'Saeed Shayesteh', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQtq4zSO55KmA_-KrCaZTEKHXhQ1_gACOh0AAjuRGVMW4iXG57Oe0T0E'}, {'msg_id': 268, 'title': 'Khaste Shodam', 'performer': 'Hamid Hiraad @RozMusic.com', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQxq5HQkarGqbMYFbSzdDXcbK19dnAAC9R0AAjuRIVPJfQOqDCX2VD0E'}, {'msg_id': 270, 'title': 'Nafaset Ki Bod (Ai)', 'performer': 'Babak Jahanbakhsh Ft Ali Abdolmaleki', 'file_id': 'CQACAgQAAyEFAAMBBZ8iywACAQ5q5rH_I_oViWBTVnjjTe_eYDwKzgACYhwAAkLlMFPw_fWN3m88Tj0E'}]

# ----------------- تنظیمات نستالژی پلیر (کانال ۵ - آلاچیق) -----------------
NOSTALGIA_TT_HOST = SHARED_TT_HOST
NOSTALGIA_TT_PORT = SHARED_TT_PORT
NOSTALGIA_TT_USER = "nostalgia player"
NOSTALGIA_TT_PASS = "nostalgia_kaafeh_123456789_doosti"
NOSTALGIA_TT_NICK = "nostalgia player"
NOSTALGIA_CHAN_ID = 5

NOSTALGIA_TG_TOKEN = _b64.b64decode("OTA0OTQ2ODA2ODpBQUhKX2Y1UlJLTHlTOHJNdllCS1VxVlZwRWJVcVNJU1E4bw==").decode()
NOSTALGIA_TG_CHANNEL = "@kaafehdoostinostaaljik"
NOSTALGIA_CACHE_DIR = r"C:\KaafehDoostiBot\music_cache_nostalgia"
NOSTALGIA_STATE_FILE = r"C:\KaafehDoostiBot\nostalgia_state.json"
NOSTALGIA_TRACK_CATALOG = [
  {
    "msg_id": 2,
    "title": "Asir",
    "performer": "Mahasti - GahMusic.com",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADAmrj6F619-IbE7GvTO5TZVYEXLadAALXHwACtnggU7ki4TRYY3-tPQQ"
  },
  {
    "msg_id": 3,
    "title": "1 abbas-ghaderii - 1 - 128 - .mp3",
    "performer": "Abbas Ghaderi - Musicmehr.com",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADA2rj6F5mc7xdkcJ2alNMg25FyvrrAALYHwACtnggU9MYp2C4qkKxPQQ"
  },
  {
    "msg_id": 4,
    "title": "Aghasi - GahMusic.com",
    "performer": "",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADBGrj6F7Fyn0W8ZS_V4sNA-sgS-Q4AALcHwACtnggU5nv9eZ5axrBPQQ"
  },
  {
    "msg_id": 5,
    "title": "Bargeh Barandeh~MelonMusic.ir",
    "performer": "Davood Behboodi",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADBWrj6F49KVFr1xQvcIhSoh-RyZhQAALdHwACtnggUy2TJNcAAbn8tj0E"
  },
  {
    "msg_id": 6,
    "title": "Sabzeh Keshmir",
    "performer": "Fataneh",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADBmrj6F48OAQRpsnqODouElsR4S7uAALeHwACtnggU2gUC4H194FcPQQ"
  },
  {
    "msg_id": 7,
    "title": "Nemiyad~MelonMusic.ir",
    "performer": "Googoosh",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADB2rj6F5mZLH2R4-vbXJ_QdUgp3Y6AALbHwACtnggUyg1F5Dhh5AwPQQ"
  },
  {
    "msg_id": 8,
    "title": "Bandari",
    "performer": "Habib",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADCGrj6F7pP0y_eaYzE5SJQm7RsStjAALfHwACtnggU5s7DAMYnnvnPQQ"
  },
  {
    "msg_id": 9,
    "title": "The Medley",
    "performer": "Hassan Shamaizadeh",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADCWrj6F76VKglB_XRGzjBbzO08iqrAALhHwACtnggU2uexfFZXNgiPQQ"
  },
  {
    "msg_id": 10,
    "title": "Vafayeh Del",
    "performer": "GahMusic.com",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADCmrj6F6OZW-Mu3k5bsWTrTo8Ats5AALgHwACtnggU2NtsLkJMG6zPQQ"
  },
  {
    "msg_id": 11,
    "title": "Alame Ashgh",
    "performer": "Homayra",
    "file_id": "CQACAgQAAyEFAAMBBf7lXgADC2rj6F7S3wiGSoC__fUP5gABlZHoywAC4h8AArZ4IFOfbnlybEChmD0E"
  }
]

os.makedirs(RADIO_CACHE_DIR, exist_ok=True)
os.makedirs(NOSTALGIA_CACHE_DIR, exist_ok=True)

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
        print(f"[Config] save_persistent_config err: {e}", flush=True)

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
        print(f"[Config] load_persistent_config err: {e}", flush=True)
    return default


class VoicePlayer:
    def __init__(self, bot):
        self.bot = bot
        self.stop_event = threading.Event()
        self.thread = None
        self.sample_rate = 48000
        self.channels = 2
        self.current_pos = 0
        self.worker_id = 0

    def play(self, track_path, start_sec=0.0):
        self.stop()
        self.stop_event.clear()
        self.worker_id += 1
        current_id = self.worker_id
        self.bot.is_streaming = True
        self.thread = threading.Thread(target=self._play_worker, args=(track_path, start_sec, current_id), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive() and self.thread != threading.current_thread():
            self.thread.join(timeout=1.0)
        try:
            self.bot.insertAudioBlock(None)
        except Exception:
            pass
        self.bot.is_streaming = False

    def _play_worker(self, track_path, start_sec=0.0, worker_id=0):
        log_p = getattr(self.bot, "log_prefix", "Radio")
        try:
            if self.stop_event.is_set() or worker_id != self.worker_id:
                return

            self.channels = 2
            self.sample_rate = 48000

            raw_pcm = None
            try:
                import miniaudio
                with open(track_path, "rb") as f_track:
                    f_bytes = f_track.read()
                decoded = miniaudio.decode(
                    f_bytes,
                    output_format=miniaudio.SampleFormat.SIGNED16,
                    nchannels=self.channels,
                    sample_rate=self.sample_rate
                )
                raw_pcm = decoded.samples.tobytes()
                del decoded
                del f_bytes
                import gc
                gc.collect()
            except Exception as e_mini:
                print(f"[{log_p}] miniaudio decode error for {track_path}: {e_mini}", flush=True)

            if self.stop_event.is_set() or worker_id != self.worker_id:
                return

            samples_per_frame = 1920
            chunk_size = samples_per_frame * self.channels * 2  # 7680 bytes
            min_chunk = chunk_size

            if not raw_pcm or len(raw_pcm) < min_chunk:
                print(f"[{log_p}] Microphone Voice: Could not decode {os.path.basename(track_path)} to PCM. Skipping to next...", flush=True)
                time.sleep(1)
                if not self.stop_event.is_set() and worker_id == self.worker_id:
                    self.bot.play_next()
                return

            total_len = len(raw_pcm)
            bytes_per_sec = self.sample_rate * self.channels * 2  # 192,000 bytes/sec
            start_pos = int(start_sec * bytes_per_sec)
            start_pos = (start_pos // chunk_size) * chunk_size
            if 0 < start_pos < total_len - (chunk_size * 25):
                pos = start_pos
                print(f"[{log_p}] Resuming playback of {os.path.basename(track_path)} from {start_sec:.1f}s (byte {pos}/{total_len})", flush=True)
            else:
                pos = 0
                start_sec = 0.0

            sample_index = 0
            self.current_pos = pos

            self.bot.is_streaming = True
            sec_now = pos / bytes_per_sec
            self.bot.current_playback_sec = sec_now
            self.bot.resume_pos_sec = sec_now
            self.bot.update_player_title()

            buf_type = ctypes.c_byte * chunk_size
            raw_buf = buf_type()

            ab = TeamTalk5.AudioBlock()
            ab.nStreamID = worker_id
            ab.nSampleRate = self.sample_rate
            ab.nChannels = self.channels
            ab.nSamples = samples_per_frame
            ab.uStreamTypes = TeamTalk5.StreamType.STREAMTYPE_VOICE
            ab.lpRawAudio = ctypes.cast(raw_buf, ctypes.c_void_p)
            ab.uSampleIndex = 0

            chunks_since_save = 0
            chunks_since_disk_save = 0
            track_duration_sec = total_len / bytes_per_sec

            clock_start = time.perf_counter()
            frame_idx = 0
            frame_duration = samples_per_frame / float(self.sample_rate)  # 0.040s

            print(f"[{log_p}] Microphone voice transmission started: {os.path.basename(track_path)} ({track_duration_sec:.1f}s)", flush=True)

            while pos < total_len and not self.stop_event.is_set() and worker_id == self.worker_id:
                chunk = raw_pcm[pos:pos + chunk_size]
                pos += len(chunk)
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

                ctypes.memmove(raw_buf, chunk, chunk_size)
                self.bot.insertAudioBlock(ab)

                chunks_since_save += 1
                if chunks_since_save >= 25:
                    chunks_since_save = 0
                    sec = pos / bytes_per_sec
                    self.bot.current_playback_sec = sec
                    self.bot.resume_pos_sec = sec

                chunks_since_disk_save += 1
                if chunks_since_disk_save >= 750:
                    chunks_since_disk_save = 0
                    threading.Thread(target=self.bot.persist_state, daemon=True).start()

                if (time.perf_counter() - clock_start) > (track_duration_sec + 20):
                    print(f"[{log_p}] Track duration watchdog reached ({track_duration_sec:.1f}s). Advancing...", flush=True)
                    break

                frame_idx += 1
                target_time = clock_start + (frame_idx * frame_duration)
                now = time.perf_counter()
                sleep_sec = target_time - now
                if sleep_sec > 0.001:
                    time.sleep(sleep_sec)
                elif sleep_sec < -0.2:
                    clock_start = time.perf_counter()
                    frame_idx = 0

            try:
                self.bot.insertAudioBlock(None)
            except Exception:
                pass

            if self.stop_event.is_set():
                if worker_id == self.worker_id:
                    if pos > (start_pos + chunk_size * 25):
                        sec = pos / bytes_per_sec
                        self.bot.current_playback_sec = sec
                        self.bot.resume_pos_sec = sec
                        self.bot.persist_state()
                        print(f"[{log_p}] Playback paused at {sec:.1f}s - position preserved.", flush=True)
                    else:
                        print(f"[{log_p}] Playback stopped before start threshold. Position {self.bot.resume_pos_sec:.1f}s", flush=True)
            else:
                if worker_id == self.worker_id:
                    print(f"[{log_p}] Track finished naturally via Microphone. Playing next track...", flush=True)
                    self.bot.current_playback_sec = 0.0
                    self.bot.resume_pos_sec = 0.0
                    self.bot.persist_state()
                    self.bot.is_streaming = False
                    self.bot.last_track_finish_at = time.time()
                    threading.Thread(target=self.bot.play_next, daemon=True).start()

        except Exception as e:
            print(f"[{log_p}] Microphone Voice playback exception: {e}", flush=True)
            try:
                self.bot.insertAudioBlock(None)
            except Exception:
                pass
            if not self.stop_event.is_set() and worker_id == self.worker_id:
                time.sleep(1)
                threading.Thread(target=self.bot.play_next, daemon=True).start()
        finally:
            raw_pcm = None
            raw_buf = None
            chunk = None
            import gc
            gc.collect()


class BaseMusicBot(TeamTalk5.TeamTalk if 'TeamTalk5' in globals() else object):
    def __init__(self, bot_type="radio", chan_id=2, tt_user="", tt_pass="", tt_nick="",
                 tg_token="", tg_channel="", cache_dir="", state_file="",
                 config_prefix="radio", initial_catalog=None, log_prefix="Radio",
                 display_name="رادیو کافه دوستی", admins=None):
        super().__init__()
        self.bot_type = bot_type
        self.chan_id = chan_id
        self.tt_user = tt_user
        self.tt_pass = tt_pass
        self.tt_nick = tt_nick
        self.tg_token = tg_token
        self.tg_channel = tg_channel
        self.cache_dir = cache_dir
        self.state_file = state_file
        self.config_prefix = config_prefix
        self.initial_catalog = initial_catalog or []
        self.log_prefix = log_prefix
        self.display_name = display_name
        self.admins = admins or RADIO_ADMINS

        self.connected = False
        self.logged_in = False
        self.joined = False
        self.my_user_id = 0

        # Pre-populate playlist immediately from initial catalog
        self.playlist = []
        for item in self.initial_catalog:
            mid = item.get("msg_id", 0)
            fid = item.get("file_id")
            title = item.get("title") or f"track_{mid}"
            performer = item.get("performer") or ""
            clean_title = "".join(c for c in title if c.isalnum() or c in " ._-()").strip()
            if not clean_title.endswith(".mp3"):
                clean_title += ".mp3"
            dest_filename = f"{mid}_{clean_title}"
            dest_path = os.path.join(self.cache_dir, dest_filename)
            display_name_track = f"{performer} - {title}".strip(" -")
            self.playlist.append({
                "msg_id": mid,
                "title": display_name_track,
                "path": dest_path,
                "file_id": fid
            })

        saved = self.load_saved_state()
        self.volume_percent = saved.get("volume_percent", 25)
        self.title_hidden = saved.get("title_hidden", False)
        self.last_track_name = saved.get("last_track_name", "")
        self.last_track_file = saved.get("last_track_file", "")
        self.saved_current_index = saved.get("current_index", 0)
        self.current_index = self.saved_current_index
        self.current_playback_sec = saved.get("playback_pos_sec", 0.0)
        self.resume_pos_sec = self.current_playback_sec
        self.created_at = time.time()
        self.last_connected_at = 0
        self.last_track_finish_at = 0
        self.last_server_packet_time = time.time()
        self._last_ping_time = time.time()

        self.is_streaming = False
        self.current_track = None
        self.last_update_id = 0
        self.restart_requested = False
        self.lock = threading.RLock()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.diag = []
        self.voice_player = VoicePlayer(self)
        self.syncing_catalog = False
        self.play_lock = threading.Lock()
        self._is_starting_playback = False
        self.restore_track_index()

    def load_saved_state(self):
        # Check prefixed key first, fallback to non-prefixed for backward compatibility
        db_vol = load_persistent_config(f"{self.config_prefix}_volume_percent", None)
        if db_vol is None and self.config_prefix == "radio":
            db_vol = load_persistent_config("volume_percent", None)
        saved_vol = 25
        if db_vol is not None:
            try:
                saved_vol = int(db_vol)
            except Exception:
                pass

        db_pos = load_persistent_config(f"{self.config_prefix}_playback_pos_sec", None)
        if db_pos is None and self.config_prefix == "radio":
            db_pos = load_persistent_config("playback_pos_sec", None)
        pos_sec = 0.0
        if db_pos is not None:
            try:
                pos_sec = float(db_pos)
            except Exception:
                pass

        db_idx = load_persistent_config(f"{self.config_prefix}_current_index", None)
        if db_idx is None and self.config_prefix == "radio":
            db_idx = load_persistent_config("current_index", None)
        cur_idx = 0
        if db_idx is not None:
            try:
                cur_idx = int(db_idx)
            except Exception:
                pass

        db_track = load_persistent_config(f"{self.config_prefix}_last_track_name", "") or ""
        if not db_track and self.config_prefix == "radio":
            db_track = load_persistent_config("last_track_name", "") or ""

        db_file = load_persistent_config(f"{self.config_prefix}_last_track_file", "") or ""
        if not db_file and self.config_prefix == "radio":
            db_file = load_persistent_config("last_track_file", "") or ""

        defaults = {
            "volume_percent": saved_vol,
            "title_hidden": False,
            "last_track_name": db_track,
            "last_track_file": db_file,
            "current_index": cur_idx,
            "playback_pos_sec": pos_sec
        }
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    defaults.update(data)
                    if "volume_percent" in data:
                        saved_vol = data["volume_percent"]
            except Exception as e:
                print(f"[{self.log_prefix}] Load state err: {e}", flush=True)
        print(f"[{self.log_prefix}] Loaded persistent state: {defaults}", flush=True)
        return defaults

    def persist_state(self):
        try:
            if getattr(self, "is_streaming", False) and hasattr(self, "voice_player") and getattr(self.voice_player, "current_pos", 0) > 0:
                cur_sec = self.voice_player.current_pos / (self.voice_player.sample_rate * self.voice_player.channels * 2)
                self.current_playback_sec = cur_sec
                self.resume_pos_sec = cur_sec
            else:
                cur_sec = getattr(self, "resume_pos_sec", getattr(self, "current_playback_sec", 0.0))

            vol = getattr(self, "volume_percent", 25)
            t_name = self.current_track.get("title", "") if self.current_track else getattr(self, "last_track_name", "")
            t_file = os.path.basename(self.current_track.get("path", "")) if self.current_track else getattr(self, "last_track_file", "")

            state = {
                "volume_percent": vol,
                "title_hidden": self.title_hidden,
                "current_index": self.current_index,
                "last_track_name": t_name,
                "last_track_file": t_file,
                "playback_pos_sec": round(cur_sec, 2)
            }
            self.last_track_name = t_name
            self.last_track_file = t_file

            save_persistent_config(f"{self.config_prefix}_volume_percent", vol)
            save_persistent_config(f"{self.config_prefix}_current_index", self.current_index)
            save_persistent_config(f"{self.config_prefix}_playback_pos_sec", round(cur_sec, 2))
            save_persistent_config(f"{self.config_prefix}_last_track_name", t_name)
            save_persistent_config(f"{self.config_prefix}_last_track_file", t_file)

            if self.config_prefix == "radio":
                global SAVED_RADIO_VOLUME
                SAVED_RADIO_VOLUME = vol
                save_persistent_config("volume_percent", vol)
                save_persistent_config("current_index", self.current_index)
                save_persistent_config("playback_pos_sec", round(cur_sec, 2))
                save_persistent_config("last_track_name", t_name)
                save_persistent_config("last_track_file", t_file)

            try:
                tmp_path = self.state_file + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
                    f.flush()
                if os.path.exists(tmp_path):
                    os.replace(tmp_path, self.state_file)
            except Exception as e:
                print(f"[{self.log_prefix}] Save state file err: {e}", flush=True)

        except Exception as e:
            print(f"[{self.log_prefix}] persist_state err: {e}", flush=True)

    def restore_track_index(self):
        with self.lock:
            if not self.playlist:
                return
            if getattr(self, "is_streaming", False) and getattr(self, "current_track", None):
                for idx, t in enumerate(self.playlist):
                    if t.get("path") == self.current_track.get("path"):
                        self.current_index = idx
                        return

            target_file = getattr(self, "last_track_file", "")
            if target_file:
                for idx, t in enumerate(self.playlist):
                    if os.path.basename(t.get("path", "")) == target_file:
                        self.current_index = idx
                        print(f"[{self.log_prefix}] Restored track by filename to index {idx}: {target_file}", flush=True)
                        return

            target_name = getattr(self, "last_track_name", "")
            if target_name:
                for idx, t in enumerate(self.playlist):
                    if t.get("title") == target_name:
                        self.current_index = idx
                        print(f"[{self.log_prefix}] Restored track by title to index {idx}: {target_name}", flush=True)
                        return

                def norm(s):
                    return re.sub(r'[^a-zA-Z0-9\u0600-\u06FF]', '', str(s).lower())

                nt = norm(target_name)
                if nt:
                    for idx, t in enumerate(self.playlist):
                        if nt in norm(t.get("title", "")) or norm(t.get("title", "")) in nt:
                            self.current_index = idx
                            print(f"[{self.log_prefix}] Restored track by normalized match to index {idx}: {t.get('title')}", flush=True)
                            return

            saved_idx = getattr(self, "saved_current_index", 0)
            if 0 <= saved_idx < len(self.playlist):
                self.current_index = saved_idx
                print(f"[{self.log_prefix}] Restored track to saved index {self.current_index}", flush=True)

    def apply_current_volume(self):
        try:
            percent = getattr(self, "volume_percent", 25)
            gain = int(max(0, min(150, percent)) / 100.0 * 1000)
            if hasattr(self, "_tt") and self._tt:
                TeamTalk5._SetSoundInputGainLevel(self._tt, gain)
            print(f"[{self.log_prefix}] apply_current_volume: {percent}% (gain: {gain})", flush=True)
            self.diag.append(f"VOL_SET:{percent}:{gain}")
        except Exception as e:
            print(f"[{self.log_prefix}] apply_current_volume err: {e}", flush=True)

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
        url = f"{TELEGRAM_API_BASE}/bot{self.tg_token}/{method}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print(f"[{self.log_prefix}] TG API {method} error: {e}", flush=True)
            return {}

    def download_tg_file(self, file_id, dest_path):
        try:
            finfo = self.tg_api("getFile", {"file_id": file_id})
            if not finfo.get("ok"):
                self.diag.append("GF_FAIL")
                return False
            file_path = finfo["result"]["file_path"]
            download_url = f"{TELEGRAM_API_BASE}/file/bot{self.tg_token}/{file_path}"
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            tmp_dest = dest_path + ".tmp"
            import shutil
            with self.opener.open(req, timeout=60) as resp, open(tmp_dest, "wb") as f:
                shutil.copyfileobj(resp, f)
            if os.path.exists(tmp_dest) and os.path.getsize(tmp_dest) > 1000:
                os.replace(tmp_dest, dest_path)
                self.diag.append(f"DL_OK:{os.path.basename(dest_path)[:8]}")
                return True
            return False
        except Exception as e:
            print(f"[{self.log_prefix}] Download error: {e}", flush=True)
            self.diag.append(f"DL_ERR:{type(e).__name__}")
            return False

    def sync_telegram_playlist(self):
        # 1. Pre-download the next track first so track transitions are instantaneous
        try:
            with self.lock:
                next_i = self.get_next_track_index() if self.playlist else 0
                next_t = self.playlist[next_i] if self.playlist else None
            if next_t and next_t.get("file_id"):
                n_path = next_t.get("path")
                if not os.path.exists(n_path) or os.path.getsize(n_path) == 0:
                    self.download_tg_file(next_t["file_id"], n_path)
        except Exception as e:
            print(f"[{self.log_prefix}] Next track prefetch err: {e}", flush=True)

        # 2. Prune old cache to keep disk and memory minimal (max 4 files)
        try:
            if os.path.exists(self.cache_dir):
                files = [os.path.join(self.cache_dir, f) for f in os.listdir(self.cache_dir) if f.endswith(".mp3")]
                if False and len(files) > 4:
                    files.sort(key=lambda x: os.path.getmtime(x))
                    protected = set()
                    with self.lock:
                        if self.playlist and 0 <= self.current_index < len(self.playlist):
                            p_curr = self.playlist[self.current_index].get("path", "")
                            if p_curr: protected.add(os.path.abspath(p_curr))
                        next_i = self.get_next_track_index() if self.playlist else 0
                        if self.playlist and 0 <= next_i < len(self.playlist):
                            p_next = self.playlist[next_i].get("path", "")
                            if p_next: protected.add(os.path.abspath(p_next))
                    for old_f in files[:-4]:
                        if os.path.abspath(old_f) not in protected:
                            try:
                                os.remove(old_f)
                                print(f"[{self.log_prefix}] Pruned old cache file: {os.path.basename(old_f)}", flush=True)
                            except Exception:
                                pass
        except Exception as e_prune:
            print(f"[{self.log_prefix}] Cache prune error: {e_prune}", flush=True)

        # 3. Check getUpdates for any brand new tracks posted by users
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
                dest_path = os.path.join(self.cache_dir, dest_filename)
                display_name_track = f"{performer} - {title}".strip(" -")
                track_info = {"msg_id": cp["message_id"], "title": display_name_track, "path": dest_path, "file_id": file_id}

                with self.lock:
                    if not any(x["path"] == dest_path for x in self.playlist):
                        self.playlist.append(track_info)
                        added_any = True

                if not os.path.exists(dest_path) or os.path.getsize(dest_path) == 0:
                    self.download_tg_file(file_id, dest_path)

            if max_uid > 0:
                self.tg_api("getUpdates", {"offset": max_uid + 1})

            if added_any and self.joined:
                self.update_player_title()
        except Exception as e:
            print(f"[{self.log_prefix}] getUpdates poll err: {e}", flush=True)

        try:
            self.load_existing_cache()
        except Exception:
            pass

        if self.joined and not getattr(self, "is_streaming", False) and self.playlist:
            threading.Thread(target=self.auto_start_playback, daemon=True).start()

    def load_existing_cache(self):
        if not os.path.exists(self.cache_dir):
            return
        files = sorted(os.listdir(self.cache_dir))
        for fname in files:
            if fname.lower().endswith((".mp3", ".m4a", ".ogg", ".wav")):
                path = os.path.join(self.cache_dir, fname)
                title = os.path.splitext(fname)[0]
                if "_" in title:
                    title = title.split("_", 1)[1]
                with self.lock:
                    if not any(t["path"] == path for t in self.playlist):
                        self.playlist.append({
                            "title": title,
                            "path": path
                        })
        print(f"[{self.log_prefix}] Loaded {len(self.playlist)} tracks from cache.", flush=True)
        if len(self.playlist) >= len(self.initial_catalog):
            self.syncing_catalog = False
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

        print(f"[{self.log_prefix}] Updating player title: {status_text}", flush=True)
        try:
            self.doChangeStatus(0, status_text)
            self.diag.append(f"TITLE:{'HIDDEN' if getattr(self, 'title_hidden', False) else curr_title[:8]}")
        except Exception as e:
            print(f"[{self.log_prefix}] doChangeStatus error: {e}", flush=True)

    def send_chat(self, text):
        if not self.joined:
            return
        try:
            msgs = TeamTalk5.buildTextMessage(text, TeamTalk5.TextMsgType.MSGTYPE_CHANNEL, nChannelID=self.chan_id)
            for m in msgs:
                self.doTextMessage(m)
        except Exception as e:
            print(f"[{self.log_prefix}] send_chat error: {e}", flush=True)

    def auto_start_playback(self):
        vp_alive = bool(hasattr(self, "voice_player") and self.voice_player.thread and self.voice_player.thread.is_alive())
        with self.play_lock:
            if getattr(self, "is_streaming", False) or getattr(self, "_is_starting_playback", False) or vp_alive:
                return
            self._is_starting_playback = True

        try:
            self.cleanup_old_channel_files()
            self.restore_track_index()
            self.update_player_title()
            vp_alive = bool(hasattr(self, "voice_player") and self.voice_player.thread and self.voice_player.thread.is_alive())
            if self.playlist and not getattr(self, "is_streaming", False) and not vp_alive:
                start_at = getattr(self, "resume_pos_sec", 0.0)
                print(f"[{self.log_prefix}] Auto-starting playback from saved position: {start_at:.1f}s", flush=True)
                self.play_track(self.current_index, start_sec=start_at)
        finally:
            with self.play_lock:
                self._is_starting_playback = False

    def play_track(self, index, start_sec=None):
        self.stop_all_playback()
        time.sleep(0.15)

        with self.lock:
            if not self.playlist:
                return
            new_idx = index % len(self.playlist)
            self.current_index = new_idx
            track = self.playlist[self.current_index]
            self.current_track = track
            self.current_playback_sec = 0.0
            self.resume_pos_sec = 0.0
            self.persist_state()

        track_path = track.get("path")
        file_id = track.get("file_id")
        if not os.path.exists(track_path) or os.path.getsize(track_path) == 0:
            if file_id:
                print(f"[{self.log_prefix}] Downloading active track on-demand: {track['title']}", flush=True)
                self.diag.append(f"DL_START:{track.get('msg_id', 0)}")
                try:
                    self.download_track_sync(track, timeout=120)
                except Exception as e_dl:
                    print(f"[{self.log_prefix}] On-demand download failed: {e_dl}", flush=True)
                    self.diag.append(f"DL_ERR:{e_dl}")
                    time.sleep(2)
                    self.play_next()
                    return

        if not os.path.exists(track_path):
            print(f"[{self.log_prefix}] Track file missing: {track_path}. Skipping...", flush=True)
            self.play_next()
            return

        try:
            my_id = self.getMyUserID()
            u = self.getUser(my_id)
            if not u or u.nChannelID != self.chan_id:
                print(f"[{self.log_prefix}] Ensuring channel {self.chan_id} (currently {getattr(u, 'nChannelID', None)})...", flush=True)
                self.doJoinChannelByID(self.chan_id, "")
                for _ in range(15):
                    self.runEventLoop(50)
                    u = self.getUser(my_id)
                    if u and u.nChannelID == self.chan_id:
                        break
                    time.sleep(0.04)
        except Exception as e_ch:
            print(f"[{self.log_prefix}] Channel verify err: {e_ch}", flush=True)

        print(f"[{self.log_prefix}] Playing [{self.current_index + 1}/{len(self.playlist)}] via Microphone: {track['title']}", flush=True)
        self.voice_player.play(track_path, start_sec=start_sec or 0.0)
        self.is_streaming = True
        self.update_player_title()

    def stop_all_playback(self):
        try:
            self.voice_player.stop()
        except Exception:
            pass
        self.is_streaming = False

    def stream_media_file_fallback(self, track_path):
        pass

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
        percent = max(0, min(150, percent))
        self.volume_percent = percent
        save_persistent_config(f"{self.config_prefix}_volume_percent", percent)
        if self.config_prefix == "radio":
            global SAVED_RADIO_VOLUME
            SAVED_RADIO_VOLUME = percent
            save_persistent_config("volume_percent", percent)
        self.persist_state()
        self.apply_current_volume()

        msg = f"🔊 بلندی صدای {self.display_name} روی {percent}٪ تنظیم شد و به صورت دائم ذخیره گردید."
        if admin_name:
            msg += f" (توسط {admin_name})"
        self.send_chat(msg)

    def schedule_file_auto_delete(self, chan_id, file_id, file_name, delay_sec=240):
        def _delete_worker():
            print(f"[{self.log_prefix}] Auto-delete countdown started: '{file_name}' (ID: {file_id}) will be deleted in {delay_sec}s", flush=True)
            time.sleep(delay_sec)
            try:
                print(f"[{self.log_prefix}] Deleting expired file '{file_name}' (ID: {file_id})...", flush=True)
                self.doDeleteFile(chan_id, file_id)
                self.send_chat(f"🗑 فایل موقت «{file_name}» پس از پایان مهلت ۴ دقیقه‌ای دانلود، با موفقیت از روم پاکسازی شد.")
            except Exception as e:
                print(f"[{self.log_prefix}] doDeleteFile error: {e}", flush=True)
        threading.Thread(target=_delete_worker, daemon=True).start()

    def cleanup_old_channel_files(self):
        try:
            files = self.getChannelFiles(self.chan_id)
            for rf in files:
                owner = TeamTalk5.ttstr(rf.szUsername).strip()
                if owner in [self.tt_user, self.tt_nick, ""] or not owner:
                    fid = rf.nFileID
                    fname = TeamTalk5.ttstr(rf.szFileName)
                    print(f"[{self.log_prefix}] Auto-cleaning stale file on join: {fname} (ID {fid})", flush=True)
                    self.doDeleteFile(self.chan_id, fid)
        except Exception as e:
            print(f"[{self.log_prefix}] cleanup_old_channel_files error: {e}", flush=True)

    def upload_current_to_channel(self, requester_name):
        if not self.current_track or not os.path.exists(self.current_track["path"]):
            self.send_chat("❌ در حال حاضر آهنگی در حال پخش نیست.")
            return
        track = self.current_track
        try:
            print(f"[{self.log_prefix}] Uploading {track['path']} to room for {requester_name}...", flush=True)
            self.send_chat(f"⏳ در حال آپلود فایل «{track['title']}» در بخش فایل‌های روم برای {requester_name} (مهلت دانلود: ۴ دقیقه)...")
            self.doSendFile(self.chan_id, track["path"])
        except Exception as e:
            print(f"[{self.log_prefix}] doSendFile error: {e}", flush=True)
            self.send_chat(f"❌ خطا در قرار دادن فایل آهنگ: {e}")

    def onCmdError(self, nSource, clienterrormsg):
        self.last_server_packet_time = time.time()
        try:
            n_err = getattr(clienterrormsg, "nErrorNo", getattr(clienterrormsg, "nError", 0))
            err_msg = TeamTalk5.ttstr(clienterrormsg.szErrorMsg)
            self.diag.append(f"CMD_ERR:{nSource}:{n_err}:{err_msg}")
            print(f"[{self.log_prefix}] CMD ERROR (src {nSource}): {n_err} - {err_msg}", flush=True)
            if "already in channel" in err_msg.lower() or n_err == 1016:
                self.joined = True
        except Exception as e:
            print(f"[{self.log_prefix}] onCmdError handler err: {e}", flush=True)

    def onCmdSuccess(self, nSource):
        self.last_server_packet_time = time.time()
        self.diag.append(f"CMD_OK:{nSource}")
        print(f"[{self.log_prefix}] CMD SUCCESS (src {nSource})", flush=True)

    def onCmdProcessing(self, nSource, bCompleted):
        self.last_server_packet_time = time.time()

    def onConnectSuccess(self):
        self.diag.append("CON_SUCCESS")
        print(f"[{self.log_prefix}] Connected to TeamTalk server!", flush=True)
        self.connected = True
        self.last_connected_at = time.time()
        cmd_id = self.doLogin(self.tt_nick, self.tt_user, self.tt_pass, CUSTOM_CLIENT_NAME)
        self.diag.append(f"LOGIN_CMD:{cmd_id}")

    def onConnectFailed(self):
        self.diag.append("CON_FAILED")
        print(f"[{self.log_prefix}] Connect failed! Recreating instance...", flush=True)
        self.connected = False
        self.persist_state()
        self.restart_requested = True

    def onConnectionLost(self):
        self.diag.append("CON_LOST")
        print(f"[{self.log_prefix}] Connection lost! Preserving playback position and recreating instance...", flush=True)
        self.persist_state()
        self.connected = False
        self.logged_in = False
        self.joined = False
        self.is_streaming = False
        self.restart_requested = True

    def onCmdMyselfLoggedIn(self, my_id, user_account):
        self.diag.append(f"LOGGED_IN:{my_id}")
        print(f"[{self.log_prefix}] Logged in! MyID: {my_id}", flush=True)
        self.logged_in = True
        self.my_user_id = my_id
        self.apply_current_volume()
        self.doChangeNickname(self.tt_nick)
        try:
            self.initSoundInputDevice(1978)
            print(f"[{self.log_prefix}] Virtual Sound Device 1978 initialized!", flush=True)
        except Exception as e_snd:
            print(f"[{self.log_prefix}] Sound init err: {e_snd}", flush=True)

        try:
            if user_account and hasattr(user_account, "szNote"):
                note_str = TeamTalk5.ttstr(user_account.szNote).strip()
                if note_str.startswith("STATE:"):
                    parts = dict(kv.split("=", 1) for kv in note_str[6:].split(";") if "=" in kv)
                    s_pos = float(parts.get("POS", 0.0))
                    s_trk = parts.get("TRK", "")
                    s_idx = int(parts.get("IDX", -1))
                    if getattr(self, "resume_pos_sec", 0.0) <= 0.0 and s_pos > 0.0:
                        self.resume_pos_sec = s_pos
                        self.current_playback_sec = s_pos
                        if s_idx >= 0:
                            self.current_index = s_idx
                        if s_trk:
                            self.last_track_file = s_trk
                        print(f"[{self.log_prefix}] Restored cold-start state from account note: pos={s_pos:.1f}s, trk={s_trk}", flush=True)
        except Exception as e:
            print(f"[{self.log_prefix}] Account note restore err: {e}", flush=True)

        my_chan = 0
        try:
            u = self.getUser(my_id)
            if u:
                my_chan = u.nChannelID
        except Exception:
            pass

        if my_chan == self.chan_id:
            print(f"[{self.log_prefix}] Already in destination channel {self.chan_id} via initchan!", flush=True)
            self.joined = True
            threading.Thread(target=self.auto_start_playback, daemon=True).start()
        else:
            res = self.doJoinChannelByID(self.chan_id, "")
            self.diag.append(f"JOIN_CMD:{res}")

    def onCmdUserJoinedChannel(self, user):
        my_id = getattr(self, "my_user_id", self.getMyUserID())
        self.diag.append(f"JOIN:{user.nUserID}:{user.nChannelID}")
        if user.nUserID == my_id:
            if user.nChannelID == self.chan_id:
                print(f"[{self.log_prefix}] Joined destination channel {user.nChannelID} successfully!", flush=True)
                self.joined = True
                self.apply_current_volume()
                threading.Thread(target=self.auto_start_playback, daemon=True).start()
            else:
                print(f"[{self.log_prefix} Self-Guard] جابجایی به کانال {user.nChannelID}. بازگشت خودکار به کانال {self.chan_id}...", flush=True)
                self.joined = False
                self.doJoinChannelByID(self.chan_id, "")

    def onCmdMyselfKickedFromChannel(self, nSource, user):
        print(f"[{self.log_prefix}] Bot left or kicked. Preserving position and rejoining immediately...", flush=True)
        self.joined = False
        try:
            self.persist_state()
        except Exception:
            pass
        self.doJoinChannelByID(self.chan_id, "")

    def onStreamMediaFile(self, mediafileinfo):
        pass

    def onCmdFileNew(self, remotefile):
        if remotefile.nChannelID == self.chan_id:
            fname = TeamTalk5.ttstr(remotefile.szFileName)
            owner = TeamTalk5.ttstr(remotefile.szUsername).strip()
            fid = remotefile.nFileID
            chid = remotefile.nChannelID
            print(f"[{self.log_prefix}] File ready in room: {fname} (ID {fid}, Owner: {owner})", flush=True)
            if owner in [self.tt_user, self.tt_nick, ""] or not owner:
                self.send_chat(f"✅ فایل «{fname}» در بخش فایل‌های روم قرار گرفت. این فایل به مدت ۴ دقیقه برای دانلود در دسترس است و پس از آن خودکار حذف خواهد شد.")
                self.schedule_file_auto_delete(chid, fid, fname, delay_sec=240)
            else:
                self.send_chat(f"✅ فایل «{fname}» در بخش فایل‌های روم قرار گرفت.")

    def onCmdUserTextMessage(self, textmessage):
        sender = TeamTalk5.ttstr(textmessage.szFromUsername).strip()
        sender_lower = sender.lower()
        msg_text = TeamTalk5.ttstr(textmessage.szMessage).strip().lower()

        print(f"[{self.log_prefix}] Chat from [{sender}]: {msg_text}", flush=True)

        if msg_text in ["dl", "دانلود"]:
            threading.Thread(target=self.upload_current_to_channel, args=(sender,), daemon=True).start()
            return

        is_admin = (sender_lower in self.admins)
        if not is_admin:
            try:
                user = self.getUser(textmessage.nFromUserID)
                if user and (getattr(user, "uUserType", 0) & 3 != 0):
                    is_admin = True
                elif hasattr(self, "_tt") and self._tt:
                    is_admin = bool(TeamTalk5._IsChannelOperator(self._tt, self.chan_id, textmessage.nFromUserID))
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
                    f"📋 راهنمای دستورات {self.display_name}:\n"
                    "• دستور dl یا دانلود: قرار دادن آهنگ فعلی در فایل‌های کانال (همه کاربران)\n"
                    "• دستور n یا بعدی: پخش آهنگ بعدی (مدیران)\n"
                    "• دستور b یا قبلی: پخش آهنگ قبلی (مدیران)\n"
                    "• دستور v با عدد (مثل v 80): تنظیم بلندی صدا (مدیران)\n"
                    "• دستور h: مخفی کردن یا نمایش مجدد تایتل پلیر (مدیران)\n"
                    "• دستور rc: راه‌اندازی مجدد و خروج و ورود دوباره ربات (مدیران)"
                )
                self.send_chat(help_text)


class RadioMusicBot(BaseMusicBot):
    def __init__(self):
        super().__init__(
            bot_type="radio",
            chan_id=RADIO_CHAN_ID,
            tt_user=RADIO_TT_USER,
            tt_pass=RADIO_TT_PASS,
            tt_nick=RADIO_TT_NICK,
            tg_token=RADIO_TG_TOKEN,
            tg_channel=RADIO_TG_CHANNEL,
            cache_dir=RADIO_CACHE_DIR,
            state_file=RADIO_STATE_FILE,
            config_prefix="radio",
            initial_catalog=BASE_TRACK_CATALOG,
            log_prefix="Radio",
            display_name="رادیو کافه دوستی",
            admins=RADIO_ADMINS
        )


class NostalgiaMusicBot(BaseMusicBot):
    def __init__(self):
        super().__init__(
            bot_type="nostalgia",
            chan_id=NOSTALGIA_CHAN_ID,
            tt_user=NOSTALGIA_TT_USER,
            tt_pass=NOSTALGIA_TT_PASS,
            tt_nick=NOSTALGIA_TT_NICK,
            tg_token=NOSTALGIA_TG_TOKEN,
            tg_channel=NOSTALGIA_TG_CHANNEL,
            cache_dir=NOSTALGIA_CACHE_DIR,
            state_file=NOSTALGIA_STATE_FILE,
            config_prefix="nostalgia",
            initial_catalog=NOSTALGIA_TRACK_CATALOG,
            log_prefix="Nostalgia",
            display_name="نستالژی پلیر کافه دوستی",
            admins=RADIO_ADMINS
        )


global_radio_bot = None
global_nostalgia_bot = None

def format_bot_status(b, bot_title, channel_title):
    if not b:
        return f"ربات {bot_title} در حال راه‌اندازی است..."
    flags = 0
    try:
        flags = b.getFlags()
    except Exception:
        pass
    lines = [
        f"لاگ رویدادها: {' | '.join(b.diag[-8:]) if getattr(b, 'diag', None) else 'هیچ'}",
        f"فلگ کلاینت: {hex(flags)}",
        f"وضعیت اتصال: {'متصل به سرور' if b.connected else 'قطع از سرور'}",
        f"ورود به حساب: {'موفق' if b.logged_in else 'ناموفق'}",
        f"حضور در کانال {channel_title}: {'بله' if b.joined else 'خیر'}",
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

def get_radio_status():
    return format_bot_status(globals().get("global_radio_bot"), "رادیو کافه دوستی", "۲ (رادیو کافه دوستی)")

def get_nostalgia_status():
    return format_bot_status(globals().get("global_nostalgia_bot"), "نستالژی پلیر", "۵ (آلاچیق)")


def music_telegram_sync_worker(bot):
    while not getattr(bot, "restart_requested", False):
        try:
            bot.sync_telegram_playlist()
        except Exception as e:
            print(f"[{bot.log_prefix}] Sync error: {e}", flush=True)
        time.sleep(15)

def run_music_bot_loop(bot_class, global_var_name, service_name, host, port):
    print(f"شروع سرویس {service_name}...", flush=True)
    try:
        ensure_linux_tt_sdk()
    except Exception as e_sdk:
        print(f"[{service_name}] SDK check warning: {e_sdk}", flush=True)

    while True:
        bot = None
        try:
            bot = bot_class()
            globals()[global_var_name] = bot
            bot.load_existing_cache()
            threading.Thread(target=music_telegram_sync_worker, args=(bot,), daemon=True).start()

            last_connect_attempt = time.time()
            print(f"[{bot.log_prefix}] Initiating connect to {host}:{port} (TCP-tunneled audio)...", flush=True)
            bot.diag.append("DO_CONNECT")
            res = bot.connect(host, port, port, 0, 0, False)
            bot.diag.append(f"CONN_RES:{res}")
            print(f"[{bot.log_prefix}] connect() called, returned: {res}", flush=True)
            if not res:
                print(f"[{bot.log_prefix}] connect() returned 0. Cleaning up and retrying in 5s...", flush=True)
                bot.persist_state()
                bot.restart_requested = True
                try:
                    bot.disconnect()
                except:
                    pass
                time.sleep(5)

            try:
                ka = TeamTalk5.ClientKeepAlive()
                ka.nConnectionLostMSec = 15000
                ka.nTcpKeepAliveIntervalMSec = 5000
                ka.nUdpKeepAliveIntervalMSec = 5000
                ka.nUdpKeepAliveRTXMSec = 1000
                ka.nUdpConnectRTXMSec = 1000
                ka.nUdpConnectTimeoutMSec = 5000
                TeamTalk5._SetClientKeepAlive(bot._tt, ctypes.byref(ka))
            except Exception as e_ka:
                print(f"[{bot.log_prefix}] KeepAlive cfg err: {e_ka}", flush=True)

            while not getattr(bot, "restart_requested", False):
                try:
                    now_ts = time.time()
                    flags = bot.getFlags()
                    is_connected = (flags & 0x00004000) != 0

                    if not is_connected:
                        if now_ts - last_connect_attempt > 15:
                            print(f"[{bot.log_prefix}] Connect timeout (>15s, flags={flags}). Forcing reconnection cycle...", flush=True)
                            bot.persist_state()
                            bot.restart_requested = True
                            break
                    else:
                        # Actively send ping every 10s to keep connection alive and prevent server 60s timeout
                        if now_ts - getattr(bot, "_last_ping_time", 0) > 10:
                            bot._last_ping_time = now_ts
                            try:
                                ping_id = bot.doPing()
                                if ping_id <= 0:
                                    print(f"[{bot.log_prefix}] doPing failed ({ping_id}). Socket dead! Forcing reconnect...", flush=True)
                                    bot.persist_state()
                                    bot.restart_requested = True
                                    break
                            except Exception as e_ping:
                                print(f"[{bot.log_prefix}] doPing err: {e_ping}. Forcing reconnect...", flush=True)
                                bot.persist_state()
                                bot.restart_requested = True
                                break

                        # Socket is active and connected
                        pass

                        if getattr(bot, "logged_in", False):
                            if now_ts - getattr(bot, "_last_self_check", 0) > 4:
                                bot._last_self_check = now_ts
                                try:
                                    my_id = bot.getMyUserID()
                                    u = bot.getUser(my_id)
                                    if u and u.nChannelID != bot.chan_id:
                                        print(f"[{bot.log_prefix} Self-Guard] حضور در کانال {u.nChannelID}. بازگشت مستقل به کانال {bot.chan_id}...", flush=True)
                                        bot.joined = False
                                        bot.doJoinChannelByID(bot.chan_id, "")
                                    elif u and u.nChannelID == bot.chan_id:
                                        bot.joined = True
                                        is_actively_streaming = bool(flags & 0x00010000) or getattr(bot, "is_streaming", False)
                                        if getattr(bot, "playlist", None) and not is_actively_streaming and not getattr(bot, "_is_starting_playback", False):
                                            if now_ts - getattr(bot, "last_track_finish_at", 0) > 10:
                                                bot.last_track_finish_at = now_ts
                                                print(f"[{bot.log_prefix} Self-Guard] ربات در کانال {bot.chan_id} است ولی صدا متوقف است. شروع خودکار پخش...", flush=True)
                                                bot.is_streaming = False
                                                threading.Thread(target=bot.auto_start_playback, daemon=True).start()
                                except Exception:
                                    pass

                    bot.runEventLoop(20)
                except Exception as e:
                    bot.diag.append(f"EXC:{type(e).__name__}:{e}")
                    print(f"[{bot.log_prefix}] Loop err: {e}", flush=True)
                    time.sleep(1)

            print(f"[{bot.log_prefix}] Restart requested. Disconnecting cleanly and restarting...", flush=True)
            try:
                bot.stop_all_playback()
                time.sleep(0.2)
                bot.disconnect()
                time.sleep(0.5)
            except Exception as e:
                print(f"[{bot.log_prefix}] Disconnect err during restart: {e}", flush=True)
            time.sleep(1)

        except Exception as e:
            import traceback
            log_p = getattr(bot, "log_prefix", service_name) if 'bot' in locals() and bot else service_name
            print(f"[{log_p}] Fatal error in run_music_bot_loop: {e}\n{traceback.format_exc()}", flush=True)
            time.sleep(5)


def start_radio_worker():
    print("[Radio Worker Thread] Started!", flush=True)
    try:
        run_music_bot_loop(RadioMusicBot, "global_radio_bot", "رادیو کافه دوستی", SHARED_TT_HOST, SHARED_TT_PORT)
    except Exception as e:
        import traceback
        print(f"[Radio Worker Thread] CRASH: {e}\n{traceback.format_exc()}", flush=True)

def start_nostalgia_worker():
    print("[Nostalgia Worker Thread] Started!", flush=True)
    try:
        run_music_bot_loop(NostalgiaMusicBot, "global_nostalgia_bot", "نستالژی پلیر کافه دوستی", SHARED_TT_HOST, SHARED_TT_PORT)
    except Exception as e:
        import traceback
        print(f"[Nostalgia Worker Thread] CRASH: {e}\n{traceback.format_exc()}", flush=True)

radio_worker_thread = None
radio_thread_lock = threading.Lock()

def ensure_radio_worker_alive():
    if not ENABLE_TT_BOTS:
        return
    global radio_worker_thread
    with radio_thread_lock:
        if radio_worker_thread is None or not radio_worker_thread.is_alive():
            print("[Watchdog] ترد رادیو متوقف شده بود! ایجاد و راه‌اندازی فوری ترد جدید رادیو...", flush=True)
            radio_worker_thread = threading.Thread(target=start_radio_worker, daemon=True, name="RadioWorkerThread")
            radio_worker_thread.start()

nostalgia_worker_thread = None
nostalgia_thread_lock = threading.Lock()

def ensure_nostalgia_worker_alive():
    if not ENABLE_TT_BOTS:
        return
    global nostalgia_worker_thread
    with nostalgia_thread_lock:
        if nostalgia_worker_thread is None or not nostalgia_worker_thread.is_alive():
            print("[Watchdog] ترد نستالژی پلیر متوقف شده بود! ایجاد و راه‌اندازی فوری ترد جدید نستالژی پلیر...", flush=True)
            nostalgia_worker_thread = threading.Thread(target=start_nostalgia_worker, daemon=True, name="NostalgiaWorkerThread")
            nostalgia_worker_thread.start()


# ----------------- سیستم دیده‌بان و پایش خودکار ربات ناظر (Watchdog Engine) -----------------
def run_supervisor_watchdog():
    if not ENABLE_TT_BOTS:
        return
    """حلقه پایش و دیده‌بان خودکار ربات ناظر (Watchdog Engine)
    به طور پیوسته وضعیت ربات رادیو و ربات نستالژی پلیر را پایش کرده و در صورت هرگونه قطعی، اخراج،
    یا خروج، بدون وقفه و در سریع‌ترین زمان آن را به کانال مقصد بازگردانده و موزیک را ادامه می‌دهد."""
    print("دیده‌بان خودکار ربات ناظر (Watchdog Engine) فعال شد و در حال پایش وضعیت ربات‌هاست...", flush=True)
    time.sleep(5)
    while True:
        try:
            ensure_radio_worker_alive()
            ensure_nostalgia_worker_alive()

            now_w = time.time()
            # Check Radio Bot
            b = globals().get("global_radio_bot")
            if b:
                age = now_w - getattr(b, "created_at", 0)
                if age > 35:
                    try:
                        flags = b.getFlags()
                    except Exception:
                        flags = 0

                    is_connected = (flags & 0x00004000) != 0
                    if not is_connected or not getattr(b, "connected", False):
                        print(f"[Watchdog] ربات ناظر عدم حضور یا قطعی رادیو را تایید کرد (conn={is_connected}). صدور دستور بازگشت فوری...", flush=True)
                        try:
                            b.persist_state()
                        except Exception:
                            pass
                        b.restart_requested = True

            # Check Nostalgia Bot
            nb = globals().get("global_nostalgia_bot")
            if nb:
                age = now_w - getattr(nb, "created_at", 0)
                if age > 35:
                    try:
                        flags = nb.getFlags()
                    except Exception:
                        flags = 0

                    is_connected = (flags & 0x00004000) != 0
                    if not is_connected or not getattr(nb, "connected", False):
                        print(f"[Watchdog] ربات ناظر عدم حضور یا قطعی نستالژی پلیر را تایید کرد (conn={is_connected}). صدور دستور بازگشت فوری...", flush=True)
                        try:
                            nb.persist_state()
                        except Exception:
                            pass
                        nb.restart_requested = True

        except Exception as e:
            print(f"[Watchdog] Error in supervisor watchdog: {e}", flush=True)

        time.sleep(5)


# ----------------- سیستم بیدار نگه‌داشتن سرور (Keep-Alive Ping) -----------------
def keep_alive_worker():
    time.sleep(10)
    while True:
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            for path in ["/", "/health", "/radio_status", "/nostalgia_status"]:
                try:
                    req = urllib.request.Request(f"https://kaafehdoosti-bot.onrender.com{path}", headers={'User-Agent': 'Mozilla/5.0 (KeepAlive/2.0)'})
                    with opener.open(req, timeout=10) as resp:
                        pass
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(60)  # هر ۶۰ ثانیه پینگ فعال ارسال می‌کند

threading.Thread(target=keep_alive_worker, daemon=True).start()
threading.Thread(target=get_tt_existing_cached, daemon=True).start()
threading.Thread(target=run_inactivity_checker, daemon=True).start()
# کنترل فعال‌سازی اتصال ربات‌های تیم‌تاک (پیش‌فرض خاموش طبق دستور کاربر تا تکمیل نهایی تست‌ها)
ENABLE_TT_BOTS = os.environ.get("ENABLE_TT_BOTS", "0") == "1"
if ENABLE_TT_BOTS:
    threading.Thread(target=monitor_teamtalk_activity, daemon=True).start()
    ensure_radio_worker_alive()
    time.sleep(5)
    ensure_nostalgia_worker_alive()
    time.sleep(3)
    threading.Thread(target=run_supervisor_watchdog, daemon=True).start()
else:
    print("[TeamTalk] ربات‌های تیم‌تاک طبق دستور ایزوله‌سازی غیرفعال هستند (ENABLE_TT_BOTS=0). فقط وب‌سرور و ربات تلگرام فعالند.", flush=True)
# OLD: threading.Thread(target=monitor_teamtalk_activity
ensure_radio_worker_alive()
time.sleep(5)
ensure_nostalgia_worker_alive()
time.sleep(3)
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
            url = f"{TELEGRAM_API_BASE}/bot{BOT_TOKEN}/getUpdates?timeout=30"
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
