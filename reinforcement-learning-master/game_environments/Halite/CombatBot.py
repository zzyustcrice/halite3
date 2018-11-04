import hlt
import logging
from collections import OrderedDict
import numpy as np
import math
import random
import os
from heapq import heapify

MAX_LEN = 384.
MAX_WID = 256.
MIN_LEN = 240.
MIN_WID = 160.
MAX_DIAG = math.sqrt(MAX_LEN**2 + MAX_WID**2)
SHIP_RADIUS = 0.5
SHIP_MAX_HP = 255.
SHIP_MAX_SPEED = 7.
WEAPEN_RANGE = 5.
WEAPEN_DAMAGE = 64.

import tensorflow as tf
from keras.models import load_model
class CombatRob:

    def __init__(self, DQN_net_model, file_name):
        self.DQN_net_model = DQN_net_model
        self.file_name = file_name
        self.game = hlt.Game("Pandas_AI")


    def combat_act(self):
        while True:
            game_map = self.game.update_map()
            all_players = game_map.all_players()
            my_id = game_map.get_me().id
            enemy_id = [id for id in all_players if id != my_id]

            command_queue = []
            # ship features
            team_ships = game_map.get_me().all_ships()
            enemy_ships = [ship for ship in game_map.get_player(id).all_ships() for id in enemy_id]
            team_ships_position = [[game_map.get_player(my_id).get_ship(id).x, game_map.get_player(my_id).get_ship(id).y]
                                   for id in team_ships]
            team_ships_vel = [game_map.get_player(my_id).get_ship(id).thrust() for id in team_ships]
            team_ships_status = [game_map.get_player(my_id).get_ship(id).docking_status for id in team_ships]
            team_ships_hp = [game_map.get_player(my_id).get_ship(id).health for id in team_ships]


            enemy_ships_position = [[game_map.get_player(p_id).get_ship(s_id).x, game_map.get_player(p_id).get_ship(s_id)]
                                     for s_id in game_map.get_player(p_id).all_ships() for p_id in enemy_id]
            enemy_ships_vel = [game_map.get_player(p_id).get_ship(s_id).thrust()
                               for s_id in game_map.get_player(p_id).all_ships() for p_id in enemy_id]
            enemy_ships_status = [game_map.get_player(p_id).get_ship(s_id).docking_status
                                  for s_id in game_map.get_player(p_id) for p_id in enemy_id]
            enemy_ships_hp = [game_map.get_player(p_id).get_ship(s_id)
                              for s_id in game_map.get_player(p_id) for p_id in enemy_id]


            my_ship_count = len(team_ships)
            enemy_ship_count = len(enemy_ships)

            all_planets = game_map.all_planets()

            empty_planets = [p for p in all_planets if not p.is_owned()]
            team_planets = [p for p in all_planets if p.owner.id == my_id]
            enemy_planets = [p for p in all_planets if p.is_owned() and p.owner.id != my_id]

            empty_plants_position = [[game_map.get_planet(id).x, game_map.get_planet(id).y] for id in empty_planets]
            team_planets_position = [[game_map.get_planet(id).x, game_map.get_planet(id).y] for id in team_planets]
            enemy_planets_position = [[game_map.get_planet(id).x, game_map.get_planet(id).y] for id in empty_planets]

            empty_planets_size = [game_map.get_planet(id).radius for id in empty_planets]
            team_planets_size = [game_map.get_planet(id).radius for id in team_planets]
            enemy_planets_size = [game_map.get_planet(id).radius for id in enemy_planets]

            empty_planets_hp = [game_map.get_planet(id).health for id in empty_planets]
            team_planets_hp = [game_map.get_planet(id).health for id in team_planets]
            enemy_planets_hp = [game_map.get_planet(id).health for id in enemy_planets]


            team_planets_docked = [len(game_map.get_planet(id).all_docked_ships()) for id in team_planets]
            team_planets_open = [game_map.get_planet(id).num_docking_spots] - team_planets_docked

            enemy_planets_docked = [len(game_map.get_planet(id).all_docked_ships()) for id in enemy_planets]
            enemy_planets_open = [game_map.get_planet(id).num_docking_spots] - enemy_planets_docked

            team_planets_count = len(team_planets_size)
            empty_planets_count = len(empty_planets_size)
            enemy_planets_count = len(enemy_planets_size)

            for i, ship in enumerate(team_ships):
                feat = []
                feat += [my_ship_count, enemy_ship_count, team_planets_count, empty_planets_count, enemy_planets_count]
                feat.append(team_ships_position[i])
                feat += self.VelStr2List(team_ships_vel[i])
                feat += self.status2List(team_ships_status[i])
                feat.append(team_ships_hp[i])
                Posi = team_ships_position[i]
                empty_planets_info = []
                for j, planet in enumerate(empty_planets):
                    dis = self.getDistance(Posi, empty_plants_position[j])
                    empty_plants_info.append((dis, empty_plants_position[j][0], empty_plants_position[j][1],
                                             enemy_planet_sizes[j], enemy_planets_hp[j]))
                heapify(empty_planets_info)
                for j in range(3):
                    if empty_planets_info:
                        feat += list(empty_planets_info.pop())
                    else:
                        feat += [9 * MAX_DIAG, 10 * MAX_LEN, 10 * MAX_WID, 0, 1000]


                team_planets_info = []
                for j, planet in enumerate(team_planets):
                    dis = self.getDistance(Posi, team_plants_position[j])
                    team_planets_info.append((dis, team_plants_position[j][0], team_plants_position[j][1],
                                             team_planet_sizes[j], team_planets_hp[j],
                                             team_planets_docked[j], team_planets_open[j]))
                heapify(team_planets_info)
                for j in range(3):
                    if team_planets_info:
                        feat += list(team_planets_info.pop())
                    else:
                        feat += [9 * MAX_DIAG, 10 * MAX_LEN, 10 * MAX_WID, 0, 1000, 0, 0]

                enemy_planets_info = []
                for j, planet in enumerate(enemy_planets):
                    dis = self.getDistance(Posi, enemy_plants_position[j])
                    enemy_planets_info.append((dis, enemy_plants_position[j][0], enemy_plants_position[j][1],
                                             enemy_planet_sizes[j], enemy_planets_hp[j],
                                             enemy_planets_docked[j], enemy_planets_open[j]))
                heapify(enemy_planets_info)
                for j in range(3):
                    if enemy_planets_info:
                        feat += list(enemy_planets_info.pop())
                    else:
                        feat += [9 * MAX_DIAG, 10 * MAX_LEN, 10 * MAX_WID, 0, 1000, 0, 0]

                team_ship_info = []
                for j, ship in enumerate(team_ships):
                    if j != i:
                        dis = self.getDistance(Posi, team_ships_position[j])
                        team_ship_info.append((dis, team_ships_position[j][0], team_ships_position[j][1],
                                               self.VelStr2List(team_ships_vel)[0], self.VelStr2List(team_ships_vel)[1],
                                               team_ships_hp[j], self.status2List(team_ships_status[j])))

                heapify(team_ship_info)
                for j in range(3):
                    if team_ship_info:
                        feat += list(team_ship_info.pop())
                    else:
                        feat += [9 * MAX_DIAG, 10 * MAX_LEN, 10 * MAX_WID, 0, 0, 255, 1, 0, 0, 0]

                enemy_ship_info = []
                for j, ship in enumerate(enemy_ships):
                    dis = self.getDistance(Posi, enemy_ships_position[j])
                    enemy_ship_info.append((dis, enemy_ships_position[j][0], enemy_ships_position[j][1],
                                            self.VelStr2List(enemy_ships_vel)[0], self.VelStr2List(enemy_ships_vel)[1],
                                            enemy_ships_hp[j], self.status2List(enemy_ships_status[j])))

                heapify(enemy_ship_info)
                for j in range(3):
                    if enemy_ship_info:
                        feat += list(enemy_ship_info.pop())
                    else:
                        feat += [9 * MAX_DIAG, 10 * MAX_LEN, 10 * MAX_WID, 0, 0, 255, 1, 0, 0, 0]

                print('feat dimension:', len(feat))
                output_vector = DQN_net_model.predict(np.array(feat))[0]
                output_max = np.argmax(output_vector)




    def VelStr2List(self,vStr):
        vList = vStr.split(' ')
        mag = num(vList[-2])
        ang = num(vList[-1])
        Vel_x = mag * math.cos(math.radians(ang))
        Vel_y = mag * math.sin(math.radians(ang))
        return [Vel_x, Vel_y]

    def status2List(self, status):
        if status == 0 or status == 'undocked':
            return 1, 0, 0, 0
        if status == 1 or status == 'docking':
            return 0, 1, 0, 0
        if status == 2 or status == 'docked':
            return 0, 0, 1, 0
        if status == 3 or status == 'undocking':
            return 0, 0, 0, 1

    def getDistance(self, Position1, Position2):
        return math.sqrt((Position1[0]-Position2[0])**2 + (Position1[1]-Position2[1])**2)









