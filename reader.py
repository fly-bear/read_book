import sys
import json
import os
import threading
import math
from datetime import datetime


last_line = '\x1b[1A'
clear_line = '\x1B[K'
clear_this_line = '\r' + clear_line
clear_last_line = last_line + clear_line
platform = 'unix'
control = 'keyboard'


class MouseClass():

    def __init__(self):
        # super(MouseClass, self).__init__(*args, **kwargs)
        from pynput import mouse
        super().__init__()
        self.mouse_listener = mouse.Listener()
        self.__mouse_run_flag_ = True
        self.__mouse_destroy_flag_ = True

    def set_value(self, book=None, skip=0, pos=0):
        self.click_time = 0
        if book is None:
            book = []
        self.book = book
        self.total = len(book)
        self.skip = skip
        self.lines = []
        self.width = os.get_terminal_size().columns
        # self.width = 100
        self.set_lines()
        self.skip += 1
        self.pos = pos

    def get_value(self):
        return self.skip, self.pos

    def on_click(self, x, y, button, pressed):
        from pynput import mouse
        if button == mouse.Button.left and pressed:
            click_time = math.ceil(datetime.now().timestamp()*1000)
            if click_time - self.click_time < 300:
                self.__mouse_destroy_flag_ = False
                sys.stdout.write(clear_this_line + clear_last_line * 2)
                sys.stdout.flush()
                self.skip -= 1
                return False
            else:
                self.click_time = click_time

    def on_scroll(self, x, y, dx, dy):
        from pynput import mouse
        if dy > 0:
            if self.pos >= len(self.lines):
                self.pos = 0
                self.set_lines()
                self.skip += 1
        elif self.pos >= 2:
            self.pos -= 2
        else:
            self.skip -= 2
            self.set_lines(-1)
            self.pos = len(self.lines) - 1
            self.skip += 1
        sys.stdout.write(clear_this_line + clear_last_line * 2)
        print(self.lines[self.pos] + '\n')
        sys.stdout.write('\t ({}/{})({:.2f}%)'.format(self.skip, self.total, (self.skip)/self.total*100))
        sys.stdout.flush()
        self.pos += 1
        if not self.__mouse_destroy_flag_:
            return False

    def set_lines(self, direct = 1):
        line = self.book[self.skip].replace('\n', '')
        while line == '':
            self.skip += direct
            line = self.book[self.skip].replace('\n', '')
        lines = []
        while len(line.encode('gbk')) > self.width:
            offset = 0
            try:
                text = line.encode('gbk')[:self.width].decode('gbk')
            except Exception as e:
                offset = 1
                text = line.encode('gbk')[:self.width - offset].decode('gbk')
            lines.append(text)
            line = line.encode('gbk')[self.width - offset:].decode('gbk')
        lines.append(line)
        self.lines = lines

    def run(self):
        from pynput import mouse
        with mouse.Listener( on_click = self.on_click, on_scroll = self.on_scroll,
                                  suppress= not self.__mouse_run_flag_) as self.mouse_listener:
            self.mouse_listener.join()


def scan_files(directory,prefix=None,postfix=None):
    files_list=[]
    
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root,special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root,special_file))
            else:
                files_list.append(os.path.join(root,special_file))
                          
    return files_list


class _Getch:
    def __init__(self):
        global platform
        try:
            self.impl = _GetchWindows()
            platform = 'win'
        except ImportError:
            self.impl = _GetchUnix()
            platform = 'unix'

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import colorama
        colorama.init()
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


_getch = _Getch()


def get_read_his():
    name = ''
    shelf = {}
    try:
        with open('./bookshelf.txt', 'r') as f:
            shelf = json.loads(f.read())
    except Exception as e:
        print(str(e))
    if shelf.__contains__('lastbook'):
        name = shelf['lastbook']
    return shelf, name


def control_by_mouse(book, skip, pos):
    km = MouseClass()
    km.set_value(book, skip, pos)
    km.run()
    return km.get_value()

