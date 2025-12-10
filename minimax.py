
import os
import sys
import time
import platform
import random
from math import inf as INF

if os.name == 'nt':
    import msvcrt

    def get_key():
        """Trả về 'UP','DOWN','LEFT','RIGHT','ENTER','QUIT' hoặc ký tự"""
        while True:
            b = msvcrt.getch()
            if b == b'\x00' or b == b'\xe0':  
                b2 = msvcrt.getch()
                codes = {b'H': 'UP', b'P': 'DOWN', b'K': 'LEFT', b'M': 'RIGHT'}
                return codes.get(b2, '')
            elif b == b'\r':
                return 'ENTER'
            elif b == b'\x03':  
                raise KeyboardInterrupt
            else:
                ch = b.decode('utf-8', errors='ignore')
                if ch:
                    return ch.upper()
else:
    import tty
    import termios

    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    codes = {'A': 'UP', 'B': 'DOWN', 'D': 'LEFT', 'C': 'RIGHT'}
                    return codes.get(ch3, '')
                return ''
            if ch == '\r' or ch == '\n':
                return 'ENTER'
            return ch.upper()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def clear():
    if platform.system().lower().startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

CSI = '\x1b['
REV = CSI + '7m'   
RESET = CSI + '0m'


EMPTY = 0
HUMAN = -1
COMP = +1

# hàm tạo bàn cờ
def mk_board(n):
    return [[EMPTY for _ in range(n)] for _ in range(n)]

# hàm hiển thị bần cờ và con trỏ di chuyển
def render(board, cursor=None, blink=True, h_sym='X', c_sym='O'):
    n = len(board)
    now = time.time()
    show = True if not blink else (int(now * 2) % 2 == 0)

    str_line = " " + "-" * (n * 3 + (n - 1))
    
    for i, row in enumerate(board):
        print(str_line)
        line = ""
        for j, cell in enumerate(row):
            if cursor == (i, j) and show:
                if cell == EMPTY:
                    ch = '.'
                else:
                    ch = h_sym if cell == HUMAN else c_sym
                cell_str = f"{REV}{ch}{RESET}"
            else:
                if cell == EMPTY:
                    ch = " "
                else:
                    ch = h_sym if cell == HUMAN else c_sym
                cell_str = ch

            line += f"| {cell_str} "
        line += "|"
        print(line)
    print(str_line)
    print()


def empty_cells(board):
    n = len(board)
    return [(i, j) for i in range(n) for j in range(n) if board[i][j] == EMPTY]

# kiểm tra nước đi có hợp lệ khong
def valid_move(board, x, y):
    n = len(board)
    return 0 <= x < n and 0 <= y < n and board[x][y] == EMPTY


def set_move(board, x, y, player):
    if valid_move(board, x, y):
        board[x][y] = player
        return True
    return False


def in_bounds(n, x, y):
    return 0 <= x < n and 0 <= y < n

def wins(board, player, K):
    n = len(board)
    if K <= 1:
        return False
    dirs = [(0,1),(1,0),(1,1),(-1,1)]
    for i in range(n):
        for j in range(n):
            if board[i][j] != player:
                continue
            for dx, dy in dirs:
                cnt = 1
                x, y = i+dx, j+dy
                while in_bounds(n, x, y) and board[x][y] == player:
                    cnt += 1
                    if cnt >= K:
                        return True
                    x += dx; y += dy
    return False

def game_over(board, K):
    return wins(board, HUMAN, K) or wins(board, COMP, K) or len(empty_cells(board)) == 0

def evaluate(board, K):
    if wins(board, COMP, K):
        return 1000
    if wins(board, HUMAN, K):
        return -1000
    return 0

def minimax(board, depth, player, K, alpha=-INF, beta=INF):
    """
    Minimax có alpha-beta pruning.
    Ưu tiên thắng sớm, thua muộn (tăng điểm theo depth).
    """
    if game_over(board, K) or depth == 0:
        if wins(board, COMP, K):
            return (-1, -1, 1000 + depth)
        elif wins(board, HUMAN, K):
            return (-1, -1, -1000 - depth)
        else:
            return (-1, -1, 0)

    best_move = (-1, -1, -INF) if player == COMP else (-1, -1, INF)

    for (x, y) in empty_cells(board):
        board[x][y] = player
        _, _, score = minimax(board, depth - 1, -player, K, alpha, beta)
        board[x][y] = EMPTY

        if player == COMP:
            if score > best_move[2]:
                best_move = (x, y, score)
            alpha = max(alpha, best_move[2])
        else:
            if score < best_move[2]:
                best_move = (x, y, score)
            beta = min(beta, best_move[2])

        if beta <= alpha:
            break

    return best_move

