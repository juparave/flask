# configuring uWSGI



```ini
# Config file for the project
# /etc/uwsgi/apps-available/midimagic.ini

[uwsgi]

# the base directory (full path)
chdir           = /home/midimagic/app

# app config
module          = wsgi:application

# virtualenv (full path)
home            =  /home/midimagic/app/venv

# run as user midimagic
uid             = midimagic
gid             = midimagic
umask           = 002

# env, include executables path on enviroment if running processes
env             = PATH=%(home)/bin:/usr/local/bin/:$(PATH)

# process-related settings
# master
master          = true
# maximum number of worker processes
processes       = 10
plugins 	= python3
# the socket (use the full path to be safe)
socket          = /home/midimagic/app/midimagic.sock
# ... with appropriate permissions - may be needed
# chmod-socket    = 664
# clear environment on exit
vacuum          = true

die-on-term = true

```


### Expanding variables/placeholders [ref](https://uwsgi-docs.readthedocs.io/en/latest/ParsingOrder.html)
After the internal config tree is assembled, variables and placeholder substitution will be applied.

The first step is substituting all of the $(VALUE) occurrences with the value of the environment variable VALUE.

```ini
[uwsgi]
foobar = $(PATH)
```
foobar value will be the content of shell’s PATH variable

The second step will expand text files embraced in @(FILENAME)

```ini
[uwsgi]
nodename = @(/etc/hostname)
```
nodename value will be the content of /etc/hostname

The last step is placeholder substitution. A placeholder is a reference to another option:

```ini
[uwsgi]
socket = :3031
foobar = %(socket)
```
the content of foobar will be mapped to the content of socket.
