# ****************************************************************************
# ****************************************************************************
# Copyright SoC Design Research Group, All rights reserved.
# Electronics and Telecommunications Research Institute (ETRI)
# 
# THESE DOCUMENTS CONTAIN CONFIDENTIAL INFORMATION AND KNOWLEDGE
# WHICH IS THE PROPERTY OF ETRI. NO PART OF THIS PUBLICATION IS
# TO BE USED FOR ANY OTHER PURPOSE, AND THESE ARE NOT TO BE
# REPRODUCED, COPIED, DISCLOSED, TRANSMITTED, STORED IN A RETRIEVAL
# SYSTEM OR TRANSLATED INTO ANY OTHER HUMAN OR COMPUTER LANGUAGE,
# IN ANY FORM, BY ANY MEANS, IN WHOLE OR IN PART, WITHOUT THE
# COMPLETE PRIOR WRITTEN PERMISSION OF ETRI.
# ****************************************************************************
# 2020-04-20
# Kyuseung Han (han@etri.re.kr)
# ****************************************************************************
# ****************************************************************************

BBGIT_NAME=rvx_init
RVX_INIT_HOME=${PWD}
include ./set_git_repo.mh

PYTHON3_VERSION=3.6.0
PIP3=${shell which pip3}

config:
	echo "RVX_INIT_HOME=${PWD}" > ./source

python_centos:
	sudo yum install python2
	sudo yum install zlib zlib-devel openssl openssl-devel
	wget https://www.python.org/ftp/python/${PYTHON3_VERSION}/Python-${PYTHON3_VERSION}.tar.xz
	tar xvf Python-${PYTHON3_VERSION}.tar.xz
	cd ./Python-${PYTHON3_VERSION}; ./configure; make; sudo make install

python_ubuntu:
	sudo apt-get install python2
	sudo apt-get install python3
	sudo apt-get install python3-pip
	sudo apt-get upgrade python3
	sudo apt-get upgrade python3-pip

pip3:
	sudo ${PIP3} install --upgrade pip
	sudo ${PIP3} install cryptography paramiko pyelftools
	sudo ${PIP3} install --upgrade cryptography paramiko pyelftools

git_config:
	git config --global core.editor vim
	git config --global credential.helper 'cache --timeout=864000'

git_config_kshan: git_config
	git config --global user.name "Kyuseung Han"
	git config --global user.email han@etir.re.kr

set_bbname:
ifdef NAME
	echo -e "BB_USERNAME=${NAME}\nSSH_ACCESS=${SSH_ACCESS}" > ./${BB_USERNAME_FILENAME}
else
	@echo "NAME is not defined"
endif
