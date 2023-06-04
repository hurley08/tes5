import unittest
import connectGame as go

game = go.gameObject()


class test_init(unittest.TestCase):
	game = go.gameObject()

	def test_default_length(self):
		self.assertEqual(5, game.length)

	def test_default_height(self):
		self.assertEqual(8, game.height)

	def test_default_matrix_dim(self):
		self.assertEqual(40, len(game.board.keys()))

	def test_custom_dimensions(self, sets=[(5, 8), (8, 8), (16, 16)]):
        # test that attributes are correctly assigned and that the board produced contains
        # exactly length*width spaces. The length of board dictionary should be correct
		for i in sets:
        	game = go.gameObject(length=i[0], height=i[1])
       		game.start_game(
        	self.assertEqual(go.length, i[0])
        	self.assertEqual(go.height, i[1])
			self.assertEqual(i[0] * i[1], len(go.board.keys()))


if __name__ == "__main__":
    unittest.main()
