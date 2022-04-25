#!/bin/bash

function start_apache {
	[ -f "/run/apache2/apache2.pid" ] && rm -f "/run/apache2/apache2.pid"
	echo "Launching apache2 in foreground with /usr/sbin/apache2ctl -DFOREGROUND -k start"
	/usr/sbin/apache2ctl -DFOREGROUND -k start
}

function stop_apache {
	echo "Stopping  apache2"
	/usr/sbin/apache2ctl stop
}

# Trap to have a clean exit
trap stop_apache HUP INT QUIT KILL TERM


# Main
cd /var/www/html
unzip -q -o /tmp/DSP2043_0.99.0a.zip
chmod 755 DSP2043_0.99.0a
ln -sf DSP2043_0.99.0a redfish
cd redfish
ln -sf . v1
cd ..
# Patch simulator to fix incorrect json
cd /
patch -p0 < /tmp/fix_manager_ei.patch
ip a
#sed -i -e 's/Listen 80/Listen 8000/' /etc/apache2/ports.conf
start_apache
