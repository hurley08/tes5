'''
Connect 4 Class that pits twp dumb players that randomly selects from a choice of possible moves

Arguments:
Full breakdown will be included in the readme eventually.
notable arguments in __init__ are
iterations                      number of games to play. Set preemptively or set disable_interaction to False if a prompt at launch is preferred
height/length                   dimensions of the board. These default to 5 and height respectively
drawBoardTurn/game_over         draw board at the end of turn / draw board at end of game
commsArduino                    aruino connected to a 16x16 led matrix can visualize the game
logLevel                        used to specify the severity of an before

Exceptions:
NA

Returns:
NA

Outputs:
Visualization of board at end of every game (if enabled)
crude metrics for each player
Requires:
load_dict
time
'''


# import serial
import pdb
import coverage
import math
import cProfile
import random
import logging
from statistics import median, mode
import time
# board needs to be made into a subclass or separate class

cov = coverage.Coverage()
cov.start()


class gameModel():
    def __init__(self, game=' '):
        self.game = game
        self.player1 = 0
        self.player2 = 0


class gameObject():
    # 2 and 3 pieces captured in a window earns player points and penalizes opponent
    rewards = {2: 2, 3: 5, -2: -1, -3: -2, 4: 10, -4: -12}

    def __init__(self, waitTime=0.1, disable_interaction=True, iterations=100, board=None, height=5, length=8, isBot=True, drawBoardTurn=True, drawBoardGameOver=True, logLevel='CRITICAL', commsArduino=False):
        self.colors = {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}
        self.dummy = 5
        self.waitTime = waitTime
        self.height = height
        self.length = length
        self.board = board
        # print('self init')
        self.isBot = isBot
        self.debug = False
        self.win_length = 4
        self.inProgress = False
        self.winner = False
        self.playerCumulative = {1: 0, 2: 0}
        self.drawBoardTurn = drawBoardTurn
        self.drawBoardGameOver = drawBoardGameOver

        self.serialConnected = False
        self.commsArduino = commsArduino
        if self.serialConnected == False and self.commsArduino == True:
            self.init_serial()

        if not disable_interaction:
            self.iterations = self.confirm_runtime()
        if disable_interaction:
            self.iterations = iterations
        if iterations < 10 and drawBoardTurn == None:
            self.drawBoardTurn = True
        if iterations > 20 and drawBoardTurn == None:
            self.drawBoardTurn = False
        self.logLevel = logLevel
        # logger.debug('{self.logLevel set to {logLevel:}}')
        logger, log = self.init_logger(logLevel)
        self.logger = logger
        self.log = log

    def init_serial(self):
        reAttempts = 5
        self.logger.warning(
            'There must be an arduino connected and enumerated on the port listed in ardu.port or this will fail')
        if not self.serialConnected:
            self.ardu.port = '/dev/tty.usbserial-0001'
            self.ardu.baudrate = 115200
            self.ardu = serial.Serial()
            self.serialConnected = True

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

    def clear_display(self):
        for i in range(self.height * self.length):
            if self.commsArduino:
                self.output_to_serial(i, 0)

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

        self.winner = False
        self.create_board(height=self.height, length=self.length)
        self.logger.info('NEW GAME')
        self.turnLog = self.init_log()
        self.logger.debug("init log")
        self.currentPlayer = random.choice([1, 2])
        self.logger.info(
            "starting player chosen: Player {self.currentPlayer}\n\n\n")
        self.logger.info("setting game parameters")
        self.define_win_dim()
        self.turnKey = False
        self.lastTurn = 0
        self.currentTurn = 0
        self.nextTurn = 1
        self.lastMove = None
        self.currentMove = None
        self.logger.info("All's tweaked. Commencing game")
        self.playerScore = {1: 0, 2: 0}
        return self

    def switch_player(self):
        self.currentPlayer = 1 if self.currentPlayer == 2 else 2
        return self.currentPlayer

    def printLineBreak(self, text='', dbl_space=False, prefix=False):
        filler = '='
        buffer = 100 - len(text)
        prefixStr = filler * 25
        if not prefix:
            prefixStr = ''
            buffer += 25

        dbl_space = '\n\n' if dbl_space else None

        print(f'{prefixStr}{text}{filler*buffer:}', end=dbl_space)

    def modPlayerPts(self, player=-1, delta=0, cumulative=False):
        if not cumulative:
            if player > 0:
                player = self.currentPlayer
            else:
                player = 1 if self.currentPlayer == 2 else 2
            try:
                self.playerScore[player] = self.playerScore[player] + delta
                self.logger.info(f"{player=} score was updated by {delta=}")
                print(f"{player=} score was updated by {delta=}")
                return True
            except:
                self.logger.warning(f"{player=} score NOT updated by {delta=}")
                print(f"{player=} score NOT updated by {delta=}")
                return False
        if cumulative:
            self.playerCumulative[1] += self.playerScore[1]
            self.playerCumulative[2] += self.playerScore[2]
            self.logger.info(f'\nSeries tally was updated to reflect')
            self.logger.debug(
                '{self.playerScore[1]=} was added to {self.playerCumulative[1]=}\n{self.playerScore[2]=} was added to {self.playerCumulative[2]=}')
            return True

    def create_board(self, height=5, length=8):
        self.height = height
        self.length = length
        boardIndex = {}
        for i in range(height * length):
            boardIndex.update(
                {i: {'color': -1, 'occupied': False, 'moveNumber': -1}})
        self.board = boardIndex
        return boardIndex

    def find_row(self, length=8, target=0):
        length = int(length)
        target = int(target)
        lbound = math.floor(target / length)
        rbound = math.ceil(target / length)
        window = [i for i in range(length * lbound, length * rbound)]
        return window

    def confirm_runtime(self):
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

    def init_log(self):
        moveLog = {}
        log = (i + 1 for i in range(len(self.board)))
        for i in log:
            moveLog[i] = False
        return moveLog

    def draw_board(self, board=None, height=5, length=8):
        height = self.height
        length = self.length
        board = self.board if board == None else board
        cipher = list(self.board.keys())
        print('0\t| ', end='')
        for key in cipher:
            piece = self.colors[self.board[key]['color']]
            print(piece + ' | ', end='')
            if int(key) != height * length and (int(key) + 1) % length == 0 and int(key) + 1 < len(cipher):
                print(f'\n{str(key+1)}\t| ', end='')

    def begin_turn(self, player, isBot):
        print('begin_turn')
        if self.currentTurn > 1:
            while self.lastMove[1] == self.currentPlayer:
                self.switch_player()
        # to increment turn variables, check player turn, and call choose_move
        if isBot != self.isBot:
            print("is this supposed to be a bot?")
        self.logger.info("Starting  Turn")
        self.turnKey = True
        msg = f"{self.lastTurn=}, {self.currentTurn=}, {self.nextTurn=}, {self.lastMove=}, {self.currentPlayer=}"

        self.printLineBreak(text=msg, dbl_space=False)
        print(self.currentPlayer)
        msg = f"current player: {self.currentPlayer}"
        self.logger.info(msg)

        # self.printLineBreak(text=msg, prefix=True)
        # print(f"lastTurn: {self.lastTurn} currentTurn: {self.currentTurn} nextTurn: {self.nextTurn}")
        if player != self.currentPlayer:
            print("Was a turn skipped?")
        self.lastTurn = self.currentTurn
        self.currentTurn = self.nextTurn
        self.nextTurn = self.nextTurn + 1
        return self.choose_move(player=player, isBot=self.isBot)

    def choose_move(self, player=0, isBot=True):
        print('choose_move')
        # use to identify which space player wants to occupy next
        choice = None
        choiceAccepted = False
        openSpaces = self.possible_moves(self.board)
        print(openSpaces)

        if isBot == False:
            while choiceAccepted == False and openSpaces != []:
                choice = int(
                    input(f'Choose a space on the board. (0-{self.length*self.height-1}).'))
                choiceAccepted = self.check_move(
                    self.currentPlayer, choice)
        if isBot == True:
            if openSpaces == False:
                self.game_over(0, self.currentPlayer)
                return False
                # this is where machine must decide what space to play
            elif len(openSpaces) > 1:
                choice = random.choice(openSpaces)
            elif len(openSpaces) == 1:
                choice = openSpaces[0]

            choiceAccepted = self.check_move(self.currentPlayer, choice)

        return self.take_move(self.currentPlayer, choice)

    def draw_win(self, sequence, board=None):
        if not board:
            board = self.board
        for i in sequence:
            f = self.colors[board[i]['color']]
            board[i]['color'] = f.upper()
        return board

    def end_turn(self, player, choice):
        print('end_turn')
        if self.drawBoardTurn:
            self.draw_board(self.board)
        self.isWinner = self.check_win(player, choice, self.board)
        print(self.isWinner)
        if isWinner[0] == True:
            pdb.set_trace()
            print('DOES THIS EVEN')
            return self.game_over(reason=1, player=player)
        self.logger.info("This turn is over")

        self.switch_player()
        return True

        self.printLineBreak(self.isWinner)
        self.printLineBreak(self.isWinner)

        # self.printLineBreak(self.isWinner[0])

       # if self.isWinner[2] > 0:
        #    self.modPlayerPts(
        #        player=player, delta=self.rewards[isWinner[2]])
        #    self.modPlayerPts(
        #        player=-player, delta=self.rewards[-isWinner[2]])
        #print("I've Returned")

    def possible_moves(self, board):
        open_spaces = []
        rows = [(self.length * self.height) -
                self.length + i for i in range(self.length)]
        for i in rows:
            if board[i]['color'] == -1:
                # print(str(i) + " is a possible move")
                open_spaces.append(i)
            if board[i]['color'] in [1, 2]:
                j = i
                # print(str(j) + " is occupied by "+ str(colors[board[i]['color']]))
                while board[j]['color'] in [1, 2] and j - self.length > 0:
                    j = j - self.length
                    try:
                        if board[j]['color'] == -1:
                            open_spaces.append(j)
                    except:
                        pdb.set_trace()
                        self.logger.error("Freak")
        self.currentAvailableSpaces = open_spaces
        print(open_spaces)
        if len(open_spaces) < 1:
            return self.game_over(0, self.currentPlayer)
        return open_spaces

    def check_move(self, player, desiredMove):
        print('check_move')
        if desiredMove not in self.currentAvailableSpaces:
            print('illegal move')
            return False
        if self.board[desiredMove]['occupied'] == True:
            print('occupied')
            return False
        if self.currentPlayer != player:
            print('wrong player')
            return False
        return True

    def take_move(self, player, choice):
        print('take_move')
        # updates the board and calls end_turn

        try:
            self.board[choice] = {
                'color': player, "occupied": True, 'moveNumber': self.currentTurn}
            self.logger.info("Move taken")
            self.modPlayerPts(player=player, delta=1)
            if self.serialConnected:
                time.sleep(1)
                self.output_to_serial(choice, player)
            self.lastMove = self.currentMove
            self.currentMove = [choice, self.currentPlayer]
            self.logger.info("Move Suceeded")

            return self.end_turn(self.currentPlayer, choice)
        except:
            self.logger.error("Something failed in take move")
            return False
        return True

    def define_win_dim(self):
        l = self.length
        n = self.win_length
       # h = self.height
        diag1 = [i * (l - 1) for i in range(-n + 1, n)]
        diag2 = [i * (l + 1) for i in range(-n + 1, n)]
        vertical = [i * l for i in range(-n + 1, n)]
        horizontal = [i for i in range(-n + 1, n)]
        self.diag1 = diag1
        self.diag2 = diag2
        self.vertical = vertical
        self.horizontal = horizontal

    def check_spillover(self, array, direction='vertical'):
        k = int(self.length / array[0])
        frame = [i for i in range(k * self.length, self.length * (k + 1))]
        frame2 = [i for i in range(
            self.length * int(array[0] / self.length), self.length * (int(array[0] / self.length) + 1))]

        self.logger.debug('{frame=}, {array=}')
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
        self.logger.debug(array)
        sequence = []
        for address in array:
            prel = (int(address / self.length) + 1) * self.length - address
            sequence.append(prel)
        result = sorted(sequence) == list(
            range(min(sequence), max(sequence) + 1))
        self.logger.debug('%s', [sequence])
        return result

        # checks if move results in a connect 4

    def check_win(self, player, target, board=None):
        print('check_win')
       # print(\f'{player==self.currentPlayer=}')
        self.logger.info('Checking for Win with {target:}')
        l = self.length
        h = self.height
        if not board:
            board = self.board
        sequence = []
        max_combo = 0

        self.logger.info("Checking Diagonals")
        for i in self.diag1:
            if 0 <= i + target < (h * l) - 1:
                if board[target + i]['color'] == player:
                    sequence.append(i + target)
                else:
                    sequence = []
                if len(sequence) == 4:
                    if self.locate_col(sequence):
                        return True, player, sequence, target
            max_combo = len(sequence) if len(
                sequence) > max_combo else max_combo
        sequence = []

        for i in self.diag2:
            if 0 <= i + target < (h * l):
                if board[target + i]['color'] == player:
                    sequence.append(i + target)
                if len(sequence) == 4:
                    sequence.reverse()
                    fa = self.locate_col(sequence)
                    if fa:
                        return True, player, sequence, target
            max_combo = len(sequence) if len(
                sequence) > max_combo else max_combo
        sequence = []

        self.logger.info("Checking Laterals")
        sequence = []
        for i in self.vertical:
            if 0 <= i + target < (h * l):
                if board[target + i]['color'] == player:
                    sequence.append(i + target)
                if len(sequence) == 2:
                    self.logger.debug('connect2!')
                    # self.modPlayerPts(player=player, delta=3)
                    # self.modPlayerPts(player=player * -1, delta=-1)
                if len(sequence) == 3:
                    self.logger.debug('connect3!')
                    # self.modPlayerPts(player=player, delta=5)
                    # self.modPlayerPts(player=player * -1, delta=-3)
                if len(sequence) == 4:
                    return True, player, sequence, target
            max_combo = len(sequence) if len(
                sequence) > max_combo else max_combo

        sequence = []

        self.logger.info("checking horizontal")
        row = self.find_row(self.length, target)
        self.logger.info(f'{row=}, {target=}, {row=}')
        combo = []

        for i in self.wind(row, self.win_length):
            for j in i:
                combo.append(
                    1) if board[j]['color'] == player else combo.append(0)
            if sum(combo) == 4:
                return True, player, i, target
            if sum(combo) < 4:
                max_combo = sum(combo) if sum(combo) > max_combo else max_combo
            combo = []
        return False, player, max_combo, target

    def wind(self, arr, k):
        for i in range(len(arr) - k + 1):
            yield arr[i:i + k]

    def game_over(self, reason, data):
        print('game_over')
        reasons = {0: {'no space for moves': "last_player\'s"},  # code:{reason for end:data field should include this inforamation
                   1: {'Connect 4!': "player number"},
                   2: {'Empty': True},
                   -1: {'youNeedToModifyThis': "orDeleteThis"}}

        if reason in reasons.keys():
            if reason == 1:
                self.winner = data
                self.logger.info(
                    f'GAME OVER, Winner: {self.isWinner[1]}, sequence: {self.isWinner[2]}, lastMove: {self.isWinner[3]}')
                jsd = self.draw_win(self.isWinner[2])
                if self.drawBoardGameOver:
                    self.draw_board(jsd)
                self.modPlayerPts(player=self.winner, delta=10)
                self.modPlayerPts(player=self.winner * -1, delta=-12)
            if reason == 0:
                self.logger.info(
                    f'GAME OVER, NO MOVES LEFT')
        if self.modPlayerPts(cumulative=True):
            self.logger.info('Cumulative Scores updated yay!')
        if self.serialConnected:
            self.ardu.close()
            self.clear_display()

        print(
            f"\nreason:{reasons[reason].keys():},winner:{self.winner:} 🔵>🟢||🔴>🟡")

        self.inProgress = False
        return self.inProgress

        # self.printLineBreak()

    #+ i for i in range(8)]def #pcvpc(self):

    def process_tally(self, tally):
        #
        aggre = {1: {'winningMoves': [], 'winCount': 0, 'score': 0, 'numScore': 0},
                 2: {'winningMoves': [], 'winCount': 0, 'score': 0, 'numScore': 0}}
        for i in tally:
            aggre[i[0]]['winningMoves'].append([i[1], i[2]])
            aggre[i[0]]['winCount'] += 1
            aggre[i[0]]['score'] += i[3][i[0]]
            aggre[i[0]]['numScore'] += 1
        self.logger.info('\nwinner\t winning seq.\twinning move\tplayer:score')
        for i in tally:
            self.logger.debug('')
            for j in i:
                self.logger.debug(str(j) + '\t')
        p1 = aggre[1]['winCount']
        p2 = aggre[2]['winCount']
        p1numScoreArray = []
        p2numScoreArray = []
        for i in tally:
            p1numScoreArray.append(i[3][1])
            p2numScoreArray.append(i[3][2])
        self.logger.debug('%s', p1numScoreArray)
        self.logger.debug('%s', p2numScoreArray)

        # print(
        #    f'\nOf {p1+p2:} games, Player 1 won {p1/(p1+p2)*100:.2f}% and Player 2 won {p2/(p1+p2)*100:.2f}% ')
        # print(
        #    f'\nPlayer 1 mean:{sum(p1numScoreArray)/len(p1numScoreArray):.2f}pts max:{max(p1numScoreArray):} min:{min(p1numScoreArray):} and Player 2 averaged {sum(p1numScoreArray)/len(p2numScoreArray):.2f}pts  max:{max(p2numScoreArray):} min:{min(p2numScoreArray):} ')
        print(f'\n\t\tPlayer 1\t\tPlayer 2 ')
        print(
            f"\nwins#:\t\t{aggre[1]['winCount']}\t\t\t{aggre[2]['winCount']}")
        print(f'\nwin%:\t\t{p1/(p1+p2)*100:.2f}%\t\t\t{p2/(p1+p2)*100:.2f}%')
        print(
            f'\nmean(pts):\t{sum(p1numScoreArray)/len(p1numScoreArray):.2f}\t\t\t{sum(p2numScoreArray)/len(p2numScoreArray):.2f}')
        print(
            f'\nmax(pts):\t{max(p1numScoreArray):}\t\t\t{max(p2numScoreArray):}')
        print(
            f'\nmedn(pts):\t{median(p1numScoreArray):}\t\t\t{median(p2numScoreArray):}')
        print(
            f'\nmode(pts):\t{mode(p1numScoreArray):}\t\t\t{mode(p2numScoreArray):}')
        print(
            f'\nmin(pts):\t{min(p1numScoreArray):}\t\t\t{min(p2numScoreArray):}')
        # print('\n', aggre)
        return aggre

    def inProgressState(self):
        return self.inProgress


