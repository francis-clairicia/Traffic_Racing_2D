# -*- coding: Utf-8 -*

from .window import Window, RESOURCES
from .text import Text
from .progress import ProgressBar
from .colors import WHITE, BLACK

class Loading(Window):
    def __init__(self, text="Loading...", font=(None, 50), bg=BLACK, fg=WHITE):
        Window.__init__(self, bg_color=bg)
        self.show_fps_in_this_window(False)
        self.__text = Text(message=text, font=font, color=fg)
        self.__progress = ProgressBar(0.15 * self.width, 0.05 * self.height, color=bg, scale_color=fg, outline=2, outline_color=fg)
        self.__thread_loading = None
        self.__loading = False

    @property
    def text(self) -> Text:
        return self.__text

    @property
    def progress(self) -> ProgressBar:
        return self.__progress

    def place_objects(self) -> None:
        self.text.move(centerx=self.centerx, bottom=self.centery - 10)
        self.progress.move(centerx=self.centerx, top=self.centery + 10)

    def on_start_loop(self) -> None:
        nb_resources_to_load = len(RESOURCES)
        if nb_resources_to_load == 0:
            self.stop()
        else:
            self.objects.set_priority(self.text, self.objects.end)
            self.objects.set_priority(self.progress, self.objects.end)
            self.progress.end = nb_resources_to_load
            self.__thread_loading = RESOURCES.threaded_load()
            self.__loading = True
    
    def on_quit(self) -> None:
        if self.__thread_loading is not None:
            self.__thread_loading.join()

    def update(self) -> None:
        if not self.__loading:
            return
        self.progress.value = RESOURCES.loaded
        if self.progress.percent == 1:
            self.after(100, self.stop)
            self.__loading = False
