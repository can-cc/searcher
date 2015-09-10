# -*- coding: utf-8 -*-

import sys
import signal
import curses
import threading
import six

from searcher.display import Display
from searcher.keyhandler import KeyHandler


class TerminateLoop(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Precol(object):

    def __init__(self):
        pass

    def __enter__(self):
        #init curses and it'screen wrapper
        self.screen = curses.initscr()
        self.display = Display(self.screen, self.encoding)

        #keyhandler
        self.keyhandler = KeyHandler(self.screen)

        #create view
        self.view = SelectorView(percol=self)
        


if __name__ == '__main__':
    pass
