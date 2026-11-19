# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_uiuAPDNq.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)
from Gui import resourse_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(997, 705)
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"	background-color: #0f172a;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(945, 32))
        self.frame.setMaximumSize(QSize(16777215, 32))
        self.frame.setStyleSheet(u"#frame {\n"
"	border-top-left-radius: 10px;\n"
"	border-top-right-radius: 10px;\n"
"	background-color: #1e293b;\n"
"	border-bottom: 1px solid #334155;\n"
"}")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(12, 0, 12, 0)
        self.horizontalSpacer = QSpacerItem(423, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.topinfo = QLabel(self.frame)
        self.topinfo.setObjectName(u"topinfo")
        self.topinfo.setStyleSheet(u"QLabel {\n"
"	color: #e2e8f0;\n"
"	font: 700 10pt \"Microsoft YaHei UI\";\n"
"	letter-spacing: 1px;\n"
"}")

        self.horizontalLayout.addWidget(self.topinfo)

        self.horizontalSpacer_2 = QSpacerItem(383, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.min_btn = QPushButton(self.frame)
        self.min_btn.setObjectName(u"min_btn")
        self.min_btn.setMinimumSize(QSize(14, 14))
        self.min_btn.setMaximumSize(QSize(14, 14))
        self.min_btn.setStyleSheet(u"#min_btn {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}\n"
"#min_btn:hover {\n"
"	background-color: #34d399;\n"
"}\n"
"#min_btn:pressed {\n"
"	background-color: #059669;\n"
"}")

        self.horizontalLayout.addWidget(self.min_btn)

        self.max_btn = QPushButton(self.frame)
        self.max_btn.setObjectName(u"max_btn")
        self.max_btn.setMinimumSize(QSize(14, 14))
        self.max_btn.setMaximumSize(QSize(14, 14))
        self.max_btn.setStyleSheet(u"#max_btn {\n"
"	border: none;\n"
"	background-color: #f59e0b;\n"
"	border-radius: 7px;\n"
"}\n"
"#max_btn:hover {\n"
"	background-color: #fbbf24;\n"
"}\n"
"#max_btn:pressed {\n"
"	background-color: #d97706;\n"
"}")

        self.horizontalLayout.addWidget(self.max_btn)

        self.close_btn = QPushButton(self.frame)
        self.close_btn.setObjectName(u"close_btn")
        self.close_btn.setMinimumSize(QSize(14, 14))
        self.close_btn.setMaximumSize(QSize(14, 14))
        self.close_btn.setStyleSheet(u"#close_btn {\n"
"	border: none;\n"
"	background-color: #ef4444;\n"
"	border-radius: 7px;\n"
"}\n"
"#close_btn:hover {\n"
"	background-color: #f87171;\n"
"}\n"
"#close_btn:pressed {\n"
"	background-color: #dc2626;\n"
"}")

        self.horizontalLayout.addWidget(self.close_btn)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setStyleSheet(u"#frame_2 {\n"
"	background-color: #0f172a;\n"
"	border-bottom-right-radius: 10px;\n"
"	border-bottom-left-radius: 10px;\n"
"}")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.frame_2)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.horizontalLayout_2 = QHBoxLayout(self.page)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.page)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(6)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy1)
        self.frame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_27 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_27.setSpacing(0)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.frame_30 = QFrame(self.frame_3)
        self.frame_30.setObjectName(u"frame_30")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(10)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_30.sizePolicy().hasHeightForWidth())
        self.frame_30.setSizePolicy(sizePolicy2)
        self.frame_30.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_3 = QVBoxLayout(self.frame_30)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.frame_30)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)
        self.label_2.setStyleSheet(u"border-image: url(:/image/image/left_bg.png);\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)


        self.horizontalLayout_27.addWidget(self.frame_30)


        self.horizontalLayout_2.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.page)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(7)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy4)
        self.frame_4.setStyleSheet(u"QFrame#frame_4 {\n"
"	background-color: #1e293b;\n"
"}")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_4 = QVBoxLayout(self.frame_4)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.frame_4)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(1)
        sizePolicy5.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy5)
        self.frame_5.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setSpacing(15)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 20, 0, 10)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.signin_section = QPushButton(self.frame_5)
        self.signin_section.setObjectName(u"signin_section")
        self.signin_section.setStyleSheet(u"#signin_section {\n"
"	border: none;\n"
"	font: 700 30pt \"Microsoft YaHei UI\";\n"
"	color: #64748b;\n"
"	padding-bottom: 5px;\n"
"}\n"
"#signin_section:focus, #signin_section:hover {\n"
"	color: #10b981;\n"
"}")

        self.horizontalLayout_3.addWidget(self.signin_section)

        self.line = QFrame(self.frame_5)
        self.line.setObjectName(u"line")
        self.line.setMaximumSize(QSize(2, 25))
        self.line.setStyleSheet(u"background-color: #334155;")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.signup_section = QPushButton(self.frame_5)
        self.signup_section.setObjectName(u"signup_section")
        self.signup_section.setStyleSheet(u"#signup_section {\n"
"	border: none;\n"
"	font: 700 30pt \"Microsoft YaHei UI\";\n"
"	color: #64748b;\n"
"	padding-bottom: 5px;\n"
"}\n"
"#signup_section:focus, #signup_section:hover {\n"
"	color: #10b981;\n"
"}")

        self.horizontalLayout_3.addWidget(self.signup_section)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)


        self.verticalLayout_4.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame_4)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(10)
        sizePolicy6.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy6)
        self.frame_6.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_5 = QVBoxLayout(self.frame_6)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_2 = QStackedWidget(self.frame_6)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")
        self.signin_page = QWidget()
        self.signin_page.setObjectName(u"signin_page")
        self.verticalLayout_6 = QVBoxLayout(self.signin_page)
        self.verticalLayout_6.setSpacing(10)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.frame_7 = QFrame(self.signin_page)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy3.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy3)
        self.frame_7.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_22 = QVBoxLayout(self.frame_7)
        self.verticalLayout_22.setSpacing(8)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(20, 15, 20, 15)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_22.addItem(self.verticalSpacer)

        self.label_13 = QLabel(self.frame_7)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setStyleSheet(u"font: 700 16pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;\n"
"letter-spacing: 1px;")
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_22.addWidget(self.label_13)

        self.label_sub_info = QLabel(self.frame_7)
        self.label_sub_info.setObjectName(u"label_sub_info")
        self.label_sub_info.setStyleSheet(u"font: 9pt \"Microsoft YaHei UI\";\n"
"color: #64748b;")
        self.label_sub_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_22.addWidget(self.label_sub_info)

        self.label_auth_tip = QLabel(self.frame_7)
        self.label_auth_tip.setObjectName(u"label_auth_tip")
        self.label_auth_tip.setStyleSheet(u"font: 9pt \"Microsoft YaHei UI\";\n"
"color: #94a3b8;\n"
"background-color: rgba(16, 185, 129, 0.08);\n"
"border: 1px dashed rgba(16, 185, 129, 0.35);\n"
"border-radius: 6px;\n"
"padding: 5px 14px;")
        self.label_auth_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_22.addWidget(self.label_auth_tip, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_6.addWidget(self.frame_7)

        self.frame_10 = QFrame(self.signin_page)
        self.frame_10.setObjectName(u"frame_10")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(4)
        sizePolicy7.setHeightForWidth(self.frame_10.sizePolicy().hasHeightForWidth())
        self.frame_10.setSizePolicy(sizePolicy7)
        self.frame_10.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalSpacer_8 = QSpacerItem(42, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)

        self.label_3 = QLabel(self.frame_10)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 700 14pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;")

        self.horizontalLayout_6.addWidget(self.label_3)

        self.horizontalSpacer_7 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.account_edit = QLineEdit(self.frame_10)
        self.account_edit.setObjectName(u"account_edit")
        self.account_edit.setMinimumSize(QSize(220, 40))
        self.account_edit.setStyleSheet(u"#account_edit {\n"
"	font: 11pt \"Microsoft YaHei UI\";\n"
"	color: #f8fafc;\n"
"	background-color: #0f172a;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 8px;\n"
"	padding-left: 10px;\n"
"}\n"
"#account_edit:focus {\n"
"	border: 2px solid #10b981;\n"
"}")

        self.horizontalLayout_6.addWidget(self.account_edit)

        self.horizontalSpacer_12 = QSpacerItem(43, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_12)


        self.verticalLayout_6.addWidget(self.frame_10)

        self.frame_8 = QFrame(self.signin_page)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy7.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy7)
        self.frame_8.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_10 = QSpacerItem(39, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)

        self.label_4 = QLabel(self.frame_8)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"font: 700 14pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;")

        self.horizontalLayout_5.addWidget(self.label_4)

        self.horizontalSpacer_11 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_11)

        self.password_edit = QLineEdit(self.frame_8)
        self.password_edit.setObjectName(u"password_edit")
        self.password_edit.setMinimumSize(QSize(220, 40))
        self.password_edit.setStyleSheet(u"#password_edit {\n"
"	font: 11pt \"Microsoft YaHei UI\";\n"
"	color: #f8fafc;\n"
"	background-color: #0f172a;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 8px;\n"
"	padding-left: 10px;\n"
"}\n"
"#password_edit:focus {\n"
"	border: 2px solid #10b981;\n"
"}")

        self.horizontalLayout_5.addWidget(self.password_edit)

        self.horizontalSpacer_9 = QSpacerItem(41, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_9)


        self.verticalLayout_6.addWidget(self.frame_8)

        self.frame_9 = QFrame(self.signin_page)
        self.frame_9.setObjectName(u"frame_9")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(5)
        sizePolicy8.setHeightForWidth(self.frame_9.sizePolicy().hasHeightForWidth())
        self.frame_9.setSizePolicy(sizePolicy8)
        self.frame_9.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(90, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.signin = QPushButton(self.frame_9)
        self.signin.setObjectName(u"signin")
        self.signin.setMinimumSize(QSize(260, 45))
        self.signin.setMaximumSize(QSize(260, 45))
        self.signin.setStyleSheet(u"#signin {\n"
"	border-radius: 22px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	font: 700 13pt \"Microsoft YaHei UI\";\n"
"	border: none;\n"
"}\n"
"#signin:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#signin:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_4.addWidget(self.signin)

        self.horizontalSpacer_6 = QSpacerItem(89, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)


        self.verticalLayout_6.addWidget(self.frame_9)

        self.stackedWidget_2.addWidget(self.signin_page)
        self.signup_page = QWidget()
        self.signup_page.setObjectName(u"signup_page")
        self.verticalLayout_7 = QVBoxLayout(self.signup_page)
        self.verticalLayout_7.setSpacing(8)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.frame_11 = QFrame(self.signup_page)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy3.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy3)
        self.frame_11.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_23 = QVBoxLayout(self.frame_11)
        self.verticalLayout_23.setSpacing(8)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(20, 15, 20, 15)
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_23.addItem(self.verticalSpacer_3)

        self.label_14 = QLabel(self.frame_11)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setStyleSheet(u"font: 700 16pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;\n"
"letter-spacing: 1px;")
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.label_14)

        self.label_sub_info2 = QLabel(self.frame_11)
        self.label_sub_info2.setObjectName(u"label_sub_info2")
        self.label_sub_info2.setStyleSheet(u"font: 9pt \"Microsoft YaHei UI\";\n"
"color: #64748b;")
        self.label_sub_info2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.label_sub_info2)

        self.label_auth_tip2 = QLabel(self.frame_11)
        self.label_auth_tip2.setObjectName(u"label_auth_tip2")
        self.label_auth_tip2.setStyleSheet(u"font: 9pt \"Microsoft YaHei UI\";\n"
"color: #94a3b8;\n"
"background-color: rgba(56, 189, 248, 0.08);\n"
"border: 1px dashed rgba(56, 189, 248, 0.35);\n"
"border-radius: 6px;\n"
"padding: 5px 14px;")
        self.label_auth_tip2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.label_auth_tip2, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_7.addWidget(self.frame_11)

        self.frame_12 = QFrame(self.signup_page)
        self.frame_12.setObjectName(u"frame_12")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(2)
        sizePolicy9.setHeightForWidth(self.frame_12.sizePolicy().hasHeightForWidth())
        self.frame_12.setSizePolicy(sizePolicy9)
        self.frame_12.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalSpacer_14 = QSpacerItem(87, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_14)

        self.label_5 = QLabel(self.frame_12)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"font: 700 13pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.horizontalSpacer_13 = QSpacerItem(68, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_13)

        self.account_edit_2 = QLineEdit(self.frame_12)
        self.account_edit_2.setObjectName(u"account_edit_2")
        self.account_edit_2.setMinimumSize(QSize(220, 38))
        self.account_edit_2.setStyleSheet(u"#account_edit_2 {\n"
"	font: 11pt \"Microsoft YaHei UI\";\n"
"	color: #f8fafc;\n"
"	background-color: #0f172a;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 8px;\n"
"	padding-left: 10px;\n"
"}\n"
"#account_edit_2:focus {\n"
"	border: 2px solid #10b981;\n"
"}")

        self.horizontalLayout_7.addWidget(self.account_edit_2)

        self.horizontalSpacer_15 = QSpacerItem(104, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_15)


        self.verticalLayout_7.addWidget(self.frame_12)

        self.frame_13 = QFrame(self.signup_page)
        self.frame_13.setObjectName(u"frame_13")
        sizePolicy9.setHeightForWidth(self.frame_13.sizePolicy().hasHeightForWidth())
        self.frame_13.setSizePolicy(sizePolicy9)
        self.frame_13.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalSpacer_16 = QSpacerItem(62, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_16)

        self.label_6 = QLabel(self.frame_13)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setStyleSheet(u"font: 700 13pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;")

        self.horizontalLayout_8.addWidget(self.label_6)

        self.horizontalSpacer_17 = QSpacerItem(52, 27, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_17)

        self.password_edit_2 = QLineEdit(self.frame_13)
        self.password_edit_2.setObjectName(u"password_edit_2")
        self.password_edit_2.setMinimumSize(QSize(220, 38))
        self.password_edit_2.setStyleSheet(u"#password_edit_2 {\n"
"	font: 11pt \"Microsoft YaHei UI\";\n"
"	color: #f8fafc;\n"
"	background-color: #0f172a;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 8px;\n"
"	padding-left: 10px;\n"
"}\n"
"#password_edit_2:focus {\n"
"	border: 2px solid #10b981;\n"
"}")

        self.horizontalLayout_8.addWidget(self.password_edit_2)

        self.horizontalSpacer_18 = QSpacerItem(95, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_18)


        self.verticalLayout_7.addWidget(self.frame_13)

        self.frame_15 = QFrame(self.signup_page)
        self.frame_15.setObjectName(u"frame_15")
        sizePolicy9.setHeightForWidth(self.frame_15.sizePolicy().hasHeightForWidth())
        self.frame_15.setSizePolicy(sizePolicy9)
        self.frame_15.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_15)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalSpacer_19 = QSpacerItem(41, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_19)

        self.label_7 = QLabel(self.frame_15)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"font: 700 13pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;")

        self.horizontalLayout_9.addWidget(self.label_7)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_20)

        self.truepassword_edit = QLineEdit(self.frame_15)
        self.truepassword_edit.setObjectName(u"truepassword_edit")
        self.truepassword_edit.setMinimumSize(QSize(220, 38))
        self.truepassword_edit.setStyleSheet(u"#truepassword_edit {\n"
"	font: 11pt \"Microsoft YaHei UI\";\n"
"	color: #f8fafc;\n"
"	background-color: #0f172a;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 8px;\n"
"	padding-left: 10px;\n"
"}\n"
"#truepassword_edit:focus {\n"
"	border: 2px solid #10b981;\n"
"}")

        self.horizontalLayout_9.addWidget(self.truepassword_edit)

        self.horizontalSpacer_21 = QSpacerItem(86, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_21)


        self.verticalLayout_7.addWidget(self.frame_15)

        self.frame_14 = QFrame(self.signup_page)
        self.frame_14.setObjectName(u"frame_14")
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(3)
        sizePolicy10.setHeightForWidth(self.frame_14.sizePolicy().hasHeightForWidth())
        self.frame_14.setSizePolicy(sizePolicy10)
        self.frame_14.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_14)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalSpacer_22 = QSpacerItem(99, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_22)

        self.signup = QPushButton(self.frame_14)
        self.signup.setObjectName(u"signup")
        self.signup.setMinimumSize(QSize(260, 45))
        self.signup.setStyleSheet(u"#signup {\n"
"	border-radius: 22px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	font: 700 13pt \"Microsoft YaHei UI\";\n"
"	border: none;\n"
"}\n"
"#signup:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#signup:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_10.addWidget(self.signup)

        self.horizontalSpacer_23 = QSpacerItem(98, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_23)


        self.verticalLayout_7.addWidget(self.frame_14)

        self.stackedWidget_2.addWidget(self.signup_page)

        self.verticalLayout_5.addWidget(self.stackedWidget_2)


        self.verticalLayout_4.addWidget(self.frame_6)


        self.horizontalLayout_2.addWidget(self.frame_4)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_8 = QVBoxLayout(self.page_2)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.frame_16 = QFrame(self.page_2)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setStyleSheet(u"#frame_16 {\n"
"	background-color: #0f172a;\n"
"}")
        self.frame_16.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_16)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.frame_17 = QFrame(self.frame_16)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setMinimumSize(QSize(80, 0))
        self.frame_17.setStyleSheet(u"#frame_17 {\n"
"	background-color: #1e293b;\n"
"	border-right: 1px solid #334155;\n"
"}")
        self.frame_17.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalLayout_14 = QVBoxLayout(self.frame_17)
        self.verticalLayout_14.setSpacing(15)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 30, 0, 20)
        self.frame_19 = QFrame(self.frame_17)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_10 = QVBoxLayout(self.frame_19)
        self.verticalLayout_10.setSpacing(4)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.home = QPushButton(self.frame_19)
        self.home.setObjectName(u"home")
        self.home.setMinimumSize(QSize(48, 48))
        self.home.setMaximumSize(QSize(48, 48))
        self.home.setStyleSheet(u"#home {\n"
"	border: none;\n"
"	border-radius: 12px;\n"
"	background-color: transparent;\n"
"}\n"
"#home:hover {\n"
"	background-color: #334155;\n"
"}\n"
"#home:focus {\n"
"	background-color: #10b981;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/image/image/home.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.home.setIcon(icon)
        self.home.setIconSize(QSize(28, 28))

        self.verticalLayout_10.addWidget(self.home, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_9 = QLabel(self.frame_19)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setStyleSheet(u"color: #94a3b8; font: 9pt \"Microsoft YaHei UI\";")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_9)


        self.verticalLayout_14.addWidget(self.frame_19, 0, Qt.AlignmentFlag.AlignHCenter)

        self.frame_20 = QFrame(self.frame_17)
        self.frame_20.setObjectName(u"frame_20")
        self.frame_20.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_11 = QVBoxLayout(self.frame_20)
        self.verticalLayout_11.setSpacing(4)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.more = QPushButton(self.frame_20)
        self.more.setObjectName(u"more")
        self.more.setMinimumSize(QSize(48, 48))
        self.more.setMaximumSize(QSize(48, 48))
        self.more.setStyleSheet(u"#more {\n"
"	border: none;\n"
"	border-radius: 12px;\n"
"	background-color: transparent;\n"
"}\n"
"#more:hover {\n"
"	background-color: #334155;\n"
"}\n"
"#more:focus {\n"
"	background-color: #10b981;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/image/image/map.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.more.setIcon(icon1)
        self.more.setIconSize(QSize(28, 28))

        self.verticalLayout_11.addWidget(self.more, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_8 = QLabel(self.frame_20)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setStyleSheet(u"color: #94a3b8; font: 9pt \"Microsoft YaHei UI\";")
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.label_8)


        self.verticalLayout_14.addWidget(self.frame_20, 0, Qt.AlignmentFlag.AlignHCenter)

        self.frame_21 = QFrame(self.frame_17)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_12 = QVBoxLayout(self.frame_21)
        self.verticalLayout_12.setSpacing(4)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.info = QPushButton(self.frame_21)
        self.info.setObjectName(u"info")
        self.info.setMinimumSize(QSize(48, 48))
        self.info.setMaximumSize(QSize(48, 48))
        self.info.setStyleSheet(u"#info {\n"
"	border: none;\n"
"	border-radius: 12px;\n"
"	background-color: transparent;\n"
"}\n"
"#info:hover {\n"
"	background-color: #334155;\n"
"}\n"
"#info:focus {\n"
"	background-color: #10b981;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/image/image/info.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.info.setIcon(icon2)
        self.info.setIconSize(QSize(28, 28))

        self.verticalLayout_12.addWidget(self.info, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label_11 = QLabel(self.frame_21)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setStyleSheet(u"color: #94a3b8; font: 9pt \"Microsoft YaHei UI\";")
        self.label_11.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_12.addWidget(self.label_11)


        self.verticalLayout_14.addWidget(self.frame_21, 0, Qt.AlignmentFlag.AlignHCenter)

        self.verticalSpacer_2 = QSpacerItem(14, 253, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_2)

        self.frame_22 = QFrame(self.frame_17)
        self.frame_22.setObjectName(u"frame_22")
        self.frame_22.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_13 = QVBoxLayout(self.frame_22)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.setting = QPushButton(self.frame_22)
        self.setting.setObjectName(u"setting")
        self.setting.setMinimumSize(QSize(48, 48))
        self.setting.setMaximumSize(QSize(48, 48))
        self.setting.setStyleSheet(u"#setting {\n"
"	border: none;\n"
"	border-radius: 12px;\n"
"	background-color: transparent;\n"
"}\n"
"#setting:hover {\n"
"	background-color: #334155;\n"
"}\n"
"#setting:focus {\n"
"	background-color: #10b981;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/image/image/setting.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.setting.setIcon(icon3)
        self.setting.setIconSize(QSize(28, 28))

        self.verticalLayout_13.addWidget(self.setting)


        self.verticalLayout_14.addWidget(self.frame_22, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_11.addWidget(self.frame_17, 0, Qt.AlignmentFlag.AlignLeft)

        self.frame_18 = QFrame(self.frame_16)
        self.frame_18.setObjectName(u"frame_18")
        sizePolicy3.setHeightForWidth(self.frame_18.sizePolicy().hasHeightForWidth())
        self.frame_18.setSizePolicy(sizePolicy3)
        self.frame_18.setStyleSheet(u"#frame_18 {\n"
"	background-color: #0f172a;\n"
"}")
        self.frame_18.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_9 = QVBoxLayout(self.frame_18)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_3 = QStackedWidget(self.frame_18)
        self.stackedWidget_3.setObjectName(u"stackedWidget_3")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout_15 = QVBoxLayout(self.page_3)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalSpacer_6 = QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_6)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalSpacer_24 = QSpacerItem(228, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_24)

        self.label = QLabel(self.page_3)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(500, 500))
        self.label.setMaximumSize(QSize(500, 500))
        self.label.setStyleSheet(u"background-image: url(:/image/image/logo_max.png);\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.label.setScaledContents(False)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(False)
        self.label.setOpenExternalLinks(False)

        self.horizontalLayout_12.addWidget(self.label)

        self.horizontalSpacer_25 = QSpacerItem(228, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_25)


        self.verticalLayout_15.addLayout(self.horizontalLayout_12)

        self.verticalSpacer_7 = QSpacerItem(6, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_7)

        self.frame_32 = QFrame(self.page_3)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_30 = QHBoxLayout(self.frame_32)
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalSpacer_57 = QSpacerItem(73, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_57)

        self.label_10 = QLabel(self.frame_32)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setStyleSheet(u"font: 700 30pt \"Microsoft YaHei UI\";\n"
"color: #f8fafc;\n"
"letter-spacing: 2px;")
        self.label_10.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_30.addWidget(self.label_10)

        self.horizontalSpacer_59 = QSpacerItem(73, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_59)


        self.verticalLayout_15.addWidget(self.frame_32)

        self.frame_33 = QFrame(self.page_3)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setMinimumSize(QSize(0, 60))
        self.frame_33.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_29 = QHBoxLayout(self.frame_33)
        self.horizontalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalSpacer_58 = QSpacerItem(73, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_29.addItem(self.horizontalSpacer_58)

        self.label_12 = QLabel(self.frame_33)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"font: 700 24pt \"Microsoft YaHei UI\";\n"
"color: #10b981;\n"
"letter-spacing: 4px;")
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_29.addWidget(self.label_12)

        self.horizontalSpacer_60 = QSpacerItem(73, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_29.addItem(self.horizontalSpacer_60)


        self.verticalLayout_15.addWidget(self.frame_33)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_8)

        self.stackedWidget_3.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.horizontalLayout_13 = QHBoxLayout(self.page_4)
        self.horizontalLayout_13.setSpacing(15)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(15, 15, 15, 15)
        self.frame_24 = QFrame(self.page_4)
        self.frame_24.setObjectName(u"frame_24")
        sizePolicy3.setHeightForWidth(self.frame_24.sizePolicy().hasHeightForWidth())
        self.frame_24.setSizePolicy(sizePolicy3)
        self.frame_24.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_17 = QVBoxLayout(self.frame_24)
        self.verticalLayout_17.setSpacing(15)
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.map_wed = QWebEngineView(self.frame_24)
        self.map_wed.setObjectName(u"map_wed")
        self.map_wed.setMinimumSize(QSize(550, 435))
        self.map_wed.setStyleSheet(u"border: 1px solid #334155;\n"
"border-radius: 12px;\n"
"background-color: #1e293b;")

        self.verticalLayout_17.addWidget(self.map_wed)


        self.horizontalLayout_13.addWidget(self.frame_24)

        self.frame_25 = QFrame(self.page_4)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setMinimumSize(QSize(310, 0))
        self.frame_25.setMaximumSize(QSize(310, 16777215))
        self.frame_25.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_21 = QVBoxLayout(self.frame_25)
        self.verticalLayout_21.setSpacing(15)
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.groupBox = QGroupBox(self.frame_25)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"QGroupBox {\n"
"	font: 700 13pt \"Microsoft YaHei UI\";\n"
"	color: #10b981;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 15px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 15px;\n"
"	padding: 0 5px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 10pt \"Microsoft YaHei UI\";\n"
"	padding: 2px;\n"
"}")
        self.verticalLayout_18 = QVBoxLayout(self.groupBox)
        self.verticalLayout_18.setSpacing(8)
        self.verticalLayout_18.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.location_s = QLabel(self.groupBox)
        self.location_s.setObjectName(u"location_s")

        self.verticalLayout_18.addWidget(self.location_s)

        self.maxtemp_s = QLabel(self.groupBox)
        self.maxtemp_s.setObjectName(u"maxtemp_s")

        self.verticalLayout_18.addWidget(self.maxtemp_s)

        self.mintemp_s = QLabel(self.groupBox)
        self.mintemp_s.setObjectName(u"mintemp_s")

        self.verticalLayout_18.addWidget(self.mintemp_s)

        self.humidity_s = QLabel(self.groupBox)
        self.humidity_s.setObjectName(u"humidity_s")

        self.verticalLayout_18.addWidget(self.humidity_s)

        self.rainfall_s = QLabel(self.groupBox)
        self.rainfall_s.setObjectName(u"rainfall_s")

        self.verticalLayout_18.addWidget(self.rainfall_s)

        self.atmosphericP_s = QLabel(self.groupBox)
        self.atmosphericP_s.setObjectName(u"atmosphericP_s")

        self.verticalLayout_18.addWidget(self.atmosphericP_s)

        self.riskrank_s = QLabel(self.groupBox)
        self.riskrank_s.setObjectName(u"riskrank_s")
        self.riskrank_s.setStyleSheet(u"color: #f87171; font-weight: bold;")

        self.verticalLayout_18.addWidget(self.riskrank_s)


        self.verticalLayout_21.addWidget(self.groupBox)

        self.verticalSpacer_14 = QSpacerItem(20, 83, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_14)

        self.frame_23 = QFrame(self.frame_25)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setMinimumSize(QSize(0, 95))
        self.frame_23.setStyleSheet(u"#frame_23 {\n"
"	border-radius: 12px;\n"
"	border: 1px solid #334155;\n"
"	background-color: #1e293b;\n"
"}")
        self.frame_23.setFrameShape(QFrame.Shape.StyledPanel)
        self.verticalLayout_16 = QVBoxLayout(self.frame_23)
        self.verticalLayout_16.setSpacing(4)
        self.verticalLayout_16.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.time = QLabel(self.frame_23)
        self.time.setObjectName(u"time")
        self.time.setStyleSheet(u"font: 700 22pt \"Microsoft YaHei UI\";\n"
"color: #38bdf8;")
        self.time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_16.addWidget(self.time)

        self.date = QLabel(self.frame_23)
        self.date.setObjectName(u"date")
        self.date.setStyleSheet(u"font: 600 13pt \"Microsoft YaHei UI\";\n"
"color: #94a3b8;")
        self.date.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_16.addWidget(self.date)


        self.verticalLayout_21.addWidget(self.frame_23)

        self.UAVFPV = QPushButton(self.frame_25)
        self.UAVFPV.setObjectName(u"UAVFPV")
        self.UAVFPV.setMinimumSize(QSize(0, 60))
        self.UAVFPV.setStyleSheet(u"#UAVFPV {\n"
"	font: 700 13pt \"Microsoft YaHei UI\";\n"
"	border-radius: 12px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#UAVFPV:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#UAVFPV:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.verticalLayout_21.addWidget(self.UAVFPV)

        self.INFOWARN = QPushButton(self.frame_25)
        self.INFOWARN.setObjectName(u"INFOWARN")
        self.INFOWARN.setMinimumSize(QSize(0, 60))
        self.INFOWARN.setStyleSheet(u"#INFOWARN {\n"
"	font: 700 13pt \"Microsoft YaHei UI\";\n"
"	border-radius: 12px;\n"
"	background-color: #ef4444;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#INFOWARN:hover {\n"
"	background-color: #dc2626;\n"
"}\n"
"#INFOWARN:pressed {\n"
"	background-color: #b91c1c;\n"
"}")

        self.verticalLayout_21.addWidget(self.INFOWARN)


        self.horizontalLayout_13.addWidget(self.frame_25)

        self.stackedWidget_3.addWidget(self.page_4)
        self.page_5 = QWidget()
        self.page_5.setObjectName(u"page_5")
        self.verticalLayout_27 = QVBoxLayout(self.page_5)
        self.verticalLayout_27.setSpacing(15)
        self.verticalLayout_27.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.frame_28 = QFrame(self.page_5)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setStyleSheet(u"#frame_28 {\n"
"	background-color: #1e293b;\n"
"	border-radius: 12px;\n"
"	border: 1px solid #334155;\n"
"}")
        self.verticalLayout_28 = QVBoxLayout(self.frame_28)
        self.verticalLayout_28.setSpacing(8)
        self.verticalLayout_28.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setSpacing(10)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.search_pos_edit = QLineEdit(self.frame_28)
        self.search_pos_edit.setObjectName(u"search_pos_edit")
        self.search_pos_edit.setMinimumSize(QSize(0, 38))
        self.search_pos_edit.setStyleSheet(u"#search_pos_edit {\n"
"	font: 10pt \"Microsoft YaHei UI\";\n"
"	color: #f8fafc;\n"
"	background-color: #0f172a;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 8px;\n"
"	padding-left: 12px;\n"
"}\n"
"#search_pos_edit:focus {\n"
"	border: 1px solid #10b981;\n"
"}")

        self.horizontalLayout_26.addWidget(self.search_pos_edit)

        self.search_pos = QPushButton(self.frame_28)
        self.search_pos.setObjectName(u"search_pos")
        self.search_pos.setMinimumSize(QSize(90, 38))
        self.search_pos.setStyleSheet(u"#search_pos {\n"
"	font: 700 10pt \"Microsoft YaHei UI\";\n"
"	border-radius: 8px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#search_pos:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#search_pos:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_26.addWidget(self.search_pos)


        self.verticalLayout_28.addLayout(self.horizontalLayout_26)

        self.label_24 = QLabel(self.frame_28)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setStyleSheet(u"font: 9pt \"Microsoft YaHei UI\";\n"
"color: #64748b;")

        self.verticalLayout_28.addWidget(self.label_24)


        self.verticalLayout_27.addWidget(self.frame_28)

        self.frame_29 = QFrame(self.page_5)
        self.frame_29.setObjectName(u"frame_29")
        self.frame_29.setStyleSheet(u"#frame_29 {\n"
"	background-color: transparent;\n"
"}")
        self.verticalLayout_31 = QVBoxLayout(self.frame_29)
        self.verticalLayout_31.setSpacing(10)
        self.verticalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.label_40 = QLabel(self.frame_29)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setStyleSheet(u"font: 700 13pt \"Microsoft YaHei UI\";\n"
"color: #e2e8f0;\n"
"padding-left: 5px;")

        self.verticalLayout_31.addWidget(self.label_40, 0, Qt.AlignmentFlag.AlignLeft)

        self.scrollArea = QScrollArea(self.frame_29)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"#scrollArea {\n"
"	border: none;\n"
"	background-color: transparent;\n"
"}\n"
"QScrollBar:vertical {\n"
"	border: none;\n"
"	background: #0f172a;\n"
"	width: 8px;\n"
"	border-radius: 4px;\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"	background: #334155;\n"
"	border-radius: 4px;\n"
"}\n"
"QScrollBar::handle:vertical:hover {\n"
"	background: #10b981;\n"
"}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 581, 578))
        self.scrollAreaWidgetContents.setStyleSheet(u"background-color: transparent;")
        self.verticalLayout_35 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_35.setSpacing(15)
        self.verticalLayout_35.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.horizontalLayout_47 = QHBoxLayout()
        self.horizontalLayout_47.setSpacing(15)
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setStyleSheet(u"QGroupBox {\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	color: #38bdf8;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 12px;\n"
"	padding: 0 4px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.verticalLayout_24 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_24.setSpacing(10)
        self.verticalLayout_24.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalSpacer_26 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_26)

        self.label_15 = QLabel(self.groupBox_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setMinimumSize(QSize(130, 120))
        self.label_15.setStyleSheet(u"border-image: url(:/image/image/robot.jpg);\n"
"border-radius: 10px;")
        self.label_15.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_14.addWidget(self.label_15)

        self.horizontalSpacer_27 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_27)


        self.verticalLayout_24.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_16 = QLabel(self.groupBox_2)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_15.addWidget(self.label_16)

        self.horizontalSpacer_28 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_28)

        self.condition = QPushButton(self.groupBox_2)
        self.condition.setObjectName(u"condition")
        self.condition.setMinimumSize(QSize(14, 14))
        self.condition.setMaximumSize(QSize(14, 14))
        self.condition.setStyleSheet(u"#condition {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}")

        self.horizontalLayout_15.addWidget(self.condition)


        self.verticalLayout_24.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_17 = QLabel(self.groupBox_2)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setStyleSheet(u"color: #38bdf8; font-weight: bold;")

        self.horizontalLayout_17.addWidget(self.label_17)


        self.verticalLayout_24.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setSpacing(8)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.gohome = QPushButton(self.groupBox_2)
        self.gohome.setObjectName(u"gohome")
        self.gohome.setMinimumSize(QSize(0, 32))
        self.gohome.setStyleSheet(u"#gohome {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #334155;\n"
"	color: #f8fafc;\n"
"	border: 1px solid #475569;\n"
"}\n"
"#gohome:hover {\n"
"	background-color: #475569;\n"
"}\n"
"#gohome:pressed {\n"
"	background-color: #1e293b;\n"
"}")

        self.horizontalLayout_16.addWidget(self.gohome)

        self.byhand_control = QPushButton(self.groupBox_2)
        self.byhand_control.setObjectName(u"byhand_control")
        self.byhand_control.setMinimumSize(QSize(0, 32))
        self.byhand_control.setStyleSheet(u"#byhand_control {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#byhand_control:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#byhand_control:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_16.addWidget(self.byhand_control)


        self.verticalLayout_24.addLayout(self.horizontalLayout_16)


        self.horizontalLayout_47.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setStyleSheet(u"QGroupBox {\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	color: #38bdf8;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 12px;\n"
"	padding: 0 4px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.verticalLayout_25 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_25.setSpacing(10)
        self.verticalLayout_25.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalSpacer_36 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_36)

        self.label_18 = QLabel(self.groupBox_3)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMinimumSize(QSize(130, 120))
        self.label_18.setStyleSheet(u"border-image: url(:/image/image/robot.jpg);\n"
"border-radius: 10px;")
        self.label_18.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_18.addWidget(self.label_18)

        self.horizontalSpacer_37 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_37)


        self.verticalLayout_25.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_19 = QLabel(self.groupBox_3)
        self.label_19.setObjectName(u"label_19")

        self.horizontalLayout_19.addWidget(self.label_19)

        self.horizontalSpacer_39 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_39)

        self.condition_2 = QPushButton(self.groupBox_3)
        self.condition_2.setObjectName(u"condition_2")
        self.condition_2.setMinimumSize(QSize(14, 14))
        self.condition_2.setMaximumSize(QSize(14, 14))
        self.condition_2.setStyleSheet(u"#condition_2 {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}")

        self.horizontalLayout_19.addWidget(self.condition_2)


        self.verticalLayout_25.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_20 = QLabel(self.groupBox_3)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setStyleSheet(u"color: #38bdf8; font-weight: bold;")

        self.horizontalLayout_20.addWidget(self.label_20)


        self.verticalLayout_25.addLayout(self.horizontalLayout_20)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setSpacing(8)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.gohome_2 = QPushButton(self.groupBox_3)
        self.gohome_2.setObjectName(u"gohome_2")
        self.gohome_2.setMinimumSize(QSize(0, 32))
        self.gohome_2.setStyleSheet(u"#gohome_2 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #334155;\n"
"	color: #f8fafc;\n"
"	border: 1px solid #475569;\n"
"}\n"
"#gohome_2:hover {\n"
"	background-color: #475569;\n"
"}\n"
"#gohome_2:pressed {\n"
"	background-color: #1e293b;\n"
"}")

        self.horizontalLayout_21.addWidget(self.gohome_2)

        self.byhand_control_2 = QPushButton(self.groupBox_3)
        self.byhand_control_2.setObjectName(u"byhand_control_2")
        self.byhand_control_2.setMinimumSize(QSize(0, 32))
        self.byhand_control_2.setStyleSheet(u"#byhand_control_2 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#byhand_control_2:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#byhand_control_2:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_21.addWidget(self.byhand_control_2)


        self.verticalLayout_25.addLayout(self.horizontalLayout_21)


        self.horizontalLayout_47.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setStyleSheet(u"QGroupBox {\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	color: #38bdf8;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 12px;\n"
"	padding: 0 4px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.verticalLayout_26 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_26.setSpacing(10)
        self.verticalLayout_26.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalSpacer_46 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_46)

        self.label_21 = QLabel(self.groupBox_4)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setMinimumSize(QSize(130, 120))
        self.label_21.setStyleSheet(u"border-image: url(:/image/image/robot1.png);\n"
"border-radius: 10px;")
        self.label_21.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_22.addWidget(self.label_21)

        self.horizontalSpacer_47 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_47)


        self.verticalLayout_26.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_22 = QLabel(self.groupBox_4)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_23.addWidget(self.label_22)

        self.horizontalSpacer_49 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_23.addItem(self.horizontalSpacer_49)

        self.condition_3 = QPushButton(self.groupBox_4)
        self.condition_3.setObjectName(u"condition_3")
        self.condition_3.setMinimumSize(QSize(14, 14))
        self.condition_3.setMaximumSize(QSize(14, 14))
        self.condition_3.setStyleSheet(u"#condition_3 {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}")

        self.horizontalLayout_23.addWidget(self.condition_3)


        self.verticalLayout_26.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_23 = QLabel(self.groupBox_4)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setStyleSheet(u"color: #38bdf8; font-weight: bold;")

        self.horizontalLayout_24.addWidget(self.label_23)


        self.verticalLayout_26.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setSpacing(8)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.gohome_3 = QPushButton(self.groupBox_4)
        self.gohome_3.setObjectName(u"gohome_3")
        self.gohome_3.setMinimumSize(QSize(0, 32))
        self.gohome_3.setStyleSheet(u"#gohome_3 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #334155;\n"
"	color: #f8fafc;\n"
"	border: 1px solid #475569;\n"
"}\n"
"#gohome_3:hover {\n"
"	background-color: #475569;\n"
"}\n"
"#gohome_3:pressed {\n"
"	background-color: #1e293b;\n"
"}")

        self.horizontalLayout_25.addWidget(self.gohome_3)

        self.byhand_control_3 = QPushButton(self.groupBox_4)
        self.byhand_control_3.setObjectName(u"byhand_control_3")
        self.byhand_control_3.setMinimumSize(QSize(0, 32))
        self.byhand_control_3.setStyleSheet(u"#byhand_control_3 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#byhand_control_3:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#byhand_control_3:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_25.addWidget(self.byhand_control_3)


        self.verticalLayout_26.addLayout(self.horizontalLayout_25)


        self.horizontalLayout_47.addWidget(self.groupBox_4)


        self.verticalLayout_35.addLayout(self.horizontalLayout_47)

        self.horizontalLayout_48 = QHBoxLayout()
        self.horizontalLayout_48.setSpacing(15)
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.groupBox_5 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setStyleSheet(u"QGroupBox {\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	color: #38bdf8;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 12px;\n"
"	padding: 0 4px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.verticalLayout_32 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_32.setSpacing(10)
        self.verticalLayout_32.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.horizontalLayout_35 = QHBoxLayout()
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.horizontalSpacer_76 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_76)

        self.label_31 = QLabel(self.groupBox_5)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(130, 120))
        self.label_31.setStyleSheet(u"border-image: url(:/image/image/robot1.png);\n"
"border-radius: 10px;")
        self.label_31.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_35.addWidget(self.label_31)

        self.horizontalSpacer_77 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_77)


        self.verticalLayout_32.addLayout(self.horizontalLayout_35)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.label_32 = QLabel(self.groupBox_5)
        self.label_32.setObjectName(u"label_32")

        self.horizontalLayout_36.addWidget(self.label_32)

        self.horizontalSpacer_79 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_36.addItem(self.horizontalSpacer_79)

        self.condition_6 = QPushButton(self.groupBox_5)
        self.condition_6.setObjectName(u"condition_6")
        self.condition_6.setMinimumSize(QSize(14, 14))
        self.condition_6.setMaximumSize(QSize(14, 14))
        self.condition_6.setStyleSheet(u"#condition_6 {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}")

        self.horizontalLayout_36.addWidget(self.condition_6)


        self.verticalLayout_32.addLayout(self.horizontalLayout_36)

        self.horizontalLayout_37 = QHBoxLayout()
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.label_33 = QLabel(self.groupBox_5)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setStyleSheet(u"color: #38bdf8; font-weight: bold;")

        self.horizontalLayout_37.addWidget(self.label_33)


        self.verticalLayout_32.addLayout(self.horizontalLayout_37)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setSpacing(8)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.gohome_6 = QPushButton(self.groupBox_5)
        self.gohome_6.setObjectName(u"gohome_6")
        self.gohome_6.setMinimumSize(QSize(0, 32))
        self.gohome_6.setStyleSheet(u"#gohome_6 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #334155;\n"
"	color: #f8fafc;\n"
"	border: 1px solid #475569;\n"
"}\n"
"#gohome_6:hover {\n"
"	background-color: #475569;\n"
"}\n"
"#gohome_6:pressed {\n"
"	background-color: #1e293b;\n"
"}")

        self.horizontalLayout_38.addWidget(self.gohome_6)

        self.byhand_control_6 = QPushButton(self.groupBox_5)
        self.byhand_control_6.setObjectName(u"byhand_control_6")
        self.byhand_control_6.setMinimumSize(QSize(0, 32))
        self.byhand_control_6.setStyleSheet(u"#byhand_control_6 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#byhand_control_6:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#byhand_control_6:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_38.addWidget(self.byhand_control_6)


        self.verticalLayout_32.addLayout(self.horizontalLayout_38)


        self.horizontalLayout_48.addWidget(self.groupBox_5)

        self.groupBox_7 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setStyleSheet(u"QGroupBox {\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	color: #38bdf8;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 12px;\n"
"	padding: 0 4px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.verticalLayout_34 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_34.setSpacing(10)
        self.verticalLayout_34.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.horizontalLayout_43 = QHBoxLayout()
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.horizontalSpacer_96 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_43.addItem(self.horizontalSpacer_96)

        self.label_37 = QLabel(self.groupBox_7)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setMinimumSize(QSize(130, 120))
        self.label_37.setStyleSheet(u"border-image: url(:/image/image/robot2.png);\n"
"border-radius: 10px;")
        self.label_37.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_43.addWidget(self.label_37)

        self.horizontalSpacer_97 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_43.addItem(self.horizontalSpacer_97)


        self.verticalLayout_34.addLayout(self.horizontalLayout_43)

        self.horizontalLayout_44 = QHBoxLayout()
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.label_38 = QLabel(self.groupBox_7)
        self.label_38.setObjectName(u"label_38")

        self.horizontalLayout_44.addWidget(self.label_38)

        self.horizontalSpacer_99 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_44.addItem(self.horizontalSpacer_99)

        self.condition_8 = QPushButton(self.groupBox_7)
        self.condition_8.setObjectName(u"condition_8")
        self.condition_8.setMinimumSize(QSize(14, 14))
        self.condition_8.setMaximumSize(QSize(14, 14))
        self.condition_8.setStyleSheet(u"#condition_8 {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}")

        self.horizontalLayout_44.addWidget(self.condition_8)


        self.verticalLayout_34.addLayout(self.horizontalLayout_44)

        self.horizontalLayout_45 = QHBoxLayout()
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.label_39 = QLabel(self.groupBox_7)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setStyleSheet(u"color: #38bdf8; font-weight: bold;")

        self.horizontalLayout_45.addWidget(self.label_39)


        self.verticalLayout_34.addLayout(self.horizontalLayout_45)

        self.horizontalLayout_46 = QHBoxLayout()
        self.horizontalLayout_46.setSpacing(8)
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.gohome_8 = QPushButton(self.groupBox_7)
        self.gohome_8.setObjectName(u"gohome_8")
        self.gohome_8.setMinimumSize(QSize(0, 32))
        self.gohome_8.setStyleSheet(u"#gohome_8 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #334155;\n"
"	color: #f8fafc;\n"
"	border: 1px solid #475569;\n"
"}\n"
"#gohome_8:hover {\n"
"	background-color: #475569;\n"
"}\n"
"#gohome_8:pressed {\n"
"	background-color: #1e293b;\n"
"}")

        self.horizontalLayout_46.addWidget(self.gohome_8)

        self.byhand_control_8 = QPushButton(self.groupBox_7)
        self.byhand_control_8.setObjectName(u"byhand_control_8")
        self.byhand_control_8.setMinimumSize(QSize(0, 32))
        self.byhand_control_8.setStyleSheet(u"#byhand_control_8 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#byhand_control_8:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#byhand_control_8:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_46.addWidget(self.byhand_control_8)


        self.verticalLayout_34.addLayout(self.horizontalLayout_46)


        self.horizontalLayout_48.addWidget(self.groupBox_7)

        self.groupBox_6 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setStyleSheet(u"QGroupBox {\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	color: #38bdf8;\n"
"	background-color: #1e293b;\n"
"	border: 1px solid #334155;\n"
"	border-radius: 12px;\n"
"	margin-top: 10px;\n"
"	padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"	subcontrol-origin: margin;\n"
"	left: 12px;\n"
"	padding: 0 4px;\n"
"}\n"
"QLabel {\n"
"	color: #cbd5e1;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.verticalLayout_33 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_33.setSpacing(10)
        self.verticalLayout_33.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.horizontalLayout_39 = QHBoxLayout()
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.horizontalSpacer_86 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_86)

        self.label_34 = QLabel(self.groupBox_6)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setMinimumSize(QSize(130, 120))
        self.label_34.setStyleSheet(u"border-image: url(:/image/image/robot2.png);\n"
"border-radius: 10px;")
        self.label_34.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_39.addWidget(self.label_34)

        self.horizontalSpacer_87 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_87)


        self.verticalLayout_33.addLayout(self.horizontalLayout_39)

        self.horizontalLayout_40 = QHBoxLayout()
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.label_35 = QLabel(self.groupBox_6)
        self.label_35.setObjectName(u"label_35")

        self.horizontalLayout_40.addWidget(self.label_35)

        self.horizontalSpacer_89 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_40.addItem(self.horizontalSpacer_89)

        self.condition_7 = QPushButton(self.groupBox_6)
        self.condition_7.setObjectName(u"condition_7")
        self.condition_7.setMinimumSize(QSize(14, 14))
        self.condition_7.setMaximumSize(QSize(14, 14))
        self.condition_7.setStyleSheet(u"#condition_7 {\n"
"	border: none;\n"
"	background-color: #10b981;\n"
"	border-radius: 7px;\n"
"}")

        self.horizontalLayout_40.addWidget(self.condition_7)


        self.verticalLayout_33.addLayout(self.horizontalLayout_40)

        self.horizontalLayout_41 = QHBoxLayout()
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.label_36 = QLabel(self.groupBox_6)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setStyleSheet(u"color: #38bdf8; font-weight: bold;")

        self.horizontalLayout_41.addWidget(self.label_36)


        self.verticalLayout_33.addLayout(self.horizontalLayout_41)

        self.horizontalLayout_42 = QHBoxLayout()
        self.horizontalLayout_42.setSpacing(8)
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.gohome_7 = QPushButton(self.groupBox_6)
        self.gohome_7.setObjectName(u"gohome_7")
        self.gohome_7.setMinimumSize(QSize(0, 32))
        self.gohome_7.setStyleSheet(u"#gohome_7 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #334155;\n"
"	color: #f8fafc;\n"
"	border: 1px solid #475569;\n"
"}\n"
"#gohome_7:hover {\n"
"	background-color: #475569;\n"
"}\n"
"#gohome_7:pressed {\n"
"	background-color: #1e293b;\n"
"}")

        self.horizontalLayout_42.addWidget(self.gohome_7)

        self.byhand_control_7 = QPushButton(self.groupBox_6)
        self.byhand_control_7.setObjectName(u"byhand_control_7")
        self.byhand_control_7.setMinimumSize(QSize(0, 32))
        self.byhand_control_7.setStyleSheet(u"#byhand_control_7 {\n"
"	font: 700 9pt \"Microsoft YaHei UI\";\n"
"	border-radius: 6px;\n"
"	background-color: #10b981;\n"
"	color: #ffffff;\n"
"	border: none;\n"
"}\n"
"#byhand_control_7:hover {\n"
"	background-color: #059669;\n"
"}\n"
"#byhand_control_7:pressed {\n"
"	background-color: #047857;\n"
"}")

        self.horizontalLayout_42.addWidget(self.byhand_control_7)


        self.verticalLayout_33.addLayout(self.horizontalLayout_42)


        self.horizontalLayout_48.addWidget(self.groupBox_6)


        self.verticalLayout_35.addLayout(self.horizontalLayout_48)

        self.verticalSpacer_25 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_35.addItem(self.verticalSpacer_25)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_31.addWidget(self.scrollArea)


        self.verticalLayout_27.addWidget(self.frame_29)

        self.stackedWidget_3.addWidget(self.page_5)
        self.page_6 = QWidget()
        self.page_6.setObjectName(u"page_6")
        self.stackedWidget_3.addWidget(self.page_6)

        self.verticalLayout_9.addWidget(self.stackedWidget_3)


        self.horizontalLayout_11.addWidget(self.frame_18)


        self.verticalLayout_8.addWidget(self.frame_16)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.verticalLayout.addWidget(self.frame_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.stackedWidget_3.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u667a\u62a4\u68ee\u6797-\u667a\u80fd\u65e0\u4eba\u673a\u5de1\u68c0\u5e73\u53f0", None))
        self.topinfo.setText(QCoreApplication.translate("MainWindow", u"\U0001f332 \U0000667a\U000062a4\U000068ee\U00006797 - \U00009996\U00009875", None))
        self.min_btn.setText("")
        self.max_btn.setText("")
        self.close_btn.setText("")
        self.label_2.setText("")
        self.signin_section.setText(QCoreApplication.translate("MainWindow", u"\u767b\u5f55", None))
        self.signup_section.setText(QCoreApplication.translate("MainWindow", u"\u6ce8\u518c", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u65e0\u4eba\u673a\u81ea\u4e3b\u5de1\u68c0\u8c03\u5ea6\u7ec8\u7aef", None))
        self.label_sub_info.setText(QCoreApplication.translate("MainWindow", u"\u6797\u706b\u667a\u80fd\u76d1\u6d4b \u00b7 \u7f16\u961f\u591a\u7ef4\u5de1\u822a \u00b7 \u7a7a\u5730\u4e00\u4f53\u6307\u6325", None))
        self.label_auth_tip.setText(QCoreApplication.translate("MainWindow", u"\U0001f512 \U00008bf7\U00008f93\U00005165\U00006388\U00006743\U000064cd\U00004f5c\U00005458/\U00007ba1\U00007406\U00005458\U000051ed\U00008bc1\U0000767b\U00005f55\U00005e73\U000053f0", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u7528\u6237\u540d\uff1a", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u5bc6\u3000\u7801\uff1a", None))
        self.signin.setText(QCoreApplication.translate("MainWindow", u"\u7acb\u5373\u767b\u5f55", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"\u521b\u5efa\u5de1\u68c0\u64cd\u4f5c\u5458\u8d26\u6237", None))
        self.label_sub_info2.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u8d26\u53f7\u9700\u7ecf\u8fc7\u6797\u4e1a\u6307\u6325\u4e2d\u5fc3\u5ba1\u6838\u540e\u65b9\u53ef\u64cd\u63a7\u8bbe\u5907", None))
        self.label_auth_tip2.setText(QCoreApplication.translate("MainWindow", u"\U0001f4cb \U00005bc6\U00007801\U0000957f\U00005ea6\U00005efa\U00008bae\U00004e0d\U00005c11\U00004e8e 6 \U00004f4d\U0000ff0c\U00008bf7\U000059a5\U00005584\U00004fdd\U00007ba1", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u7528 \u6237 \u540d\uff1a", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u8bbe \u7f6e \u5bc6 \u7801\uff1a", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u786e \u8ba4 \u5bc6 \u7801\uff1a", None))
        self.signup.setText(QCoreApplication.translate("MainWindow", u"\u7acb\u5373\u6ce8\u518c", None))
        self.home.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.more.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u5730\u56fe", None))
        self.info.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u5907", None))
        self.setting.setText("")
        self.label.setText("")
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"\u6b22\u8fce\u4f7f\u7528\u667a\u80fd\u5de1\u62a4\u5e73\u53f0", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"\u667a \u62a4 \u68ee \u6797 \u79d1 \u6280", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u5f53\u524d\u6c14\u5019\u76d1\u6d4b", None))
        self.location_s.setText(QCoreApplication.translate("MainWindow", u"\U0001f4cd \U00005730\U00005740\U0000ff1a--", None))
        self.maxtemp_s.setText(QCoreApplication.translate("MainWindow", u"\U0001f321 \U00006700\U00009ad8\U00006c14\U00006e29\U0000ff1a-- \U00002103", None))
        self.mintemp_s.setText(QCoreApplication.translate("MainWindow", u"\u2744 \u6700\u4f4e\u6c14\u6e29\uff1a-- \u2103", None))
        self.humidity_s.setText(QCoreApplication.translate("MainWindow", u"\U0001f4a7 \U00007a7a\U00006c14\U00006e7f\U00005ea6\U0000ff1a-- %", None))
        self.rainfall_s.setText(QCoreApplication.translate("MainWindow", u"\U0001f327 \U0000964d\U000096e8\U000091cf\U0000ff1a-- mm", None))
        self.atmosphericP_s.setText(QCoreApplication.translate("MainWindow", u"\U0001f9ed \U00006c14\U0000538b\U0000ff1a-- hPa", None))
        self.riskrank_s.setText(QCoreApplication.translate("MainWindow", u"\U0001f525 \U0000706b\U0000707e\U000098ce\U00009669\U00007b49\U00007ea7\U0000ff1a\U00008ba1\U00007b97\U00004e2d...", None))
        self.time.setText(QCoreApplication.translate("MainWindow", u"\u5f53\u524d\u65f6\u95f4\uff1a00:00:00", None))
        self.date.setText(QCoreApplication.translate("MainWindow", u"\u65e5\u671f\uff1a2025/09/27", None))
        self.UAVFPV.setText(QCoreApplication.translate("MainWindow", u"\U0001f3a5 \U000065e0\U00004eba\U0000673a\U00005b9e\U00005730\U000063a2\U00006d4b (FPV)", None))
        self.INFOWARN.setText(QCoreApplication.translate("MainWindow", u"\U0001f6a8 \U0000542f\U000052a8\U00004fe1\U0000606f\U00009884\U00008b66\U00007cfb\U00007edf", None))
        self.search_pos_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u8f93\u5165\u8bbe\u5907\u90e8\u7f72\u533a\u57df / \u57ce\u5e02...", None))
        self.search_pos.setText(QCoreApplication.translate("MainWindow", u"\U0001f50d \U0000641c\U00007d22", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"\U0001f4a1 \U000063d0\U0000793a\U0000ff1a\U00008f93\U00005165\U00008bbe\U00005907\U00006240\U00005728\U00005730\U0000ff08\U00005982\U0000ff1a\U00005e7f\U00005dde\U00005e02\U00003001\U000068ee\U00006797\U00004e00\U0000533a\U0000ff09\U00005373\U000053ef\U00005feb\U0000901f\U00007b5b\U00009009\U00005de1\U000068c0\U00007f16\U0000961f", None))
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"\U0001f310 \U00005f53\U0000524d\U00007ba1\U00008f96\U00005de1\U000067e5\U0000533a\U000057df\U0000ff1a\U00005e7f\U00005dde\U00005e02\U00006797\U0000533a\U00007f16\U0000961f", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\U0001f681 \U00005de1\U0000822a\U000065e0\U00004eba\U0000673a - 01", None))
        self.label_15.setText("")
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 \U00008fd0\U0000884c\U000072b6\U00006001\U0000ff1a\U00005de1\U0000822a\U00005c31\U00007eea", None))
        self.condition.setText("")
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"\u26a1 \u5269\u4f59\u7535\u91cf\uff1a89%", None))
        self.gohome.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u952e\u8fd4\u822a", None))
        self.byhand_control.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\U0001f681 \U00005de1\U0000822a\U000065e0\U00004eba\U0000673a - 02", None))
        self.label_18.setText("")
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 \U00008fd0\U0000884c\U000072b6\U00006001\U0000ff1a\U00005de1\U0000822a\U00005c31\U00007eea", None))
        self.condition_2.setText("")
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"\u26a1 \u5269\u4f59\u7535\u91cf\uff1a87%", None))
        self.gohome_2.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u952e\u8fd4\u822a", None))
        self.byhand_control_2.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"\U0001f681 \U00005de1\U0000822a\U000065e0\U00004eba\U0000673a - 03", None))
        self.label_21.setText("")
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 \U00008fd0\U0000884c\U000072b6\U00006001\U0000ff1a\U00005de1\U0000822a\U00005c31\U00007eea", None))
        self.condition_3.setText("")
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"\u26a1 \u5269\u4f59\u7535\u91cf\uff1a90%", None))
        self.gohome_3.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u952e\u8fd4\u822a", None))
        self.byhand_control_3.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"\U0001f681 \U00005de1\U0000822a\U000065e0\U00004eba\U0000673a - 04", None))
        self.label_31.setText("")
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 \U00008fd0\U0000884c\U000072b6\U00006001\U0000ff1a\U00005de1\U0000822a\U00005c31\U00007eea", None))
        self.condition_6.setText("")
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"\u26a1 \u5269\u4f59\u7535\u91cf\uff1a89%", None))
        self.gohome_6.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u952e\u8fd4\u822a", None))
        self.byhand_control_6.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"\U0001f681 \U00005de1\U0000822a\U000065e0\U00004eba\U0000673a - 05", None))
        self.label_37.setText("")
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 \U00008fd0\U0000884c\U000072b6\U00006001\U0000ff1a\U00005de1\U0000822a\U00005c31\U00007eea", None))
        self.condition_8.setText("")
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"\u26a1 \u5269\u4f59\u7535\u91cf\uff1a87%", None))
        self.gohome_8.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u952e\u8fd4\u822a", None))
        self.byhand_control_8.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"\U0001f681 \U00005de1\U0000822a\U000065e0\U00004eba\U0000673a - 06", None))
        self.label_34.setText("")
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"\U0001f7e2 \U00008fd0\U0000884c\U000072b6\U00006001\U0000ff1a\U00005de1\U0000822a\U00005c31\U00007eea", None))
        self.condition_7.setText("")
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"\u26a1 \u5269\u4f59\u7535\u91cf\uff1a90%", None))
        self.gohome_7.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u952e\u8fd4\u822a", None))
        self.byhand_control_7.setText(QCoreApplication.translate("MainWindow", u"\u624b\u52a8\u63a7\u5236", None))
    # retranslateUi

