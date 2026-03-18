import puamdp


class MDP_grid:
    def __init__(self, file, x_size, y_size, start, goal, goal_reward):
        self.types = {}
        self.actions = {}
        self.rewards = {}
        self.locations = {}
        self.transitions = {}
        self.file = file
        self.start = start
        self.goal = goal
        self.goal_reward = goal_reward

        # Must be at least 4x4
        self.GRID_X = x_size
        self.GRID_Y = y_size
        self.OBSTACLE_REWARD = -100
        self.WALK_REWARD = -1
        # types = normal / goal / obstacle / slippery / certain

    def get_transitions(self, name, a, state_type):
        state_transitions = []
        state_x = self.locations[name][0]
        state_y = self.locations[name][1]

        match a:
            case 'N':
                straight_state = 'x' + str(state_x) + 'y' + str(state_y + 1)
                left_state = 'x' + str(state_x - 1) + 'y' + str(state_y + 1)
                right_state = 'x' + str(state_x + 1) + 'y' + str(state_y + 1)
                double_straight = 'x' + str(state_x) + 'y' + str(state_y + 2)
                double_left = 'x' + str(state_x - 1) + 'y' + str(state_y + 2)
                double_right = 'x' + str(state_x + 1) + 'y' + str(state_y + 2)
                two_step_border_check = 0 < state_y + 1 == self.GRID_Y - 1
                right_border_check = 0 < state_x == self.GRID_X - 1
                left_border_check = state_x == 0 and state_x < self.GRID_X - 1

            case 'S':
                straight_state = 'x' + str(state_x) + 'y' + str(state_y - 1)
                left_state = 'x' + str(state_x + 1) + 'y' + str(state_y - 1)
                right_state = 'x' + str(state_x - 1) + 'y' + str(state_y - 1)
                double_straight = 'x' + str(state_x) + 'y' + str(state_y - 2)
                double_left = 'x' + str(state_x + 1) + 'y' + str(state_y - 2)
                double_right = 'x' + str(state_x - 1) + 'y' + str(state_y - 2)
                two_step_border_check = state_y - 1 == 0 and state_y < self.GRID_Y - 1
                right_border_check = state_x == 0 and state_x < self.GRID_X - 1
                left_border_check = 0 < state_x == self.GRID_X - 1

            case 'E':
                straight_state = 'x' + str(state_x + 1) + 'y' + str(state_y)
                left_state = 'x' + str(state_x + 1) + 'y' + str(state_y + 1)
                right_state = 'x' + str(state_x + 1) + 'y' + str(state_y - 1)
                double_straight = 'x' + str(state_x + 2) + 'y' + str(state_y)
                double_left = 'x' + str(state_x + 2) + 'y' + str(state_y + 1)
                double_right = 'x' + str(state_x + 2) + 'y' + str(state_y - 1)
                two_step_border_check = 0 < state_x + 1 == self.GRID_X - 1
                right_border_check = state_y == 0 and state_y < self.GRID_Y - 1
                left_border_check = 0 < state_y == self.GRID_Y - 1
            case 'W':
                straight_state = 'x' + str(state_x - 1) + 'y' + str(state_y)
                left_state = 'x' + str(state_x - 1) + 'y' + str(state_y - 1)
                right_state = 'x' + str(state_x - 1) + 'y' + str(state_y + 1)
                double_straight = 'x' + str(state_x - 2) + 'y' + str(state_y)
                double_left = 'x' + str(state_x - 2) + 'y' + str(state_y - 1)
                double_right = 'x' + str(state_x - 2) + 'y' + str(state_y + 1)
                two_step_border_check = state_x - 1 == 0 and state_x < self.GRID_X - 1
                right_border_check = 0 < state_y == self.GRID_Y - 1
                left_border_check = state_y == 0 and state_y < self.GRID_Y - 1

        if state_type == 'normal':
            straight_p = 0.9

            state_transitions.append((straight_state, straight_p))
            if right_border_check:
                state_transitions.append((left_state, 0.1))
            elif left_border_check:
                state_transitions.append((right_state, 0.1))
            else:
                state_transitions.append((left_state, 0.05))
                state_transitions.append((right_state, 0.05))
        elif state_type == 'slippery':
            straight_p = 0.7
            div_2 = 0.15
            div_3 = 0.1
            if two_step_border_check:
                state_transitions.append((straight_state, 1))
            elif right_border_check and not two_step_border_check:
                state_transitions.append((double_left, div_2))
                state_transitions.append((double_straight, div_2))
                state_transitions.append((straight_state, straight_p))

            elif left_border_check and not two_step_border_check:
                state_transitions.append((double_right, div_2))
                state_transitions.append((double_straight, div_2))
                state_transitions.append((straight_state, straight_p))

            else:
                state_transitions.append((double_right, div_3))
                state_transitions.append((double_left, div_3))
                state_transitions.append((double_straight, div_3))
                state_transitions.append((straight_state, straight_p))
        else:
            state_transitions.append((straight_state, 1))
        return state_transitions

    def get_grid(self):
        file = open(self.file)
        obstacles = []
        slippery = []
        certain = []

        coordinates = file.read().splitlines()
        set_type = 0
        for i in coordinates:
            if i == '1':
                set_type = 1
            elif i == '2':
                set_type = 2
            else:
                if set_type == 0:
                    obstacles.append(i)
                elif set_type == 1:
                    slippery.append(i)
                else:
                    certain.append(i)
        file.close()
        return obstacles, slippery, certain

    def get_locations(self):
        for x in range(self.GRID_X):
            for y in range(self.GRID_Y):
                state = 'x' + str(x) + 'y' + str(y)
                self.types[state] = 'normal'
                self.locations[state] = (x, y)

    def get_types(self):
        obstacles, slippery, certain = self.get_grid()
        for i in obstacles:
            self.types[i] = 'obstacle'
        for i in slippery:
            self.types[i] = 'slippery'
        for i in certain:
            self.types[i] = 'certain'

        self.types[self.goal] = 'goal'
        self.rewards[self.goal] = self.goal_reward

        for state_name in self.types.keys():
            if self.types[state_name] == 'normal' or self.types[state_name] == 'slippery' or self.types[
                state_name] == 'certain':
                self.rewards[state_name] = self.WALK_REWARD
                self.actions[state_name] = ['N', 'S', 'E', 'W']
                if self.locations[state_name][0] == 0:
                    self.actions[state_name].remove('W')
                if self.locations[state_name][0] == self.GRID_X - 1:
                    self.actions[state_name].remove('E')
                if self.locations[state_name][1] == 0:
                    self.actions[state_name].remove('S')
                if self.locations[state_name][1] == self.GRID_Y - 1:
                    self.actions[state_name].remove('N')
            elif self.types[state_name] == 'obstacle':
                self.rewards[state_name] = self.OBSTACLE_REWARD

    def assign_transitions(self):
        for state_name in self.types.keys():
            if self.types[state_name] == 'normal' or self.types[state_name] == 'slippery' or self.types[
                state_name] == 'certain':
                for action in self.actions[state_name]:
                    self.transitions[(state_name, action)] = self.get_transitions(state_name, action,
                                                                                  self.types[state_name])

    def create_grid(self):
        self.get_locations()
        self.get_types()
        self.assign_transitions()



#
