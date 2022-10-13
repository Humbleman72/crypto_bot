# Run this from local machine:
apt update
apt install -y openssh-server sshfs vde2
mkdir -p /home/samuel/workspace/crypto_logs/
ln -s crypto_logs crypto_logs_sshfs
dpipe /usr/lib/openssh/sftp-server = ssh sam@154.12.239.24 sshfs -o follow_symlinks :/home/samuel/workspace/crypto_logs/ /home/sam/workspace/crypto_logs_sshfs -o slave,nonempty
