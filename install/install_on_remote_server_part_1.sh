#!/usr/bin/env bash

# File:          install/install_on_remote_server_part_1.sh
# By:            Samuel Duclos
# For:           Myself
# Usage:         bash install/install_on_remote_server_part_1.sh
# Description:   Installs all packages required for the crypto_logger.
# Documentation: https://contabo.com/blog/first-steps-with-contabo/
#                https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-18-04

# Initial configuration.
echo "This will guide you through the initial Contabo server configuration (part 1)." && \
echo "Here is what you should read if you have any questions: https://contabo.com/blog/first-steps-with-contabo/" && \
read && \
echo "Please login with a browser to your Contabo configuration panel using your CONTABO_ACCOUNT and CONTABO_INITIAL_PASSWORD" && \
read && \
echo "Your server's IP is in \"IP management\"." && \
echo "Please navigate to \"VPS control\" and click \"Manage\", then \"Password reset\"." && \
read && \
echo "Please navigate to \"VPS control\" and click \"Manage\", then \"Disable VNC\"." && \
read && \
echo "Please add a file \"server_keys.txt\" in the repository base directory with just a single line " && \
echo "with your desired non-root user password, then press <ENTER>" && \
read && \
read -s -p "Enter your local sudo password: " LOCAL_PASSWORD && \
echo "" && \
read -s -p "Enter your server's IP address: " SERVER_IP && \
echo "" && \
echo ${LOCAL_PASSWORD} | sudo -S apt-get update && \
echo ${LOCAL_PASSWORD} | sudo -S apt-get install -y sshpass && \
read -s -p "Press the <ENTER> key, type yes then <ENTER> again, then type the password and <ENTER> again." DUMMY && \
echo "" && \
echo "Press the <ENTER> key, type the root password and <ENTER> again." && \
read -s -p "Then on the server, type \"exit\" then <ENTER>..." DUMMY && \
echo "" && \
ssh-keygen -f "${HOME}/.ssh/known_hosts" -R "${SERVER_IP}" && \
ssh root@${SERVER_IP}
