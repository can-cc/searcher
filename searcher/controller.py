# -*- coding: utf-8 -*-
import sys
import signal
import curses
import threading
import six

from searcher.display import Display
from searcher.key import KeyHandler
from searcher.finder import FinderMultiQueryString
from searcher.search import SearcherMulitQuery
from searcher.view import SelectorView
from searcher.model import SelectorModel
from searcher.command import SelectorCommand
from searcher import debug, key, actions


class TerminateLoop(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Controller(object):

    # caret is '插入符号'
    def __init__(self, descriptors=None, encoding="utf-8",
                 actions=None,
                 query=None, caret=None, index=None):

        self.global_lock = threading.Lock()
        self.encoding = encoding
        self.actions = actions
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        searcher = SearcherMulitQuery

        self.model_candidate = SelectorModel(percol=self,
                                             searcher=searcher,
                                             caret=caret,
                                             index=index)
        self.model = self.model_candidate

    def __enter__(self):
        # init curses and it'screen wrapper
        self.screen = curses.initscr()
        self.display = Display(self.screen, self.encoding)

        # keyhandler
        self.keyhandler = KeyHandler(self.screen)

        # create view
        self.view = SelectorView(percol=self)
        self.command_candidate = SelectorCommand(
            self.model_candidate, self.view)

        signal.signal(signal.SIGINT, lambda signum, frame: None)
        # handle special keys like <f1>, <down>, ...
        self.screen.keypad(True)

        curses.raw()
        curses.noecho()
        curses.cbreak()
        # Leave newline mode. Make percol distinguish between "C-m" and "C-j".
        curses.nonl()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        curses.nl()
        curses.endwin()
        self.execute_action()

    args_for_action = None

    def execute_action(self):
        selected_actions = self.model.get_selected_results_with_index()
        try:
            action = self.actions
            if action:
                action.act(
                    selected_actions, self)
        except Exception as e:
            debug.log("execute_action", e)

    # ============================================================ #
    # Statuses
    # ============================================================ #
    @property
    def command(self):
        return self.command_candidate

    SEARCH_DELAY = 0.5

    def loop(self):
        self.view.refresh_display()
        self.result_updating_timer = None

        def search_and_refresh_display():
            self.model.do_search(self.model.query)
            self.view.refresh_display()

        while True:
            try:
                self.handle_key(self.screen.getch())
                if self.model.should_search_again():
                    # search again
                    with self.global_lock:
                        # critical section
                        if not self.result_updating_timer is None:
                            # clear timer
                            self.result_updating_timer.cancel()
                            self.result_updating_timer = None

                        # with bounce
                        t = threading.Timer(
                            self.SEARCH_DELAY, search_and_refresh_display)
                        self.result_updating_timer = t
                        t.start()

                self.view.refresh_display()
            except TerminateLoop as e:
                return e.value

    # ============================================================ #
    # Key Handling
    # ============================================================ #

    keymap = {
        "C-i": lambda percol: percol.switch_model(),
        # text
        "C-h": lambda percol: percol.command.delete_backward_char(),
        "<backspace>": lambda percol: percol.command.delete_backward_char(),
        "C-w": lambda percol: percol.command.delete_backward_word(),
        "C-u": lambda percol: percol.command.clear_query(),
        "<dc>": lambda percol: percol.command.delete_forward_char(),
        # caret
        "<left>": lambda percol: percol.command.backward_char(),
        "<right>": lambda percol: percol.command.forward_char(),
        # line
        "<down>": lambda percol: percol.command.select_next(),
        "<up>": lambda percol: percol.command.select_previous(),
        # page
        "<npage>": lambda percol: percol.command.select_next_page(),
        "<ppage>": lambda percol: percol.command.select_previous_page(),
        # top / bottom
        "<home>": lambda percol: percol.command.select_top(),
        "<end>": lambda percol: percol.command.select_bottom(),
        # mark
        "C-SPC": lambda percol: percol.command.toggle_mark_and_next(),
        # finish
        "RET": lambda percol: percol.finish(),  # Is RET never sent?
        "C-m": lambda percol: percol.finish(),
        "C-j": lambda percol: percol.finish(),
        "C-c": lambda percol: percol.cancel()
    }

    def import_keymap(self, keymap, reset=False):
        if reset:
            self.keymap = {}
        else:
            self.keymap = dict(self.keymap)
        for key, cmd in six.iteritems(keymap):
            self.keymap[key] = cmd

    # default
    last_key = None

    def handle_key(self, ch):
        if ch == curses.KEY_RESIZE:
            self.last_key = self.handle_resize(ch)
        elif ch != -1 and self.keyhandler.is_utf8_multibyte_key(ch):
            self.last_key = self.handle_utf8(ch)
        else:
            self.last_key = self.handle_normal_key(ch)

    def handle_resize(self, ch):
        self.display.update_screen_size()
        # XXX: trash -1 (it seems that resize key sends -1)
        self.keyhandler.get_key_for(self.screen.getch())
        return key.SPECIAL_KEYS[ch]

    def handle_utf8(self, ch):
        ukey = self.keyhandler.get_utf8_key_for(ch)
        self.model.insert_string(ukey)
        return ukey.encode(self.encoding)

    def handle_normal_key(self, ch):
        k = self.keyhandler.get_key_for(ch)
        if k in self.keymap:
            self.keymap[k](self)
        elif self.keyhandler.is_displayable_key(ch):
            self.model.insert_char(ch)
        return k

    # ------------------------------------------------------------ #
    # Finish / Cancel
    # ------------------------------------------------------------ #

    def finish(self):
        # save selected candidates and use them later (in execute_action)
        raise TerminateLoop(self.finish_with_exit_code())          # success

    def cancel(self):
        raise TerminateLoop(self.cancel_with_exit_code())          # failure

    def finish_with_exit_code(self):
        self.args_for_action = self.model_candidate.\
            get_selected_results_with_index()
        return 0

    def cancel_with_exit_code(self):
        return 1


if __name__ == '__main__':

    def getnumbers(n):
        for x in six.moves.range(1, n):
            yield '1234'
    candidate_finder_class = action_finder_class = FinderMultiQueryString
    acts = actions.select_to_open_vim
    candidates = getnumbers(20)
    with Controller(actions=acts) as percol:
        exit_code = percol.loop()
    exit(exit_code)
