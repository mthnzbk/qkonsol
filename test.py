from qkonsol import QKonsol
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon



app = QApplication([])
konsol = QKonsol()
konsol.setWindowIcon(QIcon("terminal.svg"))
konsol.show()
app.exec_()