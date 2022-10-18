# Threat Beacon WSI

This project houses the code to deploy a Web Service Interface using flask and Python functions to construct the back-end operations. This code is meant to be deployed in a standalone container.

## Build and run the code for dev

### Build the Dev Env

    docker build -t=tb_wsi_dev .

### Run the Dev Env

#### Linux

    docker run -it \
    --mount type=bind,source=</full/path/to>/threat-beacon-wsi/src/,target=/opt/tb_wsi/ \
    --mount type=bind,source=</full/path/to>/elastipy-threat-beacon/,target=/opt/elastipy/ \
    --mount type=bind,source=</full/path/to>/tb_config.json,target=/opt/config/tb_config.json \
    --name tb_wsi_dev \
    --network="host" \
    -P \
    --rm \
    tb_wsi_dev:latest
    
*Note:*

* --mount options are required to have live reload of code working with out needing to rebuild the docker containers. 
* --it is needed for the pudb debugger to work
* --network="host" is needed for you to be able to reach the flask server from your host development machine
* -P exposes the internal ports, in this case 5000
* --rm deletes the container after it is shut down. Not required but prevents docker from filling up your disk as quickly.

#### Windows

    TODO:

## Build and run the code for Preprod/Production

### Build the Preprod/Production Env
    
This is temporary until we move them to a Gitlab automated build.
    
    docker build -f dockerfile.prod -t=tb_wsi_prod .
    
*NOTE:*

* -f dockferfile.prod must be included to build the preprod/production docker image. 
        
### Run the Prod container

This is temporary until we move this to an automated deployment with Gitlab. Pay attention to the different port used

    docker run -d \
    --mount type=bind,source=</full/path/to>/elastipy-threat-beacon/,target=/opt/elastipy/ \
    --mount type=bind,source=</full/path/to>/tb_config.json,target=/opt/config/tb_config.json \
    -p 5010:5010 tb_wsi_prod:latest
    
*Note:*
Currently you are required to have a copy of the elastipy-threat-beacon repo on the host. This will be fixed later. 

* -p 5010:5010 ensures the port mapping works correctly between the host and container
* -d runs the container in background mode, so you do not have to keep the terminal open to keep the docker container running

## Running Tests

To run tests with either the dev or the prod container, just add

    --entrypoint "pytest"

to the "docker run" command so that you override the start of the application and instead launch the testing. 