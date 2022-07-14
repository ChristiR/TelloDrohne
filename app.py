import sys
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.QtCore import Qt
import tellopy_modified as tello
import subprocess
from hsv_widget import *
from settings_widget import *
from video_stream import ThreadRunStream
from PIL import Image

# variable to store reference to the drone
drone = tello.Tello()


class MainWindow(QMainWindow):
    # Basis-Gerüst für GUI-Fenster

    def __init__(self):
        super().__init__()
        self.initUI()
        drone.set_main_window(self)

    def initUI(self):
        # Werte für den HSV-Bereich, der das Objekt das erkannt werden soll beschreibt
        self.colorUpper = (74, 203, 164)
        self.colorLower = (62, 89, 75)
        self.video_thread = None

        self.setWindowTitle("Tello Drohne")
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.StyledPanel)
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.StyledPanel)
        splitter = QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setSizes([60, 200])
        bottom_frame = QFrame(self)
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        splitter_bottom = QSplitter(Qt.Vertical)
        splitter_bottom.addWidget(splitter)
        splitter_bottom.addWidget(bottom_frame)
        splitter_bottom.setSizes([300, 50])

        # Buttons für das Menü
        self.btn_take_off = QPushButton("Take off")
        self.btn_take_off.clicked.connect(self.button_take_off)
        self.btn_take_off.setDisabled(True)
        self.btn_stream = QPushButton("Start stream")
        self.btn_stream.clicked.connect(self.button_stream)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.button_stop)
        self.btn_stop.setDisabled(True)
        self.btn_state = QPushButton("State")
        self.btn_state.clicked.connect(self.button_state)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.checkWifi)
        layout_left = QVBoxLayout()
        layout_left.addWidget(self.btn_take_off)
        layout_left.addWidget(self.btn_stream)
        layout_left.addWidget(self.btn_stop)
        layout_left.addWidget(self.btn_state)
        layout_left.addWidget(self.btn_refresh, alignment=QtCore.Qt.AlignBottom)
        left_frame.setLayout(layout_left)

        # Tabs für HSV-Einstellungen und Parameter-Einstellungen
        self.tab_1 = QLabel("Press 'Connect' to start")
        self.tab_1.setAlignment(Qt.AlignCenter)
        self.tab_2 = HsvWidget(window=self, drone=drone)
        self.right_widget = QTabWidget()
        self.tab_3 = SettingsWidget(window=self)
        self.right_widget = QTabWidget()
        self.right_widget.addTab(self.tab_1, "Video stream")
        self.right_widget.addTab(self.tab_2, "HSV Color")
        self.right_widget.addTab(self.tab_3, "Settings")
        self.tab_1.setContentsMargins(0, 0, 0, 0)
        layout_right = QVBoxLayout()
        layout_right.addWidget(self.right_widget)
        right_frame.setLayout(layout_right)
        # linkes Textfeld (Consolenfenster)
        self.loggingTextBox = QPlainTextEdit()
        self.loggingTextBox.setStyleSheet("QTextEdit {color:red}")
        self.loggingTextBox.setReadOnly(True)
        #rechtes Textfeld (Consolenfenster)
        self.loggingConsole = QPlainTextEdit()
        self.loggingConsole.setStyleSheet("QTextEdit {color:red}")
        self.loggingConsole.setReadOnly(True)
        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(self.loggingTextBox)
        layout_bottom.addWidget(self.loggingConsole)
        layout_bottom.setContentsMargins(0, 0, 0, 0)
        bottom_frame.setLayout(layout_bottom)
        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter_bottom)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setGeometry(400, 200, 1100, 700)
        self.setFixedWidth(1100)
        self.setFixedHeight(740)
        self.checkWifi()
        self.show()
        self.loadHsvValues()

    # Lädt die HSV-Werte aus der json Datei
    def loadHsvValues(self):
        with open('res/hsv.json') as f:
            data = json.load(f)
            self.colorUpper = tuple(data["hsv"]["colorUpper"])
            self.colorLower = tuple(data["hsv"]["colorLower"])

    # Diese Methode kann aufgerufen werden um die lower und upper HSV-Werte für den Video-Stream zu aktualisieren
    def updateLowerUpper(self, lower, upper):
        self.colorLower = lower
        self.colorUpper = upper
        if self.video_thread is not None:
            self.video_thread.updateLowerUpper(self.colorLower, self.colorUpper)

    # Fügt eine neue Zeile mit Text im linken Textfeld hinzu
    def addNewLogLine(self, text):
        now = datetime.now()
        ts = ("%02d:%02d:%02d.%03d" % (now.hour, now.minute, now.second, now.microsecond / 1000))
        self.loggingTextBox.appendPlainText(f"{ts}: {text}")
        self.loggingTextBox.verticalScrollBar().maximum()
        self.loggingTextBox.verticalScrollBar().setValue(10)

    # Fügt eine neue Zeile mit Text im rechten Textfeld hinzu
    def addNewLogLineRight(self, text):
        self.loggingConsole.appendPlainText(text)
        self.loggingConsole.verticalScrollBar().maximum()
        self.loggingConsole.verticalScrollBar().setValue(10)

    # Überprüft ob die Drohne mit dem Computer verbunden ist, auf dem das Programm ausgeführt wird
    def checkWifi(self):
        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
        if b"TELLO" in wifi:
            self.addNewLogLine("TELLO drone WIFI connected")
            self.btn_stream.setDisabled(False)
            self.btn_state.setDisabled(False)
        else:
            self.addNewLogLine("TELLO drone is not connected. Hit refresh to check again")
            self.btn_take_off.setDisabled(True)
            self.btn_stream.setDisabled(True)
            self.btn_stop.setDisabled(True)
            self.btn_state.setDisabled(True)

    @pyqtSlot(QImage)
    # Zeigt den Stream an
    def setStream(self, image):
        # Video in PyQt5 in other thread:
        # https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv
        self.tab_1.setPixmap(QPixmap.fromImage(image))

    # Button zum Abheben der Drohne
    def button_take_off(self):
        drone.connect()
        drone.takeoff()
        self.btn_stop.setDisabled(False)
        self.btn_take_off.setDisabled(True)
        self.right_widget.setTabEnabled(1, False)
        self.addNewLogLine(f"Take off")

    # Button um den Stream zu starten
    def button_stream(self):
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.addNewLogLine("Starting video stream...")
        self.video_thread = ThreadRunStream.instance()
        self.video_thread.set_params(self, drone, self.colorUpper, self.colorLower)
        self.video_thread.videoStream.connect(self.setStream)
        self.video_thread.start()
        self.btn_take_off.setDisabled(False)
        self.right_widget.setTabEnabled(1, True)
        self.btn_stream.setDisabled(True)

    # Button zum Landen der Drohne
    def button_stop(self):
        self.addNewLogLine("Landing...")
        self.btn_take_off.setDisabled(False)
        self.btn_stop.setDisabled(True)
        self.right_widget.setTabEnabled(1, True)
        drone.land()

    # Button um den Status der Drohne abzufragen
    def button_state(self):
        drone.connect()
        self.addNewLogLine(f"{drone.state}".replace("::", " "))
        QApplication.setOverrideCursor(Qt.ArrowCursor)

    # Wenn das Fenster geschlossen werden soll, müssen zuerst noch einige Verbindungen sauber getrennt werden
    def closeEvent(self, event):
        try:
            drone.quit()
            self.video_thread.stop()
        except:
            self.video_thread = None
        try:
            app.exit()
            event.accept()
            sys.exit()
        except:
            print(sys.exc_info()[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QTextEdit {color:red}")
    app.setQuitOnLastWindowClosed(True)
    ex = MainWindow()
    sys.exit(app.exec_())
