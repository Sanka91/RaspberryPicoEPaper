from machine import Pin, SPI
import framebuf
import utime
from read_bmp import get_image_array
import network
import time
import urequests
import base64



def connect_to_internet():

    ssid = "Phil1991"
    password = "Karibik1"

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("List of available networks:")
    available_networks = wlan.scan()
    print(available_networks)
    print("Trying to establish connection to network --{}--".format(ssid))
    wlan.connect(ssid, password)

    retries = 0
    while wlan.isconnected() == False & retries <= 10:
        print("Current connection status: {}".format(wlan.status()))
        print("Waiting for connection...")
        time.sleep(2)
        retries += 1

    if wlan.isconnected():
        print("Successfully connected to network --{}--".format(ssid))
        print("Network information: {}".format(wlan.ifconfig()))
        return True
    else:
        print("Could not connnect to network --{}--".format(ssid))
        print("Offline mode triggered")
        return False


# Display resolution
# from repos.qr_repository import QRRepository

EPD_WIDTH = 800
EPD_HEIGHT = 480

RST_PIN = 12
DC_PIN = 8
CS_PIN = 9
BUSY_PIN = 13


class EPD_7in5_B:
    def __init__(self):

        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)

        # Init muss ganz am Ende stehen
        self.init()


    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def WaitUntilIdle(self):
        print("e-Paper busy")
        while (self.digital_read(self.busy_pin) == 0):  # Wait until the busy_pin goes LOW
            self.delay_ms(20)
        self.delay_ms(20)
        print("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x12)  # DISPLAY REFRESH
        self.delay_ms(100)  # !!!The delay here is necessary, 200uS at least!!!
        self.WaitUntilIdle()

    def init(self):
        # EPD hardware init start
        self.reset()

        self.send_command(0x06)  # btst
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x28)  # If an exception is displayed, try using 0x38
        self.send_data(0x17)

        #         self.send_command(0x01)  # POWER SETTING
        #         self.send_data(0x07)
        #         self.send_data(0x07)     # VGH=20V,VGL=-20V
        #         self.send_data(0x3f)     # VDH=15V
        #         self.send_data(0x3f)     # VDL=-15V

        self.send_command(0x04)  # POWER ON
        self.delay_ms(100)
        self.WaitUntilIdle()

        self.send_command(0X00)  # PANNEL SETTING
        self.send_data(0x0F)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61)  # tres
        self.send_data(0x03)  # source 800
        self.send_data(0x20)
        self.send_data(0x01)  # gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11)
        self.send_data(0x07)

        self.send_command(0X60)  # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)  # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)  # 800*480
        self.send_data(0x00)
        self.send_data(0x00)

        return 0;

    def Clear(self):

        high = self.height
        if (self.width % 8 == 0):
            wide = self.width // 8
        else:
            wide = self.width // 8 + 1

        self.send_command(0x10)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)

        self.send_command(0x13)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)

        self.TurnOnDisplay()

    def ClearRed(self):

        high = self.height
        if (self.width % 8 == 0):
            wide = self.width // 8
        else:
            wide = self.width // 8 + 1

        self.send_command(0x10)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)

        self.send_command(0x13)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xff)

        self.TurnOnDisplay()

    def ClearBlack(self):

        high = self.height
        if (self.width % 8 == 0):
            wide = self.width // 8
        else:
            wide = self.width // 8 + 1

        self.send_command(0x10)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)

        self.send_command(0x13)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)

        self.TurnOnDisplay()

    def display(self):

        high = self.height
        if (self.width % 8 == 0):
            wide = self.width // 8
        else:
            wide = self.width // 8 + 1

        # send black data
        self.send_command(0x10)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(self.buffer_black[i + j * wide])

        # send red data
        self.send_command(0x13)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(self.buffer_red[i + j * wide])

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02)  # power off
        self.WaitUntilIdle()
        self.send_command(0x07)  # deep sleep
        self.send_data(0xa5)


def fetch_cloud_function_info():
    try:
        url = 'https://europe-west3-lsttrading.cloudfunctions.net/Epaper'
        response = urequests.get(url)
        return response.json()
    except Exception as e:
        print("Exception occurred trying to call cloud function. Error code: {}".format(e))




