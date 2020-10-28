import numpy as np

class Direction:
    # Cardinal directions
    N = np.array([0,-1])
    E = np.array([1,0])
    S = np.array([0,1])
    W = np.array([-1,0])
    # Diagonal directions
    NE = np.array([1,-1])
    SE = np.array([1,1])
    SW = np.array([-1,1])
    NW = np.array([-1,-1])

    NONE = np.array([0,0])

    direction_list = [N,E,S,W,NE,SE,SW,NW]