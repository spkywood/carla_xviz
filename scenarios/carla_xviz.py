"""
    Carla Visualization
"""

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

class CarlaXviz:
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