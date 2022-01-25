# Generates linker scripts from hints. Hints are used to define a symbol/address in uking to link to
# Hints must be defined as 
#      Links <address|symbol> <mangledName> (<comment>)
# Only lines with only comments are searched
# Included paths (file or directory) need to be added below
import os, csv, sys
from common import mangleDataName, mangleFunctionName

# consts
CUSTOM_HEADER = """
/*
 *  This is a generated file
 *  DO NOT EDIT THIS FILE DIRECTLY
 *  Generate with genLinkerScript.py instead
 */

"""
# The paths to search for LinkerHints
INCLUDE = ["include", "linkerscripts"]
# The extensions of files
EXTENSIONS = [".h", ".hpp", ".links"]
# Search strings
DISABLED = "Disabled"
LINKER_HINTS = "Links"
# Offset for symbols in main (beginning of skyline - beginning of main)
MAIN_OFFSET = "0x2d91000"
# Namespace for the generated header
HPP_NAMESPACE = "KingSymbols150"
# Prefix function name
FUNC_PREFIX = "f_"
# Prefix Data symbols
DATA_PREFIX = "d_"

FUNC_ALIAS = f"{HPP_NAMESPACE}::{FUNC_PREFIX}"
DATA_ALIAS = f"{HPP_NAMESPACE}::{DATA_PREFIX}"

LD_OUTPUT = "linkerscripts/syms150.ld"

def createLinkerScriptLine(addrStr, mangledName, comment):
    commentStr = ""
    if comment != None:
        commentStr = f"/* {comment} */"

    return f"{mangledName} = {addrStr} - {MAIN_OFFSET}; {commentStr}\n"

# If line is just comment, return comment, otherwise return None
def parseLine(rawLine):
    if rawLine.startswith("//"):
        return rawLine[2:].strip()
    elif rawLine.startswith("/*") and rawLine.endswith("*/"):
        return rawLine[2:len(rawLine)-2].strip()
    else:
        return None

def extractComments(line):
    parenStart = line.find("(")
    parenEnd = line.find(")")
    comment = None
    if parenEnd > parenStart and parenEnd != -1:
        comment = line[parenStart+1:parenEnd]
        line = line[:parenStart]
    
    return line, comment

def scanFileForLinkerHints(ldAddrData, ldSymbData, pathStr, headerFile):
    headerLines = headerFile.readlines()
    savedLines = ""
    for line in headerLines:
        lineStripped = line.strip()
        # Process multi line
        if lineStripped.endswith("\\"):
            savedLines += lineStripped[:-1]
            continue

        lineStripped = savedLines + lineStripped
        savedLines = ""
        lineContent = parseLine(lineStripped) # Part of the line without comment symbols
        if lineContent == None:
            continue
        
        lineContent, comment = extractComments(lineContent)

        parts = lineContent.split()
        if len(parts) >= 3 and parts[0] == LINKER_HINTS:
            addrStr = parts[1]
            mangledName = parts[2]
            # addrStr can be another symbol
            if not addrStr.startswith("0x"):
                # Add to symbdata to resolve later
                ldSymbData.append((addrStr, mangledName, comment, pathStr))
            else:
                ldAddrData[addrStr] = (mangledName, comment)

def scanPathForLinkerHints(ldAddrData, ldSymbData, pathStr):
    if os.path.isfile(pathStr):
        if os.path.splitext(pathStr)[1] in EXTENSIONS:
            with open(pathStr) as headerFile:
                scanFileForLinkerHints(ldAddrData, ldSymbData, pathStr, headerFile)
    elif os.path.isdir(pathStr):
        print("Scanning", pathStr)
        dirContent = os.listdir(pathStr)
        for subPathName in dirContent:
            scanPathForLinkerHints(ldAddrData, ldSymbData, os.path.join(pathStr, subPathName))



ldLines = []
ldAddrData = {}
ldSymbData = []

for pathStr in INCLUDE:
    scanPathForLinkerHints(ldAddrData, ldSymbData, pathStr)

print("Resolving...")
ldSymbolToAddress = {}
addrCount = 0
for addrStr in ldAddrData:
    mangledName, comment = ldAddrData[addrStr]
    line = createLinkerScriptLine(addrStr, mangledName, comment)
    ldSymbolToAddress[mangledName] = addrStr
    ldLines.append(line)
    addrCount+=1
print("Resolved", addrCount, "links to address")

symbCount = 0
funcCount = 0
dataCount = 0
for symbStr, mangledName, comment, pathStr in ldSymbData:
    mangledSymbol = ""
    if symbStr.startswith(FUNC_ALIAS):
        funcName = symbStr[len(FUNC_ALIAS)-len(FUNC_PREFIX):]
        mangledSymbol = mangleFunctionName(funcName)
        funcCount+=1
    elif symbStr.startswith(DATA_ALIAS):
        dataName = symbStr[len(DATA_ALIAS)-len(DATA_PREFIX):]
        mangledSymbol = mangleDataName(dataName)
        dataCount+=1
    else:
        mangledSymbol = symbStr
        symbCount+=1

    if mangledSymbol not in ldSymbolToAddress:
        print("Error: Fail to resolve", symbStr, "from", pathStr)
        sys.exit(-1)
    resolvedAddrStr = ldSymbolToAddress[mangledSymbol]
    line = createLinkerScriptLine(resolvedAddrStr, mangledName, comment)
    ldLines.append(line)

print("Resolved", symbCount, "links to symbols")
print("Resolved", funcCount, "links to uking functions")
print("Resolved", dataCount, "links to uking data")

# Write ld
print("Writing", LD_OUTPUT)
with open(LD_OUTPUT, "w+") as ldFile:
    ldFile.write(f"/* {LD_OUTPUT} */\n")
    ldFile.write(CUSTOM_HEADER)

    ldFile.write(f"blank = 0;\n")
    ldFile.writelines(ldLines)

print("Written",len(ldLines),"symbol mapping")