#!/usr/bin/env bash

# File:          install/install_on_contabo_part_2.sh
# By:            Samuel Duclos
# For:           Myself
# Usage:         cd ~/workspace/crypto_logger && bash install/install_on_contabo.sh
# Description:   Installs all packages required for the crypto_logger.
# Documentation: https://contabo.com/blog/first-steps-with-contabo/
#                https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-18-04

# Initial configuration.
echo "This will guide you through the initial Contabo server configuration (part 2)." && \
NEW_PASSWORD=$(cat contabo_keys.txt) && \
read -s -p "Enter your Contabo server's IP address: " SERVER_IP && \
echo "" && \
read -s -p "Enter your Contabo server's new user: " NEW_USER && \
echo "" && \
read -s -p "Enter your Contabo server's initial password: " SERVER_INITIAL_PASSWORD && \
echo "" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} apt-get update && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} apt-get install -y mosh supervisor && \
sshpass -p ${SERVER_INITIAL_PASSWORD} scp conf.d/*.conf root@${SERVER_IP}:/etc/supervisor/conf.d && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} supervisorctl reread && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "adduser --disabled-login --gecos \"\" \"${NEW_USER}\"" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "echo \"${NEW_USER}:${NEW_PASSWORD}\" | chpasswd" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "usermod -aG sudo ${NEW_USER}" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "sed -i 's/IPV6=no/IPV6=yes/g' /etc/default/ufw" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw default deny incoming" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw default allow outgoing" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw allow OpenSSH" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw allow 60000:61000/udp" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "yes | ufw enable" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo -e "echo \"AllowUsers\t${NEW_USER}\" >> /etc/ssh/sshd_config" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "systemctl restart sshd" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "sed -i 's/HISTSIZE=1000/HISTSIZE=100000/g' /home/${NEW_USER}/.bashrc" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "sed -i 's/HISTFILESIZE=2000/HISTFILESIZE=20000/g' /home/${NEW_USER}/.bashrc" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "mkdir -p ~/workspace" ) #&& \
#cat install/install_conda.sh ${NEW_USER} | sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} && \
#cat install/install_crypto_logger_conda_environment.sh | sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} && \
#sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} env | grep USER | sed 's/USER=//'