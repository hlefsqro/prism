IMAGE_NAME := prismpro2024/prism-fe-x86:open-6
#IMAGE_NAME := prismpro2024/prism-fe-x86:close-9

docker_buildx:
	docker buildx build --no-cache --platform linux/amd64 -t ${IMAGE_NAME} .

docker_push:
	docker push ${IMAGE_NAME}



docker_run:
	docker build -t 0.0 .
	docker run -itd -p 80:80 0.0

