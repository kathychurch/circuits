# Module:   debugger
# Date:     5th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Debugger Tests"""

from StringIO import StringIO

from circuits import Debugger
from circuits.core import Event, Component


class Test(Event):
    """Test Event"""

class App(Component):

    raiseException = False

    def __tick__(self):
        if self.raiseException:
            raise Exception()

    def test(self, raiseException=False):
        if raiseException:
            raise Exception()

class Logger(object):

    msg = None

    def debug(self, msg):
        self.msg = msg

    error = debug

def test():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    e = Event()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    assert not debugger.events

    e = Event()
    app.push(e)

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

def test_exceptions():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events
    assert debugger.errors

    e = Test(raiseException=True)
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s.startswith("<Error[*:exception]")
    stderr.seek(0)
    stderr.truncate()

    debugger.events = False
    debugger.errors = False

    assert not debugger.events
    assert not debugger.errors

    e = Test(raiseException=True)
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""

def test_tick_exceptions():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events
    assert debugger.errors

    app.raiseException = True
    app.tick()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s.startswith("<Error[*:exception] [<type 'exceptions.Exception'>, Exception(), <traceback object")
    stderr.seek(0)
    stderr.truncate()

    app.flush()
    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""

def test_IgnoreEvents():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events

    debugger.IgnoreEvents.extend([Test])

    e = Event()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = Test()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

def test_IgnoreChannels():
    app = App()
    stderr = StringIO()
    debugger = Debugger(file=stderr)
    debugger.register(app)
    while app:
        app.flush()
    stderr.seek(0)
    stderr.truncate()

    assert debugger.events
    debugger.IgnoreChannels.extend([("*", "test")])

    e = Event()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == str(e)
    stderr.seek(0)
    stderr.truncate()

    e = Test()
    app.push(e)
    app.flush()

    stderr.seek(0)
    s = stderr.read().strip()
    assert s == ""
    stderr.seek(0)
    stderr.truncate()

def test_Logger_debug():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while app:
        app.flush()

    e = Event()
    app.push(e)
    app.flush()

    assert logger.msg == repr(e)

def test_Logger_error():
    app = App()
    logger = Logger()
    debugger = Debugger(logger=logger)
    debugger.register(app)
    while app:
        app.flush()

    e = Test(raiseException=True)
    app.push(e)
    app.flush()
    app.flush()
    assert logger.msg.startswith("ERROR <listener on ('test',) {target=None, priority=0.0}> (<type 'exceptions.Exception'>):")
