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



import random
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

SIMULATOR_HOST = env.str("LGSVL__SIMULATOR_HOST", "127.0.0.1")
SIMULATOR_PORT = env.int("LGSVL__SIMULATOR_PORT", 8181)

#Bridge Disabled
#BRIDGE_HOST = env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1")
#BRIDGE_PORT = env.int("LGSVL__AUTOPILOT_0_PORT", 9090)

#LGSVL__AUTOPILOT_HD_MAP = env.str("LGSVL__AUTOPILOT_HD_MAP", "SanFrancisco")
#LGSVL__AUTOPILOT_0_VEHICLE_CONFIG = env.str("LGSVL__AUTOPILOT_0_VEHICLE_CONFIG", 'Lincoln2017MKZ')
LGSVL__SIMULATION_DURATION_SECS = 80.0
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
state.transform = spawns[3]
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
signals = sim.get_controllables("signal")
for signal in signals:
    signal.control("green=3")
    
sim.add_random_agents(lgsvl.AgentType.PEDESTRIAN)

names = [
    "Bob",
    "EntrepreneurFemale",
    "Howard",
    "Johny",
    "Pamela",
    "Presley",
    "Robin",
    "Stephen",
    "Zoe",
]

print("Creating 120 pedestrians")
for i in range(20 * 6):
    # Create peds in a block
    start = (
        spawns[3].position + 150 * forward
        + (5 + (1.0 * (i // 6))) * forward
        - (2 + (1.0 * (i % 6))) * right
    )
    end = start + 10 * forward

    # Give waypoints for the spawn location and 10m ahead
    wp = [lgsvl.WalkWaypoint(start, 0), lgsvl.WalkWaypoint(end, 0)]

    state = lgsvl.AgentState()
    state.transform.position = start
    state.transform.rotation = spawns[3].rotation
    name = random.choice(names)

    # Send the waypoints and make the pedestrian loop over the waypoints
    p = sim.add_agent(name, lgsvl.AgentType.PEDESTRIAN, state)
    # Pedestrian will walk to a random point on sidewalk
    p.walk_randomly(True)
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

sim.run(LGSVL__SIMULATION_DURATION_SECS)

