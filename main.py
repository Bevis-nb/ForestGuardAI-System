import os
import re
from datetime import datetime

# ==================== 1. 屏蔽 Chromium/WebEngine 底层网络报错 ====================
# 必须在初始化 QApplication 之前设置
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-webrtc --disable-logging --log-level=3"

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStyleFactory
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from utils.utils import get_user_data, update_user_data
from Gui.main_ui_ui import Ui_MainWindow
from utils.share import share_info
from control import Control

# ==================== 2. 深色科技风样式常量 ====================
STYLE_TAB_ACTIVE = """
    QPushButton {
        border: none;
        border-bottom: 3px solid #10b981;
        font: 700 18pt "Microsoft YaHei UI";
        color: #10b981;
        padding-bottom: 6px;
        background-color: transparent;
    }
"""
STYLE_TAB_INACTIVE = """
    QPushButton {
        border: none;
        border-bottom: 3px solid transparent;
        font: 700 18pt "Microsoft YaHei UI";
        color: #64748b;
        padding-bottom: 6px;
        background-color: transparent;
    }
    QPushButton:hover {
        color: #94a3b8;
    }
"""

STYLE_NAV_ACTIVE = """
    QPushButton {
        border-radius: 12px;
        background-color: rgba(16, 185, 129, 0.18);
        border: 1px solid #10b981;
        color: #34d399;
        font: 700 11pt "Microsoft YaHei UI";
    }
"""
STYLE_NAV_INACTIVE = """
    QPushButton {
        border-radius: 12px;
        background-color: transparent;
        border: 1px solid transparent;
        color: #94a3b8;
        font: 500 11pt "Microsoft YaHei UI";
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: #f8fafc;
    }
"""

