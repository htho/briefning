'''
    briefning: Creates a short briefing from your Thunderbird/Lightning calendar.

    Copyright (C) 2016  Hauke Thorenz <htho@thorenz.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as    published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sqlite3
import configparser
import getpass
from datetime import datetime
from datetime import timedelta
import fileinput
import locale
import argparse
VERSION = 20160303

parser = argparse.ArgumentParser(description="Creates a short briefing from your Thunderbird/Lightning calendar.")
parser.add_argument("-e", "--event", help="Show only this event.", type=int, default=None)

parser.add_argument("-l", "--long-desc", help="Write a long description.", action="store_true")
# parser.add_argument("-C", "--calendar", help="Only show TODO-List.", default=False)
# parser.add_argument("-T", "--todo", help="Only show TODO-List.", default=False)
# parser.add_argument("-B", "--both", help="Only show TODO-List.", default=True)
parser.add_argument("-w", "--weeks", help="Amount of weeks to create a briefing for.", type=int, default=2)
# parser.add_argument("-d", "--days", help="Amount of days to create a briefing for.", default=None)
# parser.add_argument("-n", "--min-events", help="Minimal amount of events to show.", default=None)
parser.add_argument("-x", "--max-events", help="Maximal amount of events to show.", type=int, default=None)
# parser.add_argument("-p", "--path", help="Path to the Thunderbird profile.", default=None)
# parser.add_argument("-P", "--profile", help="Name of the Thunderbird profile.", default=None)
# parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
parser.add_argument('-V', '--version', action='version', version="%(prog)s " + str(VERSION))
args = parser.parse_args()

WEEKS = args.weeks
MAX_EVENTS = args.max_events
USE_LONGDESC = args.long_desc
SHOW_ONLY = args.event


def txt_prefix_each_line(string, prefix, ignorefirst=False, ignorelast=False):
    """prefix each line in the given string with the given prefix.
    Useful for block indention."""
    ret = list()
    splitted = string.splitlines()
    if len(splitted) == 0:
        return ""

    if ignorefirst:
        ret.append(splitted[0])
        splitted = splitted[1:]
        if len(splitted) == 0:
            return "\n".join(ret)

    last = None
    if ignorelast:
        last = splitted[-1]
        splitted = splitted[:-1]
        if len(splitted) == 0:
            return "\n".join(ret.append(last))

    for line in splitted:
        ret.append(prefix + line)

    if ignorelast:
        ret.append(last)

    return "\n".join(ret)


locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())  # seems necessary for calendar

# determine Thunderbird Profile
username = getpass.getuser()
tb_config = configparser.ConfigParser()
tb_config.read("/home/" + username + "/.thunderbird/profiles.ini")
tb_profile = tb_config["Profile0"]["Path"]  # Use Profile0
for section in tb_config.sections():  # Find the default Profile
    if "Default" in section and section["Default"] == "1":
        tb_profile = section["Path"]  # Use the default Profile


def parse_tb_prefs(pref_path):
    settings = dict()
    with fileinput.input(files=(pref_path)) as f:
        for line in f:
            line = str(line)
            if line.startswith("user_pref("):
                line = line.lstrip("user_pref(")
                line = line.rstrip().rstrip(");")
                path_value = line.split(sep=",", maxsplit=1)
                path = path_value[0].strip().strip('"')
                value = path_value[1].strip().strip('"')
                settings[path] = value
    return settings

# read Thunderbird settings
tb_prefs = parse_tb_prefs("/home/" + username + "/.thunderbird/" + tb_profile + "/prefs.js")

# Connect to DB
db_connection = sqlite3.connect("/home/" + username + "/.thunderbird/" + tb_profile + "/calendar-data/local.sqlite")  # @UndefinedVariable because of some eclipse trouble
db_connection.row_factory = sqlite3.Row  # makes rows Row objects instead of Tuples https://docs.python.org/3/library/sqlite3.html#sqlite3.Row # @UndefinedVariable because of some eclipse trouble
db_cursor = db_connection.cursor()

# Timewindow
startdate = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
enddate = startdate + timedelta(weeks=WEEKS)

# Query
cal_query_vars = (int(startdate.timestamp() * 1000000), int(enddate.timestamp() * 1000000))  # multiplication for compability reasons
cal_query = """
SELECT id, cal_events.cal_id, title, event_start, event_end, item_id, key, value
FROM cal_events, cal_properties
WHERE event_start > ?
AND event_start < ?
AND id = item_id
ORDER BY event_start"""

result = db_cursor.execute(cal_query, cal_query_vars)

events = dict()
events_index = dict()  # (timestamp: evid) might cause trouble on overlaping events.
# TODO: sort events by date. Remove events_index

for row in result:
    evid = row["id"]
    if evid not in events:
        events[evid] = dict()
        events[evid]["start"] = datetime.fromtimestamp(int(row["event_start"]) / 1000000)
        events[evid]["startstring"] = events[evid]["start"].strftime("%a %d.%m. %H:%M")  # TODO based on locale?
        events[evid]["end"] = datetime.fromtimestamp(int(row["event_end"]) / 1000000)
        events[evid]["endstring"] = events[evid]["end"].strftime("%a %d.%m. %H:%M")  # TODO based on locale?
        events[evid]["title"] = row["title"]
        events[evid]["calendar_name"] = tb_prefs["calendar.registry." + row["cal_id"] + ".name"]
        events_index[int(row["event_start"]) / 1000000] = evid

    # if evid in events:
    if row["key"] == "LOCATION":
        events[evid]["location"] = row["value"]
    if row["key"] == "DESCRIPTION":
        events[evid]["description"] = row["value"]
        if USE_LONGDESC is False and len(events[evid]["description"]) > 69:
            events[evid]["description"] = events[evid]["description"][:64] + "[...]"

eventcounter = 1
for eventdate, eventid in sorted(events_index.items()):
    if SHOW_ONLY is None or SHOW_ONLY is not None and SHOW_ONLY == eventcounter:
        print(("=" * 78))
        print("#" + str(eventcounter) + "\t|{startstring}  -  {endstring}".format_map(events[eventid]))
        print("--------+" + ("-" * 69))
        print("Title:\t|" + txt_prefix_each_line(events[eventid]["title"], "\t", True))
        print("\t+" + ("-" * 69))
        if "location" in events[eventid]:
            print("Loc:\t|" + txt_prefix_each_line(events[eventid]["location"], "\t", True))
            print("\t+" + ("-" * 69))

        if "description" in events[eventid]:
            print("Descr:\t|" + txt_prefix_each_line(events[eventid]["description"], "\t|", True))
            print("\t+" + ("-" * 69))
        print()

    if MAX_EVENTS is not None and eventcounter >= MAX_EVENTS:
        break
    else:
        eventcounter = eventcounter + 1