def main2():

    start = time.time()

    game = gameObject(length=8, height=5)
    num_times = game.iterations
    tally = []
    # if game.serialConnected:
    #   game.init_serial()
    for tt in range(num_times):

        game.start_game()
        if game.debug:
            print(game.length, game.height)
        while game.inProgress:

            for i in range(len(game.board.keys())):

                # if game.waitTime > 0:
                    # time.sleep(game.waitTime)

                if game.debug:
                    wait = input("press enter to continue")

                # game.check_move(game.board,  game.currentPlayer, random.choice(selectFrom))
                while game.inProgress:
                    selectFrom = game.possible_moves(game.board)
                    if len(selectFrom) > 0:
                        choice = random.choice(selectFrom)

                        while game.board[choice]['color'] > 0:
                            choice = random.choice(selectFrom)

                        game.start_turn(game.currentPlayer,
                                        random.choice(selectFrom))
                        # print(f"\nlast move: {game.lastMove} current move: {game.currentMove}")
                        game.switch_player()

                    else:

                        print("there are no spaces available")
                        if game.debug:
                            print(game.printLineBreak())
        print(game.isWinner)
        tally.append([game.isWinner[1], game.isWinner[2],
                      game.isWinner[3], game.playerScore])

        # game.whose_turn()
    results = game.process_tally(tally)
    print("--- %s seconds ---" % (time.time() - start))
    game.logger.info("--- completed in %s seconds ---" %
                     (time.time() - start))
# ser.close()


def main():

    start = time.time()

    game = gameObject(length=8, height=5)
    num_times = game.iterations
    tally = []
    # if game.serialConnected:
    #   game.init_serial()
    inProgress = True
    kill = 0
    for tt in range(num_times):

        game.start_game()

        while game.inProgress == True and kill != 1:
            for i in range(len(game.board.keys())):

                # if game.waitTime > 0:
                    # time.sleep(game.waitTime)

                if game.debug:
                    wait = input("press enter to continue")

                game.begin_turn(game.currentPlayer, True)
                if game.inProgressState() == False:
                    game.inProgress = False
                    break

            if game.inProgressState() == False:
                inProgress = False
                kill = 1
                break
        # game.whose_turn()
    print(tally)
    results = game.process_tally(tally)
    print("--- %s seconds ---" % (time.time() - start))
    game.logger.info("--- completed in %s seconds ---" %
                     (time.time() - start))
# ser.close()


if __name__ == '__main__':

    cProfile.run('main()')

    cov.stop()
    cov.save()
