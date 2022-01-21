# Version (1.5.0)
VERSION := "150"
IP_FILE := "consoleip.txt"

# Wrapper for scripts/genHeader.py
header:
    python3 scripts/genHeader.py

# Wrapper for scripts/genLinkerScript.py 
ldscript:
    python3 scripts/genLinkerScript.py

# Wrapper for scripts/patchNpdm.py
npdm:
    python3 scripts/patchNpdm.py main.npdm skyline{{VERSION}}.npdm

build:
    just nso
    just ips

rebuild: clean build

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
    rm -f include/ukr{{VERSION}}.hpp
    rm -f linkerscripts/syms{{VERSION}}.ld
    rm -f skyline{{VERSION}}.npdm
    rm -f {{IP_FILE}}
    rm -rf romfsmin/

setip IP:
    echo {{IP}} > {{IP_FILE}}

# Wrapper for scripts/ftpAction.py deploy
deploy:
    @if [ ! -f {{IP_FILE}} ]; then echo "Error: Please set your console IP with\n     just setip <IP>"; exit; else python3 scripts/ftpAction.py deploy {{VERSION}} $(cat {{IP_FILE}}); fi 

# Remove deployment from switch
cleandeploy IP:
    @echo "Not Implemented!"

# Get crash report from switch
mvcrash IP:
    @echo "Not Implemented!"

