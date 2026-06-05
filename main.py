import sys
import sqlite3
import os
import json
import hashlib
import subprocess
import shutil
import random
import webbrowser
from pathlib import Path
from PIL import Image

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QLabel, QFileDialog, QStatusBar,
                               QProgressBar, QMessageBox, QLineEdit, QHBoxLayout,
                               QCompleter, QGroupBox, QScrollArea, QGridLayout,
                               QSplitter, QSizePolicy, QToolBar, QDialog,
                               QDialogButtonBox, QRadioButton, QButtonGroup,
                               QFrame, QPlainTextEdit, QFormLayout)
from PySide6.QtCore import Qt, QThread, Signal, QStringListModel, QSize, QTimer, QRunnable, QThreadPool, QObject
from PySide6.QtGui import QPixmap, QIcon, QAction, QColor


# ======================== ПУТИ (работает и из .py и из .exe) ========================

def get_app_dir() -> str:
    """Папка рядом с exe (или папка скрипта при разработке)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_tool_path(name: str) -> str:
    """Ищет ffmpeg/ffprobe/Ruxx рядом с exe, потом в PATH."""
    app_dir = get_app_dir()
    candidates = [
        os.path.join(app_dir, name + '.exe'),
        os.path.join(app_dir, name),
    ]
    if getattr(sys, 'frozen', False):
        try:
            candidates.append(os.path.join(sys._MEIPASS, name + '.exe'))
        except AttributeError:
            pass
    for p in candidates:
        if os.path.exists(p):
            return p
    return name


# ======================== ЛОКАЛИЗАЦИЯ (МУЛЬТИЯЗЫЧНОСТЬ) ========================

LANG_TEXT = {
    "ru": {
        "title": "Local_R34 by Martin v1.6",
        "toolbar_settings": "⚙  Настройки",
        "toolbar_video": "🎬  Видео-превью",
        "toolbar_image": "🖼️  Превью картинок",
        "toolbar_download": "📥  Скачать из R34",
        "btn_select_root": "📁  Выбрать корневую папку с работами",
        "lbl_no_folder": "Папка не выбрана",
        "btn_scan_db": "🔄  Просканировать / Обновить базу",
        "group_search": "  🔍  Поисковый запрос",
        "edit_search_placeholder": "Введите теги через пробел...",
        "edit_tag_placeholder": "Добавить тег (с автодополнением)...",
        "btn_add": "Добавить",
        "btn_search": "🔍  Поиск",
        "view_idle": "Выберите файл для просмотра",
        "tags_prefix": "Теги: ",
        "btn_prev": "◀  Пред.",
        "btn_next": "След. ▶",
        "btn_fullscreen": "⛶  Открыть в окне",
        "btn_save": "💾  Сохранить в...",
        "status_ready": "Готов",
        "status_db_not_found": "База данных не найдена",
        "status_no_tags": "В базе нет тегов. Проверьте, что файлы найдены.",
        "status_search_failed": "Поиск не дал результатов",
        "status_searching": "Найдено {count} файлов. Загрузка миниатюр...",
        "status_loading_tags": "Загружено {count} уникальных тегов",
        "theme_selection_title": "Выберите тему оформления:",
        "lang_selection_title": "Выберите язык / Select Language:",
        "lang_restart_msg": "Пожалуйста, перезапустите программу для полной смены языка.",
        # Окно скачивания
        "dl_title": "Массовое скачивание из RUXX by Martin",
        "dl_tags_label": "Список тегов для скачивания (каждый тег с новой строки):",
        "dl_exe_label": "Путь к Ruxx.exe:",
        "dl_out_label": "Папка для скачивания:",
        "dl_api_label": "API Ключ (необязательно):",
        "dl_uid_label": "User ID (необязательно):",
        "dl_btn_help": "❓  Помощь по API",
        "dl_btn_browse": "Обзор...",
        "dl_btn_start": "🚀  Запустить скачивание",
        "dl_btn_stop_soft": "🛑  Остановить корректно",
        "dl_btn_stop_hard": "⚡  Остановить принудительно",
        "dl_help_title": "Справка по API",
        "dl_help_content": "Как получить API Key и User ID:\n\n1. Зайдите на сайт через браузер.\n2. Откройте ваш профиль / настройки (My Account).\n3. Скопируйте User ID и сгенерируйте API Key.\n\nЕсли оставить поля пустыми, скачивание будет идти в анонимном режиме.",
        "dl_status_idle": "Ожидание запуска...",
        "dl_status_processing": "Обработка: {tag}...",
        "dl_status_soft_stopping": "Остановка... Завершаем текущий тег...",
        "dl_status_hard_stopped": "Скачивание принудительно прервано!",
        "dl_status_done": "Завершено! Всего обработано тегов: {count}",
        "dl_status_progress": "{tag}   [{current} из {total} тегов]",
    },
    "en": {
        "title": "Local_R34 by Martin v1.6",
        "toolbar_settings": "⚙  Settings",
        "toolbar_video": "🎬  Video Preview",
        "toolbar_image": "🖼️  Image Preview",
        "toolbar_download": "📥  Download from R34",
        "btn_select_root": "📁  Select Root Folder with Works",
        "lbl_no_folder": "Folder not selected",
        "btn_scan_db": "🔄  Scan / Update Database",
        "group_search": "  🔍  Search Query",
        "edit_search_placeholder": "Enter tags separated by space...",
        "edit_tag_placeholder": "Add tag (with autocomplete)...",
        "btn_add": "Add",
        "btn_search": "🔍  Search",
        "view_idle": "Select a file to view",
        "tags_prefix": "Tags: ",
        "btn_prev": "◀  Prev.",
        "btn_next": "Next ▶",
        "btn_fullscreen": "⛶  Open in Window",
        "btn_save": "💾  Save to...",
        "status_ready": "Ready",
        "status_db_not_found": "Database not found",
        "status_no_tags": "No tags in database. Ensure files are scanned.",
        "status_search_failed": "No results found",
        "status_searching": "Found {count} files. Loading thumbnails...",
        "status_loading_tags": "Loaded {count} unique tags",
        "theme_selection_title": "Select Theme UI:",
        "lang_selection_title": "Выберите язык / Select Language:",
        "lang_restart_msg": "Please restart the application to fully apply the language change.",
        # Downloader Window
        "dl_title": "Bulk Download from RUXX by Martin",
        "dl_tags_label": "List of tags to download (each tag on a new line):",
        "dl_exe_label": "Path to Ruxx.exe:",
        "dl_out_label": "Output download folder:",
        "dl_api_label": "API Key (optional):",
        "dl_uid_label": "User ID (optional):",
        "dl_btn_help": "❓  API Help",
        "dl_btn_browse": "Browse...",
        "dl_btn_start": "🚀  Start Download",
        "dl_btn_stop_soft": "🛑  Stop Softly",
        "dl_btn_stop_hard": "⚡  Kill Download",
        "dl_help_title": "API Help Reference",
        "dl_help_content": "How to get API Key and User ID:\n\n1. Log into the website via your browser.\n2. Go to your profile / settings (My Account).\n3. Copy User ID and generate your API Key.\n\nIf fields are left empty, downloads will proceed in anonymous mode.",
        "dl_status_idle": "Waiting to start...",
        "dl_status_processing": "Processing: {tag}...",
        "dl_status_soft_stopping": "Stopping... Finishing current tag...",
        "dl_status_hard_stopped": "Download forcefully terminated!",
        "dl_status_done": "Completed! Total tags processed: {count}",
        "dl_status_progress": "{tag}   [{current} of {total} tags]",
    }
}


# ======================== ТЕМЫ ОФОРМЛЕНИЯ ========================

THEMES = {
    "dark": {
        "bg":              "#2b2b2b", "bg2":             "#333333", "bg3":             "#1e1e1e",
        "accent":          "#757575", "accent2":         "#999999", "text":            "#f0f0f0",
        "text2":           "#aaaaaa", "border":          "#484848", "border_acc":      "#888888",
        "btn_hover":       "#404040", "btn_pressed":     "#555555", "chunk":           "#757575",
        "view_bg":         "#222222", "view_border":     "#555555", "toolbar_bg":      "#252525",
        "group_title":     "#bbbbbb", "scroll_bg":       "#2b2b2b", "scroll_handle":   "#555555",
        "is_dark":         True,      "label":           "🌑 Тёмная (классическая)",
    },
    "dark_blue": {
        "bg":              "#1a1f30", "bg2":             "#222840", "bg3":             "#11162a",
        "accent":          "#4a80d0", "accent2":         "#6a9fe8", "text":            "#dde8ff",
        "text2":           "#8899cc", "border":          "#2a3a60", "border_acc":      "#4a80d0",
        "btn_hover":       "#283060", "btn_pressed":     "#384580", "chunk":           "#4a80d0",
        "view_bg":         "#141928", "view_border":     "#4a80d0", "toolbar_bg":      "#141928",
        "group_title":     "#6a9fe8", "scroll_bg":       "#1a1f30", "scroll_handle":   "#4a80d0",
        "is_dark":         True,      "label":           "🔵 Тёмный + голубой акцент",
    },
    "dark_pink": {
        "bg":              "#261820", "bg2":             "#322028", "bg3":             "#180e14",
        "accent":          "#cc5577", "accent2":         "#ee7799", "text":            "#ffeef4",
        "text2":           "#cc8899", "border":          "#5a2a38", "border_acc":      "#cc5577",
        "btn_hover":       "#401828", "btn_pressed":     "#502030", "chunk":           "#cc5577",
        "view_bg":         "#1a1016", "view_border":     "#cc5577", "toolbar_bg":      "#1a1016",
        "group_title":     "#ee7799", "scroll_bg":       "#261820", "scroll_handle":   "#cc5577",
        "is_dark":         True,      "label":           "🌸 Тёмный + розовый акцент",
    },
    "dark_purple": {
        "bg":              "#1e1528", "bg2":             "#271c34", "bg3":             "#130d1a",
        "accent":          "#8844cc", "accent2":         "#aa66ee", "text":            "#f0eaff",
        "text2":           "#aa88cc", "border":          "#3d246a", "border_acc":      "#8844cc",
        "btn_hover":       "#2e1850", "btn_pressed":     "#3e2870", "chunk":           "#8844cc",
        "view_bg":         "#16101e", "view_border":     "#8844cc", "toolbar_bg":      "#16101e",
        "group_title":     "#aa66ee", "scroll_bg":       "#1e1528", "scroll_handle":   "#8844cc",
        "is_dark":         True,      "label":           "🟣 Тёмный + фиолетовый акцент",
    },
    "dark_green": {
        "bg":              "#162018", "bg2":             "#1e2a20", "bg3":             "#0e1610",
        "accent":          "#3a9a55", "accent2":         "#55bb70", "text":            "#e8ffee",
        "text2":           "#88bb99", "border":          "#234830", "border_acc":      "#3a9a55",
        "btn_hover":       "#1a3020", "btn_pressed":     "#2a4030", "chunk":           "#3a9a55",
        "view_bg":         "#0e1810", "view_border":     "#3a9a55", "toolbar_bg":      "#0e1810",
        "group_title":     "#55bb70", "scroll_bg":       "#162018", "scroll_handle":   "#3a9a55",
        "is_dark":         True,      "label":           "🍃 Тёмный + зелёный акцент",
    },
    "dark_orange": {
        "bg":              "#241808", "bg2":             "#2e2010", "bg3":             "#180e00",
        "accent":          "#c87030", "accent2":         "#e89050", "text":            "#fff0e0",
        "text2":           "#ccaa88", "border":          "#5a2c10", "border_acc":      "#c87030",
        "btn_hover":       "#3a1c08", "btn_pressed":     "#4a2c10", "chunk":           "#c87030",
        "view_bg":         "#180e04", "view_border":     "#c87030", "toolbar_bg":      "#180e04",
        "group_title":     "#e89050", "scroll_bg":       "#241808", "scroll_handle":   "#c87030",
        "is_dark":         True,      "label":           "🟠 Тёмный + оранжевый акцент",
    },
    "pasteel_pink": {
        "bg":              "#fce8ee", "bg2":             "#fad0da", "bg3":             "#fff0f4",
        "accent":          "#c05070", "accent2":         "#d87090", "text":            "#380d1a",
        "text2":           "#884060", "border":          "#e0a0b8", "border_acc":      "#c05070",
        "btn_hover":       "#f8c0cc", "btn_pressed":     "#f0aabb", "chunk":           "#c05070",
        "view_bg":         "#fff5f7", "view_border":     "#c05070", "toolbar_bg":      "#fad0d8",
        "group_title":     "#9a3050", "scroll_bg":       "#fce0e6", "scroll_handle":   "#d87090",
        "is_dark":         False,     "label":           "🌷 Пастельный розовый",
    },
    "pasteel_blue": {
        "bg":              "#dde8ff", "bg2":             "#c8daff", "bg3":             "#ecf3ff",
        "accent":          "#3a62b8", "accent2":         "#5580d0", "text":            "#0c1c48",
        "text2":           "#3050a0", "border":          "#88aadd", "border_acc":      "#3a62b8",
        "btn_hover":       "#b8ccff", "btn_pressed":     "#a8beff", "chunk":           "#3a62b8",
        "view_bg":         "#eef4ff", "view_border":     "#3a62b8", "toolbar_bg":      "#c8d8ff",
        "group_title":     "#2848a0", "scroll_bg":       "#d8e5ff", "scroll_handle":   "#5580d0",
        "is_dark":         False,     "label":           "💙 Пастельный синий",
    },
    "pasteel_purple": {
        "bg":              "#ece0ff", "bg2":             "#d8c5ff", "bg3":             "#f4eeff",
        "accent":          "#6030a8", "accent2":         "#8050c8", "text":            "#18063a",
        "text2":           "#5028a0", "border":          "#bba0e0", "border_acc":      "#6030a8",
        "btn_hover":       "#d0b8ff", "btn_pressed":     "#c0a8ff", "chunk":           "#6030a8",
        "view_bg":         "#f5f0ff", "view_border":     "#6030a8", "toolbar_bg":      "#d8c8ff",
        "group_title":     "#4818a0", "scroll_bg":       "#e4d8ff", "scroll_handle":   "#8050c8",
        "is_dark":         False,     "label":           "💜 Пастельный фиолетовый",
    },
}


def build_stylesheet(t: dict) -> str:
    """Собирает полный QSS из словаря цветов темы."""
    return f"""
        QWidget {{
            background-color: {t['bg']};
            color: {t['text']};
            font-size: 13px;
            selection-background-color: {t['accent']};
            selection-color: #ffffff;
        }}
        QMainWindow, QDialog {{
            background-color: {t['bg']};
        }}
        QToolBar {{
            background-color: {t['toolbar_bg']};
            border: none;
            border-bottom: 1px solid {t['border']};
            padding: 4px 6px;
            spacing: 6px;
        }}
        QToolBar QToolButton {{
            background-color: {t['bg2']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 5px;
            padding: 5px 14px;
            font-size: 13px;
        }}
        QToolBar QToolButton:hover {{
            background-color: {t['btn_hover']};
            border-color: {t['border_acc']};
            color: {t['text']};
        }}
        QToolBar QToolButton:pressed {{
            background-color: {t['btn_pressed']};
        }}
        QPushButton {{
            background-color: {t['bg2']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 5px;
            padding: 6px 14px;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {t['btn_hover']};
            border-color: {t['border_acc']};
        }}
        QPushButton:pressed {{
            background-color: {t['btn_pressed']};
        }}
        QPushButton:disabled {{
            color: {t['text2']};
            border-color: {t['border']};
            background-color: {t['bg']};
        }}
        QLineEdit, QPlainTextEdit {{
            background-color: {t['bg3']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 13px;
        }}
        QLineEdit:focus, QPlainTextEdit:focus {{
            border-color: {t['border_acc']};
        }}
        QGroupBox {{
            background-color: {t['bg']};
            color: {t['group_title']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 6px;
            font-weight: bold;
            font-size: 13px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {t['group_title']};
        }}
        QScrollArea {{
            background-color: {t['bg3']};
            border: 1px solid {t['border']};
            border-radius: 4px;
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: {t['bg3']};
        }}
        QScrollBar:vertical {{
            background: {t['scroll_bg']};
            width: 8px;
            margin: 0;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {t['scroll_handle']};
            border-radius: 4px;
            min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['border_acc']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QProgressBar {{
            background-color: {t['bg3']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            text-align: center;
            font-size: 11px;
        }}
        QProgressBar::chunk {{
            background-color: {t['chunk']};
            border-radius: 3px;
        }}
        QStatusBar {{
            background-color: {t['toolbar_bg']};
            color: {t['text2']};
            border-top: 1px solid {t['border']};
            font-size: 12px;
        }}
        QRadioButton {{
            color: {t['text']};
            background-color: transparent;
            padding: 5px 4px;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 14px;
            height: 14px;
            border: 2px solid {t['border_acc']};
            border-radius: 8px;
            background-color: {t['bg3']};
        }}
        QRadioButton::indicator:checked {{
            background-color: {t['accent']};
            border-color: {t['accent2']};
        }}
        QLabel#view_label {{
            background-color: {t['view_bg']};
            border: 2px solid {t['view_border']};
            border-radius: 8px;
            color: {t['text2']};
            font-size: 14px;
        }}
        QLabel#tags_label {{
            background-color: {t['bg2']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            padding: 6px 10px;
            color: {t['text2']};
            font-size: 12px;
        }}
        QLabel#file_info_label {{
            background-color: {t['bg2']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            padding: 4px 10px;
            color: {t['text']};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton#btn_search {{
            background-color: {t['accent']};
            color: #ffffff;
            border: 1px solid {t['border_acc']};
            font-weight: bold;
        }}
        QPushButton#btn_search:hover {{
            background-color: {t['accent2']};
        }}
        QWidget#thumb_container {{
            background-color: {t['bg3']};
            border: 1px solid {t['border']};
            border-radius: 6px;
        }}
        QWidget#thumb_container:hover {{
            border-color: {t['border_acc']};
        }}
        QPushButton#thumb_btn {{
            background-color: transparent;
            border: none;
        }}
        QLabel#thumb_label {{
            color: {t['text2']};
            font-size: 11px;
        }}
    """


# ======================== НАСТРОЙКИ ========================
SETTINGS_FILE = os.path.join(get_app_dir(), "settings.json")

def load_settings():
    default = {"root_path": "", "theme": "dark", "lang": "ru"}
    if not os.path.exists(SETTINGS_FILE):
        return default
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            base = default.copy()
            base.update(json.load(f))
            return base
    except:
        return default

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


# ======================== ОКНО НАСТРОЕК ========================
class SettingsDialog(QDialog):
    def __init__(self, current_theme, current_lang, parent=None):
        super().__init__(parent)
        self.parent_win = parent
        self.setWindowTitle("Настройки / Settings")
        self.setMinimumWidth(440)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Тема оформления
        theme_title = QLabel(LANG_TEXT[current_lang]["theme_selection_title"])
        theme_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 4px;")
        layout.addWidget(theme_title)

        self.theme_group = QButtonGroup(self)
        self.theme_buttons = {}

        order = [
            "pasteel_pink", "pasteel_blue", "pasteel_purple",
            "dark_blue", "dark_pink", "dark_purple",
            "dark_green", "dark_orange", "dark",
        ]
        for key in order:
            t = THEMES[key]
            row = QHBoxLayout()
            swatch = QFrame()
            swatch.setFixedSize(22, 22)
            swatch.setStyleSheet(f"background-color: {t['bg']}; border: 2px solid {t['border_acc']}; border-radius: 4px;")
            row.addWidget(swatch)

            rb = QRadioButton(t["label"])
            if key == current_theme:
                rb.setChecked(True)
            self.theme_group.addButton(rb)
            self.theme_buttons[key] = rb
            row.addWidget(rb)
            row.addStretch()
            layout.addLayout(row)

        layout.addSpacing(10)
        
        # Язык интерфейса
        lang_title = QLabel(LANG_TEXT[current_lang]["lang_selection_title"])
        lang_title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 4px;")
        layout.addWidget(lang_title)

        self.lang_group = QButtonGroup(self)
        self.rb_ru = QRadioButton("Русский (RU)")
        self.rb_en = QRadioButton("English (EN)")
        self.lang_group.addButton(self.rb_ru)
        self.lang_group.addButton(self.rb_en)

        if current_lang == "en":
            self.rb_en.setChecked(True)
        else:
            self.rb_ru.setChecked(True)

        lang_row = QHBoxLayout()
        lang_row.addWidget(self.rb_ru)
        lang_row.addWidget(self.rb_en)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        layout.addSpacing(12)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_theme(self):
        for key, rb in self.theme_buttons.items():
            if rb.isChecked():
                return key
        return "dark"

    def get_selected_lang(self):
        return "en" if self.rb_en.isChecked() else "ru"


# ======================== ПОТОК МАССОВОГО СКАЧИВАНИЯ ========================
class RuxxDownloadThread(QThread):
    status_msg = Signal(str, int, int)  # tag, current, total
    finished_count = Signal(int)

    def __init__(self, tags, exe_path, base_dir, api_data):
        super().__init__()
        self.tags = tags
        self.exe_path = exe_path
        self.base_dir = base_dir
        self.api_data = api_data # Сюда прилетает "ключ.id"
        self._soft_stop = False
        self.current_process = None

    def stop_softly(self): self._soft_stop = True
    def stop_forcefully(self):
        self._soft_stop = True
        if self.current_process: self.current_process.kill()

    def run(self):
        processed = 0
        total = len(self.tags)
        for idx, tag in enumerate(self.tags):
            if self._soft_stop: break
            self.status_msg.emit(tag, idx + 1, total)
            tag_dir = os.path.join(self.base_dir, "".join(c for c in tag if c not in r'\/<>|:'))
            os.makedirs(tag_dir, exist_ok=True)
            
            cmd = [self.exe_path, tag, "-module", "rx", "-path", tag_dir, "-threads", "8", "-include_parchi", "-timeout", "10", "-retries", "10", "-prefix", "-dump_tags", "-dump_comments", "-dump_hashes", "-append_info", "-warn_nonempty"]
            if self.api_data: cmd.extend(["-api_key", self.api_data])

            self.current_process = subprocess.Popen(cmd)
            self.current_process.wait()
            if self.current_process.returncode == 0: processed += 1
        self.finished_count.emit(processed)


# ======================== ОКНО МАССОВОГО СКАЧИВАНИЯ ========================
class RuxxDownloaderDialog(QDialog):
    def __init__(self, current_lang, parent=None):
        super().__init__(parent)
        self.lang = current_lang
        self.setWindowTitle(self.t("dl_title"))
        self.setMinimumSize(650, 700)
        self.dl_thread = None
        self.setup_ui()

    def t(self, key):
        return LANG_TEXT[self.lang].get(key, key)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(14, 14, 14, 14)

        # --- Теги ---
        layout.addWidget(QLabel(self.t("dl_tags_label")))
        self.tags_entry = QPlainTextEdit()
        self.tags_entry.setPlaceholderText(
            "tag1\ntag2\ntag3" if self.lang == "en" else "тег1\nтег2\nтег3"
        )
        self.tags_entry.setMinimumHeight(130)
        layout.addWidget(self.tags_entry)

        # --- Ruxx.exe ---
        layout.addWidget(QLabel(self.t("dl_exe_label")))
        exe_row = QHBoxLayout()
        self.exe_path_edit = QLineEdit(get_tool_path("Ruxx"))
        exe_row.addWidget(self.exe_path_edit)
        btn_browse_exe = QPushButton(self.t("dl_btn_browse"))
        btn_browse_exe.setMaximumWidth(110)
        btn_browse_exe.clicked.connect(self.browse_exe)
        exe_row.addWidget(btn_browse_exe)
        layout.addLayout(exe_row)

        # --- Папка сохранения ---
        layout.addWidget(QLabel(self.t("dl_out_label")))
        folder_row = QHBoxLayout()
        self.base_folder_edit = QLineEdit(get_app_dir())
        folder_row.addWidget(self.base_folder_edit)
        btn_browse_folder = QPushButton(self.t("dl_btn_browse"))
        btn_browse_folder.setMaximumWidth(110)
        btn_browse_folder.clicked.connect(self.browse_folder)
        folder_row.addWidget(btn_browse_folder)
        layout.addLayout(folder_row)

        # --- API ---
        layout.addWidget(QLabel(self.t("dl_api_label")))
        api_row = QHBoxLayout()
        self.api_data_edit = QLineEdit()
        self.api_data_edit.setPlaceholderText(
            "api_key.user_id  (dot-separated)" if self.lang == "en"
            else "api_ключ.user_id  (через точку)"
        )
        api_row.addWidget(self.api_data_edit)
        btn_help = QPushButton(self.t("dl_btn_help"))
        btn_help.setMaximumWidth(130)
        btn_help.clicked.connect(self.show_help)
        api_row.addWidget(btn_help)
        layout.addLayout(api_row)

        layout.addSpacing(6)

        # --- Кнопки управления ---
        ctrl_row = QHBoxLayout()
        self.btn_start = QPushButton(self.t("dl_btn_start"))
        self.btn_start.clicked.connect(self.start_download)
        ctrl_row.addWidget(self.btn_start)

        self.btn_stop_soft = QPushButton(self.t("dl_btn_stop_soft"))
        self.btn_stop_soft.setEnabled(False)
        self.btn_stop_soft.clicked.connect(self.stop_download_softly)
        ctrl_row.addWidget(self.btn_stop_soft)

        self.btn_stop_hard = QPushButton(self.t("dl_btn_stop_hard"))
        self.btn_stop_hard.setEnabled(False)
        self.btn_stop_hard.clicked.connect(self.stop_download_forcefully)
        ctrl_row.addWidget(self.btn_stop_hard)
        layout.addLayout(ctrl_row)

        # --- Прогресс-бар и статус ---
        self.dl_progress = QProgressBar()
        self.dl_progress.setVisible(False)
        self.dl_progress.setFixedHeight(14)
        layout.addWidget(self.dl_progress)

        self.status_lbl = QLabel(self.t("dl_status_idle"))
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setObjectName("file_info_label")
        layout.addWidget(self.status_lbl)

        # --- Лог вывода ---
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(120)
        self.log_output.setPlaceholderText("Log..." if self.lang == "en" else "Лог выполнения...")
        layout.addWidget(self.log_output)

    def browse_exe(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Ruxx.exe", "", "Executable Files (*.exe);;All Files (*)")
        if file_path:
            self.exe_path_edit.setText(file_path)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.base_folder_edit.text())
        if folder:
            self.base_folder_edit.setText(folder)

    def show_help(self):
        QMessageBox.information(self, self.t("dl_help_title"), self.t("dl_help_content"))

    def start_download(self):
        # Получаем список тегов из текстового поля
        tags = [line.strip() for line in self.tags_entry.toPlainText().split('\n') if line.strip()]
        if not tags: 
            return

        # Получаем данные из полей
        exe_path = self.exe_path_edit.text().strip()
        base_dir = self.base_folder_edit.text().strip()
        
        # Берем данные API из ОДНОГО поля (которое ты назвал "ключ.user_id")
        api_data = self.api_data_edit.text().strip()

        # Блокируем кнопку запуска, чтобы не запустить дважды
        self.btn_start.setEnabled(False)

        # Создаем и запускаем поток
        self.dl_thread = RuxxDownloadThread(tags, exe_path, base_dir, api_data)
        self.dl_progress.setVisible(True)
        self.dl_progress.setMaximum(len(tags))
        self.dl_progress.setValue(0)

        def on_status(tag, current, total):
            self.dl_progress.setValue(current)
            msg = self.t("dl_status_progress").format(tag=tag, current=current, total=total)
            self.status_lbl.setText(msg)
            self.log_output.appendPlainText(msg)

        self.dl_thread.status_msg.connect(on_status)
        self.dl_thread.finished_count.connect(self.download_finished)
        self.dl_thread.finished.connect(lambda: (
            self.btn_start.setEnabled(True),
            self.btn_stop_soft.setEnabled(False),
            self.btn_stop_hard.setEnabled(False),
            self.dl_progress.setVisible(False),
        ))
        self.btn_stop_soft.setEnabled(True)
        self.btn_stop_hard.setEnabled(True)
        self.dl_thread.start()

    def stop_download_softly(self):
        if self.dl_thread and self.dl_thread.isRunning():
            self.dl_thread.stop_softly()
            self.status_lbl.setText(self.t("dl_status_soft_stopping"))
            self.btn_stop_soft.setEnabled(False)

    def stop_download_forcefully(self):
        if self.dl_thread and self.dl_thread.isRunning():
            self.dl_thread.stop_forcefully()

    def download_hard_stopped(self):
        self.status_lbl.setText(self.t("dl_status_hard_stopped"))
        self.reset_ui_state()
        QMessageBox.warning(self, "Stopped", self.t("dl_status_hard_stopped"))

    def download_finished(self, count):
        self.status_lbl.setText(self.t("dl_status_done").format(count=count))
        self.reset_ui_state()
        QMessageBox.information(self, "Success", self.t("dl_status_done").format(count=count))

    def reset_ui_state(self):
        self.btn_start.setEnabled(True)
        self.tags_entry.setEnabled(True)
        self.btn_stop_soft.setEnabled(False)
        self.btn_stop_hard.setEnabled(False)


# ======================== СКАНИРОВАНИЕ БАЗЫ ========================
class ScannerThread(QThread):
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(bool, str, int, int)

    def __init__(self, root_path, db_path):
        super().__init__()
        self.root_path = root_path
        self.db_path = db_path

    def find_media_file(self, folder, file_id):
        try:
            files = os.listdir(folder)
            for f in files:
                if f.startswith(f"rx_{file_id}"):
                    full_path = os.path.join(folder, f)
                    if os.path.isfile(full_path) and not f.endswith('.json'):
                        return full_path
            return None
        except:
            return None

    def run(self):
        try:
            json_files = []
            for dirpath, dirnames, filenames in os.walk(self.root_path):
                for f in filenames:
                    if '_!info_' in f and f.endswith('.json'):
                        json_files.append(os.path.join(dirpath, f))

            total_json = len(json_files)
            if total_json == 0:
                self.status.emit("No configuration JSON files found.")
                self.finished.emit(False, "No JSON", 0, 0)
                return

            self.status.emit(f"JSON data files found: {total_json}")
            self.progress.emit(0, total_json)

            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY, path TEXT, width INTEGER, height INTEGER, file_type TEXT, md5 TEXT, author TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS tags (file_id TEXT, tag TEXT, FOREIGN KEY(file_id) REFERENCES files(id))''')
            c.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_tags_file ON tags(file_id)')
            conn.commit()

            c.execute('DELETE FROM tags')
            c.execute('DELETE FROM files')
            conn.commit()

            total_files, total_tags = 0, 0

            for idx, json_path in enumerate(json_files):
                self.status.emit(f"Processing: {os.path.basename(json_path)}")
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                author_dir = os.path.basename(os.path.dirname(json_path))
                folder = os.path.dirname(json_path)

                for item in data:
                    file_id = item.get('id')
                    if not file_id:
                        continue
                    tags_str = item.get('tags', '')
                    width = item.get('width', 0)
                    height = item.get('height', 0)
                    md5 = item.get('md5', '')
                    tags_list = tags_str.split() if tags_str else []

                    media_file = self.find_media_file(folder, file_id)
                    if not media_file:
                        continue

                    ext_low = os.path.splitext(media_file)[1][1:].lower()
                    file_type = 'video' if ext_low in ['mp4', 'webm', 'avi', 'mov', 'mkv', 'gif'] else 'image'

                    rel_path = os.path.relpath(media_file, self.root_path)
                    c.execute(
                        'INSERT OR REPLACE INTO files (id, path, width, height, file_type, md5, author) VALUES (?,?,?,?,?,?,?)',
                        (file_id, rel_path, width, height, file_type, md5, author_dir)
                    )
                    total_files += 1
                    for tag in tags_list:
                        c.execute('INSERT INTO tags (file_id, tag) VALUES (?,?)', (file_id, tag))
                        total_tags += 1
                conn.commit()
                self.progress.emit(idx + 1, total_json)

            conn.close()
            self.finished.emit(True, "Finished", total_files, total_tags)
        except Exception as e:
            self.finished.emit(False, str(e), 0, 0)


# ======================== ГЕНЕРАЦИЯ КАДРОВ ДЛЯ ВИДЕО ========================
class VideoFramesGenerator(QThread):
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal()

    def __init__(self, db_path, root_path, frames_cache_dir, frames_per_video=20):
        super().__init__()
        self.db_path = db_path
        self.root_path = root_path
        self.frames_cache_dir = frames_cache_dir
        self.frames_per_video = frames_per_video

    def run(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, path FROM files WHERE file_type='video'")
        videos = c.fetchall()
        conn.close()
        total = len(videos)
        if total == 0:
            self.finished.emit()
            return

        for idx, (file_id, rel_path) in enumerate(videos):
            full_path = os.path.join(self.root_path, rel_path)
            if not os.path.exists(full_path):
                continue
            frames_folder = os.path.join(self.frames_cache_dir, hashlib.md5(full_path.encode()).hexdigest())
            if os.path.exists(frames_folder) and len(os.listdir(frames_folder)) >= self.frames_per_video:
                self.progress.emit(idx + 1, total)
                continue

            self.status.emit(f"Rendering Video Frames: {idx+1}/{total}")
            duration = self.get_video_duration(full_path) or 300
            step = duration / (self.frames_per_video + 1)
            os.makedirs(frames_folder, exist_ok=True)
            ffmpeg_path = get_tool_path("ffmpeg")

            for i in range(1, self.frames_per_video + 1):
                ts = max(0, min(duration, i * step + random.uniform(-step * 0.3, step * 0.3)))
                out_path = os.path.join(frames_folder, f"frame_{i:03d}.jpg")
                if os.path.exists(out_path):
                    continue
                cmd = [ffmpeg_path, "-i", full_path, "-ss", str(ts), "-vframes", "1", "-vf", "scale=320:-1", out_path, "-y"]
                subprocess.run(cmd, capture_output=True, timeout=10)
            self.progress.emit(idx + 1, total)
        self.finished.emit()

    def get_video_duration(self, video_path):
        ffprobe_path = get_tool_path("ffprobe")
        cmd = [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        try:
            return float(subprocess.check_output(cmd, timeout=10).decode().strip())
        except:
            return 0


# ======================== ПУЛ ТАСКОВ ДЛЯ ПРЕВЬЮ КАРТИНОК ========================
class ThumbnailSignals(QObject):
    finished = Signal(str, QPixmap, int)

class ImageThumbnailRunnable(QRunnable):
    def __init__(self, file_path, cache_dir, size=150, search_id=0):
        super().__init__()
        self.file_path = file_path
        self.cache_dir = cache_dir
        self.size = size
        self.search_id = search_id
        self.signals = ThumbnailSignals()

    def run(self):
        hash_name = hashlib.md5(self.file_path.encode()).hexdigest() + '.jpg'
        cache_path = os.path.join(self.cache_dir, hash_name)
        if os.path.exists(cache_path):
            pixmap = QPixmap(cache_path)
            if not pixmap.isNull():
                self.signals.finished.emit(self.file_path, pixmap, self.search_id)
                return
        try:
            img = Image.open(self.file_path)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.thumbnail((self.size, self.size), Image.Resampling.LANCZOS)
            os.makedirs(self.cache_dir, exist_ok=True)
            img.save(cache_path, 'JPEG', quality=85)
            self.signals.finished.emit(self.file_path, QPixmap(cache_path), self.search_id)
        except:
            self.signals.finished.emit(self.file_path, QPixmap(), self.search_id)


# ======================== ОКНО ПОЛНОЭКРАННОГО ПРОСМОТРА ========================
class ImageViewerWindow(QMainWindow):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(file_path))
        self.file_path = file_path
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)
        self.load_image()
        self.setWindowState(Qt.WindowMaximized)

    def load_image(self):
        pixmap = QPixmap(self.file_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        self.load_image()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


# ======================== СТАРТОВЫЙ ЗАСТАВОЧНЫЙ ЭКРАН ========================
class SplashWindow(QDialog):
    DONATE_URL = "https://www.donationalerts.com/r/cheburnet_club"

    def __init__(self, theme_name, lang, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setFixedSize(480, 320)
        t = THEMES.get(theme_name, THEMES["dark"])

        self.setStyleSheet(f"""
            QDialog {{ background-color: {t['bg']}; border: 2px solid {t['border_acc']}; border-radius: 14px; }}
            QLabel {{ color: {t['text']}; }}
            QPushButton {{ background-color: {t['bg2']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 8px 22px; }}
            QPushButton:hover {{ border-color: {t['border_acc']}; background-color: {t['btn_hover']}; }}
            QPushButton#btn_donate {{ background-color: {t['accent']}; font-weight: bold; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 30)

        title = QLabel("Local R34 by Martin")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {t['accent2']};")
        layout.addWidget(title)

        sub = QLabel("Special for CHEBURNET CLUB 2026")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"font-size: 14px; color: {t['text2']}; letter-spacing: 1px;")
        layout.addWidget(sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {t['border']}; margin: 15px 0;")
        layout.addWidget(sep)
        layout.addStretch()

        btn_row = QHBoxLayout()
        self.btn_donate = QPushButton("💸  Donation Alerts")
        self.btn_donate.setObjectName("btn_donate")
        self.btn_donate.clicked.connect(lambda: webbrowser.open(self.DONATE_URL))
        
        self.btn_launch = QPushButton("▶  " + ("Запустить" if lang == "ru" else "Launch"))
        self.btn_launch.clicked.connect(self.accept)

        btn_row.addWidget(self.btn_donate)
        btn_row.addWidget(self.btn_launch)
        layout.addLayout(btn_row)
        layout.addSpacing(10)

        ver = QLabel("v1.6  •  PySide6 UI Framework")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"font-size: 11px; color: {t['border_acc']};")
        layout.addWidget(ver)


