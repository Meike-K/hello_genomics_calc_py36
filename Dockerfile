# you can use any base image you like for example python:3.6.1 or the smaller version python:3.6.1-alpine
FROM python:3.6-alpine

# These values provide you the data you need. See the readme.md file for details
VOLUME /fastgenomics/data/
VOLUME /fastgenomics/config/
VOLUME /fastgenomics/output/
VOLUME /fastgenomics/summary/

# Install core dependencies
RUN apk add --update --no-cache git

# Install any dependencies your app has (including our fastgenomics-py module)
COPY ./requirements.txt /requirements/
RUN pip install -r /requirements/requirements.txt

# Copy your app manifest to /app - must be located here for usage of default parameters
COPY manifest.json /app/

# Copy your code into the app
COPY hello_genomics /app/hello_genomics/
COPY templates /app/templates/

# Run the app when the container starts.
WORKDIR /app/
ENV PYTHONPATH /app/
CMD ["python", "-m", "hello_genomics"]
