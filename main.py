import tkinter as tk
from tkinter import messagebox

import pygame
from queue import PriorityQueue
import random

top = tk.Tk()
top.geometry("400x400")
WIDTH = 400

RED = (255, 0, 0)  # closed
GREEN = (0, 255, 0)  # open
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, anything):
        return False


def heuristic(pot1, pot2):
    y1, x1 = pot1
    y2, x2 = pot2
    return abs(y2 - y1) + abs(x2 - x1)


def reconstruct_path(parent, start, current, draw):
    while current in parent:
        current = parent[current]
        if current != start:
            current.make_path()  # PURPLE
        draw()


def Astar(draw, grid, start, end):
    open_set = PriorityQueue()
    parent = {}
    gscore = {spot: float("inf") for row in grid for spot in row}  # make it inf by default عشان تسهل علي اشياء بعدين
    fscore = {spot: float("inf") for row in grid for spot in row}

    open_set.put((0, start))
    gscore[start] = 0
    fscore[start] = heuristic(start.get_pos(), end.get_pos())
    AlSet = {start}

    while not open_set.empty():
        current = open_set.get()[1]
        AlSet.remove(current)

        if current == end:
            reconstruct_path(parent, start, end, lambda: draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            betterGscore = gscore[current] + 1  # هنا مفترض ان كل مربع ومربع بينهم 1 "المسافه"

            if betterGscore < gscore[neighbor]:  # found somthing better
                parent[neighbor] = current
                gscore[neighbor] = betterGscore
                hscore = heuristic(neighbor.get_pos(), end.get_pos())
                fscore[neighbor] = betterGscore + hscore
                if neighbor not in AlSet:
                    open_set.put((fscore[neighbor], neighbor))
                    AlSet.add(neighbor)
                    neighbor.make_open()  # Green

        draw()

        if current != start:
            current.make_closed()  # RED

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def randomebarrir(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            x = random.randint(0, 2)
            if x == 1:
                spot.make_barrier()

    draw_grid(win, rows, width)
    pygame.display.update()


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def specify():
    top.destroy()

    win = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("Saud")
    ROWS = int(x.get())
    grid = make_grid(ROWS, WIDTH)

    start = None
    end = None
    running = True

    while running:
        draw(win, grid, ROWS, WIDTH)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    Astar(lambda: draw(win, grid, ROWS, WIDTH), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)

    pygame.quit()


def randomB():
    top.destroy()

    win = pygame.display.set_mode((WIDTH, WIDTH))

    pygame.display.set_caption("Saud")

    ROWS = 50
    grid = make_grid(ROWS, WIDTH)
    randomebarrir(win, grid, ROWS, WIDTH)
    start = None
    end = None

    running = True

    while running:
        draw(win, grid, ROWS, WIDTH)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                spot = grid[row][col]
                if not start and spot != end and not spot.is_barrier():
                    start = spot
                    start.make_start()

                elif not end and spot != start and not spot.is_barrier():
                    end = spot
                    end.make_end()


            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                spot = grid[row][col]
                if spot == start:
                    spot.reset()
                    start = None
                elif spot == end:
                    spot.reset()
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    Astar(lambda: draw(win, grid, ROWS, WIDTH), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    randomB()

    pygame.quit()


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        top.destroy()


x = tk.StringVar()
f1 = tk.Entry(top, textvariable=x)
l1 = tk.Label(top, text="Enter the Number of Rows")
b1 = tk.Button(top, text="randomly generates a grid with obstacles", command=randomB, pady=10)
b2 = tk.Button(top, text="specify the dimensions of the and grid the location of the obstacles", command=specify,
               pady=10)
b1.place(x=0, y=0)
b2.place(x=0, y=50)
f1.place(x=150, y=100)
l1.place(x=0, y=100)

top.protocol("WM_DELETE_WINDOW", on_closing)

top.mainloop()
