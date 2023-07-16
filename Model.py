# import chess
import chess.engine
import numpy as np
# import pandas as pd
import tensorflow as tf
# from tensorflow.keras.models import Model
# from tensorflow.keras.layers import Dense, Flatten, Conv2D, Input, Dropout, Add, Concatenate
# import random

from tensorflow.python.keras.models import load_model

Model = tf.keras.models
Dense = tf.keras.layers.Dense
Flatten = tf.keras.layers.Flatten
Conv2D = tf.keras.layers.Conv2D
Input = tf.keras.layers.Input
Dropout = tf.keras.layers.Dropout
Add = tf.keras.layers.Add
Concatenate = tf.keras.layers.Concatenate
Adam = tf.keras.optimizers.Adam

# Define the input shape (8x8 chess board with 16 channels: 14 piece types + 2 for coordinates)
input_shape = (8, 8, 16)

# Create the model
def create_model():
    inputs = Input(shape=input_shape)
    x = Conv2D(64, kernel_size=3, activation='relu', padding='same')(inputs)
    x = Dropout(0.5)(x)
    x = Conv2D(16, kernel_size=3, padding='same')(x)  # Change 128 to 16
    x = Add()([inputs, x])
    x = tf.keras.activations.relu(x)
    x = Dropout(0.5)(x)
    x = Flatten()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    outputs = Dense(1, activation='tanh')(x)
    model = Model.Model(inputs=inputs, outputs=outputs)
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

def board_to_tensor(board):
    piece_dict = {'p': 0, 'P': 6, 'r': 1, 'R': 7, 'n': 2, 'N': 8, 'b': 3, 'B': 9, 'q': 4, 'Q': 10, 'k': 5, 'K': 11}
    tensor = np.zeros((8, 8, 16), dtype=np.uint8)  # Change to 16 in third dimension

    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            tensor[i // 8, i % 8, piece_dict[str(piece)]] = 1

    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        if board.turn:  # White to move
            tensor[move.to_square // 8, move.to_square % 8, 14] = 1
        else:  # Black to move
            tensor[move.to_square // 8, move.to_square % 8, 15] = 1

    # Add coordinates
    for i in range(8):
        for j in range(8):
            tensor[i, j, 12] = i / 7.0  # Normalize coordinates to be in range [0, 1]
            tensor[i, j, 13] = j / 7.0

    return tensor


# # Load dataset
# data = pd.read_csv('chessData.csv')
#
# # Remove rows where Evaluation starts with '#'
# data = data[~data['Evaluation'].str.startswith('#')]
#
# # Take the first n positions
# data = data.head(500000)
#
# # Convert FEN strings to board tensors and centipawn scores to normalized scores
# x_train = []
# y_train = []
#
# for index, row in data.iterrows():
#     print(index)
#     fen = row['FEN']
#     score = float(row['Evaluation'])
#
#     # Normalizing centipawn scores to range of -1 to 1
#     normalized_score = np.tanh(score / 10000)
#
#     # Convert FEN to board
#     board = chess.Board(fen)
#     tensor = board_to_tensor(board)
#
#     x_train.append(tensor)
#     y_train.append(normalized_score)
#
# x_train = np.array(x_train)
# y_train = np.array(y_train)
#
# # Save arrays to disk
# np.save('x_data.npy', x_train)
# np.save('y_data.npy', y_train)
# print("Finished saving arrays for training")
#
# # load existing arrays from disk
# x_train = np.load('x_data.npy')
# y_train = np.load('y_data.npy')
#
# # Create and train model
# print("Starting to train the model")
# model = create_model()
# batch_size = 64
# steps_per_epoch = len(x_train) // batch_size
# model.fit(x=x_train, y=y_train, epochs=10, batch_size=batch_size, steps_per_epoch=steps_per_epoch)
# print("Finished training the model")
#
# # Save the model
# model = model.save('chess_model.h5')
# print("Finished saving the model")

# Load the model
model = create_model()
model.load_weights('chess_model.h5')
optimizer = Adam(learning_rate=0.001)
model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mean_squared_error'])
print("Finished loading the model")

# Use principal variation search-like search to choose a move
def choose_move(board, depth):
    legal_moves = list(board.legal_moves)
    best_score = None
    best_move = None
    for move in legal_moves:
        board.push(move)
        score = -negamax(board, depth-1, -float('inf'), float('inf'))
        board.pop()
        if best_score is None or score > best_score:
            best_score = score
            best_move = move
    return best_move

# Negamax search with alpha-beta pruning
def negamax(board, depth, alpha, beta):
    if depth == 0 or board.is_game_over():
        return model.predict(np.expand_dims(board_to_tensor(board), axis=0))[0]
    legal_moves = list(board.legal_moves)
    score = -float('inf')
    for move in legal_moves:
        board.push(move)
        score = max(score, -negamax(board, depth-1, -beta, -alpha))
        board.pop()
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return score


# Play a game against Stockfish
engine = chess.engine.SimpleEngine.popen_uci('/usr/local/Cellar/stockfish/15.1/bin/stockfish')
board = chess.Board()
while not board.is_game_over():
    move = choose_move(board, 1)  # Change this to search deeper
    print("Model moves: " + move.uci())
    board.push(move)
    print(board)
    if not board.is_game_over():
        result = engine.play(board, chess.engine.Limit(time=2.0))
        print("Stockfish moves: " + result.move.uci())
        board.push(result.move)
        print(board)
engine.quit()
