from elfview import config
from .pad import Pad


class Window:
    def __init__(self, name: str, app: 'App', pads: list[Pad]):
        self.name = name
        self.app = app
        self.pads = pads
        self.current_pad = 0

    def get_current_pad(self) -> Pad:
        return self.pads[self.current_pad]

    def get_pad(self, name: str) -> Pad | None:
        for pad in self.pads:
            if name == pad.NAME:
                return pad
        return None

    def process_input(self, ch):
        for i in range(len(self.pads)):
            self.pads[i].vertical_pos_updated = False

        # TODO: Match-case
        if ch == config.KeyMap.KEY_DOWN.value:
            self.pads[self.current_pad].cursor_y += 1
            self.pads[self.current_pad].vertical_pos_updated = True
        elif ch == config.KeyMap.KEY_UP.value:
            self.pads[self.current_pad].cursor_y -= 1
            self.pads[self.current_pad].vertical_pos_updated = True
        elif ch == config.KeyMap.KEY_RIGHT.value:
            self.current_pad += 1
        elif ch == config.KeyMap.KEY_LEFT.value:
            self.current_pad -= 1
        elif ch == config.KeyMap.KEY_SCROLL_SKIP_UP.value:
            for _ in range(config.PAGE_SCROLL_SKIP_SIZE):
                self.process_input(config.KeyMap.KEY_UP.value)
        elif ch == config.KeyMap.KEY_SCROLL_SKIP_DOWN.value:
            # FIXME: goes beyond content end
            for _ in range(config.PAGE_SCROLL_SKIP_SIZE):
                self.process_input(config.KeyMap.KEY_DOWN.value)

        if self.current_pad < 0:
            self.current_pad = 0

        if self.current_pad >= len(self.pads):
            self.current_pad = len(self.pads) - 1

        self.get_current_pad().process_input(ch)
