from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from viewimplementation import terminal
from pyinterpreter import interpreter


class TerminalPython(terminal.Terminal):
    def __init__(self, parent=None):
        super(TerminalPython, self).__init__(parent=parent)
        # Init interpreter and add globals to context that give access from it.
        self.interpreter = interpreter.Interpreter(extra_context=globals().copy(), stream_err=True, stream_out=True)
        # active queue thread with queue interpreter
        self.active_queue_thread(self.interpreter.queue)
        # define prompt
        self.prompt = self.interpreter.prompt
        # rename interpreter
        self.interpreter.inter_name = "ThonSide Interpreter"
        self.def_to_run_code = self.interpreter.run
        # start interpreter
        self.interpreter.interact()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    console = TerminalPython()
    console.show()

    sys.exit(app.exec_())
