import os
import atexit
import readline
import rlcompleter
from PySide2 import QtCore, QtGui, QtWidgets

AUTOCOMPLETE_LIMIT = 20
AUTOCOMPLETE_SEPARATOR = "\n"

class Terminal(QtWidgets.QPlainTextEdit):

    # signal to connect at the interpreter run code
    press_enter = QtCore.Signal(str)

    def __init__(self, parent=None):
        """
        Micmic python terminal interpreter from a QPlainTextEdit. Can be override for app integration.
        Readline history is implemented, it's possible to change hist file path by define Terminal.hist_file attr.
        :param parent: parent widget
        """
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.setGeometry(50, 75, 600, 400)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.setUndoRedoEnabled(False)
        self.document().setDefaultFont(QtGui.QFont("monospace", 10, QtGui.QFont.Normal))
        self.prompt = None
        self.cursor_line = None
        self.hist_file = os.path.join(os.path.expanduser("~"), ".pyTermHist")
        self.init_history(self.hist_file)
        self.history_index = readline.get_current_history_length()
        self.completer = rlcompleter.Completer()

        # connection cursor line position
        self.cursorPositionChanged.connect(self.count_cursor_lines)

    def init_history(self, hist_file):
        """
        History initialisation with readline GNU, and use hook atexit for save history when program closing.
        :param hist_file: history file path
        :return:
        """
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(hist_file)
            except IOError:
                pass
            atexit.register(self.save_history, hist_file)

    def save_history(self, hist_file):
        """
        Hook def execute by atexit.
        :param hist_file: history file path 
        :return:
        """
        readline.set_history_length(1000)
        readline.write_history_file(hist_file)

    def write(self, data):
        """
        Append text to the Terminal. And keep cursor at the end.
        :param data: str data to write.
        :return: 
        """
        self.appendPlainText(data)
        self.moveCursor(QtGui.QTextCursor.End)

    def raw_input(self, prompt=None):
        """
        Use to write the prompt command.
        :param prompt: str prompt
        :return: 
        """
        if prompt is None:
            prompt = self.prompt
        self.write(prompt)

    def get_command(self):
        """
        Get command, read last line and remove prompt length.
        :return: str command
        """
        doc = self.document()
        current_line = (doc.findBlockByLineNumber(self.get_last_line() - 1).text())
        current_line = current_line.rstrip()
        current_line = current_line[len(self.prompt):]
        return current_line

    def get_last_line(self):
        """
        Get last terminal line.
        :return: str last line
        """
        doc = self.document()
        last_line = doc.lineCount()
        return last_line

    def get_cursor_position(self):
        """
        Get cursor position
        :return: int line cursor position.
        """
        return self.textCursor().columnNumber() - len(self.prompt)

    def remove_last_command(self):
        """
        Remove current command. Useful for display history navigation.
        :return:
        """
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        self.setTextCursor(cursor)

    def get_previous_history(self):
        """
        Get previous history in the readline GNU history file.
        :return: str history
        """
        self.history_index += 1
        if self.history_index >= readline.get_current_history_length():
            self.history_index = readline.get_current_history_length()
        return readline.get_history_item(self.history_index)

    def get_next_history(self):
        """
        Get next history in the readline GNU history file.
        :return: str history
        """
        if self.history_index <= 1:
            self.history_index = 1
        hist = readline.get_history_item(self.history_index)
        self.history_index -= 1
        return hist

    def autocomplete(self, command):
        """
        Ask different possibility from command arg, proposition is limited by AUTOCOMPLETE_LIMIT constant
        :param command: str
        :return: list of proposition
        """
        propositions = []
        completer = self.completer
        for i in range(AUTOCOMPLETE_LIMIT):
            ret = completer.complete(command, i)
            if ret:
                propositions.append(ret)
            else:
                break
        return propositions

    def write_autocomplete(self, command):
        """
        Prepare text to write.
        :param command: str command
        :return:
        """
        # Is = or space inside ?
        text_after_eq = command.split("=")[-1]
        text_strip = text_after_eq.strip()
        command_strip = text_strip.split(" ")[-1]
        propositions = self.autocomplete(command_strip)
        buffer = "--\n" + AUTOCOMPLETE_SEPARATOR.join(propositions)
        buffer = buffer.strip()
        if len(propositions) > 1:
            self.remove_last_command()
            self.write(buffer)
            self.raw_input(self.prompt + command)
        elif len(propositions) == 1:
            self.remove_last_command()
            # Replace text by last proposition
            command = command.replace(command_strip, propositions[0])
            self.write(self.prompt + command)
        else:
            return

    @QtCore.Slot()
    def count_cursor_lines(self):
        """
        Slot def keep tracking cursor position line number. Useful to compare position to know if it is an
        editable line or not.
        :return:
        """
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        lines = 1
        while cursor.positionInBlock() > 0:
            cursor.movePosition(QtGui.QTextCursor.Up)
            lines += 1
        block = cursor.block().previous()
        while block.isValid():
            lines += block.lineCount()
            block = block.previous()
        self.cursor_line = lines

    def keyPressEvent(self, event):
        """
        Override to manage key board event.
        :param event: event key.
        :return:
        """
        # Is an editable line ? if not go to the last line.
        if self.cursor_line != self.get_last_line() and not self.textCursor().hasSelection():
            self.moveCursor(QtGui.QTextCursor.End)
        # Enter key pressed to run code.
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            cmd = self.get_command()
            self.press_enter.emit(cmd)
            # add to the history.
            if bool(cmd and cmd.strip()):
                readline.add_history(cmd)
                self.history_index = readline.get_current_history_length()
            return
        # Avoid delete prompt or text before.
        elif event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Backspace):
            if self.get_cursor_position() == 0:
                return
        # History navigation.
        elif event.key() == QtCore.Qt.Key_Down:
            self.remove_last_command()
            self.raw_input(self.prompt + self.get_previous_history())
            return
        elif event.key() == QtCore.Qt.Key_Up:
            self.remove_last_command()
            self.raw_input(self.prompt + self.get_next_history())
            return
        # Tab autocomplete
        elif event.key() == QtCore.Qt.Key_Tab:
            cmd = self.get_command()
            if bool(cmd and cmd.strip()):
                self.write_autocomplete(cmd)
            return
        super(Terminal, self).keyPressEvent(event)
