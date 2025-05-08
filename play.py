import pygame
import sys
import model

pygame.init()
BOARD_SIZE = 4

# ================= UX UI ======================
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
pygame.display.set_caption('{} Puzzle'.format(BOARD_SIZE**2-1))
FPS = 30

# Fonts
titleFont = pygame.font.SysFont("", 72)

# Colors
black = (0,0,0)
white = (255, 255, 255)
yellow = (242, 197, 133)
borderColor = (92, 90, 86)
tileColor = white
fontColor = black



def gameLoop():
    clock = pygame.time.Clock()
    
    puzzle = model.Puzzle(boardSize=BOARD_SIZE)
    
    while True:
        for event in pygame.event.get():
            handleInput(event, puzzle)
            
        drawPuzzle(puzzle)
        pygame.display.flip()
        clock.tick(FPS)
        
        
def handleInput(event, puzzle):
    if event.type == pygame.QUIT: sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            puzzle.shuffle()
    elif event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        puzzleCoord = (pos[1]*puzzle.boardSize//height,
                       pos[0]*puzzle.boardSize//width)
        dir = (puzzleCoord[0] - puzzle.blankPos[0],
               puzzleCoord[1] - puzzle.blankPos[1])
        
        if dir == puzzle.RIGHT:
            puzzle.move(puzzle.RIGHT)
        elif dir == puzzle.LEFT:
            puzzle.move(puzzle.LEFT)
        elif dir == puzzle.DOWN:
            puzzle.move(puzzle.DOWN)
        elif dir == puzzle.UP:
            puzzle.move(puzzle.UP)
    
    
def drawPuzzle(puzzle):
    screen.fill(black)
    
    for i in range(puzzle.boardSize):
        for j in range(puzzle.boardSize):
            currentTileColor = tileColor
            numberText = str(puzzle[i][j])
            
            if puzzle[i][j] == 0:
                currentTileColor = borderColor
                numberText = ''
                
            rect = pygame.Rect(j*width/puzzle.boardSize,
                               i*height/puzzle.boardSize,
                               width/puzzle.boardSize,
                               height/puzzle.boardSize)
            
            pygame.draw.rect(screen, currentTileColor, rect)
            pygame.draw.rect(screen, borderColor, rect, 1)
            
            fontImg = titleFont.render(numberText, 1, fontColor)
            screen.blit(fontImg,
                        (j*width/puzzle.boardSize + (width/puzzle.boardSize - fontImg.get_width())/2,
                        i*height/puzzle.boardSize + (height/puzzle.boardSize - fontImg.get_height())/2))
    
    
if __name__ == "__main__":
    gameLoop()