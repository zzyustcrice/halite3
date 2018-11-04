#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
import sys
import os
import tensorflow as tf
# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
from hlt.positionals import Position
# This library allows you to generate random numbers.
import random
import numpy as np
# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
COEFofMOV = 0.008;
MOVEBACKCUT = 900;
MOVEBACKBOTCUT = 700;
ASMALLPOSITIVE = 1e-5;
EXPULDIS=7;
wid = game.game_map.width
height = game.game_map.height;
if wid == 56: MAXTURN = 476
if wid == 40: MAXTURN = 426
if wid == 32: MAXTURN = 401
if wid == 64: MAXTURN = 501
if wid == 48: MAXTURN = 451

occupied = np.zeros((wid, height));
backshipid = set();
priorityset=set();
""" <<<Game Loop>>> """

def shipgoingback (ship,game_map,me,occupied,command_queue):
    backshipid.add(ship.id);
    dis = game_map.calculate_distance(ship.position, shipyard.position)
    tarx = shipyard.position.x
    tary = shipyard.position.y
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(ship.position, dropoff.position);
        if dis > dis2:
            dis = dis2
            tarx = dropoff.position.x
            tary = dropoff.position.y
    if tarx-ship.position.x>wid/2:tarx-=wid;
    elif ship.position.x-tarx>wid/2:tarx+=wid;
    if tary-ship.position.y>height/2:tary-=height;
    elif ship.position.y-tary>height/2:tary+=height;
    tempos = Position(ship.position.x, ship.position.y);
    tempos.y += 1;
    tempos = game_map.normalize(tempos);
    if tary <= ship.position.y or occupied[tempos.x, tempos.y] == 1 :
        p1 = 0
    else:
        p1 = 1;
    tempos = Position(ship.position.x, ship.position.y);
    tempos.x += 1;
    tempos = game_map.normalize(tempos);
    if tarx <= ship.position.x or occupied[tempos.x, tempos.y] == 1 :
        p2 = 0
    else:
        p2 = 1
    tempos = Position(ship.position.x, ship.position.y);
    tempos.y -= 1;
    tempos = game_map.normalize(tempos);
    if tary >= ship.position.y or occupied[tempos.x, tempos.y] == 1 :
        p3 = 0
    else:
        p3 = 1
    tempos = Position(ship.position.x, ship.position.y);
    tempos.x -= 1;
    tempos = game_map.normalize(tempos);
    if tarx >= ship.position.x or occupied[tempos.x, tempos.y] == 1:
        p4 = 0
    else:
        p4 = 1
    # print(ship.id,ship.position.x,ship.position.y,tarx,tary,"p1=",p1,"p2=",p2,"p3=",p3,"p4=",p4,file=sys.stderr);
    sum = p1 + p2 + p3 + p4
    if sum > 0:
        p1 = float(p1) / sum;
        p2 = float(p2) / sum;
        p3 = float(p3) / sum;
        p4 = float(p4) / sum;
        r = np.random.random();
        if r < p1:
            command_queue.append(ship.move(Direction.South))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.y += 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p2 + p1):
            command_queue.append(ship.move(Direction.East))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.x += 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p1 + p2 + p3):
            command_queue.append(ship.move(Direction.North))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.y -= 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        else:
            command_queue.append(ship.move(Direction.West))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.x -= 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
    else:
        command_queue.append(ship.stay_still())
def forcingshipgoingback (ship,game_map,me,occupied,command_queue):
    backshipid.add(ship.id);
    dis = game_map.calculate_distance(ship.position, shipyard.position)
    tarx = shipyard.position.x
    tary = shipyard.position.y
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(ship.position, dropoff.position);
        if dis > dis2:
            dis = dis2
            tarx = dropoff.position.x
            tary = dropoff.position.y
    if tarx-ship.position.x>wid/2:tarx-=wid;
    elif ship.position.x-tarx>wid/2:tarx+=wid;
    if tary-ship.position.y>height/2:tary-=height;
    elif ship.position.y-tary>height/2:tary+=height;
    tempos = Position(ship.position.x, ship.position.y);
    tempos.y += 1;
    tempos = game_map.normalize(tempos);
    if occupied[tempos.x, tempos.y] == 1 :
        p1 = 0
    elif tary <= ship.position.y :
        p1 = 0.0;
    else:p1=1;
    tempos = Position(ship.position.x, ship.position.y);
    tempos.x += 1;
    tempos = game_map.normalize(tempos);
    if occupied[tempos.x, tempos.y] == 1 :
        p2 = 0
    elif tarx <= ship.position.x :
        p2 = 0.0
    else: p2=1;
    tempos = Position(ship.position.x, ship.position.y);
    tempos.y -= 1;
    tempos = game_map.normalize(tempos);
    if occupied[tempos.x, tempos.y] == 1 :
        p3 = 0
    elif tary >= ship.position.y:
        p3 = 0.0
    else :p3=1;
    tempos = Position(ship.position.x, ship.position.y);
    tempos.x -= 1;
    tempos = game_map.normalize(tempos);
    if occupied[tempos.x, tempos.y] == 1 :
        p4 = 0
    elif tarx >= ship.position.x:
        p4 = 0.0
    else: p4=1;
    # print(ship.id,ship.position.x,ship.position.y,tarx,tary,"p1=",p1,"p2=",p2,"p3=",p3,"p4=",p4,file=sys.stderr);
    sum = p1 + p2 + p3 + p4
    if sum > 0:
        p1 = float(p1) / sum;
        p2 = float(p2) / sum;
        p3 = float(p3) / sum;
        p4 = float(p4) / sum;
        r = np.random.random();
        if r < p1:
            command_queue.append(ship.move(Direction.South))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.y += 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p2 + p1):
            command_queue.append(ship.move(Direction.East))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.x += 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p1 + p2 + p3):
            command_queue.append(ship.move(Direction.North))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.y -= 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        else:
            command_queue.append(ship.move(Direction.West))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.x -= 1;
            tempos = game_map.normalize(tempos);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
    else:
        command_queue.append(ship.stay_still())
