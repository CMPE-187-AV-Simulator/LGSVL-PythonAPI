import os
import lgsvl
from environs import env

env = Env()

sim = lgsvl.Simulator(
    env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host),
    env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port)
)

if sim.current_scene == lgsvl.wise.DefaultAssets.map_borregasave:
    sim.reset()
else:
    sim.load(lgsvl.wise.DefaultAssets.map_borregasave)

spawns = sim.get_spawn()

state = lgsvl.AgentState()
state.transform = spawns[0]

ego = sim.add_agent(lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5, lgsvl.AgentType.EGO, state)
ego.connect_bridge(
    env.str("LGSVL__AUTOPILOT_0_HOST", lgsvl.wise.SimulatorSettings.bridge_host),
    env.int("LGSVL__AUTOPILOT_0_PORT", lgsvl.wise.SimulatorSettings.bridge_port)
)

# Dreamview setup
dv = lgsvl.dreamview.Connection(sim, ego, env.str("LGSVL__AUTOPILOT_0_HOST", "127.0.0.1"))
dv.set_hd_map('Borregas Ave')
dv.set_vehicle('Lincoln2017MKZ')
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

sim.run()