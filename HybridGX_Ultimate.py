import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage, QWebEngineScript

class CustomWebPage(QWebEnginePage):
    """Кастомна сторінка з антидетектом"""
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass

class HybridGX_Ultimate(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hybrid GX Ultra")
        self.showMaximized()
        self.setStyleSheet("background: #050505;")

        # --- СТВОРЕННЯ ПРОФІЛЮ З МАКСИМАЛЬНИМ ОБХОДОМ ---
        storage_path = os.path.join(os.path.expanduser("~"), "GX_Data")
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        # Використовуємо НЕ дефолтний профіль
        self.profile = QWebEngineProfile("HybridGX_Main", None)
        self.profile.setPersistentStoragePath(storage_path)
        self.profile.setCachePath(os.path.join(storage_path, "cache"))
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )
        
        # Найновіший Chrome 131 User-Agent (лютий 2026)
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        self.profile.setHttpUserAgent(user_agent)
        
        # Accept-Language для України
        self.profile.setHttpAcceptLanguage("uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7")
        
        # --- НАЛАШТУВАННЯ WEBENGINE ---
        settings = self.profile.settings()
        
        # Базові налаштування
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        
        # Графіка та медіа
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        
        # Автозавантаження
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        
        # Повноекранний режим
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        
        # Безпека
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        
        # Скролбари
        settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
        
        # Кодування
        settings.setDefaultTextEncoding("utf-8")

        # --- ІНТЕРФЕЙС ---
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("""
            QTabWidget { background: #050505; border: none; }
            QTabWidget::pane { border: none; background: #050505; }
            QTabBar { background: #0b0b0b; border: none; }
            QTabBar::tab {
                background: #1a1a1a; color: #888; padding: 10px 20px;
                border-top-left-radius: 5px; border-top-right-radius: 5px;
                margin-right: 2px; min-width: 150px; font-weight: bold;
            }
            QTabBar::tab:selected { background: #ff8800; color: #000; }
            QTabBar::close-button { image: none; }
        """)
        self.setCentralWidget(self.tabs)

        self.create_top_bar()
        self.create_sidebar()
        self.add_new_tab()

    def create_top_bar(self):
        tbar = QToolBar()
        tbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tbar)
        tbar.setStyleSheet("QToolBar { background: #0b0b0b; border-bottom: 2px solid #ff8800; padding: 5px; }")

        btn_style = "color: #ff8800; font-size: 18px; border: none; padding: 0 10px; font-weight: bold; background: transparent;"
        
        # Назад
        back_btn = QPushButton("←")
        back_btn.setStyleSheet(btn_style)
        back_btn.clicked.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        tbar.addWidget(back_btn)
        
        # Вперед
        forward_btn = QPushButton("→")
        forward_btn.setStyleSheet(btn_style)
        forward_btn.clicked.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        tbar.addWidget(forward_btn)

        # Перезавантажити
        relo_btn = QPushButton("↻")
        relo_btn.setStyleSheet(btn_style)
        relo_btn.clicked.connect(lambda: self.current_browser().reload() if self.current_browser() else None)
        tbar.addWidget(relo_btn)

        # URL бар
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet(
            "QLineEdit { background: #000; color: #fff; border: 1px solid #333; "
            "border-radius: 15px; padding: 5px 15px; margin: 0 10px; font-size: 14px; }"
        )
        self.url_bar.returnPressed.connect(self.navigate)
        tbar.addWidget(self.url_bar)

        # Нова вкладка
        add_btn = QPushButton("+")
        add_btn.setStyleSheet(btn_style)
        add_btn.clicked.connect(lambda: self.add_new_tab())
        tbar.addWidget(add_btn)
        
        # Налаштування
        settings_btn = QPushButton("⚙")
        settings_btn.setStyleSheet(btn_style)
        settings_btn.clicked.connect(self.show_info)
        tbar.addWidget(settings_btn)

    def create_sidebar(self):
        side = QToolBar()
        side.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, side)
        side.setStyleSheet(
            "QToolBar { background: #000; border-right: 1px solid #1a1a1a; "
            "min-width: 60px; padding-top: 10px; }"
        )
        
        links = [
            ("GX", self.go_home), 
            ("🏠", "https://google.com"), 
            ("📺", "https://youtube.com"),
            ("📧", "https://gmail.com"),
            ("🎮", "https://roblox.com"),
            ("💬", "https://discord.com")
        ]
        
        for icon, target in links:
            btn = QPushButton(icon)
            btn.setFixedSize(45, 45)
            
            if icon == "GX":
                btn.setStyleSheet(
                    "background: #ff8800; color: #000; font-weight: bold; "
                    "border-radius: 5px; font-size: 16px;"
                )
            else:
                btn.setStyleSheet(
                    "color: #ff8800; font-size: 20px; border: none; background: transparent;"
                )
            
            if callable(target):
                btn.clicked.connect(target)
            else:
                btn.clicked.connect(lambda _, u=target: self.navigate_to(u))
            
            side.addWidget(btn)

    def navigate_to(self, url):
        """Навігація на URL"""
        if self.current_browser():
            self.current_browser().setUrl(QUrl(url))

    def add_new_tab(self, qurl=None):
        """Додати нову вкладку з антидетектом"""
        browser = QWebEngineView()
        page = CustomWebPage(self.profile, browser)
        browser.setPage(page)
        
        # РОЗШИРЕНИЙ АНТИДЕТЕКТ СКРИПТ
        anti_detect = """
        (function() {
            'use strict';
            
            // 1. Видаляємо webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
            
            // 2. Chrome runtime (важливо для Google)
            window.navigator.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // 3. Plugins (реалістичні)
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        {
                            name: 'Chrome PDF Plugin',
                            filename: 'internal-pdf-viewer',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            description: 'Portable Document Format'
                        },
                        {
                            name: 'Native Client',
                            filename: 'internal-nacl-plugin',
                            description: 'Native Client Executable'
                        }
                    ];
                    return plugins;
                },
                configurable: true
            });
            
            // 4. Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['uk-UA', 'uk', 'en-US', 'en'],
                configurable: true
            });
            
            // 5. Platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32',
                configurable: true
            });
            
            // 6. Hardware Concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8,
                configurable: true
            });
            
            // 7. Device Memory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
                configurable: true
            });
            
            // 8. Permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
            
            // 9. WebGL Vendor & Renderer
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.call(this, parameter);
            };
            
            // 10. Battery API (якщо є)
            if (navigator.getBattery) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1,
                    addEventListener: () => {},
                    removeEventListener: () => {}
                });
            }
            
            // 11. Connection API
            if (navigator.connection) {
                Object.defineProperty(navigator.connection, 'rtt', {
                    get: () => 50
                });
            }
            
            // 12. Media Devices
            if (navigator.mediaDevices) {
                const origEnumerateDevices = navigator.mediaDevices.enumerateDevices;
                navigator.mediaDevices.enumerateDevices = () => {
                    return origEnumerateDevices().then(devices => {
                        return devices.length > 0 ? devices : [
                            {deviceId: "default", kind: "audioinput", label: ""},
                            {deviceId: "default", kind: "audiooutput", label: ""},
                            {deviceId: "default", kind: "videoinput", label: ""}
                        ];
                    });
                };
            }
            
            // 13. Screen properties
            Object.defineProperty(window.screen, 'colorDepth', {
                get: () => 24
            });
            Object.defineProperty(window.screen, 'pixelDepth', {
                get: () => 24
            });
            
            // 14. Window dimensions
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth
            });
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight + 85
            });
            
            // 15. Console debug (приховуємо детекцію)
            const originalDebug = console.debug;
            console.debug = function() {
                if (arguments[0] && typeof arguments[0] === 'string' && 
                    arguments[0].includes('devtools')) {
                    return;
                }
                return originalDebug.apply(console, arguments);
            };
            
        })();
        """
        
        # Додаємо скрипт
        script = QWebEngineScript()
        script.setSourceCode(anti_detect)
        script.setName("AntiDetect")
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setRunsOnSubFrames(True)
        page.scripts().insert(script)
        
        # Встановлюємо URL
        if qurl is None:
            browser.setHtml(self.get_home_html())
        else:
            browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, "Нова вкладка")
        self.tabs.setCurrentIndex(i)

        # Сигнали
        browser.urlChanged.connect(
            lambda q: self.url_bar.setText(q.toString()) 
            if self.tabs.currentWidget() == browser else None
        )
        browser.titleChanged.connect(
            lambda t: self.tabs.setTabText(
                self.tabs.indexOf(browser), 
                t[:20] if t else "Нова вкладка"
            )
        )
        
        self.tabs.currentChanged.connect(self.update_url_bar)

    def update_url_bar(self):
        """Оновити URL бар"""
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())

    def current_browser(self):
        """Поточний браузер"""
        return self.tabs.currentWidget()
    
    def close_tab(self, i):
        """Закрити вкладку"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.add_new_tab()
            self.tabs.removeTab(i)
    
    def navigate(self):
        """Навігація"""
        t = self.url_bar.text().strip()
        if not t:
            return
        
        if t.startswith("http://") or t.startswith("https://"):
            url = t
        elif t.startswith("www."):
            url = "https://" + t
        elif "." in t and " " not in t:
            url = "https://" + t
        else:
            url = f"https://www.google.com/search?q={t}"
        
        if self.current_browser():
            self.current_browser().setUrl(QUrl(url))
    
    def go_home(self):
        """На головну"""
        if self.current_browser():
            self.current_browser().setHtml(self.get_home_html())
    
    def show_info(self):
        """Показати інфо"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Hybrid GX - Інформація")
        
        storage = os.path.expanduser("~") + "\\GX_Data"
        msg.setText(
            "🚀 Hybrid GX Ultra\n\n"
            "✅ Cookies: Збережено\n"
            "✅ Історія: Збережено\n"
            "✅ Сесії: Збережено\n\n"
            f"📁 Папка даних:\n{storage}\n\n"
            "💡 Порада:\n"
            "Після входу в YouTube/Google ваш\n"
            "акаунт буде збережено назавжди!\n\n"
            "Версія: 3.0 Ultimate"
        )
        msg.setStyleSheet(
            "QMessageBox { background: #1a1a1a; color: white; }"
            "QLabel { color: white; font-size: 13px; }"
            "QPushButton { background: #ff8800; color: black; "
            "padding: 8px 20px; border-radius: 5px; font-weight: bold; }"
        )
        msg.exec()

    def get_home_html(self):
        """HTML головної сторінки"""
        return """
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hybrid GX</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    background: linear-gradient(135deg, #050505 0%, #0a0a0a 100%);
                    color: white; 
                    font-family: 'Segoe UI', sans-serif; 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center; 
                    justify-content: center; 
                    min-height: 100vh;
                }
                .logo { 
                    font-size: 60px; 
                    font-weight: bold; 
                    margin-bottom: 30px; 
                    text-shadow: 0 0 30px rgba(255, 136, 0, 0.6);
                }
                .logo span { color: #ff8800; }
                .search { width: 500px; margin-bottom: 40px; }
                .search input { 
                    width: 100%; 
                    padding: 15px 20px; 
                    border-radius: 25px; 
                    border: 2px solid #ff8800; 
                    background: #111; 
                    color: white; 
                    font-size: 16px; 
                    outline: none;
                    transition: all 0.3s;
                }
                .search input:focus {
                    border-color: #ffaa00;
                    box-shadow: 0 0 20px rgba(255, 136, 0, 0.4);
                }
                .grid { 
                    display: grid; 
                    grid-template-columns: repeat(4, 120px); 
                    gap: 15px;
                }
                .tile { 
                    background: #111; 
                    border: 1px solid #222; 
                    border-radius: 10px; 
                    padding: 20px; 
                    text-align: center; 
                    cursor: pointer; 
                    transition: all 0.3s;
                }
                .tile:hover { 
                    border-color: #ff8800; 
                    background: #1a1a1a; 
                    transform: translateY(-5px);
                    box-shadow: 0 10px 20px rgba(255, 136, 0, 0.3);
                }
                .tile img { 
                    width: 40px; 
                    height: 40px; 
                    margin-bottom: 10px; 
                    border-radius: 5px;
                }
                .tile div { font-size: 13px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="logo">Hybrid <span>GX</span></div>
            <div class="search">
                <input type="text" id="search" placeholder="🔍 Пошук або URL..." 
                       onkeydown="if(event.key==='Enter') go()">
            </div>
            <div class="grid">
                <div class="tile" onclick="nav('https://youtube.com')">
                    <img src="https://www.google.com/s2/favicons?sz=64&domain=youtube.com">
                    <div>YouTube</div>
                </div>
                <div class="tile" onclick="nav('https://gmail.com')">
                    <img src="https://www.google.com/s2/favicons?sz=64&domain=gmail.com">
                    <div>Gmail</div>
                </div>
                <div class="tile" onclick="nav('https://discord.com')">
                    <img src="https://www.google.com/s2/favicons?sz=64&domain=discord.com">
                    <div>Discord</div>
                </div>
                <div class="tile" onclick="nav('https://roblox.com')">
                    <img src="https://www.google.com/s2/favicons?sz=64&domain=roblox.com">
                    <div>Roblox</div>
                </div>
            </div>
            <script>
                function go() {
                    const v = document.getElementById('search').value;
                    if (v.startsWith('http://') || v.startsWith('https://')) {
                        window.location = v;
                    } else if (v.includes('.') && !v.includes(' ')) {
                        window.location = 'https://' + v;
                    } else {
                        window.location = 'https://www.google.com/search?q=' + v;
                    }
                }
                function nav(url) { window.location = url; }
                document.getElementById('search').focus();
            </script>
        </body>
        </html>
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Hybrid GX")
    app.setOrganizationName("HybridGX")
    
    window = HybridGX_Ultimate()
    window.show()
    
    sys.exit(app.exec())