import pygame
import sys
import model
import ai
import time
import subprocess


pygame.init()
BOARD_SIZE = 4
NANO_TO_SEC = 1000000000

# UI
board_height = 480
extra_height = 150
width = 480
# size = width, height = 480, 800
screen = pygame.display.set_mode((width, board_height + extra_height))
pygame.display.set_caption('{} Puzzle'.format(BOARD_SIZE**2-1))
FPS = 30

# Fonts
tileFont = pygame.font.SysFont("", 72)


# Colors
white = (254,254,254)
black = (0,0,0)
borderColor = (92, 90, 86)
tileColor = white
fontColor = black

# ai
ai.init(BOARD_SIZE)
aiMoveIndex = 0
aiMoves = []

autoSolve = False
speed = 200

def gameLoop():
    global aiMoveIndex
    global aiMoves
    global autoSolve
    global speed
    global status_dot_timer 
    global status_dot_index
    
    clock = pygame.time.Clock()

    puzzle = model.Puzzle(boardSize=BOARD_SIZE)

    while True:
        for event in pygame.event.get():
            handleInput(event, puzzle)
        
        # auto solve
        if autoSolve and 0 <= aiMoveIndex < len(aiMoves):
            pygame.time.delay(speed)  
            puzzle.move(aiMoves[aiMoveIndex])
            aiMoveIndex += 1
            if puzzle.checkWin() or aiMoveIndex >= len(aiMoves):
                print("Puzzle solved!")
                aiMoveIndex = 0
                aiMoves = []
                autoSolve = False

        drawPuzzle(puzzle)
        pygame.display.flip()
        clock.tick(FPS)

def handleInput(event, puzzle):
    global aiMoveIndex
    global aiMoves
    global autoSolve

    if event.type == pygame.QUIT: sys.exit()
    elif event.type == pygame.KEYDOWN:
        
        
        if event.key == pygame.K_r:
            puzzle.shuffle()
            aiMoveIndex = 0
            aiMoves = []
            autoSolve = False
            
        elif event.key == pygame.K_h:
            if len(aiMoves) == 0:
                aiMoves = ai.idaStar(puzzle)
                aiMoveIndex = 0

            if len(aiMoves) != 0:
                puzzle.move(aiMoves[aiMoveIndex])
                if puzzle.checkWin():
                    aiMoveIndex = 0
                    aiMoves = []
                else:
                    aiMoveIndex += 1
        
        elif event.key == pygame.K_h:
            if len(aiMoves) == 0:
                print("Solving...")
                     
                     
                aiMoves = ai.idaStar(puzzle)               
                aiMoveIndex = 0

            if len(aiMoves) > 0:
                autoSolve = True  
        

    elif event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        
        # shuffle button
        reset_btn_rect = pygame.Rect(20, board_height + 10, 120, 40)
        if reset_btn_rect.collidepoint(pos):
            ai.status_msg = ""
            
            puzzle.shuffle()
            aiMoveIndex = 0
            aiMoves = []
            autoSolve = False
            
        # Solve Button
        solve_btn_rect = pygame.Rect((width - 120) // 2, board_height + 10, 120, 40)
        if solve_btn_rect.collidepoint(pos):
            if len(aiMoves) == 0:
                ai.status_msg = "Searching for the shortest sequence of moves..."               
                print("Solving...")
                drawPuzzle(puzzle) 
                pygame.display.flip() 
                
                aiMoves = ai.idaStar(puzzle)
                aiMoveIndex = 0
            if len(aiMoves) > 0:
                autoSolve = True
            
         
        # Switch button
        btn_rect = pygame.Rect(width - 160, board_height + 10, 140, 40)
        if btn_rect.collidepoint(pos):
            pygame.quit()
            subprocess.Popen(["python", "puzzle_game.py"])
            sys.exit()
            
        puzzleCoord = (pos[1]*puzzle.boardSize//board_height,
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
                                i*board_height/puzzle.boardSize,
                                width/puzzle.boardSize,
                                board_height/puzzle.boardSize)

            pygame.draw.rect(screen, currentTileColor, rect)
            pygame.draw.rect(screen, borderColor, rect, 1)

            fontImg = tileFont.render(numberText, 1, fontColor)
            screen.blit(fontImg,
                        (j*width/puzzle.boardSize + (width/puzzle.boardSize - fontImg.get_width())/2,
                        i*board_height/puzzle.boardSize + (board_height/puzzle.boardSize - fontImg.get_height())/2))
            
            
    # switch button to 3x3
    btn_rect = pygame.Rect(width - 160, board_height + 10, 140, 40)
    mouse_pos = pygame.mouse.get_pos()
    btn_color = (200, 200, 200) if btn_rect.collidepoint(mouse_pos) else (230, 230, 230)
    pygame.draw.rect(screen, btn_color, btn_rect)
    pygame.draw.rect(screen, borderColor, btn_rect, 2)

    btn_font = pygame.font.SysFont("", 24)
    btn_text = btn_font.render("Switch to 3x3", True, black)
    screen.blit(btn_text, (
        btn_rect.x + (btn_rect.width - btn_text.get_width()) // 2,
        btn_rect.y + (btn_rect.height - btn_text.get_height()) // 2
    ))
    
    # Shuffle button
    reset_btn_rect = pygame.Rect(20, board_height + 10, 120, 40)
    reset_btn_color = (200, 200, 200) if reset_btn_rect.collidepoint(pygame.mouse.get_pos()) else (230, 230, 230)
    pygame.draw.rect(screen, reset_btn_color, reset_btn_rect)
    pygame.draw.rect(screen, borderColor, reset_btn_rect, 2)

    reset_btn_font = pygame.font.SysFont("", 24)
    reset_btn_text = reset_btn_font.render("Shuffle", True, black)
    screen.blit(reset_btn_text, (
        reset_btn_rect.x + (reset_btn_rect.width - reset_btn_text.get_width()) // 2,
        reset_btn_rect.y + (reset_btn_rect.height - reset_btn_text.get_height()) // 2
    ))
    
    # Solve button
    solve_btn_rect = pygame.Rect((width - 120) // 2, board_height + 10, 120, 40)
    solve_btn_color = (200, 200, 200) if solve_btn_rect.collidepoint(pygame.mouse.get_pos()) else (230, 230, 230)
    pygame.draw.rect(screen, solve_btn_color, solve_btn_rect)
    pygame.draw.rect(screen, borderColor, solve_btn_rect, 2)

    solve_btn_font = pygame.font.SysFont("", 24)
    solve_btn_text = solve_btn_font.render("Solve", True, black)
    screen.blit(solve_btn_text, (
        solve_btn_rect.x + (solve_btn_rect.width - solve_btn_text.get_width()) // 2,
        solve_btn_rect.y + (solve_btn_rect.height - solve_btn_text.get_height()) // 2
    ))
    
    # Display Messages 
    status_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
    status_text = status_font.render(ai.status_msg, True, white)
    screen.blit(status_text, (20, board_height + extra_height - 80))  
    
    # status_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
    # lines = ai.status_msg.strip().split('\n')
    # for i, line in enumerate(lines):
    #     text_surface = status_font.render(line, True, white)
    #     screen.blit(text_surface, (20, board_height + 55 + i * 22))  
    
   


if __name__ =="__main__":
    gameLoop()
