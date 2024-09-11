# Use a base image with Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

RUN apt-get update && apt-get install -y apt-utils
RUN apt-get install -y build-essential bash curl unzip wget git libgl1-mesa-glx libglib2.0-0 

#Run pip dependencies
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt



# Expose port 8888 for JupyterLab
# EXPOSE 8888 
EXPOSE 9012
# EXPOSE 11434


# Acceder a la consola de la imagen
CMD [ "/bin/bash" ]
