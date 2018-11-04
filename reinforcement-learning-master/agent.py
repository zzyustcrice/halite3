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

def main():

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

    print("Training: ", training)

    # to replace and a loooot to do in neural_net
    nn = NeuralNet(FEAT_COUNT, N_ACTIONS,
                   gamma=GAMMA,
                   learning_rate=LR,
                   verbose=verbose)

    replay_memory = ReplayMemory(capacity=REPLAY_CAPACITY)
    epsilon_greedy = EpsilonGreedy(initial_value=INITIAL_EPSILON,
                                   target_value=TARGET_EPSILON,
                                   exploration_frames=EXPLORATION_FRAMES)
    try:
        while True:
            # play 10 games and obtain the replay data
            for i in range(GAME_BATCH):
                # Todo: start a MyBot using NN to generate the replay.
                # MyBot_combat(nn, file_name)
                # Todo: save the replay in certain file.
                pass


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
                # Throw away movements that take us closer to base. We will let logic take care of returning to base
                if move is not "o" and (
                        game_map.calculate_distance(ship.position.directional_offset(self.MOVE_TO_DIRECTION[move]),
                                                    dropoffs[0].position) <
                        game_map.calculate_distance(ship.position, dropoffs[0].position)
                ):
                    continue


                for rot in range(4):  # do all 4 rotations for each game state
                    data.append(input_for_ship(game_map,
                                                    ship,
                                                    [s2.position for s2 in ships.values() if s2.id != ship.id],
                                                    [s2.position for s2 in other_ships.values()],
                                                    [d.position for d in dropoffs],
                                                    [d.position for d in other_dropoffs],
                                                    turn_number,
                                                    rotation=rot))
                    labels.append(np.array(move_id))
                    move_id = 0 if move_id == 0 else (move_id % 4) + 1
            data = np.array(data)
            labels = np.array(labels)
                # Todo: while game on, extract (s, a, r, s1, t) from the jason file
                # replay_memory.add((s, a, r, s1, t))
                # frame_iterations += 1
            if not t:
                   s = s1
            else:
                    max_score = max(max_score, score)
                    games_played += 1
                    scores[score] = scores.get(score, 0) + 1
                    print("\rMax Score: {:3} || Last Score: {:3} || Games Played: {:7} Iterations: {:10} Scores: {}" \
                        .format(max_score, score, games_played, frame_iterations, str(scores)),
                        end="\n" if verbose or games_played % 1000 == 0 else "")
                    s = env.reset()

            # Train the network with current batch data
            if training and frame_iterations > REPLAY_CAPACITY // 2:
                batch = replay_memory.get_minibatch(batch_size=BATCH_SIZE)
                loss = nn.optimize(batch)

    except KeyboardInterrupt:
        if training:
            nn.save()
            print("\nCheckpoint saved")
        nn.close_session()
        stats_saver.save_to_file(env.GAME_TITLE, max_score, games_played, frame_iterations, scores, training, start_time)
        print("Session closed")

if __name__ == "__main__":
    main()
    # Generate the feature vector
def input_for_ship(self, game_map, ship, my_other_ships, other_ships, my_dropoffs, other_dropoffs, turn_number,
                       rotation=0):
        result = [];
        N=10;
        for i in range(ship.position.x-N,ship.position.x+N):
            for j in range(ship.position.y-N,ship.position.y+N):
                result.append(game_map[game_map.normalize(positionals.Position(i,j))].halite_amount);
        myshippos=set();
        for myship in my_other_ships:
            myshippos.add(myship.position);
        for i in range(ship.position.x-N,ship.position.x+N):
            for j in range(ship.position.y-N,ship.position.y+N):
                if game_map.normalize(positionals.Position(i,j)) in myshippos:
                    result.append(1);
                else: result.append(0);
        enemyship=set();
        for othership in other_ships:
            enemyship.add(othership.position);
        for i in range(ship.position.x-N,ship.position.x+N):
            for j in range(ship.position.y-N,ship.position.y+N):
                if game_map.normalize(positionals.Position(i,j)) in enemyship:
                    result.append(1);
                else: result.append(0);
