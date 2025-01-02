IMAGE_NAME := prismpro2024/prism-fe-x86:9

docker_buildx:
	docker buildx build --platform linux/amd64 -t ${IMAGE_NAME} .

docker_push:
	docker push ${IMAGE_NAME}



docker_run:
	docker build -t ${IMAGE_NAME} .
	docker run -itd -p 80:80 ${IMAGE_NAME}

