from typing import List
from fsutils import FileInfo, list_dir_full, get_short_folder_name, file_plus_folder, get_parent_folder


class FileList():
    def __init__(self, path):
        self.__hist = {}
        self.setup(path)

    def refresh(self):
        self.setup(self.__path)

    def setup(self, path: str):
        self.__path: str = path
        self.__files: List[FileInfo] = list_dir_full(path)
        self.__select_position = 0
        self.__top_position = 0
        if path in self.__hist:
            previous_values = self.__hist[path]
            self.__select_position = previous_values["select_position"]
            self.__top_position = previous_values["top_position"]
        self.__marked = []

    def fix_positions(self, height):
        if self.__select_position <= 0:
            self.__select_position = 0
        if self.__select_position < self.__top_position:
            self.__top_position = self.__select_position

        if self.__select_position >= len(self.__files) - 1:
            self.__select_position = len(self.__files) - 1
        if self.__select_position >= self.__top_position + height:
            self.__top_position = self.__select_position - height + 1
        values = {
            "select_position": self.__select_position,
            "top_position": self.__top_position
        }
        self.__hist[self.__path] = values

    def up(self, height):
        self.__select_position = self.__select_position - 1
        self.fix_positions(height)

    def down(self, height):
        self.__select_position = self.__select_position + 1
        self.fix_positions(height)

    def page_up(self, height):
        self.__select_position = self.__select_position - height
        self.fix_positions(height)

    def page_down(self, height):
        self.__select_position = self.__select_position + height
        self.fix_positions(height)

    def get_files(self, height):
        self.fix_positions(height)
        result = []
        for i in range(self.__top_position, self.__top_position + height):
            if i < len(self.__files):
                result.append(self.__files[i])
        return result, self.__files[self.__select_position], self.__marked

    def get_selected_file(self) -> FileInfo:
        return self.__files[self.__select_position]

    def folder_down(self) -> str:
        selected = self.get_selected_file()
        if selected.file_name == "..":
            new_path = get_parent_folder(self.__path)
        else:
            new_path = file_plus_folder(self.__path, selected.file_name)
        self.setup(new_path)
        return new_path

    def get_hist(self):
        return self.__hist

    def get_path(self):
        return self.__path

    def get_path_with_selected(self) -> str:
        selected = self.get_selected_file()
        return self.__path + "/" + selected.file_name

    def mark(self) -> List[FileInfo]:
        selected = self.get_selected_file()
        if selected.file_name == "..":
            return
        if selected in self.__marked:
            self.__marked.remove(selected)
        else:
            self.__marked.append(selected)
        return self.__marked

    def get_marked(self) -> List[FileInfo]:
        return self.__marked

    def get_current_folder_name(self):
        return get_short_folder_name(self.__path)


class DoubleList():
    def __init__(self, left_path, right_path):
        self.__left_list = FileList(left_path)
        self.__right_list = FileList(right_path)
        self.__active = self.__left_list

    def left_is_active(self):
        return self.__active == self.__left_list

    def toggle(self):
        if self.left_is_active():
            self.__active = self.__right_list
        else:
            self.__active = self.__left_list

    def get_files(self, height):
        l_files, l_selected, l_marked = self.__left_list.get_files(height)
        r_files, r_selected, r_marked = self.__right_list.get_files(height)
        return self.left_is_active(),\
            l_files, l_selected, l_marked,\
            r_files, r_selected, r_marked

    def get_current_path(self):
        return self.__active.get_path()

    def get_current_path_with_selected(self):
        return self.__active.get_path_with_selected()

    def refresh(self):
        self.__active.refresh()

    def get_active(self) -> FileList:
        return self.__active

    def get_inactive(self) -> FileList:
        return self.__right_list if self.left_is_active else self.__left_list

    def get_left(self) -> FileList:
        return self.__left_list

    def get_right(self) -> FileList:
        return self.__right_list
