from queue import Queue
import threading
import time
import sys
import binascii
import nfc
import os
from systems import SystemsData

class NfcrdThread(threading.Thread):
    """
    NFCリーダ管理
    """
    def __init__(self, snd_que=None):
        print("[nfcrd]:", "__init__")
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.setDaemon(True)

        self._snd_que = snd_que
        self._sysdat = SystemsData()
        return

    def on_rdwr_connect(self, tag):
        #タッチ時の処理
        print("【 Touched 】")

        #タグ情報を表示
        print(tag)

        #IDmの表示
        self.idm = binascii.hexlify(tag._nfcid)
        print("IDm : " + str(self.idm))

        #特定のIDmだった場合
        for k, v in self._sysdat.json_dict.items():
            if self.idm == k.encode():
                print("登録されたID:", k, v)
                self._send_msg(k, "registered")
                return

        self._send_msg("unknown", "touched")

        return True

    def read_tag(self):
        print("read_tag:run")
        cl = nfc.ContactlessFrontend('usb')
        try:
            cl.connect(rdwr={'on-connect': self.on_rdwr_connect})
        finally:
            cl.close()
        print("read_tag:over")

    def stop(self):
        self.stop_event.set()

    def run(self):

        while True:
            #タッチ待ち
            self.read_tag()

            #リリース時の処理
            self._send_msg("unknown", "released")

            # 無効期間
            time.sleep(2.0)
        return

    def _send_msg(self, name, action):
        if self._snd_que is None:
            return
        print("[nfcrd]", "_send_msg:", name)
        self._snd_que.put({"type": "nfc", "name": name, "action":action})
        return

def main():
    q = Queue()
    nfcrd_th = NfcrdThread(q)
    nfcrd_th.start()
    time.sleep(10)
    nfcrd_th.stop()
    while True:
        if q.empty():
            print("!!! q.empty !!!")
            break
        print(q.get())
    return

if __name__ == "__main__":
    main()