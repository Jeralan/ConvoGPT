def readFile(filename):
    f = open(filename,"r")
    out = f.read()
    f.close()
    return out

def tokenCount(encoding,convo):
    return len(encoding.encode(convo))