"""
This file is responsible for handling user input and displaying the current GameState object.
"""

import pygame as py
import Engine

WIDTH = HEIGHT = 1024
DIMENSION = 8  # 8x8 board dimensions
SQUARE_SIZE = HEIGHT / DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called only once in the main.
'''
def loadImages():
    pieces = ['wk', 'wq', 'wb', 'wn', 'wr', 'wp', 'bk', 'bq', 'bb', 'bn', 'br', 'bp']
    for piece in pieces:
        IMAGES[piece] = py.transform.scale(py.image.load("images/" + piece + ".png"),
                                           (SQUARE_SIZE, SQUARE_SIZE))


'''
Handle user input and update images here
'''
def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    clock = py.time.Clock()
    screen.fill((py.Color("white")))
    gameState = Engine.GameState()
    loadImages()  # load images only once
    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
        drawGameState(screen,gameState)
        clock.tick(MAX_FPS)
        py.display.flip()


'''
Responsible for all graphics within a current game state.
'''
def drawGameState(screen, gameState):
    drawBoard(screen)
    drawPieces(screen, gameState.board)


'''
Draw the board squares
'''
def drawBoard(screen):
    colors = [py.Color("white"), py.Color("purple")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column) % 2]
            py.draw.rect(screen, color, py.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


'''
Draw the pieces on the board
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], py.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


if __name__ == "__main__":
    main()
