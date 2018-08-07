from PySide2.QtWidgets import QApplication
from viewimplementation import terminal
from pyinterpreter import interpreter


class TerminalPython(terminal.Terminal):
    def __init__(self, parent=None):
        super(TerminalPython, self).__init__(parent=parent)
        # Init interpreter and add globals to context that give access from it.
        self.interpreter = interpreter.Interpreter(extra_context=globals().copy())
        # connect write and input interpreter to the view implementation.
        self.interpreter.write_slot = self.write
        self.interpreter.input_slot = self.raw_input
        # define prompt
        self.prompt = self.interpreter.prompt
        # connect enter signal to interpreter
        self.press_enter.connect(self.interpreter.run)
        # rename interpreter
        self.interpreter.inter_name = "ThonSide Interpreter"
        # start interpreter
        self.interpreter.interact()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    console = TerminalPython()
    console.show()
    sys.exit(app.exec_())
