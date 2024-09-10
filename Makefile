CONTAINER_NAME := $(notdir $(CURDIR))
PORT := 8001
VOLUME_NAME = $(CONTAINER_NAME)-volume

build:
	docker build $(ARGS) --build-arg PORT=$(PORT) -t $(CONTAINER_NAME) .
run:
	docker run -d -p $(PORT):$(PORT) -v $(VOLUME_NAME):/deploy/storage $(CONTAINER_NAME)

# TODO don't hardcode storage dir
enter:
	docker run -v $(VOLUME_NAME):/deploy/storage -it $(CONTAINER_NAME) bash
kill:
	docker kill `docker ps -q --filter "ancestor=$(CONTAINER_NAME)"`
	sleep 1 # may get "port already allocated" error without this
	$(MAKE) build
	$(MAKE) run