os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99'
tf.logging.set_verbosity(tf.logging.ERROR)
model = load_model('model_checkpoint_128_batch_10_epochs.h5')

VERSION = 1

HM_ENT_FEATURES = 5
game = hlt.Game("Charles-AI-{}".format(VERSION))
logging.info("CharlesBot-{} Start".format(VERSION))

PCT_CHANGE_CHANCE = 5
DESIRED_SHIP_COUNT = 20

ship_plans = {}

def handle_list(l):
    new_list = []
    for i in range(HM_ENT_FEATURES):
            try:
                    new_list.append(l[i])
            except:
                    new_list.append(-99)
    return new_list

def key_by_value(dictionary, value):

    for k,v in dictionary.items():
        if v[0] == value:
            return k
    return -99


def fix_data(data):
    new_list = []
    last_known_idx = 0
    for i in range(HM_ENT_FEATURES):
        try:
            if i < len(data):
                last_known_idx=i
            new_list.append(data[last_known_idx])
        except:
            new_list.append(0)
            
    return new_list

##if os.path.exists("c{}_input.vec".format(VERSION)):
##    os.remove("c{}_input.vec".format(VERSION))
##
##if os.path.exists("c{}_out.vec".format(VERSION)):
##    os.remove("c{}_out.vec".format(VERSION))
    
