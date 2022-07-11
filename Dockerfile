#what is the basis of our image, get python image
FROM python:3
#environment command needed sometimes?
# ENV PYTHONUNBUFFERED 1
#workdir tells docker when you start,
#go to this directory to start (cds into app)
WORKDIR /app
#copy copies files for you into another file
#copy 1 (from app) into 2 (working dir), named the same
COPY accounts accounts
COPY attendees attendees
COPY common common
COPY conference_go conference_go
COPY events events
COPY presentations presentations
COPY requirements.txt requirements.txt
COPY manage.py manage.py
#run kicks the whole thing off
RUN pip install -r requirements.txt
#an array of strings from what you would type in terminal
CMD gunicorn --bind 0.0.0.0:8000 conference_go.wsgi

# Select the base image that is best for our application
# Install any operating system junk
# Set the working directory to copy stuff to
# Copy all the code from the local directory into the image
# Install any language dependencies
# Set the command to run the application