%define debug_package %{nil}

Name:          maxscale
Version:       21.06.18
Release:       1%{?dist}
Summary:       MaxScale - An intelligent database proxy
License:       MariaDB BSL 1.1
URL:           https://mariadb.com/products/mariadb-maxscale
Group:         Applications/Databases
Vendor:        MariaDB PLC
Source:        %{name}-%{version}.tar.gz
Source1:       avro-c-1.10.0.tar.gz
Source2:       hiredis-1.0.2.tar.gz
Source3:       libmemcached-1.0.18.tar.gz
Source4:       mongo-c-driver-1.27.5.tar.gz
Source5:       mongo-cxx-driver3.7.2.tar.gz
Source6:       mariadb-connector-c-1.27.5.tar.gz
Source7:       maxctrl_node_modules.tar.gz
Source8:       maxgui_node_modules.tar.gz
Patch0:        download-local-avro-c.patch
Patch1:        download-local-hiredis.patch
Patch2:        download-local-memcache.patch
Patch3:        download-local-mongo-c-driver.patch
Patch4:        download-local-mongo-cxx-driver.patch
Patch5:        maxctl-download-local-node-module.patch
Patch6:        maxgui-download-local-node-module.patch
Patch7:        build-maxgui-with-openssl3+.patch
BuildRequires: cmake >= 3.16
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: ncurses-devel
BuildRequires: bison
BuildRequires: glibc-devel
BuildRequires: ccache
BuildRequires: libgcc
BuildRequires: perl
BuildRequires: make
BuildRequires: libtool
BuildRequires: libaio libaio-devel
BuildRequires: systemtap-sdt-devel
BuildRequires: rpm-sign
BuildRequires: gnupg
BuildRequires: git
BuildRequires: flex
BuildRequires: rpmdevtools
BuildRequires: tcl tcl-devel
BuildRequires: openssl openssl-devel
BuildRequires: libuuid-devel xz-devel
BuildRequires: sqlite sqlite-devel
BuildRequires: pkgconfig
BuildRequires: rpm-build createrepo yum-utils
BuildRequires: gnutls-devel libgcrypt-devel
BuildRequires: pam-devel
BuildRequires: libcurl-devel
BuildRequires: libatomic
BuildRequires: cyrus-sasl-devel
BuildRequires: libxml2-devel
BuildRequires: krb5-devel
BuildRequires: libicu-devel
BuildRequires: systemd-devel systemd-rpm-macros
BuildRequires: pcre2-devel
BuildRequires: jansson-devel
BuildRequires: libmicrohttpd-devel
BuildRequires: boost-devel
BuildRequires: librdkafka-devel
BuildRequires: zlib-devel
BuildRequires: lua lua-devel
BuildRequires: libedit-devel
BuildRequires: libmemcached-devel
BuildRequires: libasan libubsan
BuildRequires: epel-release
BuildRequires: lcov
BuildRequires: libstdc++
BuildRequires: nodejs >= 22
%{?sysusers_requires_compat}

%ifarch aarch64
BuildRequires: python3 python2
%endif

Requires: nodejs >= 22
Requires: systemd
Requires: shadow-utils

%ifarch aarch64
Requires: python3 python2
%endif

%description
MariaDB MaxScale is an intelligent proxy that allows forwarding of
database statements to one or more database servers using complex rules,
a semantic understanding of the database statements and the roles of
the various servers within the backend cluster of databases.

MaxScale is designed to provide load balancing and high availability
functionality transparently to the applications. In addition it provides
a highly scalable and flexible architecture, with plugin components to
support different protocols and routing decisions.

%prep
%setup
%setup -D -a 1

%setup -D -a 2
mv hiredis server/modules/filter/cache/storage/storage_redis/

%setup -D -a 3
%setup -D -a 4
%setup -D -a 5

rm -rf mariadb-connector-c
%setup -D -a 6

%setup -D -a 7
%setup -D -a 8

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
mkdir build
cd build
cmake ../ -DCMAKE_INSTALL_PREFIX=%{_prefix} -DCMAKE_BUILD_TYPE=Release -DWITH_LTO=ON -DBUILD_TESTS=OFF
%{__make} %{?_smp_mflags}

%install
cd build
%{__make} install DESTDIR=%{buildroot}

# Remove stuff relating to System V
rm -rf %{buildroot}%{_sysconfdir}/init
rm -rf %{buildroot}%{_sysconfdir}/init.d

cp %{buildroot}%{_unitdir}/maxscale.service %{buildroot}%{_datadir}/maxscale/maxscale.service

%pre
#!/bin/sh

ARCH=$(uname -m)
REQUIRED_NODE_VERSION="22"
TIMEOUT=30
INTERVAL=1
ELAPSED=0

installed_node_version=$(node -v 2>/dev/null | cut -d. -f1 | tr -d 'v' || echo "0")
if [ "$installed_node_version" -gt "1" ] && [ "$installed_node_version" -lt "$REQUIRED_NODE_VERSION" ]; then
    echo "  Installing Node.js 22 ..."
    if [ "$ARCH" = "aarch64" ]; then
        nohup sh -c 'dnf module reset -y nodejs && dnf module enable -y nodejs:22 && dnf install -y nodejs npm' &

        while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
            installed_node_version=$(node -v 2>/dev/null | cut -d. -f1 | tr -d 'v' || echo "0")
            if [ "$installed_node_version" -eq "$REQUIRED_NODE_VERSION" ] ; then
                echo "  Completing installation of Node.js 22 ..."
                break
            fi

            sleep $INTERVAL
            ELAPSED=$((ELAPSED + INTERVAL))
        done
    else
        sh -c 'dnf module reset -y nodejs && dnf module enable -y nodejs:22 && dnf install -y nodejs npm'
    fi
