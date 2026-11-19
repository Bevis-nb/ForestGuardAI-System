"""全局亮色主题：配色、字体与 QSS。"""
from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication

# --------------------------------------------------------------------------
# 配色（森林薄荷亮色系）
# --------------------------------------------------------------------------
BG = "#F1F6F2"           # 页面底色
BG_DEEP = "#E8F1EA"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F7FBF8"
BORDER = "#E3ECE5"
BORDER_STRONG = "#CFDFD4"
TEXT = "#14251C"
TEXT_SOFT = "#3D5449"
MUTED = "#6F8579"
MUTED_LIGHT = "#9AAEA3"

ACCENT = "#12A66A"
ACCENT_DARK = "#0B8455"
ACCENT_LIGHT = "#43C68C"
ACCENT_SOFT = "#E6F6EE"
ACCENT_SOFT_2 = "#D5F0E2"

# 可切换的主题色（名称 -> 主色 / 深 / 浅 / 浅底 / 浅底2）
ACCENT_NAME = "森林绿"
PALETTES: dict[str, tuple[str, str, str, str, str]] = {
    "森林绿": ("#12A66A", "#0B8455", "#43C68C", "#E6F6EE", "#D5F0E2"),
    "天空蓝": ("#2F7DF6", "#1E5FCB", "#5B9BFF", "#E8F1FE", "#D6E6FE"),
    "琥珀橙": ("#EE9A2E", "#C1751A", "#F7B85C", "#FEF3E2", "#FBE6C6"),
    "薰衣草": ("#7C6BF2", "#5E4FD0", "#9C8FF7", "#EFECFE", "#E2DCFD"),
}

DENSITY = 1.0          # 1.0 标准 / 0.86 紧凑
ANIMATIONS = True      # 界面动效开关


def set_accent(name: str) -> str:
    """切换主色，并同步派生色与语义色。"""
    global ACCENT, ACCENT_DARK, ACCENT_LIGHT, ACCENT_SOFT, ACCENT_SOFT_2, ACCENT_NAME
    if name not in PALETTES:
        name = "森林绿"
    ACCENT, ACCENT_DARK, ACCENT_LIGHT, ACCENT_SOFT, ACCENT_SOFT_2 = PALETTES[name]
    ACCENT_NAME = name
    SEVERITY["success"] = (ACCENT, ACCENT_SOFT)
    return ACCENT


def set_density(compact: bool) -> None:
    global DENSITY
    DENSITY = 0.86 if compact else 1.0


def d(value: float, minimum: float = 0) -> int:
    """按当前信息密度缩放尺寸。"""
    return max(int(round(value * DENSITY)), int(minimum))

BLUE = "#2F7DF6"
BLUE_SOFT = "#E8F1FE"
AMBER = "#F2A93B"
AMBER_SOFT = "#FEF3E2"
RED = "#E5484D"
RED_SOFT = "#FDECEC"
PURPLE = "#7C6BF2"
PURPLE_SOFT = "#EFECFE"
CYAN = "#18AEC4"
CYAN_SOFT = "#E4F7FA"

SEVERITY = {
    "critical": (RED, RED_SOFT),
    "warning": (AMBER, AMBER_SOFT),
    "info": (BLUE, BLUE_SOFT),
    "success": (ACCENT, ACCENT_SOFT),
    "purple": (PURPLE, PURPLE_SOFT),
}

FONT_CANDIDATES = [
    "Microsoft YaHei UI",
    "Microsoft YaHei",
    "PingFang SC",
    "Source Han Sans SC",
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "WenQuanYi Micro Hei",
    "HarmonyOS Sans SC",
    "Segoe UI",
    "DejaVu Sans",
]

FONT_FAMILY = "Microsoft YaHei UI"
MONO_FAMILY = "Consolas"


def resolve_fonts() -> str:
    """挑选系统中可用的中文字体，返回最终使用的字体族。"""
    global FONT_FAMILY, MONO_FAMILY
    families = set(QFontDatabase.families())
    for name in FONT_CANDIDATES:
        if name in families:
            FONT_FAMILY = name
            break
    for name in ("Consolas", "JetBrains Mono", "Cascadia Mono", "DejaVu Sans Mono", "Courier New"):
        if name in families:
            MONO_FAMILY = name
            break
    return FONT_FAMILY


FONT_STACK = (
    '"Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", "Source Han Sans SC", '
    '"Noto Sans CJK SC", "Noto Sans SC", "Segoe UI", sans-serif'
)


