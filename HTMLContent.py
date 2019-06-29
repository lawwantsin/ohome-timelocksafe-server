#!/usr/local/bin/python3.6 -u

import os, sys, html, textwrap, platform, datetime, urllib.parse
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

def linkify(link_str, display_str=None):
    """Return a 2-tuple of link_str where the first item is quoted as if
    it was the href/option/cgi-name, and the second is escaped as if it
    is going to be displayed on a web page."""
    link_str_ = urllib.parse.quote_plus(
            link_str,
            encoding="utf-8", errors="strict")
    if display_str:
        display_str_ = html.escape(display_str)
    else:
        display_str_ = html.escape(link_str)

    return (link_str_, display_str_)


def get_exception_page(exp_str):
    """Take the given exception string and return a static error page.
    The user won't normally see this and it may be displayed if the normal
    pages can't be loaded from files so it's fine if the style does not
    match or looks super ugly or whatever.  The most important thing is that
    this never raises any kind of exception and always (unless the pi looses
    power, the thread is killed, etc.) returns something human-readable."""
    try:
        return textwrap.dedent("""\
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Unrecoverable Error</title>
                    <h1>Unrecoverable Error<h1>
                </head>
                <body>
                    <h3>Sorry.</h3>
                    <p>You can try:
                        <ul>
                            <li>Rebooting by unplugging the box, waiting
                                a few seconds, plugging it back in, waiting
                                30 seconds, and then trying again.</li>
                            <li><a href="/reset">Restting the memory (and
                                deleting any saved alarms) by clicking here.
                                </a></li>
                            <li>Asking on the forums:
                                &lt;Insert link to forum.&gt;</li>
                            <li>Filing a bug report:
                                &lt;Insert link to contact us page.&gt;</li>
                            <li>To look through the <a href="/diag">
                                diagnostics page</a> or the <a href="/log">
                                log</a> and debug it yourself.</li>
                            <li>Also, it may not work, and it won't fix
                                anything, but you might be able
                                to <a href="/?unlockonemin=true">unlock the
                                box for a minute</a>.</li>
                        </ul>
                    </p>
                    <h4>The error was:</h4>
                    <p><pre>%s</pre></p>
                </body>
            </html>
            """) % html.escape(exp_str)
    except Exception:
        return ('<html><head><meta charset="utf-8">'
                '<title>Unrecoverable Error</title>'
                '<h1>Unrecoverable Error</h1>'
                '</head><body><p>'
                'There was an error while trying to display another error.'
                '</p></body></html>'
            )


def get_path_not_found_page(path):
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <meta http-equiv="refresh" content="20; URL='/'" id="rfr">
                <title>404&mdash;Page not found</title>
                <h1>404&mdash;Page not found</h1>
            </head>
            <body>
                <script>
                    var timeleft = parseInt(document
                        .getElementById("rfr").getAttribute("content"));
                    if (isNaN(timeleft)) {
                        timeleft = 5;
                    }
                    var timer_1 = setInterval(function() {
                        if (timeleft > 1) {
                            document.getElementById("trem").innerHTML = 
                                ", and might be forwarded in "
                                + timeleft + " seconds.";
                        } else if (timeleft == 1) {
                            document.getElementById("trem").innerHTML = 
                                ", and might be forwarded in a second.";
                        } else {
                            document.getElementById("trem").innerHTML =
                                ".";
                            clearInterval(timer_1);
                        }
                        timeleft = timeleft - 1;
                    }, 1000);
                </script>
                <p>The page &ldquo;%s&rdquo; is not found.</p>
                <p>But that might be expected since when one is connected to 
                this Wi-Fi network everything (except the domains that are in
                your DNS cache) are redirected here.</p>
                <p>So, you are probably looking to go 
                <a href="/">here</a><span id="trem">, and might
                be forwarded in a few seconds.</span></p>
            </body>
        </html>
        """) % html.escape(path)

def get_reset_page():
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>Factory Reset</title>
                <h1>Attempt a Factory Reset</h1>
            </head>
            <body>
                <p>Click below to erase the memory, which means you will
                have to recreate your alarms.</p>
                <p>After clicking the box will be reset and may come back up
                in a minute, but you also may need to unplug it, wait a few
                seconds, plug it back in and wait 60 seconds more.</p>
                <p><form action="/" method="get">
                    <input type="hidden" name="reset" value="yes_really">
                    <input type="submit" value="RESET (erase memory)">
                </form></p>
            </body>
        </html>
        """)

