# Skyline for BOTW
A patch for Breath of the Wild (Switch) that adds debug capability to the executable. 

**This project is being continued as https://github.com/iTNTPiston/botw-igd**

This project is based on:
 - [skyline-dev/skyline](https://github.com/skyline-dev/skyline) for hooking and patching
 - [zeldaret/botw](https://github.com/zeldaret/botw) for linking to botw

**This repository does not contain game assets or RomFS content and cannot be used to play Breath of the Wild.**

# Repo Commands

**IMPORTANT: To save yourself from pain, you should set up the project under a linux or WSL environment**

This project uses [just](https://github.com/casey/just) to run repo commands. Click on the link and follow their instructions to install.

If you don't want to install `just`, you can open `Justfile` and execute those commands yourself

|Command|Description|
|-|-|
|`just build`|Build the nso and ips patch|
|`just ips`|Only build the ips patch|
|`just ldscript`|Generate `syms150.ld`
|`just clean`|Cleans the nso and ips patch builds|
|`just cleanall`|In addition to `clean`, also removes the generated files|
|`just diffrom`|Compare 1.5.0 and 1.6.0 romfs and generates `v160_v150_change.txt`|
|`just minrom`|Extracts the romfs files listed in `v160_v150_change.txt`|
|`just ftp deploy`|Copies output files to console via ftp|
|`just ftp clean`|Removes output nso and ips patch from console|
|`just ftp report`|Downloads crash reports from console (also removes them from console)|

# Setup
## Prerequisite

You need the following files before continuing. These files are not provided by the project
- `primitive_drawer_nvn_shader.bin` from the romfs dump of another game. This file is removed from BOTW.
- The exefs dump of v1.5.0 of the game **(only if you have v1.6.0 installed)**
- The romfs dump of v1.5.0 of the game **(only if you have v1.6.0 installed)**

You don't need the second if you already have v1.5.0 installed.
## LayeredFS Setup

### Downgrading from v1.6.0
The patch only works with v1.5.0. If you have v1.6.0 installed, you need to setup LayeredFS to override the files with the 1.5.0 version.

If you already have v1.5.0 installed, skip to the next section

**You need to have the exefs and romfs dump of v1.5.0 to continue. The dumps are NOT provided here**

It's recommended to mount the SD card to your computer to transfer the romfs files. It will take a lot longer through network transfer
1. In the repo, create a new folder `romfs150` and copy these romfs subfolers to it
   - `Actor`
   - `Effect`
   - `Event`
   - `Pack`
   - `System`
2. Run `just minrom`. The romfs files needed for downgrading is saved under `romfsmin/`
3. Copy `romfsmin/` folder to `atmosphere/content/01007EF00011E000/` on SD card and rename it `romfs`. (Create the directory if it doesn't exist)
4. Copy the exefs dump to `atmosphere/content/01007EF00011E000/exefs` on SD card (Create the directory if it doesn't exist)
5. Launch the game and verify the version is 1.5.0 on title screen
6. If you want to launch into v1.6.0, hold `L` when booting the game to disable LayeredFS

### Add `primitive_drawer_nvn_shader.bin`
The primitive drawer needed to draw text onto the screen is not present in botw, so you need to manually add it. Skyline will crash if you don't have this file.

Copy the file to the folder `atmosphere/content/01007EF00011E000/romfs/System/Sead` on SD Card (Create the directory if it doesn't exist)

## Build
### Prerequisite
Make sure you have these things installed
 - [devkitPro](https://devkitpro.org/wiki/Getting_Started)
 - Python 3
 - keystone (Run `pip install keystone-engine`). This is needed to build the ips patch

### Generated Files
#### Linker Script
The linker script is used for linking with botw symbols. Run `just ldscript` to generate/regenerate it.

If the build doesn't re-link the nso, run `just relink`

### Building
Run `just` or `just build` to build the project. If you only want to build the ips patch, run `just ips`

### Install
#### FTP Install
There is a script to install the patch on your console via FTP.

If you don't have ftpd available on your console, skip to the next section
1. Generate the patched NPDM and build both nso and ips patch (see above)
2. Start ftpd on console
3. Run `just setip <console_ip>`. `<console_ip>` should be the ip address you see on ftpd. (No need to rerun this unless ip changes)
4. Run `just ftp deploy` to copy over the files 

If you want to remove the installation, run `just ftp clean`

#### Manual Install

To install manually, copy the following files from the build directory (e.g. `build150`) to your console.

1. Copy `skyline.nso` to `/atmosphere/contents/01007EF00011E000/exefs` and rename it `subsdk9`
2. Copy `skyline.npdm` to `/atmosphere/contents/01007EF00011E000/exefs` and rename it `main.npdm`
3. Copy `16A91992BBA71201E98756F3BC8F5D2F.ips` to `/atmosphere/exefs_patches/skylinebotw`


# Link with botw
Follow these steps to link to a botw symbol
1. Find the symbol. Check if it is listed in `botw/data/data_symbols.csv`. If the symbol is listed, skip to step 7
2. If the symbol is not listed. Use the symbol in the code. An easy way to do this is print it in `ksys::skyline::RenderDebugScreen`
3. `just build`
4. Load `skyline.elf` in IDA or a dissassembler to find the mangled name for the symbol. For example, `_ZN4sead7HeapMgr10sRootHeapsE`. Look at where you used the symbol in code
5. Find the address of the symbol to link to and list it in `data_symbols.csv` (PR to `botw` later)
6. `just ldscript`
7. Find the symbol in `KingSymbols150.hpp`. You can use `just findsym <symbol>`
8. Add the link definition in one of the `.links` file in `linkerscripts`. 
9. `just ldscript relink`
10. Load `skyline.elf` again to make sure it's linked correctly.