def print_context(skip, context, total, name, direct=1, pos = 0):
    global control
    start = False
    lines = []
    term_width = os.get_terminal_size().columns
    while len(context.encode('gbk')) > term_width:
        offset = 0
        try:
            text = context.encode('gbk')[:term_width].decode('gbk')
        except Exception as e:
            offset = 1
            text = context.encode('gbk')[:term_width - offset].decode('gbk')
        lines.append(text)
        context = context.encode('gbk')[term_width - offset:].decode('gbk')
    lines.append(context)
    if direct == 1:
        pos = 0
    elif direct == -1:
        pos = len(lines) - 1
    print(lines[pos] + '\n')
    pos += 1
    sys.stdout.write('\t ({}/{})({:.2f}%)'.format(skip + 1, total, (skip+1)/total*100))
    sys.stdout.flush()
    while pos <= len(lines):
        ch = _getch()
        if platform == 'win':
            ch = ch.decode()
        while ch not in ['j', 'k', 'e', 'd', 't', 'c', 'a', 's', 'm']:
            ch = _getch()
            if platform == 'win':
                ch = ch.decode()
        if ch == 'm':
            direct = 1
            control = 'mouse'
            return skip, start, direct, pos
        sys.stdout.write(clear_this_line + clear_last_line * 2)
        if ch == 'j' or ch == 'a':
            direct = -1
            if pos < 2:
                skip -= 2
                break
            else:
                pos -= 2
                print(lines[pos] + '\n')
                sys.stdout.write('\t ({}/{})({:.2f}%)'.format(skip + 1, total, (skip+1)/total*100))
                sys.stdout.flush()
                pos += 1
        elif ch == 'k' or ch == 's':
            direct = 1
            if pos == len(lines):
                break
            print(lines[pos] + '\n')
            sys.stdout.write('\t ({}/{})({:.2f}%)'.format(skip + 1, total, (skip+1)/total*100))
            sys.stdout.flush()
            pos += 1
        elif ch == 'd':
            sys.stdout.write(clear_this_line + last_line)
        elif ch == 't':
            direct = 1
            try:
                skip = int(input("\n index: "))
                skip -= 1
            except Exception as e:
                print("not a valid num")
                sys.stdout.write(clear_this_line + clear_last_line)
            sys.stdout.write(clear_this_line + clear_last_line + last_line)
            skip -= 1
            break
        elif ch == 'e':
            sys.stdout.write(clear_this_line + clear_last_line * 3)
            shelf['lastbook'] = name
            shelf[name] = skip
            with open('./bookshelf.txt', 'w') as f:
                f.write(json.dumps(shelf))
            exit(0)
        elif ch == 'c':
            start = True
            shelf['lastbook'] = name
            shelf[name] = skip
            with open('./bookshelf.txt', 'w') as f:
                f.write(json.dumps(shelf))
            break
    return skip, start, direct, pos


def main():
    global control
    term_width = os.get_terminal_size().columns
    # term_width = 100
    book_list = list(map(lambda x: x.split('.txt')[0][8:], scan_files('./books', postfix='.txt')))
    print('choose a book: ')
    i = 1
    for item in book_list:
        index = 0
        if shelf.__contains__(item):
            index = shelf[item]
        count = 0
        try:
            with open('./books/{}.txt'.format(item), 'r', encoding='utf-8') as f:
                for a, line in enumerate(f):
                    count += 1
        except Exception as e:
            with open('./books/{}.txt'.format(item), 'r', encoding='gbk') as f:
                for a, line in enumerate(f):
                    count += 1
        print('{}. {} ({}/{})'.format(str(i), item, index + 1, count))
        i += 1
    book = []
    get = input("input book num or enter to choose default (default: {}): ".format(last_book))
    sys.stdout.write(clear_this_line + clear_last_line * (i + 1))
    if get != '':
        name = book_list[int(get) - 1]
    else:
        name = last_book

    if shelf.__contains__(name):
        skip = shelf[name]
    else:
        skip = 0
    try:
        with open('./books/' + name + '.txt', 'r', encoding='utf-8') as f:
            book = f.readlines()
    except Exception as e:
        with open('./books/' + name + '.txt', 'r', encoding='gbk') as f:
            book = f.readlines()
    total = len(book)
    direct = 1
    pos = 0
    while skip < total:
        line = book[skip].replace('\n', '')
        if line == '':
            skip += direct
            continue
        if control == 'keyboard':
            skip, start, direct, pos = print_context(skip, line, total, name, direct, pos)
        else:
            start = False
            skip -= 2
            skip, pos = control_by_mouse(book, skip, pos)
            direct = 0
            control = 'keyboard'
            pos -= 1
            skip -= 1
        if start:
            return
        skip += 1


if __name__=='__main__':
    while True:
        shelf, last_book = get_read_his()
        main()

