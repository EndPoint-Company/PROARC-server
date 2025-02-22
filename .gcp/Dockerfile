FROM ubuntu:latest

# Update packages and install necessary dependencies
RUN sudo apt update    
RUN sudo apt upgrade      
RUN sudo apt full-upgrade 
RUN sudo apt autoremove    

# Clone the repository
RUN git clone https://github.com/EndPoint-Company/PROARC-server /server

# Set the working directory
WORKDIR /server

# Install Python dependencies
RUN pip3 install orjson
RUN pip3 install psycopg2

EXPOSE 9999

# Specify the command to run the Python application
CMD ["python3", "./server.py"]