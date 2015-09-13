# -*- coding: utf-8 -*-

import sys
import os
import locale
import six

from optparse import OptionParser

import searcher
from searcher import ansi

from searcher import tty


class LoadRunCommandFileError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return "Error in rc.py: " + str(self.error)


def setup_options(parser):
    parser.add_option("--tty", dest="tty",
                      help="path to the TTY (usually, the value of $TTY)")
    parser.add_option("--rcfile", dest="rcfile",
                      help="path to the settings file")
    parser.add_option("--output-encoding", dest="output_encoding",
                      help="encoding for output")
    parser.add_option("--input-encoding", dest="input_encoding", default="utf8",
                      help="encoding for input and output (default 'utf8')")
    parser.add_option("-v", "--invert-match", action="store_true", dest="invert_match", default=False,
                      help="select non-matching lines")
    parser.add_option("--query", dest="query",
                      help="pre-input query")
    parser.add_option("--eager", action="store_true", dest="eager", default=False,
                      help="suppress lazy matching (slower, but display correct candidates count)")
    parser.add_option("--eval", dest="string_to_eval",
                      help="eval given string after loading the rc file")
    parser.add_option("--prompt", dest="prompt", default=None,
                      help="specify prompt (percol.view.PROMPT)")
    parser.add_option("--right-prompt", dest="right_prompt", default=None,
                      help="specify right prompt (percol.view.RPROMPT)")
    parser.add_option("--match-method", dest="match_method", default="",
                      help="specify matching method for query. `string` (default) and `regex` are currently supported")
    parser.add_option("--caret-position", dest="caret",
                      help="position of the caret (default length of the `query`)")
    parser.add_option("--initial-index", dest="index",
                      help="position of the initial index of the selection (numeric, \"first\" or \"last\")")
    parser.add_option("--case-sensitive", dest="case_sensitive", default=False, action="store_true",
                      help="whether distinguish the case of query or not")
    parser.add_option("--reverse", dest="reverse", default=False, action="store_true",
                      help="whether reverse the order of candidates or not")
    parser.add_option("--auto-fail", dest="auto_fail", default=False, action="store_true",
                      help="auto fail if no candidates")
    parser.add_option("--auto-match", dest="auto_match", default=False, action="store_true",
                      help="auto matching if only one candidate")

    parser.add_option("--prompt-top", dest="prompt_on_top", default=None, action="store_true",
                      help="display prompt top of the screen (default)")
    parser.add_option("--prompt-bottom", dest="prompt_on_top", default=None, action="store_false",
                      help="display prompt bottom of the screen")
    parser.add_option("--result-top-down", dest="results_top_down", default=None, action="store_true",
                      help="display results top down (default)")
    parser.add_option("--result-bottom-up", dest="results_top_down", default=None, action="store_false",
                      help="display results bottom up instead of top down")

    parser.add_option("--quote", dest="quote", default=False, action="store_true",
                      help="whether quote the output line")
    parser.add_option("--peep", action="store_true", dest="peep", default=False,
                      help="exit immediately with doing nothing to cache module files and speed up start-up time")


def read_input(filename, encoding, reverse=False):
    import codecs
    if filename:
        if six.PY2:
            stream = codecs.getreader(encoding)(open(filename, "r"), "replace")
        else:
            stream = open(filename, "r", encoding=encoding)
    else:
        if six.PY2:
            stream = codecs.getreader(encoding)(sys.stdin, "replace")
        else:
            import io
            stream = io.TextIOWrapper(sys.stdin.buffer, encoding=encoding)
    if reverse:
        lines = reversed(stream.readlines())
    else:
        lines = stream
    for line in lines:
        yield ansi.remove_escapes(line.rstrip("\r\n"))
    stream.close()


def decide_match_method(options):
    if options.match_method == "regex":
        from percol.finder import FinderMultiQueryRegex
        return FinderMultiQueryRegex
    elif options.match_method == "migemo":
        from percol.finder import FinderMultiQueryMigemo
        return FinderMultiQueryMigemo
    elif options.match_method == "pinyin":
        from percol.finder import FinderMultiQueryPinyin
        return FinderMultiQueryPinyin
    else:
        from percol.finder import FinderMultiQueryString
        return FinderMultiQueryString


def main():
    pass


if __name__ == '__main__':
    main()
