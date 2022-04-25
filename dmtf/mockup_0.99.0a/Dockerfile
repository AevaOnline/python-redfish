# Invoke with docker run -p 8000:80 <dockerimageid>
# Then use by browsing http://localhost:8000
FROM ubuntu:16.04
MAINTAINER bruno.cornec@hpe.com
ENV DEBIAN_FRONTEND noninterative
# Install deps for Redfish mockup
RUN apt-get update
RUN apt-get -y install apache2 unzip sed patch vim
EXPOSE 80
COPY redfish-setup.sh /tmp/redfish-setup.sh
COPY DSP2043_0.99.0a.zip /tmp/DSP2043_0.99.0a.zip
COPY fix_manager_ei.patch /tmp/fix_manager_ei.patch
RUN chmod 755 /tmp/redfish-setup.sh
CMD /tmp/redfish-setup.sh
