from queue import Queue
import threading
import ast
import sys

from ercode import *

class PreThread(threading.Thread):
    """
    プレゼンター
    """
    def __init__(self):
        print("__init__")
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._snd_ques = {}
        return

    def stop(self):
        print("stop")
        self.stop_event.set()
        return


    def run(self):
        print("run")
        while True:
            # time.sleep(0.050)
            item = self.rcv_que.get()
            print("[pre_th]", "run : get : ", item)
            if "sw" in item["type"]:
                self._recvice_sw(item)
            elif "nfc" in item["type"]:
                self._recvice_nfc(item)
            elif "pre" in item["type"]:
                self._recvice_pre(item)
            else:
                print("[pre_th]", "Error : ", item)

        return

    def _recvice_nfc(self, item):
        print("_recvice_nfc")
        name = item["name"]
        action = item["action"]
        if "touched" in action:
            self._put_que("buzzer", {"type": "buzzer", "name": "buzzer", "time": "200", "note": "C4"})
            self._put_que("led", {"type": "led", "name": "no1", "action": "blink"})

        elif "released" in action:
            pass
        elif "registered" in action:
            self._put_que("buzzer", {"type": "buzzer", "name": "buzzer", "time": "200", "note": "E4"})
            self._put_que("led", {"type": "led", "name": "no3", "action": "blink"})
            self._put_que("oled", {"type": "oled", "name": name, "time": "3000"})
            self._put_que("ifttt", {"type": "ifttt", "name": name})
        else:
            print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, "command not found!", name)
        return

    def _recvice_sw(self, item):
        print("_recvice_sw")

        def send_que_sw_no1(action):
            led_act = "on" if "press" in action else "off"
            self._put_que("led", {"type": "led", "name": "no1", "action":led_act})
            return

        def send_que_sw_no2(action):
            led_act = "on" if "press" in action else "off"
            self._put_que("led", {"type": "led", "name": "no2", "action": led_act})
            return

        def send_que_sw_no3(action):
            led_act = "on" if "press" in action else "off"
            self._put_que("led", {"type": "led", "name": "no3", "action": led_act})
            return

        name = item["name"]
        action = item["action"]
        if "no1" in name:
            send_que_sw_no1(action)
        elif "no2" in name:
            send_que_sw_no2(action)
        elif "no3" in name:
            send_que_sw_no3(action)
        else:
            print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, "command not found!", name)
        return


    def _recvice_pre(self, item):
        print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, item)

        def send_que_ifttt(er):
            if ErIfttt.OK == er:
                self._put_que("led", {"type": "led", "name": "no2", "action":"blink"})
            elif ErIfttt.ER_POST == er:
                self._put_que("led", {"type": "led", "name": "no1", "action":"blink"})
                self._put_que("led", {"type": "led", "name": "no2", "action":"blink"})
            elif ErIfttt.ER_EXCEPTION == er:
                self._put_que("led", {"type": "led", "name": "no1", "action":"blink"})
            else:
                self._put_que("led", {"type": "led", "name": "no1", "action":"on"})
            return

        if "ifttt" == item["src"]:
            send_que_ifttt(item["er"])
        else:
            print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, "command not found!")
        return


    def _put_que(self, key, item):
        if key in self._snd_ques:
            self._snd_ques[key].put(item)
        else:
            print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, "snd_que not found!", key)

    @property
    def rcv_que(self):
        return self._rcv_que

    @property
    def snd_ques(self):
        return self._snd_ques

    @snd_ques.setter
    def snd_ques(self, snd_ques):
        if snd_ques is None:
            raise TypeError('invalid snd_ques')
        self._snd_ques = snd_ques



def main():
    import time

    pre_th = PreThread()
    pre_th.start()
    q = pre_th.rcv_que
    q.put("123")
    time.sleep(1)

    for i in range(5):
        q.put(i)
        time.sleep(1)
    pre_th.stop()
   
    return

if __name__ == "__main__":
    main()