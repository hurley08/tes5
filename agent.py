class DQNAgent:
    def __init__(self, name, env, conv_list, dense_list, util_list):
        self.env = env
        self.conv_list = conv_list
        self.dense_list = dense_list
        self.name = [str(name) + " | " + "".join(str(c) + "C | " for c in conv_list) + "".join(
            str(d) + "D | " for d in dense_list) + "".join(u + " | " for u in util_list)][0]

        # Main model
        self.model = self.create_model(self.conv_list, self.dense_list)

        # Target network
        self.target_model = self.create_model(self.conv_list, self.dense_list)
        self.target_model.set_weights(self.model.get_weights())

        # An array with last n steps for training
        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        # Custom tensorboard object
        self.tensorboard = ModifiedTensorBoard(
            name, log_dir="{}logs/{}-{}".format(PATH, name, int(time.time())))

        # Used to count when to update target network with main network's weights
        self.target_update_counter = 0

    # Creates a convolutional block given (filters) number of filters, (dropout) dropout rate,
    # (bn) a boolean variable indecating the use of BatchNormalization,
    # (pool) a boolean variable indecating the use of MaxPooling2D

    def conv_block(self, inp, filters=64, bn=True, pool=True, dropout=0.2):
        _ = Conv2D(filters=filters, kernel_size=3, activation='relu')(inp)
        if bn:
            _ = BatchNormalization()(_)
        if pool:
            _ = MaxPooling2D(pool_size=(2, 2))(_)
        if dropout > 0:
            _ = Dropout(0.2)(_)
        return _
    # Creates the model with the given specifications:

    def create_model(self, conv_list, dense_list):
        # Defines the input layer with shape = ENVIRONMENT_SHAPE
        input_layer = Input(shape=self.env.ENVIRONMENT_SHAPE)
        # Defines the first convolutional block:
        _ = self.conv_block(
            input_layer, filters=conv_list[0], bn=False, pool=False)
        # If number of convolutional layers is 2 or more, use a loop to create them.
        if len(conv_list) > 1:
            for c in conv_list[1:]:
                _ = self.conv_block(_, filters=c)
        # Flatten the output of the last convolutional layer.
        _ = Flatten()(_)

        # Creating the dense layers:
        for d in dense_list:
            _ = Dense(units=d, activation='relu')(_)
        # The output layer has 5 nodes (one node per action)
        output = Dense(units=self.env.ACTION_SPACE_SIZE,
                       activation='linear', name='output')(_)

        # Put it all together:
        model = Model(inputs=input_layer, outputs=[output])
        model.compile(optimizer=Adam(lr=0.001),
                      loss={'output': 'mse'},
                      metrics={'output': 'accuracy'})

        return model

    # Adds step's data to a memory replay array
    # (observation space, action, reward, new observation space, done)
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    # Trains main network every step during episode
    def train(self, terminal_state, step):
        # Start training only if certain number of samples is already saved
        if len(self.replay_memory) < MIN_REPLAY_MEMORY_SIZE:
            return

        # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)

        # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(
            current_states.reshape(-1, *env.ENVIRONMENT_SHAPE))

        # Get future states from minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried
        new_current_states = np.array(
            [transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(
            new_current_states.reshape(-1, *env.ENVIRONMENT_SHAPE))

        X = []
        y = []

        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of equation here
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q
            else:
                new_q = reward

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)

        # Fit on all samples as one batch, log only on terminal state
        self.model.fit(x=np.array(X).reshape(-1, *env.ENVIRONMENT_SHAPE),
                       y=np.array(y),
                       batch_size=MINIBATCH_SIZE, verbose=0,
                       shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter += 1

        # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter > UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    # Queries main network for Q values given current observation space (environment state)
    def get_qs(self, state):
        return self.model.predict(state.reshape(-1, *env.ENVIRONMENT_SHAPE))
