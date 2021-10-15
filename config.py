import logging

#paste your AES-key here, taken from WienerNetze Webportal https://www.wienernetze.at/wnapp/smapp/ -> Anlagedaten
key ='0123456789ABCDEF0123456789ABCDEF'

# serial port
port = '/dev/ttyUSB0'

# logging
log_level=logging.DEBUG # DEBUG, INFO, WARNING, ERROR, FATAL

# mqtt
mqtt_enabled = True
mqtt_hostname = "smarthome"
mqtt_topic_prefix = "/smartmeter/"
mqtt_auth = {"username":"user","password":"password"}
mqtt_qos = 2
mqtt_retain = True
mqtt_publish_interval_seconds = 10