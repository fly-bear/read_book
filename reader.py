import sys
import tty
import termios
import json
import os
import math
import pdb


last_line = '\x1b[1A'
clear_line = '\x1B[K'
clear_this_line = '\r' + clear_line
clear_last_line = last_line + clear_line


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


def _getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


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


def print_context(skip, context, total, name):
    start = False
    jump = False
    print(context + '\n')
    sys.stdout.write('\t ({}/{})'.format(skip + 1, total))
    sys.stdout.flush()
    ch = _getch()
    while ch not in ['j','k','e','d','t','c','a','s']:
        ch = _getch()
    if ch == 'j' or ch == 'a':
        skip -= 2
        jump = True
    elif ch == 'k' or ch == 's':
    	pass
    elif ch == 'd':
        sys.stdout.write(clear_this_line + last_line)
    elif ch == 't':
        try:
            skip = int(input("\n index: "))
            skip -= 1
        except Exception as e:
            print("not a valid num")
            sys.stdout.write(clear_this_line + clear_last_line)
        sys.stdout.write(clear_this_line + clear_last_line + last_line)
        skip -= 1
        jump = True
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
    sys.stdout.write(clear_this_line + clear_last_line * 2)
    sys.stdout.flush()
    return jump, skip, start


def main():
    term_width = os.get_terminal_size().columns
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
    jump = False
    while skip < total:
        line = book[skip].replace('\n', '')
        if line == '' and not jump:
            skip += 1
            continue
        elif line == '' and jump:
            skip -= 1
            continue
        jump = False
        while len(line.encode('gbk')) > term_width:
            offset = 0
            try:
                text = line.encode('gbk')[0:term_width].decode('gbk')
            except Exception as e:
                offset = 1
                text = line.encode('gbk')[0:term_width - offset].decode('gbk')
            jump, skip, start = print_context(skip, text, total, name)
            if start:
                return
            if jump:
                break
            line = line.encode('gbk')[term_width - offset:].decode('gbk')
        if not jump:
            jump, skip, start = print_context(skip, line, total, name)
            if start:
                return
        skip += 1


if __name__=='__main__':
    while True:
        shelf, last_book = get_read_his()
        main()

