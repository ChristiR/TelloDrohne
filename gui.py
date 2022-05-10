from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton


app = QApplication([])

window = QWidget()
window.resize(900,600)
window.setWindowTitle("Tello Drohne")
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec()