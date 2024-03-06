.. _deployment-docs-ref:

Deployment
==========

There are several deployment strategies for the Integration Bridge application.

#. Self-hosted. Build from the repository and host in a datacenter at your institution.
#. Vendor-hosted. Bundle with a solution and give institutional admins access for configuration.
#. Cloud-hosted and managed by the developer. Hosted and customized for your needs. Depending on use-case, cost would be fair. For example, hosting an instance on Google Cloud has resulted in pennies a month due to the low network and storage utilization.

In all cases, customizations of the integration bridge may be required. More is covered in the :doc:`customization` section of this doc.

Recommended deployment (Docker)
-------------------------------

Development
^^^^^^^^^^^

#. Clone the repo from: https://github.com/eharvey71/edtech-platform-integration-bridge
#. From the command line, change to the root of the cloned repo. Edit the Dockerfile and ensure proper config for local dev. Depending on your environment, it should look something like the following:

.. code-block::
    :caption: **Dockerfile**

    # Use an official Python runtime as a parent image
    FROM python:3.8-slim

    # Set the working directory in the container
    WORKDIR /usr/src/app

    # Copy the current directory contents into the container at /usr/src/app
    COPY . .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Generate a random secret key and store it in an environment variable
    RUN echo "FLASK_SECRET_KEY=$(openssl rand -base64 32)" > .env

    # Make port 80 available to the world outside this container
    EXPOSE 80

    # Use Uvicorn to run the application, replace `app:app` with your application and variable
    CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

#. From the root directory of the repo, build the image and launch a container (or use Docker desktop to perfom the run action)

.. code-block::

    docker build . -t integration-bridge-test
    docker run -p 4000:80 integration-bridge-test

#. Connect to http://localhost:4000/
