#!/bin/sh
set -e

# Install AVAHI and IPV6 so that it has a name and we can find it again
sudo apt-get update
sudo apt-get install avahi-daemon
sudo update-rc.d avahi-daemon defaults
echo ipv6 | sudo tee -a /etc/modules
echo Needs reboot to apply

mkdir ~/checkouts

# Install pi4j
cd ~/checkouts
wget https://pi4j.googlecode.com/files/pi4j-1.0-SNAPSHOT.deb
sudo dpkg -i pi4j-1.0.SNAPSHOT.deb

# Install WiringPi-Python
cd ~/checkouts
git clone https://github.com/WiringPi/WiringPi-Python.git
cd WiringPi-Python/
git submodule update --init
sudo apt-get install python2.7-dev python-setuptools
sudo python setup.py install

# Let java and python run for our build server without password
echo %ittltl ALL= NOPASSWD: /usr/bin/java| sudo tee -a /etc/sudoers
echo %ittltl ALL= NOPASSWD: /usr/bin/python| sudo tee -a /etc/sudoers

# Install git-daemon
sudo apt-get install git-daemon-run

# Host a copy of the github repos
cd /var/cache/git
sudo git clone --bare git://github.com/dmcg/ittltl-beaker.git
sudo touch ittltl-beaker.git/git-daemon-export-ok
sudo chown -R gitdaemon ittltl-beaker.git
sudo mv ittltl-beaker.git ittltl.git
sudo git clone --bare git://github.com/dmcg/ittltl-elmo.git
sudo touch ittltl-elmo.git/git-daemon-export-ok
sudo chown -R gitdaemon ittltl-elmo.git