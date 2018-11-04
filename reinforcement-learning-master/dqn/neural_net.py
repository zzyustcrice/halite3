"""
Author: Panda Zhou, Yanjun Yang, Zhaoyang Zhang, Xifan Wang
Date: 8102/09/15
"""
import tensorflow as tf
import numpy as np
import os

class NeuralNet:

    """
    Deep-Q-Network used to approximate the function Q(s, a), similar to the one
    in the original DeepMind paper with experience replay and e-greedy policy.

    Args:
        W: The width of the image passed in as the input layer
        H: The height of the image passed in as the input layer
        N_ACTIONS: number of possible actions. A q-value is predicted for each
                   action in each state
        learning_rate: The optimizer's learning rate
        game_title: name of the game being played
    """
    def __init__(self, feat_count, N_ACTIONS, gamma=0.97, learning_rate=0.0025, verbose=False):
        tf.reset_default_graph()
        self.FEAT_COUNT = feat_count
        self.input_layer = tf.placeholder(dtype=tf.float32, shape=(None, self.FEAT_COUNT), name="input_layer")
        self.lr = learning_rate
        self.checkpoint_dir = os.path.join("saved_checkpoints/", "{}/{}/".format(feat_count, N_ACTIONS))
        self.N_ACTIONS = N_ACTIONS
        self.GAMMA = gamma

        self.verbose = verbose

        weight_init = tf.truncated_normal_initializer(mean=0.0, stddev=0.003)
        activation = tf.nn.relu
        dense = tf.layers.dense
        dropout = tf.nn.dropout

        # 1st fully connected layer
        NN = dense(name='fc1', inputs=self.input_layer, units=500,
                    kernel_initializer=weight_init,
                    activation=activation)

        NN = dropout(NN, 0.9)

        # 2nd fully connected layer
        NN = dense(name='fc2', inputs=NN, units=300,
                    kernel_initializer=weight_init,
                    activation=activation)

        NN = dropout(NN, 0.9)

        # 3rd fully connected layer
        NN = dense(name='fc3', inputs=NN, units=100,
                    kernel_initializer=weight_init,
                    activation=activation)

        NN = dropout(NN, 0.9)

        # Output layer
        NN = dense(name='fc_out', inputs=NN, units=self.N_ACTIONS,
                    kernel_initializer=weight_init,
                    activation=tf.nn.tahn)

        self.q_values = NN
        self.prediction = tf.argmax(self.q_values, 1)

        self.q_target = tf.placeholder(shape=[None], dtype=tf.float32)
        self.actions = tf.placeholder(shape=[None], dtype=tf.int32)
        self.actions_onehot = tf.one_hot(self.actions, self.N_ACTIONS, dtype=tf.float32)

        self.q_predicted = tf.reduce_sum(tf.multiply(self.q_values, self.actions_onehot), axis=1)

        self.td_error = tf.square(self.q_target - self.q_predicted)
        self.loss = tf.reduce_mean(self.td_error)
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.lr).minimize(self.loss)

        self.sess = tf.Session()
        self.saver = tf.train.Saver()

        self.load()

    """
    Q(state, network_params) -> (q_a1, q_a2, ..., q_an)
    Args:
        states: A batch of game states that are inputs to the neural net
    Returns:
        predicted q-value vector for each state. Each vector contains the
        predicted q-values for each action
    """
    def Q(self, states):
        return self.sess.run(self.q_values, feed_dict={self.input_layer:states})

    """
    Value function. Predicts the value of being in a given state.
    Args:
        states: The states one wants to know the value of.
    Returns:
        The maximum of （q-value predicted for each state.）
    """
    def V(self, states):
        q_values = self.Q(states)
        v_values = [max(q_values[i]) for i in range(len(q_values))]
        return v_values

    """
    Predicts the actions that should be taken at each state
    Args:
        states: The game states fed into the network
    Returns:
        An action for each state. Each action is an int in
            the range (0, N_ACTIONS)
    """
    def predict(self, states):
        q_values = self.Q(states)
        if self.verbose: print("Q-Values: ", q_values)
        actions = [np.argmax(q_values[i]) for i in range(len(states))]
        return actions

    """
    Loads the previous session or starts a new one with random weights
    """
    def load(self):
        if os.path.isdir(self.checkpoint_dir):
            self.saver.restore(self.sess, save_path=self.checkpoint_dir)
            print("Checkpoint successfully loaded from {}.".format(self.checkpoint_dir))
        else:
            self.sess.run(tf.global_variables_initializer())
            print("No checkpoint found in {}.".format(self.checkpoint_dir))
    """
    Saves the current session checkpoint
    """
    def save(self):
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)
        self.saver.save(self.sess, save_path=self.checkpoint_dir)

    """
    Closes the TensorFlow session being used
    """
    def close_session(self):
        self.sess.close()

    """
    Optimize on the equation:
    Q_target=reward + GAMMA * max_a'(Q(s', a')) 
    Q_predict=Q(s,a)
    loss=[reward + GAMMA * max_a'(Q(s', a')) - Q(s, a)]^2
    Args:
        batch: The minibatch of (s, a, r, s1, t) being fed for optimizing.
    Returns:
        The loss calculated for the given minibatch.
    """
    def optimize(self, batch):
        batch_size = len(batch)
        states      = [batch[i][0] for i in range(batch_size)]
        actions     = [batch[i][1] for i in range(batch_size)]
        rewards     = [batch[i][2] for i in range(batch_size)]
        next_states = [batch[i][3] for i in range(batch_size)]
        terminal    = [batch[i][4] for i in range(batch_size)]

        V = self.V(next_states)

        q_target = [rewards[i] + (0 if terminal[i] else self.GAMMA*V[i]) \
                    for i in range(batch_size)]

        feed_dict = {self.input_layer: states, self.q_target: q_target, self.actions: actions}

        _, loss = self.sess.run([self.optimizer, self.loss], feed_dict=feed_dict)
        return loss
