import os
import json

from scenarios.carla_scenarios import CarlaScenario

from xviz_avs.io import XVIZGLBWriter, DirectorySource, XVIZJsonWriter


OUTPUT_DIR = './output/'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sink = DirectorySource(OUTPUT_DIR)
    
    glb_writer = XVIZGLBWriter(sink)
    json_writer = XVIZJsonWriter(sink)

    scenario = CarlaScenario()

    carla_client = scenario.get_client()
    
    world = carla_client.get_world()
    map = world.get_map()

    """
        Carla Map Data.
    """
    map_json = scenario.get_map_json(map)
    with open(OUTPUT_DIR + 'map.json', 'w') as fout:
        fout.write(json.dumps(map_json)) 


    scenario.get_update_data(world)
    # glb_writer.write_message(scenario.get_metabuilder().get_message())
    json_writer.write_message(scenario.get_metabuilder().get_message())

    json_writer.close()

if __name__ == '__main__':
    main()