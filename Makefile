all:build-image

build-image:
	podman manifest rm springbrook_puller:latest
	podman build --jobs=2 --platform=linux/amd64,linux/arm64 --manifest springbrook_puller:latest .