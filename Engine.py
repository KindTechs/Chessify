"""
This file is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state and also keep a move log.
"""


class GameState:
    def __init__(self):
        # The board is a 8x8 2D list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'k', 'q', 'r', 'b', 'n' and 'p'
        # "--" represents an empty space with no piece on.
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'r': self.getRookMoves, 'b': self.getBishopMoves,
                              'n': self.getKnightMoves, 'q': self.getQueenMoves, 'k': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()  # coordinates of the square where en Passant capture is possible

    '''
    Takes a Move as a parameter and executes it
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)  # log the move
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the kings location if moved
        if move.pieceMoved == 'wk':
            self.whiteKingLocation = (move.endRow, move.endColumn)
        elif move.pieceMoved == 'bk':
            self.blackKingLocation = (move.endRow, move.endColumn)

            # pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N:")  # take this to UI later
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + promotedPiece

            # enpassant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endColumn] = '--'  # capturing the pawn

            # update enPassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only on 2 square pawn advance
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startColumn)
        else:
            self.enPassantPossible = ()

    '''
    Undo the last move made.
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:  # if a move was made to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # change player turns back
            # update the kings location if moved
            if move.pieceMoved == 'wk':
                self.whiteKingLocation = (move.startRow, move.startColumn)
            elif move.pieceMoved == 'bk':
                self.blackKingLocation = (move.startRow, move.startColumn)

            # undo en passant move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endColumn] = '--'
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endColumn)
            # undo a 2 square pawn move
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

    '''
    All valid moves considering checks. e.g. can't move a piece if it's pinned to a king
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingColumn = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingColumn = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block it or move the king away
                moves = self.getAllPossibleMoves()
                # to block a check a piece must be moves into one of the squares between the king and the enemy piece
                check = self.checks[0]  # information about the check
                checkRow = check[0]
                checkColumn = check[1]
                pieceChecking = self.board[checkRow][checkColumn]  # enemy piece checking the king
                validSquares = []  # squares that pieces can move to
                # if checking piece is the knight, it must be either captured or the king must be moved, it's check can't be blocked
                if pieceChecking[1] == 'n':
                    validSquares = [(checkRow, checkColumn)]
                else:
                    for index in range(1, 8):
                        validSquare = (kingRow + check[2] * index, kingColumn + check[3] * index)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkColumn:  # once you get to piece end checks
                            break
                # remove any moves that don't block the check or move king
                for index in range(len(moves) - 1, -1, -1):  # iterate backwards through the list while removing from it
                    if moves[index].pieceMoved[1] != 'k':  # given move doesn't move king, so it must block or capture
                        if not (moves[index].endRow, moves[index].endColumn) in validSquares:  # given move doesn't block check or capture the piece
                            moves.remove(moves[index])
            else:  # king is under double check, so it has to move
                self.getKingMoves(kingRow, kingColumn, moves)
        else:  # not in check, so all moves can be played
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:  # either checkmate or stalemate
            if self.isInCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    '''
    Returns a list of pins and checks and whether a player is in check
    '''
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startColumn = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startColumn = self.blackKingLocation[1]
        # check outward from king for pins and checks and keep track of pins
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for directionsIndex in range(len(directions)):
            direction = directions[directionsIndex]
            possiblePin = ()  # reset possible pins
            for distance in range(1, 8):
                endRow = startRow + direction[0] * distance
                endColumn = startColumn + direction[1] * distance
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece[0] == allyColor and endPiece[1] != 'k':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endColumn, direction[0], direction[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        # 1) orthogonally away from king and piece is a rook
                        # 2) diagonally away from king and piece is a bishop
                        # 3) 1 square away diagonally from king and piece is a pawn
                        # 4) in any direction from king and piece is a queen
                        # 5) any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= directionsIndex <= 3 and pieceType == 'r') or \
                                (4 <= directionsIndex <= 7 and pieceType == 'b') or \
                                (distance == 1 and pieceType == 'p' and ((enemyColor == 'w' and 6 <= directionsIndex <= 7) or (enemyColor == 'b' and 4 <= directionsIndex <= 5))) or \
                                (pieceType == 'q') or \
                                (distance == 1 and pieceType == 'k'):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endColumn, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying checks:
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knightMoves:
            endRow = startRow + move[0]
            endColumn = startColumn + move[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] == enemyColor and endPiece[1] == 'n':  # enemy knight attacking the king
                    inCheck = True
                    checks.append((endRow, endColumn, move[0], move[1]))
        return inCheck, pins, checks

    '''
    Check whether the current player is in check
    '''
    def isInCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Check whether the enemy attacks the square at given row and column
    '''
    def squareUnderAttack(self, row, column):
        self.whiteToMove = not self.whiteToMove  # switch the turn to check opponents moves
        opponentsMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch the turn back
        for move in opponentsMoves:
            if move.endRow == row and move.endColumn == column:  # square is under attack
                return True
        return False

    '''
    All moves without considering checks. e.g can move a piece even if it's pinned to a king
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]  # this can be "w" or "b" or "-"
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row, column, moves)  # calls the corresponding move function for each piece
        return moves

    '''
    Get all the pawn moves for the pawn located at row, column and add these moves to the list
    '''
    def getPawnMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piecePinned = True
                pinDirection = (self.pins[index][2], self.pins[index][3])
                self.pins.remove(self.pins[index])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"

        if self.board[row+moveAmount][column] == "--":  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, column), (row + moveAmount, column), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][column] == "--":  # 2 square pawn advance
                    moves.append(Move((row, column), (row + 2 * moveAmount, column), self.board))
        if column - 1 >= 0:  # capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][column - 1][0] == enemyColor:
                    moves.append(Move((row, column), (row + moveAmount, column - 1), self.board))
                if (row + moveAmount, column - 1) == self.enPassantPossible:
                    moves.append(Move((row, column), (row + moveAmount, column - 1), self.board, isEnPassantMove=True))
        if column + 1 <= 7:  # capture to the right
            if not piecePinned or pinDirection == (moveAmount, +1):
                if self.board[row + moveAmount][column + 1][0] == enemyColor:
                    moves.append(Move((row, column), (row + moveAmount, column + 1), self.board))
                if (row + moveAmount, column + 1) == self.enPassantPossible:
                    moves.append(Move((row, column), (row + moveAmount, column + 1), self.board, isEnPassantMove=True))

    '''
    Get all the rook moves for the pawn located at row, column and add these moves to the list
    '''
    def getRookMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piecePinned = True
                pinDirection = (self.pins[index][2], self.pins[index][3])
                if self.board[row][column][1] != 'q':
                    self.pins.remove(self.pins[index])
                break

        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for index in range(1, 8):
                endRow = row + direction[0] * index
                endColumn = column + direction[1] * index
                if 0 <= endRow < 8 and 0 <= endColumn < 8:  # check for possible moves only in boundaries of the board
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endColumn]
                        if endPiece == "--":  # empty space is valid
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                        elif endPiece[0] == enemyColor:  # capture enemy piece
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    '''
    Get all the bishop moves for the pawn located at row, column and add these moves to the list
    '''
    def getBishopMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piecePinned = True
                pinDirection = (self.pins[index][2], self.pins[index][3])
                self.pins.remove(self.pins[index])
                break

        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for index in range(1, 8):
                endRow = row + direction[0] * index
                endColumn = column + direction[1] * index
                if 0 <= endRow < 8 and 0 <= endColumn < 8:  # check for possible moves only in boundaries of the board
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endColumn]
                        if endPiece == "--":  # empty space is valid
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                        elif endPiece[0] == enemyColor:  # capture enemy piece
                            moves.append(Move((row, column), (endRow, endColumn), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    '''
    Get all the knight moves for the pawn located at row, column and add these moves to the list
    '''
    def getKnightMoves(self, row, column, moves):
        piecePinned = False
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piecePinned = True
                self.pins.remove(self.pins[index])
                break

        knightMoves = ((1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1))
        allyColor = "w" if self.whiteToMove else "b"
        for move in knightMoves:
            endRow = row + move[0]
            endColumn = column + move[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:  # check for possible moves only in boundaries of the board
                if not piecePinned:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece[0] != allyColor:  # so it's either enemy piece or empty square
                        moves.append(Move((row, column), (endRow, endColumn), self.board))

    '''
    Get all the queen moves for the pawn located at row, column and add these moves to the list
    '''
    def getQueenMoves(self, row, column, moves):
        self.getBishopMoves(row, column, moves)
        self.getRookMoves(row, column, moves)

    '''
    Get all the king moves for the pawn located at row, column and add these moves to the list
    '''
    def getKingMoves(self, row, column, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        columnMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for index in range(8):
            endRow = row + rowMoves[index]
            endColumn = column + columnMoves[index]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != allyColor:  # not a white piece, empty or enemy piece
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endColumn)
                    else:
                        self.blackKingLocation = (endRow, endColumn)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, column), (endRow, endColumn), self.board))
                    # place the king back on the original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, column)
                    else:
                        self.blackKingLocation = (row, column)


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {value: key for key, value in ranksToRows.items()}
    filesToColumns = {"a": 0, "b": 1, "c": 2, "d": 3,
                      "e": 4, "f": 5, "g": 6, "h": 7}
    columnsToFiles = {value: key for key, value in filesToColumns.items()}

    def __init__(self, startSquare, endSquare, board, isEnPassantMove=False):
        self.startRow = startSquare[0]
        self.startColumn = startSquare[1]
        self.endRow = endSquare[0]
        self.endColumn = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn

    '''
    Override equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startColumn) + self.getRankFile(self.endRow, self.endColumn)

    def getRankFile(self, row, column):
        return self.columnsToFiles[column] + self.rowsToRanks[row]
