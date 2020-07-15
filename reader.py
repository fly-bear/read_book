import sys
import json
import os
import math
from datetime import datetime


last_line = '\x1b[1A'
clear_line = '\x1B[K'
clear_this_line = '\r' + clear_line
clear_last_line = last_line + clear_line
platform = 'unix'
control = 'keyboard'
source = 'local'


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


class qidianMouseClass():

    def __init__(self):
        from pynput import mouse
        super().__init__()
        self.mouse_listener = mouse.Listener()
        self.__mouse_run_flag_ = True
        self.__mouse_destroy_flag_ = True
        self.mode = 'content'
        self.width = os.get_terminal_size().columns
        self.direct = 1
        self.reviews = []
        self.review_pos = 0
        self.review_lines = 0
        self.click_time = 0
        self.nextt = False

    def set_value(self, chapter, skip, book_id, chapter_id, pos):
        self.chapter = chapter
        self.skip = skip
        self.book_id = book_id
        self.chapter_id = chapter_id
        self.pos = pos
        self.set_lines()
        self.skip += 1
        self.pos = pos
        self.total = len(chapter)

    def get_value(self):
        return self.skip, self.direct, self.pos, self.nextt

    def on_click(self, x, y, button, pressed):
        from pynput import mouse
        if button == mouse.Button.left and pressed:
            click_time = math.ceil(datetime.now().timestamp() * 1000)
            if click_time - self.click_time < 300:
                if self.mode == 'review':
                    sys.stdout.write(clear_last_line * self.review_lines + last_line)
                    sys.stdout.flush()
                    self.mode = 'content'
                else:
                    self.__mouse_destroy_flag_ = False
                    sys.stdout.write(clear_this_line + clear_last_line * 2)
                    sys.stdout.flush()
                    self.skip -= 2 if self.skip >0 else -1
                    self.direct = 0
                    return False
            else:
                self.click_time = click_time
        elif button == mouse.Button.right and pressed and self.mode == 'content':
            self.reviews = get_review(book_id=self.book_id, chapter_id=self.chapter_id, seg_id=self.skip - 1)
            if len(self.reviews) > 0:
                self.mode = 'review'
                review = self.reviews[0]
                while len(review) > 0 and review[-1] == '\n':
                    review = review[:-1]
                print('\n' + review)
                self.review_pos = 1
                self.review_lines = count_lines(review)

    def on_scroll(self, x, y, dx, dy):
        if self.mode == 'content':
            if not self.read_content(dy):
                self.nextt = True
                return False
        else:
            if not self.read_review(dy):
                sys.stdout.write(clear_last_line * self.review_lines + last_line)
                sys.stdout.flush()
                self.mode = 'content'


    def read_content(self, dy):
        if dy > 0:
            if self.pos >= len(self.lines):
                if self.skip >= len(self.chapter):
                    # sys.stdout.write(clear_this_line + clear_last_line * 2)
                    sys.stdout.flush()
                    return False
                self.pos = 0
                self.set_lines()
                self.skip += 1
        elif self.pos >= 2:
            self.pos -= 2
        elif self.skip >= 2:
            self.skip -= 2
            self.set_lines(-1)
            self.pos = len(self.lines) - 1
            self.skip += 1
        else:
            self.skip = 0
            self.set_lines(-1)
            self.pos = len(self.lines) - 1
            self.skip += 1
        sys.stdout.write(clear_this_line + clear_last_line * 2)
        print(self.lines[self.pos] + '\n')
        sys.stdout.write('\t ({}/{})({:.2f}%)'.format(self.skip, self.total, (self.skip) / self.total * 100))
        sys.stdout.flush()
        self.pos += 1
        return True

    def read_review(self, dy):
        if dy > 0:
            if self.review_pos >= len(self.reviews):
                return False
            sys.stdout.write(clear_last_line * self.review_lines)
            sys.stdout.flush()
            review = self.reviews[self.review_pos]
            while len(review) > 0 and review[-1] == '\n':
                review = review[:-1]
            print(review)
            self.review_pos += 1
            self.review_lines = count_lines(review)
        elif self.review_pos >= 2:
            pos = self.review_pos - 2
            review = self.reviews[pos]
            while len(review) > 0 and review[-1] == '\n':
                review = review[:-1]
            sys.stdout.write(clear_last_line * self.review_lines)
            sys.stdout.flush()
            print(review)
            self.review_pos -= 1
            self.review_lines = count_lines(review)
        else:
            review = self.reviews[0]
            while len(review) > 0 and review[-1] == '\n':
                review = review[:-1]
            sys.stdout.write(clear_last_line * self.review_lines)
            sys.stdout.flush()
            print(review)
            self.review_pos = 0
            self.review_lines = count_lines(review)
        return True

    def set_lines(self, direct = 1):
        line = self.chapter[self.skip].replace('\n', '')
        while line == '':
            self.skip += direct
            if self.skip >= len(self.chapter):
                return
            elif self.skip < 0:
                self.skip = 0
            line = self.chapter[self.skip].replace('\n', '')
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


def get_review(book_id, chapter_id, seg_id):
    import request_qidian as qd
    return qd.get_reviews(book_id=book_id, chapter_id=chapter_id, segment_id=seg_id)