def get_reset_done_page():
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <meta http-equiv="refresh" content="20; URL='/'" id="rfr">
                <title>Factory Reset Complete</title>
                <h1>Factory Reset Complete (Memory Erased)</h1>
            </head>
            <body>
                <script>
                    var timeleft = parseInt(document
                        .getElementById("rfr").getAttribute("content"));
                    if (isNaN(timeleft)) {
                        timeleft = 5;
                    }
                    var timer_1 = setInterval(function() {
                        if (timeleft > 1) {
                            document.getElementById("trem").innerHTML = 
                                "" + timeleft + " seconds";
                        } else if (timeleft == 1) {
                            document.getElementById("trem").innerHTML = 
                                "a second";
                        } else {
                            document.getElementById("trem").innerHTML =
                                "an unknown number of seconds";
                            clearInterval(timer_1);
                        }
                        timeleft = timeleft - 1;
                    }, 1000);
                </script>
                <p>PRAM (memory) was erased.</p>
                <p>The webserver should come back up in
                <span id="trem">a few seconds</span>,
                but if it does not you should unplug the box, wait a few
                seconds, plug it back in, wait 60 more seconds, and then
                try and goto the <a href="/">main page</a>.</p>
                <p><big><strong>DO NOT RELOAD THIS PAGE.</strong></big></p>
            </body>
        </html>
        """)

def get_unlockonemin_page(worked):
    if worked:
        ret = "The latch on the box should be released now and will " + \
                "reclose in one minute or so."
    else:
        ret = "The latch will not be released because the box is " + \
                "LOCKED, please wait until an alarm fires to open in."
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>Box Unlocked for a Minute</title>
                <h1>Box Unlocked for a Minute</h1>
            </head>
            <body>
                <p>%s</p>
                <p>Next, you likely want to go back to the
                <a href="/">main page</a>.</p>
            </body>
        </html>
        """) % ret

def get_set_dt_tz_done_page(errstr):
    if errstr:
        ret = "<h2>There was an error when trying to set the date, " + \
                "time, or timezone:</h2>\n<pre>%s</pre>" % errstr
    else:
        ret = "The date, time, and timezone appear to have been set."
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>Finished setting up date, time, and timezone.</title>
                <h1>Finished setting up date, time, and timezone.</h1>
            </head>
            <body>
                <p>%s</p>
                <p>Next, you likely want to head to the
                <a href="/">main page</a> and finish setting up.</p>
            </body>
        </html>
        """) % ret

def add_alarm_done_page(errstr):
    if errstr:
        ret = "<h2>There was an error when trying to add an alarm:</h2>" + \
                "\n<pre>%s</pre>" % errstr
    else:
        ret = "Alarm appears to have been added."
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>Finished Adding an Alarm.</title>
                <h1>Finished Adding an Alarm.</h1>
            </head>
            <body>
                <p>%s</p>
                <p>Next, you likely want to head to the
                <a href="/">main page</a>.</p>
            </body>
        </html>
        """) % ret

def get_toggle_alarm_done_page(errstr):
    if errstr:
        ret = "<h2>There was an error when trying to toggle an alarm:</h2>" + \
                "\n<pre>%s</pre>" % errstr
    else:
        ret = "Alarm appears to have been toggled."
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>Finished Toggling an Alarm.</title>
                <h1>Finished Toggling an Alarm.</h1>
            </head>
            <body>
                <p>%s</p>
                <p>Next, you likely want to head to the
                <a href="/">main page</a>.</p>
            </body>
        </html>
        """) % ret

def get_del_alarm_done_page(errstr):
    if errstr:
        ret = "<h2>There was an error when trying to delete an alarm:</h2>" + \
                "\n<pre>%s</pre>" % errstr
    else:
        ret = "Alarm appears to have been delete."
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>Finished Deleting an Alarm.</title>
                <h1>Finished Deleting an Alarm.</h1>
            </head>
            <body>
                <p>%s</p>
                <p>Next, you likely want to head to the
                <a href="/">main page</a>.</p>
            </body>
        </html>
        """) % ret


