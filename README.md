
# ThonSide

Python interpreter embeddable in a PySide2 widget.

![alt text](https://raw.githubusercontent.com/col-one/thonside/master/img/thonside_repr.png)

Compatible PySide2 and Python3.

Interpreter embedded in a QPlainTextEdit widget. 

Here an example (./viewimplementation/widget_example.py) how to implement it : 

```python
from PySide2.QtWidgets import QApplication
from viewimplementation import terminal
from pyinterpreter import interpreter


class TerminalPython(terminal.Terminal):
    def __init__(self, parent=None):
        super(TerminalPython, self).__init__(parent=parent)
        self.interpreter = interpreter.Interpreter()
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
```

## **.Fork It Code It Share It.**

Thanks
