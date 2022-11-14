#!/usr/bin/env bash

# File:          install/install_on_contabo.sh
# By:            Samuel Duclos
# For:           Myself
# Usage:         cd ~/workspace/crypto_logger && bash install/install_on_contabo.sh
# Description:   Installs all packages required for the crypto_logger.
# Documentation: https://contabo.com/blog/first-steps-with-contabo/
#                https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-18-04

# Initial configuration.
echo "This will guide you through the initial Contabo server configuration." && \
echo "Here is what you should read if you have any questions: https://contabo.com/blog/first-steps-with-contabo/" && \
read && \
echo "Please login with a browser to your Contabo configuration panel using your CONTABO_ACCOUNT and CONTABO_INITIAL_PASSWORD" && \
read && \
echo "Your server's IP is in \"IP management\"." && \
echo "Please navigate to \"VPS control\" and click \"Manage\", then \"Password reset\"." && \
read && \
echo "Please navigate to \"VPS control\" and click \"Manage\", then \"Disable VNC\"." && \
read && \
echo "Now, make sure that you have a file named contabo_keys.txt, containing " && \
echo "your desired password, in the same directory where you are running this code." && \
read && \
NEW_PASSWORD=$(cat contabo_keys.txt) && \
read -s -p "Enter your local sudo password: " LOCAL_PASSWORD && \
read -s -p "Enter your Contabo server's IP address: " SERVER_IP && \
read -s -p "Enter your Contabo server's initial password: " SERVER_INITIAL_PASSWORD && \
echo ${LOCAL_PASSWORD} | sudo -S apt-get update && \
echo ${LOCAL_PASSWORD} | sudo -S apt-get install -y sshpass && \
ssh-keygen -f "${HOME}/.ssh/known_hosts" -R "${SERVER_IP}" && \
ssh root@${SERVER_IP} && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "adduser \"${NEW_USER}\" --disabled-login" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "echo \"${NEW_USER}:${NEW_PASSWORD}\" | chpasswd" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "usermod -aG sudo ${NEW_USER}" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "sed -i 's/IPV6=no/IPV6=yes/g' /etc/default/ufw" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} bash -c "ufw default deny incoming" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} bash -c "ufw default allow outgoing" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} bash -c "ufw allow OpenSSH" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} bash -c "ufw allow 60000:61000/udp" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} bash -c "yes | ufw enable" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} echo -e "AllowUsers\t${NEW_USER}" >> /etc/ssh/sshd_config && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} systemctl restart sshd && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} sed -i 's/HISTSIZE=1000/HISTSIZE=100000/g' /home/${NEW_USER}/.bashrc && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} sed -i 's/HISTFILESIZE=2000/HISTFILESIZE=20000/g' /home/${NEW_USER}/.bashrc && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} apt-get update && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} apt-get install -y mosh supervisor #&& \
#cat install/install_conda.sh ${NEW_USER} | sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} && \
#cat install/install_crypto_logger_conda_environment.sh | sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} && \
#sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} env | grep USER | sed 's/USER=//'
