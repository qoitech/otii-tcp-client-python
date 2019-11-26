#!/usr/bin/env python
import sys, os
import wx

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))
from otii_tcp_client import otii_connection, otii_exception, otii

import example_config as cfg

class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title = "Otii")
        # Setup UI
        self.SetBackgroundColour(wx.Colour(38, 47, 56))
        self.device_list = wx.ListBox(self)
        turn_on_button = wx.Button(self, label = "Turn on")
        turn_off_button = wx.Button(self, label = "Turn off")

        # Bind actions
        self.device_list.Bind(wx.EVT_LISTBOX, self.on_device_list_clicked)
        turn_on_button.Bind(wx.EVT_BUTTON, self.on_turn_on_clicked)
        turn_off_button.Bind(wx.EVT_BUTTON, self.on_turn_off_clicked)

        # Layout UI
        device_sizer = wx.BoxSizer(wx.VERTICAL)
        device_sizer.Add(turn_on_button, wx.SizerFlags().Expand())
        device_sizer.Add(turn_off_button, wx.SizerFlags().Expand())

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.device_list, wx.SizerFlags().Expand())
        sizer.Add(device_sizer, wx.SizerFlags().Expand().Border(wx.ALL, 10))
        self.SetSizer(sizer)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(1000)

    def update(self, event):
        if self.active_device:
            voltage = self.active_device.get_value("mv")
            print("Voltage: {0}".format(voltage))

    def add_devices(self, devices):
        self.devices = devices
        device_names = [device.name for device in self.devices]
        self.device_list.InsertItems(device_names, 0)

        if len(self.devices) > 0:
            self.device_list.SetSelection(0)
            self.on_device_list_clicked(None)

    def on_turn_on_clicked(self, event):
        self.active_device.set_main(True)

    def on_turn_off_clicked(self, event):
        self.active_device.set_main(False)

    def on_device_list_clicked(self, event):
        self.active_device = self.devices[self.device_list.GetSelection()]

# Connect to Otii
connection = otii_connection.OtiiConnection(cfg.HOST["IP"], cfg.HOST["PORT"])
connect_response = connection.connect_to_server()
if connect_response["type"] == "error":
    print("Exit! Error code: " + connect_response["errorcode"] + ", Description: " + connect_response["data"]["message"])
    sys.exit()

try:
    otii_object = otii.Otii(connection)
    devices = otii_object.get_devices()
    if len(devices) == 0:
        print("No Arc connected!")
        sys.exit()
except otii_exception.Otii_Exception as e:
    print("Error message: " + e.message)

app = wx.App()
main_window = MainWindow()
main_window.Show()
main_window.add_devices(devices)
app.MainLoop()
