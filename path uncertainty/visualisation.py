import tkinter as tk
import math


class Window(tk.Tk):
    def __init__(self, mdp_grid, policy, rewards):
        super().__init__()
        self.mdp_grid = mdp_grid
        self.policy = policy
        self.rewards = rewards
        self.length = 45
        self.border = 0
        self.offset_x = 0.5
        self.offset_y = 0.5
        self.set_window_dimensions()
        self.center_window_on_screen()
        self.resizable(False, False)
        # define the background color as white
        self.config(bg='white')
        self.canvas = tk.Canvas(self, width=self.window_width, height=self.window_height, borderwidth=0, bg='white')
        self.canvas.place(x=0, y=0)
        # define the view-mode. Default only two view-modes are set.
        self.view_mode = 0
        self.max_view = 1   # Set a higher value for debugging mode
        # add the actual drawing area for the puzzle grid
        self.drawing_area_color = "white"
        self.draw_background_rectangle()
        self.create_drawing_area()

    def set_window_dimensions(self):
        self.window_width = self.length * (1 + self.mdp_grid.GRID_X) * 1.3
        self.window_height = self.length * (1 + self.mdp_grid.GRID_Y)
        # get the screen dimension
        window_width = int(self.window_width)
        window_height = int(self.window_height)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale_x = 1
        scale_y = 1
        if window_width > 0.95*screen_width:
            scale_x = 0.95*screen_width/window_width
        if window_height > 0.7*screen_height:
            scale_y = 0.7*screen_height/window_height
        scale = min(scale_x, scale_y)
        if scale < 1:
            self.length = self.length * scale
            self.window_width = self.window_width * scale
            self.window_height = self.window_height * scale

    def center_window_on_screen(self):
        # get the screen dimension
        window_width = int(self.window_width)
        window_height = int(self.window_height)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def create_drawing_area(self):
        thin_lines = 1
        thick_lines = 3
        self.add_heatmap(self.rewards)
        self.fill_grid()
        self.add_policy_lines()
        self.draw_grid_lines(thin_lines)  # draw the thin gridlines
        self.draw_border_lines(thick_lines)  # draw thick lines around the border

    def draw_background_rectangle(self):
        size_x = self.mdp_grid.GRID_X
        size_y = self.mdp_grid.GRID_Y
        length = self.length
        border = self.border
        color = self.drawing_area_color
        x1 = length * (self.offset_x - border)
        y1 = length * (self.offset_y - border)
        x2 = length * (self.offset_x + size_x + border)
        y2 = length * (self.offset_y + size_y + border)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=0)

    def draw_border_lines(self, thickness):
        size_x = self.mdp_grid.GRID_X
        size_y = self.mdp_grid.GRID_Y
        length = self.length
        x1 = length * self.offset_x
        y1 = length * self.offset_y
        x2 = length * self.offset_x
        y2 = length * (self.offset_y + size_y)
        self.canvas.create_line(x1, y1, x2, y2, width=thickness)
        x1 = length * (self.offset_x + size_x)
        y1 = length * self.offset_y
        x2 = length * (self.offset_x + size_x)
        y2 = length * (self.offset_y + size_y)
        self.canvas.create_line(x1, y1, x2, y2, width=thickness)
        x1 = length * self.offset_x
        y1 = length * self.offset_y
        x2 = length * (self.offset_x + size_x)
        y2 = length * self.offset_y
        self.canvas.create_line(x1, y1, x2, y2, width=thickness)
        x1 = length * self.offset_x
        y1 = length * (self.offset_y + size_y)
        x2 = length * (self.offset_x + size_x)
        y2 = length * (self.offset_y + size_y)
        self.canvas.create_line(x1, y1, x2, y2, width=thickness)

    def draw_grid_lines(self, thickness):
        size_x = self.mdp_grid.GRID_X
        size_y = self.mdp_grid.GRID_Y
        length = self.length
        for col in range(size_x + 1):
            x1 = length * (self.offset_x + col)
            y1 = length * self.offset_y
            x2 = length * (self.offset_x + col)
            y2 = length * (self.offset_y + size_y)
            self.canvas.create_line(x1, y1, x2, y2, width=thickness)
        for row in range(size_y + 1):
            x1 = length * self.offset_x
            y1 = length * (self.offset_y + row)
            x2 = length * (self.offset_x + size_x)
            y2 = length * (self.offset_y + row)
            self.canvas.create_line(x1, y1, x2, y2, width=thickness)