# We use the jstz from:
#   https://raw.githubusercontent.com/iansinnott/jstz/master/dist/jstz.min.js
# because we want a version that tries to call:
#   Intl.DateTimeFormat().resolvedOptions().timeZone
# for us (so we don't have to) and that removes the Etc/* timezones from
# whatever that function may return (annoyingly stable (and tip) on pellepim's
# page shows that it does remove Etc zones BUT the minified version does not!
# I guess that since it isn't a release the merge request forgot to minify
# it or something).
# Anyway this should try and guess the modern timezone if the Intl stuff
# fails and if not we can be pretty sure that either the user has disabled
# access to timezone information or their browser sucks, so they have to
# manually set it.
with open(os.path.join(os.path.dirname(__file__), "jstz.min.js")) as f:
    jstz_min = f.read()
try:
    jstz_min_ver = jstz_min.splitlines()[0].strip(' */').split(' ')
    jstz_min_ver = "%s (%s)" % (jstz_min_ver[2], jstz_min_ver[5])
except Exception:
    jstz_min_ver = "unknown"

def get_js_load_browser_tz_dt(elem_id_utc, elem_id_local, button_id=None):
    """The first two arguments are the HTML element ID~s of the elements to
    change the innerHTML to write the date, time, and timezone provided by
    the browser (if javascript is enabled).  The button_id is the button
    (that in the HTML probably doesn't go anywhere or do anything) that will
    be tied to a function to call into the box to set the date, time, and tz.
    So in the HTML (if button_id is not None) should be a call to the func:
        <button type="button" id="<button_id>" onclick="settimefromjs()">
            Javascript is disabled, please set everything manually below.
        </button>

    This just sets the time to whatever time the browser thinks it is when the
    button is pressed.  This'll work fine if the network delay isn't too bad,
    but really we should be doing something like:
        https://www.nodeguy.com/serverdate/
    since the full NTP sync stuff takes a fairly long-lived connection.
    """
    global jstz_min
    disp_time_block = textwrap.dedent("""\
        // `tz` might be undefined, or _anything_, so we cast it to a string
        // and catch exceptions.  In every case we want tz to be a string,
        // even if that string ends up being "null" or "undefined".
        // Annoyingly a bunch of old browsers don't implement this at all, and
        // even many newer ones don't fill out timezone, and all of them don't
        // if the user's enabled some security settings on their browser,
        // so, there has to be a way to have the user manually specify both
        // the timezone and the local time.
        var tz = "Unknown";
        try {
            tz = jstz.determine().name();
        } catch(exp) {}

        // Convert num to a string and 0-pad to at least pad_to length.
        function zeropad(num, pad_to) {
            var s = String(num);
            while (s.length < pad_to) { s = "0" + s; };
            return s;
        }

        // We use this instead of th `Intl.Date...` stuff to get the actual
        // time because this is much older (I.E. 8) so it is much more likely
        // to work (the user may have set their browser to not report the
        // time).  Also note that the "timezone" returned with `new Date()`
        // is not actually a timezone but a timezone offset.  The host OS
        // changes it when a daylight saving change happens, but of course
        // the box, being disconnected from the internet can't do that.
        // So, it needs a real IANA canonical timezone (which is what we get
        // with the jstz (Intl.Date) stuff above).

        function get_iso8601sp_utc(date_obj) {
            return zeropad(date_obj.getUTCFullYear(), 4) +
                "-" + zeropad(1 + date_obj.getUTCMonth(), 2) +
                "-" + zeropad(date_obj.getUTCDate(), 2) +
                " " + zeropad(date_obj.getUTCHours(), 2) +
                ":" + zeropad(date_obj.getUTCMinutes(), 2) +
                ":" + zeropad(date_obj.getUTCSeconds(), 2) +
                " " + 'UTC';
        }

        function get_iso8601sp_local(date_obj, tz) {
            return zeropad(d.getFullYear(), 4) +
                "-" + zeropad(1 + d.getMonth(), 2) +
                "-" + zeropad(d.getDate(), 2) +
                " " + zeropad(d.getHours(), 2) +
                ":" + zeropad(d.getMinutes(), 2) +
                ":" + zeropad(d.getSeconds(), 2) +
                " " + tz;
        }

        var d = new Date();
        document.getElementById("%s").innerHTML = get_iso8601sp_utc(d);
        document.getElementById("%s").innerHTML = get_iso8601sp_local(d, tz);
        """) % (elem_id_utc, elem_id_local)

    button_block = ""
    if button_id:
        button_block = textwrap.dedent("""\
            document.getElementById("%s").innerHTML = "Click to use this " +
                "time to set box RTC time (time when clicked will be used).";

            function settimefromjs() {
                var d = new Date();
                var settime_url =
                    "/?y=" + encodeURIComponent(String(d.getFullYear())) +
                    "&mo=" + encodeURIComponent(String(1 + d.getMonth())) +
                    "&d=" + encodeURIComponent(String(d.getDate())) +
                    "&h=" + encodeURIComponent(String(d.getHours())) +
                    "&mi=" + encodeURIComponent(String(d.getMinutes())) +
                    "&s=" + encodeURIComponent(String(d.getSeconds())) +
                    "&tz=" + encodeURIComponent(String(tz));

                window.location = settime_url;
            }\
            """) % (button_id, )

    return jstz_min + disp_time_block + button_block

