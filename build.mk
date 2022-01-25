# Makefile 
# This is for building .nso and .npdm
# The content in build directory are managed by this make file
# The other wrapper scripts are contained in Justfile

ifeq ($(strip $(DEVKITPRO)),)
$(error "Please set DEVKITPRO in your environment. export DEVKITPRO=<path to>/devkitpro")
endif

include $(DEVKITPRO)/libnx/switch_rules

#---------------------------------------------------------------------------------
# Variables

# Target name
TARGET          := $(BASENAME)

# DIRECTORIES
# Build Output (This mk file operates inside the build folder)
BUILD_DIR 		:= .
# Root Directory
ROOT_DIR        := ..
# Linker Script (i.e .ld)
LDSCRIPT_DIR    := $(ROOT_DIR)/linkerscripts
# Headers 
INCLUDE_DIR     := $(ROOT_DIR)/include
# Dependencies
LIB_DIR         := $(ROOT_DIR)/libs
# Sources (i.e .c, .cpp)
SOURCE_DIR      := $(ROOT_DIR)/source

# Scan for nested source directories
ALL_SOURCES_DIRS	:= 	$(shell find $(SOURCE_DIR) -type d)
# Library paths
LIBDIRS :=  $(PORTLIBS) $(LIBNX)
# Include paths
ALL_INCLUDE_DIRS	:=	\
$(INCLUDE_DIR) \
../libs/libeiffel/include \
../libs/sead/include  \
../libs/agl/include  \
../libs/NintendoSDK/include \
../libs/botw/src \
# VPATH for make to search for files
VPATH	:=	$(foreach dir,$(ALL_SOURCES_DIRS),$(CURDIR)/$(dir))

# INPUT FILES
# Linker script for uking symbols
LDSCRIPT    := $(LDSCRIPT_DIR)/syms$(VERSION).ld
# Linker version script
LINKER_VERSION_SCRIPT := $(LDSCRIPT_DIR)/exported.txt
# Source files 
CFILES		:=	$(foreach dir,$(ALL_SOURCES_DIRS),$(notdir $(wildcard $(dir)/*.c)))
CPPFILES	:=	$(foreach dir,$(ALL_SOURCES_DIRS),$(notdir $(wildcard $(dir)/*.cpp)))
SFILES		:=	$(foreach dir,$(ALL_SOURCES_DIRS),$(notdir $(wildcard $(dir)/*.s)))

# OUTPUT FILES
# .specs file for linking
SWITCH_SPECS := $(TARGET).specs
# .o files
OFILES	 :=	$(CPPFILES:.cpp=.o) $(CFILES:.c=.o) $(SFILES:.s=.o)
# .d files 
DFILES	 :=	$(OFILES:.o=.d)
# Application json for generating npdm
APP_JSON := ../app.json

# CODE GEN OPTIONS
# Use CXX for linking
LD	    := $(CXX)
# Include path
INCLUDE	:=	\
$(foreach dir,$(ALL_INCLUDE_DIRS),-I$(CURDIR)/$(dir)) \
$(foreach dir,$(LIBDIRS),-I$(dir)/include)
# Defines
DEFINES := -D__SWITCH__ -DSWITCH -DNNSDK -DSKYLINE_DEBUG_BUILD="\"$(SKYLINE_DEBUG_BUILD)\""
# Architecture
ARCH	:= -march=armv8-a -mtune=cortex-a57 -mtp=soft -fPIC -ftls-model=local-exec
# C flags
CFLAGS	:= -g -Wall -ffunction-sections -O3 $(ARCH) $(DEFINES) $(INCLUDE) 
ifneq ($(strip $(NOLOG)),)
CFLAGS	+= "-DNOLOG"
endif
# CXX flags
CXXFLAGS	:= $(CFLAGS) -fno-rtti -fomit-frame-pointer -fno-exceptions -fno-asynchronous-unwind-tables -fno-unwind-tables -enable-libstdcxx-allocator=new -fpermissive -std=c++17 
# AS flags
ASFLAGS	    := -g $(ARCH)
# LD flags
LDFLAGS     := -specs=$(SWITCH_SPECS) -g $(ARCH) -Wl,-Map,$(TARGET).map -Wl,--version-script=$(LINKER_VERSION_SCRIPT) -Wl,-init=__custom_init -Wl,-fini=__custom_fini -Wl,--export-dynamic -nodefaultlibs
# LD libs
LIBS	    := -lgcc -lstdc++ -u malloc
# LD lib paths
LIBPATHS	:= $(foreach dir,$(LIBDIRS),-L$(dir)/lib)
# DEPSDIR used by DEVKITPRO for exporting .d files
DEPSDIR	    ?= .

#---------------------------------------------------------------------------------
# Make Targets
.PHONY:	all
all: $(TARGET).nso $(TARGET).npdm 

# spec file for linking. This is generated so we can pass in linkerscript to LD
$(SWITCH_SPECS):
	@echo "Creating $(SWITCH_SPECS)"
	@echo "%rename link old_link" > $(SWITCH_SPECS)
	@echo "" >> $(SWITCH_SPECS)
	@echo "*link:" >> $(SWITCH_SPECS)
	@echo "%(old_link) -T $(LDSCRIPT_DIR)/application.ld $(LDSCRIPT) --shared --gc-sections --build-id=sha1" >> $(SWITCH_SPECS)
	@echo "" >> $(SWITCH_SPECS)
	@echo "*startfile:" >> $(SWITCH_SPECS)
	@echo "crti%O%s crtbegin%O%s" >> $(SWITCH_SPECS)

# Make target ELF depend on all .o files
$(TARGET).elf   : $(OFILES) $(SWITCH_SPECS)

# Not sure why the default npdm rule fails. Redefining the rule here.
# The tool prints error message for missing fields in json. They are not important so we ignore the errors
$(TARGET).npdm: $(APP_JSON)
	npdmtool $(APP_JSON) $@ 2> /dev/null
# The rest of the build rules are specified by the devkitpro makefile

# Include the .d files generated
-include $(DFILES)
