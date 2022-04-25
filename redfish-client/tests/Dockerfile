# This Dockerfile is to build a container
# in order to run a standalone python-redfish example
FROM ubuntu:21.04
MAINTAINER bruno.cornec@hpe.com
ENV DEBIAN_FRONTEND noninterative
RUN apt-get update
RUN apt-get -y install python3-mock python3-pip python3-jinja2 python3-requests python3-urllib3 python3-docopt python3-simplejson python3-colorama python3-httpretty git openssh-client libpython3.9-dev python3-oslotest 
RUN pip3 install tortilla
RUN useradd -m tester
RUN chown -R tester /usr/local
RUN su - tester -c "git clone https://github.com/bcornec/python-redfish.git; pip install -r python-redfish/requirements.txt ; cd python-redfish ; python3 setup.py install -O1"
USER tester
CMD /bin/bash
