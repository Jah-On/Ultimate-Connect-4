from dearpygui.core import *
import time
import math
import socket
import threading
import numpy

ADDR = ('dpg-games.duckdns.org', 6543)
running = True
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inGame = False
staringTurn = 0

class NonNegativeNumpyIndex:
    def __init__(self, numpyArray):
        self.array = numpyArray
    def __call__(self, rowOrSearchVal = None, col = None, value = None):
        # print("A")
        if (value != None):
            self.array[rowOrSearchVal][col] = value
        elif (col != None):
            if ((rowOrSearchVal < 0) | (col < 0)):
                raise Exception("IndexOutOfBounds: No negative numbers permitted.")
            else:
                return self.array[rowOrSearchVal][col]
        else:
            return (self.array == rowOrSearchVal).sum()

def gameExit():
    global running
    running = False
    if inGame:
        try:
            s.sendto(b'lg', ADDR)
            s.shutdown(socket.SHUT_RDWR)
        except:
            pass

def twoOffline():
    global map
    map = NonNegativeNumpyIndex(numpy.full(shape=(6,7), fill_value=-1))
    set_resize_callback(NormalBoardResize, handler="##base")
    configure_item("##cM", show=False)
    add_group("gameScreen", parent="##base")
    size = (math.floor(get_item_rect_size("##base")[0] / 7)-6, math.floor(get_item_rect_size("##base")[1] / 6)-3)
    for r in range(0,6):
        for c in range(0,7):
            add_button("##" + str(r) + str(c), width=size[0], height=size[1], callback=onTwoOfflineGameSpotClick)
            set_item_color("##" + str(r) + str(c), 21, [200,200,200])
            set_item_color("##" + str(r) + str(c), 22, [190,190,190])
            set_item_color("##" + str(r) + str(c), 23, [190,190,190])
            if c != 6:
                add_same_line()
    end()
    global staringTurn
    staringTurn = (staringTurn + 1) % 2
    global turn
    turn = staringTurn
    set_main_window_title("Player " + str(turn + 1) +"\'s turn...")
    stop = False
    while True:
        tempTurn = turn
        while tempTurn == turn:
            time.sleep(0.008)
        for r in range(0, 6):
            for c in range(0,7):
                if map(r,c) != -1:
                    try:
                        if (map(r,c) == map(r + 1,c) == map(r + 2,c) == map(r + 3,c)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r - 1,c) == map(r - 2,c) == map(r - 3,c)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r,c + 1) == map(r,c + 2) == map(r,c + 3)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r,c - 1) == map(r,c - 2) == map(r,c - 3)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r + 1,c + 1) == map(r + 2,c + 2) == map(r + 3,c + 3)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r + 1,c - 1) == map(r + 2,c - 2) == map(r + 3,c - 3)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r - 1,c - 1) == map(r - 2,c - 2) == map(r - 3,c - 3)):
                            stop = True
                            break
                    except:
                        pass
                    try:
                        if (map(r,c) == map(r - 1,c + 1) == map(r - 2,c + 2) == map(r - 3,c + 3)):
                            stop = True
                            break
                    except:
                        pass
                    if (map(-1) == 0):
                        stop = True
                        add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
                        add_text("It\'s a draw!")
                        add_button("Home", callback=reset)
                        end()
                        return 0
                if stop:
                    break
            if stop:
                for r in range(0,6):
                    for c in range(0,7):
                        if get_item_callback("##" + str(r) + str(c)) != None:
                            set_item_color("##" + str(r) + str(c), 21, [200,200,200])
                            set_item_color("##" + str(r) + str(c), 22, [200,200,200])
                            set_item_color("##" + str(r) + str(c), 23, [200,200,200])
                        set_item_callback("##" + str(r) + str(c), None)
                add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
                add_text("Player " + str(turn + 1) + " won!")
                add_button("Home", callback=reset)
                end()
                return 0

