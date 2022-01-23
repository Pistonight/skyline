# Version (1.5.0)
VERSION := "150"
IP_FILE := "consoleip.txt"

default: build

# Wrapper for scripts/genHeader.py and scripts/genLinkerScript.py 
ldscript:
    python3 scripts/genHeader.py    
    python3 scripts/genLinkerScript.py

# Wrapper for scripts/patchNpdm.py
npdm:
    python3 scripts/patchNpdm.py main.npdm skyline{{VERSION}}.npdm

build:
    just nso
    just ips

rebuild: clean build

relink:
    rm -f skyline{{VERSION}}.nso
    rm -f skyline{{VERSION}}.elf
    just nso

nso:
    make skyline

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
    rm -f *.ips

# Clean the build output and all generated files
cleanall: clean
    rm -f include/KingSymbols{{VERSION}}.hpp
    rm -f linkerscripts/syms{{VERSION}}.ld
    rm -f skyline{{VERSION}}.npdm
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
    grep "{{SYMBOL}}" build{{VERSION}}/skyline{{VERSION}}.lst
    grep "{{SYMBOL}}" build{{VERSION}}/skyline{{VERSION}}.map
