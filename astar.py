import json
from queue import PriorityQueue
import pygame
from shapely.geometry import box, Point
from typing import List, Tuple, Dict

class Spot:
    def __init__(self, row, col, width, height, total_rows, total_columns):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * height
        self.state = 'default'
        self.neighbors = []
        self.width = width
        self.height = height
        self.total_rows = total_rows
        self.total_columns = total_columns

    def draw(self, win):
        if self.is_barrier():
            pygame.draw.rect(win, (0, 0, 0), pygame.Rect(self.x, self.y + 100, self.width, self.height))
        if self.state == 'path':
            pygame.draw.rect(win, (128, 0, 128), pygame.Rect(self.x, self.y + 100, self.width, self.height))

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self):
        return self.state == 'barrier'

    def reset(self):
        self.state = 'default'

    def make_closed(self):
        self.state = 'closed'

    def make_open(self):
        self.state = 'open'

    def make_barrier(self):
        self.state = 'barrier'

    def make_end(self):
        self.state = 'end'

    def make_path(self):
        self.state = 'path'

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_columns - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)
    # Returns manhattan distance between 2 points


def reconstruct_path(came_from: Dict, current: Spot):
    # Backtracks the path created and draws it
    path_list = []
    while current in came_from:
        path_list.insert(0, (current.x, current.y))
        current.make_path()
        current = came_from[current]

    return path_list


def draw_path(win, grid):

    for row in grid:
        for spot in row:
            if spot.state == 'path':
                spot.draw(win)

    pygame.display.update()


def algorithm(grid: List, start: Spot, end: Spot):
    count = 0
    open_set = PriorityQueue()  # Initialize priority queue
    open_set.put((0, count, start))  # Put in start values
    came_from = {}
    # Fill in the rest with infinity
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    # Initiate while loop
    while not open_set.empty():

        current = open_set.get()[2]
        # Get current spot
        open_set_hash.remove(current)

        # Check if we found the target spot
        if current == end:
            return reconstruct_path(came_from, end)

        # Update neighbor's g_scores
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            # If the new g score is more efficient
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                # Update g score
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                # Make sure we don't go over the same spot twice
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        if current != start:
            current.make_closed()

    # Return empty list if no path was found
    return []


def create_block(x1: int, y1: int, x2: int, y2: int, block_boxes: List) -> None:
    # Make sure x2 and y2 are the greater values
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))

    # Initialize necessary variables
    block_box = box(x1 + 1, y1 + 1, x2 - 1, y2 - 1)  # Create slightly smaller box to eliminate false collisions

    block_boxes.append(block_box)  # Append new block to total block list


def create_map_from_file(filename: str) -> List:
    with open(filename, 'r') as f:  # Open file in reading mode
        file_block_list = json.load(f)  # Load file info with json
        block_boxes = []
        for item in file_block_list:  # Loop over all blocks
            create_block(item[0], item[1], item[2], item[3], block_boxes)  # Create block from file info
        f.close()  # Close the file
    return block_boxes


def create_grid_from_file(filename: str, width: int, rows: int, columns: int):
    block_boxes = create_map_from_file(filename)
    # Get block boxes from map

    grid = []  # Create empty grid
    gap = width // columns
    for i in range(rows):  # Loop over rows
        grid.append([])
        for j in range(columns):  # Loop over columns
            spot = Spot(i, j, gap, gap, rows, columns)
            # Create new spot
            spot_box = box(spot.x, spot.y, spot.x + spot.width, spot.y + spot.height)
            # Calculate shapely box

            # Check if spot is a barrier
            for block_box in block_boxes:
                if spot_box.intersects(block_box):
                    spot.make_barrier()

            # Add spot to grid
            grid[i].append(spot)

    for row in grid:
        for spot in row:
            spot.update_neighbors(grid)

    return grid


def coords_to_spot(grid, coordinates):
    a, b = coordinates
    p = Point(a, b)

    for row in grid:
        for spot in row:
            spot_box = box(spot.x, spot.y, spot.x + spot.width, spot.y + spot.height)
            if spot_box.intersects(p):
                return spot

def findpath(grid, p1: Tuple[int, int], p2: Tuple[int, int]):
    start = coords_to_spot(grid, p1)
    end = coords_to_spot(grid, p2)
    return algorithm(grid, start, end)
