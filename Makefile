# Make Targets
.PHONY:	build clean
all: build

# Variables are exported by Just
build:
	@[ -d $(BUILD_DIR) ] || mkdir -p $(BUILD_DIR) 
	rm -f $(BUILD_DIR)/DebugVersion.o
	$(MAKE) -C $(BUILD_DIR) -f ../build.mk VERSION=$(VERSION) BASENAME=$(BASENAME) SKYLINE_DEBUG_BUILD=$$(date -u "+%D-%H%M%S")

clean:
	rm -rf $(BUILD_DIR)