from elfview.ui import prompt_bar, alert
from elfview import config


class Finder:
    def __init__(self):
        self.string = ''
        self.should_look = False
        self.occurrence = 0

    def reset(self):
        self.string = ''
        self.occurrence = 0

    def verify(self, s: str) -> bool:
        return (self.string != '') and (self.string in str(s))

    def __get_range(self, pad, collection_size: int):
        if config.SEARCH_WHOLE_BUFFER:
            return range(collection_size)
        else:
            return range(
                max(pad.get_abs_y_offset() - config.SEARCH_REACH, 0),
                min(pad.get_abs_y_offset() + config.SEARCH_REACH, collection_size-1)
            )

    def find(self, pad, collection_size, get_str, x_offset: int = 0):
        if self.occurrence >= collection_size:
            self.occurrence = collection_size - 1

        occurrence = 0
        for i in self.__get_range(pad, collection_size):
            if self.string in str(get_str(i)):
                if occurrence == self.occurrence:
                    pad.update_cursor(i)
                    return
                occurrence += 1

        if config.SEARCH_WHOLE_BUFFER:
            alert(['Can\'t find requested string', 'Press any key to close this'], pad.dimensions, x_offset)

    def find_if_requested(self, pad, collection_size, get_str, x_offset: int = 0):
        if self.should_look and len(self.string):
            self.find(pad, collection_size, get_str, x_offset)
            self.should_look = False

    def process_input(self, pad, ch, x_offset: int = 0):
        if ch == config.KeyMap.KEY_FIND.value:
            self.string = prompt_bar('Find: ', pad.dimensions, x_offset)
            self.occurrence = 0
            self.should_look = True
        elif ch == config.KeyMap.KEY_FIND_NEXT.value and config.SEARCH_USE_NEXT_OCCURRENCE:
            self.occurrence += 1
            self.should_look = True
        elif ch == config.KeyMap.KEY_FIND_PREV.value and config.SEARCH_USE_NEXT_OCCURRENCE:
            self.occurrence -= 1
            self.should_look = True

        if self.occurrence < 0:
            self.occurrence = 0
