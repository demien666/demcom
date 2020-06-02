import curses
import time
import threading
import random

from typing import List
from fsutils import FileInfo

BOTTOM_BUTTONS = {
    "F1": "Help",
    "F4": "Edit",
    "F5": "Copy",
    "F6": "RenMov",
    "F7": "Mkdir",
    "F8": "Delete",
    "F10": "Quit"
}

BOX_NORM_TEXT_COLOR = curses.COLOR_BLACK
BOX_NORM_BG_COLOR = 7
BOX_NORM_CP = 10

BOX_SEL_TEXT_COLOR = curses.COLOR_BLACK
BOX_SEL_BG_COLOR = curses.COLOR_CYAN
BOX_SEL_CP = 11

BOX_ALERT_TEXT_COLOR = curses.COLOR_WHITE
BOX_ALERT_BG_COLOR = curses.COLOR_RED
BOX_ALERT_CP = 12

STBAR_TEXT_COLOR = curses.COLOR_WHITE
STBAR_BG_COLOR = curses.COLOR_BLACK
STBAR_CP = 13


PANEL_FILE_TEXT_COLOR = 6
PANEL_FILE_CP = 20
PANEL_FOLDER_TEXT_COLOR = curses.COLOR_WHITE
PANEL_FOLDER_CP = 21
PANEL_SELECTED_TEXT_COLOR = curses.COLOR_BLACK
PANEL_SELECTED_CP = 22
PANEL_MARKED_TEXT_COLOR = 11
PANEL_MARKED_CP = 23
PANEL_MARKEDSELECTED_CP = 24
PANEL_BG_COLOR = curses.COLOR_BLUE
PANEL_SBG_COLOR = curses.COLOR_CYAN


# 1 - red
# 2 - green
# 3 - orange
# 4 - blue
# 5 - pink
# 6 - cyan
# 7 - light gray
# 8 - gark gray
# 9 - pink / red
# 10 - cyan / green
# 11 - yellow
# 12 - purple

class TaskRunner(object):
    def submit_task(self, task):
        self.__is_done = False
        self.__task = task
        self.__result = None
        self.__err_code = None
        thread = threading.Thread(target=self.run_task, args=())
        thread.start()

    def run_task(self):
        try:
            self.__result = self.__task()
            self.__err_code = 0
        except Exception as inst:
            self.__err_code = 1
            self.__result = inst
        self.__is_done = True

    def is_done(self):
        return self.__is_done

    def get_result(self):
        return self.__result

    def get_err_code(self):
        return self.__err_code


task_runner = TaskRunner()


def dummy_task():
    time.sleep(5)


def dummy_failing_task():
    dummy_task()
    raise Exception("none", "fail task exception")


def init_box_cp():
    curses.init_pair(BOX_NORM_CP, BOX_NORM_TEXT_COLOR, BOX_NORM_BG_COLOR)
    curses.init_pair(BOX_SEL_CP, BOX_SEL_TEXT_COLOR, BOX_SEL_BG_COLOR)
    curses.init_pair(BOX_ALERT_CP, BOX_ALERT_TEXT_COLOR, BOX_ALERT_BG_COLOR)
    curses.init_pair(STBAR_CP, STBAR_TEXT_COLOR, STBAR_BG_COLOR)

    curses.init_pair(PANEL_FILE_CP, PANEL_FILE_TEXT_COLOR, PANEL_BG_COLOR)
    curses.init_pair(PANEL_FOLDER_CP, PANEL_FOLDER_TEXT_COLOR, PANEL_BG_COLOR)
    curses.init_pair(PANEL_SELECTED_CP, PANEL_SELECTED_TEXT_COLOR, PANEL_SBG_COLOR)
    curses.init_pair(PANEL_MARKED_CP, PANEL_MARKED_TEXT_COLOR, PANEL_BG_COLOR)
    curses.init_pair(PANEL_MARKEDSELECTED_CP, PANEL_MARKED_TEXT_COLOR, PANEL_SBG_COLOR)