STYLE_MESSAGE_BOX = """
    QMessageBox {
        background-color: #1e293b;
    }
    /* 仅针对右侧提示文字的 QLabel 设置样式，不影响左侧图标 */
    QMessageBox QLabel#qt_msgbox_label {
        color: #f8fafc;
        font: 10pt "Microsoft YaHei UI";
        min-width: 180px;
        padding: 6px 12px 6px 4px;
    }
    /* 确保左侧图标 QLabel 保持紧凑宽度 */
    QMessageBox QLabel#qt_msgboxex_icon_label {
        min-width: 0px;
        padding-left: 8px;
    }
    QMessageBox QPushButton {
        background-color: #10b981;
        color: #ffffff;
        font: 700 10pt "Microsoft YaHei UI";
        border: none;
        border-radius: 6px;
        padding: 6px 20px;
        min-height: 20px;
        outline: none;
    }
    QMessageBox QPushButton:hover {
        background-color: #059669;
    }
    QMessageBox QPushButton:pressed {
        background-color: #047857;
    }

"""


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 隐藏默认窗口标题栏并设置透明背景
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()
        self.dragPosition = None

        # 顶栏控制按钮
        self.ui.min_btn.clicked.connect(self.showMinimized)
        self.ui.close_btn.clicked.connect(self.close)
        self.ui.max_btn.clicked.connect(self.change_window)

        # 替代原多线程：使用轻量稳定的 QTimer 刷新时钟
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)

        # 地图 URL 改变时自动刷新地址（在主线程中安全执行）
        self.ui.map_wed.urlChanged.connect(self.on_map_url_changed)

        self.init_page()

    def init_page(self):
        self.ui.topinfo.setText("智护森林 - 终端登录")
        self.ui.signin_section.clicked.connect(self.signin_up_page_btn)
        self.ui.signup_section.clicked.connect(self.signin_up_page_btn)

        self.ui.signin_section.setStyleSheet(STYLE_TAB_ACTIVE)
        self.ui.signup_section.setStyleSheet(STYLE_TAB_INACTIVE)
        self.ui.max_btn.hide()

        # 回车聚焦
        self.ui.account_edit.returnPressed.connect(self.ui.password_edit.setFocus)
        self.ui.password_edit.returnPressed.connect(self.ui.signin.click)

        self.ui.account_edit_2.returnPressed.connect(self.ui.password_edit_2.setFocus)
        self.ui.password_edit_2.returnPressed.connect(self.ui.truepassword_edit.setFocus)
        self.ui.truepassword_edit.returnPressed.connect(self.ui.signup.click)

        # 登录注册按钮
        self.ui.signin.clicked.connect(self.signin_up_page_btn)
        self.ui.signup.clicked.connect(self.signin_up_page_btn)

        # 功能导航栏
        self.ui.home.clicked.connect(self.guide_btn)
        self.ui.info.clicked.connect(self.guide_btn)
        self.ui.setting.clicked.connect(self.guide_btn)
        self.ui.more.clicked.connect(self.guide_btn)
        
        self.update_nav_styles(self.ui.home)
        self.gotostacke_2(0)

        # 业务按钮绑定
        self.ui.UAVFPV.clicked.connect(self.main_btn)
        self.ui.INFOWARN.clicked.connect(self.main_btn)

        for btn in [self.ui.gohome, self.ui.gohome_2, self.ui.gohome_3,
                    self.ui.gohome_6, self.ui.gohome_7, self.ui.gohome_8,
                    self.ui.byhand_control, self.ui.byhand_control_2, self.ui.byhand_control_3,
                    self.ui.byhand_control_6, self.ui.byhand_control_7, self.ui.byhand_control_8]:
            btn.clicked.connect(self.main_btn)

    def signin_up_page_btn(self):
        btn = self.sender()
        btname = btn.objectName()

        if btname == "signin_section":
            self.gotostacke_2(0)
            self.ui.topinfo.setText("智护森林 - 终端登录")
            self.ui.signin_section.setStyleSheet(STYLE_TAB_ACTIVE)
            self.ui.signup_section.setStyleSheet(STYLE_TAB_INACTIVE)

        elif btname == "signup_section":
            self.gotostacke_2(1)
            self.ui.topinfo.setText("智护森林 - 创建账户")
            self.ui.signin_section.setStyleSheet(STYLE_TAB_INACTIVE)
            self.ui.signup_section.setStyleSheet(STYLE_TAB_ACTIVE)

        elif btname == "signin":
            account = self.ui.account_edit.text().strip()
            password = self.ui.password_edit.text().strip()
            USERS = get_user_data()
            if not account or not password:
                self.show_warning("账号或密码不能为空！")
            else:
                if account in USERS.keys():
                    if USERS[account] == password:
                        self.show_success("身份验证通过，进入管控中心")
                        self.gotostacke(1)
                        self.gotostacke_3(0)
                        self.ui.topinfo.setText("智护森林 - 巡检调度平台")
                        self.ui.map_wed.setUrl("https://map.baidu.com/")
                        self.ui.max_btn.show()
                    else:
                        self.show_warning("登录凭证有误，密码不正确！")
                else:
                    self.show_warning("未检索到该操作员账户！")

        elif btname == "signup":
            account = self.ui.account_edit_2.text().strip()
            password = self.ui.password_edit_2.text().strip()
            truepassword = self.ui.truepassword_edit.text().strip()
            USERS = get_user_data()
            if not account or not password:
                self.show_warning("账号或密码不能为空！")
            else:
                if password == truepassword:
                    if account in USERS.keys():
                        self.show_warning("该操作员账户已存在！")
                    else:
                        update_user_data(account, password)
                        self.show_success("账户创建成功，请返回登录")
                        self.gotostacke_2(0)
                        self.ui.signin_section.setStyleSheet(STYLE_TAB_ACTIVE)
                        self.ui.signup_section.setStyleSheet(STYLE_TAB_INACTIVE)
                else:
                    self.show_warning("两次输入的密码不一致！")

    def update_nav_styles(self, active_btn):
        nav_buttons = [self.ui.home, self.ui.more, self.ui.info, self.ui.setting]
        for btn in nav_buttons:
            btn.setStyleSheet(STYLE_NAV_ACTIVE if btn == active_btn else STYLE_NAV_INACTIVE)

    def guide_btn(self):
        btn = self.sender()
        btname = btn.objectName()
        self.update_nav_styles(btn)

        if btname == "home":
            self.gotostacke_3(0)
            self.ui.topinfo.setText("智护森林 - 首页全景")
            self.clock_timer.stop()

        elif btname == "more":
            self.gotostacke_3(1)
            self.ui.topinfo.setText("智护森林 - 更多态势监控")
            self.update_clock()
            self.clock_timer.start(1000)  # 每秒刷新一次

        elif btname == "info":
            self.gotostacke_3(2)
            self.ui.topinfo.setText("智护森林 - 巡检详细参数")
            self.clock_timer.stop()

        elif btname == "setting":
            self.gotostacke_3(3)
            self.ui.topinfo.setText("智护森林 - 系统集成配置")
            self.clock_timer.stop()

    def main_btn(self):
        btn = self.sender()
        btname = btn.objectName()

        if btname == "UAVFPV":
            self.show_success("巡航编队指令已下发，无人机开始自主巡航")
        elif btname == "INFOWARN":
            self.show_success("林区热源预警信息已成功上传至指挥中心")
        elif "byhand_control" in btname:
            share_info.control_page = Control()
            share_info.control_page.show()
        elif "gohome" in btname:
            uav_mapping = {
                "6": "无人机 #04",
                "2": "无人机 #02",
                "3": "无人机 #03",
                "7": "无人机 #05",
                "8": "无人机 #07"
            }
            uav_name = "无人机 #01"
            for k, v in uav_mapping.items():
                if k in btname:
                    uav_name = v
                    break
            self.show_success(f"{uav_name} 收到返航指令，正在规划安全空域返航")

    # 定时器更新时间（主线程安全执行，无任何延迟开销）
    def update_clock(self):
        self.ui.time.setText(f"当前时间: {datetime.now().strftime('%H:%M:%S')}")
        self.ui.date.setText(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")

    # 地图 URL 发生变化时的安全槽函数
    def on_map_url_changed(self, qurl):
        url_str = qurl.toString()
        chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        chinese_chars = chinese_pattern.findall(url_str)
        position_str = ''.join(chinese_chars) if chinese_chars else "在线电子地图区域"
        self.ui.location_s.setText(f"当前坐标区: {position_str}")

    def gotostacke_2(self, index: int):
        self.ui.stackedWidget_2.setCurrentIndex(index)

    def gotostacke(self, index: int):
        self.ui.stackedWidget.setCurrentIndex(index)

    def gotostacke_3(self, index: int):
        self.ui.stackedWidget_3.setCurrentIndex(index)

    def show_success(self, text: str):
        msg = QMessageBox(self)
        msg.setStyleSheet(STYLE_MESSAGE_BOX)
        msg.setWindowTitle("系统提示")
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowIcon(QIcon("Gui/image/green_light.png"))
        msg.exec()

    def show_warning(self, text: str):
        msg = QMessageBox(self)
        msg.setStyleSheet(STYLE_MESSAGE_BOX)
        msg.setWindowTitle("安全预警")
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowIcon(QIcon("Gui/image/red_light.png"))
        msg.exec()

    # 鼠标拖动无边框窗口
    def mousePressEvent(self, event):
        if self.ui.frame.geometry().contains(event.position().toPoint()) and event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragPosition is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = None
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if self.ui.frame.geometry().contains(event.position().toPoint()):
            self.change_window()

    def change_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle(QStyleFactory.create("WindowsVista"))
    window = MainWindow()
    window.setWindowIcon(QIcon("logo.ico"))
    app.exec()