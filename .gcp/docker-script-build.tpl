cat > /root/docker-install.sh <<- "SCRIPT"
#!/bin/bash

##################Install docker#################
curl -sSL https://get.docker.com | sh

#################Install Docker Compose##########
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

SCRIPT