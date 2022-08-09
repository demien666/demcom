import os
import time
from stat import ST_SIZE, ST_MTIME
from typing import List
import shutil
import errno
import pathlib

TYPE_FOLDER = 10
TYPE_FILE = 20


class FileInfo():
    def __init__(self, file_name, is_file, size, m_time):
        self.file_name = file_name
        self.is_file = is_file
        self.size = size
        self.m_time = m_time
        if is_file:
            self.select_order = TYPE_FILE
        else:
            self.select_order = TYPE_FOLDER

    def format_file(self, width):
        suffix = hr_size(self.size) + " " + self.m_time
        name = self.file_name
        if len(name) + len(suffix) + 4 > width:
            th = width - len(suffix) - 10
            name = name[0:th] + "..."
        suffix = suffix.rjust(width - 4 - len(name))
        return name + suffix


def is_file(folder_path, file_name):
    full_path = os.path.join(folder_path, file_name)
    return os.path.isfile(full_path)


def f2(i):
    s = str(i)
    return s if len(s) > 1 else "0" + s


def hr_time(ep_time):
    l_time = time.localtime(ep_time)
    return f2(l_time.tm_year) + "-" + f2(l_time.tm_mon) + "-" \
        + f2(l_time.tm_mday) + " " + f2(l_time.tm_hour) + ":" \
        + f2(l_time.tm_min) + ":" + f2(l_time.tm_sec)


def hr_size(size):
    if len(size) == 0:
        return ""
    lbls = ["Kb", "Mb", "Gb", "Tb"]
    result = "B"
    size = int(size)
    K = 1024
    for lb in lbls:
        if size > K:
            result = lb
            size = size / K

    result = '{:03.3f}'.format(size) + result
    result = result.replace(".000", "")
    return result


def get_file_attributes(folder_path, file_name):
    full_path = os.path.join(folder_path, file_name)
    is_file = os.path.isfile(full_path)
    st = os.stat(full_path)
    size = str(st[ST_SIZE]) if is_file else ""
    mtime = hr_time(st[ST_MTIME])
    return (is_file, size, mtime)


def list_dir_full(path) -> List[FileInfo]:
    file_names = os.listdir(path)
    result = [FileInfo("..", False, "", "")]
    for f in file_names:
        try:
            file_info = FileInfo(f, *get_file_attributes(path, f))
            result.append(file_info)
        except:
            pass
    return sorted(result,
                  key=lambda finf: str(finf.select_order) + finf.file_name)


def create_folder(path, folder):
    path = file_plus_folder(path, folder)
    result_message = "Successfully created the directory %s " % path
    try:
        os.mkdir(path)
    except OSError:
        result_message = "Creation of the directory %s failed" % path
    return result_message


def copy_files(src_folder: str, src_files: List[str], dst_folder: str):
    for f in src_files:
        try:
            src = file_plus_folder(src_folder, f)
            dst = file_plus_folder(dst_folder, f)
            if os.path.isdir(src):
                shutil.copytree(src, dst, symlinks=False, ignore=None)
            else:
                shutil.copy2(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise
    return "Copy operation completed"


def move_files(src_folder: str, src_files: List[str], dst_folder: str):
    for f in src_files:
        try:
            src = file_plus_folder(src_folder, f)
            dst = file_plus_folder(dst_folder, f)
            shutil.move(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise
    return "Move operation completed"    


def remove_folder(path):
    result_message = "Successfully removed %s " % path
    try:
        path = pathlib.Path(path)
        # print("Removing:", path)
        for item in path.iterdir():
            if item.is_dir():
                # print(item)
                remove_folder(item)
            else:
                item.unlink()
        path.rmdir()
    except OSError:
        result_message = "Removal of the directory %s failed" % path
    return result_message


def get_short_folder_name(path):
    p = pathlib.Path(path)
    return os.path.basename(p)


def file_plus_folder(folder, file):
    return os.path.join(folder, file)


def get_parent_folder(path):
    return str(pathlib.Path(path).parent)


def get_working_folder():
    return str(pathlib.Path(__file__).parent.absolute())


def run_shell_command(cmd):
    os.system(cmd)


def rename(folder, old_name, new_name):
    os.rename(file_plus_folder(folder, old_name), file_plus_folder(folder, new_name))


def test():
    print("Hello world!")


if __name__ == '__main__':
    test()
