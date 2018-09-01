import sys
import code
from io import StringIO
from queue import Queue
from contextlib import redirect_stdout


class Streamer(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        if bool(text and text.strip()):
            text = text.replace("\n", "")
            self.queue.put(text)

    def flush(self):
        pass


class Interpreter(code.InteractiveConsole):
    def __init__(self, extra_context=dict(), stream_out=True, stream_err=True):
        """
        Init an interpreter, get globals and locals from current context.
        Define classic python prompt style.
        """
        context = globals().copy()
        context.update(locals().copy())
        context.update(extra_context.copy())
        #
        super(Interpreter, self).__init__(context)
        self.inter_name = self.__class__.__name__
        self.queue = Queue()
        self.streamer_out = Streamer(self.queue)
        self.streamer_err = Streamer(self.queue)
        sys.stdout = self.streamer_out if stream_out else sys.__stdout__
        sys.stderr = self.streamer_err if stream_err else sys.__stderr__
        self.write_slot = self.queue.put
        self.input_slot = self.queue.put
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
        super(Interpreter, self).runcode(code)
        # with sys.stdout as buf, redirect_stdout(buf):
        #     output = buf.getvalue()
        #     if bool(output and output.strip()):
        #         self.write(output)
        # with sys.stderr as buf, redirect_stdout(buf):
        #     output = buf.getvalue()
        #     if bool(output and output.strip()):
        #         self.write(output)
        # sys.stdout = old_stdout


