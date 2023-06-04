"""
This file is responsible for storing all the information about the current state of a chess game. It will also be responsible
for determining the valid moves at the current state and also keep a move log.
"""
class GameState():
    def __init__(self):
        #The board is an 8x8 2D list, each element of the list has 2 characters.
        #The first character represents the color of the piece, 'b' or 'w'
        #The second character represents the type of the piece, 'k', 'q', 'r', 'b', 'n' and 'p'
        #"--" represents an empty space with no piece on.
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
        self.whiteToMove = True
        self.moveLog = []


    '''
    Takes a Move as a parameter and executes it
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move) #log the move
        self.whiteToMove = not self.whiteToMove #swap players

    '''
    Undo the last move made.
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #if a move was made to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #change player turns back


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
                turn = self.board[row][column][0] #this can be "w" or "b" or "-"
                if (turn == 'w' and self.whiteToMove) and (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    if piece == 'p':
                        self.getPawnMoves(row, column, moves)
        return  moves


    '''
    get all the pawn moves for the pawn located at row, column and add these moves to the list
    '''
    def getPawnMoves(self, row, column, moves):
        pass


class Move():
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