def get_template_index_page(html_body):
    """Return a full page with the given body."""
    return textwrap.dedent("""\
        <html>
            <head>
                <meta charset="utf-8">
                <title>WeedSafe Box</title>
                <h1>WeedSafe Box</h1>
            </head>
            <body>
        %s
            <br><br><br><br><br><hr>
            <p><small>Battery guage is not reporting.</small></p>
            <p><small><a href="/?unlockonemin=true">
                Attempt to unlock the box for one minute.
            </a></small></p>
            </body>
        </html>
        """) % textwrap.indent(html_body, " "*8)

def get_settime_page(common_timezones, rtc_dt_utc, rtc_dt_local):
    """This can be called in any state except LOCKED and should work.  That
    means that the time and timezone could be set or not so we always allow
    changing of both."""

    # This includes the function set_date_time_tz_from_browser().
    body_script = textwrap.dedent("""\
        <script>
        %s
        </script>\
        """) % textwrap.indent(
                get_js_load_browser_tz_dt(
                    elem_id_utc="dt_utc", elem_id_local="dt_local",
                    button_id="settime_button"),
                " "*4)

    tz_opts = textwrap.dedent("""\
        <select name="tz">
        %s
        </select>
        """) % textwrap.indent("\n".join(tuple(
                '<option value="%s">%s</option>' %
                tz for tz in map(linkify, common_timezones)
            )), " "*4)

    askgeo_link = linkify("https://askgeo.com/")
    bash_tz_cmd = html.escape('''tz="$(perl -MCwd -e 'print Cwd::abs_path shift' /etc/localtime)" ; echo ${tz#*/zoneinfo/}''')
    win_2_iana = linkify("https://unicode.org/cldr/charts/latest/supplemental/zone_tzid.html")
    so_tz_info = linkify("https://stackoverflow.com/tags/timezone/info")

    # The 4 dt/tz values are in a table b/c it is much easier to see
    # which parts are different if they are lined up.
    body_html = textwrap.dedent("""\
        <table>
            <tr>
                <td><strong>RTC time (may be wrong or missing):</strong></td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            <tr>
                <td><strong>Browser time (from javascript):</strong></td>
                <td id="dt_utc">Unknown</td>
                <td id="dt_local">Unknown</td>
            </tr>
        </table>
        <button type="button" id="settime_button" onclick="settimefromjs()">
            Javascript is disabled, please set everything manually below.
        </button>
        <hr>
        <h3>Or, set the date, time, and timezone manually:</h3>
        <p>Set the date and time to your local date and time (be careful near
        a discontinuity like a daylight saving time change), and the timezone
        to your local timezone.  This timezone must be a real IANA canonical
        timezone.  You can find your timezone by:
        <ul>
            <li>On another device (since this device's network is the box) go
            to <a href="%s">%s</a> and drop a pin on your house and look what
            the value of <code>TimeZoneId</code> is.</li>
            <li>On macOS, Linux, BSD, and other modern unixes go to the
            command line (Bash prompt) and copy and paste in <code>%s</code>
            and hit enter.</li>
            <li>On Windows find out the windows timezone (maybe via
            <code>tzutil.exe /l</code> and then go to <a href="%s">%s</a> to
            convert.</li>
            <li>More information can be found at <a href="%s">%s</a>.</li>
        </ul>

        <form action="/" method="get">
            <fieldset>
                <legend>Choose a date, time, and timezone:</legend>
                4-digit year: <input type="text" name="y" size="4">
                2-digit month: <input type="text" name="mo" size="2">
                Day of month: <input type="text" name="d" size="2">
                00--24 hour: <input type="text" name="h" size="2">
                minute: <input type="text" name="mi" size="2">
                second: <input type="text" name="s" size="2">
                Timezone:
                %s
                <input type="submit" value="Set date, time, and timezone.">
            </fieldset>
        </form>
        """ % (
            rtc_dt_utc, rtc_dt_local,
            askgeo_link[0], askgeo_link[1],
            bash_tz_cmd,
            win_2_iana[0], win_2_iana[1],
            so_tz_info[0], so_tz_info[1],
            tz_opts,
            ))

    return get_template_index_page(body_html + body_script)

