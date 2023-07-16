"""
This file is responsible for handling user input and displaying the current GameState object.
"""
import pygame as py
import Engine
import ChessAI

WIDTH = HEIGHT = 512  # change to 1024 to make window bigger
DIMENSION = 8  # 8x8 board dimensions
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}
colors = [py.Color("white"), py.Color("grey")]  # Square colors

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
    animate = False

    loadImages()  # load images only once
    running = True
    squareSelected = ()  # keep track of the last user click in a tuple (row, column)
    playerClicks = []  # keep track of player clicks in tuples.
    gameOver = False
    playerOne = True  # if a human is white, then this will be true. If AI, then false
    playerTwo = True  # same as above but for black
    while running:
        humanTurn = (gameState.whiteToMove and playerOne) or (not gameState.whiteToMove and playerTwo)
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            # mouse handlers
            elif event.type == py.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
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
                        print(move.getChessNotation())
                        for index in range(len(validMoves)):
                            if move == validMoves[index]:
                                gameState.makeMove(validMoves[index])
                                moveMade = True
                                animate = True
                                squareSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]
            # key handlers
            elif event.type == py.KEYDOWN:
                if event.key == py.K_u:  # undo when 'u' is pressed
                    gameState.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if event.key == py.K_r:  # reset the board when 'r' is pressed
                    gameState = Engine.GameState()
                    validMoves = gameState.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI move finder
        if not gameOver and not humanTurn:
            aiMove = ChessAI.findBestMove(gameState, validMoves)
            if aiMove is None:
                aiMove = ChessAI.findRandomMove(validMoves)
            gameState.makeMove(aiMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gameState.moveLog[-1], screen, gameState.board, clock)
            validMoves = gameState.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gameState, validMoves, squareSelected)
        if gameState.checkMate:
            gameOver = True
            drawText(screen, 'Checkmate')
        elif gameState.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        py.display.flip()


'''
Highlight the selected square and move the selected piece
'''
def highlightSquares(screen, gameState, validMoves, squareSelected):
    if squareSelected != ():
        row, column = squareSelected
        if gameState.board[row][column][0] == ('w' if gameState.whiteToMove else 'b'):  # square selected is a piece that can be moved
            # highlight selected square
            square = py.Surface((SQUARE_SIZE, SQUARE_SIZE))
            square.set_alpha(100)  # transparency value (0 - transparent, 255 opaque)
            square.fill(py.Color('blue'))
            screen.blit(square, (column*SQUARE_SIZE, row*SQUARE_SIZE))
            # highlight moves from that square
            square.fill(py.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startColumn == column:
                    screen.blit(square, (move.endColumn*SQUARE_SIZE, move.endRow*SQUARE_SIZE))


'''
Responsible for all graphics within a current game state.
'''
def drawGameState(screen, gameState, validMoves, squareSelected):
    drawBoard(screen)
    highlightSquares(screen, gameState, validMoves, squareSelected)
    drawPieces(screen, gameState.board)


'''
Draw the board squares
'''
def drawBoard(screen):
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


# '''
# Animate a move
# '''
def animateMove(move, screen, board, clock):
    deltaRow = move.endRow - move.startRow
    deltaColumn = move.endColumn - move.startColumn
    framesPerSquare = 20
    frameCount = (abs(deltaRow) + abs(deltaColumn)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, column = (move.startRow + deltaRow*frame/frameCount, move.startColumn + deltaColumn*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endColumn) % 2]
        endSquare = py.Rect(move.endColumn*SQUARE_SIZE, move.endRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        py.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnPassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = py.Rect(move.endColumn * SQUARE_SIZE, enPassantRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], py.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        py.display.flip()
        clock.tick(360)

def drawText(screen, text):
    font = py.font.Font(py.font.get_default_font(), 32)
    textObject = font.render(text, False, py.Color('Gray'))
    textLocation = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, py.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
