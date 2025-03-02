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
print("Loading map {}...".format(scene_name))
if sim.current_scene == scene_name:
    sim.reset()
else:
    sim.load(scene_name)


# reset time of the day
sim.set_date_time(datetime(2022, 4, 1, 18, 0, 0, 0), True)
sim.weather = lgsvl.WeatherState(rain=0.8, fog=0.5, wetness=0.6, cloudiness=0.8, damage=0)
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
    sim.stop()
ego.on_collision(on_collision)

print(state.position)
print(forward)

finalPOVWaypointPosition = state.position - 2.15 * right
POVState = lgsvl.AgentState()
POVState.transform.position = state.position + (20) * forward - 8.5 * right
POVState.transform.rotation = lgsvl.Vector(0, -180, 0)
POV = sim.add_agent("SchoolBus", lgsvl.AgentType.NPC, POVState)
POV.on_collision(on_collision)
POV.follow_closest_lane(follow=True, max_speed=11.176)
sim.run(10)
POVWaypoints = []
POVWaypoints.append(lgsvl.DriveWaypoint(POVState.transform.position, MAX_POV_SPEED, POVState.transform.rotation))
POVWaypoints.append(lgsvl.DriveWaypoint(finalPOVWaypointPosition, 0, POVState.transform.rotation))

endOfRoad = state.position + 200 * forward

# NPC will follow the HD map at a max speed of 11.176 m/s (25 mph)
POV.follow_closest_lane(follow=True, max_speed=11.176)

 

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
destination = spawns[1].destinations[0]
dv.setup_apollo(destination.position.x, destination.position.z, modules)
dv.disable_apollo()
dv.setup_apollo(destination.position.x, destination.position.z, default_modules)
'''

sim.run(LGSVL__SIMULATION_DURATION_SECS)
sim.stop()
sim.close()

