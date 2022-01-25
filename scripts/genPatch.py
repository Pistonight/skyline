import os, sys, re, ctypes, struct
from keystone import *

class Patch:
    def __init__(self, offset, length, content):
        self.offset = offset
        self.length = length
        self.content = content

# consts
PATCH_DIR = "patches"
PATCH_EXTENSION = ".slpatch"

NSO_HEADER_LEN = 0x100
PATCH_CONFIG_DIR = PATCH_DIR
PATCH_CONFIG_EXTENSION = ".config"

IPS_FORMAT = ".ips"
IPS_HEADER_MAGIC = bytes("IPS32", 'ASCII')
IPS_EOF_MAGIC = bytes("EEOF", 'ASCII')

def initConfig(configPath):
    configObject = {}
    # read config file
    with open(configPath) as configFile:
        curConfigName = None
        for line in configFile:
            line = line.strip()
            configNameLineMatch = re.match(r'\[(.+)\]', line)
            if configNameLineMatch:
                curConfigName = configNameLineMatch.group(1)
                configObject[curConfigName] = {}
                continue

            if '=' in line:
                configKey, configValue = line.split('=', 1)
                if not configKey.isalnum():
                    continue
                if '+' in configValue:
                    print("genPatch.py error:", line, "awaits implementation")
                    sys.exit(-1)
                configObject[curConfigName][configKey] = configValue
    
    return configObject

# returns symbol at it's loaded addr relative to main
def getSkylineSymAddr(target, regexStr, symStr):
    mapFile = None
    def getFoundPosAddr(start):
        regexMatch = re.search(regexStr, mapFile[start:])
        if not regexMatch:
            return -1, -1

        foundLinePos = mapFile.rfind('\n', 0, regexMatch.span()[0] + start) + 1
        foundLineEndPos = mapFile.find('\n', regexMatch.span()[1] + start)
        foundLine = mapFile[foundLinePos:foundLineEndPos].strip()
        foundAddr = int(foundLine[:foundLine.find(" ")].replace("00000000:00000071", ''), 16)
        return foundLineEndPos, foundAddr

    mapFile = SLMapFile
    loadAddrAdjustment = int(patchConfig["nso_load_addr"]["skyline"], 16)

    foundPos, firstFoundAddr = getFoundPosAddr(0)
    
    if foundPos == -1:
        raise NameError

    # check uniqueness
    while True:
        foundPos, moreFoundAddr = getFoundPosAddr(foundPos)
        if foundPos == -1:
            break

        if moreFoundAddr != firstFoundAddr:
            print("genPatch.py error:", symStr, "is ambiguous!")
            sys.exit(-1)

    # map stores signed address relative to skline as unsigned?
    return loadAddrAdjustment + ctypes.c_long(firstFoundAddr).value

def resolveAddressAndTarget(target, symbolStr):
    resolvedAddr = 0

    # resolve + offset
    plusSplit = symbolStr.split('+', 1)
    if len(plusSplit) > 1:
        symbolStr = plusSplit[0]
        resolvedAddr += int(plusSplit[1], 16)

    # if symbol is in skyline
    funcStr = symbolStr + r'\('
    try:
        addrInSkyline = getSkylineSymAddr("skyline", funcStr, symbolStr)
        # if no exception, then symbolStr is found is skyline
        print("Resolved Skyline Symbol", symbolStr, "=", addrInSkyline)
        resolvedAddr += addrInSkyline
        return target, resolvedAddr
    except NameError:
        pass

    # BOTW: symbolStr has to be an address for simplicify
    if not symbolStr.startswith("0x"):
        print("Undefined symbol:", symbolStr)
        sys.exit(-1)

    try:
        resolvedAddr += int(symbolStr, 16)
        resolvedAddr += int(patchConfig["nso_load_addr"][target], 16)
        return target, resolvedAddr
    except ValueError:
        pass

    # BOTW: no search symbol in map

    return target, resolvedAddr

