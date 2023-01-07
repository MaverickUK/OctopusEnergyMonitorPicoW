import machine
import network
import time
from secrets import *

led= machine.Pin('LED', machine.Pin.OUT)

# Connect to Wifi using the credentials held in secrets.py
def wifi_connect(ssid=secrets['ssid'],psk=secrets['password']):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, psk)
    
    led.off()
 
    # Wait for connect or fail
    wait = 10
    while wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        wait -= 1
        print('waiting for connection...')
        time.sleep(1)
        led.toggle()
         
    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('wifi connection failed')
        led.off()
    else:
        led.on()
        print('connected')
        ip=wlan.ifconfig()[0]
        print('network config: ', ip)
        return ip
