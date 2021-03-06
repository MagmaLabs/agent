#!/bin/bash

aptitude install build-essential python-dev

# api deps
aptitude install supervisor python-pip python-gevent python-requests
pip install docopt pyzmq

# metrics deps
#aptitude install python-psutil
pip install psutil

mkdir -p /var/log/appbus/

DIR=$( cd "$( dirname "$0" )" && pwd )

if [ ! -f $DIR/agent.conf ]; then
	cat > $DIR/agent.conf << EOF
[appbus]
api_host=api-dev.appbus.io
api_key=APIKEYHERE
EOF
fi

cat > /etc/supervisor/conf.d/appbus-agent.conf << EOF
[program:appbus-pusher]
command=python2.7 $DIR/appbusagent/pusher.py -f $DIR/agent.conf
redirect_stderr=true
stdout_logfile=/var/log/appbus/pusher.log

[program:appbus-metrics]
command=python2.7 $DIR/appbusagent/metricsService.py -f $DIR/agent.conf
redirect_stderr=true
stdout_logfile=/var/log/appbus/metrics.log

[program:appbus-updates]
command=python2.7 $DIR/appbusagent/updatesService.py -f $DIR/agent.conf
redirect_stderr=true
stdout_logfile=/var/log/appbus/updates.log
EOF

chmod o-rwx $DIR/agent.conf

echo 
echo 'Ready, just edit agent.conf and set up your api key.'
echo
echo 'To start the agent: supervisorctl reload; supervisorctl restart appbus-pusher'