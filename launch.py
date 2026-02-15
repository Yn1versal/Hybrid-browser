import os
import subprocess
import sys

print("=" * 60)
print("         HYBRID GX - CHROME LAUNCHER")
print("=" * 60)
print()

# Шляхи до Chrome
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]

def find_chrome():
    """Знайти Chrome"""
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def open_chrome(url):
    """Відкрити Chrome з профілем"""
    chrome = find_chrome()
    
    if not chrome:
        print("❌ Chrome не знайдено!")
        print("Встановіть Chrome: https://www.google.com/chrome/")
        input("\nНатисніть Enter...")
        return
    
    # Профіль
    profile = os.path.join(os.getcwd(), "HybridGX_Profile")
    if not os.path.exists(profile):
        os.makedirs(profile)
        print(f"✅ Створено профіль: {profile}")
    
    # Запуск
    cmd = [
        chrome,
        f"--user-data-dir={profile}",
        "--no-first-run",
        "--no-default-browser-check",
        url
    ]
    
    print(f"\n🚀 Запускаю Chrome...")
    print(f"📍 URL: {url}")
    print(f"📁 Профіль: {profile}")
    
    try:
        subprocess.Popen(cmd)
        print("\n✅ Chrome запущено успішно!")
        print("\n💡 Підказка:")
        print("   • Увійдіть в Google акаунт")
        print("   • Всі дані збережуться")
        print("   • При наступному запуску ви вже будете залогінені")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
    
    input("\nНатисніть Enter для виходу...")

# Меню
print("Виберіть сайт:")
print()
print("1. 🏠 Google")
print("2. 📺 YouTube")
print("3. 📧 Gmail")
print("4. 🎮 Roblox")
print("5. 💬 Discord")
print("6. 🔍 Інший URL")
print()

choice = input("Ваш вибір (1-6): ").strip()

urls = {
    "1": "https://google.com",
    "2": "https://youtube.com",
    "3": "https://gmail.com",
    "4": "https://roblox.com",
    "5": "https://discord.com",
}

if choice in urls:
    open_chrome(urls[choice])
elif choice == "6":
    custom = input("\nВведіть URL: ").strip()
    if custom:
        if not custom.startswith("http"):
            custom = "https://" + custom
        open_chrome(custom)
else:
    print("❌ Невірний вибір!")
    input("\nНатисніть Enter...")
