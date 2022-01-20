# TODO (Khangaroo): Make this process a lot less hacky (no, export did not work)
# See MakefileNSO

.PHONY: all clean skyline send

CROSSVER ?= 150

PYTHON := python3
ifeq (, $(shell which python3))
	# if no python3 alias, fall back to `python` and hope it's py3
	PYTHON   := python
endif

NAME 			:= $(shell basename $(CURDIR))
NAME_LOWER		:= $(shell echo $(NAME) | tr A-Z a-z)
PATCH_PREFIX	:= $(NAME_LOWER)_patch_
PATCH 			:= $(PATCH_PREFIX)$(CROSSVER)

PATCH_DIR 		:= patches
SCRIPTS_DIR		:= scripts
BUILD_DIR 		:= build$(CROSSVER)

CONFIGS 		:= $(PATCH_DIR)/configs
CROSS_CONFIG 	:= $(CONFIGS)/$(CROSSVER).config

MAPS 			:= $(PATCH_DIR)/maps
CROSS_MAPS 		:= $(MAPS)/$(CROSSVER)
NAME_MAP 		:= $(BUILD_DIR)/$(NAME)$(CROSSVER).map


MAKE_NSO		:= nso.mk

all: skyline

skyline:
	$(MAKE) all -f $(MAKE_NSO) MAKE_NSO=$(MAKE_NSO) CROSSVER=$(CROSSVER) BUILD=$(BUILD_DIR) TARGET=$(NAME)$(CROSSVER)

clean:
	$(MAKE) clean -f $(MAKE_NSO)