def get_index_NEW_page():
    return get_template_index_page(textwrap.dedent("""\
        <p>Hello.  If you just turned on this box for the first time you
        probably want to start <a href="/settime">setting it up</a>.</p>
        <p>If, however, you have been using this box for a while and are
        seeing this page that means that the battery in the real-time clock
        and memory module has died (after which the box lost power).  So you
        should change the battery like this:</p>
        <p>&lt;Insert type of battery with pictures and instructions on how
        to change it here.&gt;<br>Note that if we use the current module we
        need to use an LR2032 (or LiR2032) type battery and NOT a CR2032
        because it is designed sloppily (if someone uses a CR2032 it'll bulge
        out and fail from the overcurrent).</p>\
        """))

def get_index_LOCKED_page(time_unlocked_str, time_until_unlocked_str):
    return get_template_index_page(textwrap.dedent("""\
            <h2>The box is locked.</h2>
            <p>The box will unlock on %s, which is in %s.</p>
        """) % (time_unlocked_str, time_until_unlocked_str))

def get_index_NOALARMS_UNLOCKED_page(dt_loc_str, alarm_aid_str):
    alarms_forms = []
    for aid_str in alarm_aid_str:
        alarms_forms.append(textwrap.dedent("""\
            <hr>
            %s
            <form action="/" method="get">
                <input type="hidden" name="toggleaid" value="%d">
                <input type="submit" value="Enable/Disable">
            </form>
            <form action="/" method="get">
                <input type="hidden" name="delaid" value="%d">
                <input type="submit" value="Delete">
            </form>
            <hr>
            """ % (aid_str[1], aid_str[0], aid_str[0])))
    if alarms_forms:
        alarms_forms = "\n".join(alarms_forms)
    else:
        alarms_forms = "No alarms found."

    return get_template_index_page(textwrap.dedent("""\
        <p>Current local time is: %s <a href="/settime">change</a></p>
        <h2>Alarms:</h2>
        <p>The awful format (which should be changed) is: ID enabled (active_days_of_the_week_Mon=0) hour:min-mins_before+mins_after</p>
        %s
        <br><br>
        <h2>New Alarm:</h2>
        <form action="/" method="get">
            <input type="checkbox" name="dowm" value="0" checked>Monday<br>
            <input type="checkbox" name="dowt" value="1" checked>Tuesday<br>
            <input type="checkbox" name="doww" value="2" checked>Wednesday<br>
            <input type="checkbox" name="dowh" value="3" checked>Thursday<br>
            <input type="checkbox" name="dowf" value="4" checked>Friday<br>
            <input type="checkbox" name="dows" value="5" checked>Saturday<br>
            <input type="checkbox" name="dowu" value="6" checked>Sunday<br>
            <input type="text" size="2" name="h">Hour (0&ndash;23)<br>
            <input type="text" size="2" name="m">Minute (0&ndash;59)<br>
            <input type="text" size="2" name="mb">Minutes Before (0&ndash;3)<br>
            <input type="text" size="2" name="mf">Minutes After (0&ndash;7)<br>
            <input type="submit" value="Add Alarm">
        </form>\
        """) % (
            dt_loc_str,
            alarms_forms,
            ))

