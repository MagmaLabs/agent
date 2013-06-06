#!/bin/bash

aptitude install supervisor python-pip python-gevent python-requests
pip install docopt

DIR=$( cd "$( dirname "$0" )" && pwd )

if [ ! -f $DIR/agent.conf ]; then
	cat > $DIR/agent.conf << EOF
[appbus]
api_host=api-dev.appbus.io
api_key=APIKEYHERE
EOF
fi

cat > /etc/supervisor/conf.d/appbus-agent.conf << EOF
[program:appbusagent]
command=python2.7 $DIR/agent.py -f $DIR/agent.conf
redirect_stderr=true
stdout_logfile=/var/log/appbus.log
EOF

chmod o-rwx $DIR/agent.conf

echo 
echo 'Ready, just edit agent.conf and set up your api key.'
echo
echo 'To start the agent: supervisorctl reload; supervisorctl restart appbusagent'