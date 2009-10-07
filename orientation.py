# There are a limited number of valid orientation combinations available,
# assuming each card has two neighboring patterns of the same gender, e.g.,
# north and east are the same gender, wst and south are the same gender in the
# initial position
#
# Since the gender of a neighboring edge has to be opposite, the following
# constraints apply:
#
ORIENTATION_CONSTRAINTS = [(-1,-1),(0,-1),(1,-1), \
                           (-1,0), (3,1), (4,2), \
                           (-1,3), (6,4), (7,5)]
# where the pairs are (left dependency, top dependency)
# and -1 indicates an edge, i.e., no dpendency
#
# Thus there are 4x2x2x2x1x1x2x1x1 = 64 possible orientation sets.

# unconstrained positions
ROTS = (0,90,180,270)

# constraint tables
LEFT = {0:(0,270),90:(90,180),180:(90,180),270:(0,270)}
TOP = {0:(0,90),90:(0,90),180:(180,270),270:(180,270)}
TOP_LEFT = [{0:0,90:90,180:90,270:0}, \
                 {0:0,90:90,180:90,270:0}, \
                 {0:270,90:180,180:180,270:270}, \
                 {0:270,90:180,180:180,270:270}]

def get_rotation_sets():

    # Create a list of rotation sets (assuming CCW rotation)
    rot_sets = []
    for i in range(64):
        rot_sets.append([])
    
    # first tile can be any rotation (4 groups of 16)
    for i in range(4):
        for j in range(16):
            rot_sets[i*16+j].append(ROTS[i])

    # second tile is constrained to the left only (4 groups of 8x2)
    for i in range(4):
        for j in range(8):
            rot_sets[i*16+j].append(LEFT[rot_sets[i*16+j][0]][0])
            rot_sets[i*16+j+8].append(LEFT[rot_sets[i*16+j+8][0]][1])

    # third tile is constrained to the left only (8 groups of 4x2)
    for i in range(8):
        for j in range(4):
            rot_sets[i*8+j].append(LEFT[rot_sets[i*8+j][1]][0])
            rot_sets[i*8+j+4].append(LEFT[rot_sets[i*8+j+4][1]][1])

    # fourth tile is constrained to the top only (16 groups of 2x2
    for i in range(16):
        for j in range(2):
            rot_sets[i*4+j].append(TOP[rot_sets[i*4+j][1]][0])
            rot_sets[i*4+j+2].append(TOP[rot_sets[i*4+j+2][1]][1])

    # fifth tile is constrained by top and left
    # sixth tile is constrained by top and left
    for i in range(64):
        rot_sets[i].append(TOP_LEFT[ROTS.index(rot_sets[i][1])][rot_sets[i][3]])
        rot_sets[i].append(TOP_LEFT[ROTS.index(rot_sets[i][2])][rot_sets[i][4]])

    # seventh tile is constrained to the top only (32 groups of 1x2)
    for i in range(32):
        rot_sets[i*2].append(TOP[rot_sets[i*2][4]][0])
        rot_sets[i*2+1].append(TOP[rot_sets[i*2+1][4]][1])

    # eigth tile is constrained by top and left
    # ninth tile is constrained by top and left
    for i in range(64):
        rot_sets[i].append(TOP_LEFT[ROTS.index(rot_sets[i][4])][rot_sets[i][6]])
        rot_sets[i].append(TOP_LEFT[ROTS.index(rot_sets[i][5])][rot_sets[i][7]])

    return rot_sets