# -*- coding: Utf-8 -*

from .classes import Text

class CountDown(Text):
    def __init__(self, master, seconds: int, *args, **kwargs):
        Text.__init__(self, str(), *args, **kwargs)
        self.__seconds = seconds
        self.__master = master
        self.__callback = None

    def start(self, at_end=None):
        self.show()
        for i in range(self.__seconds):
            self.__master.after(1000 * i, lambda value=self.__seconds - i: self.set_string(value))
        self.__master.after(1000 * self.__seconds, self.__end)
        if callable(at_end):
            self.__callback = at_end
        else:
            self.__callback = None

    def __end(self):
        self.hide()
        if self.__callback is not None:
            self.__callback()