#!/usr/bin/env python
import sys, os
import wx

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))
from otii_tcp_client import otii_connection, otii_exception, otii

import example_config as cfg

START_RECORDING_LABEL = "Start timed recording"
STOP_RECORDING_LABEL = "Stop timed recording"

# Connect to Otii
def connect():
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
        project = otii_object.get_active_project()
        if project == None:
            print("No active project")
            sys.exit()
    except otii_exception.Otii_Exception as e:
        print("Error message: " + e.message)

    return otii_object, project

class MainWindow(wx.Frame):
    def __init__(self, otii_object, project):
        wx.Frame.__init__(self, None, title = "Otii - Timed Recording")
        self.otii_object = otii_object
        self.project = project

        # Menu
        tools_menu = wx.Menu()
        timed_recording_item = tools_menu.Append(-1, "&Timed recording", kind = wx.ITEM_CHECK)
        timed_recording_item.Check(True)
        tools_menu.AppendSeparator()
        about_item = tools_menu.Append(wx.ID_ABOUT)
        exit_item = tools_menu.Append(wx.ID_EXIT)
        menu_bar = wx.MenuBar()
        menu_bar.Append(tools_menu, "&Tools")
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        # Setup UI
        self.SetBackgroundColour(wx.Colour(236, 236, 236))
        self.record_button = wx.Button(self, label = START_RECORDING_LABEL)
        self.record_button.Bind(wx.EVT_BUTTON, self.on_record_clicked)
        self.auto_power = wx.CheckBox(self, label = "Auto power");
        self.auto_power.SetValue(False)
        seconds_label = wx.StaticText(self, label = "Seconds:")
        self.seconds = wx.SpinCtrl(self, min = 1, max = 600, initial = 5)

        # Layout UI
        seconds_sizer = wx.BoxSizer(wx.HORIZONTAL)
        seconds_sizer.Add(seconds_label, wx.SizerFlags().Border(wx.RIGHT, 10))
        seconds_sizer.Add(self.seconds, wx.SizerFlags())

        row_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer.Add(self.record_button, wx.SizerFlags().Border(wx.ALL, 10))
        row_sizer.Add(seconds_sizer, wx.SizerFlags().Border(wx.ALL, 10))
        row_sizer.Add(self.auto_power, wx.SizerFlags().Border(wx.ALL, 10))

        self.SetSizer(row_sizer)

        self.started = False
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)

    def on_about(self, event):
        wx.MessageBox("Otii start timed recording",
                      "Otii start timed recording",
                      wx.OK | wx.ICON_INFORMATION)

    def on_exit(self, event):
        self.Close()

    def on_record_clicked(self, event):
        if not self.started:
            self.start()
        else:
            self.stop()
        pass

    def update(self, event):
        time = self.seconds.GetValue()
        time -= 1
        self.seconds.SetValue(time)
        if time == 0:
            self.stop()

    def start(self):
        self.record_button.SetLabel(STOP_RECORDING_LABEL)
        self.initial = self.seconds.GetValue()
        self.timer.Start(1000)
        self.auto_power.Enable(False)
        self.seconds.Enable(False)
        self.started = True
        if self.auto_power.GetValue():
            otii_object.set_all_main(True)
        project.start_recording()

    def stop(self):
        project.stop_recording()
        if self.auto_power.GetValue():
            otii_object.set_all_main(False)
        self.record_button.SetLabel(START_RECORDING_LABEL)
        self.timer.Stop()
        self.seconds.SetValue(self.initial)
        self.seconds.Enable(True)
        self.auto_power.Enable(True)
        self.started = False

otii_object, project = connect()

app = wx.App()
main_window = MainWindow(otii_object, project)
main_window.Show()
app.MainLoop()
