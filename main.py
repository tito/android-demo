'''
Android API demonstration, from Python
======================================

This demonstration shows how you could access to Android API from Python, using
PyJNIus. Please note that this is not that easy, and we intend to develop one
more library that will be called Plyer, to access easily to some features of the
platform.
'''

__version__ = '1.0'

import kivy
kivy.require('1.6.1')

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty, StringProperty, \
        NumericProperty, BooleanProperty, AliasProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from lib.sensor import SensorListener, SensorNotFound, sensortypes
from lib.gps import GpsListener


class NumberSlider(FloatLayout):
    title = StringProperty()
    unit = StringProperty()
    value = NumericProperty()
    min = NumericProperty()
    max = NumericProperty()

    def on_value(self, instance, value):
        if self.min is None:
            self.min = value
        elif self.min > value:
            self.min = value
        if self.max is None:
            self.max = value
        elif self.max < value:
            self.max = value

    def get_normalized_value(self):
        if self.max is None or self.min is None:
            rg = 1.
        else:
            rg = float(max(1., self.max - self.min))
        return self.value / rg
    normalized_value = AliasProperty(get_normalized_value, None, bind=('value',
        'min', 'max'))


class MainUI(FloatLayout):
    dropdown = ObjectProperty()
    maincontent = ObjectProperty()
    maininit = BooleanProperty()


class AndroidDemoApp(App):

    categories = ListProperty()

    def on_gps(self, provider, eventname, *args):
        if provider is not self.provider:
            return
        print 'on_gps()', provider, eventname, args
        if eventname == 'provider-disabled':
            self.gps_values[1] = args[0]
            self.trigger_gps_update_values()

        elif eventname == 'location':
            location = args[0]
            self.gps_values[2:] = [location.getLatitude(),
                    location.getLongitude()]
            self.trigger_gps_update_values()

    def gps_update_values(self, *args):
        self.root.maincontent.clear_widgets()
        content = self.root.maincontent
        if not self.root.maininit:
            for x in xrange(4):
                content.add_widget(Label())
        values = self.gps_values
        content.children[0].text = 'Last status: {}'.format(values[0])
        content.children[1].text = 'Provider disabled: {}'.format(values[1])
        content.children[2].text = 'Latitude: {}'.format(values[2])
        content.children[3].text = 'Longitude: {}'.format(values[3])

    def on_sensor(self, provider, eventname, *args):
        if provider is not self.provider:
            return
        if eventname == 'accuracy-changed':
            sensor, accuracy = args[:2]

        elif eventname == 'sensor-changed':
            event = args[0]
            self.sensor_values = event.values
            self.trigger_sensor_update_values()

    def sensor_update_values(self, *args):
        values = self.sensor_values
        if not self.root.maininit:
            self.sensor_create_ui(values)
        self.sensor_fill_ui(values)

    def sensor_create_ui(self, values):
        self.root.maincontent.clear_widgets()
        for index in xrange(len(values)):
            self.root.maincontent.add_widget(NumberSlider())
        self.root.maininit = True

    def sensor_fill_ui(self, values):
        for index, value in enumerate(values):
            self.root.maincontent.children[index].value = value

    def error(self, msg):
        self.root.maininit = False
        self.root.maincontent.clear_widgets()
        lbl = Label(text=msg, text_size=('100sp', None))
        self.root.maincontent.add_widget(lbl)

    def select_category(self, button):
        if self.provider:
            self.provider.stop()
            self.provider = None

        category, subcategory = button.text.split('-', 1)
        if category == 'sensor':
            try:
                self.provider = SensorListener(subcategory, self.on_sensor)
            except SensorNotFound:
                self.error('Sensor {} not available on this device'.format(
                    subcategory))
                return
        else:
            self.provider = GpsListener(self.on_gps)

        self.root.maininit = False
        self.root.maincontent.clear_widgets()
        self.root.maincontent.add_widget(
                Label(text='Waiting informations from the sensor'))
        self.provider.start()

        # just for a better "ui"
        button.state = 'down'

    def on_stop(self):
        if self.provider:
            self.provider.stop()
        super(AndroidDemoApp, self).on_stop()

    def on_pause(self):
        if self.provider:
            self.provider.stop()
        return True

    def on_resume(self):
        if self.provider:
            self.provider.start()

    def build(self):
        self.provider = None
        self.sensors_values = []
        self.gps_values = ['', '', 0, 0]
        self.trigger_sensor_update_values = \
                Clock.create_trigger(self.sensor_update_values, 0)
        self.trigger_gps_update_values = \
                Clock.create_trigger(self.gps_update_values, 0)

        # search categories
        self.categories = ['gps-location']
        for key in sensortypes:
            self.categories.append('sensor-{}'.format(key))

        # create main ui
        root = MainUI()

        # fill the dropdown with all the categories
        for cat in self.categories:
            btn = ToggleButton(text=cat, size_hint_y=None, height='44sp',
            group='sensors')
            btn.bind(on_release=self.select_category)
            root.dropdown.add_widget(btn)

        return root


if __name__ == '__main__':
    AndroidDemoApp().run()