while True:
    game_map = game.update_map()
    
    command_queue = []
    team_ships = game_map.get_me().all_ships()
    all_ships = game_map._all_ships()
    enemy_ships = [ship for ship in game_map._all_ships() if ship not in team_ships]

    my_ship_count = len(team_ships)
    enemy_ship_count = len(enemy_ships)
    all_ship_count = len(all_ships)

    #logging.info(", ".join([str(len(team_ships)), str(len(enemy_ships)), str(len(all_ships))]))


    my_id = game_map.get_me().id

    empty_planet_sizes = {}
    our_planet_sizes = {}
    enemy_planet_sizes = {}
    
    for p in game_map.all_planets():
        radius = p.radius
        if not p.is_owned():
            empty_planet_sizes[radius] = p
        elif p.owner.id == game_map.get_me().id:
            our_planet_sizes[radius] = p
        elif p.owner.id != game_map.get_me().id:
            enemy_planet_sizes[radius] = p

    hm_our_planets = len(our_planet_sizes)
    hm_empty_planets = len(empty_planet_sizes)
    hm_enemy_planets = len(enemy_planet_sizes)
    
        
    empty_planet_keys = sorted([k for k in empty_planet_sizes])[::-1]

    our_planet_keys = sorted([k for k in our_planet_sizes])[::-1]

    enemy_planet_keys= sorted([k for k in enemy_planet_sizes])[::-1]

    for ship in game_map.get_me().all_ships():
        
        try:
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                # Skip this ship
                continue


            shipid = ship.id
            change = False
            if random.randint(1,100) <= PCT_CHANGE_CHANCE:
                change = True

            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                # Skip this ship
                continue

            logging.info("got here!!!")

            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))


            closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
            closest_empty_planet_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
            
            
            closest_my_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Planet) and entities_by_distance[distance][0].is_owned() and (entities_by_distance[distance][0].owner.id == game_map.get_me().id)]
            closest_my_planets_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Planet) and entities_by_distance[distance][0].is_owned() and (entities_by_distance[distance][0].owner.id == game_map.get_me().id)]


            closest_enemy_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Planet) and entities_by_distance[distance][0] not in closest_my_planets and entities_by_distance[distance][0] not in closest_empty_planets]
            closest_enemy_planets_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Planet) and entities_by_distance[distance][0] not in closest_my_planets and entities_by_distance[distance][0] not in closest_empty_planets]
    
            
            closest_team_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Ship) and entities_by_distance[distance][0] in team_ships]
            closest_team_ships_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Ship) and entities_by_distance[distance][0] in team_ships]
            
            closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]
            closest_enemy_ships_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], game_environments.Halite.hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]

            largest_empty_planet_distances = []
            largest_our_planet_distances = []
            largest_enemy_planet_distances = []

            for i in range(HM_ENT_FEATURES):
                try: largest_empty_planet_distances.append(key_by_value(entities_by_distance, empty_planet_sizes[empty_planet_keys[i]]))
                except:largest_empty_planet_distances.append(-99)

                try: largest_our_planet_distances.append(key_by_value(entities_by_distance, our_planet_sizes[our_planet_keys[i]]))
                except:largest_our_planet_distances.append(-99)

                try: largest_enemy_planet_distances.append(key_by_value(entities_by_distance, enemy_planet_sizes[enemy_planet_keys[i]]))
                except:largest_enemy_planet_distances.append(-99)
                

            entity_lists = [fix_data(closest_empty_planet_distances),
                            fix_data(closest_my_planets_distances),
                            fix_data(closest_enemy_planets_distances),
                            fix_data(closest_team_ships_distances),
                            fix_data(closest_enemy_ships_distances),
                            fix_data(empty_planet_keys),
                            fix_data(our_planet_keys),
                            fix_data(enemy_planet_keys),
                            fix_data(largest_empty_planet_distances),
                            fix_data(largest_our_planet_distances),
                            fix_data(largest_enemy_planet_distances)]


            input_vector = []
            

            for i in entity_lists:
                for ii in i[:HM_ENT_FEATURES]:
                    input_vector.append(ii)

            input_vector += [my_ship_count,
                             enemy_ship_count,
                             hm_our_planets,
                             hm_empty_planets,
                             hm_enemy_planets]


            if my_ship_count > DESIRED_SHIP_COUNT:
                output_vector = 3*[0]
                output_vector[0] = 1
                ship_plans[ship.id] = output_vector

            elif change or ship.id not in ship_plans:
                '''
                pick new "plan"
                '''
                input_vector = [round(item,3) for item in input_vector]
                output_vector = model.predict(np.array([input_vector]))[0]
                output_max = np.argmax(output_vector)
                argmax_vector = [0,0,0]
                argmax_vector[output_max] = 1
                output_vector = argmax_vector
                logging.info(output_max)
                ship_plans[ship.id] = output_vector

            else:
                '''continue to execute existing plan'''
                output_vector = ship_plans[ship.id]

            #output_vector = [0,0,0,1]

            closest_empty_planets = fix_data(closest_empty_planets)
            closest_my_planets = fix_data(closest_my_planets)
            closest_enemy_planets = fix_data(closest_enemy_planets)
            closest_team_ships = fix_data(closest_team_ships)
            closest_enemy_ships = fix_data(closest_enemy_ships)

            try:
                # ATTACK ENEMY SHIP #
                if np.argmax(output_vector) == 0:
                    '''
                    type: 0
                    Find closest enemy ship, and attack!
                    '''
                    if not isinstance(closest_enemy_ships[0], int):
                        navigate_command = ship.navigate(
                                    ship.closest_point_to(closest_enemy_ships[0]),
                                    game_map,
                                    speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                        if navigate_command:
                            command_queue.append(navigate_command)


                # MINE ONE OF OUR PLANETS #
                elif np.argmax(output_vector) == 1:
                    '''
                    type: 1
                    Mine closest already-owned planet
                    '''
                    if not isinstance(closest_my_planets[0], int):
                        target =  closest_my_planets[0]

                        if len(target._docked_ship_ids) < target.num_docking_spots:
                            if ship.can_dock(target):
                                command_queue.append(ship.dock(target))
                            else:
                                navigate_command = ship.navigate(
                                            ship.closest_point_to(target),
                                            game_map,
                                            speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                            ignore_ships=False)

                                if navigate_command:
                                    command_queue.append(navigate_command)
                        else:
                            #attack!
                            if not isinstance(closest_enemy_ships[0], int):
                                navigate_command = ship.navigate(
                                            ship.closest_point_to(closest_enemy_ships[0]),
                                            game_map,
                                            speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                            ignore_ships=False)

                                if navigate_command:
                                    command_queue.append(navigate_command)
                            

                                
                    elif not isinstance(closest_empty_planets[0], int):
                        target =  closest_empty_planets[0]
                        if ship.can_dock(target):
                            command_queue.append(ship.dock(target))
                        else:
                            navigate_command = ship.navigate(
                                        ship.closest_point_to(target),
                                        game_map,
                                        speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                        ignore_ships=False)

                            if navigate_command:
                                command_queue.append(navigate_command)

                    #attack!
                    elif not isinstance(closest_enemy_ships[0], int):
                        navigate_command = ship.navigate(
                                    ship.closest_point_to(closest_enemy_ships[0]),
                                    game_map,
                                    speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                        if navigate_command:
                            command_queue.append(navigate_command)


                # FIND AND MINE AN EMPTY PLANET #
                elif np.argmax(output_vector) == 2:
                    '''
                    type: 2
                    Mine an empty planet. 
                    '''
                    if not isinstance(closest_empty_planets[0], int):
                        target =  closest_empty_planets[0]
                        
                        if ship.can_dock(target):
                            command_queue.append(ship.dock(target))
                        else:
                            navigate_command = ship.navigate(
                                        ship.closest_point_to(target),
                                        game_map,
                                        speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                        ignore_ships=False)

                            if navigate_command:
                                command_queue.append(navigate_command)

                    else:
                        #attack!
                        if not isinstance(closest_enemy_ships[0], int):
                            navigate_command = ship.navigate(
                                        ship.closest_point_to(closest_enemy_ships[0]),
                                        game_map,
                                        speed=int(game_environments.Halite.hlt.constants.MAX_SPEED),
                                        ignore_ships=False)

                            if navigate_command:
                                command_queue.append(navigate_command)

            except Exception as e:
                logging.info(str(e))
                
##            with open("c{}_input.vec".format(VERSION),"a") as f:
##                f.write(str( [round(item,3) for item in input_vector] ))
##                f.write('\n')
##
##            with open("c{}_out.vec".format(VERSION),"a") as f:
##                f.write(str(output_vector))
##                f.write('\n')

        except Exception as e:
            logging.info(str(e))

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
