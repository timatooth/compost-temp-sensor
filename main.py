import requests
from machine import Pin
import machine
import onewire
import time, ds18x20
from machine import Timer

# Grafana.net API creds
USER_ID = ''
API_KEY = ''

ow = onewire.OneWire(Pin(12)) # create a OneWire bus on GPIO12
ds = ds18x20.DS18X20(ow)
# use gpio4 as a power source for the DS18B20
supply_pin = Pin(4, Pin.OUT)

def publish_metric(rom, temp):
    body = 'compost_temp,rom={},source=compost-esp metric={}'.format(rom, temp)
    print(body)

    max_retries = 6
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.post(
                'http://influx-prod-09-prod-au-southeast-0.grafana.net/api/v1/push/influx/write',
                headers={
                    'Content-Type': 'text/plain',
                },
                data=str(body),
                auth=(USER_ID, API_KEY)
            )

            status_code = response.status_code
            if status_code == 204:  # Successful response
                break
            else:
                print(f"Failed to publish metric. Status code: {status_code}")
        except Exception as e:
            print(f"Error: {e}")

        retry_count += 1
        time.sleep(1)  # Wait for a short duration before retrying


def update_temps():
    supply_pin.value(1)
    time.sleep(1)
    roms = ds.scan()
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        temp = ds.read_temp(rom)
        print("{}: {}C".format(rom.hex(), temp))
        publish_metric(rom.hex(), temp)
    supply_pin.value(0)

def deep_sleep(duration):
    print("Going to deep sleep...")
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire (waking the device)
    rtc.alarm(rtc.ALARM0, duration * 1000)

    # put the device to sleep
    machine.deepsleep()

while True:
    time.sleep(5)
    update_temps()
    deep_sleep(1800) # deep sleep for 30 minutes