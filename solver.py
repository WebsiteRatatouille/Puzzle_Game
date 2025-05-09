import time
import heapq
from collections import deque
import numpy as np

MAX_SEARCH_TIME = 1.0

def is_solvable(board):
    flat = board.flatten()
    inv = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] and flat[j] and flat[i] > flat[j]:
                inv += 1
    return inv % 2 == 0

def get_solution_path(state):
    path = []
    while state.parent is not None:
        path.append(state.move)
        state = state.parent
    return path[::-1]

def solve_bfs(initial_state):
    start = time.time()
    visited = set()
    queue = deque([initial_state])
    while queue and time.time() - start < MAX_SEARCH_TIME:
        state = queue.popleft()
        if state.cost == 0:
            return get_solution_path(state)
        if state in visited:
            continue
        visited.add(state)
        for next_pos in state.get_possible_moves():
            new_state = state.get_new_state(next_pos)
            if new_state not in visited:
                queue.append(new_state)
    return None

def solve_astar(initial_state):
    start_time = time.time()
    visited = {}
    heap = []
    count = 0
    heapq.heappush(heap, (initial_state.cost + initial_state.depth, count, initial_state))

    while heap and time.time() - start_time < MAX_SEARCH_TIME:
        _, _, state = heapq.heappop(heap)

        if state.cost == 0:
            return get_solution_path(state)

        state_hash = state.hash
        if state_hash in visited and visited[state_hash] <= state.depth:
            continue
        visited[state_hash] = state.depth

        for move in state.get_possible_moves():
            new_state = state.get_new_state(move)
            new_hash = new_state.hash
            if new_hash not in visited or new_state.depth < visited[new_hash]:
                count += 1
                heapq.heappush(heap, (new_state.cost + new_state.depth, count, new_state))
    return None