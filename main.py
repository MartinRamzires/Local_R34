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
                               QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QStringListModel, QSize, QTimer, QRunnable, QThreadPool, QObject
from PySide6.QtGui import QPixmap, QIcon, QAction, QColor


# ======================== ПУТИ (работает и из .py и из .exe) ========================

def get_app_dir() -> str:
    """Папка рядом с exe (или папка скрипта при разработке)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_tool_path(name: str) -> str:
    """Ищет ffmpeg/ffprobe рядом с exe, потом в PATH."""
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


# ======================== ТЕМЫ ========================

THEMES = {
    "dark": {
        "bg":              "#2b2b2b",
        "bg2":             "#333333",
        "bg3":             "#1e1e1e",
        "accent":          "#757575",
        "accent2":         "#999999",
        "text":            "#f0f0f0",
        "text2":           "#aaaaaa",
        "border":          "#484848",
        "border_acc":      "#888888",
        "btn_hover":       "#404040",
        "btn_pressed":     "#555555",
        "chunk":           "#757575",
        "view_bg":         "#222222",
        "view_border":     "#555555",
        "toolbar_bg":      "#252525",
        "group_title":     "#bbbbbb",
        "scroll_bg":       "#2b2b2b",
        "scroll_handle":   "#555555",
        "is_dark":         True,
        "label":           "🌑 Тёмная (классическая)",
    },
    "dark_blue": {
        "bg":              "#1a1f30",
        "bg2":             "#222840",
        "bg3":             "#11162a",
        "accent":          "#4a80d0",
        "accent2":         "#6a9fe8",
        "text":            "#dde8ff",
        "text2":           "#8899cc",
        "border":          "#2a3a60",
        "border_acc":      "#4a80d0",
        "btn_hover":       "#283060",
        "btn_pressed":     "#384580",
        "chunk":           "#4a80d0",
        "view_bg":         "#141928",
        "view_border":     "#4a80d0",
        "toolbar_bg":      "#141928",
        "group_title":     "#6a9fe8",
        "scroll_bg":       "#1a1f30",
        "scroll_handle":   "#4a80d0",
        "is_dark":         True,
        "label":           "🔵 Тёмный + голубой акцент",
    },
    "dark_pink": {
        "bg":              "#261820",
        "bg2":             "#322028",
        "bg3":             "#180e14",
        "accent":          "#cc5577",
        "accent2":         "#ee7799",
        "text":            "#ffeef4",
        "text2":           "#cc8899",
        "border":          "#5a2a38",
        "border_acc":      "#cc5577",
        "btn_hover":       "#401828",
        "btn_pressed":     "#502030",
        "chunk":           "#cc5577",
        "view_bg":         "#1a1016",
        "view_border":     "#cc5577",
        "toolbar_bg":      "#1a1016",
        "group_title":     "#ee7799",
        "scroll_bg":       "#261820",
        "scroll_handle":   "#cc5577",
        "is_dark":         True,
        "label":           "🌸 Тёмный + розовый акцент",
    },
    "dark_purple": {
        "bg":              "#1e1528",
        "bg2":             "#271c34",
        "bg3":             "#130d1a",
        "accent":          "#8844cc",
        "accent2":         "#aa66ee",
        "text":            "#f0eaff",
        "text2":           "#aa88cc",
        "border":          "#3d246a",
        "border_acc":      "#8844cc",
        "btn_hover":       "#2e1850",
        "btn_pressed":     "#3e2870",
        "chunk":           "#8844cc",
        "view_bg":         "#16101e",
        "view_border":     "#8844cc",
        "toolbar_bg":      "#16101e",
        "group_title":     "#aa66ee",
        "scroll_bg":       "#1e1528",
        "scroll_handle":   "#8844cc",
        "is_dark":         True,
        "label":           "🟣 Тёмный + фиолетовый акцент",
    },
    "dark_green": {
        "bg":              "#162018",
        "bg2":             "#1e2a20",
        "bg3":             "#0e1610",
        "accent":          "#3a9a55",
        "accent2":         "#55bb70",
        "text":            "#e8ffee",
        "text2":           "#88bb99",
        "border":          "#234830",
        "border_acc":      "#3a9a55",
        "btn_hover":       "#1a3020",
        "btn_pressed":     "#2a4030",
        "chunk":           "#3a9a55",
        "view_bg":         "#0e1810",
        "view_border":     "#3a9a55",
        "toolbar_bg":      "#0e1810",
        "group_title":     "#55bb70",
        "scroll_bg":       "#162018",
        "scroll_handle":   "#3a9a55",
        "is_dark":         True,
        "label":           "🍃 Тёмный + зелёный акцент",
    },
    "dark_orange": {
        "bg":              "#241808",
        "bg2":             "#2e2010",
        "bg3":             "#180e00",
        "accent":          "#c87030",
        "accent2":         "#e89050",
        "text":            "#fff0e0",
        "text2":           "#ccaa88",
        "border":          "#5a2c10",
        "border_acc":      "#c87030",
        "btn_hover":       "#3a1c08",
        "btn_pressed":     "#4a2c10",
        "chunk":           "#c87030",
        "view_bg":         "#180e04",
        "view_border":     "#c87030",
        "toolbar_bg":      "#180e04",
        "group_title":     "#e89050",
        "scroll_bg":       "#241808",
        "scroll_handle":   "#c87030",
        "is_dark":         True,
        "label":           "🟠 Тёмный + оранжевый акцент",
    },
    "pasteel_pink": {
        "bg":              "#fce8ee",
        "bg2":             "#fad0da",
        "bg3":             "#fff0f4",
        "accent":          "#c05070",
        "accent2":         "#d87090",
        "text":            "#380d1a",
        "text2":           "#884060",
        "border":          "#e0a0b8",
        "border_acc":      "#c05070",
        "btn_hover":       "#f8c0cc",
        "btn_pressed":     "#f0aabb",
        "chunk":           "#c05070",
        "view_bg":         "#fff5f7",
        "view_border":     "#c05070",
        "toolbar_bg":      "#fad0d8",
        "group_title":     "#9a3050",
        "scroll_bg":       "#fce0e6",
        "scroll_handle":   "#d87090",
        "is_dark":         False,
        "label":           "🌷 Пастельный розовый",
    },
    "pasteel_blue": {
        "bg":              "#dde8ff",
        "bg2":             "#c8daff",
        "bg3":             "#ecf3ff",
        "accent":          "#3a62b8",
        "accent2":         "#5580d0",
        "text":            "#0c1c48",
        "text2":           "#3050a0",
        "border":          "#88aadd",
        "border_acc":      "#3a62b8",
        "btn_hover":       "#b8ccff",
        "btn_pressed":     "#a8beff",
        "chunk":           "#3a62b8",
        "view_bg":         "#eef4ff",
        "view_border":     "#3a62b8",
        "toolbar_bg":      "#c8d8ff",
        "group_title":     "#2848a0",
        "scroll_bg":       "#d8e5ff",
        "scroll_handle":   "#5580d0",
        "is_dark":         False,
        "label":           "💙 Пастельный синий",
    },
    "pasteel_purple": {
        "bg":              "#ece0ff",
        "bg2":             "#d8c5ff",
        "bg3":             "#f4eeff",
        "accent":          "#6030a8",
        "accent2":         "#8050c8",
        "text":            "#18063a",
        "text2":           "#5028a0",
        "border":          "#bba0e0",
        "border_acc":      "#6030a8",
        "btn_hover":       "#d0b8ff",
        "btn_pressed":     "#c0a8ff",
        "chunk":           "#6030a8",
        "view_bg":         "#f5f0ff",
        "view_border":     "#6030a8",
        "toolbar_bg":      "#d8c8ff",
        "group_title":     "#4818a0",
        "scroll_bg":       "#e4d8ff",
        "scroll_handle":   "#8050c8",
        "is_dark":         False,
        "label":           "💜 Пастельный фиолетовый",
    },
}


def build_stylesheet(t: dict) -> str:
    """Собирает полный QSS из словаря цветов темы."""
    return f"""
        /* === Базовые виджеты === */
        QWidget {{
            background-color: {t['bg']};
            color: {t['text']};
            font-size: 13px;
            selection-background-color: {t['accent']};
            selection-color: {"#ffffff" if t['is_dark'] else "#ffffff"};
        }}
        QMainWindow, QDialog {{
            background-color: {t['bg']};
        }}

        /* === Тулбар === */
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

        /* === Кнопки === */
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

        /* === Текстовые поля === */
        QLineEdit {{
            background-color: {t['bg3']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border-color: {t['border_acc']};
        }}
        QLineEdit:disabled {{
            color: {t['text2']};
            background-color: {t['bg']};
        }}

        /* === Группировка === */
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

        /* === Прокрутка === */
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
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {t['scroll_bg']};
            height: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {t['scroll_handle']};
            border-radius: 4px;
            min-width: 24px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {t['border_acc']};
        }}
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* === Прогресс === */
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

        /* === Статусбар === */
        QStatusBar {{
            background-color: {t['toolbar_bg']};
            color: {t['text2']};
            border-top: 1px solid {t['border']};
            font-size: 12px;
        }}

        /* === Метки === */
        QLabel {{
            background-color: transparent;
            color: {t['text']};
            border: none;
            padding: 0;
        }}

        /* === Сплиттер === */
        QSplitter::handle {{
            background-color: {t['border']};
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        /* === Диалоги === */
        QDialog {{
            background-color: {t['bg']};
        }}
        QMessageBox {{
            background-color: {t['bg']};
        }}
        QMessageBox QLabel {{
            color: {t['text']};
        }}

        /* === Радио-кнопки === */
        QRadioButton {{
            color: {t['text']};
            background-color: transparent;
            padding: 5px 4px;
            spacing: 8px;
            font-size: 13px;
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
        QRadioButton::indicator:hover {{
            border-color: {t['accent2']};
        }}

        /* === Именованные виджеты === */
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
        QLabel#label_path {{
            color: {t['text2']};
            font-size: 12px;
        }}
        QPushButton#btn_search {{
            background-color: {t['accent']};
            color: {"#ffffff"};
            border: 1px solid {t['border_acc']};
            font-weight: bold;
        }}
        QPushButton#btn_search:hover {{
            background-color: {t['accent2']};
        }}
        QPushButton#btn_scan {{
            background-color: {t['bg2']};
            color: {t['text']};
            border: 1px solid {t['border_acc']};
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
            padding: 0;
        }}
        QPushButton#thumb_btn:hover {{
            background-color: {t['btn_hover']};
        }}
        QLabel#thumb_label {{
            color: {t['text2']};
            font-size: 11px;
            background-color: transparent;
        }}
        QWidget#scroll_inner {{
            background-color: {t['bg3']};
        }}
    """


# ======================== НАСТРОЙКИ ========================
SETTINGS_FILE = "settings.json"

def load_settings():
    default = {"root_path": "", "theme": "dark"}
    if not os.path.exists(SETTINGS_FILE):
        return default
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


# ======================== ОКНО НАСТРОЕК ========================
class SettingsDialog(QDialog):
    def __init__(self, current_theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки — Тема оформления")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        title = QLabel("Выберите тему оформления:")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 4px;")
        layout.addWidget(title)

        self.theme_group = QButtonGroup(self)
        self.theme_buttons = {}

        # Порядок отображения тем
        order = [
            "pasteel_pink", "pasteel_blue", "pasteel_purple",
            "dark_blue", "dark_pink", "dark_purple",
            "dark_green", "dark_orange", "dark",
        ]
        for key in order:
            t = THEMES[key]
            row = QHBoxLayout()

            # Цветной квадрат-превью
            swatch = QFrame()
            swatch.setFixedSize(22, 22)
            swatch.setStyleSheet(
                f"background-color: {t['bg']};"
                f"border: 2px solid {t['border_acc']};"
                f"border-radius: 4px;"
            )
            row.addWidget(swatch)

            rb = QRadioButton(t["label"])
            if key == current_theme:
                rb.setChecked(True)
            self.theme_group.addButton(rb)
            self.theme_buttons[key] = rb
            row.addWidget(rb)
            row.addStretch()
            layout.addLayout(row)

        layout.addSpacing(8)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_theme(self):
        for key, rb in self.theme_buttons.items():
            if rb.isChecked():
                return key
        return "dark"


# ======================== СКАНИРОВАНИЕ ========================
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
        except Exception:
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
                self.status.emit("Не найдено JSON-файлов с тегами")
                self.finished.emit(False, "Нет JSON", 0, 0)
                return

            self.status.emit(f"Найдено JSON: {total_json}")
            self.progress.emit(0, total_json)

            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                path TEXT,
                width INTEGER,
                height INTEGER,
                file_type TEXT,
                md5 TEXT,
                author TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS tags (
                file_id TEXT,
                tag TEXT,
                FOREIGN KEY(file_id) REFERENCES files(id)
            )''')
            c.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_tags_file ON tags(file_id)')
            c.execute('''CREATE TABLE IF NOT EXISTS video_frames_status (
                file_id TEXT PRIMARY KEY,
                frames_count INTEGER,
                generated_at TEXT
            )''')
            conn.commit()

            c.execute('DELETE FROM tags')
            c.execute('DELETE FROM files')
            c.execute('DELETE FROM video_frames_status')
            conn.commit()

            total_files = 0
            total_tags = 0

            for idx, json_path in enumerate(json_files):
                self.status.emit(f"Обработка: {os.path.basename(json_path)}")
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
                    if ext_low in ['mp4', 'webm', 'avi', 'mov', 'mkv', 'gif']:
                        file_type = 'video'
                    else:
                        file_type = 'image'

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
            self.status.emit("Сканирование завершено")
            self.finished.emit(True, f"Обработано JSON: {total_json}", total_files, total_tags)
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
            self.status.emit("Нет видео в базе")
            self.finished.emit()
            return
        self.status.emit(f"Генерация кадров для видео (0/{total})...")
        for idx, (file_id, rel_path) in enumerate(videos):
            full_path = os.path.join(self.root_path, rel_path)
            if not os.path.exists(full_path):
                continue
            frames_folder = self.get_frames_folder(full_path)
            if os.path.exists(frames_folder) and len(os.listdir(frames_folder)) >= self.frames_per_video:
                self.progress.emit(idx + 1, total)
                continue
            self.status.emit(f"Обработка: {os.path.basename(full_path)} ({idx+1}/{total})")
            duration = self.get_video_duration(full_path)
            if duration <= 0:
                duration = 300
            timestamps = []
            step = duration / (self.frames_per_video + 1)
            for i in range(1, self.frames_per_video + 1):
                t = i * step + random.uniform(-step * 0.3, step * 0.3)
                t = max(0, min(duration, t))
                timestamps.append(t)
            os.makedirs(frames_folder, exist_ok=True)
            ffmpeg_path = get_tool_path("ffmpeg")
            for i, ts in enumerate(timestamps):
                out_path = os.path.join(frames_folder, f"frame_{i+1:03d}.jpg")
                if os.path.exists(out_path):
                    continue
                cmd = [ffmpeg_path, "-i", full_path, "-ss", str(ts), "-vframes", "1", "-vf", "scale=320:-1", out_path, "-y"]
                subprocess.run(cmd, capture_output=True, timeout=10)
            self.progress.emit(idx + 1, total)
        self.status.emit("Генерация кадров для видео завершена")
        self.finished.emit()

    def get_frames_folder(self, video_path):
        hash_name = hashlib.md5(video_path.encode()).hexdigest()
        return os.path.join(self.frames_cache_dir, hash_name)

    def get_video_duration(self, video_path):
        ffprobe_path = get_tool_path("ffprobe")
        cmd = [ffprobe_path, "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        try:
            output = subprocess.check_output(cmd, timeout=10).decode().strip()
            return float(output)
        except:
            return 0


# ======================== ГЕНЕРАЦИЯ МИНИАТЮР ПОТОКОМ ПУЛА ========================
class ThumbnailSignals(QObject):
    finished = Signal(str, QPixmap, int)  # file_path, pixmap, search_id


class ImageThumbnailRunnable(QRunnable):
    def __init__(self, file_path, cache_dir, size=180, search_id=0):
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
            pixmap = QPixmap(cache_path)
            self.signals.finished.emit(self.file_path, pixmap, self.search_id)
        except Exception:
            self.signals.finished.emit(self.file_path, QPixmap(), self.search_id)


# ======================== ОКНО ПРОСМОТРА ========================
class ImageViewerWindow(QMainWindow):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Просмотр: {os.path.basename(file_path)}")
        self.file_path = file_path
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        self.load_image()
        self.setWindowState(Qt.WindowMaximized)

    def load_image(self):
        pixmap = QPixmap(self.file_path)
        if not pixmap.isNull():
            ws = self.size()
            scaled = pixmap.scaled(ws.width(), ws.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("Не удалось загрузить изображение")

    def resizeEvent(self, event):
        self.load_image()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


# ======================== ПРИВЕТСТВЕННОЕ ОКНО ========================
class SplashWindow(QDialog):
    """Стартовый экран с кнопкой доната."""
    DONATE_URL = "https://www.donationalerts.com/r/cheburnet_club"

    def __init__(self, theme_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Local R34 by Martin")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setFixedSize(480, 320)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        t = THEMES.get(theme_name, THEMES["dark"])

        # Фон через стиль
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {t['bg']};
                border: 2px solid {t['border_acc']};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {t['text']};
            }}
            QPushButton {{
                background-color: {t['bg2']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {t['btn_hover']};
                border-color: {t['border_acc']};
            }}
            QPushButton#btn_donate {{
                background-color: {t['accent']};
                color: #ffffff;
                border-color: {t['accent2']};
                font-weight: bold;
                font-size: 14px;
                padding: 10px 28px;
            }}
            QPushButton#btn_donate:hover {{
                background-color: {t['accent2']};
            }}
            QPushButton#btn_launch {{
                font-size: 13px;
                padding: 8px 22px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 28)
        root.setSpacing(0)

        # Заголовок
        title = QLabel("Local R34 by Martin")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 28px; font-weight: bold; letter-spacing: 1px;"
            f"color: {t['accent2']}; margin-bottom: 4px;"
        )
        root.addWidget(title)

        # Подзаголовок
        sub = QLabel("Special for CHEBURNET CLUB 2026")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(
            f"font-size: 15px; letter-spacing: 2px;"
            f"color: {t['text2']}; margin-bottom: 0px;"
        )
        root.addWidget(sub)

        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {t['border']}; margin: 18px 0 16px 0;")
        root.addWidget(sep)

        root.addStretch(1)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self.btn_donate = QPushButton("💸  Задонатить")
        self.btn_donate.setObjectName("btn_donate")
        self.btn_donate.setCursor(Qt.PointingHandCursor)
        self.btn_donate.clicked.connect(self.open_donate)
        btn_row.addWidget(self.btn_donate)

        self.btn_launch = QPushButton("▶  Запустить")
        self.btn_launch.setObjectName("btn_launch")
        self.btn_launch.setCursor(Qt.PointingHandCursor)
        self.btn_launch.clicked.connect(self.accept)
        btn_row.addWidget(self.btn_launch)

        root.addLayout(btn_row)

        root.addSpacing(14)

        # Версия
        ver = QLabel("v1.5  •  PySide6")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"font-size: 11px; color: {t['border_acc']};")
        root.addWidget(ver)

    def open_donate(self):
        webbrowser.open(self.DONATE_URL)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.accept()


# ======================== ГЛАВНОЕ ОКНО ========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.setWindowTitle("Local_R34 by Martin v1.5")
        self.setMinimumSize(1200, 700)

        self.root_path = self.settings.get("root_path", "")
        self.db_path = os.path.join(get_app_dir(), "data", "tags.db")
        self.all_tags = []
        self.tag_completer = None
        self.current_results = []
        self.current_index = -1
        self.search_id = 0  # Токен для отсечения старых запросов пула
        self.current_video_frames = []
        self.current_frame_index = 0

        self.setMenuBar(None)
        self.setup_ui()
        self.apply_theme(self.settings.get("theme", "dark"))
        self.load_tags_for_autocomplete()
        if self.root_path and os.path.exists(self.root_path):
            self.label_path.setText(f"📂 {self.root_path}")

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Тулбар ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        settings_action = QAction("⚙  Настройки", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

        toolbar.addSeparator()

        self.action_gen_video_frames = QAction("🎬  Видео-превью", self)
        self.action_gen_video_frames.triggered.connect(self.generate_video_frames)
        toolbar.addAction(self.action_gen_video_frames)

        self.action_gen_image_thumbs = QAction("🖼️  Превью картинок", self)
        self.action_gen_image_thumbs.triggered.connect(self.generate_image_thumbnails)
        toolbar.addAction(self.action_gen_image_thumbs)

        # --- Левая панель ---
        left_panel = QWidget()
        left_panel.setMinimumWidth(500)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 4, 8)
        left_layout.setSpacing(8)

        self.btn_select = QPushButton("📁  Выбрать корневую папку с работами")
        self.btn_select.clicked.connect(self.select_root_folder)
        left_layout.addWidget(self.btn_select)

        self.label_path = QLabel("Папка не выбрана")
        self.label_path.setObjectName("label_path")
        self.label_path.setWordWrap(True)
        self.label_path.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.label_path)

        self.btn_scan = QPushButton("🔄  Просканировать / Обновить базу")
        self.btn_scan.setObjectName("btn_scan")
        self.btn_scan.setEnabled(False)
        self.btn_scan.clicked.connect(self.start_scan)
        left_layout.addWidget(self.btn_scan)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)
        left_layout.addWidget(self.progress_bar)

        # Группа поиска
        search_group = QGroupBox("  🔍  Поисковый запрос")
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(6)

        query_row = QHBoxLayout()
        self.search_query_edit = QLineEdit()
        self.search_query_edit.setPlaceholderText("Введите теги через пробел...")
        self.search_query_edit.returnPressed.connect(self.perform_search)
        query_row.addWidget(self.search_query_edit)

        self.btn_clear_query = QPushButton("✖")
        self.btn_clear_query.setMaximumWidth(32)
        self.btn_clear_query.setToolTip("Очистить запрос")
        self.btn_clear_query.clicked.connect(self.clear_search_query)
        query_row.addWidget(self.btn_clear_query)
        search_layout.addLayout(query_row)

        add_layout = QHBoxLayout()
        add_lbl = QLabel("➕")
        add_lbl.setMaximumWidth(24)
        add_layout.addWidget(add_lbl)
        self.tag_adder_edit = QLineEdit()
        self.tag_adder_edit.setPlaceholderText("Добавить тег (с автодополнением)...")
        self.tag_adder_edit.setEnabled(False)
        self.tag_adder_edit.returnPressed.connect(self.add_tag_to_query)
        add_layout.addWidget(self.tag_adder_edit)
        self.btn_add_tag = QPushButton("Добавить")
        self.btn_add_tag.setEnabled(False)
        self.btn_add_tag.clicked.connect(self.add_tag_to_query)
        self.btn_add_tag.setMaximumWidth(90)
        add_layout.addWidget(self.btn_add_tag)
        search_layout.addLayout(add_layout)

        self.btn_search = QPushButton("🔍  Поиск")
        self.btn_search.setObjectName("btn_search")
        self.btn_search.clicked.connect(self.perform_search)
        search_layout.addWidget(self.btn_search)

        left_layout.addWidget(search_group)

        # Сетка миниатюр
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scroll_inner")
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_area.setWidget(self.scroll_widget)
        left_layout.addWidget(self.scroll_area)

        # --- Правая панель ---
        right_panel = QWidget()
        right_panel.setMinimumWidth(360)
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 8, 8, 8)
        right_layout.setSpacing(6)

        self.view_label = QLabel("Выберите файл для просмотра")
        self.view_label.setObjectName("view_label")
        self.view_label.setAlignment(Qt.AlignCenter)
        self.view_label.setMinimumHeight(300)
        self.view_label.setScaledContents(False)
        self.view_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.view_label, 1)

        self.file_info_label = QLabel("")
        self.file_info_label.setObjectName("file_info_label")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setWordWrap(True)
        right_layout.addWidget(self.file_info_label)

        self.tags_label = QLabel("Теги: ")
        self.tags_label.setObjectName("tags_label")
        self.tags_label.setWordWrap(True)
        self.tags_label.setAlignment(Qt.AlignLeft)
        self.tags_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        right_layout.addWidget(self.tags_label)

        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀  Пред.")
        self.btn_prev.setEnabled(False)
        self.btn_prev.clicked.connect(self.show_previous)
        nav_layout.addWidget(self.btn_prev)

        self.btn_fullscreen = QPushButton("⛶  Открыть в окне")
        self.btn_fullscreen.setEnabled(False)
        self.btn_fullscreen.clicked.connect(self.open_in_window)
        nav_layout.addWidget(self.btn_fullscreen)

        self.btn_save = QPushButton("💾  Сохранить в...")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_current_file)
        nav_layout.addWidget(self.btn_save)

        self.btn_next = QPushButton("След. ▶")
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.show_next)
        nav_layout.addWidget(self.btn_next)
        right_layout.addLayout(nav_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Готов")

        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.next_video_frame)

    # ======================== ТЕМЫ ========================
    def apply_theme(self, theme_name: str):
        if theme_name not in THEMES:
            theme_name = "dark"
        self.settings["theme"] = theme_name
        save_settings(self.settings)
        t = THEMES[theme_name]
        QApplication.instance().setStyleSheet(build_stylesheet(t))

    def open_settings(self):
        dialog = SettingsDialog(self.settings.get("theme", "dark"), self)
        if dialog.exec():
            new_theme = dialog.get_selected_theme()
            if new_theme != self.settings.get("theme"):
                self.apply_theme(new_theme)

    # ======================== ПАПКА И СКАНИРОВАНИЕ ========================
    def select_root_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите корневую папку с работами авторов",
            self.root_path if self.root_path else "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.root_path = folder
            self.settings["root_path"] = folder
            save_settings(self.settings)
            self.label_path.setText(f"📂 {folder}")
            self.btn_scan.setEnabled(True)
            self.statusbar.showMessage("Готов к сканированию. Нажмите 'Просканировать'")
        else:
            self.statusbar.showMessage("Выбор папки отменён")

    def start_scan(self):
        if not self.root_path:
            return
        self.btn_scan.setEnabled(False)
        self.btn_select.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.db_path = os.path.join(get_app_dir(), "data", "tags.db")
        self.scanner = ScannerThread(self.root_path, self.db_path)
        self.scanner.progress.connect(self.update_progress)
        self.scanner.status.connect(self.statusbar.showMessage)
        self.scanner.finished.connect(self.scan_finished)
        self.scanner.start()

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def scan_finished(self, success, message, total_files, total_tags):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.btn_select.setEnabled(True)
        if success:
            QMessageBox.information(self, "Готово",
                f"{message}\nФайлов добавлено: {total_files}\nТегов добавлено: {total_tags}")
            self.load_tags_for_autocomplete()
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить сканирование:\n{message}")

    # ======================== ТЕГИ И ПОИСК ========================
    def load_tags_for_autocomplete(self):
        if not self.db_path or not os.path.exists(self.db_path):
            self.statusbar.showMessage("База данных не найдена")
            return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT DISTINCT tag FROM tags ORDER BY tag")
        rows = c.fetchall()
        conn.close()
        self.all_tags = [row[0] for row in rows]
        if not self.all_tags:
            self.statusbar.showMessage("В базе нет тегов. Проверьте, что файлы найдены.")
            return
        model = QStringListModel(self.all_tags)
        self.tag_completer = QCompleter()
        self.tag_completer.setModel(model)
        self.tag_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.tag_completer.setFilterMode(Qt.MatchContains)
        self.tag_adder_edit.setCompleter(self.tag_completer)
        self.tag_adder_edit.setEnabled(True)
        self.btn_add_tag.setEnabled(True)
        self.statusbar.showMessage(f"Загружено {len(self.all_tags)} уникальных тегов")

    def add_tag_to_query(self):
        tag = self.tag_adder_edit.text().strip()
        if not tag:
            return
        tag = tag.split()[0]
        current_query = self.search_query_edit.text().strip()
        self.search_query_edit.setText((current_query + " " + tag).strip())
        self.tag_adder_edit.clear()
        self.tag_adder_edit.setFocus()

    def clear_search_query(self):
        self.search_query_edit.clear()
        self.search_query_edit.setFocus()

    def perform_search(self):
        if not self.db_path or not os.path.exists(self.db_path):
            QMessageBox.warning(self, "Нет базы", "Сначала выполните сканирование.")
            return
        raw_text = self.search_query_edit.text().strip()
        if not raw_text:
            QMessageBox.information(self, "Поиск", "Введите хотя бы один тег.")
            return
        tags = [t.strip() for t in raw_text.split() if t.strip()]
        if not tags:
            return

        conditions = " AND ".join(
            ["EXISTS (SELECT 1 FROM tags WHERE file_id = files.id AND tag = ?)"] * len(tags)
        )
        query = f"""
            SELECT files.id, files.path, files.width, files.height, files.file_type, files.author
            FROM files WHERE {conditions}
            ORDER BY files.author, files.id
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, tags)
        results = c.fetchall()
        conn.close()

        # Инкрементируем ID поиска и очищаем очередь пула от старых невыполненных задач
        self.search_id += 1
        QThreadPool.globalInstance().clear()

        self.clear_grid()
        self.current_results = []
        for row in results:
            file_id, rel_path, w, h, ftype, author = row
            full_path = os.path.join(self.root_path, rel_path) if self.root_path else rel_path
            self.current_results.append({
                'id': file_id, 'path': full_path, 'width': w, 'height': h,
                'type': ftype, 'author': author, 'rel_path': rel_path
            })

        if not self.current_results:
            self.statusbar.showMessage("Поиск не дал результатов")
            self.view_label.setText("Выберите файл для просмотра")
            self.view_label.setPixmap(QPixmap())
            self.file_info_label.setText("")
            self.tags_label.setText("Теги: ")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            self.btn_fullscreen.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.current_index = -1
            self.stop_video_preview()
            return

        self.statusbar.showMessage(f"Найдено {len(self.current_results)} файлов. Загрузка миниатюр...")
        self.load_thumbnails()

    # ======================== МИНИАТЮРЫ ========================
    def clear_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_thumbnails(self):
        image_cache_dir = os.path.join(get_app_dir(), "cache", "thumbnails", "pic")
        os.makedirs(image_cache_dir, exist_ok=True)
        
        current_sid = self.search_id
        
        for idx, item in enumerate(self.current_results):
            file_path = item['path']
            if item['type'] == 'image':
                # Передаем задачу в глобальный пул потоков
                runnable = ImageThumbnailRunnable(file_path, image_cache_dir, size=150, search_id=current_sid)
                runnable.signals.finished.connect(self.add_thumbnail_to_grid)
                QThreadPool.globalInstance().start(runnable)
            else:
                frames_folder = self.get_video_frames_folder(file_path)
                first_frame = os.path.join(frames_folder, "frame_001.jpg") if os.path.exists(frames_folder) else None
                if first_frame and os.path.exists(first_frame):
                    pixmap = QPixmap(first_frame)
                else:
                    pixmap = QPixmap(150, 150)
                    pixmap.fill(Qt.gray)
                self.add_thumbnail_to_grid(file_path, pixmap, current_sid)

    def get_video_frames_folder(self, video_path):
        hash_name = hashlib.md5(video_path.encode()).hexdigest()
        return os.path.join(get_app_dir(), "cache", "video_frames", hash_name)

    def add_thumbnail_to_grid(self, file_path, pixmap, search_id):
        # Игнорируем сигналы, пришедшие от старых поисковых запросов
        if search_id != self.search_id:
            return
            
        for idx, item in enumerate(self.current_results):
            if item['path'] == file_path:
                # Контейнер с именем для стилизации
                container = QWidget()
                container.setObjectName("thumb_container")
                vlay = QVBoxLayout(container)
                vlay.setContentsMargins(4, 4, 4, 4)
                vlay.setSpacing(2)

                btn = QPushButton()
                btn.setObjectName("thumb_btn")
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(150, 150))
                btn.setFixedSize(158, 158)
                btn.setToolTip(
                    f"{item['author']} / {item['id']}\n"
                    f"{item['width']}x{item['height']}\n"
                    f"{os.path.basename(file_path)}"
                )
                btn.setProperty("index", idx)
                btn.clicked.connect(self.on_thumbnail_clicked)
                vlay.addWidget(btn, alignment=Qt.AlignCenter)

                lbl = QLabel(os.path.basename(file_path)[:25])
                lbl.setObjectName("thumb_label")
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setWordWrap(True)
                vlay.addWidget(lbl)

                row = idx // 4
                col = idx % 4
                self.grid_layout.addWidget(container, row, col)
                break

    def on_thumbnail_clicked(self):
        btn = self.sender()
        idx = btn.property("index")
        if idx is not None:
            self.current_index = idx
            self.display_current_file()

    # ======================== ПРОСМОТР ========================
    def display_current_file(self):
        if self.current_index < 0 or self.current_index >= len(self.current_results):
            return
        item = self.current_results[self.current_index]
        file_path = item['path']
        file_type = item['type']
        self.file_info_label.setText(
            f"{item['author']} / {item['id']}  |  "
            f"{item['width']}x{item['height']}  |  "
            f"{os.path.basename(file_path)}"
        )

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT tag FROM tags WHERE file_id = ?", (item['id'],))
        tags = [row[0] for row in c.fetchall()]
        conn.close()
        self.tags_label.setText("Теги: " + ", ".join(tags))

        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.current_results) - 1)
        self.btn_fullscreen.setEnabled(True)
        self.btn_save.setEnabled(True)

        self.stop_video_preview()

        if file_type == 'image':
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                target_size = self.view_label.size()
                if target_size.width() > 5 and target_size.height() > 5:
                    scaled = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.view_label.setPixmap(scaled)
                else:
                    self.view_label.setPixmap(pixmap)
            else:
                self.view_label.setText("Не удалось загрузить изображение")
                self.view_label.setPixmap(QPixmap())
        else:
            frames_folder = self.get_video_frames_folder(file_path)
            if os.path.exists(frames_folder):
                frames = sorted([
                    os.path.join(frames_folder, f)
                    for f in os.listdir(frames_folder)
                    if f.startswith('frame_') and f.endswith('.jpg')
                ])
                if frames:
                    self.current_video_frames = frames
                    self.current_frame_index = 0
                    self.view_label.setPixmap(
                        QPixmap(frames[0]).scaled(self.view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                    self.video_timer.start(500)
                else:
                    self.view_label.setText("Нет кадров. Нажмите «Видео-превью» на панели инструментов")
            else:
                self.view_label.setText("Нет кадров. Нажмите «Видео-превью» на панели инструментов")

    def next_video_frame(self):
        if not self.current_video_frames:
            self.video_timer.stop()
            return
        self.current_frame_index = (self.current_frame_index + 1) % len(self.current_video_frames)
        frame_path = self.current_video_frames[self.current_frame_index]
        pixmap = QPixmap(frame_path)
        if not pixmap.isNull():
            self.view_label.setPixmap(
                pixmap.scaled(self.view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

    def stop_video_preview(self):
        if self.video_timer.isActive():
            self.video_timer.stop()
        self.current_video_frames = []
        self.current_frame_index = 0

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_file()

    def show_next(self):
        if self.current_index < len(self.current_results) - 1:
            self.current_index += 1
            self.display_current_file()

    def open_in_window(self):
        if self.current_index < 0 or self.current_index >= len(self.current_results):
            return
        item = self.current_results[self.current_index]
        if item['type'] == 'image':
            viewer = ImageViewerWindow(item['path'], self)
            viewer.show()
        else:
            if sys.platform == 'win32':
                os.startfile(item['path'])
            elif sys.platform == 'darwin':
                subprocess.run(['open', item['path']])
            else:
                subprocess.run(['xdg-open', item['path']])

    def save_current_file(self):
        if self.current_index < 0 or self.current_index >= len(self.current_results):
            return
        item = self.current_results[self.current_index]
        src_path = item['path']
        if not os.path.exists(src_path):
            QMessageBox.warning(self, "Ошибка", "Исходный файл не найден.")
            return
        dest_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", "")
        if dest_dir:
            dest_path = os.path.join(dest_dir, os.path.basename(src_path))
            try:
                shutil.copy2(src_path, dest_path)
                self.statusbar.showMessage(f"Сохранено: {dest_path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось скопировать файл:\n{e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_index < 0:
            return
        item = self.current_results[self.current_index]
        if item['type'] == 'image':
            self.display_current_file()
        elif item['type'] == 'video' and self.current_video_frames:
            frame = QPixmap(self.current_video_frames[self.current_frame_index])
            if not frame.isNull():
                self.view_label.setPixmap(
                    frame.scaled(self.view_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

    # ======================== ГЕНЕРАЦИЯ ПРЕВЬЮ ========================
    def generate_video_frames(self):
        if not self.db_path or not os.path.exists(self.db_path):
            QMessageBox.warning(self, "Нет базы", "Сначала выполните сканирование.")
            return
        if not self.root_path:
            QMessageBox.warning(self, "Нет папки", "Укажите корневую папку.")
            return
        frames_cache_dir = os.path.join(get_app_dir(), "cache", "video_frames")
        os.makedirs(frames_cache_dir, exist_ok=True)
        self.video_gen = VideoFramesGenerator(self.db_path, self.root_path, frames_cache_dir, frames_per_video=20)
        self.video_gen.progress.connect(self.update_video_progress)
        self.video_gen.status.connect(self.statusbar.showMessage)
        self.video_gen.finished.connect(self.video_gen_finished)
        self.video_gen.start()
        self.progress_bar.setVisible(True)
        self.action_gen_video_frames.setEnabled(False)

    def update_video_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def video_gen_finished(self):
        self.progress_bar.setVisible(False)
        self.action_gen_video_frames.setEnabled(True)
        self.statusbar.showMessage("Генерация кадров для видео завершена")
        if self.current_results:
            self.load_thumbnails()

    def generate_image_thumbnails(self):
        if not self.db_path or not os.path.exists(self.db_path):
            QMessageBox.warning(self, "Нет базы", "Сначала выполните сканирование.")
            return
        if not self.root_path:
            QMessageBox.warning(self, "Нет папки", "Укажите корневую папку.")
            return
        thumb_dir = os.path.join(get_app_dir(), "cache", "thumbnails", "pic")
        os.makedirs(thumb_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT path FROM files WHERE file_type='image'")
        images = c.fetchall()
        conn.close()
        total = len(images)
        if total == 0:
            self.statusbar.showMessage("Нет изображений в базе")
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        self.action_gen_image_thumbs.setEnabled(False)
        for idx, (rel_path,) in enumerate(images):
            full_path = os.path.join(self.root_path, rel_path)
            if os.path.exists(full_path):
                # Запускаем в синхронном режиме, но прокручиваем очередь событий UI
                runnable = ImageThumbnailRunnable(full_path, thumb_dir, size=150, search_id=-1)
                runnable.run()
            self.progress_bar.setValue(idx + 1)
            self.statusbar.showMessage(f"Генерация миниатюр для изображений ({idx+1}/{total})...")
            QApplication.processEvents()  # Предотвращает фриз GUI
        self.progress_bar.setVisible(False)
        self.action_gen_image_thumbs.setEnabled(True)
        self.statusbar.showMessage("Генерация миниатюр для изображений завершена")
        if self.current_results:
            self.load_thumbnails()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Читаем тему ДО создания главного окна
    settings = load_settings()
    theme_name = settings.get("theme", "dark")

    # Применяем тему сразу — splash тоже будет стилизован
    t = THEMES.get(theme_name, THEMES["dark"])
    app.setStyleSheet(build_stylesheet(t))

    # Приветственное окно
    splash = SplashWindow(theme_name)
    splash.exec()   # блокирует до нажатия кнопки

    # Главное окно
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()