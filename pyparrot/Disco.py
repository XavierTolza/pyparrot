from threading import Thread
from time import sleep

import scipy as scipy

from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision


class DiscoError(Exception):
    pass


class DiscoConnectError(DiscoError):
    def __init__(self):
        super(DiscoConnectError, self).__init__("Cannot connect to Disco")


class DiscoVisionError(DiscoError):
    pass


class DiscoVision(object):
    def __init__(self, disco_instance, callback=None):
        self.callback = callback
        self.disco_instance = disco_instance
        self.__dv = None

    def start(self):
        self.__dv = dv = DroneVision(self.disco_instance, is_bebop=True)

        def callback(*args, **kwargs):
            if self.callback is not None:
                img = dv.get_latest_valid_picture()
                self.callback(img)

        dv.set_user_callback_function(callback, user_callback_args=None)
        if not dv.open_video():
            raise DiscoVisionError("Cannot start video stream")

    def stop(self):
        self.__dv.close_video()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def latest_image(self):
        return self.__dv.get_latest_valid_picture()


class Disco(Bebop):
    def __init__(self, ip_adress=None):
        super(Disco, self).__init__(drone_type="Disco", ip_address=ip_adress)

    def __enter__(self):
        if not self.connect(10):
            raise DiscoConnectError()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def video_stream(self, callback=None):
        return DiscoVision(self, callback=callback)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot

    def callback(x):
        scipy.imsave('/tmp/outfile.jpg', x)

    with Disco() as d:
        with d.video_stream(callback=callback) as stream:
            d.smart_sleep(10)