# hàm kiẻm tra xem có the thang trong 1 nuoc đi khong
def immediate_win_or_block(board, player, K):
    for x,y in empty_cells(board):
        # giả su dat thu nuoc di do là nguoi choi
        board[x][y] = player
        if wins(board, player, K):
            board[x][y] = EMPTY
            return (x,y)
            # nếu không thang tra ve o trong ko có nước đi thắng
        board[x][y] = EMPTY
    return None

# hàm tính điem herisctic ô trong
def heuristic_score_for_cell(board, x, y, player, K):
    """Đếm số chuỗi liên tiếp có thể tạo quanh ô (simple)"""
    n = len(board)
    score = 0
    dirs = [(0,1),(1,0),(1,1),(-1,1)]
    for dx,dy in dirs:
        cnt = 1
        i,j = x+dx, y+dy
        while in_bounds(n,i,j) and board[i][j] == player:
            cnt += 1
            i += dx; j += dy
        i,j = x-dx, y-dy
        while in_bounds(n,i,j) and board[i][j] == player:
            cnt += 1
            i -= dx; j -= dy
        score = max(score, cnt)
    return score

# thuạt toán chọn nước đi nhanh cho máy đánh
def ai_quick_move(board, K):
    # kiểm tra AI có thắng ngay được không --> néu có ưu tien
    mv = immediate_win_or_block(board, COMP, K)
    if mv:
        return mv
#    kiểm tra đối thủ có thể thắng không --> nếu có chặn lại
    mv = immediate_win_or_block(board, HUMAN, K)
    if mv:
        return mv
  
#   tìm herisctic cho các ô trống
    # best danh sách các ô các có diem herictic cao nhat
    best_moves = []
    # khơi tao diem cao nhat
    best_score = -1
    for x,y in empty_cells(board):
        # điem máy vào ô đó
        s = heuristic_score_for_cell(board, x, y, COMP, K)
        s2 = heuristic_score_for_cell(board, x, y, HUMAN, K)
        total = s + s2  
        if total > best_score:
            # ghi nhận ô tôt hien tia
            best_score = total
            best_moves = [(x,y)]
        elif total == best_score:
            best_moves.append((x,y))
    if best_moves:
        return random.choice(best_moves)
    empties = empty_cells(board)
    return random.choice(empties) if empties else (-1,-1)


# hàm tìm nước đi tốt nhất cho máy 
def ai_move(board, K):

    # 1. Máy có thể thắng ngay → ưu tiên
    mv = immediate_win_or_block(board, COMP, K)
    if mv:
        return mv

    # 2. Chặn thắng đối thủ
    mv = immediate_win_or_block(board, HUMAN, K)
    if mv:
        return mv

    # 3. ƯU TIÊN ĐÁNH GIỮA (quan trọng nhất)
    n = len(board)
    cx = cy = n // 2
    if board[cx][cy] == EMPTY:
        return (cx, cy)

    # 4. Nếu bàn nhỏ (3×3 / 4×4) → dùng minimax
    if n <= 4 or (n <= 6 and K <= 3):
        max_depth = min(6, len(empty_cells(board)))
        x, y, _ = minimax(board, max_depth, COMP, K)

        if x == -1 or y == -1:
            empties = empty_cells(board)
            if empties:
                return random.choice(empties)
            return (-1, -1)
        return (x, y)

    # 5. Nếu bàn lớn → dùng quick-move
    return ai_quick_move(board, K)

    
    mv = immediate_win_or_block(board, COMP, K)
    if mv:
        return mv

    
    mv = immediate_win_or_block(board, HUMAN, K)
    if mv:
        return mv

    
    n = len(board)
    if n <= 4 or (n <= 6 and K <= 3):
        max_depth = min(6, len(empty_cells(board))) 
        # gọi hàm minimax để tìm nước đi tối ưu
        x, y, _ = minimax(board, max_depth, COMP, K)
        # nếu if -1 nghĩa là ko tìm đc nuoc toi uu nó trả vê danh sách ban trong và chọn ngau nhien tre nban
        if x == -1 or y == -1:
            empties = empty_cells(board)
            if empties:
                return random.choice(empties)
                # nếu bàn ko còn chỗ tra -1 -1 
            return (-1, -1)
            #  nếu tra ve x , y là hop le máy sẽ đi ô đó
        return (x, y)
    # nếu bàn nhỏ thì nó chuyển sang bàn lớn hơn
    return ai_quick_move(board, K)

