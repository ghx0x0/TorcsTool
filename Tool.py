#!/usr/bin/python3
"""
author: zj
file: TorcsTool.py
time: 17-6-20
"""
from ctypes import cdll, c_int, c_uint8, c_double, c_bool,Structure, POINTER,c_float, sizeof
from itertools import chain
import numpy as np
import time
import sys
import os
from numpy.ctypeslib import ndpointer
import scipy.misc
import scipy
import math
import matplotlib.pyplot as plt
print(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
lib = cdll.LoadLibrary(dir_path + '/TorcsTool.so')
STUCK_ANGLE = 0.8

def clip(lo, x, hi):
    """

    :param lo:
    :param x:
    :param hi:
    :return: x -> [lo , hi]
    """
    # print(x)
    if x < lo:
        return lo
    elif x > hi:
        return hi
    else:
        return x


class Tool(object):
    class _29data(Structure):
        _fields_ = [
            ("angle",
             c_float),
            ("track",
             c_float * 19),
            ("trackPos",
             c_float),
            ("speedX",
             c_float),
            ("speedY",
             c_float),
            ("speedZ",
             c_float),
            ("wheelSpinVel",
             c_float * 4),
            ("rpm",
             c_float)
        ]
    class read(Structure):

        _fields_ = [
            ("steer",
             c_double),
            ("brake",
             c_double),
            ("accel",
             c_double),
            ("gear",
             c_int),
            ("clutch",
             c_double),
            ("speed_x",
             c_double),
            ("speed_y",
             c_double),
            ("speed_z",
             c_double),
            ("track_angle", # -pi,pi
             c_double),
            ("track_pos",
             c_double),
            ("rpm",
             c_double),
            ("radius",
             c_double)]

    
    def __init__(self,grab_shot=False,key=1234):
        lib.init.argtypes = [c_int]
        lib.init(key)
        if grab_shot:
            self.reserveScreenShotFlag()
        self.gear = 1
    def __str__(self):
        return("speed:{} steer:{} gear:{} clutch:{} accel:{} brake:{}"
               .format(str(self.speed), str(self.steer), str(self.gear), str(self.clutch), str(self.accel), str(self.brake)))

    def reserveScreenShotFlag(self):
        lib.reserveScreenShotFlag()

    def getStateCount(self):
        return len(self.allData)

    @property
    def _29data_size(self):
        return int(sizeof(self._29data) / 4)

    @property
    def get29Data(self):

        lib.get29Data.restype = POINTER(self._29data)
        x = lib.get29Data().contents
        # y = [x.speed_x,x.speed_y,x.speed_z,x.steer,x.brake]
        # array = x.track

        array = [getattr(x, key[0]) for key in x._fields_]
        result = []
        for i in array:
            if isinstance(i,float):
                result.append(i)
            else:
                result.extend(i)
        # array = [i if isinstance(i,float) else chain(i) for i in array]
        # result[-8] *= 300
        return np.asarray(result,dtype=np.float32)[None,:]
    @property
    def allData(self):
        lib.getStruct.restype = POINTER(self.read)
        x = lib.getStruct().contents
        # y = [x.speed_x,x.speed_y,x.speed_z,x.steer,x.brake]
        array = np.asarray([getattr(x, key[0]) for key in x._fields_])
        # array[0] =
        # array[1] =
        # array[2] =
        array[3] /= 6.
        array[5] /= 300.
        array[6] /= 300.
        array[7] /= 300.
        array[8] /= 3.1415
        # array[9] = clip(-1,array[9],1)
        array[10] /= 10000.
        array[11] /= 500.
        # if not self.pre:

        return array

    @property
    def image(self):
        lib.getScreenshot.restype = ndpointer(
            dtype=c_uint8, shape=(480, 640, 3))
        image = np.flipud(lib.getScreenshot())
        image = scipy.misc.imresize(image, [240, 320])
        return image

    def stop(self):
        lib.stopTorcsTool()
        lib.clearFinish()

    @property
    def track_angle(self):
        lib.getTrackAngle.restype = c_double
        angle = lib.getTrackAngle()
        return angle

    @property
    def is_hit_wall(self):
        lib.isHitWall.restype = c_bool

        return lib.isHitWall()

    @property
    def speed(self):
        lib.getSpeedX.restype = c_double
        speed = lib.getSpeedX()
        return speed

    @property
    def speed_y(self):
        lib.getSpeedY.restype = c_double
        speed = lib.getSpeedY()
        return speed

    @property
    def speed_z(self):
        lib.getSpeedY.restype = c_double
        speed = lib.getSpeedZ()
        return speed

    @property
    def radius(self):
        lib.getRadius.restype = c_double
        radius = lib.getRadius()
        return radius

    @property
    def rpm(self):
        lib.getRpm.restype = c_double
        rpm = lib.getRpm()
        return rpm

    @property
    def track_pos(self):
        lib.getTrackPos.restype = c_double
        pos = lib.getTrackPos()
        return pos

    @property
    def steer(self):
        lib.getSteer.restype = c_double
        steer = lib.getSteer()
        return steer

    @steer.setter
    def steer(self, _steer):
        lib.setSteer.argtypes = [c_double]
        _steer = clip(-1, _steer, 1)
        lib.setSteer(_steer)

    @property
    def brake(self):
        lib.getBrake.restype = c_double
        brake = lib.getBrake()
        return brake

    @brake.setter
    def brake(self, _brake):
        lib.setBrake.argtypes = [c_double]
        _brake = clip(0, _brake, 1)
        lib.setBrake(_brake)

    @property
    def clutch(self):
        lib.getClutch.restype = c_double
        clutch = lib.getClutch()
        return clutch

    @clutch.setter
    def clutch(self, _clutch):
        lib.setClutch.argtypes = [c_double]
        lib.setClutch(_clutch)

    @property
    def gear(self):
        lib.getGear.restype = c_int
        gear = lib.getGear()
        return gear

    @gear.setter
    def gear(self, _gear):
        lib.setGear.argtypes = [c_int]
        lib.setGear(_gear)
        # print("gear set to {}".format(_gear))

    @property
    def accel(self):
        lib.getAccel.restype = c_double
        accel = lib.getAccel()
        return accel

    @accel.setter
    def accel(self, _accel):
        lib.setAccel.argtypes = [c_double]
        _accel = clip(0, _accel, 1)
        lib.setAccel(_accel)

    @property
    def is_finish(self):
        lib.isFinish.restype = c_bool

        r = lib.isFinish()
        while lib.isFinish():
            # time.sleep(0.1)
            lib.clearFinish()
        return r

        # lib.clearFinish()
        # print(f)


    def restart(self):
        lib.restart()
        lib.clearFinish()
        lib.clearHitWall()
        lib.clearStuck()

    @property
    def is_stuck(self):
        lib.isStuck.restype = c_bool
        stuck = lib.isStuck()
        lib.clearStuck()
        return stuck or np.cos(self.track_angle) < 0

    def process_img(self,img):
        img = scipy.misc.imread( img )[ 90:156, 60:260 ]
        img = img / 127.5 - 1.
        return img

    @property
    def track(self):
        lib.getTrack.restype = ndpointer(
            dtype=c_float, shape=(19,))
        x = lib.getTrack()
        return np.array(lib.getTrack())

    @property
    def angle(self):
        lib.getAngle.restype = c_float
        return lib.getAngle()

if __name__ == '__main__':
    import pprint
    s = Tool(grab_shot=True)
    i = 0
    while True:
        # all 29 datas from scr_server
        print(s.get29Data)
        #s.restart()
        #scipy.misc.imsave('/home/zj/Desktop/torcs/{}.png'.format(str(i).zfill(9)),s.image)
        i+=1
        s.accel=1.
        s.steer=1.
        time.sleep(1)