def NormalGameScreen():
    global inGame
    inGame = True
    global map
    map = numpy.full(shape=(6,7), fill_value=-1)
    configure_item("##cM", show=False)
    set_main_window_title("Waiting in queue...")
    try:
        s.connect(ADDR)
        s.sendto(b'0', ADDR)
        global player
        player = s.recvfrom(1)
    except:
        add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
        add_text("Server down or unreachable. Please check \nhttps://github.com/Jah-On/Ultimate-Connect-4 \nfor updates.")
        add_button("Home", callback=reset)
        end()
        return 0
    while (len(player[0]) == 0):
        player = s.recvfrom(1)
        time.sleep(0.01)
    global color
    if player[0] == b'0':
        color = [255,0,0]
        oColor = [0,0,255]
        oPone = 1
    else:
        color = [0,0,255]
        oColor = [255,0,0]
        oPone = 0
    while not does_item_exist("##base") or not is_dearpygui_running():
        time.sleep(0.004)
    time.sleep(1)
    set_resize_callback(NormalBoardResize, handler="##base")
    add_group("gameScreen", parent="##base")
    size = (math.floor(get_item_rect_size("##base")[0] / 7)-6, math.floor(get_item_rect_size("##base")[1] / 6)-3)
    for r in range(0,6):
        for c in range(0,7):
            add_button("##" + str(r) + str(c), width=size[0], height=size[1], callback=onNormalGameSpotClick)
            set_item_color("##" + str(r) + str(c), 21, [200,200,200])
            set_item_color("##" + str(r) + str(c), 22, [190,190,190])
            set_item_color("##" + str(r) + str(c), 23, color)
            if c != 6:
                add_same_line()
    end()
    if player[0] == b'0':
        add_window("##noClick", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_background=True, no_move=True, x_pos=0, y_pos=0, width=int(get_item_rect_size("##base")[0])-1, height=int(get_item_rect_size("##base")[1])-1, show=False)
        set_main_window_title("Your turn...")
    else:
        add_window("##noClick", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_background=True, no_move=True, x_pos=0, y_pos=0, width=int(get_item_rect_size("##base")[0])-1, height=int(get_item_rect_size("##base")[1])-1, show=True)
        set_main_window_title("Opponent's turn...")
    end()
    while running:
        op = s.recvfrom(2)
        while (len(op[0]) == 0) & running:
            time.sleep(0.001)
            op = s.recvfrom(2)
        if not running:
            return -1
        if op[0] == b'lg':
            inGame = False
            configure_item("##noClick", show=True)
            add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
            add_text("Opponent left.")
            add_button("Home", callback=reset)
            end()
            configure_item("##noClick", no_bring_to_front_on_focus=True)
            return 0
        if op[0] == b'w':
            inGame = False
            configure_item("##noClick", show=True)
            add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
            add_text("You won!")
            add_button("Home", callback=reset)
            end()
            configure_item("##noClick", no_bring_to_front_on_focus=True)
            return 0
        if op[0] == b'l':
            inGame = False
            configure_item("##noClick", show=True)
            add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
            add_text("Player " + str(oPone + 1) + " won!")
            add_button("Home", callback=reset)
            end()
            configure_item("##noClick", no_bring_to_front_on_focus=True)
            return 0
        if op[0] == b'd':
            inGame = False
            configure_item("##noClick", show=True)
            add_window("##end", no_close=True, no_collapse=True, no_title_bar=True,no_resize=True, no_move=True, x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)), width=int(get_item_rect_size("##base")[0] * 0.3), height=int(get_item_rect_size("##base")[1] * 0.3))
            add_text("It\'s a draw!")
            add_button("Home", callback=reset)
            end()
            configure_item("##noClick", no_bring_to_front_on_focus=True)
            return 0
        op = op[0].decode()
        map[int(op[0])][int(op[1])] = oPone
        set_item_color("##" + str(op), 21, oColor)
        set_item_color("##" + str(op), 22, oColor)
        set_item_color("##" + str(op), 23, oColor)
        set_item_callback("##" + str(op), None)
        configure_item("##noClick", show=False)
        set_main_window_title("Your turn...")

