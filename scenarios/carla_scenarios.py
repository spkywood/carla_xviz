"""
    Carla Visualization
"""

import math
import os, sys
import carla
from loguru import logger
import traceback

from xviz_avs import XVIZBuilder, \
    XVIZMetadataBuilder, \
    ANNOTATION_TYPES,\
    CATEGORY,\
    COORDINATE_TYPES,\
    SCALAR_TYPE,\
    PRIMITIVE_TYPES,\
    UIPRIMITIVE_TYPES

from xviz_avs.builder.xviz_ui_builder import XVIZContainerBuilder,\
    XVIZBaseUiBuilder,\
    XVIZMetricBuilder,\
    XVIZPanelBuilder,\
    XVIZPlotBuilder,\
    XVIZSelectBuilder,\
    XVIZTableBuilder,\
    XVIZTreeTableBuilder,\
    XVIZUIBuilder,\
    XVIZVideoBuilder


from xviz_avs.builder.declarative_ui import UI_TYPES, UI_LAYOUT, UI_INTERACTIONS

DEG_1_AS_RAD  = math.pi / 180
DEG_90_AS_RAD = 90 * DEG_1_AS_RAD
M_PI		  = 3.14159265358979323846

class CarlaScenario:
    def __init__(self, host='localhost', port=2000, time_out=3) -> None:
        self._host = host
        self._port = port
        self._timeout = time_out

        self.start_time = None
        self.end_time = None

        self.ego_vehicle = None

    def get_client(self):
        try:
            client = carla.Client(self._host, self._port)
            client.set_timeout(self._timeout)

            return client
        except:
            logger.info(traceback.format_exc())

    # get map json
    def get_map_json(self, map):
        topology = map.get_topology()

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


    def get_metabuilder(self):
        builder = XVIZMetadataBuilder()
        builder.stream("/vehicle_pose")\
            .category(CATEGORY.POSE)

        builder.stream("/game/time").category(CATEGORY.UI_PRIMITIVE)

        builder.stream("/object/vehicles")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POLYGON)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                'extruded' : True,
                'fill_color' : [200, 200, 0, 128],
                "height" : 2.0
            })

        builder.stream("/object/walkers")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POLYGON)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                "extruded": True,
                "fill_color": [0, 200, 70, 128],
                "height": 1.5
            })

        builder.stream("/object/tracking_vehicles")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.CIRCLE)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                'fill_color' : [200, 200, 0, 128]
            })

        builder.stream("/object/tracking_walkers")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.CIRCLE)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                "fill_color": [0, 200, 70, 128]
            })

        builder.stream("/vehicle/acceleration")\
            .category(CATEGORY.TIME_SERIES)\
            .unit("m/s^2")\
            .type(SCALAR_TYPE.FLOAT)
        
        builder.stream("/vehicle/velocity")\
            .category(CATEGORY.TIME_SERIES)\
            .unit("m/s")\
            .type(SCALAR_TYPE.FLOAT)

        builder.stream("/traffic/stop_signs")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POLYLINE)\
            .stream_style({
                "stroke_width": 0.1,
                "stroke_color": [200, 200, 0, 128]
            })\
            .style_class("vertical", {"stroke_width": 0.2, "stroke_color": [200, 200, 0, 128]})

        builder.stream("/traffic/traffic_lights")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POLYGON)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                "extruded": True, 
                "height": 0.1
            })\
            .style_class("red_state", {"fill_color": [200, 200, 0, 128]})\
            .style_class("yellow_state", {"fill_color": [200, 200, 0, 128]})\
            .style_class("green_state", {"fill_color": [200, 200, 0, 128]})\
            .style_class("unknown", {"fill_color": [200, 200, 0, 128]})
        
        builder.stream("/lidar/points")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POINT)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                "point_color_mode" : "ELEVATION",
                "radius_pixels" : 2
            })

        builder.stream("/radar/points")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POINT)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                "radius_pixels" : 2
            })

        builder.stream("/drawing/polylines")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POLYLINE)\
            .coordinate(COORDINATE_TYPES.IDENTITY)\
            .stream_style({
                "stroke_color" : [200, 200, 0, 128],
            "stroke_width" : 2.0
        })
        
        builder.stream("/drawing/points")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.POLYLINE)\
            .coordinate(COORDINATE_TYPES.IDENTITY)

        builder.stream("/drawing/texts")\
            .category(CATEGORY.PRIMITIVE)\
            .type(PRIMITIVE_TYPES.TEXT)\
            .coordinate(COORDINATE_TYPES.IDENTITY)
        
        builder.stream("/sensor/other/collision")\
            .category(CATEGORY.UI_PRIMITIVE)

        builder.stream("/sensor/other/gnss")\
            .category(CATEGORY.UI_PRIMITIVE)

        builder.stream("/sensor/other/imu")\
            .category(CATEGORY.UI_PRIMITIVE)

        builder.ui(self.get_ui([], ['/vehicle/acceleration'], ['/vehicle/velocity'], []))

        return builder

    def get_ui(self, cameras, acceleration_stream, velocity_stream, table_streams):
        ui_builder = XVIZUIBuilder()
        
        metrics = ui_builder.panel("Metrics")

        metrics_builder = ui_builder.container('metrics')
        metrics_builder.child(ui_builder.metric(streams=acceleration_stream, 
                                                  title='acceleration',
                                                  description='acceleration'))
        metrics_builder.child(ui_builder.metric(streams=velocity_stream,
                                                  title='velocity',
                                                  description='velocity'))
        metrics.child(metrics_builder)

        tables = ui_builder.panel("Tables")
        tables_builder = ui_builder.container('tables')
        tables_builder.child(ui_builder.table(stream="/game/time",
                                             title="time",
                                             description="/game/time"))
        tables_builder.child(ui_builder.table(stream="/sensor/other/collision",
                                             title="Collision",
                                             description="/sensor/other/collision"))
        tables_builder.child(ui_builder.table(stream="/sensor/other/gnss",
                                             title="GNSS",
                                             description="/sensor/other/gnss"))
        tables_builder.child(ui_builder.table(stream="/sensor/other/imu",
                                             title="Imu",
                                             description="/sensor/other/imu"))
        tables.child(tables_builder)

        ui_builder.child(metrics)
        ui_builder.child(tables)
        
        return ui_builder

    def get_update_data(self, world):
        world_snapshots = world.wait_for_tick(seconds=30)

        now_time = world_snapshots.timestamp.elapsed_seconds
        now_frame = world_snapshots.frame

        if self.start_time is None:
            self.start_time = now_time

        for world_snapshot in world_snapshots:
            id = world_snapshot.id
            actor = world.get_actor(id)
            if self.ego_vehicle is not None:
                continue
            
            for _key, _value in actor.attributes.items():
                if (_key == "role_name" and _value == "ego_vehicle"):
                    self.ego_vehicle = actor
                    logger.info('{} : {}'.format(_key, _value))
