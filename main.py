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
    # epd.imageblack.fill_rect(400, 0, 200, 240, 0x00 )
    # epd.imageblack.fill_rect(0, 0, 200, 240, 0x00 )
    epd.imagered.fill_rect(300, 240, 200, 240, 0xff)

    # Image rendering is upside down
    arrow_down_icon = get_image_array("images/Arrow_up.bmp", 10, 11)
    arrow_down_buf = framebuf.FrameBuffer(arrow_down_icon, 10, 11, framebuf.MONO_HLSB)
    arrow_up_icon = get_image_array("images/Arrow_down.bmp", 10, 11)
    arrow_up_buf = framebuf.FrameBuffer(arrow_up_icon, 10, 11, framebuf.MONO_HLSB)

    sun_icon = get_image_array("images/Sun.bmp", 30, 30)
    sun_buf = framebuf.FrameBuffer(sun_icon, 30, 30, framebuf.MONO_HLSB)
    epd.imageblack.blit(sun_buf, 113, 17)

    rain_icon = get_image_array("images/Rain.bmp", 30, 30)
    rain_buf = framebuf.FrameBuffer(rain_icon, 30, 30, framebuf.MONO_HLSB)
    epd.imageblack.blit(rain_buf, 285, 17)

    temperature_icon = get_image_array("images/Temperature.bmp", 30, 30)
    temperature_buf = framebuf.FrameBuffer(temperature_icon, 30, 30, framebuf.MONO_HLSB)
    epd.imageblack.blit(temperature_buf, 195, 17)

    like_icon = get_image_array("images/Like.bmp", 25, 25)
    like_buf = framebuf.FrameBuffer(like_icon, 25, 25, framebuf.MONO_HLSB)
    epd.imagered.blit(like_buf, 330, 420)

    dairy_icon = get_image_array("images/Dairy.bmp", 25, 25)
    dairy_buf = framebuf.FrameBuffer(dairy_icon, 25, 25, framebuf.MONO_HLSB)
    epd.imagered.blit(dairy_buf, 325, 450)

    clock_icon = get_image_array("images/Clock.bmp", 25, 25)
    clock_buf = framebuf.FrameBuffer(clock_icon, 25, 25, framebuf.MONO_HLSB)
    epd.imagered.blit(clock_buf, 415, 420)

    veggie_icon = get_image_array("images/Veggie.bmp", 25, 25)
    veggie_buf = framebuf.FrameBuffer(veggie_icon, 25, 25, framebuf.MONO_HLSB)
    epd.imagered.blit(veggie_buf, 415, 450)


    is_connected = connect_to_internet()
    if is_connected:
        cloud_function_resp = fetch_cloud_function_info()
        weather_response = cloud_function_resp["Weather"]
        recipe_response = cloud_function_resp["Recipe"]

        # Recipe module with QR Code
        qr_bytes = bytearray(base64.b64decode(recipe_response["qr_code"]))
        qr_code = framebuf.FrameBuffer(qr_bytes, 125, 125, framebuf.MONO_HLSB)
        epd.imagered.blit(qr_code, 335, 287)
        if len(recipe_response["title"]) > 20:
            epd.imagered.text(recipe_response["title"][:20], 320, 250, 0x00)
            epd.imagered.text("{}...".format(recipe_response["title"][20:38]), 320, 265, 0x00)
        else:
            epd.imagered.text(recipe_response["title"], 320, 250, 0x00)


        epd.imagered.text("{}".format(recipe_response["readyInMinutes"]), 445, 430, 0x00)
        epd.imagered.text("{}".format(recipe_response["aggregateLikes"]), 360, 430, 0x00)
        epd.imagered.text("{}".format(recipe_response["vegetarian"]), 445, 460, 0x00)
        epd.imagered.text("{}".format(recipe_response["dairy"]), 355, 460, 0x00)


        # Weather
        # epd.imagered.text("Updated: {}".format(today_info["last_updated"]), 275, vertical_start, 0xff)
        epd.imagered.text("{},".format(weather_response["location_name"]), 0,  0, 0xff)
        epd.imageblack.text("{}".format(weather_response["location_country"]), 0, 15, 0x00)
        # epd.imageblack.hline(240,  45, 300, 0x00)

        vertical_shift = 5
        for forecast_day in weather_response["forecasts"]:
            date = forecast_day["date"]
            epd.imagered.text(date, 0, 43 + vertical_shift, 0xff)
            epd.imageblack.hline(0, 53 + vertical_shift, 90, 0x00)

            weather_icon_bytes = forecast_day["icon"]
            weather_icon_bytearray = bytearray(base64.b64decode(weather_icon_bytes))
            weather_icon = framebuf.FrameBuffer(weather_icon_bytearray, 40, 40, framebuf.MONO_HLSB)
            epd.imageblack.blit(weather_icon, 18, 55 + vertical_shift)

            epd.imageblack.blit(arrow_up_buf, 95, 62 + vertical_shift)
            epd.imageblack.blit(arrow_down_buf, 95, 79 + vertical_shift)

            epd.imageblack.text("{}".format(forecast_day["sunrise"]), 110, 65 + vertical_shift, 0x00 )
            epd.imageblack.text("{}".format(forecast_day["sunset"]), 110, 80 + vertical_shift, 0x00 )

            epd.imageblack.text("Max:{}".format(forecast_day["maxtemp_c"]), 180, 65 + vertical_shift, 0x00 )
            epd.imageblack.text("Min:{}".format(forecast_day["mintemp_c"]), 180, 80 + vertical_shift, 0x00 )

            epd.imageblack.text("Prob: {}%".format(forecast_day["daily_chance_of_rain"]), 270, 65 + vertical_shift, 0x00)
            epd.imageblack.text("{} mm".format(forecast_day["totalprecip_mm"]), 270, 80 + vertical_shift, 0x00)

            vertical_shift += 67


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