def rectangle(win, begin_y, begin_x, height, width):
    win.vline(begin_y,    begin_x,
              curses.ACS_VLINE, height, curses.A_BOLD)
    win.hline(begin_y,        begin_x,
              curses.ACS_HLINE, width, curses.A_BOLD)
    win.hline(height+begin_y, begin_x,
              curses.ACS_HLINE, width, curses.A_BOLD)
    win.vline(begin_y,    begin_x+width,
              curses.ACS_VLINE, height, curses.A_BOLD)
    win.addch(begin_y,        begin_x,
              curses.ACS_ULCORNER,  curses.A_BOLD)
    win.addch(begin_y,        begin_x+width,
              curses.ACS_URCORNER,  curses.A_BOLD)
    win.addch(height+begin_y, begin_x,
              curses.ACS_LLCORNER,  curses.A_BOLD)
    win.addch(begin_y+height, begin_x+width,
              curses.ACS_LRCORNER,  curses.A_BOLD)
    win.refresh()


def message_box(title, message, cp_id, text_attr):
    init_box_cp()

    maxy, maxx = curses.LINES, curses.COLS
    nlines = message.count('\n') + 7
    ncols = int(maxx/2)
    begin_y = int((maxy/2) - nlines/2)
    begin_x = int(maxx/2 - ncols/2)

    win = curses.newwin(nlines, ncols, begin_y, begin_x)
    win.bkgd(' ', curses.color_pair(cp_id))
    rectangle(win, 1, 1, nlines - 3, ncols - 3)
    y, x = win.getmaxyx()

    if title:
        title = " " + title + " "
        win.addstr(1, int(x / 2 - len(title) / 2), title, text_attr)
    for (i, msg) in enumerate(message.split('\n')):
        win.addstr(i+2, 3, msg, text_attr)

    win.keypad(1)
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()

    return win


def left_right_key_event_handler(win, max, focus, enterKey):
    win.refresh()
    key = win.getch()
    if key == curses.KEY_LEFT and focus != 0:
        focus -= 1
    elif key == curses.KEY_RIGHT and focus != max-1:
        focus += 1
    elif key == ord('\n'):
        enterKey = True
    return focus, enterKey


def confirm_box(title, message, cp_norm_id, cp_sel_id, text_attr, buttons):
    win = message_box(title, message, cp_norm_id, text_attr)
    y, x = win.getmaxyx()
    focus = 0
    enterKey = False
    while not enterKey:
        for (i, button) in enumerate(buttons):
            attr = curses.color_pair(cp_sel_id) if focus == i else text_attr
            pos_x = int(x / (len(buttons) + 1)) * (i + 1)
            caption = "[< " + button + " >]"
            win.addstr(y - 3, pos_x - int(len(caption) / 2), caption, attr)

        (focus, enterKey) = left_right_key_event_handler(
            win, len(buttons), focus, enterKey)
    return buttons[focus]


def confirm_box_alert(title, message):
    return confirm_box(title, message, BOX_ALERT_CP, BOX_NORM_CP, curses.A_BOLD, ["OK", "Cancel"])


def confirm_box_norm(title, message):
    return confirm_box(title, message, BOX_NORM_CP, BOX_SEL_CP, curses.A_NORMAL, ["OK", "Cancel"])


def info_box_alert(title, message):
    return confirm_box(title, message, BOX_ALERT_CP, BOX_NORM_CP, curses.A_BOLD, ["OK"])


def info_box_norm(title, message):
    return confirm_box(title, message, BOX_NORM_CP, BOX_SEL_CP, curses.A_NORMAL, ["OK"])


def input_box(title, message):
    text_attr = curses.A_NORMAL
    win = message_box(title, message, BOX_NORM_CP, text_attr)
    curses.curs_set(1)
    win.attron(text_attr)
    y, x = win.getmaxyx()
    top = y - 3
    left = 3
    win.addstr(top, left, " "*(x-6), curses.color_pair(BOX_SEL_CP))
    win.addstr(top, left - 1, " ", text_attr)
    input = ""
    enterKey = False
    while not enterKey:
        key = win.getch()
        if key == ord('\n'):
            enterKey = True
        elif key == 263:  # curses.KEY_BACKSPACE
            if len(input) > 0:
                input = input[:-1]
                win.addstr(top, left + len(input), " ", text_attr | curses.color_pair(BOX_SEL_CP))
        elif key == 27:
            input = ""
            enterKey = True
        else:
            input = input + chr(key)
        win.addstr(top, left, input, text_attr | curses.color_pair(BOX_SEL_CP))
    return input