def get_index_OVERRIDE_page(now_utc, now_local, until_utc, until_local):
    """This is a little annoying.  This can be called in any state, which means
    if the state is NEW there isn't a timezone set which means there isn't a
    local time, further it is possible that the (UTC) time on the RTC isn't
    even set (so when read could return any date/time at all).  There should be
    a better answer but for now I just display whatever time the RTC has and
    the local time if the tz has been set."""
    return get_template_index_page(textwrap.dedent("""\
        <p>The lock has been manually overriden and the box can be opened
        right now.</p>
        <style type="text/css">
            td { padding: 0 2em 0 0; }
        </style>
        <table>
            <tr><td>Current time:</td><td>%s</td><td>%s</td></tr>
            <tr><td>Unlocked until:</td><td>%s</td><td>%s</td></tr>
        </table>\
        """) % (now_utc, now_local, until_utc, until_local))

def get_log_page():
    with open(os.path.join(os.path.dirname(__file__), "box.log")) as f:
        return get_template_index_page(
            '<pre>\n' +
            html.escape(f.read()) +
            '\n</pre>')


# This takes about 5 seconds, blocking httpd startup (which is way better than
# producing this on the fly since page load time is way more important than
# startup time).  Since the box should be powered on most of the time, this
# isn't bad (and it already takes like 30 seconds to boot and another 10 to
# start), but we could do this in a thread (and some other things) to save
# those startup seconds.
try:
    with open(__file__, "r") as f:
        get_diag_page_this_file_pygments = pygments.highlight(
                f.read(),
                Python3Lexer(),
                HtmlFormatter(style='tango'))
except Exception:
    get_diag_page_this_file_pygments = \
            'No filename found for current script or other pygments error.'


with open("/usr/share/doc/tc/release.txt") as f:
    picore_version = f.read().strip()

with open(os.path.join(os.path.dirname(__file__), "TODO.txt")) as f:
    box_todo_items = f.readlines()

