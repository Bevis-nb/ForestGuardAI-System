# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'controlSUYAMC.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
from Gui import resourse_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(960, 640)
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"	background-color: #11111b;\n"
"}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.centralwidget)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"QFrame#frame_3 {\n"
"	background-color: #11111b;\n"
"}")
        self.frame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout_4 = QVBoxLayout(self.frame_3)
        self.verticalLayout_4.setSpacing(15)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(20, 20, 20, 20)
        self.verticalSpacer = QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.label = QLabel(self.frame_3)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(160, 36))
        self.label.setStyleSheet(u"QLabel {\n"
"	color: #f38ba8;\n"
"	background-color: rgba(243, 139, 168, 0.12);\n"
"	border: 1px solid rgba(243, 139, 168, 0.3);\n"
"	border-radius: 18px;\n"
"	font: 700 11pt \"Microsoft YaHei UI\";\n"
"	padding-left: 15px;\n"
"	padding-right: 15px;\n"
"}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.verticalSpacer_2 = QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"QFrame#frame_4 {\n"
"	background-color: transparent;\n"
"}")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout = QHBoxLayout(self.frame_4)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.frame_4)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QFrame#frame {\n"
"	background-color: #1e1e2e;\n"
"	border: 1px solid #313244;\n"
"	border-radius: 12px;\n"
"}\n"
"QLabel {\n"
"	color: #cdd6f4;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(15, 15, 15, 15)
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 2)

        self.label_10 = QLabel(self.frame)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(20, 20))
        self.label_10.setMaximumSize(QSize(20, 20))
        self.label_10.setStyleSheet(u"border-image: url(:/image/image/\u5411\u4e0a.png);")

        self.gridLayout.addWidget(self.label_10, 1, 2, 1, 1)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_13 = QLabel(self.frame)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(20, 20))
        self.label_13.setMaximumSize(QSize(20, 20))
        self.label_13.setStyleSheet(u"border-image: url(:/image/image/\u5411\u5de6.png);")

        self.gridLayout.addWidget(self.label_13, 2, 1, 1, 1)

        self.label_11 = QLabel(self.frame)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(20, 20))
        self.label_11.setMaximumSize(QSize(20, 20))
        self.label_11.setStyleSheet(u"border-image: url(:/image/image/\u5411\u53f3.png);")

        self.gridLayout.addWidget(self.label_11, 2, 3, 1, 1)

        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 4, 1, 1)

        self.label_12 = QLabel(self.frame)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(20, 20))
        self.label_12.setMaximumSize(QSize(20, 20))
        self.label_12.setStyleSheet(u"border-image: url(:/image/image/\u5411\u4e0b.png);")

        self.gridLayout.addWidget(self.label_12, 3, 2, 1, 1)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_3, 4, 2, 1, 2)


        self.horizontalLayout.addWidget(self.frame)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.verticalLayout_2.addItem(self.horizontalSpacer)

        self.label_18 = QLabel(self.frame_4)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setStyleSheet(u"QLabel {\n"
"	color: #a6adc8;\n"
"	background-color: #1e1e2e;\n"
"	border: 1px solid #313244;\n"
"	border-radius: 6px;\n"
"	padding: 6px 12px;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.label_18.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_18, 0, Qt.AlignmentFlag.AlignVCenter)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.frame_2 = QFrame(self.frame_4)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"QFrame#frame_2 {\n"
"	background-color: #1e1e2e;\n"
"	border: 1px solid #313244;\n"
"	border-radius: 12px;\n"
"}\n"
"QLabel {\n"
"	color: #cdd6f4;\n"
"	font: 9pt \"Microsoft YaHei UI\";\n"
"}")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.gridLayout_2 = QGridLayout(self.frame_2)
        self.gridLayout_2.setSpacing(8)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(15, 15, 15, 15)
        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_6, 0, 2, 1, 2)

        self.label_15 = QLabel(self.frame_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setMinimumSize(QSize(20, 20))
        self.label_15.setMaximumSize(QSize(20, 20))
        self.label_15.setStyleSheet(u"border-image: url(:/image/image/\u5411\u4e0a.png);")

        self.gridLayout_2.addWidget(self.label_15, 1, 2, 1, 1)

        self.label_9 = QLabel(self.frame_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 2, 0, 1, 1)

        self.label_16 = QLabel(self.frame_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setMinimumSize(QSize(20, 20))
        self.label_16.setMaximumSize(QSize(20, 20))
        self.label_16.setStyleSheet(u"border-image: url(:/image/image/\u5411\u5de6.png);")

        self.gridLayout_2.addWidget(self.label_16, 2, 1, 1, 1)

        self.label_14 = QLabel(self.frame_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(20, 20))
        self.label_14.setMaximumSize(QSize(20, 20))
        self.label_14.setStyleSheet(u"border-image: url(:/image/image/\u5411\u53f3.png);")

        self.gridLayout_2.addWidget(self.label_14, 2, 3, 1, 1)

        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 2, 4, 1, 1)

        self.label_17 = QLabel(self.frame_2)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(20, 20))
        self.label_17.setMaximumSize(QSize(20, 20))
        self.label_17.setStyleSheet(u"border-image: url(:/image/image/\u5411\u4e0b.png);")

        self.gridLayout_2.addWidget(self.label_17, 3, 2, 1, 1)

        self.label_8 = QLabel(self.frame_2)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_8, 4, 2, 1, 2)


        self.horizontalLayout.addWidget(self.frame_2)


        self.verticalLayout_4.addWidget(self.frame_4)


        self.verticalLayout.addWidget(self.frame_3)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u8bbe\u5907\u63a7\u5236\u7ec8\u7aef", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u25cf \u672a\u8fde\u63a5\u8bbe\u5907", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"W\uff1a\u524d\u79fb", None))
        self.label_10.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"A\uff1a\u5de6\u79fb", None))
        self.label_13.setText("")
        self.label_11.setText("")
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"D\uff1a\u53f3\u79fb", None))
        self.label_12.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"S\uff1a\u540e\u79fb", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"\u6309 ESC \u952e\u53ef\u9000\u51fa\u7a0b\u5e8f", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"I\uff1a\u4e0a\u5347", None))
        self.label_15.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"J\uff1a\u5de6\u65cb", None))
        self.label_16.setText("")
        self.label_14.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"L\uff1a\u53f3\u65cb", None))
        self.label_17.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"K\uff1a\u4e0b\u964d", None))
    # retranslateUi

