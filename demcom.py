import curses
import ui
import flists
import fsutils
import sys
import traceback

# it should be something like : "code $1 &"
EDITOR_COMMAND: str = "code $1 &"

CANC = lambda op: op + " operation was canceled"
FCR_LBL = "Folder creation"
FCR_MSG = "Enter folder name:"
FCR_MSG_N = FCR_MSG + " %s"
FCR_CANC = CANC(FCR_MSG)

DEL_LBL = "Delete"
DEL_ASK = "Do you really want to delete: \n%s?"
DEL_MSG = "Deleting: %s"
DEL_CANC = CANC(DEL_MSG)

COPY_LBL = "Copy"
COPY_ASK = "Do you really want to copy: \n%s\n to:\n%s?"
COPY_CANC = CANC(COPY_LBL)

MOVE_LBL = "Move"
MOVE_ASK = "Do you really want to move: \n%s?"
MOVE_CANC = CANC(MOVE_LBL)


KEY_TAB = 9
KEY_ENTER = 10
KEY_SPACE = 32
KEY_DEL = 330
KEY_INS = 331
KEY_PAGE_DOWN = 338
KEY_PAGE_UP = 339
KEY_F4 = 268
KEY_F5 = 269
KEY_F6 = 270
KEY_F7 = 271
KEY_F8 = 272
KEY_F10 = 274


def try_op(stdscr, op, message):
    result = message
    try:
        op()
    except:
        e = sys.exc_info()[0]
        result = "Error with operation: [" + message + "]"
        ui.info_box_alert(stdscr, result, str(e))
    return result


def show_main_screen(stdscr):
    k = 0
    double_list = flists.DoubleList("/", fsutils.get_working_folder())
    statusbarstr = "Started!"

    while (k != KEY_F10):
        height, width = stdscr.getmaxyx()
        file_list_height = curses.LINES - 9
        active_path = double_list.get_active().get_path()
        active_selected = double_list.get_active().get_selected_file().file_name
        active_path_selected = fsutils.file_plus_folder(active_path, active_selected)
        active_marked = double_list.get_active().get_marked()
        active_is_marked = len(active_marked) > 0
        active_marked_info = "[" + str(len(active_marked)) + " marked]"
        inactive_path = double_list.get_inactive().get_path()

        def delete():
            if active_is_marked:
                return str([fsutils.remove_folder(fsutils.file_plus_folder(active_path, f.file_name)) for f in active_marked])
            else:
                return fsutils.remove_folder(active_path_selected)

        def copy_move(fun):
            if active_is_marked:
                fun(active_path, [f.file_name for f in active_marked], inactive_path)
            else:
                fun(active_path, [active_selected], inactive_path)          

        def copy():
            copy_move(fsutils.copy_files)

        def move():
            copy_move(fsutils.move_files)

        op_lambda = None
        op_msg = None

        if k == curses.KEY_DOWN:
            double_list.get_active().down(file_list_height)
        elif k == curses.KEY_UP:
            double_list.get_active().up(file_list_height)
        elif k == KEY_ENTER:  # ENTER
            fun = double_list.get_active().folder_down
            msg = "Entering folder: " + double_list.get_active().get_selected_file().file_name
            statusbarstr = try_op(stdscr, fun, msg)
        elif k == KEY_PAGE_DOWN:  # PG DOWN
            double_list.get_active().page_down(file_list_height)
        elif k == KEY_PAGE_UP:  # PG UP
            double_list.get_active().page_up(file_list_height)
        elif k == KEY_TAB:  # TAB
            double_list.toggle()
        elif k == KEY_F7:  # F7
            new_folder = ui.input_box(stdscr, FCR_LBL, FCR_MSG)
            if len(new_folder) > 0:
                op_lambda = lambda: fsutils.create_folder(active_path, new_folder)
                op_msg = FCR_MSG_N % new_folder
            else:
                statusbarstr = FCR_CANC
        elif k == KEY_F8 or k == KEY_DEL:  # F8 or DEL
            file_name = active_path_selected if not active_is_marked else active_marked_info
            confirm_result = ui.confirm_box_alert(stdscr, DEL_LBL, DEL_ASK % file_name)
            if confirm_result == "OK":
                op_lambda = lambda: delete()
                op_msg = DEL_MSG % file_name
            else:
                statusbarstr = DEL_CANC
        elif k == KEY_SPACE or k == KEY_INS:  # SPACE or INS
            marked = double_list.get_active().mark()
            statusbarstr = "[" + str(len(marked)) + " marked]"
            double_list.get_active().down(file_list_height)
        elif k == KEY_F5:  # F5
            _from = active_path_selected if not active_is_marked else active_marked_info
            copy_info = COPY_ASK % (_from, inactive_path)
            confirm_result = ui.confirm_box_norm(stdscr, COPY_LBL, copy_info)
            if confirm_result == "OK":
                statusbarstr = str(ui.task_run_box(stdscr, COPY_LBL, copy_info, copy))
                double_list.refresh()
            else:
                statusbarstr = COPY_CANC
        elif k == KEY_F6:  # F6
            _from = active_path_selected if not active_is_marked else active_marked_info
            copy_info = _from + "\n" + "To: \n   " + inactive_path
            confirm_result = ui.confirm_box_norm(stdscr, MOVE_LBL,  MOVE_ASK % copy_info)
            if confirm_result == "OK":
                statusbarstr = str(ui.task_run_box(stdscr, MOVE_LBL, copy_info, move))
                double_list.refresh()
            else:
                statusbarstr = MOVE_CANC
        elif k == KEY_F4:
            if EDITOR_COMMAND is None:
                ui.info_box_alert(stdscr, "EDITOR_COMMAND not defined", "You should define variable EDITOR_COMMAND in main script.")
            else:
                fsutils.run_shell_command(EDITOR_COMMAND.replace("$1", active_path_selected))
        elif k == 282:  # Shift + F6
            new_name = ui.input_box(stdscr, "Rename", "Enter new name:")
            if new_name is not None and len(new_name) > 0:
                fsutils.rename(active_path, active_selected, new_name)
                statusbarstr = active_selected + " renamed to " + new_name
                double_list.refresh()

        if op_lambda is not None:
            statusbarstr = try_op(stdscr, op_lambda, op_msg)
            double_list.refresh()

        left_is_active = double_list.left_is_active()
        left_path = double_list.get_left().get_path()
        right_path = double_list.get_right().get_path()
        left_files, left_selected, left_marked = double_list.get_left().get_files(file_list_height)
        right_files, right_selected, right_marked = double_list.get_right().get_files(file_list_height)

        ui.file_box(stdscr, left_path, left_is_active, True, left_files, left_selected, left_marked)
        ui.file_box(stdscr, right_path, not left_is_active, False, right_files, right_selected, right_marked)

        ui.status_bar(stdscr, statusbarstr)

        # Refresh the screen
        stdscr.refresh()

        k = stdscr.getch()


def main():
    try:
        curses.initscr()

        curses.start_color()
        curses.curs_set(0)
        curses.use_default_colors()

        curses.wrapper(show_main_screen)

        curses.endwin()
    except:
        e = traceback.format_exc()
        curses.endwin()
        print(e)
        
if __name__ == '__main__':
    # test()
    main()
