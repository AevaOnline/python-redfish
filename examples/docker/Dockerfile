FROM ubuntu:15.04
MAINTAINER bruno.cornec@hp.com
ENV DEBIAN_FRONTEND noninterative
ENV http_proxy http://web-proxy.fra.hp.com:8080
ENV https_proxy http://web-proxy.fra.hp.com:8080
# Install deps for Redfish mockup
RUN apt-get update
RUN apt-get -y install python-mock python-pip git openssh-client libpython2.7-dev python-oslotest
RUN apt-get -y ansible
RUN useradd -m bruno
RUN chown -R bruno /usr/local
RUN su - bruno -c "git clone https://github.com/bcornec/python-redfish.git ; pip install -r python-redfish/requirements.txt ; cd python-redfish ; python setup.py install -O1"
CMD /bin/bash
