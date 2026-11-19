"""亮色系登录 / 注册页。"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .. import icons, theme
from ..widgets import button, icon_button, label, soft_bg
from utils.utils import get_user_data, update_user_data


class BrandArt(QWidget):
    """左侧品牌插画：森林 + 无人机 + 数据光环。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        if self.isVisible():
            self.phase += 0.02
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor("#0E7C55"))
        bg.setColorAt(0.45, QColor("#12A66A"))
        bg.setColorAt(1.0, QColor("#7EDCB2"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRect(0, 0, w, h)

        # 光晕
        glow = QRadialGradient(QPointF(w * 0.78, h * 0.18), w * 0.6)
        glow.setColorAt(0, QColor(255, 255, 255, 90))
        glow.setColorAt(1, QColor(255, 255, 255, 0))
        p.setBrush(glow)
        p.drawRect(0, 0, w, h)

        # 同心数据环
        for i in range(4):
            rad = w * (0.22 + i * 0.075) + math.sin(self.phase + i) * 4
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 34 - i * 6), 1.2))
            p.drawEllipse(QPointF(w * 0.78, h * 0.20), rad, rad)

        # 山峦
        hills = [
            (0.58, QColor(255, 255, 255, 30)),
            (0.70, QColor(255, 255, 255, 44)),
            (0.82, QColor(255, 255, 255, 68)),
        ]
        for base, color in hills:
            path = QPainterPath(QPointF(0, h))
            path.lineTo(0, h * base)
            x = 0.0
            while x < w:
                path.quadTo(x + w * 0.08, h * (base - 0.09), x + w * 0.17, h * base)
                x += w * 0.17
            path.lineTo(w, h)
            path.closeSubpath()
            p.setBrush(color)
            p.drawPath(path)

        # 树剪影（三层针叶松）
        for i in range(11):
            x = w * (i + 0.5) / 11
            base = h * 0.94
            th = h * (0.15 + (i % 3) * 0.03)
            for layer in range(3):
                top = base - th * (1 - layer * 0.26)
                half = th * (0.16 + layer * 0.075)
                p.setBrush(QColor(9, 92, 62, 70 + layer * 34))
                tree = QPainterPath(QPointF(x, top))
                tree.cubicTo(x + half * 0.5, top + th * 0.10,
                             x + half * 0.9, top + th * 0.20,
                             x + half, top + th * 0.30)
                tree.lineTo(x - half, top + th * 0.30)
                tree.cubicTo(x - half * 0.9, top + th * 0.20,
                             x - half * 0.5, top + th * 0.10,
                             x, top)
                p.drawPath(tree)

        # 无人机
        ux, uy = w * 0.78 + math.sin(self.phase) * 8, h * 0.20 + math.cos(self.phase * 0.8) * 5
        p.setBrush(QColor(255, 255, 255, 235))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(ux - 13, uy - 8, 26, 16), 5, 5)
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            p.setPen(QPen(QColor(255, 255, 255, 200), 1.6))
            p.drawLine(QPointF(ux + dx * 10, uy + dy * 6), QPointF(ux + dx * 22, uy + dy * 14))
            p.setBrush(QColor(255, 255, 255, 170))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(ux + dx * 23, uy + dy * 15), 6, 3)

        # 扫描锥
        cone = QPainterPath(QPointF(ux, uy + 8))
        cone.lineTo(ux - w * 0.20, h)
        cone.lineTo(ux + w * 0.20, h)
        cone.closeSubpath()
        grad = QLinearGradient(ux, uy, ux, h)
        grad.setColorAt(0, QColor(255, 255, 255, 32))
        grad.setColorAt(1, QColor(255, 255, 255, 0))
        p.setBrush(grad)
        p.drawPath(cone)

        # 网格纹理
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        for i in range(1, 10):
            p.drawLine(QPointF(0, h * i / 10), QPointF(w, h * i / 10))

        # ---------------- 文案 ----------------
        left = w * 0.10
        # 品牌徽标
        tile = QRectF(left, h * 0.062, 42, 42)
        p.setBrush(QColor(255, 255, 255, 46))
        p.setPen(QPen(QColor(255, 255, 255, 90), 1))
        p.drawRoundedRect(tile, 12, 12)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPixmap(QPointF(tile.center().x() - 12, tile.center().y() - 12),
                     icons.pixmap("leaf", "#FFFFFF", 24))
        p.setPen(QColor(255, 255, 255, 218))
        f = QFont(theme.FONT_FAMILY)
        f.setPixelSize(max(11, int(w * 0.028)))
        f.setWeight(QFont.Weight.DemiBold)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        p.setFont(f)
        p.drawText(QRectF(left + 54, h * 0.066, w * 0.8, 22), Qt.AlignmentFlag.AlignLeft, "FORESTGUARD AI")
        p.setPen(QColor(255, 255, 255, 150))
        f2 = QFont(theme.FONT_FAMILY)
        f2.setPixelSize(max(9, int(w * 0.021)))
        p.setFont(f2)
        p.drawText(QRectF(left + 54, h * 0.066 + 21, w * 0.8, 18), Qt.AlignmentFlag.AlignLeft,
                   "森林防火空地协同指挥平台")
        p.setPen(QColor(255, 255, 255, 218))
        f.setPixelSize(max(11, int(w * 0.028)))

        f = QFont(theme.FONT_FAMILY)
        f.setPixelSize(max(24, int(w * 0.085)))
        f.setWeight(QFont.Weight.Bold)
        p.setFont(f)
        p.setPen(QColor("#FFFFFF"))
        p.drawText(QRectF(left, h * 0.135, w * 0.85, h * 0.09),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "智护森林")

        f = QFont(theme.FONT_FAMILY)
        f.setPixelSize(max(12, int(w * 0.032)))
        p.setFont(f)
        p.setPen(QColor(255, 255, 255, 225))
        p.drawText(QRectF(left, h * 0.246, w * 0.80, 26),
                   Qt.AlignmentFlag.AlignLeft, "智能森林防火空地协同指挥系统")

        f.setPixelSize(max(10, int(w * 0.023)))
        p.setFont(f)
        p.setPen(QColor(255, 255, 255, 175))
        p.drawText(QRectF(left, h * 0.288, w * 0.76, h * 0.10),
                   Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                   "SLAM 自主导航 · 多机器人拍卖协作 · 贝叶斯火势推演\n"
                   "从「侦察—打击」闭环到一键处置的完整指挥链路")

        # 能力标签
        tags = ["自主导航", "多机协作", "火情分析", "人机交互"]
        f.setPixelSize(max(9, int(w * 0.022)))
        f.setWeight(QFont.Weight.DemiBold)
        p.setFont(f)
        x = left
        y = h * 0.455
        for tag in tags:
            tw = p.fontMetrics().horizontalAdvance(tag) + 20
            p.setPen(QPen(QColor(255, 255, 255, 80), 1))
            p.setBrush(QColor(255, 255, 255, 34))
            p.drawRoundedRect(QRectF(x, y, tw, 24), 12, 12)
            p.setPen(QColor(255, 255, 255, 232))
            p.drawText(QRectF(x, y, tw, 24), Qt.AlignmentFlag.AlignCenter, tag)
            x += tw + 8

        # 底部状态
        f.setPixelSize(max(9, int(w * 0.020)))
        f.setWeight(QFont.Weight.Normal)
        p.setFont(f)
        p.setPen(QColor(255, 255, 255, 170))
        p.drawText(QRectF(left, h - 42, w * 0.8, 20), Qt.AlignmentFlag.AlignLeft,
                   "系统版本 v2.0  ·  演示环境  ·  数据仅用于功能展示")
        p.end()


