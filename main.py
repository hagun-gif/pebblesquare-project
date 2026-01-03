from ursina import *  # 게임엔진 import
import numpy as np
from tensorflow.keras.models import load_model
import threading

model = load_model('C:/Users/Hageon/Desktop/2024_1/engineering/pve_pvp_fin/models/dataset_10000.h5')
app = Ursina()

# 기본 설정
camera.orthographic = True
camera.fov = 960
camera.position = (0, 0)
Text.default_resolution *= 2
mouse.visible = True

# 배경 Entity 만들기
bg = Entity(parent=scene, model='quad', texture="img.jpg", scale=(1900, 1280), z=10, color=color.light_gray)

# 가로세로 길이
w = 15
h = 15

# 오목판 정의
board = [[None for x in range(w)] for y in range(h)]  # 보여지는 오목판 UI
pan = [[0 for x in range(w)] for y in range(h)]  # 보여지지 않는 오목판
per = [[None for x in range(w)] for y in range(h)]

# 오목판 가로 세로 인덱스
eng = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']

# 현재 선택된 위치
current_x, current_y = 7, 7

# 플레이어 설정
player = Entity(name='1', color=color.black)  # 플레이어가 흑(1)->백(2)->흑(1)-> 으로 바뀌면서 플레이됨.

# 방향 및 거리 변수 초기화
direction = ""
move_info = ""

# 문자열 입력 변수
input_text = ""

direction_map = {
    "왼쪽": "Left",
    "오른쪽": "Right",
    "위": "Up",
    "아래": "Down"
}

# 현재 커서 위치 표시를 위한 빨간 점
cursor = None

# 게임 모드
game_mode = None

# create UI
def create_UI():
    global player, board, cursor
    for y in range(h):
        for x in range(w):
            b = Button(parent=scene, text='', radius=0.5, position=(70 * (y - 7), -70 * (x - 7)), scale=(70, 70), color=Color(0, 0, 0, 0))
            board[x][y] = b
    cursor = Entity(parent=scene, model='circle', color=color.red, scale=(10, 10), position=(70 * (current_y - 7), -70 * (current_x - 7)), z=-1)

# 커서 이동
def move_cursor(direction, distance=1):
    global current_x, current_y, cursor

    if direction == "왼쪽":
        current_y = max(0, current_y - distance)
    elif direction == "오른쪽":
        current_y = min(w - 1, current_y + distance)
    elif direction == "위":
        current_x = max(0, current_x - distance)
    elif direction == "아래":
        current_x = min(h - 1, current_x + distance)

    cursor.position = (70 * (current_y - 7), -70 * (current_x - 7))
    cursor.z = -1
    print(f"현재 위치: ({current_x}, {current_y})")

# 착수
def place_stone():
    global player, board, current_x, current_y, pan

    if pan[current_x][current_y] == 0:
        if player.name == '1':
            board[current_x][current_y].text = '1'  # 착수한지점을 1로표시
            board[current_x][current_y].color = color.black  # 착수한 지점에 흑돌표시
            pan[current_x][current_y] = 1
            player.name = '2'  # 다음 차례는 백
            print(f"흑: ({current_x}, {current_y})")

            print('현재 판 상태:')
            read_board_and_debug_on_terminal()  # 판 상태 표시

            check_for_six_black()
            if not connect_six:
                check_for_victory_black()
            check_for_three_three_black(current_x, current_y)
            check_for_four_four_black(current_x, current_y)  # 금수확인

            if not (black_won or connect_six or three_three or four_four):
                if game_mode == 'PVE':
                    read_board_and_put_by_cpu()  # 금수 아니면 AI의 턴
                else:
                    player.name = '2'
        else:
            board[current_x][current_y].text = '2'
            board[current_x][current_y].color = color.white
            pan[current_x][current_y] = 2
            player.name = '1'  # 다음 차례는 흑
            print(f"백: ({current_x}, {current_y})")

            print('현재 판 상태:')
            read_board_and_debug_on_terminal()  # 판 상태 표시

            check_for_six_black()
            if not connect_six:
                check_for_victory_black()
            check_for_three_three_black(current_x, current_y)
            check_for_four_four_black(current_x, current_y)  # 금수확인

            if not (black_won or connect_six or three_three or four_four):
                player.name = '1'
    else:
        print("이미 돌이 놓인 자리입니다. 다른 위치를 선택해 주세요.")

def read_board_and_debug_on_terminal():
    for i in pan:
        print(i)
    print('\n')

