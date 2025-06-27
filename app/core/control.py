from __future__ import annotations

from app.core.tools import _csi


class Control:
    cursor_up = staticmethod(lambda n=1: _csi('A', n))
    cursor_down = staticmethod(lambda n=1: _csi('B', n))
    cursor_forward = staticmethod(lambda n=1: _csi('C', n))
    cursor_back = staticmethod(lambda n=1: _csi('D', n))
    cursor_next_line = staticmethod(lambda n=1: _csi('E', n))
    cursor_previous_line = staticmethod(lambda n=1: _csi('F', n))
    cursor_horizontal_absolute = staticmethod(lambda n=1: _csi('G', n))
    cursor_position = staticmethod(lambda x, y: _csi('H', x, y))
    erase_data = staticmethod(lambda n=0: _csi('J', n))
    erase_line = staticmethod(lambda n=0: _csi('K', n))
    scroll_up = staticmethod(lambda n=1: _csi('S', n))
    scroll_down = staticmethod(lambda n=1: _csi('T', n))
    save_cursor_position = staticmethod(lambda: _csi('s'))
    restore_cursor_position = staticmethod(lambda: _csi('u'))
