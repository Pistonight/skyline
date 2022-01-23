# Namespace for the generated header
HPP_NAMESPACE = "KingSymbols150"

# Mangle for extern void cleanName()
def mangleFunctionName(cleanName):
    return "_ZN" + str(len(HPP_NAMESPACE)) + HPP_NAMESPACE + str(len(cleanName)) + cleanName + "Ev"

# Mangle for extern void* cleanName;
def mangleDataName(cleanName):
    return "_ZN" + str(len(HPP_NAMESPACE)) + HPP_NAMESPACE + str(len(cleanName)) + cleanName + "E"