def read_board_and_put_by_cpu():
    global per, player
    input_data = pan.copy()
    input_data = np.array(input_data)
    input_data[(input_data != 1) & (input_data != 0)] = -1
    input_data[(input_data == 1) & (input_data != 0)] = 1
    input_data = np.expand_dims(input_data, axis=(0, -1)).astype(np.float32)

    output = model.predict(input_data).squeeze()
    output = output.reshape((w, h))
    output_x, output_y = np.unravel_index(np.argmax(output), output.shape)

    percent = output
    percent = percent.tolist()
    for i in percent:
        for j in i:
            print("{:.10f}".format(j), end=' ')
        print('\n')

    for y in range(h):
        for x in range(w):
            destroy(per[y][x])

    per = [[None for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            p = Entity(parent=scene, model='quad', position=(70 * (y - 7), -70 * (x - 7)), scale=(8, 8), color=Color(1, 0, 0, percent[x][y]))
            per[x][y] = p

    pan[output_x][output_y] = 2
    board[output_x][output_y].text = '2'
    board[output_x][output_y].color = color.white
    board[output_x][output_y].collision = False

    print(f"AI: ({output_x}, {output_y})")
    read_board_and_debug_on_terminal()

    # AI가 돌을 놓은 후 다시 흑의 차례로 설정
    player.name = '1'
    print("흑의 차례입니다.")

# 오목의 승리에 관한 함수들
def check_for_victory_white():
    global player
    player.name = '2'
    name = '2'
    won = False

    for y in range(h):
        for x in range(w):
            try:
                if board[y][x].text == name and board[y + 1][x].text == name and board[y + 2][x].text == name and board[y + 3][x].text == name and board[y + 4][x].text == name:
                    name = player.name
                    won = True
                    break
            except:
                pass

            try:
                if board[y][x].text == name and board[y][x + 1].text == name and board[y][x + 2].text == name and board[y][x + 3].text == name and board[y][x + 4].text == name:
                    name = player.name
                    won = True
                    break
            except:
                pass

            try:
                if board[y][x].text == name and board[y + 1][x + 1].text == name and board[y + 2][x + 2].text == name and board[y + 3][x + 3].text == name and board[y + 4][x + 4].text == name:
                    name = player.name
                    won = True
                    break
            except:
                pass

            try:
                if x >= 4 and board[y][x].text == name and board[y + 1][x - 1].text == name and board[y + 2][x - 2].text == name and board[y + 3][x - 3].text == name and board[y + 4][x - 4].text == name:
                    name = player.name
                    won = True
                    break

            except:
                pass

        if won:
            break

    if won:
        create_win_UI()

def check_for_victory_black():
    name = '1'
    global black_won
    black_won = False

    for y in range(h):
        for x in range(w):
            try:
                if board[y][x].text == name and board[y + 1][x].text == name and board[y + 2][x].text == name and board[y + 3][x].text == name and board[y + 4][x].text == name:
                    name = player.name
                    black_won = True
                    break
            except:
                pass

            try:
                if board[y][x].text == name and board[y][x + 1].text == name and board[y][x + 2].text == name and board[y][x + 3].text == name and board[y][x + 4].text == name:
                    name = player.name
                    black_won = True
                    break
            except:
                pass

            try:
                if board[y][x].text == name and board[y + 1][x + 1].text == name and board[y + 2][x + 2].text == name and board[y + 3][x + 3].text == name and board[y + 4][x + 4].text == name:
                    name = player.name
                    black_won = True
                    break
            except:
                pass

            try:
                if x >= 4 and board[y][x].text == name and board[y + 1][x - 1].text == name and board[y + 2][x - 2].text == name and board[y + 3][x - 3].text == name and board[y + 4][x - 4].text == name:
                    name = player.name
                    black_won = True
                    break

            except:
                pass

        if black_won:
            break

    if black_won:
        create_win_UI()

############### 오목의 금수에 관한 함수들 #######################

def check_for_three_three_black(x_on, y_on):
    global three_three
    three_three = False
    open_three = 0
    x = x_on
    y = y_on
    direction_vector = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
    direction_vector_half = [[0, 1], [1, 1], [1, 0], [1, -1]]

    for i, j in direction_vector:
        try:
            # 열린3 N*@@N -> ^N*@@N^
            if pan[x - 2 * i][y - 2 * j] != 1 and pan[x - 1 * i][y - 1 * j] == 0 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 0 and pan[x + 4 * i][y + 4 * j] != 1:
                open_three += 1
            # 열린3 N@*N@N
            if pan[x - 2 * i][y - 2 * j] == 0 and pan[x - 1 * i][y - 1 * j] == 1 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 0 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 0:
                open_three += 1
            # 열린3 N*N@@N
            if pan[x - 1 * i][y - 1 * j] == 0 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 0 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 1 and pan[x + 4 * i][y + 4 * j] == 0:
                open_three += 1
            # 열린3 N*@N@N
            if pan[x - 1 * i][y - 1 * j] == 0 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 1 and pan[x + 4 * i][y + 4 * j] == 0:
                open_three += 1
        except:
            pass

    for i, j in direction_vector_half:
        try:
            # 열린3 N@*@N
            if pan[x - 3 * i][y - 3 * j] != 1 and pan[x - 2 * i][y - 2 * j] == 0 and pan[x - 1 * i][y - 1 * j] == 1 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 0 and pan[x + 3 * i][y + 3 * j] != 1:
                open_three += 1
        except:
            pass

    if open_three >= 2:
        three_three = True
        create_ban_UI()

def check_for_four_four_black(x_on, y_on):
    global four_four
    four_four = False
    four = 0
    x = x_on
    y = y_on

    direction_vector = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

    for i, j in direction_vector:
        try:
            # 열린4 N*@@@N / 닫힌4 N*@@@O O*@@@N
            if pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 1:
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 2 and pan[x + 4 * i][y + 4 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 2:
                    four += 1
            # 0[1]01110
            if pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 0 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 1 and pan[x + 4 * i][y + 4 * j] == 1:
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 5 * i][y + 5 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 2 and pan[x + 5 * i][y + 5 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 5 * i][y + 5 * j] == 2:
                    four += 1
            # 0[1]10110
            if pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 1 and pan[x + 4 * i][y + 4 * j] == 1:
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 5 * i][y + 5 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 2 and pan[x + 5 * i][y + 5 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 5 * i][y + 5 * j] == 2:
                    four += 1
            # 0[1]11010
            if pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 1:
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 5 * i][y + 5 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 2 and pan[x + 5 * i][y + 5 * j] == 0:
                    four += 1
                if pan[x - 1 * i][y - 1 * j] == 0 and pan[x + 5 * i][y + 5 * j] == 2:
                    four += 1
            # 01[1]110
            if pan[x - 1 * i][y - 1 * j] == 1 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 1:
                if pan[x - 2 * i][y - 2 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 0:
                    four += 1
                if pan[x - 2 * i][y - 2 * j] == 2 and pan[x + 3 * i][y + 3 * j] == 0:
                    four += 1
                if pan[x - 2 * i][y - 2 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 2:
                    four += 1
            # 01[1]0110
            if pan[x - 1 * i][y - 1 * j] == 1 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 0 and pan[x + 2 * i][y + 2 * j] == 1 and pan[x + 3 * i][y + 3 * j] == 1:
                if pan[x - 2 * i][y - 2 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 0:
                    four += 1
                if pan[x - 2 * i][y - 2 * j] == 2 and pan[x + 4 * i][y + 4 * j] == 0:
                    four += 1
                if pan[x - 2 * i][y - 2 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 2:
                    four += 1
            # 01[1]1010
            if pan[x - 1 * i][y - 1 * j] == 1 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 1:
                if pan[x - 2 * i][y - 2 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 0:
                    four += 1
                if pan[x - 2 * i][y - 2 * j] == 2 and pan[x + 4 * i][y + 4 * j] == 0:
                    four += 1
                if pan[x - 2 * i][y - 2 * j] == 0 and pan[x + 4 * i][y + 4 * j] == 2:
                    four += 1
            # 010[1]110
            if pan[x - 2 * i][y - 2 * j] == 1 and pan[x - 1 * i][y - 1 * j] == 0 and pan[x][y] == 1 and pan[x + 1 * i][y + 1 * j] == 1 and pan[x + 2 * i][y + 2 * j] == 1:
                if pan[x - 3 * i][y - 3 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 0:
                    four += 1
                if pan[x - 3 * i][y - 3 * j] == 2 and pan[x + 3 * i][y + 3 * j] == 0:
                    four += 1
                if pan[x - 3 * i][y - 3 * j] == 0 and pan[x + 3 * i][y + 3 * j] == 2:
                    four += 1
        except:
            pass

    if four >= 2:
        four_four = True
        create_ban_UI()

def check_for_six_black():
    global connect_six
    connect_six = False

    for y in range(h):
        for x in range(w):
            try:
                if board[y][x].text == board[y + 1][x].text == board[y + 2][x].text == board[y + 3][x].text == board[y + 4][x].text == board[y + 5][x].text == '1':
                    connect_six = True
                    break
            except:
                pass

            try:
                if board[y][x].text == board[y][x + 1].text == board[y][x + 2].text == board[y][x + 3].text == board[y][x + 4].text == board[y + 5][x + 5].text == '1':
                    connect_six = True
                    break
            except:
                pass

            try:
                if board[y][x].text == board[y + 1][x + 1].text == board[y + 2][x + 2].text == board[y + 3][x + 3].text == board[y + 4][x + 4].text == board[y + 5][x + 5].text == '1':
                    connect_six = True
                    break
            except:
                pass

            try:
                if x >= 5 and board[y][x].text == board[y + 1][x - 1].text == board[y + 2][x - 2].text == board[y + 3][x - 3].text == board[y + 4][x - 4].text == board[y + 5][x - 5].text == '1':
                    connect_six = True
                    break
            except:
                pass
        if connect_six:
            break

    if connect_six:
        create_ban_UI()

def delete_and_create_all_UI():
    global player, board, pan
    #밀기
    for y in range(h):
        for x in range(w):
            destroy(board[y][x])
    destroy(t)
    destroy(p)
    destroy(b_exit)
    destroy(b_replay)

    #재정의
    player = Entity(name='1', color=color.black) 
    board = [[None for x in range(w)] for y in range(h)]
    pan = [[ 0 for x in range(w)] for y in range(h)]
    create_UI()

def delete_and_create_board_UI():
    global board
    global pan
    pan[x_on][y_on] = 0
    destroy(board[x_on][y_on])
    b = Button(parent=scene, radius=0.5, position=(70*(y_on-7),-70*(x_on-7)), scale=(70,70), color=Color(0, 0, 0, 0))
    board[x_on][y_on] = b

# 승리 UI 생성 함수
def create_win_UI():
    name = player.name
    p = Panel(z=1, scale=10, model='quad')
    b_exit = Button(text='exit', color=color.azure, scale=(0.05, 0.03), text_origin=(0, 0), position=(-0.05, -0.1))
    b_exit.on_click = application.quit  # 종료
    b_exit.tooltip = 'exit'  # Tooltip 제거
    b_replay = Button(text='replay', color=color.azure, scale=(0.08, 0.03), text_origin=(0, 0), position=(0.05, -0.1))
    b_replay.on_click = delete_and_create_all_UI  # 재시작
    b_replay.tooltip = 'replay'  # Tooltip 제거
    t = Text(f'Player{name}\n  won!', scale=3, origin=(0, 0), background=True)
    t.create_background(padding=(.5, .25), radius=Text.size / 2)
    t.background.color = player.color.tint(-.2)
    print('winner is:', name)

# Input Handling:
def handle_input():
    global current_x, current_y, player
    while True:
        direction = input("입력: ").split()
        if len(direction) == 2 and direction[0] in ["왼쪽", "오른쪽", "위", "아래"] and direction[1].isdigit():
            move_cursor(direction[0], int(direction[1]))
        elif direction[0] in ["왼쪽", "오른쪽", "위", "아래"]:
            move_cursor(direction[0])
        elif direction[0] == "확인":
            place_stone()
        else:
            print("잘못된 입력입니다. 다시 입력해 주세요.")

# 스레드로 입력 핸들링
input_thread = threading.Thread(target=handle_input)
input_thread.daemon = True
input_thread.start()

# 메뉴 생성
def set_pvp():
    global game_mode
    game_mode = 'PVP'
    print("PVP 모드 선택됨")
    create_UI()  # PVP용 UI 생성
    pvp_button.disable()  # pvp_button 비활성화
    ai_button.disable()  # pve_button 비활성화

def set_ai():
    global game_mode
    game_mode = 'PVE'
    print("PVE 모드 선택됨")
    create_UI()  # AI용 UI 생성
    pvp_button.disable()  # pvp_button 비활성화
    ai_button.disable()  # pve_button 비활성화

# UI 요소 생성
pvp_button = Button(text="PVP 모드", color=color.black, scale=(0.2, 0.1), on_click=set_pvp)
ai_button = Button(text="PVE 모드", color=color.black, scale=(0.2, 0.1), on_click=set_ai)

# UI 배치
pvp_button.x = 0.3
ai_button.x = -0.3

if __name__ == '__main__':
    app.run()
