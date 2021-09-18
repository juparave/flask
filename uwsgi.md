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


## Configuring uWSGI for Production Deployment (Bloomberg)

ref: https://www.techatbloomberg.com/blog/configuring-uwsgi-production-deployment/

The complete config

```ini
[uwsgi]
strict = true
master = true
enable-threads = true
vacuum = true                        ; Delete sockets during shutdown
single-interpreter = true
die-on-term = true                   ; Shutdown when receiving SIGTERM (default is respawn)
need-app = true

disable-logging = true               ; Disable built-in logging 
log-4xx = true                       ; but log 4xx's anyway
log-5xx = true                       ; and 5xx's

harakiri = 60                        ; forcefully kill workers after 60 seconds
py-callos-afterfork = true           ; allow workers to trap signals

max-requests = 1000                  ; Restart workers after this many requests
max-worker-lifetime = 3600           ; Restart workers after this many seconds
reload-on-rss = 2048                 ; Restart workers after this much resident memory
worker-reload-mercy = 60             ; How long to wait before forcefully killing workers

cheaper-algo = busyness
processes = 128                      ; Maximum number of workers allowed
cheaper = 8                          ; Minimum number of workers allowed
cheaper-initial = 16                 ; Workers created at startup
cheaper-overload = 1                 ; Length of a cycle in seconds
cheaper-step = 16                    ; How many workers to spawn at a time

cheaper-busyness-multiplier = 30     ; How many cycles to wait before killing workers
cheaper-busyness-min = 20            ; Below this threshold, kill workers (if stable for multiplier cycles)
cheaper-busyness-max = 70            ; Above this threshold, spawn new workers
cheaper-busyness-backlog-alert = 16  ; Spawn emergency workers if more than this many requests are waiting in the queue
cheaper-busyness-backlog-step = 2    ; How many emergency workers to create if there are too many requests in the queue
```
