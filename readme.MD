Goal.

Create a connect 4 system that can be played by a user against and automated opponent or that can be played by two automated players. AI/machine learning implementation is the ultimate goal. 


- [x]		User is able to set the dimensions of the board at start
- [ ]		User can select human or pc players		
- [ ] 		User can choose moves 										
- [x]		Game can detect horizontal connect4s 
- [x]		Game can detect vertical connect4s 
- [x]		Game handles scenarios where sequential pieces are not wins (spillover)
- [ ]		User can select number of pieces to connect to win
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
- [ ]		Enable Reinforcement Learning
- [x]		Define conditions and rewards
- [x]		Define what constitutes a single Step (both player completes a turn)
- [x]		Game assigns points to each player for each game in a series
- [x]		Game has at least 2 levels of output messages one and user can select
- [x]		One level of output contains highly granular debug information
- [x]		Game messages should have some formatting for presentation
- [ ]		User can modify Game parameters at execution via command line arguments
- [ ] 		process_tally and confirm_runtime methods should be a part of gameObjects class
- [ ]		Write unit tests
- [ ]		Allow selection of log file 
- [ ]		Allow visualization of boards smaller than 16x16 on 16x16 matrix (currently only 16x16 boards are visualized this way)
- [ ] 		Enable code coverage analysis 
