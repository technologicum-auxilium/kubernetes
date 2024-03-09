#!/bin/bash
echo "Install repositorio Vagrant"
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

echo "Update System"
sudo apt update
sudo apt upgrade

echo "Install Vagrant and Python"
sudo apt install vagrant python3-pip

echo "Install Plugin"
vagrant plugin install vagrant-bindfs
vagrant plugin install virtualbox_WSL2

echo "Ansible, Ansible Vault, Molecule and Pre Commit"
pip3 install ansible ansible-vault molecule pre-commit