def get_diag_page(
        some_versions,
        hw_state_and_timeout,
        unrecoverable_error,
        local_time_zone,
        rtc_dt_utc,
        rtc_dt_local,
        temperature_fahrenheit,
        proc_uptime_str,
        hw_state_desc,
        alarm_strs,
        ):
    """Build a page that displays everything we can."""

    # This will apply to all the tables (and everything else) below.
    body_style = textwrap.dedent("""\
        <style type="text/css">
            td { padding: 0 2em 0 0; }
            ul { overflow: auto; }
            ul > li {
                display: block;
                width: 20%%;
                float: left;
                padding: 0 2em 0 0;
            }
%s
        </style>\
        """) % textwrap.indent(
            HtmlFormatter(style='tango').get_style_defs('.highlight'),
            " "*4)

    # Each element will be in it's own paragraph tag.
    entries = []

    entries.append('In addition to this diagnostics page you might want to '
            'look at the <a href="/log">log file</a> or do a factory '
            '<a href="/reset">reset</a>.')

    entries.append('<strong>To do:</strong><br><ol>\n' +
            textwrap.indent("\n".join(tuple(
                "<li>%s</li>" % i for i in box_todo_items)), " "*4)
        + '\n</ol>')

    entries.append(textwrap.dedent("""\
        <table>
            <tr> <th>What</th> <th>Version</th> </tr>
%s
        </table>""") % textwrap.indent("\n".join(map(
            lambda v: ("<tr> <td>%s</td> <td>%s</td> </tr>" %
                (html.escape(v[0]), html.escape(v[1]))),
            (
                ("Tiny (pi)Core", picore_version),
                ("python", platform.python_version()),
                ("pygments", pygments.__version__),
                ("jstz_min", jstz_min_ver),
            ) + some_versions)), " "*4))


    entries.append('<strong>Hardware State (see description below):</strong> '
            + "%s until %s" % hw_state_and_timeout)

    entries.append('<strong>Unrecoverable Error:</strong> %s' %
            unrecoverable_error)

    if local_time_zone:
        entries.append('<strong>User set timezone:</strong> ' +
            html.escape(local_time_zone))
    else:
        entries.append('<strong>User set timezone:</strong> unset')

    entries.append('<strong>Alarms:</strong><pre>\n ' +
        "\n".join(alarm_strs) + '\n</pre>')

    if not rtc_dt_utc:
        rtc_dt_utc = "Unknown"

    if not rtc_dt_local:
        if not local_time_zone:
            rtc_dt_local = 'Unknown b/c timezone is not set.'
        else:
            rtc_dt_local = "Unknown"


    # The 4 dt/tz values are in a table b/c it is much easier to see
    # which parts are different if they are lined up.
    entries.append(textwrap.dedent("""\
        <table>
            <tr>
                <td><strong>RTC time:</strong></td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            <tr>
                <td><strong>Browser time:</strong></td>
                <td id="dt_utc">Unknown</td>
                <td id="dt_local">Unknown</td>
            </tr>
        </table>""") % (rtc_dt_utc, rtc_dt_local))

    body_script = textwrap.dedent("""\
        <script>
        %s
        </script>\
        """) % textwrap.indent(
                get_js_load_browser_tz_dt(
                    elem_id_utc="dt_utc", elem_id_local="dt_local"),
                " "*4)



    entries.append("<strong>Battery:</strong> State not known.")

    # (-40.00, 185.00), 2 decimals, so %6.2f will always be 6 chars long.
    entries.append("<strong>RTC temperature:</strong> %6.2f&deg;F" % \
            temperature_fahrenheit)

    entries.append("<strong>Weight:</strong> Scale not present.")

    entries.append("<strong>Humidity:</strong> Sensor not present.")

    entries.append("<strong>uname:</strong> " +
            " ".join(platform.uname()))

    with open('/proc/uptime', 'r') as f:
        entries.append(
            '<strong>Uptime:</strong> %s, <strong>idle</strong>: %s' %
            tuple(map(
                lambda fs: str(datetime.timedelta(seconds=float(fs))),
                f.readline().split())))

    entries.append('<strong>Proc (httpd.py) uptime:</strong> %s' %
            proc_uptime_str)

    with open('/proc/loadavg', "r") as f:
        entries.append('<strong>loadavg:</strong> ' +
            html.escape(f.read()))

    meminfo_list = []
    with open('/proc/meminfo', "r") as f:
        for line in f.readlines():
            meminfo_list.append(html.escape(line.strip()))
    meminfo_list_chunked = []
    for i in range(0,len(meminfo_list),5):
        meminfo_list_chunked.append("<br>".join(meminfo_list[i:i+5]))
    entries.append('<strong>meminfo:</strong>\n<ul>\n%s\n</ul>' %
        textwrap.indent(
            "\n".join('<li><pre>%s</pre></li>' % t for t in meminfo_list_chunked),
            " "*4))

    for fn in ('stat', 'cpuinfo', ):
        with open('/proc/' + fn, "r") as f:
            entries.append('<strong>' + fn + ':</strong>\n<pre>\n' +
                html.escape(f.read()) + '</pre>\n')


    entries.append("\n".join((
            '<h3>Hardware State Description</h3>',
            html.escape(hw_state_desc[0]),
            '<ul>',
            "\n".join(map(
                    lambda s: '<li><strong>%s:</strong> %s</li>' % s,
                    hw_state_desc[1],
                )),
            '</ul>',
        )))


    entries.append('<h3>SSH</h3>'
            'You can ssh in, the user is "tc" with password "piCore".  '
            'Obviously this is the defualt user and password for TinyCore '
            'Linux.  You can find out all about how to mess with it at '
            'their <a href="https://tinycorelinux.net">website</a>.')

    entries.append('<h3>The HTML Display</h3> or UI stuff is badly '
            'seperated out into the following file (<i>HTMLContent.py</i>).  '
            'I should have done more work to make this more of an '
            'API and less of some python spilled over into another file, oh '
            'well, I guess that comes later.  And there are so many problems '
            'with this, sorry.  We will fix it all.')

    global get_diag_page_this_file_pygments
    entries.append(get_diag_page_this_file_pygments)

    return get_template_index_page("\n".join((
        body_style,
        "\n".join('<p>%s</p>' % e for e in entries),
        body_script,
        )))
