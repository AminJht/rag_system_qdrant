# main.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import webbrowser
import threading
import time
import asyncio  # برای run_in_executor

from chain import start  # تابع اصلیِ ساخت پاسخ 

app = FastAPI()


# Mount static files (for serving HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store connected clients
connected_clients = set()

# HTML for the chat interface
with open("static/index.html", "r", encoding="utf-8") as file:
    html_content = file.read()

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            question = await websocket.receive_text()

            # --- بهبود پرفورمنس بدون تغییر رفتار ---
            # اگر start(question) بلاکینگ باشد، حلقهٔ رویداد را قفل می‌کند.
            # برای جلوگیری، آن را در ThreadPool اجرا می‌کنیم.
            # اگر نخواستی: می‌توانی 3 خط زیر را حذف و مستقیماً start(question) را صدا بزنی.
            loop = asyncio.get_running_loop()
            generate_data = await loop.run_in_executor(None, start, question)
            # --- پایان بهبود پرفورمنس ---

            # اگر حالت قبلی را دقیقاً می‌خواهی (بلاکینگ)، این خط را جایگزین کن:
            # generate_data = start(question)

            # Format bot message with newline (همان رفتار قبلی)
            bot_message = f"خروجی:\n {generate_data}"

            # Broadcast to all connected clients (همان رفتار قبلی)
            # برای جلوگیری از تغییر اندازهٔ set هنگام iteration، یک snapshot می‌گیریم.
            clients_snapshot = list(connected_clients)
            for client in clients_snapshot:
                try:
                    await client.send_text(bot_message)
                except Exception:
                    # اگر کلاینت دچار مشکل شد، حذفش می‌کنیم
                    connected_clients.discard(client)
    except Exception:
        # می‌توانی اینجا لاگ بگیری، ولی رفتار را تغییر ندادم
        pass
    finally:
        # پاک‌سازی حتماً در finally تا در هر حالت انجام شود (پایداری بیشتر)
        connected_clients.discard(websocket)
        try:
            await websocket.close()
        except Exception:
            pass


def open_browser():
    # Wait briefly to ensure the server is running
    time.sleep(1)
    webbrowser.open("http://localhost:8002")


if __name__ == "__main__":
    # Start the browser in a separate thread to avoid blocking the server
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="debug")
