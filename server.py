import socket
import asyncio
import threading
import time
import numpy
import os

inGame = False

class NonNegativeNumpyIndex:
    def __init__(self, numpyArray):
        self.array = numpyArray
    def __call__(self, row, col, value = None):
        if (row < 0) | (col < 0):
            raise Exception("IndexOutOfBounds: No negative numbers permitted.")
        elif (value != None):
            self.array[row][col] = value
        else:
            return self.array[row][col]

def NormalGame(client1, client2):
    global inGamePacketQueue
    map = NonNegativeNumpyIndex(numpy.full(shape=(6,7), fill_value=-1))
    _a = {}
    _a[0], _a[1] = client1, client2
    s.sendto(b'0', _a[0])
    s.sendto(b'1', _a[1])
    while True:
        for sock in range(2):
            while inGamePacketQueue[_a[sock]] == b'':
                time.sleep(0.01)
                if inGamePacketQueue[_a[(sock + 1) % 2]] == b'lg':
                    try:
                        s.sendto(b'lg', _a[sock])
                    except:
                        pass
                    del inGame[inGame.index(_a[0])]
                    del inGame[inGame.index(_a[1])]
                    del inGamePacketQueue[_a[0]]
                    del inGamePacketQueue[_a[1]]
                    return 0
            slot = inGamePacketQueue[_a[sock]]
            inGamePacketQueue[_a[sock]] = b''
            if slot == b'lg':
                try:
                    s.sendto(b'lg', _a[(sock + 1) % 2])
                except:
                    pass
                del inGame[inGame.index(_a[0])]
                del inGame[inGame.index(_a[1])]
                del inGamePacketQueue[_a[0]]
                del inGamePacketQueue[_a[1]]
                return 0
            try:
                dcSlot = slot.decode()
                map(int(dcSlot[0]), int(dcSlot[1]), sock)
                stop = False
            except:
                s.sendto(b'BANNED', _a[sock])
                os.system("iptables -A INPUT -s " + _a[sock][0] + " -j DROP")
                print("\033[93m" + _a[sock][0] + " has been BANNED")
                try:
                    s.sendto(b'lg', _a[(sock + 1) % 2])
                except:
                    pass
                del inGame[inGame.index(_a[0])]
                del inGame[inGame.index(_a[1])]
                del inGamePacketQueue[_a[0]]
                del inGamePacketQueue[_a[1]]
                return 0
            print(map)
            for r in range(0, 6):
                for c in range(0,7):
                    if map(r,c) != -1:
                        print((r,c))
                        try:
                            if (map(r,c) == map(r + 1,c) == map(r + 2,c) == map(r + 3,c)):
                                stop = True
                                print(1)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r - 1,c) == map(r - 2,c) == map(r - 3,c)):
                                stop = True
                                print(2)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r,c + 1) == map(r,c + 2) == map(r,c + 3)):
                                stop = True
                                print(3)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r,c - 1) == map(r,c - 2) == map(r,c - 3)):
                                stop = True
                                print(4)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r + 1,c + 1) == map(r + 2,c + 2) == map(r + 3,c + 3)):
                                stop = True
                                print(5)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r + 1,c - 1) == map(r + 2,c - 2) == map(r + 3,c - 3)):
                                stop = True
                                print(6)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r - 1,c - 1) == map(r - 2,c - 2) == map(r - 3,c - 3)):
                                print(map(r - 1,c - 1))
                                stop = True
                                print(7)
                                break
                        except:
                            pass
                        try:
                            if (map(r,c) == map(r - 1,c + 1) == map(r - 2,c + 2) == map(r - 3,c + 3)):
                                stop = True
                                print(8)
                                break
                        except:
                            pass
                if stop:
                    break
            s.sendto(slot, _a[(sock + 1) % 2])
            if stop:
                print(inGame)
                print(inGamePacketQueue)
                del inGame[inGame.index(_a[0])]
                del inGame[inGame.index(_a[1])]
                del inGamePacketQueue[_a[0]]
                del inGamePacketQueue[_a[1]]
                print(inGame)
                print(inGamePacketQueue)
                s.sendto(b'l', _a[(sock + 1) % 2])
                s.sendto(b'w', _a[sock])
                return 0

if os.geteuid() != 0:
    print("Root like permissions not found, exiting...")
    quit()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 6543))

accepting = True

warned = {}

inGame = []
inGamePacketQueue = {}
gameQueue = {b'0':[]} # , b'1':[], b'2':[] ... to be added later
classDict = {b'0':NormalGame}
gameCount = 0
gameTHRESHOLD = 100

def acceptor():
    while True:
        data, addr = s.recvfrom(2)
        try:
            if (data == b'lg') & (addr in gameQueue[b'0']):
                del gameQueue[b'0'][gameQueue[b'0'].index(addr)]
            elif (addr not in inGame) & (addr not in gameQueue[b'0']) & accepting:
                gameQueue[data].append(addr)
            else:
                inGamePacketQueue[addr] = data
        except:
            if (addr not in inGame) & (addr not in gameQueue[b'0']):
                if addr in warned:
                    warned[addr] += 1
                    s.sendto(b'warning, YOU WILL BE BANNED', addr)
                    print("\033[94m" + addr[0] + " has been warned")
                else:
                    warned[addr] = 1
                    s.sendto(b'warning, YOU WILL BE BANNED', addr)
                    print("\033[94m" + addr[0] + " has been warned")
                if warned[addr] > 2:
                    s.sendto(b'BANNED', addr)
                    os.system("iptables -A INPUT -s " + addr[0] + " -j DROP")
                    print("\033[93m" + addr[0] + " has been BANNED")
                    del warned[addr]

def dispatch():
    while accepting:
        for i in range(len(gameQueue)):
            if len(gameQueue[bytes(str(i), "utf-8")]) > 1:
                threading.Thread(target=classDict[bytes(str(i), "utf-8")], args=(gameQueue[bytes(str(i), "utf-8")][0], gameQueue[bytes(str(i), "utf-8")][1])).start()
                inGame.append(gameQueue[bytes(str(i), "utf-8")][0])
                inGame.append(gameQueue[bytes(str(i), "utf-8")][1])
                inGamePacketQueue[gameQueue[bytes(str(i), "utf-8")][0]] = b''
                inGamePacketQueue[gameQueue[bytes(str(i), "utf-8")][1]] = b''
                del gameQueue[bytes(str(i), "utf-8")][0]
                del gameQueue[bytes(str(i), "utf-8")][0]
        time.sleep(0.01)

threading.Thread(target=acceptor).start()
threading.Thread(target=dispatch).start()
while True:
    shell = input()
    if "e" in shell:
        accepting = False
    if "k" in shell:
        print("\033[91m" + "KILLING SERVER... ")
        accepting = False
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        break
