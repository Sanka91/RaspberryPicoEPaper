import machine
import time

led_pin = machine.Pin("LED", machine.Pin.OUT)

while True:
    print("Hello")
    led_pin.on()
    time.sleep(3)
    led_pin.off()
    time.sleep(3)