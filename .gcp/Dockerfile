FROM amazonlinux:latest

# Update packages and install necessary dependencies
RUN yum update -y && \
    yum install -y git python3-pip

# Clone the repository
RUN git clone https://github.com/Sada-Siva-Reddy07/fish.git /fish

# Set the working directory
WORKDIR /fish

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose port 2000 (if required)
EXPOSE 9999

# Specify the command to run the Python application
CMD ["python3", "./server.py"]