def input_initial_state(board):
    clear()
    print("Nhập trạng thái ban đầu (bàn cờ cho sẵn). Gõ 'done' để kết thúc.")
    print("Ví dụ nhập: 0 0 X")
    while True:
        s = input("Nhập: ").strip()
        if s.lower() == 'done' or s == '':
            break
        parts = s.split()
        if len(parts) != 3:
            print("Sai định dạng, thử lại.")
            continue
        try:
            x = int(parts[0]); y = int(parts[1]); ch = parts[2].upper()
            if not in_bounds(len(board), x, y):
                print("Ngoài vùng bàn cờ.")
                continue
            if board[x][y] != EMPTY:
                print("Ô này đã có quân, chọn ô khác.")
                continue
            if ch == 'X':
                board[x][y] = HUMAN
            elif ch == 'O':
                board[x][y] = COMP
            else:
                print("Ký tự chỉ X hoặc O")
        except Exception as e:
            print("Lỗi:", e)

def human_turn_with_cursor(board, K):
    n = len(board)
    empties = empty_cells(board)
    if not empties:
        return
    cx, cy = (n//2, n//2) if board[n//2][n//2] == EMPTY else empties[0]
    while True:
        clear()
        print("Dùng mũi tên hoặc nút W A S D để di chuyển,nhấn Enter để đánh,nhấn Q để thoát.")
        render(board, cursor=(cx,cy), blink=True)
        k = get_key()
        if k in ('UP','W'):
            if cx > 0: cx -= 1
        elif k in ('DOWN','S'):
            if cx < n-1: cx += 1
        elif k in ('LEFT','A'):
            if cy > 0: cy -= 1
        elif k in ('RIGHT','D'):
            if cy < n-1: cy += 1
        elif k == 'ENTER':
            if set_move(board, cx, cy, HUMAN):
                break
            else:
                print("Ô đã bị đánh, bạn hãy chọn ô khác.")
                time.sleep(0.8)
        elif k == 'Q':
            raise KeyboardInterrupt
        else:
            time.sleep(0.05)

def main():
    while True:
        try:
            clear()
            print("TIC-TAC-TOE CỜ CARO")
            while True:
                try:
                    n = int(input("Chọn kích thước bàn (3, 10, 20): ").strip())
                    if n <= 0:
                        print("Vui lòng nhập > 0")
                        continue
                    break
                except:
                    print("Nhập số hợp lệ.")
            while True:
                try:
                    K = int(input("Chọn số ô liên tiếp để thắng (3 ô thắng , 5 ô thắng): ").strip())
                    if K <= 0 or K > n:
                        print("Vui lòng nhập > 0 và <= n")
                        continue
                    break
                except:
                    print("Nhập số hợp lệ.")

            board = mk_board(n)
            ans = ''
            while ans not in ('Y', 'N'):
                ans = input("Bạn có muốn nhập trạng thái ban đầu không? Chọn (Y hoặc N): ").strip().upper()
            if ans == 'Y':
                input_initial_state(board)

            first = ''
            while first not in ('Y', 'N'):
                first = input("Bạn có muốn đi trước không? Chọn (Y hoặc N): ").strip().upper()
            human_first = (first == 'Y')

            # --- vòng chơi ---
            while not game_over(board, K):
                if human_first:
                    human_turn_with_cursor(board, K)
                    if game_over(board, K): break
                    print("Máy nghĩ...")
                    time.sleep(0.5)
                    ax, ay = ai_move(board, K)
                    set_move(board, ax, ay, COMP)
                else:
                    print("Máy đi trước...")
                    time.sleep(0.5)
                    ax, ay = ai_move(board, K)
                    set_move(board, ax, ay, COMP)
                    if game_over(board, K): break
                    human_turn_with_cursor(board, K)

            clear()
            render(board, cursor=None, blink=False)
            if wins(board, HUMAN, K):
                print("Bạn thắng!")
            elif wins(board, COMP, K):
                print("Máy thắng!")
            else:
                print("Trận đấu Hòa rồi.")

            again = input("\nBạn có muốn chơi lại không? Chọn (Y hoặc N): ").strip().upper()
            if again != 'Y':
                print("Cảm ơn bạn đã chơi Tic Tac Toe!")
                break

        except KeyboardInterrupt:
            print("\nThoát chương trình.")
            break

if __name__ == '__main__':
    main()
