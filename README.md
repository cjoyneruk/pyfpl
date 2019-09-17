# pyfpl (v0.1.1)

A python package to interact with the fantasy premier league API, to analyse player statics and help make points predictions

## Installation and setup

#### Installation

We recommend installing `pyfpl` in a virtual environment using pip, with the command

```
pip install git+https://github.com/cjoyneruk/pyfpl
```

#### Setup

Once installed open python and run the commands

```
>>> from pyfpl import setup
>>> setup()
```

This will ask for the directory in which to store the data. It will also ask for user details (should you wish to provide them) of
the user's name, their email address and password (for logging in to fantasy.premierleague.com) and their team ID. To obtain your
team ID you can log in and go to the points tab, in the browser address bar you will see something of the form
https://fantasy.premierleague.com/entry/{team-id}/event/{GW}.

`setup()` only needs to be run once. If you update `pyfpl` then the settings will be remembered. You can edit the settings of the
data directory or user the user details, or add more users by running

```
>>> from pyfpl import update_settings
>>> update_settings()
```
