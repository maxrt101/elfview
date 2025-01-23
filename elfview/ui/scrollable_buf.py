from elfview.util.curses import Position


class ScrollableBuffer:
    def __init__(self, max_dimensions: Position, offset: Position = Position(0, 0)):
        self.scroll_y = 0
        self.max_dimensions = max_dimensions
        self.offset = offset
        self.lines = list()

    def add_line(self, line: str):
        self.lines.append(line)
        overflow = len(self.lines) - self.max_dimensions.y - self.scroll_y
        if overflow > 0:
            self.scroll_y += overflow

    def render(self, pad):
        y = 0

        for i in range(self.scroll_y, len(self.lines)):
            line = self.lines[i]

            pad.addstr(
                y + self.offset.y,
                self.offset.x,
                line[:min(len(line), self.max_dimensions.x - self.offset.x - 1)]
            )

            y += 1
            if y >= self.max_dimensions.y - self.offset.y - 1:
                break
