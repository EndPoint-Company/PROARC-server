cat > /root/docker-compose.yml <<- "SCRIPT"

version: '3.3'

services:
  python_app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "9999:9999"
    
networks: #use same network across containers to simplify communication between containers
  dockernet:
    #driver: bridge
    external: # network created previously by 'docker network create dockernet' command
      name: dockernet

SCRIPT