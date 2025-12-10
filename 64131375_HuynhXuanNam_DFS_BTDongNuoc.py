#có 6 trạng thái mới sinh ra
def get_next_states(state):
    x, y = state
    states = []
    states.append((7, y))
    states.append((x, 5))

    states.append((0, y))
    states.append((x, 0))

    pourAmount = min(x, 5 - y)
    states.append((x - pourAmount, y + pourAmount))

    pourAmount = min(y, 7 - x)
    states.append((x + pourAmount, y - pourAmount))

    return states

def dfs_search(target=6):
    start = (0, 0) 
    stack = [(start, [])] #khởi động với stack có 1 nút đầu tiên (nơi lưu các nút chứa trạng thái để xét)
    visited = set([start]) # tập hợp các nút đã xét trong không gian trạng thái

    while stack:
        (x, y), path = stack.pop()

        if x == target:
            solution = path + [(x, y)]
            return solution, len(solution)

        for next_state in get_next_states((x, y)):
            if next_state not in visited:
                visited.add(next_state)
                stack.append((next_state, path + [(x, y)]))
    return None, 0


solution, numStates = dfs_search(target=6)
if solution:
    print("Các bước chuyển trạng thái (DFS) để đạt được 6 lít trong bình 7 lít:")
    for step in solution:
        print(step)
    print("Tổng số nút đã từng ghé thăm:", numStates) 
else:
    print("Không tìm thấy lời giải")