def explore(ship,game_map,occupied,command_queue):
    tempos = Position(ship.position.x, ship.position.y);
    tempos.y += 1;
    tempos = game_map.normalize(tempos);
    dis = game_map.calculate_distance(ship.position, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(ship.position, dropoff.position);
        if dis > dis2:
            dis = dis2
    newdis = game_map.calculate_distance(tempos, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(tempos, dropoff.position);
        if newdis > dis2:
            newdis = dis2
    if occupied[tempos.x, tempos.y] == 1 or game_map[tempos].is_occupied or (newdis<dis and dis<EXPULDIS):
        p1 = 0
    else:
        p1 = max(ASMALLPOSITIVE,
                 COEFofMOV * (game_map[tempos].halite_amount - 0.1 * game_map[ship.position].halite_amount));
    tempos = Position(ship.position.x, ship.position.y);
    tempos.x += 1;
    tempos = game_map.normalize(tempos);
    dis = game_map.calculate_distance(ship.position, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(ship.position, dropoff.position);
        if dis > dis2:
            dis = dis2
    newdis = game_map.calculate_distance(tempos, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(tempos, dropoff.position);
        if newdis > dis2:
            newdis = dis2
    if occupied[tempos.x, tempos.y] == 1 or game_map[tempos].is_occupied or (newdis<dis and dis<EXPULDIS):
        p2 = 0
    else:
        p2 = max(ASMALLPOSITIVE,
                 COEFofMOV * (game_map[tempos].halite_amount - 0.1 * game_map[ship.position].halite_amount));
    tempos = Position(ship.position.x, ship.position.y);
    tempos.y -= 1;
    tempos = game_map.normalize(tempos);
    dis = game_map.calculate_distance(ship.position, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(ship.position, dropoff.position);
        if dis > dis2:
            dis = dis2
    newdis = game_map.calculate_distance(tempos, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(tempos, dropoff.position);
        if newdis > dis2:
            newdis = dis2
    if occupied[tempos.x, tempos.y] == 1 or game_map[tempos].is_occupied or (newdis<dis and dis<EXPULDIS):
        p3 = 0
    else:
        p3 = max(ASMALLPOSITIVE,
                 COEFofMOV * (game_map[tempos].halite_amount - 0.1 * game_map[ship.position].halite_amount));
    tempos = Position(ship.position.x, ship.position.y);
    tempos.x -= 1;
    tempos = game_map.normalize(tempos);
    dis = game_map.calculate_distance(ship.position, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(ship.position, dropoff.position);
        if dis > dis2:
            dis = dis2
    newdis = game_map.calculate_distance(tempos, shipyard.position)
    for dropoff in me.get_dropoffs():
        dis2 = game_map.calculate_distance(tempos, dropoff.position);
        if newdis > dis2:
            newdis = dis2
    if occupied[tempos.x, tempos.y] == 1 or game_map[tempos].is_occupied or (newdis<dis and dis<EXPULDIS):
        p4 = 0
    else:
        p4 = max(ASMALLPOSITIVE,
                 COEFofMOV * (game_map[tempos].halite_amount - 0.1 * game_map[ship.position].halite_amount));
    p5 = 0.25 * game_map[ship.position].halite_amount;
    sum = p1 + p2 + p3 + p4 + p5;
    if sum > 0:
        p1 = float(p1) / sum;
        p2 = float(p2) / sum;
        p3 = float(p3) / sum;
        p4 = float(p4) / sum;
        r = np.random.random();
        if r < p1:
            command_queue.append(ship.move(Direction.South))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.y += 1;
            tempos = game_map.normalize(tempos);  #
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p2 + p1):
            command_queue.append(ship.move(Direction.East))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.x += 1;
            tempos = game_map.normalize(
                tempos);  # print(ship.id,ship.position.x,ship.position.y,"p2=",p2,occupied[tempos.x,tempos.y],file=sys.stderr);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p1 + p2 + p3):
            command_queue.append(ship.move(Direction.North))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.y -= 1;
            tempos = game_map.normalize(
                tempos);  # print(ship.id,ship.position.x,ship.position.y,"p3=",p3,occupied[tempos.x,tempos.y],file=sys.stderr);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        elif r < (p1 + p2 + p3 + p4):
            command_queue.append(ship.move(Direction.West))
            tempos = Position(ship.position.x, ship.position.y);
            tempos.x -= 1;
            tempos = game_map.normalize(
                tempos);  # print(ship.id,ship.position.x,ship.position.y,"p4=",p4,occupied[tempos.x,tempos.y],file=sys.stderr);
            occupied[tempos.x, tempos.y] = 1
            occupied[ship.position.x, ship.position.y] = 0
        else:
            command_queue.append(
                ship.stay_still());  # print(ship.id,ship.position.x,ship.position.y,"p5=",p5,occupied[tempos.x,tempos.y],file=sys.stderr);
    else:
        command_queue.append(
            ship.stay_still());  # print(ship.id,ship.position.x,ship.position.y,"p5=",p5,occupied[tempos.x,tempos.y],file=sys.stderr)
def shiploop(ship,game_map,me,occupied,command_queue):
    if MAXTURN - game.turn_number > wid:
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if ship.halite_amount < 0.1 * game_map[ship.position].halite_amount:
            command_queue.append(ship.stay_still())
            return;
        if ship.halite_amount < MOVEBACKBOTCUT and ship.id in backshipid:
            backshipid.remove(ship.id);
        if ship.halite_amount < MOVEBACKCUT and ship.id not in backshipid:
            explore(ship, game_map, occupied, command_queue)
        else:
            shipgoingback(ship, game_map, me, occupied, command_queue)
    else:
        dis = game_map.calculate_distance(ship.position, shipyard.position)
        tarx = shipyard.position.x
        tary = shipyard.position.y
        for dropoff in me.get_dropoffs():
            dis2 = game_map.calculate_distance(ship.position, dropoff.position);
            if dis > dis2:
                dis = dis2
                tarx = dropoff.position.x
                tary = dropoff.position.y
        if MAXTURN - game.turn_number > dis + totalship / 4 + 6:
            if ship.halite_amount < 0.1 * game_map[ship.position].halite_amount:
                command_queue.append(ship.stay_still())
                return;
            if ship.halite_amount < MOVEBACKBOTCUT and ship.id in backshipid:
                backshipid.remove(ship.id);
            if ship.halite_amount < MOVEBACKCUT and ship.id not in backshipid:
                explore(ship, game_map, occupied, command_queue)
            else:
                shipgoingback(ship, game_map, me, occupied, command_queue)
        else:
            forcingshipgoingback(ship, game_map, me, occupied, command_queue)
            occupied[shipyard.position.x, shipyard.position.y] = 0;
while True:

    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    totalship = len(me.get_ships());
    game_map = game.game_map
    shipyard = me.shipyard
    priorityset.clear();
    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    occupied = np.zeros((wid, height));
    for ship in me.get_ships():
        occupied[ship.position.x, ship.position.y] = 1;
        if ship.position==shipyard.position:priorityset.add(ship)
        for dropoff in me.get_dropoffs():
            if ship.position == dropoff.position: priorityset.add(ship)
    for ship in priorityset:shiploop(ship,game_map,me,occupied,command_queue)
    for ship in me.get_ships():
        if ship not in priorityset:
            shiploop(ship, game_map, me, occupied, command_queue)

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    nearshipyard1 = 0;
    nearshipyard2 = 0
    for id in backshipid:
        distancetoshipyard = 1000;
        if (me.has_ship(id)): distancetoshipyard = game_map.calculate_distance(me.get_ship(id).position,
                                                                               me.shipyard.position)
        if (distancetoshipyard < 2): nearshipyard2 += 1;
        if (distancetoshipyard < 1): nearshipyard1 += 1;
    if game.turn_number <= MAXTURN*0.6 and me.halite_amount >= constants.SHIP_COST and occupied[
        me.shipyard.position.x, me.shipyard.position.y] == 0 and nearshipyard1 == 0 and nearshipyard2 <= 3:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

