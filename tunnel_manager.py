"""
Tunnel manager to expose local WebApp via Cloudflare Tunnel
and automatically register it with Telegram Bot API
"""
import os
import re
import sys
import time
import json
import logging
import threading
import subprocess
import urllib.request
from config import BOT_TOKEN

logger = logging.getLogger("TunnelManager")

active_tunnel_url = None

def get_web_app_url() -> str:
    """Returns the live HTTPS WebApp URL."""
    global active_tunnel_url
    if active_tunnel_url:
        return active_tunnel_url
    env_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBAPP_URL")
    if env_url:
        return env_url
    url_file = os.path.join(os.path.dirname(__file__), "tunnel_url.txt")
    if os.path.exists(url_file):
        try:
            with open(url_file, "r", encoding="utf-8") as f:
                u = f.read().strip()
                if u.startswith("https://"):
                    active_tunnel_url = u
                    return u
        except Exception:
            pass
    return "https://essential-words-bot.onrender.com"

def update_telegram_menu_button(web_app_url: str):
    """Sets the Telegram bot chat menu button to the WebApp URL."""
    global active_tunnel_url
    active_tunnel_url = web_app_url
    try:
        url_file = os.path.join(os.path.dirname(__file__), "tunnel_url.txt")
        with open(url_file, "w", encoding="utf-8") as f:
            f.write(web_app_url)
    except Exception:
        pass

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton"
        payload = {
            "menu_button": {
                "type": "web_app",
                "text": "🎓 4000 Academy",
                "web_app": {
                    "url": web_app_url
                }
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read().decode("utf-8"))
        if data.get("ok"):
            print(f"[+] Telegram WebApp muvaffaqiyatli ulandi: {web_app_url}", flush=True)
            return True
        else:
            print(f"[!] setChatMenuButton error: {data}", flush=True)
    except Exception as e:
        logger.error(f"Error setting Telegram menu button: {e}")
    return False

def start_tunnel_process(port: int = 8080):
    """Starts cloudflared tunnel and listens for the HTTPS URL."""
    global active_tunnel_url
    cf_path = os.path.join(os.path.dirname(__file__), "cloudflared.exe")
    if not os.path.exists(cf_path):
        cf_path = "cloudflared"

    cmd = [cf_path, "tunnel", "--url", f"http://127.0.0.1:{port}"]
    
    print("[*] Cloudflare Tunnel ishga tushirilmoqda...", flush=True)
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace"
        )

        tunnel_url = None
        url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

        for line in iter(proc.stdout.readline, ""):
            if not line:
                break
            match = url_pattern.search(line)
            if match:
                tunnel_url = match.group(0)
                active_tunnel_url = tunnel_url
                print(f"[+] Jonli HTTPS Havola yaratildi: {tunnel_url}", flush=True)
                update_telegram_menu_button(tunnel_url)
                break

        # Keep reading in background to prevent buffer stall
        def drain_pipe():
            for _ in iter(proc.stdout.readline, ""):
                pass
                
        threading.Thread(target=drain_pipe, daemon=True).start()
        return proc, tunnel_url
    except Exception as e:
        logger.warning(f"Cloudflare tunnelni ishga tushirib bo'lmadi (agar cloud serverda bo'lsangiz WEBAPP_URL dan foydalaniladi): {e}")
        return None, None