# ======================== ГЛАВНОЕ ОКНО ПРОГРАММЫ ========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.lang = self.settings.get("lang", "ru")
        self.setWindowTitle(self.t("title"))
        self.setMinimumSize(1250, 750)

        self.root_path = self.settings.get("root_path", "")
        self.db_path = os.path.join(get_app_dir(), "data", "tags.db")
        self.all_tags = []
        self.current_results = []
        self.current_index = -1
        self.search_id = 0
        self.current_video_frames = []
        self.current_frame_index = 0

        self.setup_ui()
        self.apply_theme(self.settings.get("theme", "dark"))
        self.load_tags_for_autocomplete()
        if self.root_path and os.path.exists(self.root_path):
            self.label_path.setText(f"📂 {self.root_path}")

    def t(self, key):
        return LANG_TEXT[self.lang].get(key, key)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Тулбар
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.action_settings = QAction(self.t("toolbar_settings"), self)
        self.action_settings.triggered.connect(self.open_settings)
        toolbar.addAction(self.action_settings)
        toolbar.addSeparator()

        self.action_video = QAction(self.t("toolbar_video"), self)
        self.action_video.triggered.connect(self.generate_video_frames)
        toolbar.addAction(self.action_video)

        self.action_image = QAction(self.t("toolbar_image"), self)
        self.action_image.triggered.connect(self.generate_image_thumbnails)
        toolbar.addAction(self.action_image)
        toolbar.addSeparator()

        # Новая кнопка интеграции модуля скачивания
        self.action_download = QAction(self.t("toolbar_download"), self)
        self.action_download.triggered.connect(self.open_downloader)
        toolbar.addAction(self.action_download)

        # Левая часть
        left_panel = QWidget()
        left_panel.setMinimumWidth(520)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 4, 8)

        self.btn_select = QPushButton(self.t("btn_select_root"))
        self.btn_select.clicked.connect(self.select_root_folder)
        left_layout.addWidget(self.btn_select)

        self.label_path = QLabel(self.t("lbl_no_folder"))
        self.label_path.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.label_path)

        self.btn_scan = QPushButton(self.t("btn_scan_db"))
        self.btn_scan.setEnabled(bool(self.root_path))
        self.btn_scan.clicked.connect(self.start_scan)
        left_layout.addWidget(self.btn_scan)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(14)
        left_layout.addWidget(self.progress_bar)

        search_group = QGroupBox(self.t("group_search"))
        search_layout = QVBoxLayout(search_group)

        q_row = QHBoxLayout()
        self.search_query_edit = QLineEdit()
        self.search_query_edit.setPlaceholderText(self.t("edit_search_placeholder"))
        self.search_query_edit.returnPressed.connect(self.perform_search)
        self.btn_clear = QPushButton("✖")
        self.btn_clear.setMaximumWidth(30)
        self.btn_clear.clicked.connect(self.search_query_edit.clear)
        q_row.addWidget(self.search_query_edit)
        q_row.addWidget(self.btn_clear)
        search_layout.addLayout(q_row)

        add_row = QHBoxLayout()
        self.tag_adder_edit = QLineEdit()
        self.tag_adder_edit.setPlaceholderText(self.t("edit_tag_placeholder"))
        self.tag_adder_edit.returnPressed.connect(self.add_tag_to_query)
        self.btn_add_tag = QPushButton(self.t("btn_add"))
        self.btn_add_tag.clicked.connect(self.add_tag_to_query)
        add_row.addWidget(self.tag_adder_edit)
        add_row.addWidget(self.btn_add_tag)
        search_layout.addLayout(add_row)

        self.btn_search = QPushButton(self.t("btn_search"))
        self.btn_search.setObjectName("btn_search")
        self.btn_search.clicked.connect(self.perform_search)
        search_layout.addWidget(self.btn_search)
        left_layout.addWidget(search_group)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scroll_inner")
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        left_layout.addWidget(self.scroll_area)

        # Правая панель просмотра
        right_panel = QWidget()
        right_panel.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 8, 8, 8)

        self.view_label = QLabel(self.t("view_idle"))
        self.view_label.setObjectName("view_label")
        self.view_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.view_label, 1)

        self.file_info_label = QLabel("")
        self.file_info_label.setObjectName("file_info_label")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.file_info_label)

        self.tags_label = QLabel(self.t("tags_prefix"))
        self.tags_label.setObjectName("tags_label")
        self.tags_label.setWordWrap(True)
        self.tags_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        right_layout.addWidget(self.tags_label)

        nav_row = QHBoxLayout()
        self.btn_prev = QPushButton(self.t("btn_prev"))
        self.btn_prev.setEnabled(False)
        self.btn_prev.clicked.connect(self.show_previous)
        
        self.btn_fullscreen = QPushButton(self.t("btn_fullscreen"))
        self.btn_fullscreen.setEnabled(False)
        self.btn_fullscreen.clicked.connect(self.open_in_window)

        self.btn_save = QPushButton(self.t("btn_save"))
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_current_file)

        self.btn_next = QPushButton(self.t("btn_next"))
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.show_next)

        nav_row.addWidget(self.btn_prev)
        nav_row.addWidget(self.btn_fullscreen)
        nav_row.addWidget(self.btn_save)
        nav_row.addWidget(self.btn_next)
        right_layout.addLayout(nav_row)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([750, 450])
        main_layout.addWidget(splitter)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(self.t("status_ready"))

        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.next_video_frame)

    def apply_theme(self, theme_name):
        if theme_name not in THEMES: theme_name = "dark"
        self.settings["theme"] = theme_name
        save_settings(self.settings)
        QApplication.instance().setStyleSheet(build_stylesheet(THEMES[theme_name]))

    def open_settings(self):
        dialog = SettingsDialog(self.settings.get("theme", "dark"), self.lang, self)
        if dialog.exec():
            # Сохранение темы
            new_theme = dialog.get_selected_theme()
            if new_theme != self.settings.get("theme"):
                self.apply_theme(new_theme)
            
            # Сохранение языка
            new_lang = dialog.get_selected_lang()
            if new_lang != self.lang:
                self.settings["lang"] = new_lang
                save_settings(self.settings)
                QMessageBox.information(self, "Language / Язык", self.t("lang_restart_msg"))

    def open_downloader(self):
        downloader = RuxxDownloaderDialog(self.lang, self)
        downloader.exec()

    def select_root_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.root_path)
        if folder:
            self.root_path = folder
            self.settings["root_path"] = folder
            save_settings(self.settings)
            self.label_path.setText(f"📂 {folder}")
            self.btn_scan.setEnabled(True)

    def start_scan(self):
        if not self.root_path: return
        self.btn_scan.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.scanner = ScannerThread(self.root_path, self.db_path)
        self.scanner.progress.connect(lambda c, t: (self.progress_bar.setMaximum(t), self.progress_bar.setValue(c)))
        self.scanner.status.connect(self.statusbar.showMessage)
        self.scanner.finished.connect(self.scan_finished)
        self.scanner.start()

    def scan_finished(self, success, message, total_files, total_tags):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        if success:
            QMessageBox.information(self, "Database Updated", f"Files: {total_files}\nTags: {total_tags}")
            self.load_tags_for_autocomplete()

    def load_tags_for_autocomplete(self):
        if not os.path.exists(self.db_path): return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT DISTINCT tag FROM tags ORDER BY tag")
        self.all_tags = [row[0] for row in c.fetchall()]
        conn.close()
        
        completer = QCompleter()
        completer.setModel(QStringListModel(self.all_tags))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.tag_adder_edit.setCompleter(completer)
        self.statusbar.showMessage(self.t("status_loading_tags").format(count=len(self.all_tags)))

    def add_tag_to_query(self):
        tag = self.tag_adder_edit.text().strip()
        if tag:
            curr = self.search_query_edit.text().strip()
            self.search_query_edit.setText(f"{curr} {tag}".strip())
            self.tag_adder_edit.clear()

    def perform_search(self):
        if not os.path.exists(self.db_path): return
        raw_text = self.search_query_edit.text().strip()
        tags = [t.strip() for t in raw_text.split() if t.strip()]
        if not tags: return

        conds = " AND ".join(["EXISTS (SELECT 1 FROM tags WHERE file_id = files.id AND tag = ?)"] * len(tags))
        query = f"SELECT id, path, width, height, file_type, author FROM files WHERE {conds} ORDER BY author, id"
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, tags)
        rows = c.fetchall()
        conn.close()

        self.search_id += 1
        QThreadPool.globalInstance().clear()
        self.clear_grid()
        self.current_results = []

        for row in rows:
            f_id, r_path, w, h, f_type, author = row
            self.current_results.append({
                'id': f_id, 'path': os.path.join(self.root_path, r_path),
                'width': w, 'height': h, 'type': f_type, 'author': author
            })

        if not self.current_results:
            self.statusbar.showMessage(self.t("status_search_failed"))
            return

        self.statusbar.showMessage(self.t("status_searching").format(count=len(self.current_results)))
        self.load_thumbnails()

    def clear_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w: w.deleteLater()

    def load_thumbnails(self):
        cache_dir = os.path.join(get_app_dir(), "cache", "thumbnails", "pic")
        os.makedirs(cache_dir, exist_ok=True)
        sid = self.search_id

        for idx, item in enumerate(self.current_results):
            if item['type'] == 'image':
                runnable = ImageThumbnailRunnable(item['path'], cache_dir, size=150, search_id=sid)
                runnable.signals.finished.connect(self.add_thumbnail_to_grid)
                QThreadPool.globalInstance().start(runnable)
            else:
                v_folder = os.path.join(get_app_dir(), "cache", "video_frames", hashlib.md5(item['path'].encode()).hexdigest())
                f_frame = os.path.join(v_folder, "frame_001.jpg")
                pix = QPixmap(f_frame) if os.path.exists(f_frame) else QPixmap(150, 150)
                if os.path.exists(f_frame) is False: pix.fill(Qt.gray)
                self.add_thumbnail_to_grid(item['path'], pix, sid)

    def add_thumbnail_to_grid(self, file_path, pixmap, search_id):
        if search_id != self.search_id: return
        for idx, item in enumerate(self.current_results):
            if item['path'] == file_path:
                container = QWidget()
                container.setObjectName("thumb_container")
                vlay = QVBoxLayout(container)
                vlay.setContentsMargins(4, 4, 4, 4)

                btn = QPushButton()
                btn.setObjectName("thumb_btn")
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(140, 140))
                btn.setFixedSize(148, 148)
                btn.setProperty("index", idx)
                btn.clicked.connect(self.on_thumbnail_clicked)
                
                vlay.addWidget(btn, alignment=Qt.AlignCenter)
                lbl = QLabel(os.path.basename(file_path)[:20])
                lbl.setObjectName("thumb_label")
                lbl.setAlignment(Qt.AlignCenter)
                vlay.addWidget(lbl)

                self.grid_layout.addWidget(container, idx // 4, idx % 4)
                break

    def on_thumbnail_clicked(self):
        idx = self.sender().property("index")
        if idx is not None:
            self.current_index = idx
            self.display_current_file()

    def display_current_file(self):
        if self.current_index < 0 or self.current_index >= len(self.current_results): return
        item = self.current_results[self.current_index]
        # Тип файла и размер
        file_ext = os.path.splitext(item['path'])[1].lstrip('.').upper() or '?'
        try:
            file_size = os.path.getsize(item['path'])
            if file_size >= 1024 * 1024:
                size_str = f"{file_size / 1024 / 1024:.1f} MB"
            elif file_size >= 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} B"
        except OSError:
            size_str = "?"
        self.file_info_label.setText(
            f"👤 {item['author']}    🔢 {item['id']}    📄 {file_ext}    📦 {size_str}"
        )

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT tag FROM tags WHERE file_id = ?", (item['id'],))
        self.tags_label.setText(self.t("tags_prefix") + ", ".join([r[0] for r in c.fetchall()]))
        conn.close()

        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.current_results) - 1)
        self.btn_fullscreen.setEnabled(True)
        self.btn_save.setEnabled(True)

        self.stop_video_preview()

        if item['type'] == 'image':
            pix = QPixmap(item['path'])
            if not pix.isNull():
                self.view_label.setPixmap(pix.scaled(self.view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            v_folder = os.path.join(get_app_dir(), "cache", "video_frames", hashlib.md5(item['path'].encode()).hexdigest())
            if os.path.exists(v_folder):
                self.current_video_frames = sorted([os.path.join(v_folder, f) for f in os.listdir(v_folder) if f.endswith('.jpg')])
                if self.current_video_frames:
                    self.current_frame_index = 0
                    self.video_timer.start(500)

    def next_video_frame(self):
        if not self.current_video_frames: return
        self.current_frame_index = (self.current_frame_index + 1) % len(self.current_video_frames)
        pix = QPixmap(self.current_video_frames[self.current_frame_index])
        self.view_label.setPixmap(pix.scaled(self.view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def stop_video_preview(self):
        self.video_timer.stop()
        self.current_video_frames = []

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_file()

    def show_next(self):
        if self.current_index < len(self.current_results) - 1:
            self.current_index += 1
            self.display_current_file()

    def open_in_window(self):
        item = self.current_results[self.current_index]
        if item['type'] == 'image':
            self.viewer = ImageViewerWindow(item['path'], self)
            self.viewer.show()
        else:
            if sys.platform == 'win32': os.startfile(item['path'])
            else: subprocess.run(['xdg-open', item['path']])

    def save_current_file(self):
        src = self.current_results[self.current_index]['path']
        folder = QFileDialog.getExistingDirectory(self, "Save File To")
        if folder:
            shutil.copy2(src, os.path.join(folder, os.path.basename(src)))

    def generate_video_frames(self):
        if not self.root_path: return
        self.progress_bar.setVisible(True)
        self.action_video.setEnabled(False)
        cache = os.path.join(get_app_dir(), "cache", "video_frames")
        self.v_gen = VideoFramesGenerator(self.db_path, self.root_path, cache)
        self.v_gen.progress.connect(lambda c, t: (self.progress_bar.setMaximum(t), self.progress_bar.setValue(c)))
        self.v_gen.finished.connect(lambda: (self.progress_bar.setVisible(False), self.action_video.setEnabled(True)))
        self.v_gen.start()

    def generate_image_thumbnails(self):
        if not self.root_path: return
        cache = os.path.join(get_app_dir(), "cache", "thumbnails", "pic")
        conn = sqlite3.connect(self.db_path)
        images = [r[0] for r in conn.cursor().execute("SELECT path FROM files WHERE file_type='image'").fetchall()]
        conn.close()

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(images))
        self.action_image.setEnabled(False)

        for idx, r_path in enumerate(images):
            full = os.path.join(self.root_path, r_path)
            if os.path.exists(full):
                runnable = ImageThumbnailRunnable(full, cache, search_id=-1)
                runnable.run()
            self.progress_bar.setValue(idx + 1)
            QApplication.processEvents()
        self.progress_bar.setVisible(False)
        self.action_image.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    settings = load_settings()
    theme = settings.get("theme", "dark")
    lang = settings.get("lang", "ru")

    app.setStyleSheet(build_stylesheet(THEMES.get(theme, THEMES["dark"])))

    splash = SplashWindow(theme, lang)
    splash.exec()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
