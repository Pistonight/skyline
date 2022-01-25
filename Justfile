
IP_FILE   := "consoleip.txt"
# Export these to make them available for make
# Version. 150 means v1.5.0. This is here in case we want to support botw v1.6.0 later
export VERSION   := "150"
export BUILD_DIR := "build" + VERSION
export BASENAME  := "skyline"

default: build

# Wrapper for scripts/genBotwSymbols.py and scripts/genLinkerScript.py 
ldscript:
    python3 scripts/genBotwSymbols.py    
    python3 scripts/genLinkerScript.py

build:
    make build
    just ips

rebuild: clean build

relink:
    rm -f {{BUILD_DIR}}/{{BASENAME}}*
    just build

# Wrapper for scripts/genPatch.py
ips:
    python3 scripts/genPatch.py {{VERSION}}

# Wrapper for scripts/diffRomFs.py
diffrom:
    python3 scripts/diffRomFs.py romfs150 romfs160 v160_v150_change.txt

# Wrapper for scripts/minRomFs.py
minrom:
    rm -rf romfsmin/
    python3 scripts/minRomfs.py romfs150 v160_v150_change.txt romfsmin

# Cleans the elf and ips
clean:
    make clean

# Clean the build output and all generated files
cleanall: clean
    rm -f include/KingSymbols{{VERSION}}.hpp
    rm -f linkerscripts/syms{{VERSION}}.ld
    rm -f {{IP_FILE}}
    rm -rf romfsmin/
    rm -rf crash_reports/

setip IP:
    echo {{IP}} > {{IP_FILE}}

# Wrapper for scripts/ftpUtil.py
# FTP_OPTION can be:
# deploy: copy npdm, nso and ips patch to console
# clean: remove nso and ips patch from console (not npdm)
# report: get crash reports from console (also deletes them from console)
ftp FTP_OPTION:
    @if [ ! -f {{IP_FILE}} ]; then echo "Error: Please set your console IP with\n     just setip <IP>"; exit; else python3 scripts/ftpUtil.py {{FTP_OPTION}} {{VERSION}} $(cat {{IP_FILE}}); fi 

findsym SYMBOL:
    -grep -i "{{SYMBOL}}" {{BUILD_DIR}}/{{BASENAME}}.lst
    -grep -i "{{SYMBOL}}" {{BUILD_DIR}}/{{BASENAME}}.map
    grep -i "{{SYMBOL}}" include/KingSymbols{{VERSION}}.hpp
