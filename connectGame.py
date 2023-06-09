import serial
import coverage
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
                self.logger.debug('Serial connection established. setting serialConnected')
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
        for i in range(self.height*self.length):
            output_to_serial(i, 0)


    def output_to_serial(self, space, player):
        colorr = {0:{'r':0, 'g':0, 'b':0},
                  1: {'r': 50, 'g': 150, 'b': 50},
                  2: {'r': 200, 'g': 100, 'b': 0}}
        text = f"{space}, {colorr[player]['r']}, {colorr[player]['g']}, {colorr[player]['b']}"

        self.ardu.write(f'<setPixelColor, {text}>\0'.encode())

    def start_game(self):
        if self.commsArduino == True and self.serialConnected == False:
            self.init_serial()
        self.inProgress = True

        self.winner = False
        self.board = self.create_board(height=self.height, length=self.length)
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
        self.currentTurn = 1
        self.nextTurn = 2
        self.lastMove = None
        self.currentMove = None
        self.logger.info("All's tweaked. Commencing game")
        self.playerScore = {1: 0, 2: 0}
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

    def modPlayerPts(self, player=-1, delta=0, cumulative=False):
        if not cumulative:
            if player > 0:
                player = self.currentPlayer
            else:
                player = 1 if self.currentPlayer == 2 else 2
            try:
                self.playerScore[player] = self.playerScore[player] + delta
                self.logger.info(f"{player=} score was updated by {delta=}")
                return True
            except:
                self.logger.warning(f"{player=} score NOT updated by {delta=}")
                return False
        if cumulative:
            self.playerCumulative[1] += self.playerScore[1]
            self.playerCumulative[2] += self.playerScore[2]
            self.logger.info(f'\nSeries tally was updated to reflect')
            self.logger.debug(
                '\n{self.playerScore[1]=} was added to {self.playerCumulative[1]=}\n{self.playerScore[2]=} was added to {self.playerCumulative[2]=}')

    def create_board(self, height=5, length=8):
        height = self.height
        length = self.length
        boardIndex = {}
        for i in range(height * length):
            boardIndex.update(
                {i: {'color': -1, 'occupied': False, 'moveNumber': -1}})
        return boardIndex

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

        self.logger.info("Starting  Turn")
        self.turnKey = True
        msg = f"{self.lastTurn=}, {self.currentTurn=}, {self.nextTurn=}, {self.lastMove=}, {self.currentPlayer=}"

        # self.printLineBreak(text=msg, dbl_space=False)

        msg = f"current player: {game.currentPlayer} desired move: {choice}"
        self.logger.info(msg)

        # self.printLineBreak(text=msg, prefix=True)
        # print(f"lastTurn: {self.lastTurn} currentTurn: {self.currentTurn} nextTurn: {self.nextTurn}")
        self.lastTurn = self.currentTurn
        self.currentTurn = self.nextTurn
        # self.nextTurn = self.nextTurn + 1

        openSpaces = self.possible_moves(self.board)
        choiceAccepted = self.check_move(self.currentPlayer, choice)
        while choiceAccepted == False:
            if len(openSpaces) < 1:
                return False

            choiceAccepted = self.check_move(self.currentPlayer, int(
                input('Integers 1-39 represent the spaces on the board. Choose one')))
        if choiceAccepted:
            self.currentMove = choice

            self.logger.info("Submitting Move")
        return self.take_move(self.currentPlayer, choice)

    def draw_win(self, sequence, board=None):
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
            self.modPlayerPts(player=player, delta=10)
            self.modPlayerPts(player=player * -1, delta=-12)
            self.logger.info(
                f'GAME OVER, Winner: {isWinner[1]}, sequence: {isWinner[2]}, lastMove: {isWinner[3]}')
            jsd = self.draw_win(isWinner[2])
            if self.drawBoardGameOver:
                draw_board(jsd)
            self.game_over(1, player)
            return True

        try:
            if self.drawBoardTurn:
                self.draw_board(self.board)
            self.modPlayerPts(player=player, delta=1)
            self.logger.info("This turn is over")
            return True
        except:
            logger.Error("something failed in endTurn")
            return False

    def possible_moves(self, board, height=5, length=8):
        open_spaces = []
        taken = []
        rows = [(height * length) - length + i for i in range(length)]
        for i in rows:
            if board[i]['color'] == -1:
                # print(str(i) + " is a possible move")
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

                # print(str(j) + " is occupied by "+ str(colors[board[i]['color']]))
        if len(open_spaces) > 1:
            return open_spaces
        return False
        while (board[j]['color'] in [1, 2]) and (j > -1):
            j = j - 8
            try:
                open_spaces.append(j)
            except:
                logger.error("Something in possible_moves() failed")
        if len(open_spaces) == 0:
            return self.game_over(reason=-1, data=self.whose_turn())
        return(open_spaces)
