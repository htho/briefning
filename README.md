# briefning
Creates a short **brief**ing from your Thunderbird/Light**ning** calendar.

## Usage
### Short
`python briefning.py`

### Long
```
python briefning.py -h
usage: briefning.py [-h] [-e EVENT] [-l] [-w WEEKS] [-x MAX_EVENTS] [-V]

Creates a short briefing from your Thunderbird/Lightning calendar.

optional arguments:
  -h, --help            show this help message and exit
  -e EVENT, --event EVENT
                        Show only this event.
  -l, --long-desc       Write a long description.
  -w WEEKS, --weeks WEEKS
                        Amount of weeks to create a briefing for.
  -x MAX_EVENTS, --max-events MAX_EVENTS
                        Maximal amount of events to show.
  -V, --version         show program's version number and exit
```

## Requirements

  * Thunderbird with the Lightning extension
  * Python 3. (Developed and tested with Python 3.5.1)
  * Linux (Why would anybody want tp use this with Windows? Apple users are welcome to port this - but why would they?)

## PAQ (Probably Asked Questions)
### Who Needs it?
Anybody who wants to have a quick overview of their calendar and
todo-lists from the command line.

I personally use it as part of my MOTD.

### How Does it Work?
briefning determines your Thunderbird Profile from `~/.thunderbird/profiles.ini`.
Relevant settings are extracted from `~/.thunderbird/PROFILE/prefs.js`.
The calendar information is taken from `~/.thunderbird/PROFILE/calendar-data/local.sqlite`.

Everything else is some simple SQL and Python magic.

## TBD
A lot!
When it is necessary!