from queue import Queue
import threading
import time
import sys
import requests
from systems import SystemsData
from ercode import ErIfttt

IFTTT_TOKEN = "xxxxxxxxxxxxxxxxxxxxxx"

class IftttThread(threading.Thread):
    """
    IFTTT管理
    例:
    queue経由で、{"name":key}
    を取得すると、IFTTT - webhookにトリガーリクエストを送信
    """
    def __init__(self, snd_que=None):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._rcv_que = Queue()
        self._snd_que = snd_que
        self._sysdat = SystemsData()
        return


    def stop(self):
        self.stop_event.set()
        return


    def run(self):
        while True:
            value = self.rcv_que.get()
            print("[ifttt_th]", value)
            
            if "ifttt" not in value["type"]:
                print("[ifttt_th]", "error!!!")
                continue
            
            if value["name"] in self._sysdat.json_dict:
                name = value["name"]
                self._post_request(name)
            else:
                print("[ifttt_th]", "error!!!_name")
        return

    @property
    def rcv_que(self):
        return self._rcv_que

    def _post_request(self, name):
        val = self._sysdat.json_dict[name]

        payload = {"value1": "",
                    "value2": "",
                    "value3": "" }
        payload["value1"] = val["cell"]
        payload["value2"] = val["value"]
        payload["value3"] = ""

        url = "https://maker.ifttt.com/trigger/" + val["event_id"] + "/with/key/" + IFTTT_TOKEN
        print(url)

        try:
            response = requests.post(url, data=payload)
            if 200 == response.status_code and "Congratulations" in response.text:
                self._message_error(ErIfttt.OK)
            else:
                self._message_error(ErIfttt.ER_POST)
            response.close()
        except requests.exceptions.RequestException as e:
            print("[ifttt_th] e", e)
            self._message_error(ErIfttt.ER_EXCEPTION)
        return


    def _message_error(self, er):
        print(sys._getframe().f_code.co_filename, sys._getframe().f_code.co_name, er)
        if self._snd_que is not None:
            self._snd_que.put({"type": "pre", "src": "ifttt", "er":er})
        return


def main():
    ifttt_th = IftttThread()
    ifttt_th.start()
    q = ifttt_th.rcv_que

    q.put({"type": "ifttt", "name": "04102001af4905"})
    time.sleep(10)

    ifttt_th.stop()
   
    return

if __name__ == "__main__":
    main()