# ----------------- update contents of the puzzle in the GUI --------------

    def fill_grid(self):
        for x in range(self.mdp_grid.GRID_X):
            for y in range(self.mdp_grid.GRID_Y):
                draw_symbol(self, x, y)

    def add_policy_lines(self):
        for x in range(self.mdp_grid.GRID_X):
            for y in range(self.mdp_grid.GRID_Y):
                loc_name = 'x' + str(x) + 'y' + str(y)
                if loc_name == self.mdp_grid.start:
                    x_start = x
                    y_start = y

        route_tiles = draw_route(self, x_start, y_start)
        for x in range(self.mdp_grid.GRID_X):
            for y in range(self.mdp_grid.GRID_Y):
                loc_name = 'x' + str(x) + 'y' + str(y)
                if loc_name in self.policy and loc_name in route_tiles:
                    draw_line(self, x, y, self.policy[loc_name], route=True)
                elif loc_name in self.policy and loc_name not in route_tiles:
                    draw_line(self, x, y, self.policy[loc_name])

    def add_heatmap(self, rewards):
        for x in range(self.mdp_grid.GRID_X):
            for y in range(self.mdp_grid.GRID_Y):
                if 'x' + str(x) + 'y' + str(y) in rewards:
                    draw_heatmap_cell(self, x, y, rewards)

        r_x1 = int(self.length * 33)
        r_x2 = int(self.length * 36)
        r_y1 = int(self.length * 6)
        r_y2 = int(self.length * 36)

        min_val = min(rewards.values())
        max_val = max(rewards.values())
        value_range = max_val - min_val
        bar_length = r_y2 - r_y1
        print(bar_length)
        for i in range(bar_length + 1):
            score = max_val - (value_range / bar_length) * i
            colour = map_colours(rewards, score)
            self.canvas.create_rectangle(r_x1, r_y1 + i, r_x2, r_y1 + i, fill=colour, width=0)

        x1 = r_x2 - self.length
        x2 = r_x2
        for i in range(11):
            y1 = int(r_y1 + (bar_length / 10) * i)
            y2 = y1
            text_value = int(max_val - (value_range / 10) * i)
            self.canvas.create_line(x1, y1, x2, y2)
            self.canvas.create_text(r_x2 + self.length, y1, text=str(text_value), fill="black", font=("Helvetica", 10))

        self.canvas.create_rectangle(r_x1, r_y1, r_x2, r_y2, width=1)


def draw_heatmap_cell(window, x_val, y_val, values):
    # To draw with y = 0 at bottom
    new_y_val = window.mdp_grid.GRID_Y - 1 - y_val
    mag = 0.94
    mid_x = 1 + window.length * (0.5 + window.offset_x + x_val)
    mid_y = 1 + window.length * (0.5 + window.offset_y + new_y_val)
    x1 = int(mid_x - mag * window.length * 0.5) - 1
    y1 = int(mid_y - mag * window.length * 0.5) - 1
    x2 = int(mid_x + mag * window.length * 0.5)
    y2 = int(mid_y + mag * window.length * 0.5)
    loc_name = 'x' + str(x_val) + 'y' + str(y_val)
    colour = map_colours(values, values[loc_name])
    window.canvas.create_rectangle(x1, y1, x2, y2, fill=colour, width=1)


