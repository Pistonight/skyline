# Make Targets
.PHONY:	build clean
all: build

# Variables are exported by Just
build:
	@[ -d $(BUILD_DIR) ] || mkdir -p $(BUILD_DIR) 
	$(MAKE) -C $(BUILD_DIR) -f ../build.mk VERSION=$(VERSION) BASENAME=$(BASENAME)

clean:
	rm -rf $(BUILD_DIR)