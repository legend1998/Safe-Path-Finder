
# import libraries 


import shapefile
import pandas as pd
import numpy as np
import shapefile
import math
import statistics
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# get cordinates from shapefile crime_dt  using get-cord()

def get_cord():
    sf = shapefile.Reader('shape/crime_dt')
    shapes = sf.shapes()
    cordinates=[]

    for shape in shapes:
        cord=[]
        cord.append(shape.__geo_interface__['coordinates'][1])
        cord.append(shape.__geo_interface__['coordinates'][0])
        cordinates.append(cord)

    return cordinates


# generate grid using threshold (input by user)
  
def with_threshold(base,threshold,grid_size):
    total_crime_by_block=[]

    for i in range(len(base)):
        for j in range(len(base)):
            total_crime_by_block.append(base[i][j])

    total_crime_by_block.sort()
    threshold_val = total_crime_by_block[int((threshold/100)*len(total_crime_by_block))]
    std_dev = statistics.stdev(total_crime_by_block)

    maze = np.zeros((grid_size,grid_size))
    
    for i in range(len(base)):
        for j in range(len(base)):
            if(base[i][j]>threshold_val):
                maze[i][j]=1
    
    plt.pcolormesh(maze)
    for i in range(len(base)):
        for j in range(len(base)):
            plt.text(i,j,int(base[j][i]),fontsize=6)
    xlabel= [round(xlab,2) for xlab in np.linspace(45.49,45.53,grid_size)]
    ylabel= [round(ylab,2) for ylab in np.linspace(-73.59,-73.55,grid_size)]
    plt.xticks(range(grid_size),xlabel ,rotation="vertical")
    plt.yticks(range(grid_size),ylabel)
    plt.savefig("static/base.png")
    plt.close()

    return maze,std_dev


# make different size of grid usign cordinates 

def dynamic_grid(cordinates,grid_size=20):
    multiplyer=grid_size/4
    multiplyer*=100
    x=[]
    y=[]

    for cord in cordinates:
        x.append(cord[1])
        y.append(cord[0])
    x=np.array(x)
    y=np.array(y)
    x+=73.590
    y-=45.49
    x*=multiplyer
    y*=multiplyer

    base = np.zeros((grid_size,grid_size))
    
    for i in range(len(x)):
        try:
            base[int(y[i])][int(x[i])]+=1
        except:
            pass
    
    mean = base.mean()
    plt.pcolormesh(base,cmap='hot')
    plt.colorbar()
    xlabel= [round(xlab,2) for xlab in np.linspace(45.49,45.53,grid_size)]
    ylabel= [round(ylab,2) for ylab in np.linspace(-73.59,-73.55,grid_size)]
    plt.xticks(range(grid_size),xlabel ,rotation="vertical")
    plt.yticks(range(grid_size),ylabel)

    plt.savefig("static/foo.png")
    plt.close()
    return base,mean    

def get_geojson_grid(upper_right=(45.53,-73.55), lower_left=(45.49,-73.59), n=20):
    """Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids" (the default is the upper right hand [lat, lon] of the USA).

    lower_left: array_like
        The lower left hand corner of "grid of grids"  (the default is the lower left hand [lat, lon] of the USA).

    n: integer
        The number of rows/columns in the (n,n) grid.

    Returns
    -------

    list
        List of "geojson style" dictionary objects   
    """

    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]
            geo_json = {"type": "FeatureCollection",
                        "properties":{
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features":[]}

            grid_feature = {
                "type":"Feature",
                "geometry":{
                    "type":"Polygon",
                    "coordinates": [coordinates],
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)

    return all_boxes



#class for node 

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position



# astar algorithm

# this is admissible beacause it uses actual cost as 
# admissible candition
# estimated cost of h(n) <= actual cost

def astar(maze, start, end):
    upper_right=(45.53,-73.55)
    lower_left=(45.49,-73.59)
    lat_ = np.linspace(lower_left[0], upper_right[0], len(maze)+1)
    lon_ = np.linspace(lower_left[1], upper_right[1], len(maze)+1)

    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    if(maze[start[0]][start[1]]==1 or maze[end[0]][end[1]]==1):
        return "block is selected choose another point"
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    tim=time.perf_counter()+10
    open_list.append(start_node)
    while len(open_list) > 0:
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)
    
        if current_node == end_node:
            path = []
            total_cost=current_node.g
            current = current_node
            while current is not None:
                pos=current.position
                x=lat_[pos[0]]
                y=lon_[pos[1]]
                path.append((x,y))
                current = current.parent
            return [path[::-1],total_cost] # RetuRN PATH
        if time.perf_counter()>tim:
            break
        children=[]
        for childpos in neighbours(maze,current_node.position):
            if(maze[childpos[0]][childpos[1]]==1):
                continue
            new_node = Node(current_node, childpos)
            children.append(new_node)

        for child in children:
            for closed_child in closed_list:
                if child==closed_child:
                    continue
            child.g=gvalue(maze, current_node,child.position)
            child.h=((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f=child.g+child.h
            
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue
                # Add the child to the open list
            open_list.append(child)
    return False


# gvalue is used inside the function for getting the g value


def gvalue(maze,curr,childpos):
    #get current postion

    g=curr.g
    cpos=curr.position

    # if child is diagonal
    if(cpos[0]!=childpos[0] and cpos[1]!=childpos[1]):
        return 1.5+g
    else:
        direction=(cpos[0]-childpos[0],cpos[1]-childpos[1])

        # check if any block area alongside the path if present the cost will be 1.3 else 1

        if(direction==(1,0) or direction==(0,1)):
            if(maze[cpos[0]-1][cpos[1]-1]==1):
                return 1.3+g
            else:
                 return 1+g
        if(direction==(0,-1)):
            if(maze[cpos[0]-1][cpos[1]]==1):
                return 1.3+g
            else:
                 return 1+g
        if(direction==(-1,0)):
            if(maze[cpos[0]][cpos[1]-1]==1):
                return 1.3+g
            else :
                return 1+g
    

# return child of the current node executing

def neighbours(maze, node):
    #the 8 neighbours
    neigh=[(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    neighbour=[]
    for pos in neigh:
        newpos=(node[0]+pos[0],node[1]+pos[1])
        #if child is outside the grid skip
        if(newpos[0] > len(maze)-1 or newpos[0] < 0 or newpos[1] > len(maze)-1 or newpos[1]<0):
            continue
        #if(diagonal is block skip)
        if(newpos[0]>node[0] and newpos[1]<node[1]):
            if(maze[newpos[0]-1][newpos[1]]==1):
                continue
        elif(newpos[0]<node[0] and newpos[1]>node[1]):
            if(maze[newpos[0]][newpos[1]-1]):
                continue
        neighbour.append(newpos)
    return neighbour
