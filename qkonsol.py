from PySide2.QtCore import QProcess, Qt
from PySide2.QtGui import QFontMetrics, QKeyEvent, QPalette, QColor
from PySide2.QtWidgets import QPlainTextEdit, QFrame
import sys
import ctypes


class QKonsol(QPlainTextEdit):

    userTextEntry = ""
    commandList = [""]
    length = 0

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.setWindowTitle(self.tr("Terminal"))
        self.setCursorWidth(7)
        font = self.font()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.setFont(font)
        self.setUndoRedoEnabled(False)
        palette = QPalette()
        palette.setColor(QPalette.Base, Qt.black)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Highlight, Qt.white)
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setFrameShape(QFrame.NoFrame)
        self.setPalette(palette)
        self.resize(720, 480)

        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.setReadChannel(QProcess.StandardOutput)

        self.process.readyReadStandardOutput.connect(self.readStandartOutput)
        self.cursorPositionChanged.connect(self.cursorPosition)


        if sys.platform == "win32":
            self.process.start("powershell.exe", mode=QProcess.ReadWrite)

        else:
            self.process.start("./bin/bash", mode=QProcess.ReadWrite)




    def readStandartOutput(self):
        st = self.process.readAllStandardOutput().data().decode(str(ctypes.cdll.kernel32.GetConsoleOutputCP()))
        # ss = QTextStream(st)
        # ss.setCodec(ctypes.cdll.kernel32.GetConsoleOutputCP())
        # ss = ss.readAll()
        # print(st,self.commandList[-1] == ss)
        if self.commandList[-1] != st:
            self.appendPlainText(st)


    def keyPressEvent(self, event: QKeyEvent):

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.userTextEntry += "\r\n"
            print(repr(self.userTextEntry))
            self.commandList.append(self.userTextEntry)
            self.length = len(self.userTextEntry)
            self.process.writeData(self.userTextEntry, self.length)
            self.userTextEntry = ""

        elif event.key() == Qt.Key_Backspace:
            if self.userTextEntry == "":
                return

            else:
                self.userTextEntry = self.userTextEntry[:-1]
                super().keyPressEvent(event)


        elif event.modifiers() != Qt.ControlModifier:
            super().keyPressEvent(event)
            self.userTextEntry += event.text()


    def cursorPosition(self):
        pass


    def closeEvent(self, event):
        self.process.close()