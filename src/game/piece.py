import tkinter as tk
from math import sqrt

from src.constants import *


def dist(point1: tuple, point2: tuple) -> float:
    return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


class Piece:
    """Class representing a piece object used by the Board."""

    DEFAULT_RADIUS = 30

    radius = DEFAULT_RADIUS

    def __init__(self, x: int, y: int, color: tuple, canvas: tk.Canvas):
        self.x = x
        self.y = y
        self.color = color
        self.canvas = canvas
        self.picked_up = False

        self.reached_position = True
        self.velocity = (0, 0)
        self.target = (0, 0)

        self.remove_after_reached_position = False
        self.remove_func = None
        self.pending_remove = False

        self.oval = self.canvas.create_oval(self.x - Piece.radius - 2, self.y - Piece.radius - 2, self.x + Piece.radius,
                                            self.y + Piece.radius, fill="#ffe363" if self.color == WHITE else "black")

    def __repr__(self):
        return "WHITE piece" if self.color == WHITE else "BLACK piece"

    def update(self, mouse_x: int, mouse_y: int):
        if self.picked_up:
            self.x = mouse_x
            self.y = mouse_y
            self.canvas.coords(self.oval, self.x - Piece.radius - 2, self.y - Piece.radius - 2, self.x + Piece.radius,
                               self.y + Piece.radius)

        if not self.reached_position:
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            self.canvas.coords(self.oval, self.x - Piece.radius - 2, self.y - Piece.radius - 2, self.x + Piece.radius,
                               self.y + Piece.radius)
            if dist((self.x, self.y), (self.target[0], self.target[1])) < 12.1:
                self.x = self.target[0]
                self.y = self.target[1]
                self.canvas.coords(self.oval, self.x - Piece.radius - 2, self.y - Piece.radius - 2, self.x + Piece.radius,
                                   self.y + Piece.radius)  # Correct the position
                self.reached_position = True
                self.velocity = (0, 0)
                self.target = (0, 0)

                if self.remove_after_reached_position:  # Dirty hack part 2
                    self.remove_func(True)
                    self.remove_after_reached_position = False

    def pick_up(self, turn: int) -> bool:
        if (turn == PLAYER1 and self.color == WHITE) or (turn == PLAYER2 and self.color == BLACK):
            self.picked_up = True
            return True
        else:
            return False

    def release(self, node):
        self.picked_up = False
        self.x = node.x
        self.y = node.y
        self.canvas.coords(self.oval, self.x - Piece.radius - 2, self.y - Piece.radius - 2, self.x + Piece.radius,
                           self.y + Piece.radius)
