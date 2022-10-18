### MAKEFILE TEMPLATE ###
### Edit this makefile to include the necessary mount points ###
build-deploy-dev: build-dev deploy-dev
build-deploy-prod: build-prod deploy-prod

build-dev:
	docker build -t=tb_wsi_dev .

deploy-dev:
	docker run -it \
    --mount type=bind,source=</full/path/to>/threat-beacon-wsi/src/,target=/opt/tb_wsi/ \
    --mount type=bind,source=</full/path/to>/elastipy-threat-beacon/,target=/opt/elastipy/ \
    --mount type=bind,source=</full/path/to>/tb_config.json,target=/opt/config/tb_config.json \
    --name tb_wsi_dev \
    --network="host" \
    -P \
    --rm \
    tb_wsi_dev:latest

build-prod:
	docker build -f dockerfile.prod -t=tb_wsi_prod .

deploy-prod:
    - docker stop tb_wsi
    - docker rm tb_wsi
    docker run -d \
    --mount type=bind,source=</full/path/to>/elastipy-threat-beacon/,target=/opt/elastipy/ \
    --mount type=bind,source=</full/path/to>/tb_config.json,target=/opt/config/tb_config.json \
    --name tb_wsi \
    -p 5010:5010 tb_wsi_prod:latest