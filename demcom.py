import curses
import ui
import flists
import fsutils
import sys


def try_op(op, message):
    result = message
    try:
        op()
    except:
        e = sys.exc_info()[0]
        result = "Error with operation: [" + message + "]"
        ui.info_box_alert(result, str(e))
    return result


def show_main_screen(stdscr):
    k = 0
    double_list = flists.DoubleList("/home/dmitry/Develop", "/")
    statusbarstr = "Started!"

    while (k != ord('q')):
        file_list_height = curses.LINES - 9

        if k == curses.KEY_DOWN:
            double_list.get_active().down(file_list_height)
        elif k == curses.KEY_UP:
            double_list.get_active().up(file_list_height)
        elif k == 10:  # ENTER
            fun = double_list.get_active().folder_down
            msg = "Entering folder: " + double_list.get_active().get_selected_file().file_name
            statusbarstr = try_op(fun, msg)
        elif k == 338:  # PG DOWN
            double_list.get_active().page_down(file_list_height)
        elif k == 339:  # PG UP
            double_list.get_active().page_up(file_list_height)
        elif k == 9:  # TAB
            double_list.toggle()
        elif k == 271:  # F7
            new_folder = ui.input_box("Folder creation", "Enter folder name:")
            if len(new_folder) > 0:
                new_folder_path = fsutils.file_plus_folder(double_list.get_current_path(), new_folder)
                fun = lambda: fsutils.create_folder(new_folder_path)
                msg = "Folder creation: " + new_folder
                statusbarstr = try_op(fun, msg)
                double_list.refresh()
            else:
                statusbarstr = "Folder creation was canceled"
        elif k == 272 or k == 330:  # F8 or DEL
            marked = double_list.get_active().get_marked()
            # selected_name = double_list.get_active().get_selected_file().file_name
            selected_name = double_list.get_current_path_with_selected()
            is_marked = (len(marked) > 0)
            file_name = selected_name if not is_marked else str(len(marked)) + " selected files"
            confirm_result = ui.confirm_box_alert("Delete", "Do you really want to delete: \n" + file_name + " ?")
            if confirm_result == "OK":                
                fun_marked = lambda: str([fsutils.remove_folder(fsutils.file_plus_folder(double_list.get_current_path(), f.file_name)) for f in marked])
                fun_selected = lambda: fsutils.remove_folder(double_list.get_current_path_with_selected())
                fun = fun_marked if is_marked else fun_selected
                msg = "Delete: " + file_name
                statusbarstr = try_op(fun, msg)
                double_list.refresh()
            else:
                statusbarstr = "Delete operation was canceled"
        elif k == 32 or k == 331:  # SPACE or INS
            marked = double_list.get_active().mark()
            statusbarstr = str(len(marked)) + " file(files) are marked"
            double_list.get_active().down(file_list_height)

        left_is_active = double_list.left_is_active()
        left_path = double_list.get_left().get_path()
        right_path = double_list.get_right().get_path()
        left_files, left_selected, left_marked = double_list.get_left().get_files(file_list_height)
        right_files, right_selected, right_marked = double_list.get_right().get_files(file_list_height)

        ui.file_box(left_path, left_is_active, True, left_files, left_selected, left_marked)
        ui.file_box(right_path, not left_is_active, False, right_files, right_selected, right_marked)

        ui.status_bar(stdscr, statusbarstr)

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
        e = sys.exc_info()[0]
        curses.endwin()
        print(e)
        
if __name__ == '__main__':
    # test()
    main()
