import sys
import code
from io import StringIO
from contextlib import redirect_stdout


class Interpreter(code.InteractiveConsole):
    def __init__(self, extra_context=dict()):
        """
        Init an interpreter, get globals and locals from current context.
        Define classic python prompt style.
        """
        context = globals().copy()
        context.update(locals().copy())
        context.update(extra_context.copy())
        super(Interpreter, self).__init__(context)
        self.inter_name = self.__class__.__name__
        self.write_slot = None
        self.input_slot = None
        self.more = 0
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        self.prompt = sys.ps1

    def write(self, data):
        """
        Override InteractiveConsole.write method to add a 'slot' connection, useful for different view implementation.
        :param data: str data to write
        :return:
        """
        if hasattr(self.write_slot, "__call__"):
            self.write_slot(data)
        else:
            super(Interpreter, self).write(data)

    def raw_input(self, prompt=""):
        """
        Override InteractiveConsole.raw_input method to add a 'slot' connection, useful for different view implementation.
        :param prompt: str prompt to write
        :return:
        """
        if hasattr(self.input_slot, "__call__"):
            self.input_slot(prompt)
        else:
            super(Interpreter, self).raw_input(prompt)

    def interact(self, banner=None, exitmsg=None):
        """
        Starting point for the interpreter. It is override for avoid while loop as classic shell. In this context
        interpreter doesn't use this functionality.
        :param banner: starter text
        :param exitmsg: no used
        :return:
        """
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            self.write("Python %s on %s\n%s\n(%s)\n" % (sys.version, sys.platform, cprt, self.inter_name))
        elif banner:
            self.write("%s\n" % str(banner))
        # run first prompt input.
        self.raw_input(self.prompt)

    def run(self, code):
        """
        Manage run code, like continue if : or ( with prompt switch >>> to ...
        :param code: str code to run
        :return:
        """
        self.more = self.push(code)
        if self.more:
            self.prompt = sys.ps2
        else:
            self.prompt = sys.ps1
        self.raw_input(self.prompt)

    def runcode(self, code):
        """
        Override InteractiveConsole.runcode method to manage stdout as a buffer. Useful for view implementation.
        :param code: str code to run
        :return:
        """
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        super(Interpreter, self).runcode(code)
        with sys.stdout as buf, redirect_stdout(buf):
            output = buf.getvalue()
            if bool(output and output.strip()):
                self.write(output)
        with sys.stderr as buf, redirect_stdout(buf):
            output = buf.getvalue()
            if bool(output and output.strip()):
                self.write(output)
        sys.stdout = old_stdout


