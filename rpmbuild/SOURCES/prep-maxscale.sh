#!/bin/bash

set -e

VERSION="21.06.18"
LIBMEMCACHED_VERSION="1.0.18"
MONGO_C_DRIVER_VERSION="1.27.5"
MONGO_CXX_DRIVER_VERSION="3.7.2"

rm -f *.tar.gz

git clone --branch maxscale-$VERSION --depth 1 https://github.com/mariadb-corporation/MaxScale.git
pushd MaxScale
git submodule update --init --recursive
bash maxctrl/npm_install.sh
bash maxgui/npm_install.sh

tar -zcf ../mariadb-connector-c-1.27.5.tar.gz mariadb-connector-c
tar -zcf ../maxctrl_node_modules.tar.gz maxctrl/node_modules
tar -zcf ../maxgui_node_modules.tar.gz maxgui/node_modules
popd

rm -rf MaxScale
wget https://github.com/mariadb-corporation/MaxScale/archive/refs/tags/maxscale-$VERSION.tar.gz
tar -zxf maxscale-$VERSION.tar.gz
mv MaxScale-maxscale-$VERSION maxscale-$VERSION
tar -zcf maxscale-$VERSION.tar.gz maxscale-$VERSION
rm -rf maxscale-$VERSION

# Tarball avro-c-1.10.0
wget https://github.com/apache/avro/archive/release-1.10.0.tar.gz
tar -zxf release-1.10.0.tar.gz && rm -f  release-1.10.0.tar.gz
mv avro-release-1.10.0 avro-c
tar -zcf avro-c-1.10.0.tar.gz avro-c
rm -rf  release-1.10.0.tar.gz avro-c

# Tarball hiredis-1.0.2
git clone --branch v1.0.2 --depth 1 https://github.com/redis/hiredis.git
tar -zcf hiredis-1.0.2.tar.gz hiredis
rm -rf hiredis

# Tarball libmemcached
wget https://launchpad.net/libmemcached/1.0/${LIBMEMCACHED_VERSION}/+download/libmemcached-${LIBMEMCACHED_VERSION}.tar.gz
tar -zxf libmemcached-${LIBMEMCACHED_VERSION}.tar.gz && rm -f libmemcached-${LIBMEMCACHED_VERSION}.tar.gz
mv libmemcached-${LIBMEMCACHED_VERSION} libmemcached
tar -zcf libmemcached-${LIBMEMCACHED_VERSION}.tar.gz libmemcached
rm -rf libmemcached

# Tarball mongo-c-driver-1.27.5
wget https://github.com/mongodb/mongo-c-driver/releases/download/${MONGO_C_DRIVER_VERSION}/mongo-c-driver-${MONGO_C_DRIVER_VERSION}.tar.gz
tar -zxf mongo-c-driver-1.27.5.tar.gz && rm -f mongo-c-driver-1.27.5.tar.gz
mkdir -p mongo-c-driver
mv mongo-c-driver-1.27.5 mongo-c-driver/
pushd mongo-c-driver
mv mongo-c-driver-1.27.5 src
popd
tar -zcf mongo-c-driver-1.27.5.tar.gz mongo-c-driver
rm -rf mongo-c-driver

# Tarball mongo-cxx-driver-${MONGO_CXX_DRIVER_VERSION}
git clone --branch v1.1.0 --depth 1 https://github.com/mnmlstc/core
mv core mnmlstc_core

wget https://github.com/mongodb/mongo-cxx-driver/releases/download/r${MONGO_CXX_DRIVER_VERSION}/mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION}.tar.gz
tar -zxf mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION}.tar.gz && rm -f mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION}.tar.gz
cp download-local-mnmlstc-core.patch mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION}/
pushd mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION}
patch -p1 < download-local-mnmlstc-core.patch
popd
mv mnmlstc_core mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION}/src/bsoncxx/third_party/
mkdir -p mongo-cxx-driver
mv mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION} mongo-cxx-driver/

pushd mongo-cxx-driver
mv mongo-cxx-driver-r${MONGO_CXX_DRIVER_VERSION} src
popd

tar -zcf mongo-cxx-driver${MONGO_CXX_DRIVER_VERSION}.tar.gz mongo-cxx-driver
rm -rf mongo-cxx-driver
