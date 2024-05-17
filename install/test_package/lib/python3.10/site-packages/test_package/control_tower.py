import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import KioskManager
import StoreManager
import threading

from TcpNode import *


store_clients = []


def main(args=None):
    global store_clients

    rp.init(args=args)
    tcpnode = TcpNode()
    store = StoreManager.StoreServer('192.168.0.36', 9022, store_clients)
    kiosk = KioskManager.KioskServer('192.168.0.36', 9021, store_clients, tcpnode)

    store_thread = threading.Thread(target=store.start_server)
    kiosk_thread = threading.Thread(target=kiosk.start_server)

    kiosk_thread.daemon = True  # 메인 스레드가 종료될 때 자동으로 종료되도록 설정

    store_thread.start()
    kiosk_thread.start()

    rp.spin(tcpnode)
    rp.shutdown()


if __name__ == '__main__':
    main()
