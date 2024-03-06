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

Development Server
^^^^^^^^^^^^^^^^^^

1. Clone the repo from: https://github.com/eharvey71/edtech-platform-integration-bridge
2. From the command line, change to the root of the cloned repo. Edit the Dockerfile and ensure proper config for local dev. Depending on your environment, it should look something like the following:

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

    # Build the starter sample database
    RUN python build_database.py

    # Make port 80 available to the world outside this container
    EXPOSE 80

    # Use Uvicorn to run the application, replace `app:app` with your application and variable
    CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

3. From the root directory of the repo, build the image and launch a container (or use Docker desktop to perfom the run action)

.. code-block::

    docker build . -t integration-bridge-test
    docker run -p 4000:80 integration-bridge-test

4. Connect to http://localhost:4000/

Production Server
^^^^^^^^^^^^^^^^^

The following examples don't take into account the necessary optimization that may be required to deploy the Integation Bridge within certain cloud environments.
Please use them as a guide to get things started on certain target platforms.

Containerized App on Google Cloud Run - Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is just one method for deploying to Google Cloud Run. 
Using the UI provided by Google for deployment works fine but may be confusing, so this assumes knowlege of the Google CLI.
This is a simplified version to help get you started. Please refer to Google's documentation
for configuring your serverless instance and setting up your monitoring dashboard.

1. Install the `Google Cloud CLI`_ for your OS
   
.. _Google Cloud CLI: https://cloud.google.com/sdk/docs/install

2. Clone the repo from: https://github.com/eharvey71/edtech-platform-integration-bridge

   
3. From the command line, change to the root of the cloned repo. Edit the Dockerfile for "production"

.. code-block::
    :caption: **Dockerfile**

    # Use an official Python runtime as a parent image
    FROM python:3.8-slim

    # Set the working directory in the container
    WORKDIR /usr/src/app

    # Copy the current directory contents into the container at /usr/src/app
    COPY . .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements-prod.txt

    # Generate a random secret key and store it in an environment variable
    RUN echo "FLASK_SECRET_KEY=$(openssl rand -base64 32)" > .env

    # Build the starter sample database
    RUN python build_database.py

    # Production uses gunicorn
    CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app:app

4. From your current cloned project directory, you may need to initialize and get your project id before completing the next steps

.. code-block::

    gcloud init
    gcloud config get-value project

5. Set your region. This example assumes us-east-5

.. code-block::

    gcloud config set run/region us-east5

6. Build the new container image using the gcloud CLI and record the resulting container URL for the next step

.. code-block::

    gcloud builds submit --tag gcr.io/{YOUR-PROJECT-ID}/integration-bridge 

7. Launch the new containerized deployment from the glcoud container registry

.. code-block::

    gcloud run deploy integration-bridge --image {CONTAINER-URL} --platform managed

Step-by-Step Full Deployment
----------------------------

The integration bridge is built using the following frameworks and libaries:

* Connexion 3 Python web framework (with Flask, Uvicorn, Swagger-UI extras)
* Bootstrap 5
* SQL Alchemy ORM
* Additional Swagger-UI Bundle (when additional customization is required)

More to come ...