def request_qidian():
    import request_qidian as qd
    global source, control
    source = 'qidian'
    shelf = {}
    with open('./bookshelf.txt', 'r') as f:
        shelf = json.loads(f.read())
    # book_id = 1010868264
    chap_id = -1
    last = -1
    choice = -1
    book_name = ''
    book_id = -1
    if shelf.__contains__('qidian'):
        books = list(shelf['qidian'].keys())
        if len(books) > 0:
            index = 1
            for book in books:
                print("{}. {}".format(index, book))
                index += 1
            get = input("choose a num: ")
            sys.stdout.write(clear_last_line * (len(books) + 1))
            sys.stdout.flush()
            if get == '':
                choice = -1
            else:
                choice = int(get)-1
                book_name = books[choice]
                book_id = shelf['qidian'][book_name]['book_id']
                chap_id = shelf['qidian'][book_name]['chapter_id']
                last = shelf['qidian'][book_name]['skip']
    if choice == -1:
        book_name = input("book name: ")
        book_id = input("book_id: ")
        sys.stdout.write(clear_last_line * 2)
        sys.stdout.flush()
    index = 0
    ids = qd.get_chapter_ids(book_id=book_id)
    while index < len(ids):
        if index < 0:
            index = 0
        chapter_id = ids[index] # chapter_id: [[id, name], [id, name], ...]
        index += 1
        if chap_id != -1 and chap_id != chapter_id[0]:
            continue
        chap_id = -1
        lines = qd.get_chapter(book_id=book_id, chapter_id=chapter_id[0])
        lines.insert(0, chapter_id[1])
        if last == -1:
            skip = 0
        else:
            skip = last
            last = -1
        pos = 0
        while skip < len(lines):
            text = lines[skip].replace('\n', '')
            if text == '':
                skip += 1
                continue
            if control == 'keyboard':
                skip, start, direct, pos, nextt = print_context(shelf=shelf, skip=skip, context=lines[skip], total=len(lines),
                                                     name=book_name, pos=0, book_id=book_id, chapter_id=chapter_id[0])
            else:
                skip, direct, pos, nextt = control_by_mouse_qidian(lines, skip, book_id, chapter_id[0], pos)
                if not nextt:
                    control = 'keyboard'
            if nextt and direct == 1:
                break
            elif nextt and direct == -1:
                index -= 2
                break
            skip += 1


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


def control_by_mouse_qidian(chapter, skip, book_id, chapter_id, pos):
    km = qidianMouseClass()
    km.set_value(chapter, skip, book_id, chapter_id, pos)
    km.run()
    return km.get_value()


def control_by_mouse(book, skip, pos):
    km = MouseClass()
    km.set_value(book, skip, pos)
    km.run()
    return km.get_value()


def print_context(shelf, skip, context, total, name, direct=1, pos = 0, book_id=0, chapter_id=0):
    global control, source
    start = False
    nextt = False
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
        while ch not in ['j', 'k', 'e', 'd', 't', 'c', 'a', 's', 'm', 'r', 'n', 'l']:
            ch = _getch()
            if platform == 'win':
                ch = ch.decode()
        if ch == 'm':
            direct = 1
            control = 'mouse'
            return skip, start, direct, pos, nextt
        elif ch =='r':
            if source == 'qidian' and skip > 0:
                reviews = get_review(book_id=book_id, chapter_id=chapter_id, seg_id=skip)
                show_reviews(reviews)
            continue
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
            save_shelf(shelf, name, skip, source, book_id, chapter_id)
            exit(0)
        elif ch == 'c':
            start = True
            save_shelf(shelf, name, skip, source, book_id, chapter_id)
            break
        elif ch == 'n':
            nextt = True
            direct = 1
            break
        elif ch == 'l':
            nextt = True
            direct = -1
            break
    return skip, start, direct, pos, nextt


def show_reviews(reviews):
    if len(reviews) == 0:
        return
    print('\n' + reviews[0])
    index = 1
    review = reviews[0]
    while len(review)>0 and review[-1] == '\n':
        review = review[:-1]
    lines = count_lines(review)
    while index < len(reviews):
        if index < 0:
            index = 0
        ch = _getch()
        if platform == 'win':
            ch = ch.decode()
        while ch not in ['a', 's', 'j', 'k', 'e', 'd']:
            ch = _getch()
            if platform == 'win':
                ch = ch.decode()
        if ch == 'd':
            sys.stdout.write(clear_last_line)
            sys.stdout.flush()
            continue
        sys.stdout.write(clear_last_line * lines)
        if ch == 'e':
            sys.stdout.write(last_line)
            sys.stdout.flush()
            return
        elif ch == 'j' or ch == 'a':
            index -= 2
            if index < 0:
                index = 0
            review = reviews[index]
            index += 1
            while len(review)>0 and review[-1] == '\n':
                review = review[:-1]
            print(review)
            lines = count_lines(review)
        elif ch == 'k' or ch == 's':
            review = reviews[index]
            index += 1
            while len(review)>0 and review[-1] == '\n':
                review = review[:-1]
            print(review)
            lines = count_lines(review)

    sys.stdout.write(clear_last_line * lines + last_line)
    sys.stdout.flush()


def count_lines(text):
    count = 0
    lines = text.split('\n')
    count += len(lines)
    width = os.get_terminal_size().columns
    for line in lines:
        try:
            count += (len(line.encode('gbk')) - 1) // width
        except Exception as e:
            pass
    return count


def save_shelf(shelf, name, skip, source, book_id = 0, chapter_id=0):
    if source == 'local':
        shelf['lastbook'] = name
        shelf[name] = skip
    elif shelf.__contains__("qidian"):
        shelf['qidian'][name] = {'book_id':book_id, 'chapter_id':chapter_id, 'skip': skip}
    else:
        shelf['qidian'] = {}
        shelf['qidian'][name] = {'book_id':book_id, 'chapter_id':chapter_id, 'skip': skip}
    with open('./bookshelf.txt', 'w') as f:
        f.write(json.dumps(shelf))


def main():
    global control
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
            skip, start, direct, pos, nextt = print_context(shelf, skip, line, total, name, direct, pos)
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
    args = sys.argv
    if len(args) > 1 and args[1] == 'qidian':
        request_qidian()
    else:
        while True:
            shelf, last_book = get_read_his()
            main()

