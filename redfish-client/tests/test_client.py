# coding=utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from builtins import object
import os
import stat
import subprocess
import re
import pytest
from docker import Client
from path import Path
standard_library.install_aliases()


class DockerTest(object):
    def __init__(self):
        self.cli = Client(base_url='unix://var/run/docker.sock')

    def build(self, dockerfile):
        dockerfile = Path(dockerfile)
        tag = 'rf-' + dockerfile.basename().replace('.dkf', '')
        dockerfile.copy('redfish-client/tests/Dockerfile')
        response = [line for line in self.cli.build(
            path='redfish-client/tests',
            tag=tag,
            rm=True)]
        return(response)

    def run(self, image, command):
        container = self.cli.create_container(image=image,
                                              command=command,
                                              tty=True,
                                              stdin_open=True)
        self.cli.start(container=container.get('Id'))
        self.cli.wait(container=container.get('Id'))
        response = self.cli.logs(container=container.get('Id'),
                                 stdout=True)
        self.cli.remove_container(container=container.get('Id'))
        return(response.decode('utf8'))


def local_docker_available():
    try:
        mode = os.stat('/var/run/docker.sock').st_mode
    except OSError:
        return False
    isSocket = stat.S_ISSOCK(mode)
    if not isSocket:
        print('Make sure docker services are running')
        return False

    cli = Client(base_url='unix://var/run/docker.sock')
    response = cli.containers()
    if not isinstance(response, list):
        print('Ensure you have sufficiant' +
              'credentials to use docker with' +
              'your current user')
        return False
    return True


local_docker = pytest.mark.skipif(
    not local_docker_available(), reason="Docker is not available locally")


@local_docker
def test_sources():
    output = subprocess.check_output(["python", "setup.py", "sdist"])
    search = re.search(r"removing '(\S+)'", str(output))
    filename = Path('dist/' + search.group(1) + '.tar.gz')
    filename.copy('redfish-client/tests/python-redfish.src.tar.gz')
    assert Path('redfish-client/tests/python-redfish.src.tar.gz').isfile()


@local_docker
def test_dockerbuild():
    docker = DockerTest()
    # Warning :  Image tag is derived from file name, do not use uppercase !!!
    #            because docker image tags can not use uppercase so far.
    dockerfiles = ('redfish-client/tests/ubuntu-20.04-src-p3.dkf',
                   'redfish-client/tests/debian-11-src-p3.dkf',
                   'redfish-client/tests/centos-7-src-p3.dkf',
                   'redfish-client/tests/fedora-35-src-p3.dkf',
                   'redfish-client/tests/fedora-35-pip-p3.dkf',)
    for dockerfile in dockerfiles:
        print('Testing : {}'.format(dockerfile))
        response = docker.build(dockerfile)
        status = str(response[-2])
        assert 'Successfully built' in status, f"error with {dockerfile} : {status}"


@local_docker
def test_install():
    docker = DockerTest()
    images = ('rf-ubuntu-20.04-src-p3',
              'rf-debian-11-src-p3',
              'rf-centos-7-src-p3',
              'rf-fedora-35-src-p3',
              'rf-fedora-35-pip-p3')
    for img in images:
        print('Testing : {}'.format(img))
        response = docker.run(img, 'redfish-client config showall')
        print(response)
        assert ('Managers configured' in response and 'None' in response)


@local_docker
def test_versionformat():
    docker = DockerTest()
    images = ('rf-ubuntu-20.04-src-p3',
              'rf-debian-11-src-p3',
              'rf-centos-7-src-p3',
              'rf-fedora-35-src-p3',
              'rf-fedora-35-pip-p3')
    for img in images:
        print('Testing : {}'.format(img))
        response = docker.run(img, 'redfish-client --version')
        print(response)
        assert (re.match(r'redfish-client \d+\.\d+', response))
