__all__ = ('SensorNotFound', 'SensorListener', 'sensortypes')

from jnius import PythonJavaClass, java_method, autoclass, cast

PythonActivity = autoclass('org.renpy.android.PythonActivity')
Context = autoclass('android.content.Context')
Sensor = autoclass('android.hardware.Sensor')
SensorManager = autoclass('android.hardware.SensorManager')

sensortypes = {
    'accelerometer': Sensor.TYPE_ACCELEROMETER,
    'magnetic-field': Sensor.TYPE_MAGNETIC_FIELD,
    'gyroscope': Sensor.TYPE_GYROSCOPE,
    'light': Sensor.TYPE_LIGHT,
    'pressure': Sensor.TYPE_PRESSURE,
    'proximity': Sensor.TYPE_PROXIMITY,
    'linear-acceleration': Sensor.TYPE_LINEAR_ACCELERATION,
    #'rotation-vector': Sensor.TYPE_ROTATION_VECTOR, #API 9
    'orientation': Sensor.TYPE_ORIENTATION,
    #'humidity': Sensor.TYPE_RELATIVE_HUMDITY, #API 14
    'ambient-temperature': Sensor.TYPE_AMBIENT_TEMPERATURE }


class SensorNotFound(Exception):
    pass

class SensorListener(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/SensorEventListener']

    def __init__(self, sensortype, callback):
        super(SensorListener, self).__init__()
        self.callback = callback
        assert(sensortype in sensortypes)

        self.manager = cast('android.hardware.SensorManager',
                PythonActivity.mActivity.getSystemService(Context.SENSOR_SERVICE))

        self.do_stop = False
        java_sensortype = sensortypes[sensortype]
        self.sensortype = java_sensortype
        self.sensor = self.manager.getDefaultSensor(java_sensortype)
        if self.sensor is None:
            raise SensorNotFound()

    def start(self):
        self.do_stop = False
        self.manager.registerListener(self, self.sensor,
                SensorManager.SENSOR_DELAY_NORMAL)

    def stop(self):
        self.do_stop = True
        self.manager.unregisterListener(self, self.sensor)

    @java_method('()I')
    def hashCode(self):
        return id(self)

    @java_method('(Landroid/hardware/Sensor;I)V')
    def onAccuracyChanged(self, sensor, accuracy):
        if self.do_stop:
            print 'sensor avoided accuracy-changed, stop has been called.'
            return
        self.callback(self, 'accuracy-changed', sensor, accuracy)

    @java_method('(Landroid/hardware/SensorEvent;)V')
    def onSensorChanged(self, event):
        if self.do_stop:
            print 'sensor avoided sensor-changed, stop has been called.'
            return
        self.callback(self, 'sensor-changed', event)

