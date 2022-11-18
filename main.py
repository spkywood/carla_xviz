import os
import json
import threading
from loguru import logger
import signal
from scenarios.carla_scenarios import CarlaScenario

from xviz_avs.io import XVIZGLBWriter, DirectorySource, XVIZJsonWriter

scenario = CarlaScenario()

OUTPUT_DIR = './_out/'    

def signal_handler(signum, stop):
    scenario.clear()
    logger.info("User ctrl+c exit.")
    os.kill(os.getpid(), signal.SIGKILL)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sink = DirectorySource(OUTPUT_DIR)
    
    # glb_writer = XVIZGLBWriter(sink)
    # json_writer = XVIZJsonWriter(sink)

    scenario.get_client()
    
    # world = client.get_world()
    # map = world.get_map()

    """
        Carla Map Data.
    """
    map_json = scenario.get_map_json()
    with open(OUTPUT_DIR + 'map.json', 'w') as fout:
        fout.write(json.dumps(map_json)) 

    threading.Thread(target=scenario.sensor_process, daemon=True).start()
    scenario.register_sensor()
    
    while True:
        scenario.get_update_data()


    # glb_writer.write_message(scenario.get_metabuilder().get_message())
    # json_writer.write_message(scenario.get_metabuilder().get_message())

    # json_writer.close()

if __name__ == '__main__':
    main()