import random
from collections import deque

CELL = 40  # cell size in pixels

def generate_maze(cols, rows):
    """Recursive backtracker maze generation. Returns 2D grid of walls."""
    visited = [[False]*cols for _ in range(rows)]
    # walls: each cell has [N, S, E, W]
    walls = [[[True,True,True,True] for _ in range(cols)] for _ in range(rows)]
    
    def neighbors(r, c):
        dirs = [(-1,0,0,1),(1,0,1,0),(0,1,2,3),(0,-1,3,2)]  # dr,dc,wall_dir,opp_dir
        result = []
        for dr,dc,wd,od in dirs:
            nr,nc = r+dr,c+dc
            if 0<=nr<rows and 0<=nc<cols and not visited[nr][nc]:
                result.append((nr,nc,wd,od))
        return result

    stack = [(0,0)]
    visited[0][0] = True
    while stack:
        r,c = stack[-1]
        nbrs = neighbors(r,c)
        if nbrs:
            nr,nc,wd,od = random.choice(nbrs)
            walls[r][c][wd] = False
            walls[nr][nc][od] = False
            visited[nr][nc] = True
            stack.append((nr,nc))
        else:
            stack.pop()
    return walls

def solve_bfs(walls, start, end, rows, cols):
    """Finds the shortest path from start (r, c) to end (r, c) using BFS.
    Returns a list of (r, c) tuples representing cell coordinates along the path."""
    if start == end:
        return [start]

    queue = deque([start])
    parent = {start: None}

    # Directions: (dr, dc, wall_index)
    # 0: North (-1, 0), 1: South (1, 0), 2: East (0, 1), 3: West (0, -1)
    dirs = [(-1, 0, 0), (1, 0, 1), (0, 1, 2), (0, -1, 3)]

    while queue:
        r, c = queue.popleft()
        if (r, c) == end:
            break

        for dr, dc, w_idx in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not walls[r][c][w_idx]:  # path is open (no wall)
                    if (nr, nc) not in parent:
                        parent[(nr, nc)] = (r, c)
                        queue.append((nr, nc))

    if end not in parent:
        return []

    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    return path

def cell_rect(r, c, import_pygame=None):
    import pygame
    return pygame.Rect(c*CELL, r*CELL, CELL, CELL)