if __name__ == '__main__':
    print("Epaper started")

    epd = EPD_7in5_B()

    epd.imageblack.fill(0xff)

    # Horizontal Lines
    epd.imageblack.hline(0, 240, 800, 0x00)

    # # Colored, filled, rectangles
    epd.imageblack.fill_rect(400, 0, 200, 240, 0x00 )
    # epd.imageblack.fill_rect(0, 0, 200, 240, 0x00 )
    epd.imagered.fill_rect(300, 240, 200, 240, 0xff)

    arrow_up_icon = get_image_array("images/Arrow_up_new.bmp", 10, 11)
    arrow_up_buf = framebuf.FrameBuffer(arrow_up_icon, 10, 11, framebuf.MONO_HLSB)
    epd.imageblack.blit(arrow_up_buf, 15, 350)

    sun_icon = get_image_array("images/Sun.bmp", 30, 30)
    sun_buf = framebuf.FrameBuffer(sun_icon, 30, 30, framebuf.MONO_HLSB)
    epd.imageblack.blit(sun_buf, 50, 350)

    is_connected = connect_to_internet()
    if is_connected:
        cloud_function_resp = fetch_cloud_function_info()
        print(cloud_function_resp)

        # QR Code
        #qr_bytes = bytearray(base64.b64decode(cloud_function_resp["qr_code"]))
        # qr_code = framebuf.FrameBuffer(qr_bytes, 100, 100, framebuf.MONO_HLSB)
        # epd.imagered.blit(qr_code, 350, 310)
        # epd.imagered.text(cloud_function_resp["title"], 305, 260, 0x00)

        # Weather
        # epd.imagered.text("Updated: {}".format(today_info["last_updated"]), 275, vertical_start, 0xff)
        epd.imagered.text("{}, {}".format(cloud_function_resp["location_name"], cloud_function_resp["location_country"]), 0,  10, 0xff)
        # epd.imageblack.hline(240,  45, 300, 0x00)

        vertical_shift = 0
        for forecast_day in cloud_function_resp["forecasts"]:
            date = forecast_day["date"]

            weather_icon_bytes = forecast_day["icon"]
            weather_icon_bytearray = bytearray(base64.b64decode(weather_icon_bytes))
            weather_icon = framebuf.FrameBuffer(weather_icon_bytearray, 40, 40, framebuf.MONO_HLSB)
            epd.imageblack.blit(weather_icon, 40, 55 + vertical_shift)

            epd.imageblack.text("U:{}".format(forecast_day["sunrise"]), 120, 65 + vertical_shift, 0x00 )
            epd.imageblack.text("D:{}".format(forecast_day["sunset"]), 120, 80 + vertical_shift, 0x00 )

            epd.imageblack.text("Max:{}".format(forecast_day["maxtemp_c"]), 220, 65 + vertical_shift, 0x00 )
            epd.imageblack.text("Min:{}".format(forecast_day["mintemp_c"]), 220, 80 + vertical_shift, 0x00 )

            epd.imageblack.text("Wind:{} kmH".format(forecast_day["maxwind_kph"]), 320, 65 + vertical_shift, 0x00)
            epd.imageblack.text("Hum:{}%".format(forecast_day["avghumidity"]), 320, 80 + vertical_shift, 0x00)

            vertical_shift += 50


    epd.display()


    # while True:
    #
    #     # epd.ufo_sprite.fill_rect(70, 300, 50, 80, 0xff)
    #     # epd.screen_buffer.blit(epd.ufo_sprite, 50, 50)

    #     epd.imageblack.fill(0xff)
    #     # epd.imagered.fill(0x00)
    #
    #     epd.imageblack.blit(epd.ufo_sprite, 350, 290)
    #     # epd.imagered.blit(epd.ufo_sprite, 100, 200)
    #
    #     epd.imageblack.text("Waveshare", 5, 10, 0x00)
    #     epd.imagered.text("Testpaper", 5, 40, 0xff)
    #     epd.imageblack.text("Raspberry Pico", 5, 70, 0x00)
    #

        # epd.imageblack.vline(10, 90, 60, 0x00)

    #
    #
    #     # epd.imageblack.rect(400, 180, 50, 80, 0x00)
    #     # epd.imageblack.fill_rect(70, 180, 50, 80, 0x00)
    #     # epd.imagered.rect(400, 300, 50, 80, 0xff)
    #     # epd.imagered.fill_rect(70, 300, 50, 80, 0xff)
    #     epd.display()
    #     epd.delay_ms(500)
    #
    #     # epd.Clear()
    #     # epd.delay_ms(2000)
    #     print("sleep")
    #     # epd.sleep()

