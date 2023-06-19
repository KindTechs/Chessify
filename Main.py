"""
This file is responsible for handling user input and displaying the current GameState object.
"""

import pygame as py
import Engine

WIDTH = HEIGHT = 512
DIMENSION = 8  # 8x8 board dimensions
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called only once in the main.
'''
def loadImages():
    pieces = ['wk', 'wq', 'wb', 'wn', 'wr', 'wp', 'bk', 'bq', 'bb', 'bn', 'br', 'bp']
    for piece in pieces:
        IMAGES[piece] = py.transform.scale(py.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


'''
Handle user input and update images here
'''
def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    clock = py.time.Clock()
    screen.fill((py.Color("white")))
    gameState = Engine.GameState()
    validMoves = gameState.getValidMoves()
    moveMade = False

    loadImages()  # load images only once
    running = True
    squareSelected = ()  # keep track of the last user click in a tuple (row, column)
    playerClicks = []  # keep track of player clicks in two tuples.
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            # mouse handlers
            elif event.type == py.MOUSEBUTTONDOWN:
                location = py.mouse.get_pos()  # x,y location of the mouse
                column = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if squareSelected == (row, column):  # user clicked the same square twice
                    squareSelected = ()  # deselect the square
                    playerClicks = []  # clear the player clicks
                else:
                    squareSelected = (row, column)
                    playerClicks.append(
                        squareSelected)  # append for both first and second clicks. From square a To square b
                if len(playerClicks) == 2:
                    move = Engine.Move(playerClicks[0], playerClicks[1], gameState.board)
                    # print(move.getChessNotation())
                    for index in range(len(validMoves)):
                        if move == validMoves[index]:
                            gameState.makeMove(validMoves[index])
                            moveMade = True
                            squareSelected = ()  # reset user clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [squareSelected]
            # key handlers
            elif event.type == py.KEYDOWN:
                if event.key == py.K_u:  # undo when 'u' is pressed
                    gameState.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False

        drawGameState(screen, gameState)
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
