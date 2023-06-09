import random
import sys
import serial.tools
import time
import serial.tools.list_ports as list_ports
# board needs to be made into a subclass or separate class


class gameModel():
    def __init__(self, game=' '):
        self.game = game
        self.player1 = 0
        self.player2 = 0


class gameObject():

    def __init__(self, waitTime=0.1, disable_interaction=True, iterations=10, board=None, height=5, length=8, isBot=False, drawBoardTurn=False, drawBoardGameOver=True, logLevel='CRITICAL', commsArduino=True):
        self.colors = {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}
        self.dummy = 5
        self.waitTime = waitTime
        self.height = height
        self.length = length
        self.board = board
        # print('self init')
        self.isBot = isBot
        self.debug = False

        self.inProgress = False
        self.winner = False
        self.playerCumulative = {1: 0, 2: 0}
        self.drawBoardTurn = drawBoardTurn
        self.drawBoardGameOver = drawBoardGameOver

        self.serialConnected = False
        self.commsArduino = commsArduino
        if serialConnected == False and self.commsArduino == True:
            self.init_serial()

        if not disable_interaction:
            self.iterations = self.confirm_runtime()
        if disable_interaction:
            self.iterations = 10
        if self.iterations > 20 and drawBoardTurn == None:
            self.drawBoardTurn = False
        self.logLevel = logLevel
        # logger.debug('{self.logLevel set to {logLevel:}}')
        logger, log = self.init_logger(logLevel)
        self.logger = logger
        self.log = log

    def init_logger(self, logLevel):
        logger = logging.getLogger(__name__)
        logger.setLevel(logLevel)
        log = logging.StreamHandler()
        log.setLevel(logLevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log.setFormatter(formatter)
        logger.addHandler(log)
        return logger, log

    def init_serial(self):
        reAttempts = 5
        self.logger.warning(
            'There must be an arduino connected and enumerated on the port listed in ardu.port or this will fail')
        if not self.serialConnected:
            self.ardu.port = '/dev/tty.usbserial-0001'
            self.ardu.baudrate = 115200
            self.ardu = serial.Serial()

        while self.serialConnected == False:
            self.logger.debug('Open Attempt')
            self.logger.debug(self.ardu)
            self.ardu.open()
            if self.ardu.is_open:
                self.serialConnected = True
                self.logger.debug(
                    'Serial connection established. setting serialConnected')
                self.serialConnected = True
            else:
                self.ardu.close()
                self.logger.info(f'{reAttempts=}')
                self.logger.debug(self.ardu)
                print(f'{reAttempts=}, {self.ardu}')
                reAttempts = reAttempts - 1
            if reAttempts == -1:
                break
        return self.ardu

    def clear_display(self):
        for i in range(self.height * self.length):
            output_to_serial(i, 0)


class comms():
    def __init__(self, port='COM3', baud=115200):
        self.ports = list(serial.tools.list_ports.comports())
        self.logger.debug(ports)
        self.ardu = serial.Serial('COM14', 115200)
        self.ardu.open()
        if self.ardu.is_open:
            self.serialConnected = True
            return self.ardu
        else:
            self.logger.debug('_init_serial')

    def output_to_serial(self, space, player):
        colorr = {0: {'r': 0, 'g': 0, 'b': 0},
                  1: {'r': 50, 'g': 150, 'b': 50},
                  2: {'r': 200, 'g': 100, 'b': 0}}
        text = f"{space}, {colorr[player]['r']}, {colorr[player]['g']}, {colorr[player]['b']}"

        self.ardu.write(f'<setPixelColor, {text}>\0'.encode())

    def start_game(self):
        if self.commsArduino == True and self.serialConnected == False:
            self.init_serial()
        self.inProgress = True


class gameObject():

    def __init__(self, waitTime=0.1, board={}, height=5, length=8, isBot=False):
        self.colors = {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}
        self.dummy = 5
        self.waitTime = waitTime
        self.height = height
        self.length = length
        self.board = board
        print('self init')
        self.isBot = isBot
        self.debug = False
        self.serialConnected = True
        self.inProgress = False
        self.winner = False

    def start_game(self):
        self.inProgress = True
        self.winner = False
        self.board = self.create_board(height=self.height, length=self.length)
        print('init board')
        self.turnLog = self.init_log()
        print("init log")
        self.currentPlayer = random.choice([1, 2])
        print("starting player chosen: Player {self.currentPlayer}\n\n\n")
        print("setting game parameters")
        self.define_win_dim()
        self.turnKey = False
        self.lastTurn = 0
        self.currentTurn = 1
        self.nextTurn = 2
        self.lastMove = None
        self.currentMove = None
        print("done. commencing game")
        self.playerScore = [{1: 0}, {2: 0}]
        return self

    def switch_player(self):
        self.currentPlayer = 1 if self.currentPlayer == 2 else 2

    def printLineBreak(self, text='', dbl_space=False, prefix=False):
        filler = '='
        buffer = 100 - len(text)
        prefixStr = filler * 25
        if not prefix:
            prefixStr = ''
            buffer += 25

        dbl_space = '\n\n' if dbl_space else None
        print(f'{prefixStr}{text}{filler*buffer:}', end=dbl_space)

    def modPlayerPts(player=-1, delta=0):
        if player == -1:
            player = self.currentPlayer
        try:
            self.playerScore[player] = self.playerScore[player] + delta
            print(f"{player=} score was updated by {delta=}")
            return True
        except:
            print(f"{player=} score NOT updated by {delta=}")
            return False

    def create_board(self, height=5, length=8):
        height = self.height
        length = self.length
        boardIndex = {}
        for i in range(height * length):
            boardIndex.update(
                {i: {'color': -1, 'occupied': False, 'moveNumber': -1}})
        return boardIndex

    def init_log(self):
        moveLog = {}
        log = (i + 1 for i in range(len(self.board)))
        for i in log:
            moveLog[i] = False
        return moveLog

    def draw_board(self, board, height=5, length=8):
        height = self.height
        length = self.length
        print('0\t| ', end='')
        for key in self.board.keys():
            piece = self.colors[self.board[key]['color']]
            print(piece + ' | ', end='')
            if int(key) != height * length and (int(key) + 1) % length == 0:
                print(f'\n{str(key+1)}\t| ', end='')

    def start_turn(self, player, choice=None):
        self.printLineBreak(text='starting turn')
        self.turnKey = True
        msg = f"{self.lastTurn=}, {self.currentTurn=}, {self.nextTurn=}, {self.lastMove=}, {self.currentPlayer=}"
        self.printLineBreak(text=msg, dbl_space=False)

        msg = f"current player: {game.currentPlayer} desired move: {choice}"

        self.printLineBreak(text=msg, prefix=True)
        #print(f"lastTurn: {self.lastTurn} currentTurn: {self.currentTurn} nextTurn: {self.nextTurn}")
        self.lastTurn = self.currentTurn
        self.currentTurn = self.nextTurn
        #self.nextTurn = self.nextTurn + 1

        openSpaces = self.possible_moves(self.board)
        choiceAccepted = self.check_move(self.currentPlayer, choice)
        while choiceAccepted == False:
            if len(openSpaces) < 1:
                return False

            choiceAccepted = self.check_move(self.currentPlayer, int(
                input('Integers 1-39 represent the spaces on the board. Choose one')))
        if choiceAccepted:
            self.currentMove = choice
        self.printLineBreak(text="Submitting Move", prefix=True)
        return self.take_move(self.currentPlayer, choice)

    def draw_win(self, sequence, board={}):
        if not board:
            board = self.board
        for i in sequence:
            f = self.colors[board[i]['color']]
            board[i]['color'] = f.upper()
        return board

    def end_turn(self, player, choice):

        self.isWinner = self.check_win(player, choice, self.board)
        isWinner = self.isWinner
        if isWinner[0]:
            self.modPlayerPts(player, 10)
            otherPlayer = 1 if player == 2 else 2
            self.modPlayerPts(otherPlayer, -12)
            print(
                f'{isWinner[0]=}, player: {isWinner[1]}, sequence: {isWinner[2]}, lastMove: {isWinner[3]}')
            jsd = self.draw_win(isWinner[2])
            draw_board(jsd)
            self.game_over(1, player)
            return True

        try:

            # draw_board(self.board)
            self.modPlayerPts(player, 1)

            self.printLineBreak(text=f"This turn is over", dbl_space=True)
            #print(f"turnKey: {self.turnKey} lastTurn: {self.lastTurn} currentTurn: {self.currentTurn} mextTurn: {self.nextTurn} lastMove: {self.lastMove}")
            return True
        except:
            print("something failed in endTurn")
            return False

    def possible_moves(self, board, height=5, length=8):
        open_spaces = []
        taken = []
        rows = [(height * length) - length + i for i in range(length)]
        for i in rows:
            if board[i]['color'] == -1:
                #print(str(i) + " is a possible move")
                open_spaces.append(i)
            if board[i]['color'] in [1, 2]:
                taken.append(i)
        for k in taken:
            while k - length <= 0:
                if board[k]['color'] in (1, 2) and board[k - 8]['color'] == -1:
                    open_spaces.append(k - length)
                    break

            # while k - 8 >= 0 and board[k]['color'] in (1,2):
            #   print(k,board[k]['color'],k-8,board[k-8]['color'])
            #   if board[k-8]['color'] == -1:
            #       open_spaces.append(k)
            #   k=k-8

                #print(str(j) + " is occupied by "+ str(colors[board[i]['color']]))
        if len(open_spaces) > 1:
            return open_spaces
        return False
        while (board[j]['color'] in [1, 2]) and (j > -1):
            j = j - 8
            try:
                open_spaces.append(j)
            except:
                print("vreak")
        if len(open_spaces) == 0:
            return game_over(reason=-1, data=self.whose_turn())
        return(open_spaces)
# if turnKey == True nextTurn is the turn in progress lastMove is the most recent piece placed at a space and

    def check_move(self, player, desiredMove):

        #       if not self.lastMove:
        #           print("this is the first turn")
        if self.lastMove != None:
            if self.board[desiredMove]['occupied'] == True:
                print("the desired space is occuppied")
                return False
            if self.board[self.lastMove]['color'] == player:
                print('this player took the last turn ')
                return False
            if desiredMove not in possible_moves(self.board):
                print("the desired move is not currently accessible")
                return False
        return True

    def take_move(self, player, choice):

        self.board[choice]['color'] = self.currentPlayer
        self.board[choice]['occupied'] = True
        self.board[choice]['moveNumber'] = self.currentTurn
        self.printLineBreak(text="Move Taken", prefix=True)
        if self.serialConnected:
            time.sleep(1)
            self.output_to_serial(choice, player)
        return self.end_turn(self.currentPlayer, choice)

    def define_win_dim(self):
        l = self.length
        h = self.height
        self.diag1 = [-(l - 1) * 3, -(l - 1) * 2, -(l - 1),
                      0, l - 1, (l - 1) * 2, (l - 1) * 3]
        self.diag2 = [-(l + 1) * 3, -(l + 1) * 2, -(l + 1),
                      0, l + 1, (l + 1) * 2, (l + 1) * 3]
        self.vertical = [-3 * l, -2 * l, -l, 0, l, 2 * l, 3 * l]
        self.horizontal = [-4, -3, -2, -1, 0, 1, 2, 3, 4]

    def check_spillover(self, array, direction='vertical'):
        k = int(game.length / array[0])
        frame = [i for i in range(k * self.length, self.length * (k + 1))]
        frame2 = [i for i in range(
            self.length * int(array[0] / self.length), self.length * (int(array[0] / self.length) + 1))]
        print(f'{frame=}, {array=}')
        if direction == 'vertical':
            for i in array:
                if i not in frame:
                    return False
            return True
        if direction == 'horizontal':
            for i in array:
                if i not in frame2:
                    return False
            return True

    def locate_col(self, array):
        print(array)
        sequence = []
        for address in array:
            prel = (int(address / game.length) + 1) * self.length - address
            sequence.append(prel)
        result = sorted(sequence) == list(
            range(min(sequence), max(sequence) + 1))
        self.printLineBreak(dbl_space=True, text=f'{sequence:}')
        return result

    # checks if move results in a connect 4
    def check_win(self, player, last_move, board=None):
        self.printLineBreak(
            text=f'Checking for Win with {last_move:}', prefix=True)
        l = self.length
        h = self.height
        if not board:
            board = self.board
        sequence = []
        self.printLineBreak(text="Checking Diagonals", prefix=True)
        for i in self.diag1:
            if 0 <= i + last_move < (self.height * self.length) - 1:
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                else:
                    sequence = []
                if len(sequence) == 2:
                    print('connect2!')
                if len(sequence) == 3:
                    print('connect 3!')
                if len(sequence) == 4:
                    if self.locate_col(sequence):
                        return True, player, sequence, last_move
        sequence = []
        for i in self.diag2:
            if 0 <= i + last_move < (self.length * self.height):
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                if len(sequence) == 4:
                    sequence.reverse()
                    fa = self.locate_col(sequence)
                    if fa:
                        return True, player, sequence, last_move
        sequence = []

        self.printLineBreak(text="Checking Laterals", prefix=True)
        sequence = []
        for i in self.vertical:
            if 0 <= i + last_move < (self.height * self.length):
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                if len(sequence) == 4:
                    return True, player, sequence, last_move

        sequence = []
        self.printLineBreak(text="checking horizontal")

        for i in self.horizontal:
            print(f"{i=}")
            if (last_move + i < (self.length * self.height)) and (last_move + i > -1):
                print(f"{last_move=},{last_move+i=},{board[last_move+i]=}")
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                    if len(sequence) == 4:
                        fa = self.check_spillover(
                            sequence, direction='horizontal')
                        if fa:
                            return True, player, sequence, last_move
                        else:
                            sequence = []
                else:
                    sequence = []
            # if (i*(i%self.length))<=i+last_move<(i+1)*(i%self.length):

        return False, player, sequence, last_move

    def game_over(self, reason, data):
        reasons = {0: {'no space for moves': "last_player\'s"},  # code:{reason for end:data field should include this inforamation
                   1: {'Connect 4!': "player number"},
                   2: {'Empty': True},
                   -1: {'youNeedToModifyThis': "orDeleteThis"}}
        if reason in reasons.keys():
            if reason == 1:
                self.winner = data

    if self.modPlayerPts(cumulative=True):

        self.logger.info('Cumulative Scores updated yay!')
        print(
            f"\nreason:{reasons[reason].keys():},winner:{self.winner:} 🔵>🟢||🔴>🟡")
    self.clear_display()

    print(
        f"reason:{reasons[reason].keys():},winner:{self.winner:} 🔵>🟢||🔴>🟡")


>>>>>> > b02
    self.inProgress = False
    self.printLineBreak()
    return self.inProgress

    # if self.serialConnected:
    #       self.ardu.close()
    #+ i for i in range(8)]def #pcvpc(self):


if __name__ == '__main__':

    def draw_board(boardDict, height=5, length=8):
        length = game.length
        height = game.height
        print('0\t| ', end='')
        for key in boardDict.keys():
            piece = game.colors[boardDict[key]['color']]
            print(piece + ' | ', end='')
            if int(key) != (height * length) - 1 and (int(key) + 1) % length == 0:
                print(f'\n{str(key+1)}\t| ', end='')

    def possible_moves(board):
        open_spaces = []
        rows = [(game.length * game.height) -
                game.length + i for i in range(game.length)]
        for i in rows:
            if board[i]['color'] == -1:
                #print(str(i) + " is a possible move")
                open_spaces.append(i)
            if board[i]['color'] in [1, 2]:
                j = i
                #print(str(j) + " is occupied by "+ str(colors[board[i]['color']]))
                while board[j]['color'] in [1, 2] and j - game.length > 0:
                    j = j - game.length
                    try:
                        if board[j]['color'] == -1:
                            open_spaces.append(j)
                    except:
                        print("vreak")
        return open_spaces

    game = gameObject(length=8, height=5)
    num_times = game.iterations

    def confirm_runtime():
        num_times = False
        confirm = False
        while not confirm:
            while not num_times:
                num_times = input(
                    'press enter number of iterations to continue: ')
                try:
                    num_times = int(num_times)
                except:
                    num_times = False
            check = input(
                f'You entered {num_times:}. Confirm by re-entering this value:')
            try:
                check = int(check)
            except:
                num_times = False
            if check != num_times:
                num_times = False
            if check == num_times:
                confirm = True
                return num_times

    def process_tally(tally):
        aggre = {1: {'winningMoves': [], 'count': 0},
                 2: {'winningMoves': [], 'count': 0}}
        for i in tally:
            aggre[i[0]]['winningMoves'].append([i[1], i[2]])
            aggre[i[0]]['count'] += 1
        print(aggre)
        return aggre

    num_times = confirm_runtime()
>>>>>> > b02
    tally = []
    # if game.serialConnected:
    #   game.init_serial()
    for tt in range(num_times):
        game = gameObject(length=8, height=8)
        game.start_game()
        print(game.length, game.height)
        while game.inProgress:

            for i in range(len(game.board.keys())):

                # if game.waitTime > 0:
                    # time.sleep(game.waitTime)

                if game.debug:
                    wait = input("press enter to continue")

                #game.check_move(game.board,  game.currentPlayer, random.choice(selectFrom))
                while game.inProgress:
                    selectFrom = possible_moves(game.board)
                    if len(selectFrom) > 0:
                        choice = random.choice(selectFrom)

                        while game.board[choice]['color'] > 0:
                            choice = random.choice(selectFrom)

                        game.start_turn(game.currentPlayer,
                                        random.choice(selectFrom))
                        #print(f"\nlast move: {game.lastMove} current move: {game.currentMove}")
                        game.draw_board(game.board)
                        game.switch_player()

                    else:

                        print("there are no spaces available")
                        game.game_over(0, game.currentPlayer)
                        print(game.printLineBreak())
        print(game.isWinner)
        tally.append([game.isWinner[1], game.isWinner[2], game.isWinner[3]])

        # game.whose_turn()
    process_tally(tally)
