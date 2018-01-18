import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)
directions2 = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South, bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest, bc.Direction.Center]
tryRotate = [0, -1, 1, -2, 2]
random.seed(6137)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Ranger)

my_team = gc.team()
round = 0


def invert(loc):  # assumes Earth
    newx = earthMap.width - loc.x
    newy = earthMap.height - loc.y
    return bc.MapLocation(bc.Planet.Earth, newx, newy)


def locToStr(loc):
    return '(' + str(loc.x) + ',' + str(loc.y) + ')'





def rotate(dir, amount):
    ind = directions.index(dir)
    return directions[(ind + amount) % 8]


def goto(unit, dest):
    d = unit.location.map_location().direction_to(dest)
    if gc.can_move(unit.id, d):
        gc.move_robot(unit.id, d)


def fuzzygoto(unit, dest):
    toward = unit.location.map_location().direction_to(dest)
    for tilt in tryRotate:
        d = rotate(toward, tilt)
        if gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
            break


enemyStart = None
if gc.planet() == bc.Planet.Earth:
    oneLoc = gc.my_units()[0].location.map_location()
    earthMap = gc.starting_map(bc.Planet.Earth)
    enemyStart = invert(oneLoc);
    print('worker starts at ' + locToStr(oneLoc))
    print('enemy worker presumably at ' + locToStr(enemyStart))

numWorkers = 0
while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')
    units = [bc.UnitType.Knight, bc.UnitType.Ranger, bc.UnitType.Mage]
    x = random.choice(units)
    # frequent try/catches are a good idea
    try:
        # walk through our units:

        unity = gc.my_units()
        attackLoc = None
        attacked = False

        blueprintLocation = None
        blueprintWaiting = False
        for unit in gc.my_units():

            # first, factory logic
            d = random.choice(directions2)
            location = unit.location
            if unit.unit_type == bc.UnitType.Factory:
                if not unit.structure_is_built():
                    ml = unit.location.map_location()
                    blueprintLocation = ml
                    blueprintWaiting = True
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                        continue
                if gc.can_produce_robot(unit.id, x):
                    gc.produce_robot(unit.id, x)
                    print('produced a robot!')
                    continue

            if unit.unit_type == bc.UnitType.Worker:

                if numWorkers < 5 and gc.can_replicate(unit.id, d):
                    gc.replicate(unit.id, d)
                    numWorkers += 1
                    continue
                if gc.karbonite() > bc.UnitType.Factory.blueprint_cost():  # blueprint
                    if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                        gc.blueprint(unit.id, bc.UnitType.Factory, d)
                        continue
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        continue
                if blueprintWaiting:
                    if gc.is_move_ready(unit.id):
                        ml = unit.location.map_location()
                        bdist = ml.distance_squared_to(blueprintLocation)
                        if bdist > 2:
                            fuzzygoto(unit, blueprintLocation)
                if gc.can_harvest(unit.id, d):
                    gc.harvest(unit.id, d)
                    continue

            #if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
            if unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Factory and unit.unit_type != bc.UnitType.Rocket:
                if location.is_on_map():
                    nearby = gc.sense_nearby_units(location.map_location(), 2)
                    for other in nearby:
                        if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                            print('attacked a thing!')
                            gc.attack(unit.id, other.id)
                            attackLoc = location
                            attacked = True
                            continue
                        else:
                            if gc.is_move_ready(unit.id):
                                if gc.round() > 50:
                                    fuzzygoto(unit, enemyStart)
                                    continue

            # if unit.unit_type == bc.UnitType.Worker:
            #     if gc.can_harvest(unit.id, d):
            #         gc.harvest(unit.id, d)
            # first, let's look for nearby blueprints to work on









            # okay, there weren't any dudes around
            # pick a random direction:


            # or, try to build a factory:
            dir = random.choice(directions)



            # elif unit.unit_type == bc.UnitType.Worker and gc.can_replicate(unit.id, dir) and round % 10 == 0:
            #     gc.replicate(unit.id, dir)
            #     continue

            round += 1

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
