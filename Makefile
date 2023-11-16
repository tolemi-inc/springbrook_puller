all:build-image

build-image:
	podman manifest rm springbrook-puller:latest
	podman build --jobs=2 --platform=linux/amd64,linux/arm64 --manifest springbrook-puller:latest .