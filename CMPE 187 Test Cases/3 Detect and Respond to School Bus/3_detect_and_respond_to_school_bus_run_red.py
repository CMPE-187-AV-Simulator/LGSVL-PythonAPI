#!/usr/bin/env python3
#
# CMPE 187 - Project Group 11
#   John A. Bautista
#   Tue Do
#   Anh Nguyen
#   Aaron Rice
#
# This software contains some code snipets provided by the LGSVL Python API Guide.
#   https://www.svlsimulator.com/docs/python-api/python-api/
#



import time
from datetime import datetime
import lgsvl
import sys
from environs import Env



'''
LGSVL__AUTOPILOT_0_HOST             IP address of the computer running the bridge to connect to
LGSVL__AUTOPILOT_0_PORT             Port that the bridge listens on for messages
LGSVL__AUTOPILOT_0_VEHICLE_CONFIG   Vehicle configuration to be loaded in Dreamview (Capitalization and spacing must match the dropdown in Dreamview)
LGSVL__AUTOPILOT_HD_MAP             HD map to be loaded in Dreamview (Capitalization and spacing must match the dropdown in Dreamview)
LGSVL__MAP                          ID of map to be loaded in Simulator
LGSVL__RANDOM_SEED                  Simulation random seed
LGSVL__SIMULATION_DURATION_SECS     How long to run the simulation for
LGSVL__SIMULATOR_HOST               IP address of computer running simulator (Master node if a cluster)
LGSVL__SIMULATOR_PORT               Port that the simulator allows websocket connections over
LGSVL__VEHICLE_0                    ID of EGO vehicle to be loaded in Simulator
'''

env = Env()

MAX_EGO_SPEED = 11.18  # (40 km/h, 25 mph)
SPEED_VARIANCE = 10  # Simple Physics does not return an accurate value
MAX_POV_SPEED = 8.94  # (32 km/h, 20 mph)
MAX_POV_ROTATION = 5  # deg/s
TIME_LIMIT = 30  # seconds
TIME_DELAY = 5
MAX_FOLLOWING_DISTANCE = 100  # Apollo 3.5 is very cautious

SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)

#Bridge Disabled
#BRIDGE_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
#BRIDGE_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

#LGSVL__AUTOPILOT_HD_MAP = env.str("LGSVL__AUTOPILOT_HD_MAP", "SanFrancisco")
#LGSVL__AUTOPILOT_0_VEHICLE_CONFIG = env.str("LGSVL__AUTOPILOT_0_VEHICLE_CONFIG", 'Lincoln2017MKZ')
LGSVL__SIMULATION_DURATION_SECS = 40.0
LGSVL__RANDOM_SEED = env.int("LGSVL__RANDOM_SEED", 51472)

vehicle_conf = env.str("LGSVL__VEHICLE_0", '99270b72-b957-47b0-af0d-7fdc92ddb384')
scene_name = env.str("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_sanfrancisco)
sim = lgsvl.Simulator(SIMULATOR_HOST, SIMULATOR_PORT)
try:
    print("Loading map {}...".format(scene_name))
    sim.load(scene_name) # laod map with random seed
except Exception:
    if sim.current_scene == scene_name:
        sim.reset()
    else:
        sim.load(scene_name)


# reset time of the day
sim.set_date_time(datetime(2022, 4, 1, 9, 0, 0, 0), True)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[1]
forward = lgsvl.utils.transform_to_forward(state.transform)
right = lgsvl.utils.transform_to_right(state.transform)
print("Loading vehicle {}...".format(vehicle_conf))
ego = sim.add_agent(vehicle_conf, lgsvl.AgentType.EGO, state)

#Raise 
def on_collision(agent1, agent2, contact):
    raise Exception("{} collided with {}".format(agent1, agent2))
    sys.exit()
ego.on_collision(on_collision)

print(state.position)
print(forward)

POVState = lgsvl.AgentState()
POVState.transform = sim.map_point_on_lane(state.position + 50 * forward)
POV = sim.add_agent("SchoolBus", lgsvl.AgentType.NPC, POVState)

POV.on_collision(on_collision)
print("adding npcs")
sim.add_random_agents(lgsvl.AgentType.NPC)
sim.add_random_agents(lgsvl.AgentType.PEDESTRIAN)
endOfRoad = state.position + 200 * forward
# Set all the traffic lights to green.
# It is possible to set only the lights visible by the EGO to green, but positions of the lights must be known
signals = sim.get_controllables("signal")
for signal in signals:
    signal.control("green=3")
# NPC will follow the HD map at a max speed of 11.176 m/s (25 mph)
POV.follow_closest_lane(follow=True, max_speed=11.176)

# Run Simulation for 3 seconds
sim.run(3)

# Force the NPC to come to a stop
control = lgsvl.NPCControl()
control.e_stop = True

POV.apply_control(control)

sim.run(20) 

# Dreamview setup Disabled
'''
print("Connecting to bridge...")
# The EGO is now looking for a bridge at the specified IP and port
ego.connect_bridge(BRIDGE_HOST, BRIDGE_PORT)
dv = lgsvl.dreamview.Connection(sim, ego, BRIDGE_HOST)
dv.set_hd_map(LGSVL__AUTOPILOT_HD_MAP)
dv.set_vehicle(LGSVL__AUTOPILOT_0_VEHICLE_CONFIG)
modules = [
    'Localization',
    'Perception',
    'Transform',
    'Routing',
    'Prediction',
    'Planning',
    'Camera',
    'Traffic Light',
    'Control'
]
destination = spawns[0].destinations[0]
dv.setup_apollo(destination.position.x, destination.position.z, modules)
dv.disable_apollo()
dv.setup_apollo(destination.position.x, destination.position.z, default_modules)
'''
try:
    t0 = time.time()
    sim.run(TIME_DELAY)  # The EGO should start moving first
    POV.follow_closest_lane(True, MAX_POV_SPEED, False)
    while True:
        sim.run(0.5)
        egoCurrentState = ego.state
        if egoCurrentState.speed > MAX_EGO_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "Ego speed exceeded limit, {} > {} m/s".format(egoCurrentState.speed, MAX_EGO_SPEED + SPEED_VARIANCE)
            )
        POVCurrentState = POV.state
        if POVCurrentState.speed > MAX_POV_SPEED + SPEED_VARIANCE:
            raise lgsvl.evaluator.TestException(
                "POV speed exceeded limit, {} > {} m/s".format(POVCurrentState.speed, MAX_POV_SPEED + SPEED_VARIANCE)
            )
        if POVCurrentState.angular_velocity.y > MAX_POV_ROTATION:
            raise lgsvl.evaluator.TestException(
                "POV angular rotation exceeded limit, {} > {} deg/s".format(
                    POVCurrentState.angular_velocity, MAX_POV_ROTATION
                )
            )
        if lgsvl.evaluator.separation(POVCurrentState.position, endOfRoad) < 5:
            break
        if time.time() - t0 > TIME_LIMIT:
            break
except lgsvl.evaluator.TestException as e:
    exit("FAILED: {}".format(e))

separation = lgsvl.evaluator.separation(egoCurrentState.position, POVCurrentState.position)

sim.run(LGSVL__SIMULATION_DURATION_SECS)
sim.stop()
sim.close()

