IMAGE ?= ubuntu
TMP_IMAGE_NAME ?= dotfile_test_image:$(IMAGE)
LIMITS="--cpu-shares=256"
USER ?= $(shell whoami)
DOCKER ?= docker

BUILD:="${DOCKER}" build . -t ${TMP_IMAGE_NAME} ${LIMITS} --build-arg USER=${USER}

all: 
	$(MAKE) run
	$(MAKE) clean

build:
	${BUILD} -f Dockerfile-${IMAGE}

clean:
	${DOCKER} image rm -f ${TMP_IMAGE_NAME}

# Network host is used to avoid a plethora of issues such as proxy configuration, VPN, etc..
# Shared mount of home dirs is used to support the autofs mounts.
run: build
	@echo ""
	@echo "---------------------------------------------------------"
	@echo "You are about to be moved to the root directory of docker"
	@echo "---------------------------------------------------------"
	@echo ""
	@docker --version >/dev/null
	"${DOCKER}" run "${LIMITS}" --network host -it --rm ${TMP_IMAGE_NAME} bash

.PHONY: run deps all build deps-finished
