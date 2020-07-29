#Functions for game
import numpy as np
from matplotlib import pyplot as plt
import time
import random
from random import choice
import pickle
from os.path import sep

empty = 1
white = 0
black = 2

def createBoard():
    board = np.empty((8,8))
    for i in range(8):
        for j in range(8):
            board[i][j] = empty
    board[3][3] = white
    board[4][4] = white
    board[4][3] = black
    board[3][4] = black
    return board

def countColor(board,color):
    colors = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == color:
                colors += 1
    return colors

def weightedCountColor(board,color):
    colors = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == color:
                if (i,j) == (0,0) or (i,j) == (0,7) or (i,j) == (7,0) or (i,j) == (7,7):
                    colors += 1000
                elif i == 0 or j == 0 or i == 7 or j == 7:
                    colors += 100
                else:
                    colors += 1
    return colors

def onBoard(i,j,board):
    if (i <= board.shape[0]-1 and i >= 0) and (j <= board.shape[1]-1 and j >= 0):# You need some more conditions here! 
        return True
    else:
        return False
    
def getOtherColor(color):
    if color == white:
        return black
    elif color == black:
        return white
    else:
        return None

def isSequence(placedChip,neighborChip,board):
    capturedColor = board[neighborChip[0]][neighborChip[1]]
    otherColor = getOtherColor(capturedColor)
    di = neighborChip[0] - placedChip[0]
    dj = neighborChip[1] - placedChip[1]
    currentCoords = (neighborChip)
    for i in range(1,8):
        if not onBoard(i * di + neighborChip[0],i * dj + neighborChip[1],board):
            return False
        currentCoords = (i * di + neighborChip[0],i * dj + neighborChip[1])
        currentColor = board[currentCoords[0]][currentCoords[1]]
        if currentColor == otherColor:
            return True
        elif currentColor == capturedColor:
            continue
        elif currentColor == empty:
            return False
    
def getPossibleMoves(color,board):
    possibleMoves = []
    for i in range(8):
        for j in range(8):
            if board[i][j] == empty:
                for neighbor in [(i-1, j),(i, j-1),(i+1, j),(i, j+1),(i+1, j+1),(i-1, j+1),(i-1, j-1),(i+1, j-1)]:
                    if onBoard(neighbor[0],neighbor[1],board) and board[neighbor[0]][neighbor[1]] == getOtherColor(color):
                        if isSequence((i,j),neighbor,board):
                            possibleMoves.append((i,j))
    return possibleMoves
                        
def placeMarker(color,coordinates,boar):
    board = np.copy(boar)
    otherColor = getOtherColor(color)
    i = coordinates[0]
    j = coordinates[1]
    board[i][j] = color
    for neighbor in [(i-1, j),(i, j-1),(i+1, j),(i, j+1),(i+1, j+1),(i-1, j+1),(i-1, j-1),(i+1, j-1)]:
        if onBoard(neighbor[0],neighbor[1],board) and board[neighbor[0]][neighbor[1]] == getOtherColor(color):
            if isSequence((i,j),neighbor,board):
                board[neighbor[0]][neighbor[1]] = color
                di = neighbor[0] - i
                dj = neighbor[1] - j
                for y in range(1,8):
                    if not onBoard(y * di + neighbor[0],y * dj + neighbor[1],board):
                        break
                    currentCoords = (y * di + neighbor[0],y * dj + neighbor[1])
                    currentColor = board[currentCoords[0]][currentCoords[1]]
                    if currentColor == color:
                        break
                    elif currentColor == otherColor:
                        board[y * di + neighbor[0]][y * dj + neighbor[1]] = color
                    elif currentColor == empty:
                        break
    return board

def getMaxMove(turn,board):
    moves = getPossibleMoves(turn,board)
    maxMove = (-5,-5)
    maximum = 0
    for move in moves:
        tempBoard =  placeMarker(turn,move,board)
        num = countColor(tempBoard,turn)
        if num > maximum:
            maximum = num
            maxMove = move
    return maxMove

def getSmartMove1D(turn,board):
    max_ = -1
    maxMove = (-5,-5)
    moves = getPossibleMoves(turn,board)
    enemy = getOtherColor(turn)
    for moves in moves:
        tempBoard = placeMarker(turn,move,board)
        enemyMoves = getPossibleMoves(enemy,tempBoard)
        enemyMove = getMaxMove(enemy,tempBoard)
        tempBoard = placeMarker(enemy,enemyMove,tempBoard)
        num = countColor(tempBoard,turn)
        if num > max_:
            max_ = num
            maxMove = move
    return move

def utility(turn, board):
    opponent = getOtherColor(turn)
    p = 0
    m = 0
    e = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == empty:
                e += 1
            elif board[i][j] == turn:
                p += 1
            elif board[i][j] == opponent:
                m += 1
            else:
                print("Critical Error")
    if e == 0 and p > m:
        return 100
    elif e == 0 and p < m:
        return -100
    else:
        return p - m

