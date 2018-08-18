import numpy as np
import pyibex as pi
from scipy import optimize
import copy

class BB():
    """
    This class specifies the base Game class. To define your own game, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    See othello/OthelloGame.py for an example implementation.
    """
    def __init__(self, function, input_box, output_range,func):
        self.function = function
        self.input_box = input_box
        self.output_range = output_range
        self.contractor = pi.CtcFwdBwd(self.function, self.output_range)
        self.func = func
        # size of representation for each variable
        self.embedding_size = 3
        self.addGradient = True

    def getRoot(self):
        """
        Returns:
            : a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        return getBoardFromInput_box(self.input_box)

    def addGradient(self,currentInput_box):
        #get gradient:
        data_point = []

        eps = np.sqrt(np.finfo(float).eps)
        derivative = []
        for x in data_point:
            derivative.append(optimize.approx_fprime(x, func, [eps, np.sqrt(200) * eps]))

    def getBoardFromInput_box(self, currentInput_box):


        shape = self.getBoardSize()

        embedding = np.zeros((2,3))

        for i in range(2):
            lower = currentInput_box[i][0]
            upper = currentInput_box[i][1]
            middle = float((lower + upper) / 2)

            embedding[i,0] = lower
            embedding[i,1] = middle
            embedding[i,2] = upper

        #find derivative
        if self.addGradient:
            data_point = embedding.transpose();
            eps = np.sqrt(np.finfo(float).eps)
            derivative = []
            for x in data_point:
                derivative.append(optimize.approx_fprime(x, self.func, [eps, np.sqrt(200) * eps]))
            return np.concatenate((embedding, np.asarray(derivative).transpose()),axis = 1)
        return embedding

    def getBoardSize(self):
        """
        Returns:
            (x,y): a tuple of board dimensions
        """
        if self.addGradient:
            return len(self.input_box),self.embedding_size*2
        return  len(self.input_box),self.embedding_size

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        return 2**len(self.input_box)

    def getNextState(self, currentInput_box, action):
        """
        Input:
            state: current state
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
        """
        var_index = int(action / 2)
        direction = action % 2

        # split the interval of the selected variable ([(),()],[(),()])
        new_boxes = currentInput_box.bisect(var_index, 0.5)

        # choose go to half of the interval
        currentInput_box = new_boxes[direction]

        self.contractor.contract(currentInput_box)

        #TODO: return the STATE

        return currentInput_box



    def getValidMoves(self,currentInput_box, threshold):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """

        mask = np.zeros(self.getActionSize())

        for i in range(len(currentInput_box)):
            if currentInput_box[i].diam() > threshold:
                mask[2*i] = 1
                mask[2*i+1] = 1

        return mask


    def getGameEnded(self,currentInput_box, threshold):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """


        # TODO: situation for empty box
        if currentInput_box.is_empty():
            return -5


        if 1 not in self.getValidMoves(currentInput_box, threshold):
            currentValue = [[currentInput_box[i].diam()/2 + currentInput_box[i][0],currentInput_box[i].diam()/2 + currentInput_box[i][0]] for i in range(len(currentInput_box))]
            #print(pi.IntervalVector(currentValue)[0])
            #print(self.function.eval(pi.IntervalVector(currentValue))[0])
            return 1 - np.abs(self.function.eval(pi.IntervalVector(currentValue))[0])
        else:
            return 0



    def stringRepresentation(self, currentInput_box):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        string = ''.join(str(x) for x in currentInput_box)
        return string
