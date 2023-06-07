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