def reset():
    set_main_window_title("Ultimate Connect Four")
    try:
        delete_item("gameScreen")
        delete_item("##noClick")
    except:
        pass
    delete_item("##end")
    configure_item("##cM", show=True)

def onNormalGameSpotClick(sender, data):
    row = int(sender[2])
    col = int(sender[3])
    for attempt in range(row, 6):
        try:
            if map[attempt + 1][col] != -1:
                row = attempt
                break
        except:
            row = 5
    configure_item("##noClick", show=True)
    set_main_window_title("Opponent's turn...")
    set_item_color("##" + str(row) + str(col), 21, color)
    set_item_color("##" + str(row) + str(col), 22, color)
    set_item_color("##" + str(row) + str(col), 23, color)
    set_item_callback("##" + str(row) + str(col), None)
    map[row][col] = int(player[0])
    s.sendto(bytes(str(row) + str(col), "utf-8"), ADDR)

def onTwoOfflineGameSpotClick(sender, data):
    global turn
    color = {0:[255,0,0], 1:[0,0,255]}
    row = int(sender[2])
    col = int(sender[3])
    for attempt in range(row, 6):
        try:
            if map(attempt + 1,col) != -1:
                row = attempt
                break
        except:
            row = 5
    set_item_color("##" + str(row) + str(col), 21, color[turn])
    set_item_color("##" + str(row) + str(col), 22, color[turn])
    set_item_color("##" + str(row) + str(col), 23, color[turn])
    set_item_callback("##" + str(row) + str(col), None)
    map(row, col, turn)
    turn = (turn + 1) % 2
    time.sleep(0.008)
    set_main_window_title("Player " + str(turn + 1) +"\'s turn...")

def NormalBoardResize():
    size = (math.floor(get_item_rect_size("##base")[0] / 7)-6, math.floor(get_item_rect_size("##base")[1] / 6)-3)
    for r in range(0,6):
        for c in range(0,7):
            configure_item("##" + str(r) + str(c), width=size[0])
            configure_item("##" + str(r) + str(c), height=size[1])

# To be reused later
def homeScreenResize():
    pass
    # configure_item("##cM", x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.2)/2)))
    # configure_item("##cM", y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[0] * 0.2)/2)))
    # configure_item("##cM", width=int(get_item_rect_size("##base")[0] * 0.2))
    # configure_item("##cM", height=int(get_item_rect_size("##base")[0] * 0.2))
    # configure_item("Classic multiplayer", width=int(get_item_rect_size("##base")[0] * 0.2))
    # configure_item("Classic multiplayer", height=int(get_item_rect_size("##base")[0] * 0.2))

def spawner(sender, data):
    if data == 2:
        threading.Thread(target=NormalGameScreen).start()
    elif data == 1:
        threading.Thread(target=twoOffline).start()

set_main_window_title("Ultimate Connect Four")
set_style_window_border_size(0.0)
set_style_window_padding(0,0)
set_vsync(True)
add_window("##base")
set_resize_callback(homeScreenResize, handler="##base")
# x_pos=int((get_item_rect_size("##base")[0] / 2) - ((get_item_rect_size("##base")[0] * 0.3)/2)), y_pos=int((get_item_rect_size("##base")[1] / 2) - ((get_item_rect_size("##base")[1] * 0.3)/2)),
set_exit_callback(gameExit)
end()
add_group("##cM", parent="##base")
add_button("Offline PvP", callback=spawner, callback_data=1, width=300, height=300)
add_same_line()
add_button("Classic multiplayer", callback=spawner, callback_data=2, width=300, height=300)
end()

if __name__ == "__main__":
    start_dearpygui(primary_window="##base")
