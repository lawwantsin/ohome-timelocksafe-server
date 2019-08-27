#!/usr/local/bin/python3.6 -u

import os, sys, html, textwrap, platform, datetime, urllib.parse, json
import pygments  # Local module.
from pygments.lexers import Python3Lexer
from pygments.formatters import HtmlFormatter


if __name__ == "__main__":
    print("Please load as a module, instead of running as a script.",
        file=sys.stderr)
    sys.exit(1)


# This file should have as much as possible related to displaying HTML.  It
# really should be a full templeting engine, but the couple I tried used
# hundreads of megs of memory (no idea on what) and were not fast enough to
# comfortably call on every request.  So instead of continuing to look for one
# that wasn't terrible I did the arguably less than ideal thing and wrote a
# site generator.  Along with the memory, CPU, and speed advantages this also
# means you only need to know python (instead of a bunch of templating
# languages) to understand it.
# I'm sorry.

def get_exception_page(exp_str):
    """Take the given exception string and return a static error page.
    The user won't normally see this and it may be displayed if the normal
    pages can't be loaded from files so it's fine if the style does not
    match or looks super ugly or whatever.  The most important thing is that
    this never raises any kind of exception and always (unless the pi looses
    power, the thread is killed, etc.) returns something human-readable."""
    try:
        return textwrap.dedent("""\
            {
                "error": "Unrecoverable Error",
                "message": "%s"
            }
            """) % html.escape(exp_str)
    except Exception:
        return ("""
            {
                "error": "Unrecoverable Error",
                "message": "Error while displaying unrecoverable error."
            }
        """)

def timezones(tz):
    return textwrap.dedent("""\
        {
            "data": %s
        }
        """) % json.dumps(tz)
