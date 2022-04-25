#
# $Id$
#
%global with_python3 PBWITHPY3

Name:           PBREALPKG
Version:        PBVER
Release:        PBTAGPBSUF
Summary:        PBSUMMARY

License:        PBLIC
Group:          PBGRP
Url:            PBURL
Source:         PBREPO/PBSRC
Requires:       PBPYTHON2DEP,PBREALPKG-data
BuildArch:      noarch
BuildRequires:  PBPYTHON2BDEP, PB2PYTHON2BDEP

%description
PBDESC
Python2 version.

%if %{?with_python3}
%package -n PBPYTHON3PKG
Summary: %{summary} / Python 3 library
BuildRequires:  PBPYTHON3BDEP,PB2PYTHON3BDEP
Requires:       PBPYTHON3DEP,PBREALPKG-data

%description -n PBPYTHON3PKG
PBDESC
Python3 version.
%endif # if with_python3

%package -n PBREALPKG-doc
Summary: %{summary} / Documentation
BuildRequires:  PBPYTHONDOCBDEP

%description -n PBREALPKG-doc
PBDESC
Documentation

%package -n PBREALPKG-data
Summary: %{summary} / Data

%description -n PBREALPKG-data
PBDESC
Data

%prep
%setup -q -n %{name}-%{version}PBEXTDIR
# Fix for now as long as setuptools isn't more recent in distributions
%if %{?with_python3}
PBPYTHON3FILTER
cp -a . %{py3dir}
# python3 doesn't provide configparser at all
(cd %{py3dir} ; perl -pi -e "s|configparser>=3.3.0||" requirements.txt)
%endif # if with_python3

%build
%if %{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
# Build minimal documentation
cd doc
make man
popd
%endif # if with_python3

%{__python} setup.py build
# Build minimal documentation
cd doc
make man
make singlehtml
make latexpdf

%install

%if %{?with_python3}
pushd %{py3dir} 
./install.sh %{__python3} %{buildroot} %{python3_sitelib} %{_prefix} PBPYTHON3PKG
mv %{buildroot}%{_bindir}/redfish-client  %{buildroot}%{_bindir}/redfish-client-3
mv %{buildroot}%{_bindir}/redfish-check-cartridge  %{buildroot}%{_bindir}/redfish-check-cartridge-3
popd
%endif # if with_python3

./install.sh %{__python} %{buildroot} %{python_sitelib} %{_prefix} PBPKG

./install.sh %{_docdir} %{buildroot} %{python_sitelib} %{_prefix} PBPKG

for i in `ls %{buildroot}/%{_mandir}/man1/*-py2.1*`; do
	j=`echo $i | perl -p -e 's|-py2||'`
	cp -a $i $j
done

%files
%doc README.rst examples/[a-z]*.py LICENSE AUTHORS ChangeLog
%exclude %{_docdir}/PBREALPKG/manual/html
%exclude %{_docdir}/PBREALPKG/manual/*.pdf
%{_bindir}/redfish-client
%{_bindir}/redfish-check-cartridge
%dir %{python_sitelib}/redfish
%{python_sitelib}/redfish/*.py*
%{python_sitelib}/redfish/oem/*.py*
%{python_sitelib}/redfish/tests/*.py*
%{python_sitelib}/python_redfish*
# Needs improvement to host all .1 man pages but not the py3 ones
%{_mandir}/man1/PBREALPKG.1*
%{_mandir}/man1/*-py2.1*

%if %{?with_python3}
%files -n PBPYTHON3PKG
%doc README.rst examples/[a-z]*.py LICENSE AUTHORS ChangeLog
%exclude %{_docdir}/PBREALPKG/manual/html
%exclude %{_docdir}/PBREALPKG/manual/*.pdf
%{_bindir}/redfish-client-3
%{_bindir}/redfish-check-cartridge-3
%dir %{python3_sitelib}/redfish
%{python3_sitelib}/redfish/*.py*
%{python3_sitelib}/redfish/oem/*.py*
%{python3_sitelib}/redfish/oem/__pycache__/*.py*
%{python3_sitelib}/redfish/__pycache__/*.py*
%{python3_sitelib}/redfish/tests/*.py*
%{python3_sitelib}/redfish/tests/__pycache__/*.py*
%{python3_sitelib}/python_redfish*
%{_mandir}/man1/*-py3.1*
%endif # if with_python3

%files -n PBREALPKG-data
%config(noreplace) %{_sysconfdir}/redfish-client.conf
%config(noreplace) %{_sysconfdir}/bash_completion.d/redfish-client.bash
%dir %{_datadir}/redfish-client
%{_datadir}/redfish-client/templates/*
%{_datadir}/redfish-client/*.txt

%files -n PBREALPKG-doc
%{_docdir}/PBREALPKG/manual/html/_static/*
%{_docdir}/PBREALPKG/manual/html/index.html
%{_docdir}/PBREALPKG/manual/*.pdf

%changelog
PBLOG
