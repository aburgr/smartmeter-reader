# Smartmeter Reader for Landis + Gyr E450

This project deals with the Smartmeter Landis + Gyr E450 which is (in my case) operated by Wiener Netze. It reads the data from the optical user  interface (de: Kundenschnittstelle).

## Requirements
- Smartmeter Landis + Gyr E450
- Raspberry Pi
- Python 3
- IR Schreib/Lesekopf USB (Optokopf) (Norm: IEC-62056-21). I used this one https://shop.weidmann-elektronik.de/index.php?page=product&info=24)

## Install requirements
```
pip3 install -r requirements.txt
```

## Configuration
This configuration is stored in `config.py`.

## Start script
in console:
```
python3 smartmeter.py
```

in background (logging to smartmeter.log in home directory):
```
nohup python3 smartmeter.py > ~/smartmeter.log 2>&1 &
```

# Troubleshooting
## Msg timeout or no valid Smartmeter message found
Check if there is data on the serial port.

```
stty -F /dev/ttyUSB0 9600 -parenb cs8 -cstopb -ixoff -crtscts -hupcl -ixon -opost -onlcr -isig -icanon -iexten -echo -echoe -echoctl -echoke 
cat /dev/ttyUSB0 | hexdump
```
(from https://shop.weidmann-elektronik.de/media/files_public/9d73b590bf0752a5beff32d229d4497d/HowToRaspberryPi.pdf)

## -bash: ./smartmeter.py: Permission denied

Set the executable flag for the smartmeter.py
```
chmod +x smartmeter.py
```