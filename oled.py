from queue import Queue
import threading
import time
from systems import SystemsData

# Imports the necessary libraries...
import socket
import fcntl
import struct
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import sys

from systems import SystemsData


# OLED設定
DISP_WIDTH = 128
DISP_HEIGHT = 64
DEVICE_ADDR = 0x3C

PATH_FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"

class OledThread(threading.Thread):
    """
    OLED管理
    例:
    queue経由で、{"type":"oled", "time": "3000", "name":"ip"}
    disp : ip / clear
    """
    def __init__(self, snd_que=None):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._snd_que = snd_que
        self._sysdat = SystemsData()

        # Setting some variables for our reset pin etc.
        RESET_PIN = digitalio.DigitalInOut(board.D4)
        TEXT = ""

        # Very important... This lets py-gaugette 'know' what pins to use in order to reset the display
        i2c = board.I2C()
        self._oled = adafruit_ssd1306.SSD1306_I2C(DISP_WIDTH, DISP_HEIGHT, i2c, addr=DEVICE_ADDR, reset=RESET_PIN)

        # font
        self._font10 = ImageFont.truetype(PATH_FONT, 10)
        self._font12 = ImageFont.truetype(PATH_FONT, 12)
        self._font14 = ImageFont.truetype(PATH_FONT, 14)
        self._font16 = ImageFont.truetype(PATH_FONT, 16)
        self._font18 = ImageFont.truetype(PATH_FONT, 18)

        # Clear display.
        self._oled.fill(0)
        self._oled.show()
        
        # system data
        self._sysdat = SystemsData()
        return

    def stop(self):
        self.stop_event.set()
        # cleanup
        self._oled.fill(0)
        self._oled.show()
        return


    def run(self):
        while True:
            item = self.rcv_que.get()
            print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, item)
            
            if "oled" not in item["type"]:
                print("[oled_th]", "error : type")
                continue
            
            self._recvice(item)
        return

    @property
    def rcv_que(self):
        return self._rcv_que

    def _recvice(self, item):
        val_time = int(item["time"]) / 1000
        val_name = item["name"]

        def display_ip():
            def get_ip_address(ifname):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                return socket.inet_ntoa(
                    fcntl.ioctl(
                        s.fileno(),
                        0x8915,  # SIOCGIFADDR
                        struct.pack("256s", str.encode(ifname[:15])),
                    )[20:24]
                )
            # This sets TEXT equal to whatever your IP address is, or isn't
            try:
                TEXT = get_ip_address("wlan0")  # WiFi address of WiFi adapter. NOT ETHERNET
            except IOError:
                try:
                    TEXT = get_ip_address("eth0")  # WiFi address of Ethernet cable. NOT ADAPTER
                except IOError:
                    TEXT = "NO INTERNET!"


            # Clear display.
            self._oled.fill(0)
            self._oled.show()

            # Create blank image for drawing.
            image = Image.new("1", (self._oled.width, self._oled.height))
            draw = ImageDraw.Draw(image)

            # Draw the text
            intro = "＜ラズパイ＞"
            ip = "IPアドレス:"
            draw.text((0, 46), TEXT, font=self._font14, fill=255)
            draw.text((0, 0), intro, font=self._font18, fill=255)
            draw.text((0, 30), ip, font=self._font14, fill=255)

            # Display image
            self._oled.image(image)
            self._oled.show()
            return

        def display_clear():
            self._oled.fill(0)
            self._oled.show()
            return

        def display_key(val_name):
            # Clear display.
            self._oled.fill(0)
            self._oled.show()
            
            if val_name in self._sysdat.json_dict:
                item_name = self._sysdat.json_dict[val_name]["name"]
                item_value = self._sysdat.json_dict[val_name]["value"]
            else:
                return

            # Create blank image for drawing.
            image = Image.new("1", (self._oled.width, self._oled.height))
            draw = ImageDraw.Draw(image)

            # Draw the text
            draw.text((0, 0), item_name, font=self._font18, fill=255)
            draw.text((0, 30), item_value, font=self._font18, fill=255)

            # Display image
            self._oled.image(image)
            self._oled.show()
            return


        if "ip" in val_name:
            display_ip()
        elif "clear" in val_name:
            # Clear display.
            display_clear()
        else:
            display_key(val_name)

        if val_time > 0:
            time.sleep(val_time)
            display_clear()
        return

def main():
    import time

    oled_th = OledThread()
    oled_th.start()
    q = oled_th.rcv_que

    q.put({"type": "oled", "time": "3000", "name":"ip"})
    time.sleep(10)
    q.put({"type": "oled", "time": "3000", "name":"clear"})
    time.sleep(1)

    oled_th.stop()
   
    return

if __name__ == "__main__":
    main()