grid = MDP_grid('grid_values.txt', 30, 40, 'x2y2', 'x27y37', 1)
grid.create_grid()
mdp = puamdp.PUAMDP(grid.rewards, grid.actions, grid.transitions)
horizon = (grid.GRID_X + grid.GRID_Y) * 2
for i in range(11):
    w = i / 10
    policy, rewards, uncertainty = mdp.compute_optimal_policy(w, horizon, grid.start)