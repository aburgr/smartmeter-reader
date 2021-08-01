#!/usr/bin/python3

#external imports
import os
import time
import logging
import serial

# internal imports
import config
import decode
import publish

logging.basicConfig(level=config.log_level, format='%(asctime)s %(message)s')
logging.info("Process-Id: {0}".format(os.getpid()))

ser = serial.Serial(config.port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0)
data = bytearray()
dataLen = 0
timeLastRx = time.time() 
#data = bytearray(bytes.fromhex('a0a07ea067ceff031338bde6e700db084c475a67734381ad4f20000a140946086eb4f72682ed760f60d195990ad82b24993ca28e17e27bb72c3bf04df26a5e80932052d4d31f488bd594622a9bb5a519626a71690ff1712a2c816151f3ef5e791e73bfd454ef4c568a8f7e7ea067ceff031338bde6e700db084c475a67734381ad4f20000a140a01af08db49e7fc527454185052938aa1d1fd97b17dc11f52457f54d65ab40b3a14eed675f03b942d71688d45d99aa280a3bbfb6265f8d409680a94d3c28acd29966955c24bab950d7ea89d377e7ea067ceff031338bde6e700db084c475a67734381ad4f20000a140b87cf85e00d130c22a67c532c2107bbcc8275f4323e764f016fddffb28fce4153d0de2f64edf3bf463af79e75a01edbcfaafd7ef60067b89af600fb1b02727615042ba61d02bb0d45695b71867e7ea067ceff031338bde6e700db084c475a67734381ad4f20000a140c9be1b9f3b22ccff457148d670a377118ca1a814d76f94219166b869f58e8f0cda996e1b92dddfb82f89278de76bc6339eadd016f49a7b166e83ed84d5d2978c85afcb544d3f182dfed6c2c897e'))

def hex_str(s:str):
    return " ".join("{:02X}".format(ord(c)) for c in s)

def hex_str(ba:bytearray):
    return " ".join("{:02X}".format(c) for c in ba)

def parseData():
    global data
    msgs = []
    msgFound = True

    while (len(data) >= 91 and msgFound):
        mStart = data.find(b"\x7E\xA0")
        mLen = data[mStart+2]
        logging.debug("found msgStart at " + str(mStart) + ", msgLen is " + str(mLen) + ", dataLen is " + str(len(data)))
        if ((mStart + mLen + 2) <= len(data)):
            fullMsg = data[mStart:(mStart + mLen + 2)]
            logging.debug("full message received (" + hex_str(fullMsg) + ")")
            decodedMsg = decode.decode_packet(data[mStart:(mStart + mLen + 2)])
            
            # remove processed contents from data
            del data[0:(mStart + mLen + 2)]
            msgs.append(decode.parse_msg(decodedMsg))
        else:
            msgFound = False

    return msgs

try:
    while True:
        now = time.time()
        
        # read data from serial
        dataLen = ser.inWaiting()
        if(dataLen != 0):
            logging.debug("read data from serial. dataLen: " + str(dataLen))
            newData = ser.read(dataLen)
            timeLastRx = now
            data += newData
            
            # simple plausibilty check
            if(now - timeLastRx >= 10.0 or len(data) > 500):
                logging.error("Msg timeout or no valid Smartmeter message found, discard (" + hex_str(data) + ")")
                data = bytearray()
            else: 
                # parse data to message list (there may be multiple message read at once)
                msgList = parseData()

                # process messages
                for msg in msgList:
                    publish.process(msg)
        
        time.sleep(0.5)

except KeyboardInterrupt:
    logging.info("\nScript aborted through keyboard interrupt!\n")