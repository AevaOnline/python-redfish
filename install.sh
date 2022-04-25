#!/bin/bash

# Syntax: install.sh <Python> <Root Dir> <Python SiteLib> <Prefix> <PkgName>
set -x 

export python=$1
export rootdir=$2
export sitelib=$3
export prefix=$4
export pkg=$5

# Documentation installation only
echo $python | grep -q "/doc"
if [ $? -eq 0 ]; then
	install -m 755 -d $rootdir/$python/$5/manual/html/_static
	install -m 644 doc/build/singlehtml/*.html $rootdir/$python/$5/manual/html
	install -m 644 doc/build/singlehtml/_static/* $rootdir/$python/$5/manual/html/_static
	install -m 644 doc/build/latex/*.pdf $rootdir/$python/$5/manual/
	exit 0
fi

pyver=`$python --version 2>&1 | perl -p -e 's|.* ([2-3])\..*|$1|'`
$python setup.py install --skip-build --root=$rootdir --prefix=$prefix

rm -rf $rootdir/$sitelib/redfish/old $rootdir/$prefix/share/doc/$5/html $rootdir/$prefix/share/doc/$5/*.pdf

# Hardcoded for now to solve the delivery of the conf file still not correct with setup.py
install -d 755 $rootdir/etc
mv $rootdir/$prefix/etc/redfish-client.conf $rootdir/etc/redfish-client.conf
install -d 755 $rootdir/etc/bash_completion.d
install -m 644 redfish-client/etc/bash_completion.d/redfish-client.bash $rootdir/etc/bash_completion.d

# Man pages installation
for i in 1; do
	mkdir -p $rootdir/$prefix/share/man/man$i
	for e in `ls doc/build/man/*.$i`; do
		ne=`echo $e | perl -p -e 's|.*/([^/]*)\.'$i'|$1-py'$pyver.$i'|'`
		install -m 644 $e $rootdir/$prefix/share/man/man$i/$ne
	done
done
