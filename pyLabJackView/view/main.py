"""Defines the mainView"""

from . import *


class MainWindow(Window):
    """"""

    def __init__(self, parent, controller):
        super(MainWindow, self).__init__(parent, controller)
        self._current_view = None

    def setup(self):
        self.pack(side="top", fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # add view
        v = MainView(self, self.controller)
        self.add_view("main", v)
        v.setup()

    def show(self):
        self.show_view()

    def show_view(self, name="main"):
        super(MainWindow, self).show_view(name)


class MainView(View):

    def __init__(self, parent, window):
        super(MainView, self).__init__(parent, window)

    @property
    def controller(self):
        """

        :rtype: pyLabJackView.controller.main.MainController
        """
        return super(MainView, self).controller

    def setup(self):
        self.grid(row=0, column=0, sticky="nsew")
        # label
        label = ttk.Label(self, text="This is the start page", font=self.FONT_LARGE)
        label.pack(pady=10, padx=10)
        # button for plot
        button = ttk.Button(self, text="Show plot", command=self.show_plot)
        button.pack()

    def show_plot(self):
        self.controller.goto_plot()