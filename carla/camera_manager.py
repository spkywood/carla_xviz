import carla
from carla import ColorConverter as cc
from loguru import logger
from time import sleep

class CameraManager(object):

    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor

        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        bound_z = 0.5 + self._parent.bounding_box.extent.z

        self._camera_transform = carla.Transform(
            carla.Location(x=-1.5*bound_x, y=+0.0*bound_y, z=1.5*bound_z),
            carla.Rotation(pitch=8.0)
        )

        Attachment = carla.AttachmentType
        self._camera_attach = Attachment.SpringArm

        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()

        self.bp = bp_library.find('sensor.camera.rgb')
        self.bp.set_attribute('image_size_x', '1280')
        self.bp.set_attribute('image_size_y', '720')
        self.bp.set_attribute('fov', '110')
        self.bp.set_attribute('role_name', 'record_camera')
        self.bp.set_attribute('gamma', '2.2')

    def set_camera(self):
        if self.sensor is not None:
            self.sensor.destroy()

        self.sensor = self._parent.get_world().spawn_actor(
            self.bp,
            self._camera_transform,
            attach_to=self._parent,
            attachment_type=self._camera_attach
        )

        return self.sensor

def sensor_callback(sensor_data):
    # p = Process(target=save_to_disk, args=(sensor_data, task_id, ))
    # p.start()
    # logger.info('{} : {}'.format(sensor_data.width, sensor_data.height))
    queue.append(sensor_data)
    # pass

if __name__ == '__main__':
    queue = []

    logger.info("carla image Recode")
    client = carla.Client('localhost', 2000)
    world = client.get_world()

    world_snapshots = world.wait_for_tick(seconds = 30)
    sensor = None
    for world_snapshot in world_snapshots:
        id = world_snapshot.id
        actor = world.get_actor(id)
        if (actor.attributes.get('role_name') == 'ego_vehicle'):
            ego_actor = actor
            
            # logger.info(ego_actor)
            cm = CameraManager(ego_actor)
            sensor = cm.set_camera()
            sensor.listen(lambda data: sensor_callback(data))
    

    sleep(10)

    sensor.stop()
    logger.info("queue size {}".format(len(queue)))