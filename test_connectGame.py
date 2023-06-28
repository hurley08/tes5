import pytest
from connectGame import gameObject


@pytest.fixture
def game(height=5, length=8):
    game = gameObject(height=height, length=length)
    return game


@pytest.fixture
def started_game(height=16, length=16):
    game = gameObject(height=height, length=length)
    started_game = game.start_game()
    return started_game


def test_func_fast():
    p = "penis"
    pass


@pytest.mark.smoke
def test_game_height_set(game, started_game):
    assert game.height == 5
    assert started_game.height == 16


@ pytest.mark.smoke
def test_game_length_set(game, started_game):
    assert game.length == 8
    assert started_game.length == 16


@ pytest.mark.smoke
def test_game_area(game, started_game):
    assert len(list(started_game.board.keys())) == 256
    game.create_board()
    assert len(list(game.board.keys())) == 40
    board = started_game.create_board(height=8, length=8)

    assert len(list(board.keys())) == 64


@ pytest.mark.smoke
def test_started_defaults(started_game):
    print(started_game)
    assert started_game.inProgress == True
    assert started_game.winner == False
    assert started_game.currentPlayer in [1, 2]
    assert started_game.lastTurn == 0
    assert started_game.currentTurn == 1
    assert started_game.lastMove == None
    assert started_game.currentMove == None


@pytest.mark.smoke
def test_game_defaults(started_game):

    assert started_game.inProgress == True
    assert started_game.winner == False
    assert started_game.playerCumulative == {1: 0, 2: 0}
    assert started_game.colors == {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}


@pytest.mark.smoke
def test_more_default_params(game):
    assert game.drawBoardTurn in (None, True)
    assert game.drawBoardGameOver == True
    assert game.commsArduino == False


@pytest.mark.regression
def test_switch_player(started_game):
    lastPlayer = started_game.currentPlayer
    assert lastPlayer in [1, 2]
    print(lastPlayer)
    started_game.switch_player()
    assert lastPlayer != started_game.currentPlayer
    assert lastPlayer in [1, 2]


@pytest.mark.regression
def test_win_dim(started_game):
    assert (started_game.horizontal, started_game.vertical, started_game.diag1, started_game.diag2) == ([-4, -3, -2, -1, 0, 1, 2, 3, 4],
                                                                                                        [-48, -32, -16,
                                                                                                         0, 16, 32, 48],
                                                                                                        [-45, -30, -15,
                                                                                                         0, 15, 30, 45], [-51, -34, -17, 0, 17, 34, 51])
    started_game.length = 8
    started_game.sdaasdasdasd()
    assert started_game.horizontal == [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    assert started_game.vertical == [-24, -16, -8, 0, 8, 16, 24]
    assert started_game.diag1 == [-21, -14, -7, 0, 7, 14, 21]
    assert started_game.diag2 == [-27, -18, -9, 0, 9, 18, 27]


defsdasdasd
