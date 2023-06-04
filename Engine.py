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

    '''
    Takes a Move as a parameter and executes it
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)  # log the move
        self.whiteToMove = not self.whiteToMove  # swap players

    '''
    Undo the last move made.
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:  # if a move was made to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # change player turns back

    '''
    All valid moves considering checks. e.g. can't move a piece if it's pinned to a king
    '''
    def getValidMoves(self):
        return self.getAllPossibleMoves()

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
        if self.whiteToMove:  # white pawn moves
            if self.board[row - 1][column] == "--":  # 1 square pawn move
                moves.append(Move((row, column), (row - 1, column), self.board))
                if row == 6 and self.board[row - 2][column] == "--":  # 2 square pawn move
                    moves.append(Move((row, column), (row - 2, column), self.board))
            if column - 1 >= 0:  # pawn captures to the left
                if self.board[row - 1][column - 1][0] == 'b':  # black piece to capture diagonally
                    moves.append(Move((row, column), (row - 1, column - 1), self.board))
            if column + 1 <= 7:  # pawn captures to the right
                if self.board[row - 1][column + 1][0] == 'b':  # black piece to capture diagonally
                    moves.append(Move((row, column), (row - 1, column + 1), self.board))

        else:  # black pawn moves
            if self.board[row + 1][column] == "--":  # 1 square pawn move
                moves.append(Move((row, column), (row + 1, column), self.board))
                if row == 1 and self.board[row + 2][column] == "--":  # 2 square pawn move
                    moves.append(Move((row, column), (row + 2, column), self.board))
            if column + 1 <= 7:  # pawn captures to the left
                if self.board[row + 1][column + 1][0] == 'w':  # white piece to capture diagonally
                    moves.append(Move((row, column), (row + 1, column + 1), self.board))
            if column - 1 >= 0:  # pawn captures to the right
                if self.board[row + 1][column - 1][0] == 'w':  # black piece to capture diagonally
                    moves.append(Move((row, column), (row + 1, column - 1), self.board))

    '''
    Get all the rook moves for the pawn located at row, column and add these moves to the list
    '''
    def getRookMoves(self, row, column, moves):
        pass

    '''
    Get all the bishop moves for the pawn located at row, column and add these moves to the list
    '''
    def getBishopMoves(self, row, column, moves):
        pass

    '''
    Get all the knight moves for the pawn located at row, column and add these moves to the list
    '''
    def getKnightMoves(self, row, column, moves):
        pass

    '''
    Get all the queen moves for the pawn located at row, column and add these moves to the list
    '''
    def getQueenMoves(self, row, column, moves):
        pass

    '''
    Get all the king moves for the pawn located at row, column and add these moves to the list
    '''
    def getKingMoves(self, row, column, moves):
        pass


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {value: key for key, value in ranksToRows.items()}
    filesToColumns = {"a": 0, "b": 1, "c": 2, "d": 3,
                      "e": 4, "f": 5, "g": 6, "h": 7}
    columnsToFiles = {value: key for key, value in filesToColumns.items()}

    def __init__(self, startSquare, endSquare, board):
        self.startRow = startSquare[0]
        self.startColumn = startSquare[1]
        self.endRow = endSquare[0]
        self.endColumn = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
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