# if turnKey == True nextTurn is the turn in progress lastMove is the most recent piece placed at a space and

    def check_move(self, player, desiredMove):

        #       if not self.lastMove:
        #           print("this is the first turn")
        if self.lastMove != None:
            if self.board[desiredMove]['occupied'] == True:
                log.error("the desired space is occuppied")
                return False
            if self.board[self.lastMove]['color'] == player:
                log.error('this player took the last turn ')
                return False
            if desiredMove not in possible_moves(self.board):
                log.error("the desired move is not currently accessible")
                return False
        return True

    def take_move(self, player, choice):

        self.board[choice]['color'] = self.currentPlayer
        self.board[choice]['occupied'] = True
        self.board[choice]['moveNumber'] = self.currentTurn
        self.logger.info("Move taken")
        if self.serialConnected:
            time.sleep(1)
            self.output_to_serial(choice, player)
        return self.end_turn(self.currentPlayer, choice)

    def define_win_dim(self):
        l = self.length
       # h = self.height
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
            prel = (int(address / game.length) + 1) * self.length - address
            sequence.append(prel)
        result = sorted(sequence) == list(
            range(min(sequence), max(sequence) + 1))
        self.logger.debug('%s', [sequence])
        return result

        # checks if move results in a connect 4

    def check_win(self, player, last_move, board=None):
       # print(\f'{player==self.currentPlayer=}')
        self.logger.info('Checking for Win with {last_move:}')
        l = self.length
        h = self.height
        if not board:
            board = self.board
            board = self.board
        sequence = []
        self.logger.info("Checking Diagonals")
        for i in self.diag1:
            if 0 <= i + last_move < (h * l) - 1:
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                else:
                    sequence = []
                if len(sequence) == 2:
                    self.logger.debug('connect2!')
                   # self.modPlayerPts(player=player, delta=3)
                   # self.modPlayerPts(player=player * -1, delta=-1)
                if len(sequence) == 3:
                    self.logger.debug('connect3!')
                   # self.modPlayerPts(player=player, delta=5)
                   # self.modPlayerPts(player=player * -1, delta=-3)
                if len(sequence) == 4:
                    if self.locate_col(sequence):
                        return True, player, sequence, last_move
        sequence = []
        for i in self.diag2:
            if 0 <= i + last_move < (h * l):
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                if len(sequence) == 2:
                    self.logger.debug('connect2!')
                   # self.modPlayerPts(player=player, delta=3)
                   # self.modPlayerPts(player=player * -1, delta=-1)
                if len(sequence) == 3:
                    self.logger.debug('connect3!')
                    # self.modPlayerPts(player=player, delta=5)
                    # self.modPlayerPts(player=player * -1, delta=-3)
                if len(sequence) == 4:
                    sequence.reverse()
                    fa = self.locate_col(sequence)
                    if fa:
                        return True, player, sequence, last_move
        sequence = []

        self.logger.info("Checking Laterals")
        sequence = []
        for i in self.vertical:
            if 0 <= i + last_move < (h * l):
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                if len(sequence) == 2:
                    self.logger.debug('connect2!')
                    # self.modPlayerPts(player=player, delta=3)
                    # self.modPlayerPts(player=player * -1, delta=-1)
                if len(sequence) == 3:
                    self.logger.debug('connect3!')
                    # self.modPlayerPts(player=player, delta=5)
                    # self.modPlayerPts(player=player * -1, delta=-3)
                if len(sequence) == 4:
                    return True, player, sequence, last_move

        sequence = []

        self.logger.info("checking horizontal")

        for i in self.horizontal:

            self.logger.debug(f"{i=}")
            if (last_move + i < (h * l)) and (last_move + i > -1):

                self.logger.debug(
                    "{last_move=},{last_move+i=},{board[last_move+i]=}")
                if board[last_move + i]['color'] == player:
                    sequence.append(i + last_move)
                    if len(sequence) == 2:
                        self.logger.debug('connect2!')
                        # self.modPlayerPts(player=player, delta=3)
                        # self.modPlayerPts(player=player * -1, delta=-1)
                    if len(sequence) == 3:
                        self.logger.debug('connect3!')
                        # self.modPlayerPts(player=player, delta=5)
                        # self.modPlayerPts(player=player * -1, delta=-3)
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
        self.inProgress = False

        # self.printLineBreak()
        return self.inProgress

    #+ i for i in range(8)]def #pcvpc(self):

    def process_tally(self, tally):
        aggre = {1: {'winningMoves': [], 'count': 0, 'score': 0, 'numScore': 0},
                 2: {'winningMoves': [], 'count': 0, 'score': 0, 'numScore': 0}}
        for i in tally:
            aggre[i[0]]['winningMoves'].append([i[1], i[2]])
            aggre[i[0]]['count'] += 1
            aggre[i[0]]['score'] += i[3][i[0]]
            aggre[i[0]]['numScore'] += 1
        self.logger.info('\nwinner\t winning seq.\twinning move\tplayer:score')
        for i in tally:
            self.logger.debug('')
            for j in i:
                self.logger.debug(str(j) + '\t')
        p1 = aggre[1]['count']
        p2 = aggre[2]['count']
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
        print(f"\nwins#:\t\t{aggre[1]['count']}\t\t\t{aggre[2]['count']}")
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


if __name__ == '__main__':
    start = time.time()

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
                # print(str(i) + " is a possible move")
                open_spaces.append(i)
            if board[i]['color'] in [1, 2]:
                j = i
                # print(str(j) + " is occupied by "+ str(colors[board[i]['color']]))
                while board[j]['color'] in [1, 2] and j - game.length > 0:
                    j = j - game.length
                    try:
                        if board[j]['color'] == -1:
                            open_spaces.append(j)
                    except:
                        game.logger.error("vreak")
        return open_spaces

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
                    selectFrom = possible_moves(game.board)
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
                        game.game_over(0, game.currentPlayer)
                        if game.debug:
                            print(game.printLineBreak())
        print(game.isWinner)
        tally.append([game.isWinner[1], game.isWinner[2],
                      game.isWinner[3], game.playerScore])

        # game.whose_turn()
    results = game.process_tally(tally)
    print("--- %s seconds ---" % (time.time() - start))
    game.logger.info("--- completed in %s seconds ---" % (time.time() - start))
cov.stop()
cov.save()
cov.html_report()
