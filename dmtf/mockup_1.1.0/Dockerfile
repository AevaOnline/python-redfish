FROM httpd:2.4
MAINTAINER bruno.cornec@hpe.com
ENV DEBIAN_FRONTEND noninterative
# Install deps for Redfish mockup
RUN apt-get update
RUN apt-get -y install unzip sed vim lsof curl
EXPOSE 8001 8002 8003 8004 8005 8006
COPY redfish-setup.sh /tmp/redfish-setup.sh
COPY DSP2043_1.1.0.zip /usr/local/apache2/htdocs/DSP2043_1.1.0.zip
RUN chmod 755 /tmp/redfish-setup.sh
RUN cd /usr/local/apache2/htdocs && unzip DSP2043_1.1.0.zip
RUN chmod -R og+rx /usr/local/apache2/htdocs/DSP2043_1.1.0
COPY httpd.conf /usr/local/apache2/conf/httpd.conf
COPY httpd-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf
CMD /tmp/redfish-setup.sh