def map_colours(values, score):
    colour_min = "#1fd6ff"
    colour_max = "#ff6a1f"
    min_val = min(values.values())
    max_val = max(values.values())
    normalised_score = (score - min_val) / (max_val - min_val)
    red = int((1 - normalised_score) * int(colour_min[1:3], 16) + normalised_score * int(colour_max[1:3], 16))
    green = int((1 - normalised_score) * int(colour_min[3:5], 16) + normalised_score * int(colour_max[3:5], 16))
    blue = int((1 - normalised_score) * int(colour_min[5:7], 16) + normalised_score * int(colour_max[5:7], 16))
    colour = f"#{red:02x}{green:02x}{blue:02x}"
    return colour


def draw_line(window, x_val, y_val, direction, route=False):
    # To draw with y = 0 at bottom
    new_y_val = window.mdp_grid.GRID_Y - 1 - y_val
    mid_x = window.length * (0.5 + window.offset_x + x_val)
    mid_y = window.length * (0.5 + window.offset_y + new_y_val)

    match direction:
        case 'N':
            x2 = mid_x
            y2 = int(mid_y - window.length * 0.5)
        case 'E':
            x2 = int(mid_x + window.length * 0.5)
            y2 = mid_y
        case 'S':
            x2 = mid_x
            y2 = int(mid_y + window.length * 0.5)
        case 'W':
            x2 = int(mid_x - window.length * 0.5)
            y2 = mid_y
    if route:
        window.canvas.create_line(mid_x, mid_y, x2, y2, width=4)
    else:
        window.canvas.create_line(mid_x, mid_y, x2, y2)


def draw_route(window, x, y):
    visited_route = []
    loc_name = 'x' + str(x) + 'y' + str(y)
    while loc_name in window.mdp_grid.actions and loc_name not in visited_route:
        print(loc_name)
        direction = window.policy[loc_name]
        match direction:
            case 'N':
                next_x = x
                next_y = y + 1
                opp_dir = 'S'
            case 'E':
                next_x = x + 1
                next_y = y
                opp_dir = 'W'
            case 'S':
                next_x = x
                next_y = y - 1
                opp_dir = 'N'
            case 'W':
                next_x = x - 1
                next_y = y
                opp_dir = 'E'
        draw_line(window, next_x, next_y, opp_dir, route=True)
        visited_route.append(loc_name)
        loc_name = 'x' + str(next_x) + 'y' + str(next_y)
        x = next_x
        y = next_y
    return visited_route


def draw_symbol(window, x_val, y_val):
    # To draw with y = 0 at bottom
    new_y_val = window.mdp_grid.GRID_Y - 1 - y_val
    loc_name = 'x' + str(x_val) + 'y' + str(y_val)
    mag = 0.94
    mid_x = 1 + window.length * (0.5 + window.offset_x + x_val)
    mid_y = 1 + window.length * (0.5 + window.offset_y + new_y_val)
    x1 = math.floor(mid_x - mag * window.length * 0.5) - 1
    y1 = math.floor(mid_y - mag * window.length * 0.5) - 1
    x2 = math.floor(mid_x + mag * window.length * 0.5)
    y2 = math.floor(mid_y + mag * window.length * 0.5)
    if window.mdp_grid.start == loc_name:
        window.canvas.create_rectangle(x1, y1, x2, y2, fill="#6aff1f", width=1)
        window.canvas.create_text(mid_x, mid_y-1, text='s', fill="black", font=("Helvetica", 10, 'bold'))
    match window.mdp_grid.types[loc_name]:
        case 'obstacle':
            window.canvas.create_rectangle(x1, y1, x2, y2, fill="black", width=1)
        case 'goal':
            window.canvas.create_rectangle(x1, y1, x2, y2, fill="#6aff1f", width=1)
            window.canvas.create_text(mid_x, mid_y-1, text='g', fill="black", font=("Helvetica", 10, 'bold'))
        case 'slippery':
            window.canvas.create_rectangle(x1, y1, x2, y2, fill="#b0ffff", width=1)
        case 'grip':
            window.canvas.create_rectangle(x1, y1, x2, y2, fill="#ffb9b0", width=1)
