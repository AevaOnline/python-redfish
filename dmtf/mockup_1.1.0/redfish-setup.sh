#!/bin/bash

function start_apache {
	[ -f "/usr/local/apache2/logs/httpd.pid" ] && rm -f "/usr/local/apache2/logs/httpd.pid"
	echo "Launching apache2 in foreground with /usr/local/apache2/bin/apachectl -DFOREGROUND -k start"
	/usr/local/apache2/bin/apachectl -DFOREGROUND -k start
}

function stop_apache {
	echo "Stopping  apache2"
	/usr/local/apache2/bin/apachectl stop
}

# Trap to have a clean exit
trap stop_apache HUP INT QUIT KILL TERM


# Main
start_apache
