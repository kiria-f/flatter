from enum import StrEnum

from app.core.widgets import DataBox


class Border(StrEnum):
    BAR_H = '─'  # '\u2500'
    BAR_V = '│'  # '\u2502'
    CORNER_BR = '┌'  # '\u250c'
    CORNER_BL = '┐'  # '\u2510'
    CORNER_TR = '└'  # '\u2514'
    CORNER_TL = '┘'  # '\u2518'
    CORNER_VR = '├'  # '\u251c'
    CORNER_VL = '┤'  # '\u2524'
    CORNER_HB = '┬'  # '\u252c'
    CORNER_HT = '┴'  # '\u2534'
    ARC_BR = '╭'  # '\u256d'
    ARC_BL = '╮'  # '\u256e'
    ARC_TL = '╯'  # '\u256f'
    ARC_TR = '╰'  # '\u2570'


def make_frame(self, width, height):
    frame = []
    frame.append(Border.ARC_BR + Border.BAR_H * (width - 2) + Border.ARC_BL)
    for _ in range(height - 2):
        frame.append(Border.BAR_V + ' ' * (width - 2) + Border.BAR_V)
    frame.append(Border.ARC_TR + Border.BAR_H * (width - 2) + Border.ARC_TL)
    return frame


frame = DataBox(
    renderer=make_frame,
    id='frame',
    depends_on=['width', 'height'],
)


frame = SimpleFrameControl()
frame_window = Window(content=frame)
