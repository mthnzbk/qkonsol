from PySide2.QtCore import QProcess, Qt, QDir
from PySide2.QtGui import QFontMetrics, QKeyEvent, QPalette, QColor, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit, QFrame
import sys
import ctypes


class QKonsol(QPlainTextEdit):

    userTextEntry = ""
    commandList = ["cd " + QDir.homePath()]
    length = 0
    history = -1

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.setWindowTitle(self.tr("Terminal"))
        self.setCursorWidth(7)
        self.setContextMenuPolicy(Qt.NoContextMenu)
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

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.setReadChannel(QProcess.StandardOutput)

        self.process.readyReadStandardOutput.connect(self.readStandartOutput)
        self.process.readyReadStandardError.connect(lambda : print(self.readAllStandartError()))
        self.cursorPositionChanged.connect(self.cursorPosition)
        self.textChanged.connect(self.whatText)


        if sys.platform == "win32":
            self.process.start("cmd.exe", [], mode=QProcess.ReadWrite)

        else:
            self.process.start("bash", ["-i"], mode=QProcess.ReadWrite) # bash -i interactive mode




    def readStandartOutput(self):
        if sys.platform == "win32":
            st = self.process.readAllStandardOutput().data().decode(str(ctypes.cdll.kernel32.GetConsoleOutputCP()))

        else:
            st = self.process.readAllStandardOutput().data().decode("utf-8")

        # print(repr(st), self.commandList)
        if not st.startswith(self.commandList[-1]):
            self.appendPlainText(st)


    def __line_end(self):
        if sys.platform == "win32":
            return "\r\n"

        elif sys.platform == "linux":
            return "\n"

        elif sys.platform == "darwin":
            return "\r"


    def keyPressEvent(self, event: QKeyEvent):

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if self.commandList[-1] != self.userTextEntry and self.userTextEntry != "":
                self.commandList.append(self.userTextEntry)

            self.length = len(self.userTextEntry + self.__line_end())
            self.process.writeData(self.userTextEntry + self.__line_end(), self.length)
            self.userTextEntry = ""

        elif event.key() == Qt.Key_Backspace:
            if self.userTextEntry == "":
                return

            else:
                self.userTextEntry = self.userTextEntry[:-1]
                super().keyPressEvent(event)

        elif event.key() == Qt.Key_Up:
            if -len(self.commandList) < self.history:
                self.history -= 1
                print(self.commandList[self.history])
            return

        elif event.key() == Qt.Key_Down:
            if self.history < -1:
                self.history += 1
                print(self.commandList[self.history])
            return

        elif event.key() == Qt.Key_Delete:
            return

        elif event.modifiers() == Qt.ControlModifier:
            super().keyPressEvent(event)

        else:
            super().keyPressEvent(event)
            self.userTextEntry += event.text()


    def cursorPosition(self): pass
        # print(self.textCursor().position())




    def whatText(self): pass
        # print(self.blockCount())


    def insertFromMimeData(self, source):
        super().insertFromMimeData(source)
        self.userTextEntry += source.text()

    def mouseReleaseEvent(self, event):
        super().mousePressEvent(event)
        cur = self.textCursor()

        if event.button() == Qt.LeftButton:
            cur.movePosition(QTextCursor.End, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cur)


    def closeEvent(self, event):
        self.process.close()