# -*- coding: utf-8 -*-
from percol.action import action
import subprocess
import six


def double_quote_string(string):
    return '"' + string.replace('"', r'\"') + '"'


def get_raw_stream(stream):
    if six.PY2:
        return stream
    else:
        return stream.buffer

@action()
def select_to_open_vim(selected_actions, percol):
    "select_to_open_vim"
    for selected_action in selected_actions:
        goto_line_param = '+' + str(selected_action[4])
        subprocess.call(['vim', goto_line_param, selected_action[3]])
