import grid_env
import puamdp
import time

WIDTH_MAZE = 3


def run_program(w,horizon,depth_maze):
    start_time_grid = time.time()

    # file_name = "input_files/empty_tiles_"+str(depth_maze)
    # f = open(file_name, "w")
    # maze = ""
    # for i in range(depth_maze):
    #    maze += "x"+str(i)+"y0\n"
    #    maze += "x" + str(i) + "y4\n"
    # maze+="x1y0\n"

    # f.write("Now the file has more content!")
    # f.close()

    grid = grid_env.MDP_grid('empty_grid.txt', depth_maze, WIDTH_MAZE, 'x0y0', 'x' + str(depth_maze) + 'y2', 1)
    nb_tiles = depth_maze * WIDTH_MAZE
    grid.create_grid()
    mdp = puamdp.PUAMDP(grid.rewards, grid.actions, grid.transitions)

    start_time_policy = time.time()
    policy, rewards, uncertainty = mdp.compute_optimal_policy(w, horizon, grid.start)

    end_time = time.time()

    with open('results.txt', 'a') as f:
        f.write(str(horizon) + "\t" + str(depth_maze) + "\t" + str(nb_tiles) + "\t" + str(w) + "\t" + str(
            end_time - start_time_grid) + "\t" + str(end_time - start_time_policy) + "\n")
        f.close()


for depth_maze in [50,100,150,200,250,300,350,400,450,500]:
    for w in [0, 0.5, 1]:
        for horizon in [200,400,600]:
            run_program(w,horizon,depth_maze)
