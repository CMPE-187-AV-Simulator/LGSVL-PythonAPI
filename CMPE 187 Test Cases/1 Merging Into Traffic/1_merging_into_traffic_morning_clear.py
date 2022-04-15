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
LGSVL__SIMULATION_DURATION_SECS = 40.0
LGSVL__RANDOM_SEED = env.int("LGSVL__RANDOM_SEED", 51472)

vehicle_conf = env.str("LGSVL__VEHICLE_0", '99270b72-b957-47b0-af0d-7fdc92ddb384')
scene_name = env.str("LGSVL__MAP", lgsvl.wise.DefaultAssets.map_sanfrancisco)
sim = lgsvl.Simulator(SIMULATOR_HOST, SIMULATOR_PORT)
print("Loading map {}...".format(scene_name))
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name)


# reset time of the day
sim.set_date_time(datetime(2022, 4, 1, 9, 0, 0, 0), True)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]
forward = lgsvl.utils.transform_to_forward(state.transform)
print("Loading vehicle {}...".format(vehicle_conf))
ego = sim.add_agent(vehicle_conf, lgsvl.AgentType.EGO, state)

#Raise 
def on_collision(agent1, agent2, contact):
    raise Exception("{} collided with {}".format(agent1, agent2))
    sys.exit()
ego.on_collision(on_collision)

print(state.position)
print(forward)

POVList = []

POV1State = lgsvl.AgentState()
POV1State.transform = sim.map_point_on_lane(state.position + (20) * forward)
POV1 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POV1State)
POV1.on_collision(on_collision)
POVList.append(POV1)

POV2State = lgsvl.AgentState()
POV2State.transform = sim.map_point_on_lane(state.position + (30) * forward)
POV2 = sim.add_agent("Sedan", lgsvl.AgentType.NPC, POV2State)
POV2.on_collision(on_collision)
POVList.append(POV2)

POV3State = lgsvl.AgentState()
POV3State.transform = sim.map_point_on_lane(state.position + (10) * forward)
POV3 = sim.add_agent("SUV", lgsvl.AgentType.NPC, POV3State)
POV3.on_collision(on_collision)
POVList.append(POV3)

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


