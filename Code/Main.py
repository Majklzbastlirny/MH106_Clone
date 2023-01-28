#Code for emulating MH106 clock IC with micropython and RP2040
#Author: Michal Basler
#Date: 2023-01-28
#Version: 0.1
#License: GPL v3.0

#Description:
#This code is intended to emulate MH106 clock IC with micropython and RP2040. It can display time (HH:MM:SS), Date/Calendar (DD.MM.YYY), Stopwatch (MM:SS:MS / HH:MM:SS after minute overflow) and Alarm
#It has 12 input pins and 26 output pins, 24 driven by three TPIC6C595 shift registers in series and 2 driven by 2 N channel mosfets.

#Pin assignments:
#OUTPUTS:
#SHIFT_RCK = GPIO(16) register clock
#SHIFT_SRCK = GPIO(15) shift register clock
#SHIFT_DATA = GPIO(17) serial data

#Pins 0-7: TPIC6C595 1 (SEG F/PA/AS 6, SEG A/SO/AS 5, BCD D/AS 3, BCD B/AS 1, BCD A/AS 0, BCD C/AS 2, SEG G/NE/AS 4, !ALARM)
#Pins 0-7: TPIC6C595 2 (SEG D/PO/AS 10, SEG C/AS 9, SEG B/AS 8, SEG E/AS 7, !LMS, !LML, !LSS, !LSL)
#Pins 0-7: TPIC6C595 3 (!DMX 8, !DMX6, !DMX4, !DMX2, !DMX1, !DMX3, !DMX5, !DMX7)


#FET1: (!CAL out) = GPIO(18)
#FET2: (!strobe out) = GPIO(14)

#INPUTS:
#!GR = GPIO(2)
#EOSC = GPIO(3)
#Z = GPIO(4)
#!LST/LSP = GPIO(5)
#!DO/RY = GPIO(6)
#MC 0 = GPIO(7)
#MC 1 = GPIO(8)
#SST/SSP = GPIO(9)
#NUL/LAP/LAP = GPIO(10)
#CHOD.FO/!NAST = GPIO(11)
#PHASE = GPIO(12)
#STROBE in = GPIO(13)

#I2C: optional for future use (RTC DS3231)
#SDA = GPIO(20)
#SCL = GPIO(21)

#LIBRARIES:
import machine
import utime
import ustruct
import uasyncio
import ujson
import uos
import uerrno
import uio
import uarray

#CONSTANTS:
#Constants for shift register:
SHIFT_RCK = machine.Pin(16, machine.Pin.OUT) #register clock
SHIFT_SRCK = machine.Pin(15, machine.Pin.OUT) #shift register clock
SHIFT_DATA = machine.Pin(17, machine.Pin.OUT) #serial data






#Routines and functions:
#Reading INPUTS:
def read_inputs(): #Each input is a variable, which is set to 1 if the input is high and 0 if the input is low
    global GR
    global EOSC
    global Z
    global LST_LSP
    global DO_RY
    global MC_0
    global MC_1
    global SST_SSP
    global NUL_LAP
    global CHOD_FO
    global PHASE
    global STROBE_IN
    GR = 1 if GPIO(2).value() else 0
    EOSC = 1 if GPIO(3).value() else 0
    Z = 1 if GPIO(4).value() else 0
    LST_LSP = 1 if GPIO(5).value() else 0
    DO_RY = 1 if GPIO(6).value() else 0
    MC_0 = 1 if GPIO(7).value() else 0
    MC_1 = 1 if GPIO(8).value() else 0
    SST_SSP = 1 if GPIO(9).value() else 0
    NUL_LAP = 1 if GPIO(10).value() else 0
    CHOD_FO = 1 if GPIO(11).value() else 0
    PHASE = 1 if GPIO(12).value() else 0
    STROBE_IN = 1 if GPIO(13).value() else 0

#Writing OUTPUTS:
def write_outputs(): #Each output is a variable, which is set to 1 if the output should be high and 0 if the output should be low
    global ALARM
    global BCD_A
    global BCD_B
    global BCD_C
    global BCD_D
    global SEG_A
    global SEG_B
    global SEG_C
    global SEG_D
    global SEG_E
    global SEG_F
    global SEG_G
    global CAL
    global LSS
    global LSL
    global LMS
    global LML
    global STROBE_OUT
    global DMX1
    global DMX2
    global DMX3
    global DMX4
    global DMX5
    global DMX6
    global DMX7
    global DMX8


    #Firstly clear all outputs:
    clear_outputs()

    #Then set the outputs:
    shift_data([DMX7,DMX5,DMX3,DMX1,DMX2,DMX4,DMX6,DMX8, LSL,LSS,LML,LMS,SEG_E,SEG_B,SEG_C,SEG_D, ALARM,SEG_G,SEG_C,SEG_A,SEG_B,SEG_D,SEG_A,SEG_F])
    GPIO(18).value(CAL) #setting FET1 (CAL)
    GPIO(14).value(STROBE_OUT) #setting FET2 (strobe out)

def shift_data(data):
    for bit in data:
        SHIFT_DATA.value(bit) #set the data bit
        SHIFT_RCK.on() #clock the data into the register
        SHIFT_RCK.off() 
    SHIFT_SRCK.on() #clock the register into the output
    SHIFT_SRCK.off() 

    
def clear_outputs(): #clears all outputs
    shift_data([0,0,0,0,0,0,0,0]*3) #clearing shift registers
    GPIO(18).off() #clearing FET1 (CAL)
    GPIO(14).off() #clearing FET2 (strobe out)



#MAIN CODE:
if __name__ == "__main__":
    #Bootup (run once):
    clear_outputs() #clear all outputs

    #Main loop:
    while True:
        read_inputs()
        write_outputs()
    