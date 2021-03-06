"""Controller for interacting with a labjack"""

from julesTk.controller.poller import Poller
from pyLabJackView import PyLabJackViewException
from pyLabJackView.connection.labjack import LabJackConnection
from pyLabJackView.model.labjack import LabJackModel
from pyLabJackView.view.labjack import LabJackView
import numpy as np

__author__ = "Joeri Jongbloets <joeri@jongbloets.net>"


class LabJackController(Poller):
    """A controller for """

    def __init__(self, app, view=None, model=None, connection=None):
        if connection is None:
            connection = LabJackConnection()
        self._connection = connection
        if model is None:
            model = LabJackModel(self.connection)
        super(LabJackController, self).__init__(app, view=view, model=model)
        self._plots = {}

    @property
    def view(self):
        """Returns the view managed by this controller

        :rtype: pyLabJackView.view.labjack.LabJackView
        """
        return super(LabJackController, self).view

    @property
    def connection(self):
        """

        :rtype: pyLabJackView.connection.labjack.LabJackConnection
        """
        return self._connection

    def _prepare(self, view=None):
        if view is None:
            view = self._view
        if view is None:
            self._view = LabJackView(self.view, self)
        self.view.prepare()
        return self

    def start(self):
        self.view.show()

    def update(self, observable):
        if isinstance(observable, LabJackModel):
            pass
            #self.update_plot()

    def update_resolution(self, resolution):
        self.model.resolution = resolution
        for ain in self.model.get_channels():
            self.model.get_channel(ain).resolution = resolution
        self.view.set_status_text("New resolution index: {}".format(resolution))

    def update_gain(self, gain):
        self.model.gain = gain
        for ain in self.model.get_channels():
            self.model.get_channel(ain).gain = gain
        self.view.set_status_text("New gain index: {}".format(gain))

    def toggle_ain(self, ain, v):
        v = bool(v)
        if v and not self.model.has_channel(ain):
                self.model.add_channel(ain)
        if self.model.has_channel(ain):
            self.model.get_channel(ain).is_active = v

    def toggle_dio(self, dio, v):
        self.connection.set_do_state(dio, state=1 if v else 0)

    def start_update(self):
        result = self.connection.is_connected()
        if not result:
            result = self.connection.connect()
            self.view.set_status_text("Connected!")
        if result:
            self.set_polling(True)
            self.run()
            result = True
        else:
            self.view.set_status_text("Unable to connect")
        return result

    def stop_update(self):
        self.set_polling(False)
        self.view.set_status_text("Paused")
        # then disconnect
        result = not self.connection.is_connected()
        if not result:
            if self.connection.disconnect():
                self.view.set_status_text("Disconnected!")
                result = True
            else:
                self.view.set_status_text("Unable to disconnect")
        return result

    def execute(self):
        self.model.update()
        self.update_plot()
        self.view.set_status_text("Running every {:3} seconds".format(self.interval))

    def update_plot(self):
        xlim, ylim = [None, None], [None, None]
        for ain in self.model.get_channels():
            model = self.model.get_channel(ain)
            if model.is_active:
                # get latest data
                data = model.data[-1]
                t_point = data.get("time")
                if t_point is not None:
                    y = data.get("value", 0.0)
                    lxlim, lylim = self.view.plot.update_line(ain, t_point, y)
                    xlim = self.update_limits(xlim, lxlim)
                    ylim = self.update_limits(ylim, lylim)
        self.view.plot.add_legend()
        # update limits
        xlim[0] = xlim[0] if xlim[0] is not None else -0.1
        xlim[1] = xlim[1] if xlim[1] is not None else 0.1
        self.view.plot.axes.set_xlim((xlim[0]*0.9, xlim[1]*1.1))
        ylim[0] = ylim[0] if ylim[0] is not None else -0.1
        ylim[1] = ylim[1] if ylim[1] is not None else 0.1
        self.view.plot.axes.set_ylim((ylim[0]*0.9, ylim[1]*1.1))
        self.view.plot.draw()

    def update_limits(self, before, after):
        """selects the minimum by position"""
        result = before[:]
        if before[0] is None or before[0] >= after[0]:
            result[0] = after[0]
        if before[1] is None or before[1] <= after[1]:
            result[1] = after[1]
        return result

    def reset_plot(self):
        for ain in self.model.get_channels():
            self.model.get_channel(ain).reset()
        self.view.plot.clear()

    def hide(self):
        self.stop_update()

    def stop(self):
        self.stop_update()
        if self.connection.is_connected():
            self.connection.disconnect()


class LabJackControllerException(PyLabJackViewException):

    def __init__(self, msg):
        super(LabJackControllerException, self).__init__(msg)