def deep2(turn, board, turn0):
    op = getOtherColor(turn)
    maxMove = (-5,-5)
    ma = -999999999
    if countColor(board,empty) == 0:
        return countColor(board,turn0) - countColor(board,getOtherColor(turn0))
    moves = getPossibleMoves(turn, board)
    for move in moves:
        tempBoard = placeMarker(turn,move,board)
        opMove = getMaxMove(op,tempBoard)
        tempBoard = placeMarker(op,opMove,tempBoard)
        moves2 = getPossibleMoves(turn,tempBoard)
        for move2 in moves2:
            tempBoard2 = placeMarker(turn,move2,tempBoard)
            opMove = getMaxMove(op,tempBoard2)
            score = countColor(tempBoard2,turn) - countColor(tempBoard2,op)
            if score > ma:
                ma = score
                maxMove = move
    return maxMove

def recursive(turn,board,turn0,depth):
    op = getOtherColor(turn)
    if countColor(board,empty) == 0 or depth == 6:
        return countColor(board,turn0) - countColor(board,getOtherColor(turn0))
    moves = getPossibleMoves(turn, board)
    maxScore = -90
    maxMove = (-5,-5)
    minScore = 90
    for move in moves:
        tempBoard = placeMarker(turn,move,board)
        score = recursive(op,tempBoard,turn0,depth + 1)
        if score > maxScore:
            maxScore = score
            maxMove = move
        if score < minScore:
            minScore = score
    if depth == 0:
        return maxMove
    elif  depth % 2 == 0:
        return maxScore
    elif depth % 2 == 1:
        return minScore

def weightedRecursive(turn,board,turn0,depth):
    op = getOtherColor(turn)
    if countColor(board,empty) == 0 or depth == 6:
        return weightedCountColor(board,turn0) - weightedCountColor(board,getOtherColor(turn0))
    moves = getPossibleMoves(turn, board)
    maxScore = -90
    maxMove = (-5,-5)
    minScore = 90
    for move in moves:
        tempBoard = placeMarker(turn,move,board)
        score = recursive(op,tempBoard,turn0,depth + 1)
        if score > maxScore:
            maxScore = score
            maxMove = move
        if score < minScore:
            minScore = score
    if depth == 0:
        return maxMove
    elif  depth % 2 == 0:
        return maxScore
    elif depth % 2 == 1:
        return minScore

def random(turn, board):
    moves = getPossibleMoves(turn, board)
    return random.choice(moves)
        
def flipBoard(origionalBoard):
    board = np.copy(origionalBoard)
    for i in range(8):
        for j in range(8):
            if board[i][j] == white:
                board[i][j] = black
            elif board[i][j] == black:
                board[i][j] = white
    return board


def generateGames(numGames):
    for i in range(1000000):
        movesBlack = []
        board = createBoard()
        turn = white
        while countColor(board,empty) > 0:
            moves = getPossibleMoves(turn,board)
            if len(moves) == 0 and len(getPossibleMoves(getOtherColor(turn),board)) == 0:
                break
            if len(moves) == 0:
                turn = getOtherColor(turn)
                continue
            move = recursive(turn,board,turn,0)
            if turn == black:
                movesBlack.append((board,move))
            else:
                movesBlack.append((flipBoard(board),move))
            board = placeMarker(turn,move,board)
            turn = getOtherColor(turn)
        #print('black',countColor(board, black), 'white',countColor(board, white))
        with open("Games2" + sep + str(i) + '_othello.pkl','wb') as outFile:
            pickle.dump(movesBlack,outFile)
            print(i)


        

board = createBoard()
turn = white
plt.imshow(board,cmap = 'binary')
plt.title("White's Turn")
plt.xlabel('J')
plt.ylabel('I')
plt.show()
boards = []


while not countColor(board,empty) == 0:
    if turn == white:
        i = input('i: ')
        j = input('j: ')
        if 'show' in i or 'show' in j:
            plt.imshow(board,cmap = 'binary')
            plt.title("White's Turn")
            plt.xlabel('J')
            plt.ylabel('I')
            plt.show()
            continue
        if 'last' in i or 'last' in j:
            for boar in boards[-3:]:
                plt.imshow(boar,cmap = 'binary')
                plt.show()
            continue
        i = int(i)
        j = int(j)
        move = (i,j)
        moves = getPossibleMoves(turn,board)
        if len(moves) == 0:
            turn = getOtherColor(turn)
            continue
        if not move in moves:
            plt.imshow(board,cmap = 'binary')
            plt.title("Not a Valid Move, Try Again")
            plt.xlabel('J')
            plt.ylabel('I')
            plt.show()
            continue
        board = placeMarker(turn,move,board)
        plt.imshow(board,cmap = 'binary')
        plt.title("Black's Turn")
        plt.xlabel('J')
        plt.ylabel('I')
        plt.show()
        turn = getOtherColor(turn)
    else:
        time.sleep(2)
        moves = getPossibleMoves(turn,board)
        if len(moves) == 0:
            turn = getOtherColor(turn)
            continue
        move = recursive(turn,board,turn,0)#deep2(turn,board,turn)
        board = placeMarker(turn,move,board)
        turn = getOtherColor(turn)
        for boar in boards:
            plt.imshow(boar,cmap='binary')
        plt.imshow(board,cmap = 'binary')
        plt.title("White's Turn")
        plt.xlabel('J')
        plt.ylabel('I')
        plt.show()
    boards.append(board)
