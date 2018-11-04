import numpy as np

"""
CONSTANTS
"""
MAX_LEN = 384.
MAX_WID = 256.
MIN_LEN = 240.
MIN_WID = 160.
MAX_DIAG = np.sqrt(MAX_LEN**2 + MAX_WID**2)
SHIP_RADIUS = 0.5
SHIP_MAX_HP = 255.
SHIP_MAX_SPEED = 7.
WEAPEN_RANGE = 5.
WEAPEN_DAMAGE = 64.

"""
Define all the rewards
"""
# WIN_GAME = 100.
SHOOT_DOWN = 6.
DOCK_EMPTY_COMPLETE = 6.
DOCK_SELF_COMPLETE = 3.
DOCKING = 0.5
MINING = 0.5
SHIP_DIE = -6.
KEEP_FLY = -0.5

"""
Define all the states for each craft:                                       3*n*n+5 
All states of each ship is a 1 by 29 list contains:
num of our ships                                                            1
nearest dock relative position                                              2
ship states (cargo vol,moving dir)                                          2
surrounding mine                                                            n*n
our ship position in n*n nearby area                                        n*n
enemy ship position and cargo in n*n nearby area                            n*n
"""

class Halite:

    def __init__(self, frame, ship_id, jason_file):
        """
        :param ship_id: ship's id (tag)
        """
        self.ship_id = ship_id
	self.frame = frame
        self.jason_file = jason_file
	self.ships = jason_file['frame']['ships']
	self.ship = self.ships[ship_id]
        self.friend_ships = []
        self.enemy_ships = []
        self.friend_planets = []
        self.enemy_planets = []
        self.empty_planets = []

    def get_self_info(self, ship_id):
        # Todo: return self position, vel, states, hp
        pass

    def get_global_info(self):
        # Todo: return (num of our ships, num of enemy ship, num of our planets, num of enemy planets)
        pass

    def get_nearest_empty_planets_info(self):
        # Todo: return dict{planets_id: distance, position, size, hp}
        pass

    def get_nearest_friend_planets_info(self):
        # Todo: return dict{planets_id: distance, position, size, hp, docked_ships}
        pass

    def get_nearest_enemy_planets_info(self):
        # Todo: return dict{planets_id: distance, position, size, hp, docked_ships}
        pass

    def get_nearest_friend_ships_info(self):
        # Todo: return dict{ship_id: distance, position, speed, status, hp}
        pass

    def get_nearest_enemy_ships_info(self):
        # Todo: return dict{ship_id: distance, position, speed, status, hp}
        pass

    def get_total_info(self):
        # Todo: return feature list
        pass

    def isWin(self):
        # Todo: return if win or not
        pass

    def isLose(self):
        # Todo: return if lose or not
        pass

    def reward_at_step(self):
        # Todo: return the reward get at this step
        pass
    
    # helper function
    def getShipOwner(self, ships, ship_id):
        """
        Get index of ship owner
        """
        if ship_id in ships['0'].keys():
            our_team = '0'
        else:
            our_team = '1'
        return our_team
    
    # helper function
    def getTeamSize(self, frame, ship_id):
        """
        Get tuple of size for both teams
        """
        ships = frame['ships']
        our_team_id = self.getShipOwner(ships, ship_id)
        their_team_id = '1' if our_team_id == '0' else '0'
        our_team_size = len(ships[our_team_id])
        their_team_size = len(ships['1'])
        return our_team_size, their_team_size

    '''
    Ship has 10 actions:
    Define all the action
    1, 2 Docking to nearest 1, 2 empty planet
    3, 4 Docking to nearest 1, 2 self planet
    5, 6 Attacking nearest 1, 2 enemy ship
    7, 8 Attacking nearest 1, 2 enemy planet
    9 Stay unchanged
    10 Random move
    In hindsight, this function could have been planned out better...
    '''

    # return a random move command
    def move_random(self):
        return
    # return a dock to planet command
    def dock_planet(self, planet_id):
        return
    # return an attacking command
    def attack_ship(self, ship_id):
        return
    # return an attack planet command
    def attack_planet(self, planet_id):
        return

    def move(self, action):
        rand_command = self.move_random()
        if action == 0:
            if nearest_1_empty_planet:
                command = self.dock_planet(planet_id)
                return command
            else:
                return rand_command
        elif action == 1:
            if nearest_2_empty_plant:
                command = self.dock_planet(planet_id)
                return command
            else:
                return rand_command
        elif action == 2:
            if nearest_1_self_planet:
                command = self.dock_planet(planet_id)
                return command
            else:
                return rand_command

        elif action == 3:
            if nearest_2_self_planet:
                command = self.aockplanet(planet_id)
                return command
            else:
                return rand_command

        elif action == 4:
            if nearest_1_enemyship:
                command = self.attack_ship(ship_id)
                return command
            else:
                return rand_command

        elif action == 5:
            if nearest_2_enemyship:
                command = self.attack_ship(ship_id)
                return command
            else:
                return rand_command

        elif action == 6:
            if nearest_1_enemyplant:
                command = self.attack_planet(plant_id)
                return command
            else:
                return rand_command

        elif action == 7:
            if nearest_2_enemyplant:
                command = self.attack_planet(plant_id)
                return command
            else:
                return rand_command

        elif action == 8:
            return command(no move)

        else:
            return rand_command
