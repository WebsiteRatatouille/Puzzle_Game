from core import model
import pickle
import sys
from collections import deque
import math
from time import perf_counter_ns
from multiprocessing import Pool

NANO_TO_SEC = 1000000000

def fact(n):
    if n <= 1:
        return 1
    return n * fact(n-1)

def nPr(n,r):
    return math.floor(fact(n)/fact(n-r))

def buildPatternDb(boardSize, group, groupNum):
    # tao puzzle trang thai ban dau
    puzzle = model.Puzzle(boardSize, shuffle = False)
    puzzle.count = 0


    groupWithBlank = group.copy()
    groupWithBlank.add(0)  # them tile 0 -> {0, 1, 2}

    visited = set() 
    closedList = {} 
    openList = deque() 
    
    iter = 0
    totIter = nPr(boardSize**2, len(groupWithBlank))
    t1 = perf_counter_ns()


    #(puzzle, prior direction)
    openList.append((puzzle,(0,0)))


    while openList:
        cur, prevMove = openList.popleft()

        # DA DUYET = BO QUA
        if not visitNode(cur,
                        visited,
                        closedList,
                        groupWithBlank,
                        group):
            continue
        
        for dir in puzzle.DIRECTIONS:
            if dir == prevMove: # HUONG LAP LAI
                continue

            validMove, simPuzzle = cur.simulateMove(dir)
            if not validMove:
                continue

            if simPuzzle[cur.blankPos[0]][cur.blankPos[1]] in group:
                simPuzzle.count += 1

            openList.append((simPuzzle, (-dir[0],-dir[1])))
        iter += 1


        if iter % 100000 == 0:
            t2 = perf_counter_ns()
            tDelta = (t2 - t1)/ NANO_TO_SEC
            print("Group {}, Iteration {:,} of {:,}, time elapsed: {}".format(groupNum, iter, totIter, tDelta))
            print("Size of closed list: {:,}".format(len(closedList)))
            print("Size of open list: {:,}".format(len(openList)))
            t1 = t2

    return closedList

# note lai trang trai moi va cap nhap min so buoc
def visitNode(puzzle, visited, closedList, groupWithBlank, group):
    puzzleHashWithBlank = puzzle.hash(groupWithBlank) #1-2-3-4-0-7
    # da xuat hien, da tham
    if puzzleHashWithBlank in visited:
        return False

    visited.add(puzzleHashWithBlank)

    
    groupHash = puzzle.hash(group)  
    if groupHash not in closedList:
        closedList[groupHash] = puzzle.count
        
    # so buoc hien tai it hon
    elif closedList[groupHash] > puzzle.count:
        closedList[groupHash] = puzzle.count

    return True

def main():
    
    
    boardSize = 4
    groups = [{1, 2, 3, 4, 7},{5, 6, 9, 10, 13},{8, 11, 12, 14, 15}]
    
    # boardSize = 5
    # groups = [{1,2,3,4,5},{6,7,8,9,10},{11,12,13,14,15},{16,17,18,19,20},{21,22,23,24}]
    
  
    closedList = []

    with Pool(processes=2) as pool:
        results = [pool.apply_async(buildPatternDb, (boardSize,groups[i],i)) for i in range(len(groups))]
        results = [res.get() for res in results]

        for res in results:
            closedList.append(res)


    with open('patternDb_'+str(boardSize)+'.dat', 'wb') as patternDbFile:
        pickle.dump(groups, patternDbFile)
        pickle.dump(closedList, patternDbFile)

    for i in range(len(closedList)):
        group = closedList[i]
        print("Group:",groups[i],len(group),"permutations")

if __name__ == '__main__':
    main()
