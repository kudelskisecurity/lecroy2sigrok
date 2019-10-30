#!/usr/bin/env python3
""" lecroy2sigrok.py

lecroy2sigrok is derived from leCroyParser.py
which is available at https://github.com/bennomeier/lecroyparser

"""

import sys
import numpy as np

posWAVEDESC = 0

def parseFile(path):
	global posWAVEDESC
	endianness = "<"

	f = open(path, mode='rb')
	fileContent = f.read()

	#Find position of substring WAVEDESC
	try:
		posWAVEDESC = fileContent.index(b"WAVEDESC")
	except ValueError:
			sys.exit("Error wrong file format")

	commOrder = parseInt16(f, 34, endianness) #big endian (>) if 0, else little
	if commOrder > 1:
		sys.exit("Error wrong file format")

	endianness = [">", "<"][commOrder]
	commType = parseInt16(f, 32, endianness) # encodes whether data is stored as 8 or 16bit
	
	if commType == 1:
		dataFormat = "S16_LE"
	elif commType == 0:
		dataFormat = "S8"
	else:
		sys.exit("Error wrong file format")

	waveDescriptor = parseInt32(f, 36, endianness)
	userText = parseInt32(f, 40, endianness)
	trigTimeArray = parseInt32(f, 48, endianness)
	waveArray1 = parseInt32(f, 60, endianness)
	horizInterval = int(1 / parseFloat(f, 176, endianness))

	f.seek(posWAVEDESC + waveDescriptor + userText
		   + trigTimeArray)

	data = f.read(waveArray1)
	f.close()

	return data, dataFormat, horizInterval
        
def unpack(f, pos, formatSpecifier, length, endianness):
	""" a wrapper that reads binary data
	in a given position in the file, with correct endianness, and returns the parsed
	data as a tuple, according to the format specifier. """
	f.seek(pos + posWAVEDESC)
	x = np.fromstring(f.read(length), endianness + formatSpecifier)[0]
	return x

def parseInt16(f, pos, endianness):
    return unpack(f, pos, "u2", 2, endianness)

def parseInt32(f, pos, endianness):
    return unpack(f, pos, "i4", 4, endianness)

def parseFloat(f, pos, endianness):
    return unpack(f, pos, "f4", 4, endianness)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage : " + sys.argv[0] + " trace.trc")
		sys.exit()
	path = sys.argv[1]
	data, dataFormat, horizInterval = parseFile(path)
	print("Data format: " + dataFormat)
	print("Sample rate (Hz): " + str(horizInterval) + "\n")

	f = open(path[:-4] + ".bin", "wb")
	f.write(data)
	f.close()
	print("Raw analog data written in " + path[:-4] + ".bin")

