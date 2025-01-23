from elfview.util.curses import Position


class Pad:
    # TODO: Pass layout within window
    def __init__(self, y: int = 0, x: int = 0):
        # TODO: cursor = Position, offset = Position, scroll = Position
        self.dimensions = Position(y, x)
        self.cursor_y = 0
        self.scroll_y = 0
        self.y_offset = 0
        self.vertical_pos_updated = False
        self.max_y_size = self.dimensions.y

    def update_cursor(self, y_pos: int):
        self.cursor_y = y_pos
        if self.cursor_y >= self.dimensions.y - self.y_offset:
            self.scroll_y = self.cursor_y - 1
            self.cursor_y = 1

    def get_abs_y_offset(self):
        return self.cursor_y + self.scroll_y

    def calculate_dimensions(self, win_dimensions):
        ...

    def refresh(self, pad, win_dimensions):
        ...

    def render(self, win, pad):
        ...

    def process_input(self, ch):
        if self.cursor_y < 0:
            self.cursor_y = 0

        if self.cursor_y >= self.dimensions.y - self.y_offset:
            self.cursor_y -= 1
            self.scroll_y += 1

        if self.cursor_y < 1:
            self.scroll_y -= 1

        if self.scroll_y < 0:
            self.scroll_y = 0

        if self.cursor_y + self.scroll_y > self.max_y_size:
            self.cursor_y = self.max_y_size - self.scroll_y
