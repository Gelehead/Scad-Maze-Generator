# Louis Duong 20201723
# Oscar Lavolet, 20242868

import sys
import random

cell_size = 10 #mm
wall_height = 10 #mm
wall_thickness = 1 #mm

labWidth = 13

strategy_choice = 1

def printl(twodArray):
    for row in twodArray:
        print(row)

def write(fileName, content):
    file = open(fileName, "w")
    file.write(content)
    file.close()

class Strategy :
    def __init__(self):
        pass

    def Apply(self):
        print("Applying Abstract Strategy")


# depth first search strategy 
class Algorithm1(Strategy) :

    def Apply(self):
        return self.make_maze(labWidth, labWidth)

    # found on https://rosettacode.org/wiki/Maze_generation#Python
    def make_maze(self, w = 16, h = 8):
        # empty map representation of maze
        vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
        # complete (full) map of the 2n+1-th lines
        ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
        # complete (full) map of the 2n-th lines 
        hor = [["+--"] * w + ['+'] for _ in range(h + 1)]
        def walk(x, y):
            # mark as visited
            vis[y][x] = 1

            # neighbours
            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]

            # shuffle neighbours
            random.shuffle(d)

            # for reah neighbours in the shuffled list :
            for (nx, ny) in d:
                # if visited : ignore
                if vis[ny][nx]: continue
                # if not visited and on the same x, break the vertical wall in between
                if nx == x: hor[max(y, ny)][x] = "+  "
                # if not visited and on the same y, break the horizontal wall in between
                if ny == y: ver[y][max(x, nx)] = "   "
                # explore the chosen neighbour
                walk(nx, ny)

        # starts the function with random coordinates
        walk(random.randrange(w), random.randrange(h))

        s = ""
        # joins the maze 2 lines by 2 lines
        for (a, b) in zip(hor, ver):
            s += ''.join(a + ['\n'] + b + ['\n'])
        return s

# "Prim" inspired Strategy
class Algorithm2(Strategy) :
    def Apply(self):
        return self.make_maze(labWidth, labWidth)
    
    # handmade Prim algorithm
    def make_maze(self, w = 16, h = 8):
        cells = [[[x,y] for y in range(h)] for x in range(w)]
        ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
        hor = [["+--"] * w + ['+'] for _ in range(h + 1)]

        # take a random cell as first cell
        x = random.randint(0,w-1) ; y = random.randint(0,h-1) 
        first = cells[x][y]

        # add the first cell to the visited cells list
        vis = [first]
        #remove it from the "cells" list
        cells = [[cell for cell in x if cell != first] for x in cells]

        # while "cells" is not empty
        while not self.allEmpty(cells) :
            # visit a random cell within the visited cells
            current  = vis[random.randint(0, len(vis)-1)]

            # visit its neighbour, making sure it is not in the visited cells list 
            # and is in the "cells" list (so we dont go out of bounds)
            x = current[0] ; y = current[1]
            n = [[x - 1, y], [x, y + 1], [x + 1, y], [x, y - 1]]
            visiting = n[random.randint(0,3)]

            # same principle as in DFS
            if visiting not in vis and self.isInSubset(visiting, cells) :
                    nx = visiting[0] ; ny = visiting[1] 
                    if nx == x: hor[max(y, ny)][x] = "+  "
                    if ny == y: ver[y][max(x, nx)] = "   "
                    vis.append(visiting)
                    # remove the cell from the "cells" list
                    cells = [[cell for cell in x if cell != visiting] for x in cells]
            
        s = ""
        # joins the maze 2 lines by 2 lines
        for (a, b) in zip(hor, ver):
            s += ''.join(a + ['\n'] + b + ['\n'])
        return s
    
    def isInSubset(self, pos, listOfCells):
        for cells in listOfCells:
            if pos in cells : 
                return True
        return False

    def allEmpty(self, listOfCells):
        for row in listOfCells :
            if len(row) != 0 :
                return False
        return True


# --------------------------------------------------------------
# --------------------- END ALGORITHM PART --------------------- 
# --------------------------------------------------------------

class Generator() :
    strategy = None
    lab = ""
    def __init__(self):
        pass

    def SetStrategy(self, new_strategy):
        self.strategy = new_strategy

    def Generate(self):
        self.lab = self.strategy.Apply()
        return self.lab

# --------------------------------------------------------------
# --------------------- END GENERATOR PART --------------------- 
# --------------------------------------------------------------

# TODO problem : ~5mm too much on each side 
class Creator() :
    blueprint = ""
    def __init__(self):
        pass

    # takes an ASCII representation of the labyrinth
    def scadify(self, lab):
        self.blueprint += "difference(){" 
        self.blueprint += "union(){cube(["+str(labWidth*cell_size)+","+str(labWidth*cell_size)+",1], center=false);"
        y = i = x = 0 
        # identify each wall and add its correpsonding 3d wall to the blueprint
        while i < len(lab):
            x = 0
            for _ in range(i,i+3*labWidth, 3):
                cell = lab[i:i+3]
                self.blueprint += self.identify(cell, x, y)
                i += 3    
                x += 10
            y += 5
            i += 2

        # adding exterior wall
        self.blueprint += "translate(["+str(labWidth*cell_size)+",0,0]){rotate([0,0,90]){cube(["+str((labWidth*cell_size)+1)+",1, "+str(cell_size)+"],center=false);}}}"
        # adding entrance
        self.blueprint += "union(){translate([0,1.01,1]){rotate([90,0,0]){cube(["+str(cell_size-1)+","+str(cell_size+1)+", 1.5],center=false);}}"
        # adding carving 
        self.blueprint += "translate(["+str(cell_size)+",0.15,2]){rotate([90,0,0]){linear_extrude(1) text( \"IFT 2125 LD & OL\", size= 5.0);}}"
        # adding exit
        self.blueprint += "translate(["+str(labWidth*cell_size-1)+","+str(labWidth*cell_size-9)+",1]){rotate([0,00,1]){cube(["+str(cell_size)+","+str(cell_size-1)+", "+str(cell_size+1)+"],center=false);}}}}"
        # TODO : add the carving thing
        return self.blueprint

    # gives the scad representation of the ASCII maze, wall by wall
    def identify(self, cell, x, y):
        if cell == "+--" : 
            return "translate(["+str(x-1)+","+str(y)+",0]){rotate([0,0,0]){cube(["+str(cell_size+1)+",1,"+str(cell_size)+"], center=false);}}"
        if cell == "|  ":
            return "translate(["+str(x)+","+str(y-(cell_size/2.5))+",0]){rotate([0,0,90]){cube(["+str(cell_size)+",1,"+str(cell_size)+"], center=false);}}"
        else:
            return ""

# --------------------------------------------------------------
# ---------------------- END CREATOR PART ---------------------- 
# --------------------------------------------------------------


# main call
def main():
    global strategy_choice

    output_file = "test.scad"

    args = sys.argv[:]
    if len(args) >= 2 :
        strategy_choice = int(args[1])

# ------------- Generator ------------------
    my_generator = Generator()
    if strategy_choice == 1:
        my_generator.SetStrategy(Algorithm1())
    elif strategy_choice == 2:
        my_generator.SetStrategy(Algorithm2())
    else :
        print("error strategy choice")

    lab = my_generator.Generate()

# ------------- Creator ------------------
    my_creator = Creator()
    my_creator.scadify(lab)

    blueprint = my_creator.blueprint

# ------------- Main ------------------ 
    
    # un - commentary this line to get the ASCII maze
    # print(lab)

    write(output_file,blueprint)

if __name__ == "__main__":
    main()
