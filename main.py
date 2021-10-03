import time
import sys

from presenter import PreThread

from led import LedThread
from buzzer import BuzzerThread
from ifttt import IftttThread
from oled import OledThread

from sw import SwThread
from nfcrd import NfcrdThread

def main():

    print("main:run")

    # メッセージの交通整理のスレッド - メッセージの交通整理
    pre_th = PreThread()
    que_pre = pre_th.rcv_que
    pre_th.start()

    # 出力側のスレッド - メッセージを受け取る
    out_ths = {}
    out_ths["led"] = LedThread()
    out_ths["buzzer"] = BuzzerThread()
    out_ths["ifttt"] = IftttThread(que_pre)
    out_ths["oled"] = OledThread()
    out_ques = {k:v.rcv_que for k, v in out_ths.items()}
    for out_th in out_ths.values():
        out_th.start()

    pre_th.snd_ques = out_ques

    # 入力側のスレッド - メッセージを送信する
    in_ths = {}
    in_ths["nfcrd"] = NfcrdThread(que_pre)
    in_ths["sw"] = SwThread(que_pre)
    for in_th in in_ths.values():
        in_th.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("stop")

    # 終了処理
    for out_th in out_ths.values():
        out_th.stop()
    pre_th.stop()
    for in_th in in_ths.values():
        in_th.stop()
    return

if __name__ == "__main__":
    main()