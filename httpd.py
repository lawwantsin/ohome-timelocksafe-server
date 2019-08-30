#!/usr/local/bin/python3.6 -u

# We expect this script to be called on boot with std{out,err} redirected.
# The `-u` in the shebang line makes sure python uses unbuffered output so
# we don't need to flush output on every request to see it in the log.
# Since `BaseHTTPRequestHandler` does not automatically do that (obviously),
# it would be kinda a pain to subclass just for that.

import sys, traceback, http.server, urllib.parse
import HTMLContent  # Local.
import JSONContent  # Local.
import Hardware  # Local.

class HTMLContentWrapper():
    """As requested, attempt to (badly) keep some seperation between the
    pretty interface and the functional parts, but a few things should
    have some processing in this file, so this class is just a wrapper to
    do some of that here instead of HTMLContent (which would otherwise have
    to import and know things that are not really part of the UI."""

    def get_diag_page():
        rtc_dt_utc = Hardware.get_datetime()
        rtc_dt_local = Hardware.fmt_datetime_local(rtc_dt_utc)
        rtc_dt_utc = Hardware.fmt_datetime(rtc_dt_utc)
        hw_state_desc = (
                Hardware.STATE.__doc__,
                ((state.name, state.value) for state in Hardware.STATE),
            )
        return HTMLContent.get_diag_page(
            Hardware.versions_tuple,
            Hardware.get_state_name(),
            Hardware.get_unrecoverable_error_str(),
            Hardware.get_timezone_name(),
            rtc_dt_utc,
            rtc_dt_local,
            Hardware.get_temperature_fahrenheit(),
            Hardware.proc_uptime_str(),
            hw_state_desc,
            Hardware.get_alarm_strings(),
            )




