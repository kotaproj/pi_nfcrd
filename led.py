from queue import Queue
import threading
import time
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
import sys

# LEDのピン設定
PIN_LED_NO1 = 16
PIN_LED_NO2 = 20
PIN_LED_NO3 = 21

LED_DICT = {
    "no1" : PIN_LED_NO1,
    "no2" : PIN_LED_NO2,
    "no3" : PIN_LED_NO3,
}


class LedThread(threading.Thread):
    """
    LED管理
    例:
    queue経由で、{"name":"no1", "action":"on"}
    を取得すると、LED1を点灯
    """
    def __init__(self, snd_que=None):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._snd_que = snd_que
        self._leds = {}

        # 各ピンをLED設定
        factory = PiGPIOFactory()
        for key, pin in LED_DICT.items():
            self._leds[key] = LED(pin, pin_factory=PiGPIOFactory())
        
        # LED2 - blink
        self._blink_leds("no2", interval=0.1, n=20)
        return

    def stop(self):
        self.stop_event.set()
        return


    def run(self):
        while True:
            value = self.rcv_que.get()
            print("[led_th]", value)
            
            if "led" not in value["type"]:
                print("[led_th]", "error!!!")
                continue
            
            if value["action"] in "blink":
                name = value["name"]
                self._blink_leds(name)
                continue
            
            if value["name"] in self._leds:
                name = value["name"]
                on_off = True if ("on" in value["action"]) else False
                self._write_leds(name, on_off)
        return

    @property
    def rcv_que(self):
        return self._rcv_que

    def _write_leds(self, name, on_off):
        if on_off:
            self._leds[name].on()
        else:
            self._leds[name].off()
        return

    def _blink_leds(self, name, interval=0.1, n=5):
        self._leds[name].blink(on_time=interval, off_time=interval, n=n)
        return


def main():
    import time

    led_th = LedThread()
    led_th.start()
    q = led_th.rcv_que

    q.put({"type": "led", "name": "no1", "action": "on"})
    time.sleep(3)
    q.put({"type": "led", "name": "no1", "action": "off"})
    time.sleep(1)
    q.put({"type": "led", "name": "no2", "action": "on"})
    time.sleep(3)
    q.put({"type": "led", "name": "no2", "action": "off"})
    time.sleep(1)
    q.put({"type": "led", "name": "no3", "action": "on"})
    time.sleep(3)
    q.put({"type": "led", "name": "no3", "action": "off"})
    time.sleep(1)

    led_th.stop()
   
    return

if __name__ == "__main__":
    main()