fi

%post
#!/bin/sh

# Create directories
mkdir -p %{_libdir}/maxscale
mkdir -p %{_bindir}
mkdir -p %{_datadir}/maxscale
mkdir -p %{_datadir}/doc/MaxScale/maxscale

# MAXSCALE_VARDIR is an absolute path to /var by default
mkdir -p /var/log/maxscale
mkdir -p /var/lib/maxscale
mkdir -p /var/cache/maxscale
mkdir -p /var/run/maxscale

# Create MaxScale user if it doesnt' exist
if ! getent passwd maxscale > /dev/null
then
    groupadd -r maxscale
    useradd -r -s /bin/false -g maxscale maxscale
fi

# Change the owner of the directories to maxscale:maxscale
chown -R maxscale:maxscale /var/log/maxscale
chown -R maxscale:maxscale /var/lib/maxscale
chown -R maxscale:maxscale /var/cache/maxscale
chown -R maxscale:maxscale /var/run/maxscale
chmod 0755 /var/log/maxscale
chmod 0755 /var/lib/maxscale
chmod 0755 /var/cache/maxscale
chmod 0755 /var/run/maxscale

# Create the module configuration directory (default: /etc/maxscale.modules.d/)
mkdir -p %{_sysconfdir}/maxscale.modules.d

# Only copy the service files if the systemd folder and systemctl executable are found
if [ -f %{_datadir}/maxscale/maxscale.service ] && command -v systemctl > /dev/null
then
    if [ -d "/lib/systemd/system"  ]
    then
        cp %{_datadir}/maxscale/maxscale.service /lib/systemd/system
        systemctl daemon-reload > /dev/null 2>&1
    elif [ -d "%{_unitdir}"  ]
    then
        cp %{_datadir}/maxscale/maxscale.service %{_unitdir}
        systemctl daemon-reload > /dev/null 2>&1
    fi

    # Remove old directories, mistakenly installed by a few versions
    if [ -d /lib/systemd/system/maxscale.service.d ]
    then
        rmdir /lib/systemd/system/maxscale.service.d
    elif  [ -d %{_unitdir}/maxscale.service.d ]
    then
        rmdir %{_unitdir}/maxscale.service.d
    fi

    mkdir -p %{_sysconfdir}/systemd/system/maxscale.service.d
    systemctl enable maxscale.service > /dev/null 2>&1

    systemctl is-active maxscale.service --quiet > /dev/null 2&>1 && systemctl restart maxscale.service > /dev/null 2>&1
fi

# If no maxscale.cnf file is found in /etc, copy the template file there
if [ ! -f "%{_sysconfdir}/maxscale.cnf" ]
then
    cp %{_sysconfdir}/maxscale.cnf.template %{_sysconfdir}/maxscale.cnf
    mkdir -p %{_sysconfdir}/maxscale.cnf.d/
fi

# If no logrotate config file is found, create one
if [ ! -f "%{_sysconfdir}/logrotate.d/maxscale_logrotate" ]
then
    cp %{_datadir}/maxscale/maxscale_logrotate %{_sysconfdir}/logrotate.d/maxscale_logrotate
fi

/sbin/ldconfig

%preun

#!/bin/sh

# The first argument is the number of packages left after
# this one has been removed. If it is 0 then the package is being
# removed from the system.
if [ "$1" = "0" ] || [ "$1" = "remove" ]; then
    SERVICE_FILE=""

    # Determine the correct service file location
    if [ -f %{_unitdir}/maxscale.service ]; then
        SERVICE_FILE="%{_unitdir}/maxscale.service"
    elif [ -f /lib/systemd/system/maxscale.service ]; then
        SERVICE_FILE="/lib/systemd/system/maxscale.service"
    fi

    # If the service file exists, stop, disable, and remove it
    if [ -n "$SERVICE_FILE" ]; then
        systemctl stop maxscale.service > /dev/null 2>&1
        systemctl disable maxscale.service > /dev/null 2>&1
        rm -f "$SERVICE_FILE"
        systemctl daemon-reload > /dev/null 2>&1
    fi
fi

%postun
%systemd_postun %{name}.service

%files
%defattr(-,root,root,-)

%{_bindir}/cdc*.py
%{_bindir}/dbfwchk
%{_bindir}/max*
%{_bindir}/test_pam_login

%{_libdir}/maxscale

%{_datadir}/maxscale
%{_datadir}/man/man1/maxctrl.1*
%{_datadir}/man/man1/maxkeys.1*
%{_datadir}/man/man1/maxpasswd.1*
%{_datadir}/man/man1/maxscale.1*

%config %{_sysconfdir}/maxscale.cnf.template

%{_sysconfdir}/ld.so.conf.d/maxscale.conf
%{_sysconfdir}/logrotate.d/maxscale_logrotate
%ghost %{_unitdir}/maxscale.service

%changelog
* Fri Feb 28 2025 <nthien86@gmail.com> - 21.06.18-1
- Initial package for maxscale

