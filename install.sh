#!/bin/bash

aptitude install supervisor python-pip python-gevent python-docopt python-requests

DIR=$( cd "$( dirname "$0" )" && pwd )

cat > $DIR/agent.conf << EOF
[appbus]
api_host=api-dev.appbus.io
api_key=APIKEYHERE
EOF

cat > /etc/supervisor/conf.d/appbus-agent.conf << EOF
[program:appbusagent]
command=python2.7 $DIR/agent.py -f $DIR/agent.conf
redirect_stderr=true
stdout_logfile=/var/log/appbus.log
EOF