class MyHTTPHandler(http.server.BaseHTTPRequestHandler):

    # Kill the server on reset, after sending the page, so we'll re-read PRAM.
    kill_this_process = False

    def split_path_and_query_string(self, path_qs):
        """BaseHTTPRequestHandler provides the query string in the path, so we
        will always want to split it out and then select what page to show
        based on what is there.  We preserve the order and will fail with an
        error (raise an exception) if any names are duplicated, or the names
        and values end up being different sizes so the caller can just take
        len() on the names to know how many there are."""

        # Split file from query args, in every case we will get a file (lhs).
        path_qs = path_qs.split("?")
        if 1 == len(path_qs):
            path, qs = path_qs[0], ""
        elif 2 == len(path_qs):
            path, qs = path_qs
        else:
            raise Exception("Too many parts: %s" % str(path_qs))

        qs_names = []
        qs_values = []
        if qs:
            # List of 2-tuples (name, val) in order, name may be in >1 tuple.
            for qs_name, qs_value in urllib.parse.parse_qsl(
                                qs,
                                keep_blank_values=True, strict_parsing=True,
                                encoding='utf-8', errors='strict'):
                if qs_name in qs_names:
                    raise Exception("Duplicate name in: %s" % path_qs)

                qs_names.append(urllib.parse.unquote_plus(
                       qs_name,
                       encoding='utf-8', errors='strict'))

                qs_values.append(urllib.parse.unquote_plus(
                       qs_value,
                       encoding='utf-8', errors='strict'))

        if len(qs_names) != len(qs_values):
            raise Exception("Not as many values as names: %s" % path_qs)

        return path, qs_names, qs_values


    def choose_path(self):
        """Return a response code and html content, or throw an exception on
        error.  This is it's own function so we can just return when the
        correct page if found instead of an annoying-to-read-and-write nested
        if-and-elif-and-else mess."""

        path, qs_ns, qs_vs = self.split_path_and_query_string(self.path)

        if not qs_ns:
            print("PATH: "+path)
            # New Routes
            if (path.find('/html') != -1):
                try:
                    if path.endswith(".html") or path.endswith(".svg") or path.endswith(".css") or path.endswith(".js")  or path.endswith(".ico")  or path.endswith(".png"):
                        file = '/home/tc/static' + path[5:]
                    else:
                        file = '/home/tc/static/index.html'
                    print("FILE: " + file)
                    f = open(file)
                    return 200, f.read()

                except IOError:
                    print("ERROR: " + self.path)
                    return 404, HTMLContent.get_path_not_found_page(self.path)

            elif path == '/timezones.json':
                tzs = Hardware.get_common_timezones()
                return 200, JSONContent.timezones(tzs)

            elif path == '/alarms.json':
                alarms = Hardware.get_alarm_strings();
                return 200, JSONContent.alarms(alarms)

            # Legacy Routes
            elif path == '/diags':
                return 200, HTMLContentWrapper.get_diag_page()

            elif path == '/log':
                return 200, HTMLContent.get_log_page()

            elif path == '/reset':
                return 200, HTMLContent.get_reset_page()

            elif path == '/settime':
                if Hardware.get_state_name()[0] == 'LOCKED':
                    return 200, HTMLContent.get_index_LOCKED_page(
                            Hardware.fmt_datetime_local(expect_ch_dt_utc),
                            Hardware.fmt_datetime_until(expect_ch_dt_utc))
                else:
                    rtc_dt_utc = Hardware.get_datetime()
                    rtc_dt_local = Hardware.fmt_datetime_local(rtc_dt_utc)
                    rtc_dt_utc = Hardware.fmt_datetime(rtc_dt_utc)
                    return 200, HTMLContent.get_settime_page(
                            Hardware.get_common_timezones(),
                            rtc_dt_utc, rtc_dt_local,
                            )

            elif path == '/':
                hw_state, expect_ch_dt_utc = Hardware.get_state_name()

                if hw_state == 'NEW':
                    return 200, HTMLContent.get_index_NEW_page()

                elif hw_state == 'LOCKED':
                    return 200, HTMLContent.get_index_LOCKED_page(
                            Hardware.fmt_datetime_local(expect_ch_dt_utc),
                            Hardware.fmt_datetime_until(expect_ch_dt_utc))

                elif hw_state in ('NOALARMS', 'UNLOCKED'):
                    return 200, HTMLContent.get_index_NOALARMS_UNLOCKED_page(
                            Hardware.fmt_datetime_local(
                                Hardware.get_datetime()),
                            Hardware.get_alarms_for_noalarm_page())

                elif hw_state == 'OVERRIDE':
                    rtc_dt_utc = Hardware.get_datetime()
                    rtc_dt_local = Hardware.fmt_datetime_local(rtc_dt_utc)
                    rtc_dt_utc = Hardware.fmt_datetime(rtc_dt_utc)
                    return 200, HTMLContent.get_index_OVERRIDE_page(
                            rtc_dt_utc, rtc_dt_local,
                            Hardware.fmt_datetime(expect_ch_dt_utc),
                            Hardware.fmt_datetime_local(expect_ch_dt_utc))

                elif hw_state == 'CORRUPT':
                    raise Exception(Hardware.get_unrecoverable_error_str())

                else:
                    raise Exception(f"Unknown hardware state:  {hw_state}")

        elif path == '/':  #  Here we for sure have something in qs_ns.

            if (qs_ns, qs_vs) == (["reset", ], ["yes_really", ]):
                # First so this works in any hardware state (yes this is a
                # way to get into the box when it's locked, but most people
                # won't know how to manually append a query string to the URL
                # in thier browser bar, and there are so many more ways to
                # get in even without this).
                self.kill_this_process = True
                Hardware.PRAM_clear()
                return 200, HTMLContent.get_reset_done_page()

            elif (qs_ns, qs_vs) == (["unlockonemin", ], ["true", ]):
                return 200, HTMLContent.get_unlockonemin_page( \
                    Hardware.StateVariablesAlarmThread \
                        .manually_unlock_for_a_minute())

            elif set(qs_ns) == set(["y", "mo", "d", "h", "mi", "s", "tz"]):
                # Set Time
                try:
                    return 200, HTMLContent.get_set_dt_tz_done_page(
                            errstr=Hardware.set_datetime_and_timezone(
                                qs_vs[qs_ns.index("y")],
                                qs_vs[qs_ns.index("mo")],
                                qs_vs[qs_ns.index("d")],
                                qs_vs[qs_ns.index("h")],
                                qs_vs[qs_ns.index("mi")],
                                qs_vs[qs_ns.index("s")],
                                qs_vs[qs_ns.index("tz")],
                                ))
                except Exception:
                    err = "".join(traceback.format_exception(*sys.exc_info()))
                    print(f"{self.path}:\n{err}", file=sys.stderr)
                    # Still return 200.  We don't use 500 b/c this might be
                    # recoverable (like if the user entered an invalid month
                    # they should be able to re-enter).
                    return 200, HTMLContent.get_set_dt_tz_done_page(
                            errstr=err)


            elif set(["h", "m", "mb", "mf"]).issubset(set(qs_ns)) and \
                    set(qs_ns).issubset(set(["h", "m", "mb", "mf",
                    'dowm', 'dowt', 'doww', 'dowh', 'dowf', 'dows', 'dowu'])):
                # Set alarm
                try:
                    h = qs_vs[qs_ns.index("h")]
                    m = qs_vs[qs_ns.index("m")]
                    mb = qs_vs[qs_ns.index("mb")]
                    mf = qs_vs[qs_ns.index("mf")]
                    dsow = []
                    for dow in ('dowm', 'dowt', 'doww', 'dowh', 'dowf', \
                            'dows', 'dowu'):
                        if dow in qs_ns:
                            dsow.append(qs_vs[qs_ns.index(dow)])
                    return 200, HTMLContent.add_alarm_done_page(
                            errstr=Hardware.add_new_alarm(h, m, mb, mf, dsow))
                except Exception:
                    err = "".join(traceback.format_exception(*sys.exc_info()))
                    print(f"{self.path}:\n{err}", file=sys.stderr)
                    # Still return 200.  Might be recoverable.
                    return 200, HTMLContent.add_alarm_done_page(errstr=err)

            elif qs_ns == ["toggleaid", ]:
                # Enable/Disable Alarm
                try:
                    return 200, HTMLContent.get_toggle_alarm_done_page(
                            errstr=Hardware.toggle_alarm(int(qs_vs[0])))
                except Exception:
                    err = "".join(traceback.format_exception(*sys.exc_info()))
                    print(f"{self.path}:\n{err}", file=sys.stderr)
                    # Still return 200.  Might be recoverable.
                    return 200, HTMLContent.get_toggle_alarm_done_page(errstr=err)

            elif qs_ns == ["delaid", ]:
                # Delete an alarm
                try:
                    return 200, HTMLContent.get_del_alarm_done_page(
                            errstr=Hardware.del_alarm(int(qs_vs[0])))
                except Exception:
                    err = "".join(traceback.format_exception(*sys.exc_info()))
                    print(f"{self.path}:\n{err}", file=sys.stderr)
                    # Still return 200.  Might be recoverable.
                    return 200, HTMLContent.get_del_alarm_done_page(errstr=err)

        # Nothing matched (path or query string), so return a 404.
        return 404, HTMLContent.get_path_not_found_page(self.path)

    def guess_type(self, path):
        if (path.find(".") != -1):
            ext = path.split(".")[-1]
            ext = ext.lower()
            types = {
                'html': "text/html",
                'css': "text/css",
                'js': "text/javascript",
                'svg': "image/svg+xml",
                'png': "image/png",
                'ico': "image/ico",
                "json": "application/json"
            }
            return types[ext]
        else:
            return "text/html"

    def do_GET(self):
        """We only use the following response codes:
            200: The normal case and should be all the user ever sees.
            404: Since every domain/page/request is routed to us when the
                 client is connected to this Wi-Fi network this may happen a
                 lot.  The 404 page will forward to the main page after
                 displaying a message saying what it is they've connected to.
                 Apart from the user this page is returned when most OS~es
                 connect to the Wi-Fi network and try to login (the popup when
                 you connect to a hotel access point or whatever Apple uses
                 /hotspot-detect.html for his).
            500: Unrecoverable error.  This is when the python throws an
                 exception (could be on purpose) meaning there isn't anything
                 this software can do.  So the user sees suggestions like
                 reboot or ask on the forums, etc.  If this is query strings
                 or whatever it could also be a bug in this thing.
        """
        try:
            html_response, html_content = self.choose_path()
        except Exception:
            html_response = 500
            err = "".join(traceback.format_exception(*sys.exc_info()))
            print(f"{self.path}:\n{err}", file=sys.stderr)
            html_content = HTMLContent.get_exception_page(err)
        finally:
            path, qs_ns, qs_vs = self.split_path_and_query_string(self.path)
            self.send_response(html_response)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            if html_content:
                self.wfile.write(html_content.encode("utf-8"))
            else:
                self.wfile.write("<html><body>Unknown error.</body></html>")
            if self.kill_this_process:
                sys.exit(1)  # Should be restarted by the OS.


# Finally start the thing.
print("Starting server.", file=sys.stderr)
http.server.HTTPServer(('', 80), MyHTTPHandler).serve_forever()