def task_run_box(title, message, task):
    text_attr = curses.A_NORMAL
    win = message_box(title, message, BOX_NORM_CP, text_attr)
    y, x = win.getmaxyx()
    syms = ["|", "/", "-", "\\"]
    task_runner.submit_task(task)
    syms_pos = 0
    while not task_runner.is_done():
        sym = syms[syms_pos]
        syms_pos += 1
        syms_pos = 0 if syms_pos == len(syms) - 1 else syms_pos
        win.addstr(y-3, int(x / 2), " " + sym + " ")
        win.refresh()
        time.sleep(0.3)
    task_result = task_runner.get_result()
    if task_runner.get_err_code() == 1:
        info_box_alert("Error", "Task execution was failed. \n " + str(task_result))
    return task_result


def file_box(title: str, is_active: bool, is_left: bool, files: List[FileInfo], selectedFile: FileInfo, markedFiles: List[FileInfo]):
    init_box_cp()
    cp_id = PANEL_FOLDER_CP
    text_attr = curses.A_BOLD

    # maxy, maxx = curses.LINES, curses.COLS
    nlines = curses.LINES - 5
    ncols = int((curses.COLS - 1)/2)

    if len(title) > ncols - 10:
        title = "..." + title[10:]

    # win = curses.newwin(nlines, ncols, 2, 2)
    left = 1 if is_left else ncols + 1
    win = curses.newwin(nlines, ncols, 1, left)
    win.bkgd(' ', curses.color_pair(cp_id))
    rectangle(win, 1, 1, nlines - 3, ncols - 3)
    y, x = win.getmaxyx()

    if title:
        title = " " + title + " "
        win.addstr(1, int(x / 2 - len(title) / 2), title, text_attr)

    if files is not None and len(files) > 0:
        pos = 1
        for file in files:
            pos = pos + 1
            color_pair = None
            is_marked = markedFiles is not None and file in markedFiles
            is_selected = selectedFile is not None and file == selectedFile and is_active
            if is_marked and is_selected:
                color_pair = PANEL_MARKEDSELECTED_CP
            elif is_marked:
                color_pair = PANEL_MARKED_CP
            elif is_selected:
                color_pair = PANEL_SELECTED_CP
            elif file.is_file:
                color_pair = PANEL_FILE_CP
            else:
                color_pair = PANEL_FOLDER_CP

            win.addstr(pos, 2, file.format_file(x), text_attr | curses.color_pair(color_pair))

    win.keypad(1)
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    win.refresh()


def status_bar(stdscr, message):
    init_box_cp()
    nlines = curses.LINES
    ncols = curses.COLS
    stdscr.addstr(nlines-2, 0, message, curses.color_pair(STBAR_CP))
    button_len = int(ncols / len(BOTTOM_BUTTONS))

    pos = 0
    for key, label in BOTTOM_BUTTONS.items():
        stdscr.addstr(nlines-1, pos, " " + key, curses.color_pair(STBAR_CP))
        l = label
        if len(label) > button_len - 3:
            l = l[0:button_len - 3]
        else:
            l = l + " "*(button_len - 3 - len(l))
        stdscr.addstr(nlines-1, pos + len(key) + 1, l, curses.color_pair(BOX_SEL_CP))
        pos = pos + len(key) + len(l)


def get_file(id, is_file):
    name = "file " if is_file else "Folder "
    return FileInfo(name + str(id), is_file, str(random.randint(1, 1000000)), "2012-11-12 12:12:32")


def get_files(cnt, is_file):
    return [get_file(i, is_file) for i in range(0, cnt)]


files = get_files(10, False) + get_files(5, True)


def test():
    try:
        stdscr = curses.initscr()

        curses.start_color()
        curses.curs_set(0)
        curses.use_default_colors()
        #r = confirm_box_alert("Hello", "World! \n Is \n a \n perfect \n place \n to \n live")
        #r = confirm_box_norm("Hello", "World! \n Is \n a \n perfect \n place \n to \n live")
        #r = input_box(
        #    "Hello", "World! \n Is \n a \n perfect \n place \n to \n live")
        # r = task_run_box("Hello", "World! \n Is \n a \n perfect \n place \n to \n live", dummy_task)
        #r = task_run_box("Hello", "World! \n Is \n a \n perfect \n place \n to \n live", dummy_failing_task)
        r = file_box("Hello", False, True, files, files[3], files[6:10])
        r = file_box("Hello", True, False, files, files[3], files[6:10])

        curses.endwin()
        print(r)
    except:
        curses.endwin()


if __name__ == '__main__':
    test()
