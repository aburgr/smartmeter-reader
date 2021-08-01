#!/usr/bin/python3
# this file contains the code to decode and parse a message with the AES key

import binascii
import logging

#internal imports
import config

logging.basicConfig(level=config.log_level, format='%(asctime)s %(message)s')

##CRC-STUFF BEGIN
CRC_INIT=0xffff
POLYNOMIAL=0x1021

def byte_mirror(c):
    c=(c&0xF0)>>4|(c&0x0F)<<4
    c=(c&0xCC)>>2|(c&0x33)<<2
    c=(c&0xAA)>>1|(c&0x55)<<1
    return c

def calc_crc16(data):
    crc=CRC_INIT
    for i in range(len(data)):
        c=byte_mirror(data[i])<<8
        for j in range(8):
            if (crc^c)&0x8000: crc=(crc<<1)^POLYNOMIAL
            else: crc=crc<<1
            crc=crc%65536
            c=(c<<1)%65536
    crc=0xFFFF-crc
    return 256*byte_mirror(crc//256)+byte_mirror(crc%256)

def verify_crc16(input, skip=0, last=2, cut=0):
    lenn=len(input)
    data=input[skip:lenn-last-cut]
    goal=input[lenn-last-cut:lenn-cut]
    if   last == 0: return hex(calc_crc16(data))
    elif last == 2: return calc_crc16(data)==goal[0]*256 + goal[1]
    return False
##CRC-STUFF DONE

##DECODE-STUFF BEGIN
from Crypto.Cipher import AES
def decode_packet(input):  ##expects input to be bytearray.fromhex(hexstring), full packet  "7ea067..7e"
    if verify_crc16(input, 1, 2, 1):
        nonce=bytes(input[14:22]+input[24:28])  #systemTitle+invocation counter
        cipher=AES.new(binascii.unhexlify(config.key), AES.MODE_CTR, nonce=nonce, initial_value=2)
        return cipher.decrypt(input[28:-3])
    else:
        return ''
##DECODE-STUFF DONE

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + b
    return result

def parse_msg(s):
    m = {
        "dateTime" : {
            "year" : bytes_to_int(s[22:24]),
            "month" : bytes_to_int(s[24:25]),
            "day" : bytes_to_int(s[25:26]),
            "hour" : bytes_to_int(s[27:28]),
            "minute" : bytes_to_int(s[28:29]),
            "second" : bytes_to_int(s[29:30]),
        },
        "A+" : bytes_to_int(s[35:39])/1000.000, # +A Wh
        "A-" : bytes_to_int(s[40:44])/1000.000, # -A Wh
        "R+" : bytes_to_int(s[45:49])/1000.000, # +R varh
        "R-" : bytes_to_int(s[50:54])/1000.000, # -R varh
        "P+" : bytes_to_int(s[55:59]), # +P Watt
        "P-" : bytes_to_int(s[60:64]), # -P Watt
        "Q+" : bytes_to_int(s[65:69]), # +Q var
        "Q-" : bytes_to_int(s[70:74]), # -Q var
    }

    logging.info(str(m))
    return m


# data string explained:
# 7e         start-byte, hdlc opening flag
# a0         address field?
# 67         length field?
# cf         control field?
# 02         length field?
# 23         ?
# 13         frame type
# fbf1       crc16 from byte 2-7
# e6e700     some header?
# db         some header?
# 08         length of next field
# 44556677889900aa   systemTitle, includes S/N of meter in the right 4.5 bytes "7889900aa"
# 4f         length of next field
# 20         security byte: encryption-only
# 88887777   invocation counter
# 5540d5496ab897685e9b7e469942209b881fe280526f77c9d1dee763afb463a9bbe88449cb3fe79725875de945a405cb0f3119d3e06e3c4790130a29bc090cdf4b323cd7019d628ca255 ciphertext
# fce5       crc16 from byte 2 until end of ciphertext
# 7e         end-byte

# plaintext hex string explained
# 0f                          start-byte?
# 0059a374                    packet number, appears to be IC+1 (faked in this example)
# 0c                          intro 12byte-timestamp
# 07e5 01 1b 03 10 0b 2d 00ffc400   timestamp: year,month,day,dow,hours,minutes,seconds
# 020909                      some header for the following 9-value-structure?
# 0c                          intro 12byte-timestamp
# 07e5 01 1b 03 10 0b 2d 00ffc400   timestamp: year,month,day,dow,hours,minutes,seconds
# 06                          intro 32bit-value
# 004484bc                    +A Wh
# 06                          intro 32bit-value
# 0000053e                    -A Wh
# 06                          intro 32bit-value
# 0001004b                    +R varh
# 06                          intro 32bit-value
# 001c20f1                    -R varh
# 06                          intro 32bit-value
# 00000176                    +P W
# 06                          intro 32bit-value
# 00000000                    -P W
# 06                          intro 32bit-value
# 00000000                    +Q var
# 06                          intro 32bit-value
# 000000f4                    -Q var