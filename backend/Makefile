run_app:
	poetry run python -m prism.app

docker_build:
	docker build -t prismpro2024/prism-be:latest .

docker_buildx:
	docker buildx build --platform linux/amd64 -t prismpro2024/prism-be-x86:latest .



docker_push:
	docker push prismpro2024/prism-be:latest

docker_push_x86:
	docker push prismpro2024/prism-be-x86:latest