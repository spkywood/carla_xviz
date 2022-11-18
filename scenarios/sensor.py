import carla

class CarlaImage:
    def __init__(self, id, frame_id, data) -> None:
        self._id = id
        self._frame_id = frame_id
        self._data = data