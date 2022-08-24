import subprocess
import time
import os
import signal
import re
import random
import serial
import struct
import sys

from datetime import datetime

timestamp = str(datetime.now())

reg_val_regex = re.compile(r'0x(.*)')

def sendCommand(input_stream, command):
	print(command.decode("utf-8"))
	input_stream.write(command)
	input_stream.flush()

def readRegAll(process):
	sendCommand(process.stdin, ("info all-registers\n").encode("utf-8"))
	reg_all = process.stdout.readline().decode("utf-8")
	return reg_all

def readMemValue(process, mem):
	sendCommand(process.stdin, ("x/x " + mem + "\n").encode("utf-8"))
	raw_val = process.stdout.readline().decode("utf-8")
	hex_val = reg_val_regex.findall(raw_val)[0]

	bin_str = bin(int(hex_val[-8:], 16))[2:].zfill(32)
	return bin_str

def writeMemValue(process, mem, val, base=2):
	int_val = int(val, base)
	sendCommand(process.stdin, ("set {int}" + str(mem) + " = " + str(int_val) + "\n").encode("utf-8"))

def readRegValue(process, reg):
	sendCommand(process.stdin, ("p/x " + reg + "\n").encode("utf-8"))
	raw_val = process.stdout.readline().decode("utf-8")
	hex_val = reg_val_regex.findall(raw_val)[0]

	bin_str = bin(int(hex_val, 16))[2:].zfill(32)
	return bin_str

	# print (reg + " = " + str(len(bin_str)))
	# print (reg + " = " + (bin_str))
	# print (reg + " = " + (hex_val))

def writeRegValue(process, reg, val, base=2):
	int_val = int(val, base)
	sendCommand(process.stdin, ("set " + str(reg) + " = " + str(int_val) + "\n").encode("utf-8"))

	# waitTillPrompt(process)
	# print(("p/x " + reg + "\n").encode("utf-8"))
	# process.stdin.write(("p/x " + reg + "\n").encode("utf-8"))
	# print("-->" + process.stdout.readline().decode("utf-8"))
	# print("<-->" + process.stdout.readline().decode("utf-8"))

def waitTillPrompt(process):
	currentLine = ""
	while(True):
		readChar = process.stdout.read(1).decode("utf-8")
		# print(readChar)
		currentLine += str(readChar)
		if(readChar == '\n'):
			print(currentLine, end='')
			currentLine = ""
		elif "(gdb) " in currentLine:
			print(currentLine, end='')
			break


regs = ["$r0","$r1","$r2","$r3","$r4","$r5","$r6","$r7","$r8","$r9","$r10","$r11","$r12","$sp","$lr","$pc","$xpsr","$fpscr","$PRIMASK","$BASEPRI","$FAULTMASK","$CONTROL","$MSP","$PSP"]

pathToProcess = "arm-none-eabi-gdb"
process = subprocess.Popen([pathToProcess, "../Core/Core.elf"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# print(process.pid)

waitTillPrompt(process)

sendCommand(process.stdin, b'target extended-remote localhost:61234\n')

waitTillPrompt(process)

sendCommand(process.stdin, b'load\n')

waitTillPrompt(process)

sendCommand(process.stdin, b'break main\n')

time.sleep(1)

waitTillPrompt(process)

sendCommand(process.stdin, b'continue\n')

#############################################
# Read memory
mem_to_inject = "0x2000fff6"
waitTillPrompt(process)
val = readMemValue(process, mem_to_inject)
print(mem_to_inject, ":", val)

#############################################
# Inject a fault in the memory
waitTillPrompt(process)

val = list(val)
val[31] = '0' if val[31] == '1' else '1'
val = "".join(list(val))

writeMemValue(process, mem_to_inject, val)

#############################################
# Read memory
waitTillPrompt(process)
val = readMemValue(process, mem_to_inject)
print(mem_to_inject, ":", val)

#############################################
# Read all registers
waitTillPrompt(process)
val = readRegAll(process)
print(val)

#############################################
# Read registers
for i in range(len(regs)):
	register_to_inject = regs[i]
	waitTillPrompt(process)
	val = readRegValue(process, register_to_inject)
	print(register_to_inject, ":", val)

#############################################
# Switch to another part of the code 
for i in range(5):
	sendCommand(process.stdin, b'next\n')
	waitTillPrompt(process)

#############################################
# Inject a fault in the register
time.sleep(2)
#process.send_signal(signal.SIGINT)

register_to_inject = regs[5]
waitTillPrompt(process)

val = readRegValue(process, register_to_inject)
print("[FI]",register_to_inject, ":", val)
waitTillPrompt(process)

val = list(val)
bit_to_change = random.randint(0, 31)
val[bit_to_change] = '0' if val[bit_to_change] == 1 else '1'
val = "".join(list(val))

writeRegValue(process, register_to_inject, val)
print("[FI]",register_to_inject, ":", val)

#waitTillPrompt(process)
#sendCommand(process.stdin, b'continue\n')

#############################################
# Switch to another part of the code 
for i in range(2):
	sendCommand(process.stdin, b'next\n')
	waitTillPrompt(process)

#############################################
# Read registers
for i in range(len(regs)):
	register_to_inject = regs[i]
	waitTillPrompt(process)
	val = readRegValue(process, register_to_inject)
	print(register_to_inject, ":", val)

sendCommand(process.stdin, b'continue\n')

while(True):
	pass
	print(str(process.stdout.read(1)), end="")
 