def build_qss(fam: str = FONT_FAMILY, mono: str = MONO_FAMILY) -> str:
    """生成全局样式表。"""
    return f"""
* {{
    outline: none;
}}
QWidget {{
    font-family: {FONT_STACK};
    font-size: 13px;
    color: {TEXT};
}}
QMainWindow, QDialog {{
    background: {BG};
}}
QToolTip {{
    background: {TEXT};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ---------------- 卡片 ---------------- */
QFrame#Card, QFrame#Panel, QFrame#GlassCard {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
}}
QFrame#CardAlt {{
    background: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}
QFrame#HeroCard {{
    border: none;
    border-radius: 16px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #E9F8F0, stop:1 #F7FDFA);
}}
QFrame#Divider {{
    background: {BORDER};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

/* ---------------- 文字 ---------------- */
QLabel[role="h1"] {{ font-size: 24px; font-weight: 700; color: {TEXT}; }}
QLabel[role="h2"] {{ font-size: 18px; font-weight: 700; color: {TEXT}; }}
QLabel[role="h3"] {{ font-size: 15px; font-weight: 700; color: {TEXT}; }}
QLabel[role="cardTitle"] {{ font-size: 14px; font-weight: 700; color: {TEXT}; }}
QLabel[role="value"] {{ font-size: 26px; font-weight: 700; color: {TEXT}; }}
QLabel[role="valueSm"] {{ font-size: 19px; font-weight: 700; color: {TEXT}; }}
QLabel[role="muted"] {{ color: {MUTED}; font-size: 12px; }}
QLabel[role="caption"] {{ color: {MUTED}; font-size: 11px; }}
QLabel[role="accent"] {{ color: {ACCENT}; font-weight: 700; }}
QLabel[role="mono"] {{ font-family: "{mono}", monospace; font-size: 12px; color: {TEXT_SOFT}; }}

/* ---------------- 按钮 ---------------- */
QPushButton {{
    border: 1px solid {BORDER_STRONG};
    border-radius: 9px;
    background: {SURFACE};
    color: {TEXT_SOFT};
    padding: 7px 14px;
    font-weight: 600;
}}
QPushButton:hover {{ background: {SURFACE_ALT}; border-color: {ACCENT_LIGHT}; color: {ACCENT_DARK}; }}
QPushButton:pressed {{ background: {ACCENT_SOFT}; }}
QPushButton:disabled {{ color: {MUTED_LIGHT}; border-color: {BORDER}; background: {SURFACE_ALT}; }}

QPushButton[variant="primary"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1CBB7C, stop:1 {ACCENT});
    color: #FFFFFF; border: none; padding: 9px 18px;
}}
QPushButton[variant="primary"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #22C98A, stop:1 #10B273);
}}
QPushButton[variant="primary"]:pressed {{ background: {ACCENT_DARK}; }}
QPushButton[variant="primary"]:disabled {{ background: #B9DCCC; color: #F2FBF7; }}

QPushButton[variant="soft"] {{ background: {ACCENT_SOFT}; color: {ACCENT_DARK}; border: 1px solid {ACCENT_SOFT_2}; }}
QPushButton[variant="soft"]:hover {{ background: {ACCENT_SOFT_2}; }}
QPushButton[variant="ghost"] {{ background: transparent; border: 1px solid transparent; color: {MUTED}; }}
QPushButton[variant="ghost"]:hover {{ background: {SURFACE_ALT}; color: {TEXT}; }}
QPushButton[variant="danger"] {{ background: {RED}; color: #FFFFFF; border: none; }}
QPushButton[variant="danger"]:hover {{ background: #D93A3F; }}
QPushButton[variant="dangerSoft"] {{ background: {RED_SOFT}; color: {RED}; border: 1px solid #F8D3D4; }}
QPushButton[variant="dangerSoft"]:hover {{ background: #FBDDDD; }}
QPushButton[variant="blue"] {{ background: {BLUE_SOFT}; color: {BLUE}; border: 1px solid #D6E5FE; }}
QPushButton[variant="blue"]:hover {{ background: #DCEAFE; }}
QPushButton[variant="nav"] {{
    background: transparent; border: none; border-radius: 11px;
    color: {TEXT_SOFT}; text-align: left; padding: 0px 14px; font-weight: 600; font-size: 13.5px;
}}
QPushButton[variant="nav"]:hover {{ background: {ACCENT_SOFT}; color: {ACCENT_DARK}; }}
QPushButton[variant="nav"][active="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E3F7ED, stop:1 #F1FBF6);
    color: {ACCENT_DARK};
}}
QPushButton[variant="icon"] {{
    background: transparent; border: none; border-radius: 8px; padding: 4px;
}}
QPushButton[variant="icon"]:hover {{ background: {ACCENT_SOFT}; }}
QPushButton[variant="win"] {{
    background: transparent; border: none; border-radius: 8px; padding: 0;
    color: {MUTED};
}}
QPushButton[variant="win"]:hover {{ background: {BG_DEEP}; }}
QPushButton[variant="winClose"] {{ background: transparent; border: none; border-radius: 8px; padding: 0; }}
QPushButton[variant="winClose"]:hover {{ background: {RED}; }}

/* ---------------- 输入 ---------------- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateTimeEdit {{
    background: {SURFACE};
    border: 1px solid {BORDER_STRONG};
    border-radius: 9px;
    padding: 7px 11px;
    color: {TEXT};
    selection-background-color: {ACCENT_SOFT_2};
    selection-color: {ACCENT_DARK};
    min-height: 18px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QDateTimeEdit:focus {{
    border: 1px solid {ACCENT_LIGHT};
    background: #FCFEFD;
}}
QLineEdit[role="search"] {{ padding-left: 30px; background: {SURFACE_ALT}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px;
    selection-background-color: {ACCENT_SOFT}; selection-color: {ACCENT_DARK}; padding: 4px;
    outline: none;
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 0px; border: none; }}

QSlider::groove:horizontal {{ height: 5px; background: {BG_DEEP}; border-radius: 3px; }}
QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_LIGHT}, stop:1 {ACCENT});
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: #FFFFFF; border: 3px solid {ACCENT}; width: 12px; height: 12px;
    margin: -6px 0; border-radius: 9px;
}}
QSlider::handle:horizontal:hover {{ border-color: {ACCENT_DARK}; }}

QCheckBox, QRadioButton {{ color: {TEXT_SOFT}; spacing: 8px; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px; height: 16px; border: 1px solid {BORDER_STRONG}; background: {SURFACE};
}}
QCheckBox::indicator {{ border-radius: 5px; }}
QRadioButton::indicator {{ border-radius: 9px; }}
QCheckBox::indicator:checked {{
    background: {ACCENT}; border-color: {ACCENT};
    image: url(none);
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border: 4px solid #FFFFFF; }}

/* ---------------- 滚动 ---------------- */
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #CFDED5; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {ACCENT_LIGHT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #CFDED5; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}

/* ---------------- 列表 / 表格 ---------------- */
QListWidget, QTableWidget, QTreeWidget {{
    background: transparent; border: none; outline: none;
    gridline-color: {BORDER};
    selection-background-color: {ACCENT_SOFT};
    selection-color: {TEXT};
}}
QTableWidget::item {{ padding: 6px 8px; border-bottom: 1px solid {BORDER}; }}
QHeaderView::section {{
    background: transparent; border: none; border-bottom: 1px solid {BORDER};
    color: {MUTED}; font-weight: 600; font-size: 12px; padding: 8px;
}}
QTableCornerButton::section {{ background: transparent; border: none; }}
QListWidget::item {{ border-radius: 8px; padding: 6px; }}
QListWidget::item:selected {{ background: {ACCENT_SOFT}; color: {ACCENT_DARK}; }}

/* ---------------- 其他 ---------------- */
QProgressBar {{ background: {BG_DEEP}; border: none; border-radius: 4px; height: 8px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QMenu {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px; padding: 6px; }}
QMenu::item {{ padding: 7px 22px; border-radius: 6px; color: {TEXT_SOFT}; }}
QMenu::item:selected {{ background: {ACCENT_SOFT}; color: {ACCENT_DARK}; }}
QToolButton {{ border: none; background: transparent; }}
QSplitter::handle {{ background: transparent; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{
    background: transparent; color: {MUTED}; padding: 8px 16px; border-radius: 8px;
    font-weight: 600;
}}
QTabBar::tab:selected {{ background: {ACCENT_SOFT}; color: {ACCENT_DARK}; }}
QMessageBox {{ background: {SURFACE}; }}
QMessageBox QLabel {{ color: {TEXT}; }}
"""


def apply_theme(app: QApplication) -> None:
    """解析字体、设置调色板并挂载全局 QSS。"""
    fam = resolve_fonts()
    font = QFont(fam)
    font.setPixelSize(13)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window, QColor(BG))
    pal.setColor(QPalette.ColorRole.Base, QColor(SURFACE))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE_ALT))
    pal.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_SOFT))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor("#FFFFFF"))
    app.setPalette(pal)
    app.setStyleSheet(build_qss(fam))