def getPatchBin(target, patchAddress, patchValueStr):
    # bytes patch
    try:
        patchBin = bytearray.fromhex(patchValueStr)
        return patchBin
    except ValueError:
        pass
    # string patch
    stringMatch = re.search(r'"(.+)"', patchValueStr)
    if stringMatch:
        return bytearray(bytes(stringMatch.group(1), 'utf-8').decode('unicode_escape') + '\0', 'utf-8')

    # asm patch
    branchNeedResolveMatch = re.match(r'([Bb][Ll]?\s+)([^\#]+$)', patchValueStr)
    if branchNeedResolveMatch:
        target, toAddr = resolveAddressAndTarget(target, branchNeedResolveMatch.group(2))
        patchValueStr = (branchNeedResolveMatch.group(1) + '#' + hex(toAddr - patchAddress))

    ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
    encodedBytes, insCount = ks.asm(patchValueStr)
    return bytearray(encodedBytes)

def addPatchToPatchlist(target, patchAddress, patchContent):
    if target not in patchList:
        patchList[target] = []
    patchList[target].append(Patch(
        patchAddress - int(patchConfig["nso_load_addr"][target], 16) + NSO_HEADER_LEN, 
        len(patchContent), patchContent ))

def addPatchFromFile(patchFilePath):
    PATCH_VERSION_ALL = "all"
    patchVars = {
        "version" : None,
        "target" : "main"
    }

    with open(patchFilePath) as patchFile:
        fileLinesIter = iter(patchFile)
        isInMultiPatch = False
        while True:
            # read next line
            if isInMultiPatch:
                # multiPatch check already read new line; simply false the flag
                isInMultiPatch = False
            else:
                try:
                    line = next(fileLinesIter)
                except StopIteration:
                    break

            # Strip off comments
            line = line.split(';', 1)[0].strip()
            # Skip empty lines
            if len(line) == 0:
                continue

            # if is patch variable line, e.g. [version=310]
            patchVarLineMatch = re.match(r'\[(.+)\]', line)
            if patchVarLineMatch:
                patchVarMatches = re.findall(r'(\w+)=(\w+)', patchVarLineMatch.group(1))
                for match in patchVarMatches:
                    patchVars[match[0]] = match[1]
                continue

            # skip all lines not for our version
            if patchVars["version"] != buildVersion and patchVars["version"] != PATCH_VERSION_ALL:
                continue

            # parse patches
            addressSplit = line.split(' ', 1)
            isInMultiPatch = addressSplit[0].endswith(':')
            if len(addressSplit) < 2 and not isInMultiPatch:
                continue
            
            patchTarget, patchAddress = resolveAddressAndTarget(patchVars["target"],
                addressSplit[0] if not isInMultiPatch else addressSplit[0][:-1])
            patchContent = bytearray()

            if isInMultiPatch:
                try:
                    line = next(fileLinesIter).split('/', 1)[0]
                    ident = re.search(r'\s+', line).group()
                    while True:
                        patchContent += getPatchBin(patchTarget, patchAddress + len(patchContent), line.strip())
                        line = next(fileLinesIter).split('/', 1)[0]
                        if not line.startswith(ident):
                            break
                except StopIteration:
                    addPatchToPatchlist(patchTarget, patchAddress, patchContent)
                    break
            else:
                patchContent = getPatchBin(patchTarget, patchAddress, addressSplit[1])

            addPatchToPatchlist(patchTarget, patchAddress, patchContent)

if len(sys.argv) < 2:
    print('Usage: ' + sys.argv[0] + ' [version]')
    sys.exit(-1)

buildVersion = sys.argv[1]
configPath = os.path.join(PATCH_DIR, buildVersion + PATCH_CONFIG_EXTENSION)
patchConfig = initConfig(configPath)
patchList = {}

SLMapFilePath = os.path.join("build" + buildVersion, os.path.basename(os.getcwd()) + ".map")
with open(SLMapFilePath, 'r') as f:
    SLMapFile = f.read()

for file in os.listdir(PATCH_DIR):
    if file.endswith(PATCH_EXTENSION):
        addPatchFromFile(os.path.join(PATCH_DIR, file))

for nso in patchList:
    ipsOutPath =os.path.join("build" + buildVersion, patchConfig["build_id"][nso] + IPS_FORMAT)
    with open(ipsOutPath, 'wb') as ipsFile:
        ipsFile.write(IPS_HEADER_MAGIC)
        for patch in patchList[nso]:
            ipsFile.write(struct.pack('>I', patch.offset))
            ipsFile.write(struct.pack('>H', patch.length))
            ipsFile.write(patch.content)
        ipsFile.write(IPS_EOF_MAGIC)
    print("Generated", nso, "->", ipsOutPath, "OK")
