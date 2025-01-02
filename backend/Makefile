IMAGE_NAME := prismpro2024/prism-be-x86:27

run_app:
	poetry run python -m prism.app

docker_buildx:
	docker buildx build --platform linux/amd64 -t ${IMAGE_NAME} .

docker_push:
	docker push ${IMAGE_NAME}