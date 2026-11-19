from PySide6.QtWidgets import QMainWindow,QApplication
from PySide6.QtCore import  Qt
from Gui.control_ui import Ui_MainWindow

class Control(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.showMaximized()
    
    #按下esc出去
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication()
    control = Control()
    control.show()
    app.exec_()