# -*- coding: utf-8 -*-

import searcher.info

__doc__  = info.__doc__
__version__ = info.__version__
__logo__ = info.__logo__

import sys
import signal
import curses
import threading
import six



class TerminateLoop(Exception):
	def __init__(self, value):
		self.value = value;

	def __str__(self):
		return repr(self.value)
