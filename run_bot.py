"""
Master Runner for 4000 Essential English Words Telegram Bot & WebApp
Features:
- Concurrent Aiohttp Web Server (serving WebApp & REST APIs)
- Cloudflare Tunnel (providing instant HTTPS URL for Telegram WebApp)
- Automatic registration with Telegram setChatMenuButton
- Telegram Bot polling engine with auto-recovery
- Support for 24/7 cloud deployments (Render, Railway, Koyeb, Docker)
"""
import os
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import asyncio
import logging
import threading
from aiohttp import web

from bot import build_application
from web_server import create_web_app
import tunnel_manager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("Runner")

def start_aiohttp_server(port: int = 8080):
    """Runs the aiohttp web server in a separate background event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = create_web_app()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, "0.0.0.0", port)
    loop.run_until_complete(site.start())
    print(f"[+] WebApp va API server 0.0.0.0:{port} da ishga tushdi.", flush=True)
    loop.run_forever()

def run():
    print("=" * 60, flush=True)
    print(" 🚀 4000 ESSENTIAL WORDS TELEGRAM BOT & WEBAPP ISHGA TUSHMOQDA...", flush=True)
    print("=" * 60, flush=True)

    port = int(os.getenv("PORT", 8080))
    
    # 1. Start WebApp & API Server in background thread
    web_thread = threading.Thread(target=start_aiohttp_server, args=(port,), daemon=True)
    web_thread.start()
    time.sleep(1)

    # 2. Configure Telegram WebApp URL
    cloud_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBAPP_URL")
    if cloud_url:
        print(f"[*] Cloud URL aniqlandi: {cloud_url}", flush=True)
        tunnel_manager.update_telegram_menu_button(cloud_url)
    else:
        # Start local Cloudflare Tunnel to provide live HTTPS for Telegram WebApp
        threading.Thread(target=tunnel_manager.start_tunnel_process, args=(port,), daemon=True).start()

    # 3. Start Telegram Bot Polling
    while True:
        try:
            app = build_application()
            print("[+] Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda!", flush=True)
            app.run_polling(drop_pending_updates=False, close_loop=False)
        except Exception as e:
            logger.error(f"Botda xatolik yuz berdi: {e}", exc_info=True)
            print("[!] 5 soniyadan so'ng qayta ishga tushiriladi...", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    run()
