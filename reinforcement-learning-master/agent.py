"""
Author: Panda Zhou, Yanjun Yang, Zhaoyang Zhang, Xifan Wang
Date: 8102/09/15
"""
#TODO: move this into a class and run it's methods from a main script

from dqn.neural_net import NeuralNet
from dqn.replay_memory import ReplayMemory
from dqn.epsilon_greedy import EpsilonGreedy
import numpy as np
import util.parser as parser
import util.stats_saver as stats_saver
import time
from hlt import constants
from hlt import positionals


class HaliteModel:
    MAX_FILES = 100
    DIRECTION_ORDER = [positionals.Direction.West,
                       positionals.Direction.North,
                       positionals.Direction.East,
                       positionals.Direction.South]
    MOVE_TO_DIRECTION = {
        "o": positionals.Direction.Still,
        "w": positionals.Direction.West,
        "n": positionals.Direction.North,
        "e": positionals.Direction.East,
        "s": positionals.Direction.South}
    OUTPUT_TO_MOVE = {
        0: "o",
        1: "w",
        2: "n",
        3: "e",
        4: "s"}
    MOVE_TO_OUTPUT = {v: k for k, v in OUTPUT_TO_MOVE.items()}

    def train_on_files(self, replay_folder, player_name):
#get data from replay and feed it to train();
        REPLAY_CAPACITY = 100000
        INITIAL_EPSILON = 1.0
        TARGET_EPSILON  = 0.1
        EXPLORATION_FRAMES = 1e6
        BATCH_SIZE = 32
        GAMMA = 0.97
        LR = 0.0005
        GAME_BATCH = 10
        FEAT_COUNT = 130
        N_ACTIONS = 10

        training, game, verbose, fps, W, H = parser.get_arguments()
        training = parser.str2bool(training)
        start_time = time.time()

        max_score = 0
        games_played = 0
        frame_iterations = 0
        scores = {}

        # to replace and a loooot to do in neural_net
        nn = NeuralNet(FEAT_COUNT, N_ACTIONS,
                       gamma=GAMMA,
                       learning_rate=LR,
                       verbose=verbose)
        print("Training: ", training)
        try:
            while True:

                    # Todo: read the replay
                    # env = HaliteGame(player_id, replay_id)
                game_data = parser.parse_replay_folder(replay_folder, player_name, GAME_BATCH)#all game data in the folder
                print("Processing Game States")
                game_states = []
                for g in game_data:#loop through each game
                    turn_number = 0
                    for game_map, moves, ships, other_ships, dropoffs, other_dropoffs in g:
                        turn_number += 1
                        for ship in list(ships.values()):
                            game_states.append((game_map, moves, ships, other_ships, dropoffs,
                                                    other_dropoffs, turn_number, ship))

                print("Generating Training Data")
                data, labels = [], []
                for game_map, moves, ships, other_ships, dropoffs, other_dropoffs, turn_number, ship in tqdm(game_states):

                    move = "o" if ship.id not in moves else moves[ship.id]
                    '''
                    # Throw away movements that take us closer to base. We will let logic take care of returning to base
                    if move is not "o" and (
                            game_map.calculate_distance(ship.position.directional_offset(self.MOVE_TO_DIRECTION[move]),
                                                        dropoffs[0].position) <
                            game_map.calculate_distance(ship.position, dropoffs[0].position)
                    ):
                        continue'''

                    move_id = self.MOVE_TO_OUTPUT[move]
                    for rot in range(4):  # do all 4 rotations for each game state
                        data.append(self.input_for_ship(game_map,
                                                        ship,
                                                        [s2.position for s2 in ships.values() if s2.id != ship.id],
                                                        [s2.position for s2 in other_ships.values()],
                                                        [d.position for d in dropoffs],
                                                        [d.position for d in other_dropoffs],
                                                        turn_number,
                                                        rotation=rot))#append input data
                        labels.append(np.array(move_id))#append action of ship
                        move_id = 0 if move_id == 0 else (move_id % 4) + 1
                data = np.array(data)
                labels = np.array(labels)
                self.train(data, labels,nn)
                    # Todo: while game on, extract (s, a, r, s1, t) from the jason file
                    # replay_memory.add((s, a, r, s1, t))
                    # frame_iterations += 1;
    def train(self, data, moves,nn):
        try:
            batch=[];
            terminal=data[-1];#terminal state
            for i in range(len(moves)-1):
                r=self.CalculateReward(data[i],moves[i]);
                NextStates=data[i+1];
                batch.append([data[i],moves[i],r,NextStates,terminal])
            loss = nn.optimize(batch)



        except KeyboardInterrupt:
            nn.save()
            print("\nCheckpoint saved")
            nn.close_session()
            stats_saver.save_to_file(env.GAME_TITLE, max_score, games_played, frame_iterations, scores, training, start_time)
            print("Session closed")
    def CalculateReward(self,gamedata,move):
        #todo: the reward function

    def input_for_ship(self, game_map, ship, my_other_ships, other_ships, my_dropoffs, other_dropoffs, turn_number,
                           rotation=0):
        #output: input training data
            N=10;
            nearbyhalite = np.zeros((2*N+1,2*N+1));
            nearbymyship= np.zeros((2*N+1,2*N+1));
            nearbyenemyship= np.zeros((2*N+1,2*N+1));
            for i in range(ship.position.x-N,ship.position.x+N):
                for j in range(ship.position.y-N,ship.position.y+N):
                    nearbyhalite[i-(ship.position.x-N)][j-(ship.position.x-N)]=game_map[game_map.normalize(positionals.Position(i,j))].halite_amount;
            myshippos=set();
            for myship in my_other_ships:
                myshippos.add(my_other_ships);
            for i in range(ship.position.x-N,ship.position.x+N):
                for j in range(ship.position.y-N,ship.position.y+N):
                    if game_map.normalize(positionals.Position(i,j)) in myshippos:
                        nearbymyship[i-(ship.position.x-N)][j-(ship.position.x-N)]=1;

            enemyship=set();
            for othership in other_ships:
                enemyship.add(othership.position);
            for i in range(ship.position.x-N,ship.position.x+N):
                for j in range(ship.position.y-N,ship.position.y+N):
                    if game_map.normalize(positionals.Position(i,j)) in enemyship:
                        nearbyenemyship[i-(ship.position.x-N)][j-(ship.position.x-N)]=1;
            wid = game_map.width
            if wid == 56: maxturn = 476
            if wid == 40: maxturn = 426
            if wid == 32: maxturn= 401
            if wid == 64: maxturn= 501
            if wid == 48: maxturn = 451
            #get relative coordinate of nearest dropoff site
            for dropoff in my_dropoffs():
                dis2 = game_map.calculate_distance(ship.position, dropoff.position);
                if dis > dis2:
                    dis = dis2
                    tarx = dropoff.position.x-ship.position.x
                    tary = dropoff.position.y-ship.position.y
            #periodic boundary condition
            if tarx>wid/2:tarx=tarx-wid;
            if tarx<-wid/2:tarx=tarx+wid;
            if tary>wid/2:tary=tary-wid;
            if tary<-wid/2:tary=tary+wid;
            return [nearbyhalite,nearbyenemyship,nearbymyship,turn_number,maxturn,ship.halite_amount,tarx,tary]
