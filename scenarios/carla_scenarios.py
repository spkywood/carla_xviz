import os, sys
import math
import carla
from loguru import logger
import traceback
from queue import Queue
from time import sleep
import cv2
import numpy as np

import matplotlib.pyplot as plt

DEG_1_AS_RAD  = math.pi / 180
DEG_90_AS_RAD = 90 * DEG_1_AS_RAD
M_PI		  = 3.14159265358979323846

class CarlaScenario:
    """
        c_client: carla client
        c_map: Carla map
    """
    def __init__(self, host='localhost', port=2000, time_out=3) -> None:
        self._host = host
        self._port = port
        self._timeout = time_out

        self.run = True

        self.start_time = None
        self.end_time = None

        self.ego_vehicle = None

        self.traffic_lights = {}  # {id, []}
        
        self.c_client = None
        self.c_world = None
        self.c_map = None
        
        self.listen_sensor = {}
        self.frame_queue_ = Queue()
        self.imu_queue_ = Queue()
        self.image_queue_ = Queue()
        self.ego_acc = Queue()
        self.ego_vel = Queue()

    def get_client(self):
        try:
            self.c_client = carla.Client(self._host, self._port)
            self.c_client.set_timeout(self._timeout)

            self.c_world = self.c_client.get_world()
            self.c_map = self.c_world.get_map()
        except:
            logger.info(traceback.format_exc())

    # get map json
    def get_map_json(self):
        if self.c_map is None:
            self.get_client()

        topology = self.c_map.get_topology()

        map_json = {}
        map_json["type"] = "FeatureCollection"
        map_json["features"] = []

        idx = 0
        for point_pair in topology:
            self._add_one_side(point_pair[0], map_json, idx)
            self._add_one_side(point_pair[1], map_json, idx + 2)
            idx+=4

        return map_json

    def _add_one_side(self, waypoint, map_dict, idx):
        precision_ = 0.5

        waypoints = []
        road_id = waypoint.road_id
        next_waypoints = waypoint.next(precision_)
        waypoints.append(waypoint)

        while (next_waypoints):
            next_waypoint = next_waypoints[0]
            if (next_waypoint.road_id == road_id):
                waypoints.append(next_waypoint)
                next_waypoints = next_waypoint.next(precision_)
            else:
                break

        # logger.info(waypoints)
        points = []
        for waypoint in waypoints:
            points.append(self._lateral_shift(waypoint.transform, -waypoint.lane_width*0.5))

        self._add_one_line(points, road_id, map_dict, idx)

    
    def _lateral_shift(self, transform, shift):
        transform.rotation.yaw += 90.0
        p1 = [transform.location.x, transform.location.y, transform.location.z]
        tmp = shift * transform.get_forward_vector()
        p2 = [tmp.x, tmp.y, tmp.z]
        return [p1[0] + p2[0], p1[1] + p2[1], p1[2] + p2[2]]

    def _add_one_line(self, points, road_id, map_dict, idx):
        feature = dict()
        feature["id"] = str(idx)
        feature["type"] = "Feature"
        feature["properties"] = {"name" : str(road_id)}

        coordinates = []
        for point in points:
            coordinates.append([point[0], -point[1], point[2]])

        feature["geometry"] = {
            "coordinates" : coordinates,
            "type" : "LineString"
        }

        map_dict["features"].append(feature)

    @staticmethod
    def _imu_callback(data, id, queue):
        queue.put_nowait({data.frame: {id : data}})

    @staticmethod
    def _image_callback(data, id, queue):
        queue.put_nowait({data.frame: {id : data}})

    @staticmethod
    def compute_speed(v):
        return math.sqrt(v.x*v.x + v.y*v.y + v.z*v.z)

    def register_sensor(self):
        if self.c_world is None:
            self.get_client()

        actor_list = self.c_world.get_actors()
        # logger.info(actor_list)

        # sensor = None
        for actor in actor_list:
            actor_type = actor.type_id
            sensor = self.c_world.get_actor(actor.id)
            if actor_type == 'sensor.other.imu':
                sensor_id = sensor.id 
                if not self.listen_sensor.get(actor_list):
                    self.listen_sensor[sensor_id] = sensor
    
                    sensor.listen(lambda data: CarlaScenario._imu_callback(data, sensor_id, self.imu_queue_))
            elif actor_type == 'sensor.camera.rgb':
                sensor_id = sensor.id
                if not self.listen_sensor.get(actor_list):
                    self.listen_sensor[sensor_id] = sensor
                    sensor.listen(lambda data: CarlaScenario._image_callback(data, sensor_id, self.image_queue_))
            else:
                pass

        # for snapshot in snapshots:
        #     id = snapshot.id
        #     actor = 
        #     if self.ego_vehicle is not None:
        #         continue
            
        #     for _key, _value in actor.attributes.items():
        #         if (_key == "role_name" and _value == "ego_vehicle"):
        #             self.ego_vehicle = actor
        #             logger.info('{} : {}'.format(_key, _value))
    
    def sensor_process(self):
        plt.ion()   
        # plt.style.use("ggplot")
        # fig, ax = plt.subplots(figsize=(12, 7))
        acc_list = []
        vel_list = []
        x = []
        i = 0.05
        while self.run:
            frame_id = self.frame_queue_.get()
            imu_data = self.imu_queue_.get()
            if imu_data:
                imu = imu_data.get(frame_id)
                # if imu:
                #     logger.info(imu)

            image_data = self.image_queue_.get()
            if image_data:
                img = image_data.get(frame_id-1)
                if img:
                    for k, v in img.items():
                        array = np.frombuffer(v.raw_data, dtype=np.dtype("uint8"))
                        array = np.reshape(array, (v.height, v.width, 4))
                        array = array[:, :, :3]
                        cv2.imshow('img', array)
                        cv2.waitKey(1)
                        # cv2.imwrite('_out/{}.png'.format(frame_id), array)
            
            # acc_data = self.ego_acc.get()
            # if acc_data:
            #     acc = acc_data.get(frame_id)
            #     acc = CarlaScenario.compute_speed(acc)
            #     # logger.info('{} : {} - {} -{}'.format(frame_id, acc.x, acc.y, acc.z))
            #     logger.info(acc)
            #     acc_list.append(acc)

            # vel_data = self.ego_vel.get()
            # if vel_data:
            #     vel = vel_data.get(frame_id)
            #     vel = CarlaScenario.compute_speed(vel)
            #     logger.info(vel)
            #     vel_list.append(vel)
            #     # logger.info('{} : {} - {} -{}'.format(frame_id, vel.x, vel.y, vel.z))

            # x.append(i)
            # i+=0.05
            # plt.clf() 
            # plt.plot(x, acc_list)
            # plt.plot(x, vel_list)
            # plt.pause(0.001)

    # def image_process(self):
    #     while self.run:
    #         frame_id = self.frame_queue_.get()
    #         # logger.info(frame_id)
    #         imu_data = self.imu_queue_.get(frame_id)
    #         if imu_data:
    #             logger.info(imu_data)

    def get_update_data(self):
        if self.c_world is None:
            self.get_client()

        snapshots = self.c_world.wait_for_tick(seconds=2.0)

        now_time = snapshots.timestamp.elapsed_seconds
        now_frame = snapshots.frame
        # logger.info(now_frame)
        self.frame_queue_.put_nowait(now_frame)

        if self.start_time is None:
            self.start_time = now_time
        
        if self.ego_vehicle is None:
            
            for snapshot in snapshots:
                id = snapshot.id
                actor = self.c_world.get_actor(id)
            
                for _key, _value in actor.attributes.items():
                    if (_key == "role_name" and _value == "ego_vehicle"):
                        self.ego_vehicle = actor
                        logger.info('{} : {}'.format(_key, _value))
        
        self.ego_acc.put_nowait({now_frame : self.ego_vehicle.get_acceleration()})
        self.ego_vel.put_nowait({now_frame : self.ego_vehicle.get_velocity()})

    def traffic_ight_areas(self, actor):
        pass

    def stop_sign_areas(self, actor):
        pass

    def clear(self):
        for k, v in self.listen_sensor.items():
            logger.info('stop subscribe from {} : {}'.format(k, v))
            v.stop()