class LoginPage(QWidget):
    logged_in = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginPage")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧品牌区
        brand = QFrame()
        brand.setObjectName("BrandPane")
        brand_lay = QVBoxLayout(brand)
        brand_lay.setContentsMargins(0, 0, 0, 0)
        brand_lay.setSpacing(0)
        self.art = BrandArt()
        self.art.setMinimumWidth(360)
        brand_lay.addWidget(self.art, 1)
        # 插画上的文案用纯绘制实现（避免布局干扰）
        self.art.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(brand, 46)

        # 右侧表单区
        right = QFrame()
        right.setObjectName("LoginForm")
        right.setStyleSheet(f"#LoginForm {{ background:{theme.SURFACE}; }}")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(56, 30, 56, 26)
        right_lay.setSpacing(0)

        top = QHBoxLayout()
        top.addStretch(1)
        self.close_btn = icon_button("close", theme.MUTED, 32, 16, self._on_close)
        self.close_btn.setProperty("variant", "win")
        top.addWidget(self.close_btn)
        right_lay.addLayout(top)
        right_lay.addSpacing(10)

        mark = QHBoxLayout()
        mark.setSpacing(10)
        badge = QLabel()
        badge.setFixedSize(42, 42)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setPixmap(icons.pixmap("leaf", "#FFFFFF", 22))
        badge.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1CBB7C, stop:1 #0B8455);"
            "border-radius:13px;"
        )
        mark.addWidget(badge)
        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        title = QLabel("智护森林")
        title.setStyleSheet(f"font-size:20px; font-weight:700; color:{theme.TEXT};")
        name_col.addWidget(title)
        sub = QLabel("ForestGuard AI")
        sub.setStyleSheet(f"font-size:11px; color:{theme.MUTED}; letter-spacing:1px;")
        name_col.addWidget(sub)
        mark.addLayout(name_col)
        mark.addStretch(1)
        right_lay.addLayout(mark)
        right_lay.addSpacing(22)

        self.heading = QLabel("欢迎回来")
        self.heading.setStyleSheet(f"font-size:26px; font-weight:700; color:{theme.TEXT};")
        right_lay.addWidget(self.heading)
        self.subheading = QLabel("登录森林防火空地协同指挥平台")
        self.subheading.setStyleSheet(f"font-size:13px; color:{theme.MUTED};")
        right_lay.addWidget(self.subheading)
        right_lay.addSpacing(18)

        # 选项卡
        tabs = QHBoxLayout()
        tabs.setSpacing(6)
        tabs.setContentsMargins(0, 0, 0, 0)
        tab_wrap = QFrame()
        soft_bg(tab_wrap, theme.SURFACE_ALT, 10)
        tab_lay = QHBoxLayout(tab_wrap)
        tab_lay.setContentsMargins(4, 4, 4, 4)
        tab_lay.setSpacing(4)
        self.tab_login = QPushButton("账号登录")
        self.tab_register = QPushButton("创建账户")
        for i, btn in enumerate((self.tab_login, self.tab_register)):
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(34)
            btn.setStyleSheet(
                f"QPushButton {{ border:none; border-radius:8px; font-size:13px; font-weight:700;"
                f" color:{theme.MUTED}; background:transparent; }}"
                f"QPushButton:checked {{ background:{theme.SURFACE}; color:{theme.ACCENT_DARK}; }}"
            )
            tab_lay.addWidget(btn, 1)
        self.tab_login.setChecked(True)
        tabs.addWidget(tab_wrap, 1)
        right_lay.addLayout(tabs)
        right_lay.addSpacing(18)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_login_form())
        self.stack.addWidget(self._build_register_form())
        right_lay.addWidget(self.stack, 1)

        # 底部说明
        right_lay.addSpacing(8)
        foot = QHBoxLayout()
        tip = QLabel()
        tip.setText(
            f"<span style='color:{theme.MUTED};'>演示账号 </span>"
            f"<span style='color:{theme.ACCENT_DARK}; font-weight:700;'>admin</span>"
            f"<span style='color:{theme.MUTED};'> / </span>"
            f"<span style='color:{theme.ACCENT_DARK}; font-weight:700;'>admin</span>"
        )
        tip.setStyleSheet("font-size:12px;")
        foot.addWidget(tip)
        foot.addStretch(1)
        ver = QLabel("v2.0 · 演示环境")
        ver.setStyleSheet(f"font-size:11px; color:{theme.MUTED_LIGHT};")
        foot.addWidget(ver)
        right_lay.addLayout(foot)

        root.addWidget(right, 54)

        self.tab_login.clicked.connect(lambda: self._switch_page(0))
        self.tab_register.clicked.connect(lambda: self._switch_page(1))

    # ------------------------------------------------------------------
    def _on_close(self):
        self.window().close()

    def _field(self, placeholder: str, icon_name: str, password: bool = False) -> QLineEdit:
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setMinimumHeight(42)
        edit.addAction(icons.icon(icon_name, theme.MUTED_LIGHT, 16),
                       QLineEdit.ActionPosition.LeadingPosition)
        if password:
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        return edit

    def _form_label(self, text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(f"font-size:12px; font-weight:700; color:{theme.TEXT_SOFT};")
        return lb

    def _build_login_form(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        lay.addWidget(self._form_label("操作员账号"))
        self.account = self._field("请输入操作员账号", "user")
        lay.addWidget(self.account)

        lay.addWidget(self._form_label("登录密码"))
        self.password = self._field("请输入登录密码", "lock", password=True)
        lay.addWidget(self.password)

        row = QHBoxLayout()
        self.remember = QCheckBox("记住此终端")
        self.remember.setStyleSheet(
            "QCheckBox{font-size:12px; color:#5B6F63; spacing:7px;}"
            "QCheckBox::indicator{width:15px; height:15px; border:1.5px solid #CFDBD3;"
            " border-radius:4px; background:#FFFFFF;}"
            "QCheckBox::indicator:checked{background:#12A66A; border:1.5px solid #12A66A;}"
        )
        row.addWidget(self.remember)
        row.addStretch(1)
        forgot = QPushButton("忘记密码？")
        forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot.setStyleSheet(
            f"border:none; background:transparent; color:{theme.ACCENT_DARK}; font-size:12px;"
            f" font-weight:600; padding:0;"
        )
        forgot.clicked.connect(lambda: self._show_error("请联系系统管理员重置凭证（演示环境可自助注册）", "info"))
        row.addWidget(forgot)
        lay.addLayout(row)

        self.login_error = QLabel("")
        self.login_error.setWordWrap(True)
        self.login_error.setVisible(False)
        self.login_error.setStyleSheet(
            f"background:{theme.RED_SOFT}; color:{theme.RED}; border-radius:8px;"
            f"padding:8px 10px; font-size:12px;"
        )
        lay.addWidget(self.login_error)

        self.login_btn = button("进入指挥中心", "primary", "arrow-right", height=46, size=14,
                                on_click=self._do_login)
        lay.addWidget(self.login_btn)
        lay.addSpacing(6)
        hint = QLabel("登录即表示您已阅读并同意《林区数据使用规范》")
        hint.setStyleSheet(f"font-size:11px; color:{theme.MUTED_LIGHT};")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(hint)
        lay.addStretch(1)

        self.account.returnPressed.connect(lambda: self.password.setFocus())
        self.password.returnPressed.connect(self._do_login)
        return page

    def _build_register_form(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        lay.addWidget(self._form_label("操作员账号"))
        self.account_r = self._field("设置操作员账号", "user")
        lay.addWidget(self.account_r)
        lay.addWidget(self._form_label("登录密码"))
        self.password_r = self._field("设置登录密码", "lock", password=True)
        lay.addWidget(self.password_r)
        lay.addWidget(self._form_label("确认密码"))
        self.password_r2 = self._field("再次输入密码", "lock", password=True)
        lay.addWidget(self.password_r2)

        self.reg_error = QLabel("")
        self.reg_error.setWordWrap(True)
        self.reg_error.setVisible(False)
        self.reg_error.setStyleSheet(
            f"background:{theme.RED_SOFT}; color:{theme.RED}; border-radius:8px;"
            f"padding:8px 10px; font-size:12px;"
        )
        lay.addWidget(self.reg_error)

        self.register_btn = button("创建操作员账户", "primary", "plus", height=44, size=14,
                                   on_click=self._do_register)
        lay.addWidget(self.register_btn)
        lay.addStretch(1)
        self.password_r2.returnPressed.connect(self._do_register)
        return page

    # ------------------------------------------------------------------
    def _show_error(self, text: str, kind: str = "error"):
        target = self.reg_error if self.stack.currentIndex() == 1 else self.login_error
        color = theme.RED if kind == "error" else theme.BLUE
        bg = theme.RED_SOFT if kind == "error" else theme.BLUE_SOFT
        target.setStyleSheet(
            f"background:{bg}; color:{color}; border-radius:8px; padding:8px 10px; font-size:12px;"
        )
        target.setText(text)
        target.setVisible(True)

    def _clear_error(self):
        for w in (self.login_error, self.reg_error):
            w.setVisible(False)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        self.tab_login.setChecked(index == 0)
        self.tab_register.setChecked(index == 1)
        self.heading.setText("欢迎回来" if index == 0 else "创建操作员账户")
        self.subheading.setText("登录森林防火空地协同指挥平台" if index == 0
                                else "注册后可接入林区指挥终端与装备控制权限")
        self._clear_error()

    def _do_login(self):
        self._clear_error()
        account = self.account.text().strip()
        password = self.password.text().strip()
        if not account or not password:
            self._show_error("账号或密码不能为空")
            return
        users = get_user_data()
        if account not in users:
            self._show_error("未检索到该操作员账户，请先创建账户")
            return
        if users[account] != password:
            self._show_error("登录凭证有误，密码不正确")
            return
        self.login_btn.setText("正在接入指挥链路…")
        self.login_btn.setEnabled(False)
        QTimer.singleShot(380, lambda: self.logged_in.emit(account))

    def _do_register(self):
        self._clear_error()
        account = self.account_r.text().strip()
        password = self.password_r.text().strip()
        confirm = self.password_r2.text().strip()
        if not account or not password:
            self._show_error("账号或密码不能为空")
            return
        if len(password) < 3:
            self._show_error("密码长度至少 3 位")
            return
        if password != confirm:
            self._show_error("两次输入的密码不一致")
            return
        users = get_user_data()
        if account in users:
            self._show_error("该操作员账户已存在")
            return
        update_user_data(account, password)
        self._switch_page(0)
        self.account.setText(account)
        self.password.setText(password)
        self.password.setFocus()
        self._show_error("账户创建成功，请点击「进入指挥中心」", "info")
