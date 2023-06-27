import pytest
from connectGame import gameObject


@pytest.fixture
def game():
    game = gameObject(height=5, length=8)
    return game


@pytest.fixture
def started_game():
    game = gameObject(height=8, length=8)
    started_game = game.start_game()
    return started_game


def test_func_fast():
    p = "penis"
    pass


@pytest.mark.smoke
def test_game_defaults(started_game):

    assert started_game.inProgress == True
    assert started_game.winner == False
    assert started_game.playerCumulative == {1: 0, 2: 0}
    assert started_game.colors == {-1: '⚫', 1: '🔴', 2: '🔵', '🔴': '🟡', '🔵': '🟢'}


@pytest.mark.smoke
def test_more_default_params(game):
    assert game.drawBoardTurn == False
    assert game.drawBoardGameOver == True
    assert game.commsArduino == False


@pytest.mark.smoke
def test_game_height_set(game):
    assert game.height == 5


@pytest.mark.smoke
def test_game_length_set(game):
    assert game.length == 8


@pytest.mark.smoke
def test_game_area(started_game):
    assert len(started_game.board.keys()) == 64


@ pytest.mark.smoke
def test_start_game_defaults(started_game):
    print(started_game)
    assert started_game.inProgress == True
    assert started_game.winner == False
    assert started_game.currentPlayer in [1, 2]
    assert started_game.lastTurn == 0
    assert started_game.currentTurn == 1
    assert started_game.lastMove == None
    assert started_game.currentMove == None
