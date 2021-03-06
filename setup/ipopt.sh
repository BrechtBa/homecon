#!/bin/bash
# Ipopt (pronounced eye pee opt) is a solver for large scale non-linear programs (NLP) using the interior point algorithm. 
# In KNXControl we will use the program from Smarthome.py to do a system identification. 
# We will compile the program from source ourself as there is no suitable binary for Raspberry-pi. 
# Documentation is found at http://www.coin-or.org/Ipopt/documentation/

# Get the current working directory
cwd=$(pwd)

# Install prequisites
apt-get -y install git gcc g++ gfortran subversion patch wget

# Get ipopt from the repository
cd /usr/local
svn co https://projects.coin-or.org/svn/Ipopt/stable/3.11 CoinIpopt 
installdir="/usr/local/CoinIpopt"
cd $installdir


# Getting 3rd party libraries, there are files present in the Ipopt source to do this so we will use them. 
# We will use the MUMPS Linear solver as it is open, not everyone has access to an academic solver like MA57 and for our purpose it will be sufficient.
cd $installdir/ThirdParty/Blas/
./get.Blas
cd $installdir/ThirdParty/Lapack
./get.Lapack
cd $installdir/ThirdParty/ASL
./get.ASL
cd $installdir/ThirdParty/Mumps
./get.Mumps
cd $installdir/ThirdParty/Metis
./get.Metis
cd $installdir

# compiling
mkdir $installdir/build
cd $installdir/build
$installdir/configure --prefix=/usr/local/ -C ADD_CFLAGS="-DNO_fpu_control"
make
make test
make install

# test the example
cd $installdir/build/Ipopt/examples/hs071_cpp
make
./hs071_cpp

# If everything works you should see some program iterations and a reported that a solution was found `*** The problem solved!`.


cd $cwd
