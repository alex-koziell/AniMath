import numpy as np
from shape import Shape

def superImpose(shape1: Shape, shape2: Shape):
    """ Superimposes shape1 onto shape 2, without rotation or scaling. """
    shape1.translate(shape2.center-shape1.center)

def shapeInterpolation(shape1: Shape, shape2: Shape):
    """ Transforms shape1 into shape2. """
    
    # add vertices to either shape if necessary
    numToAdd = int((shape1.vertices.size - shape2.vertices.size)/2)
    if numToAdd > 0:
        addVertices(shape2, numToAdd)
    elif numToAdd < 0:
        addVertices(shape1, abs(numToAdd))

    assert shape1.vertices.size == shape2.vertices.size
    N = int(shape1.vertices.size/2)

    # match them between shapes
    # compute pair-wise distance matrix
    pairWiseDist = np.empty((N,N))
    for n in range(N):
        for m in range(N):
            # rows for shape 1 vertex
            pairWiseDist[n,m] = np.linalg.norm(shape1.vertices[n] - shape2.vertices[m])

    # Hungarian Algorithm
    costMatrix = pairWiseDist # Abstract awaaaay 0_¬
    costMatrix = costMatrix - np.reshape(costMatrix.min(axis=1), (N, 1)) # subtract minimum of every row
    costMatrix = costMatrix - costMatrix.min(axis=0)                     # and minimum of every column
    print(costMatrix)

    # Find minimum lines to cover zeros
    maxZeros = np.empty((N,N))
    for n in range(N):
        for m in range(N):
            rowZeros = sum(x==0 for x in costMatrix[n,:])
            colZeros = sum(y==0 for y in costMatrix[:,m])
            maxZeros[n,m] = colZeros - rowZeros
            if costMatrix[n,m] == 0 and rowZeros == 1 and colZeros == 1:
                maxZeros[n,m] = 1
    print(maxZeros)

    lines = np.zeros((N,N))
    numLines = 0
    for n in range(N):
        for m in range(N):
            if costMatrix[n,m] == 0:
                if maxZeros[n,m] > 0:
                    for i in range(N):
                        maxZeros[i,m] = 0
                        lines[i,m] = 1
                    numLines += 1
                elif maxZeros[n,m] < 0:
                    for j in range(N):
                        maxZeros[n,j] = 0
                        lines[n,j] = 1
                    numLines += 1
    print(lines)
    print(numLines)

    # If numLines < N

    # Assign one zero per row and column as a list of (shape1_index, shape2_index)
    # pairs = []
    # for n in range(N):
    #     for m in range(N):
    #         if costMatrix[n,m] == 0:


    




    # interpolate shape1 vertices to shape 2 vertices
    # clean up by turning shape 1 into shape 2 if shape 2 had fewer vertices

def addVertices(shape: Shape, N: int):
    """ Adds evenly distributed vertices along the edges of the shape. """
    numSides = int(shape.vertices.size/2)
    
    sides = np.asarray([]) # vectors for each edge of the original shape
    perimeter = 0
    for i in range(numSides):
        edgeVector = shape.vertices[(i+1)%numSides]-shape.vertices[i]
        perimeter += np.linalg.norm(edgeVector)
        sides = np.append(sides, edgeVector)
    sides = sides.reshape(numSides, 2)

    if N <= 0:
        return
    
    elif N == 1:
        newVertex = shape.vertices[0] + sides[0]/2 # add to first side
        shape.vertices = np.insert(shape.vertices, 1, newVertex, axis=0)

    elif N == 2:
        newVertex = shape.vertices[0] + sides[0]/2 # add to first and last sides
        shape.vertices = np.insert(shape.vertices, 1, newVertex, axis=0)
        newVertex = shape.vertices[-1] + sides[-1]/2
        shape.vertices = np.append(shape.vertices, newVertex)

    elif N == numSides: #simple case: half way between each side
        for n in range(N):
            newVertex = shape.vertices[2*n] + sides[n]/2
            shape.vertices = np.insert(shape.vertices, 2*n+1, newVertex, axis=0)

    else:
        spacing = (N-2)*perimeter/N
        distances = np.linspace(perimeter/N, (N-1)*perimeter/N, N) # divide perimeter evenly
        old_vertices = np.asarray(shape.vertices)
        for n, distance in enumerate(distances):
            travelled = 0 # travel along perimeter
            for sideNum, side in enumerate(sides):
                hadTravelled = travelled
                travelled += np.linalg.norm(side)
                if distance < travelled: # if we are on the right edge
                    alongEdgeByFraction = (distance-hadTravelled)/np.linalg.norm(side)
                    newVertex = old_vertices[sideNum] + sides[sideNum]*alongEdgeByFraction
                    shape.vertices = np.insert(shape.vertices, sideNum+n+1, newVertex, axis=0)
                    break
    
    shape.vertices = shape.vertices.reshape(numSides+N, 2)