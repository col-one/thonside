from PySide2.QtWidgets import QApplication
from viewimplementation import terminal
from pyinterpreter import interpreter


class TerminalPython(terminal.Terminal):
    def __init__(self, parent=None):
        super(TerminalPython, self).__init__(parent=parent)
        self.interpreter = interpreter.Interpreter()
        # connect write and input interpreter to the view implementation.
        self.interpreter.write_slot = self.write
        self.interpreter.raw_input = self.raw_input
        # define prompt
        self.prompt = self.interpreter.prompt
        # connect enter signal to interpreter
        self.press_enter.connect(self.interpreter.run)
        # start interpreter
        self.interpreter.interact()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    console = TerminalPython()
    console.show()
    sys.exit(app.exec_())
