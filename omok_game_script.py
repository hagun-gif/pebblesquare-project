import pygame
import sys
import threading

# 초기화
pygame.init()

# 상수 정의
SCREEN_SIZE = 600
GRID_SIZE = 19
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
SCREEN = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("오목 PVP")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOARD_COLOR = (245, 222, 179)
RED = (255, 0, 0)

# 게임 보드 초기화
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# 플레이어 정의
player = 1

# 폰트 설정
font = pygame.font.Font(None, 36)

# 빨간 박스 초기 위치
red_box_pos = [GRID_SIZE // 2, GRID_SIZE // 2]

# 방향 및 거리 변수 초기화
direction = ""
distance = 0
move_info = ""

# 문자열 입력 변수
input_text = ""

direction_map = {
    "왼쪽": "Left",
    "오른쪽": "Right",
    "위": "Up",
    "아래": "Down"
}

distance_map = {
    "하나": 1, "한": 1,
    "둘": 2, "두": 2,
    "셋": 3, "세": 3,
    "넷": 4, "네": 4, "대": 4, "데": 4, "넥": 4,
    "다섯": 5, "다서": 5,
    "여섯": 6, "유서": 6, "유섯": 6,
    "일곱": 7, "열고": 7, "외국": 7,
    "여덟": 8,
    "아홉": 9
}

def draw_board():
    SCREEN.fill(BOARD_COLOR)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(SCREEN, BLACK, rect, 1)
            if board[y][x] == 1:
                pygame.draw.circle(SCREEN, BLACK, rect.center, CELL_SIZE // 2 - 2)
            elif board[y][x] == 2:
                pygame.draw.circle(SCREEN, WHITE, rect.center, CELL_SIZE // 2 - 2)
    # 빨간 박스 그리기
    red_box_rect = pygame.Rect(red_box_pos[0] * CELL_SIZE, red_box_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(SCREEN, RED, red_box_rect, 3)
    
    # 이동 정보 표시
    info_text = font.render(move_info, True, BLACK)
    SCREEN.blit(info_text, (10, SCREEN_SIZE - 40))

def check_winner():
    # 가로, 세로, 대각선 확인
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if board[y][x] != 0:
                # 가로 확인
                if x <= GRID_SIZE - 5 and all(board[y][x + i] == board[y][x] for i in range(5)):
                    return board[y][x]
                # 세로 확인
                if y <= GRID_SIZE - 5 and all(board[y + i][x] == board[y][x] for i in range(5)):
                    return board[y][x]
                # 대각선 확인 (\)
                if x <= GRID_SIZE - 5 and y <= GRID_SIZE - 5 and all(board[y + i][x + i] == board[y][x] for i in range(5)):
                    return board[y][x]
                # 대각선 확인 (/)
                if x >= 4 and y <= GRID_SIZE - 5 and all(board[y + i][x - i] == board[y][x] for i in range(5)):
                    return board[y][x]
    return 0

def display_winner(winner):
    if winner == 1:
        text = font.render("Black wins!", True, BLACK)
    elif winner == 2:
        text = font.render("White wins!", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2))
    pygame.draw.rect(SCREEN, BOARD_COLOR, text_rect.inflate(20, 20))
    SCREEN.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(3000)

def move_red_box(direction, distance):
    global red_box_pos, move_info
    if direction == "왼쪽":
        red_box_pos[0] = max(0, red_box_pos[0] - distance)
    elif direction == "오른쪽":
        red_box_pos[0] = min(GRID_SIZE - 1, red_box_pos[0] + distance)
    elif direction == "위":
        red_box_pos[1] = max(0, red_box_pos[1] - distance)
    elif direction == "아래":
        red_box_pos[1] = min(GRID_SIZE - 1, red_box_pos[1] + distance)
    move_info = f"{direction_map[direction]} {distance}"

# 문자열 필터링 함수
def filter_input(input_str):
    global direction, distance, player, board, red_box_pos
    directions = ["왼쪽", "오른쪽", "위", "아래"]
    distances = distance_map.keys()
    
    if "확인" in input_str:
        x, y = red_box_pos
        if board[y][x] == 0:
            board[y][x] = player
            winner = check_winner()
            if winner:
                draw_board()
                pygame.display.update()
                display_winner(winner)
                board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            player = 3 - player
        return

    for word in input_str.split():
        for dir in directions:
            if dir in word:
                direction = dir
                print(f"Direction: {direction}")
                break
        for dist in distances:
            if dist in word:
                distance = distance_map[dist]
                print(f"Distance: {distance}")
                break
    
    if direction and distance:
        move_red_box(direction, distance)
        direction = ""
        distance = 0

def handle_terminal_input():
    global input_text
    while True:
        input_text = input("입력: ")
        filter_input(input_text)

# 별도의 스레드에서 터미널 입력 처리
input_thread = threading.Thread(target=handle_terminal_input)
input_thread.daemon = True
input_thread.start()

# 게임 루프
running = True
while running:
    draw_board()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
