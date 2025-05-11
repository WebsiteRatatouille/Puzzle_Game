import pygame
import sys
from core import ai
from core import model
import slice_image
import time
import subprocess

import tkinter as tk
from tkinter import filedialog



pygame.init()
tk.Tk().withdraw()

BOARD_SIZE = 4
NANO_TO_SEC = 1000000000

# UI
board_height = 480
extra_height = 200
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

# Switch mode
useImageMode = False

# Loading image tiles
tileImages = {}
for i in range(1, BOARD_SIZE * BOARD_SIZE):
    img = pygame.image.load(f"assets/tiles/{i}.png")
    img = pygame.transform.scale(img, (width // BOARD_SIZE, board_height // BOARD_SIZE))
    tileImages[i] = img
    
# Loading full image
imageDisplay = pygame.image.load("assets/img/number.png")



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
    global imageDisplay
    global useImageMode

    if event.type == pygame.QUIT: sys.exit()
    elif event.type == pygame.KEYDOWN:
        
        
        if event.key == pygame.K_r:
            puzzle.shuffle()
            aiMoveIndex = 0
            aiMoves = []
            autoSolve = False
            
        elif event.key == pygame.K_h:
            if len(aiMoves) == 0:
                print("Solving...")
                aiMoves = ai.idaStar(puzzle)
                aiMoveIndex = 0

            if len(aiMoves) != 0:
                puzzle.move(aiMoves[aiMoveIndex])
                if puzzle.checkWin():
                    aiMoveIndex = 0
                    aiMoves = []
                else:
                    aiMoveIndex += 1
            
            if len(aiMoves) > 0:
                autoSolve = True 
    

    elif event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()
        
        # shuffle button
        reset_btn_rect = pygame.Rect(20, board_height + 10, 90, 40)
        if reset_btn_rect.collidepoint(pos):
            ai.status_msg = ""
            
            puzzle.shuffle()
            aiMoveIndex = 0
            aiMoves = []
            autoSolve = False
            
        # Solve Button
        solve_btn_rect = pygame.Rect(120, board_height + 10, 100, 40)
        if solve_btn_rect.collidepoint(pos):
            if len(aiMoves) == 0:
                ai.status_msg = "Searching for the shortest sequence of moves..."               
                print("Solving...")
                drawPuzzle(puzzle) 
                pygame.display.flip() 
                            
                aiMoves = ai.idaStar(puzzle)
                aiMoveIndex = 0
                
            if len(aiMoves) != 0:
                puzzle.move(aiMoves[aiMoveIndex])
                if puzzle.checkWin():
                    aiMoveIndex = 0
                    aiMoves = []
                else:
                    aiMoveIndex += 1
                    
            if len(aiMoves) > 0:
                autoSolve = True
            
         
        # Switch 3x3 button
        btn_rect = pygame.Rect(20, board_height + 110, 200, 40)
        if btn_rect.collidepoint(pos):
            # reset tile
            slice_image.slice_image("assets/img/cat.png", "assets/tiles", rows=4, cols=4)
            tileImages.clear()
            for i in range(1, BOARD_SIZE * BOARD_SIZE):
                img = pygame.image.load(f"assets/tiles/{i}.png")
                img = pygame.transform.scale(img, (width // BOARD_SIZE, board_height // BOARD_SIZE))
                tileImages[i] = img
                
            pygame.quit()
            subprocess.Popen(["python", "puzzle_game.py"])
            sys.exit()
            
            
        # Switch Display mode button
        toggle_btn_rect = pygame.Rect(20, board_height + 60, 200, 40)
        if toggle_btn_rect.collidepoint(pos):
            global useImageMode
            useImageMode = not useImageMode
            
            if useImageMode == True:
                imageDisplay = pygame.image.load(slice_image.image_path)
            else:
                imageDisplay = pygame.image.load("assets/img/number.png")
                
        # Changing image
        example_rect = pygame.Rect(width - 40 - 150, board_height + extra_height - 40 - 150, 150, 150)
        if example_rect.collidepoint(pos):
            tk.Tk().withdraw()  #hide window tk
            file_path = filedialog.askopenfilename(
                
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
            )

            if file_path:               
                # update img
                imageDisplay = pygame.image.load(file_path)

                # call cutting image funcion
                slice_image.slice_image(file_path, "assets/tiles", rows=BOARD_SIZE, cols=BOARD_SIZE)
                slice_image.image_path = file_path

                # Loading tile
                tileImages.clear()
                for i in range(1, BOARD_SIZE * BOARD_SIZE):
                    img = pygame.image.load(f"assets/tiles/{i}.png")
                    img = pygame.transform.scale(img, (width // BOARD_SIZE, board_height // BOARD_SIZE))
                    tileImages[i] = img

                useImageMode = True
                
            
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
    global exampleImg
    global imageDisplay
    
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

            if numberText != '' and useImageMode:
                screen.blit(tileImages[int(numberText)], (rect.x, rect.y))
            elif numberText != '':
                fontImg = tileFont.render(numberText, 1, fontColor)
                screen.blit(fontImg,
                    (j*width/puzzle.boardSize + (width/puzzle.boardSize - fontImg.get_width())/2,
                    i*board_height/puzzle.boardSize + (board_height/puzzle.boardSize - fontImg.get_height())/2)
    )
            
            
    # switch button to 3x3
    btn_rect = pygame.Rect(20, board_height + 110, 200, 40)
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
    reset_btn_rect = pygame.Rect(20, board_height + 10, 90, 40)
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
    solve_btn_rect = pygame.Rect(120, board_height + 10, 100, 40)
    solve_btn_color = (200, 200, 200) if solve_btn_rect.collidepoint(pygame.mouse.get_pos()) else (230, 230, 230)
    pygame.draw.rect(screen, solve_btn_color, solve_btn_rect)
    pygame.draw.rect(screen, borderColor, solve_btn_rect, 2)

    solve_btn_font = pygame.font.SysFont("", 24)
    solve_btn_text = solve_btn_font.render("Solve", True, black)
    screen.blit(solve_btn_text, (
        solve_btn_rect.x + (solve_btn_rect.width - solve_btn_text.get_width()) // 2,
        solve_btn_rect.y + (solve_btn_rect.height - solve_btn_text.get_height()) // 2
    ))
    
    #display mode button
    toggle_btn_rect = pygame.Rect(20, board_height + 60, 200, 40)
    toggle_color = (200, 200, 200) if toggle_btn_rect.collidepoint(pygame.mouse.get_pos()) else (230, 230, 230)
    pygame.draw.rect(screen, toggle_color, toggle_btn_rect)
    pygame.draw.rect(screen, borderColor, toggle_btn_rect, 2)

    toggle_font = pygame.font.SysFont("", 24)
    toggle_text = toggle_font.render("Switch Display", True, black)
    screen.blit(toggle_text, (
        toggle_btn_rect.x + (toggle_btn_rect.width - toggle_text.get_width()) // 2,
        toggle_btn_rect.y + (toggle_btn_rect.height - toggle_text.get_height()) // 2
    ))

    
    # Display Messages 
    status_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
    status_text = status_font.render(ai.status_msg, True, white)
    screen.blit(status_text, (20, board_height + extra_height - 30))  
    
   
    
    # Example image
    imageDisplay = pygame.transform.scale(imageDisplay, (150, 150))
    example_rect = imageDisplay.get_rect()
    example_rect.bottomright = (width - 40, board_height + extra_height - 40)
    screen.blit(imageDisplay, example_rect) 
    
   


if __name__ =="__main__":
    gameLoop()
