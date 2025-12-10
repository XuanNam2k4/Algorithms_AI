import heapq

start = [[5, 2, 1],
         [7, 4, 3],
         [0, 8, 6]]

goal = [[1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]]

def to_tuple(state):
    return tuple(sum(state, []))

def find_pos(state, value):
    for i in range(3):
        for j in range(3):
            if state[i][j] == value:
                return (i, j)

def heuristic_h1(state):
    count = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0 and state[i][j] != goal[i][j]:
                count += 1
    return count

def get_neighbors(state):
    neighbors = []
    i, j = find_pos(state, 0)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in moves:
        x, y = i + dx, j + dy
        if 0 <= x < 3 and 0 <= y < 3:
            new_state = [row[:] for row in state]
            new_state[i][j], new_state[x][y] = new_state[x][y], new_state[i][j]
            neighbors.append(new_state)
    return neighbors

def print_state(state):
    for row in state:
        print(row)
    print()

def a_star(start, heuristic_ham):
    frontier = []
    heapq.heappush(frontier, (heuristic_ham(start), 0, start, []))  
    visited = set()
    i = 0
    while frontier:
        f, g, state, path = heapq.heappop(frontier)

        if to_tuple(state) in visited:
            continue
        visited.add(to_tuple(state))
        i = i + 1
        print(f"Dang duyet trang thai thu {i} voi f={f}, g={g}, h={f - g}:")
        print_state(state)

        if state == goal:
            print("Duong di tu dau den dich:")
            for step in path + [state]:
                print_state(step)
            print(f"Tong so buoc di (g): {g}")
            print(f"Tong so trang thai da duyet: {len(visited)}")
            return

        for neighbor in get_neighbors(state):
            if to_tuple(neighbor) not in visited:
                new_g = g + 1
                h = heuristic_ham(neighbor)
                new_f = new_g + h
                heapq.heappush(frontier, (new_f, new_g, neighbor, path + [state]))

a_star(start, heuristic_h1)

