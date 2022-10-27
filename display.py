import ctypes
import os
import shutil
import sys


class Colors:
    reset = "\033[0m"

    fg_black = "\033[30m"
    fg_brightBlack = "\033[30;1m"
    fg_red = "\033[31m"
    fg_brightRed = "\033[31;1m"
    fg_green = "\033[32m"
    fg_bright_green = "\033[32;1m"
    fg_yellow = "\033[33m"
    fg_bright_yellow = "\033[33;1m"
    fg_blue = "\033[34m"
    fg_bright_blue = "\033[34;1m"
    fg_magenta = "\033[35m"
    fg_bright_magenta = "\033[35;1m"
    fg_cyan = "\033[36m"
    fg_bright_cyan = "\033[36;1m"
    fg_white = "\033[37m"
    fg_bright_white = "\033[37;1m"

    bg_black = "\033[40m"
    bg_bright_black = "\033[40;1m"
    bg_red = "\033[41m"
    bg_bright_red = "\033[41;1m"
    bg_green = "\033[42m"
    bg_bright_green = "\033[42;1m"
    bg_yellow = "\033[43m"
    bg_bright_yellow = "\033[43;1m"
    bg_blue = "\033[44m"
    bg_bright_blue = "\033[44;1m"
    bg_magenta = "\033[45m"
    bg_bright_magenta = "\033[45;1m"
    bg_cyan = "\033[46m"
    bg_bright_cyan = "\033[46;1m"
    bg_white = "\033[47m"
    bg_bright_white = "\033[47;1m"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def setup_windows_console():
    # setup console
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    cmd = 'mode 200, 60'
    os.system(cmd)


def put(to_screen):
    sys.stdout.write(to_screen)


def draw_row(margin, char_map, widths, data=None):
    outline = Colors.fg_blue
    inner = Colors.fg_yellow
    # if there is no data in this row make a blank list
    if data is None:
        data = []
        for width in widths:
            data.append("")

    # print the left margin, then left char
    print(margin, end="")
    print(outline + char_map[0], end="")

    # print each piece of data at set width, using filler char, and separator char
    for i in range(len(widths)):
        # lead with appropriate amount of filler char
        print(outline + str(char_map[1] * (widths[i] - len(str(data[i])))) + inner + str(data[i])[:widths[i]], end="")
        # use appropriate right hand char
        if i < len(widths) - 1:
            print(outline + char_map[2] + inner, end="")
        else:
            print(outline + char_map[3] + inner)


def set_widths(table_data, column_headings=None):
    column_widths = []
    # easy way to make sure rows fit on screen
    max_width = shutil.get_terminal_size().columns - len(table_data[0])
    # set minimum column widths to the header widths
    if column_headings:
        for heading in column_headings:
            column_widths.append(len(heading))
    else:
        for item in table_data[0]:
            column_widths.append(len(str(item)))
    # step through rows of data finding the longest string in each column
    for row in table_data:
        for i, item in enumerate(row):
            min_width = column_widths[i]

            if len(str(item)) > min_width:
                column_widths[i] = len(str(item))

    # make sure the table is not too wide for the screen
    if sum(column_widths) >= max_width:
        shave_amount = sum(column_widths) - max_width + 1
        col_index = 0
        while shave_amount > 0:
            column_widths[col_index % len(column_widths)] -= 1
            shave_amount -= 1
            col_index += 1

    return column_widths


def table(table_data, column_headings=None, column_widths=None):
    if table_data is None:
        print("no data to display")
        return None
    # set column widths

    if column_widths is None:
        if column_headings is None:
            column_widths = set_widths(table_data)
        else:
            column_widths = set_widths(table_data, column_headings)

    if column_widths:
        column_widths = column_widths

    # set left margin
    # add up columns plus count of columns plus one // 2
    data_width = 0
    for width in column_widths:
        data_width += width
    data_width = (data_width + len(column_widths) + 1)
    terminal_size = shutil.get_terminal_size()
    margin = (terminal_size.columns - data_width) // 2
    left_margin = " " * margin

    # Table characters *left, filler, separator, right*
    top_chars = ["╭", "─", "┬", "╮"]
    outline_chars = ["├", "─", "┼", "┤"]
    data_row_chars = ["│", " ", "│", "│"]
    bottom_chars = ["╰", "─", "┴", "╯"]

    # Top of table
    draw_row(left_margin, top_chars, column_widths)

    # Headings for Table
    if column_headings is not None:
        draw_row(left_margin, data_row_chars, column_widths, column_headings)
        # Heading Data separator
        draw_row(left_margin, outline_chars, column_widths)

    # Table contents
    for item in table_data:
        draw_row(left_margin, data_row_chars, column_widths, item)

    # end of Table
    draw_row(left_margin, bottom_chars, column_widths)
    # reset color
    print(Colors.reset, end="")


def get_center_screen():
    return shutil.get_terminal_size().columns // 2


def up(lines):
    put("\033[" + str(lines) + "A")


def down(lines):
    put("\033[" + str(lines) + "B")


def right(lines):
    put("\33[" + str(lines) + "C")


def left(lines):
    put("\33[" + str(lines) + "D")


def main_menu():
    outer = Colors.fg_bright_blue
    outer_chars = ["*", "-", "|"]
    inner = Colors.fg_yellow
    color = "inner"

    with open("resources/main_menu.txt", "r") as menu:
        line = menu.readline()
        offset = get_center_screen() - (len(line) // 2)
        margin = " " * offset
        while line:
            put(margin)
            for character in line:
                if character in outer_chars:
                    if not (color.__eq__("outer")):
                        color = "outer"
                        put(outer)
                else:
                    if not color.__eq__("inner"):
                        color = "inner"
                        put(inner)
                put(character)
            line = menu.readline()
        put(inner)


def ascii_wguncl_colored():
    outer = Colors.fg_bright_blue
    inner = Colors.fg_yellow
    width = 158
    center = get_center_screen()
    offset = center - (width // 2)
    margin = " " * offset
    outline = False
    with open("resources/wgu_ncl.txt", "r") as logo:
        for line in logo:
            output = margin
            for character in line:
                if character.isupper() and not outline:
                    output += outer
                    outline = True
                if not character.isupper() and outline:
                    output += inner
                    outline = False

                # for the fowl owl coloring *******
                if character in ["\\", "/", "_", "{", "}", "(", ")"]:
                    output += "\u001b[38;5;94m"
                if character in [","]:
                    output += Colors.fg_bright_yellow
                if character in ["0", "o"]:
                    output += Colors.fg_red
                # for the fowl owl coloring *******

                output += character
            print(f"{output}", end="")
    print()
