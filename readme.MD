Goal.

Create a connect 4 system that can be played by a user against and automated opponent or that can be played by two automated players. AI/machine learning implementation is the ultimate goal. 

Attributes:
-init
self.colors 				yes			defines how pieces on the board will be displayed by draw_board
self.dummy 					no			forgot the intent of this one -_-													 
self.waitTime 				no			intended to allow user to set time to wait between turns, rounds, or whatever
self.height 				yes			# of pieces can be stacked on the board default is 5
self.length					yes			# of pieces can be laid per level on the board 
self.board 					yes			tracks which spaces are/n't occupied and by whom
self.isBot 					no			intended to toggle bot v bot or bot v player	
self.debug 					yes			was used to toggle debug prints but logger was implemented. so should be deprecated
self.inProgress 			yes			this is true while a game is in progress until winning move 
self.winner 				yes			this is false until a winning move is made 
self.playerCumulative 		yes			this tracks the scores earned by players through a series of games 
self.drawBoardTurn			yes			if true draw_board will be called at the end of each players turn 
self.drawBoardGameOver 		yes			if true draw_board will be called when a winning move is made
self.serialConnected 		yes			if true we have a live connection with an Arduino
self.commsArduino			yes			if true then we will init serial and attempt to conect to arduino 

-start_game
self.turnLog				yes			intended to store the history of moves 
self.currentPlayer 			yes			stores the player of the current turn
self.horizontal 			yes			stores the spaces that must be checked to determine horizontal connect4
self.vertical 				yes			stores the spaces that must be checked to determine vertical connect4			
self.diag1 					yes			stores the spaces that must be checked to determine horizontal connect4
self.diag2 				    yes			stores the spaces that must be checked to determine horizontal connect4
self.turnKey 				no			intended to be used to lock variables between certain events but abandoned
self.lastTurn 				yes			current turn number - 1 
self.currentTurn 			yes			current turn number
self.nextTurn 				yes			current turn number + 1
self.lastMove 				yes			space chosen by the previous turn
self.currentMove 			yes			used to store desired move by current player until next turn
self.playerScore 			yes			stores each player's score for the current game 





To Do:
- [ ]		User can select human or pc players		
- [ ] 		User can choose moves 						
- [ ]		User can select number of pieces to connect to win
- [ ]		Enable Reinforcement Learning
- [ ]		User can modify Game parameters at e
- [ ] 		process_tally and confirm_runtime methods should be a part of gameObjects class
- [ ]		Allow execution of options via command line arguments
- [ ]		Allow selection of log file 
- [ ]		Allow visualization of boards smaller than 16
- [ ]		Refactor the huge game class into smaller more modular classes
- [ ]		Refactor and use data structures that are not unique to a single method 
- [ ]		Improve code coverage. Highest was ~75% current coverage is ~67% 
- [ ]		This project should be using dataframes 

Completed:
- [x]		User is able to set the dimensions of the board at start
- [x]		Game can detect horizontal connect4s 
- [x]		Game can detect vertical connect4s 
- [x]		Game handles scenarios where sequential pieces are not wins (spillover)
- [x]		Game draws a graphical representation of game 
- [x]		Game can conect to Arduino serially 
- [x]		Arduino can accept moves from Game and display on matrix 
- [x]		Game tracks the progression of the game 
- [x]		Game knows what spaces are occupied 
- [x]		Game knows which moves are legal 
- [x]		Game outputs information as each turn is made 
- [x]		User can select if board is drawn at endTurn
- [x]		User can input how many games to play in series
- [x]		Game verifies user input before proceeding on a series 
- [x]		Game can track the outcome of every game in a series 
- [x]		Game displays winner and relevant information 
- [x]		Game ends the current game following a win detect 
- [x] 		Game can clear memory and begin a new game (if a series is set by User)
- [x]		Define conditions and rewards
- [x]		Define what constitutes a single Step (both player completes a turn)
- [x]		Game assigns points to each player for each game in a series
- [x]		Game has at least 2 levels of output messages one and user can select
- [x]		One level of output contains highly granular debug information
- [x]		Game messages should have some formatting for presentation
- [x]		Write unit tests
x16 on 16x16 matrix (currently only 16x16 boards are visualized this way)
- [x] 		Enable code coverage analysis 