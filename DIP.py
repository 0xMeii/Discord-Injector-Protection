import os
import shutil
import sys
import time
import tkinter as tk
import ctypes
import winreg
import json

from tkinter import messagebox
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer


class WatchDogEvent(LoggingEventHandler):
    def on_modified(self, event):
        local = os.getenv('LOCALAPPDATA')
        paths = [
            os.path.join(local, 'Discord'),
            os.path.join(local, 'discordcanary'),
            os.path.join(local, 'discordptb'),
        ]
        detected = False
        for path in paths:
            if os.path.exists(path):
                version = get_discord_version(path)
                if version:
                    core_path = os.path.join(path, f'app-{version}', 'modules', f'discord_desktop_core-{version}', 'discord_desktop_core')
                    if os.path.exists(core_path):
                        with open(os.path.join(core_path, 'index.js'), 'r', encoding='utf8') as f:
                            content = f.read()
                            if 'NixSquad' in content:
                                os.remove(os.path.join(core_path, 'index.js'))
                                with open(os.path.join(core_path, 'index.txt'), 'w', encoding='utf8') as f:
                                    f.write("module.exports = require('./core.asar');")
                                os.rename(os.path.join(core_path, 'index.txt'), os.path.join(core_path, 'index.js'))
                                ctypes.windll.user32.MessageBoxW(0, "¡Se detectó una inyección y se eliminó!", "Discord Injector Protection", 1)
                                detected = True
                                break
        if not detected:
            ctypes.windll.user32.MessageBoxW(0, "No se detectó ninguna inyección. #NixSquad", "Discord Injector Protection", 1)

def get_discord_version(path):
    """
     Devuelve el número de versión de Discord encontrado en la ruta dada,
     leyendo el archivo "package.json".
    """
    package_path = os.path.join(path, 'package.json')
    if os.path.exists(package_path):
        with open(package_path, 'r') as f:
            data = json.load(f)
            if 'version' in data:
                return data['version'].split('.')[0]
    return None

def main():
    local = os.getenv('LOCALAPPDATA')
    paths = [
        os.path.join(local, 'Discord'),
        os.path.join(local, 'discordcanary'),
        os.path.join(local, 'discordptb'),
    ]
    for path in paths:
        if os.path.exists(path):
            version = get_discord_version(path)
            if version:
                core_path = os.path.join(path, f'app-{version}', 'modules', f'discord_desktop_core-{version}', 'discord_desktop_core')
                if os.path.exists(core_path):
                    observer = Observer()
                    observer.schedule(WatchDogEvent(), core_path, recursive=True)
                    ctypes.windll.user32.MessageBoxW(0, "Su Discord está siendo monitoreado por Discord Injector Protection. #NixSquad", "Discord Injector Protection", 1)
                    observer.start()
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        observer.stop()
                    observer.join()
                    return
    ctypes.windll.user32.MessageBoxW(0, "No se detectó ninguna inyección. #NixSquad", "Discord Injector Protection", 1)

def startup():
    confirm = tk.messagebox.askyesno("Discord Injector Protection", "¿Desea agregar el programa al inicio del sistema?")
    if not confirm:
        return

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
    path = os.path.abspath(sys.argv[0])
    try:
        winreg.SetValueEx(key, 'Windows Update Service', 0, winreg.REG_SZ, path)
        tk.messagebox.showinfo("Discord Injector Protection", "El programa se agregó correctamente al inicio del sistema.")
    except Exception as e:
        tk.messagebox.showerror("Discord Injector Protection", f"No se pudo agregar el programa al inicio del sistema. Error: {e}")

if __name__ == "__main__":
    main()
    startup()
