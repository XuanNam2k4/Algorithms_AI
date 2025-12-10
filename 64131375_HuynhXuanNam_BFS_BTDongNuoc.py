from collections import deque
# hàm này là sinh các trạng thái kế tiếp
# mỗi trạng thái biểu diễn 1 tuple với 2 bình nước x của a và y là b
#state là trạng thái của 2 bình nước
def get_next_states(state):
    x, y = state
    states = []

    states.append((7, y))
    states.append((x, 5))

    states.append((0, y))
    states.append((x, 0))

    # số lượng nước trống trong bình y
    pourAmount  = min(x, 5 - y)
    states.append((x - pourAmount, y + pourAmount))

    pourAmount  = min(y, 7 - x)
    states.append((x + pourAmount, y - pourAmount))

    return states


def bfsSearch():
    start = (0, 0)
    openStates = deque([(start, [])])
    closedStates = set([start])
    TARGET = 6
    count = 0
    all = []
# hàng đợi các trạng thái cần được duyệt
    while openStates:
        (x, y), path = openStates.popleft()
        count += 1
        all.append((x,y))
        
        if x == TARGET:
            return path + [(x, y)], count,all

        for next_state in get_next_states((x, y)):
            if next_state not in closedStates:
                closedStates.add(next_state)
                openStates.append((next_state, path + [(x, y)]))

    return None, count,all


solution, numStates,all = bfsSearch()
if solution:
    print("Các bước chuyển trạng thái để đạt được 6 lít trong bình 7 lít:")
    for step in solution:
        print(step)
    print("Tổng số trạng thái đã duyệt:", numStates)
    for st in all:
        print(st)
else:
    print("Không tìm thấy lời giải")
