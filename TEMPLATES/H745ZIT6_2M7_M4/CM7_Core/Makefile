# Author: Rafael Garibotti

##### Project setup #####
# Name of your current project
PROJ_NAME = $(shell basename $(CURDIR))

LINKER_SCRIPT = ../STM32H745ZITx_FLASH_CM7.ld

# Directory containing CMSIS and HAL_Driver source code
CMSIS_DIR = ../Drivers/CMSIS
DRIVER_DIR = ../Drivers/STM32H7xx_HAL_Driver

##### Arm Toolchain #####
TRIPLE  = arm-none-eabi
CC      = ${TRIPLE}-gcc
LD      = ${TRIPLE}-ld
AS      = ${TRIPLE}-as
GDB 	= ${TRIPLE}-gdb
OBJCOPY = ${TRIPLE}-objcopy
OBJDUMP = ${TRIPLE}-objdump

##### Compiler options #####
CFLAGS = -g3 -std=gnu11 -Wall -T$(LINKER_SCRIPT)
CFLAGS += -DDEBUG -DCORE_CM7 -DUSE_HAL_DRIVER -DUSE_FULL_LL_DRIVER -DSTM32H745xx
CFLAGS += -ffunction-sections -fdata-sections #-fstack-usage
CFLAGS += -mthumb -mcpu=cortex-m7 -O0 -MMD -MP
CFLAGS += -mfloat-abi=hard -mfpu=fpv5-d16 --specs=nosys.specs --specs=nano.specs

##### Project specific libraries #####
SRC_FILES += $(wildcard Startup/*.s)
SRC_FILES += $(wildcard Src/*.c)
CFLAGS += -IInc

##### CMSIS libraries and source code #####
#SRC_FILES += $(CMSIS_DIR)/src/*
CFLAGS += -I$(CMSIS_DIR)/Include
CFLAGS += -I$(CMSIS_DIR)/Device/ST/STM32H7xx/Include

SRC_FILES += $(DRIVER_DIR)/Src/*
CFLAGS += -I$(DRIVER_DIR)/Inc

all: elf

##### Flash code to board #####
flash: hex
	STM32_Programmer_CLI -c port=SWD -w $(shell pwd)/$(PROJ_NAME).hex -v -ob displ -rst

##### Serial communication program #####
minicom:
	sudo minicom -D /dev/ttyACM0 -b 115200

##### Debug: GDB commands #####
gdb-server:
	ST-LINK_gdbserver

gdb-client:
	$(GDB) $(PROJ_NAME).elf -ex "target extended-remote localhost:61234" -ex "load" 

gdb:
	$(GDB) $(PROJ_NAME).elf -ex "target extended-remote localhost:61234" -ex "load" -ex "break main" -ex "continue"

# Print out disassembly of specified function using GDB (Example: make disass FUNC=main)
disass:
	$(GDB) $(PROJ_NAME).elf -batch -ex 'disass /r $(FUNC)'

##### General commands #####
clean:
	rm -f $(PROJ_NAME).bin $(PROJ_NAME).hex $(PROJ_NAME).elf $(PROJ_NAME).d $(PROJ_NAME).s *.su

disass-all:
	$(OBJDUMP) -D $(PROJ_NAME).elf > $(PROJ_NAME).s

elf:	$(SRC_FILES)
	$(CC) $(CFLAGS) -o $(PROJ_NAME).elf $^

hex:	
	$(OBJCOPY) -O ihex $(PROJ_NAME).elf $(PROJ_NAME).hex

bin:	
	$(OBJCOPY) -O binary $(PROJ_NAME).elf $(PROJ_NAME).bin

