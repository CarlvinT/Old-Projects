import sys
import pyLoop

def clear(fileName):

    with open(fileName, 'w') as theFile:

        theFile.write("0")

def addBiker(hasLight):

    if hasLight == 1:

        addLight('hasLight.csv')

    else:

        addLight('noLight.csv')

def displayFile(fileName):

    with open(fileName, 'r') as theFile:

        fileContent = theFile.read()

        print("test: {}".format(fileContent))
        return fileContent

def addLight(fileName):

    lightCount = displayFile(fileName)

    lc = int(lightCount)

    print(type(lc))

    clear(fileName)

    with open(fileName, 'w') as theFile:

        theFile.write("{}".format(lc+1))

    if lc > 8:
        print("Clearing file")
        pyLoop.sendToTTN()
        clear(fileName)
