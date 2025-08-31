import pygame
import sys
import random
from particles import ParticleSystem


pygame.init()

clock = pygame.time.Clock()

pygame.key.set_repeat(200, 100)

particle_system = ParticleSystem()
 
fps = 60

screen_width = 500
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tetris")

held_shape = None
held_color = None
shape_held = False
can_store = True
stored_shape = None
stored_color = None
can_store = True

shape_locked = False


# colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (50, 50, 50)
RED = (255, 0, 0)

shape_colors = [
    (0, 255, 255), #
    (255, 165, 0), #
    (0, 0, 255), # Blue
    (255, 0, 0), # Red
    (0, 255, 0), # Green
    (255, 255, 0), # 
    (160, 32, 240) # Purple?
]

random_shape_color = random.randint(0, len(shape_colors) - 1)


print(random_shape_color)

columns = 10
rows = 20
block_size = 30

font = pygame.font.SysFont("Arial", 24)

score = 0

grid = [[0 for _ in range(columns)] for _ in range(rows)]

shapes = [
    [[1, 1, 1,], [0, 1, 0]], # short T
    [[1, 0], [1,0], [1, 1]], # right L
    [[1, 1, 0], [0, 1, 1]], # cube
    [[0, 1], [0, 1], [1, 1]], # left L
    [[1, 0], [1, 1], [1, 0], [1, 0]], # 
    [[1],[1],[1],[1]], # I
    [[0, 1], [1, 1]], #smal L left
]

def draw_grid(surface):
    for row in range(rows):
        for col in range(columns):
            pygame.draw.rect(surface, GREY, (col * block_size, row * block_size, block_size, block_size), 1)

def draw_shape(surface, shape, offset_x, offset_y, color):
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col] == 1:
           
                draw_shadow(surface, offset_x + col * block_size, offset_y + row * block_size, block_size, block_size)

          

         
                overlay = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                overlay.fill(color)
                surface.blit(overlay, (offset_x + col * block_size, offset_y + row * block_size))

                # Draw border
                border_color = (0, 0, 0)
                border_rect = pygame.Rect(offset_x + col * block_size, offset_y + row * block_size, block_size, block_size)
                pygame.draw.rect(surface, border_color, border_rect, 2)




                

                #draw_gradient(surface, offset_x + col * block_size, offset_y + row * block_size, block_size, block_size, color, (0, 0, 0))




def calculate_ghost_position(shape, offset_x, offset_y):
    ghost_y = offset_y
    while True:
        if (ghost_y // block_size) + len(shape) >= rows:
            break
        elif any(grid[(ghost_y // block_size) + row + 1][(offset_x // block_size) + col] != 0
                 for row in range(len(shape))
                 for col in range(len(shape[row]))
                 if shape[row][col] == 1):
            break
        ghost_y += block_size

    return ghost_y


def draw_ghost_piece(surface, shape, offset_x, ghost_y):
    ghost_color = (200, 200, 200)
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col] == 1:
                pygame.draw.rect(surface, ghost_color, (offset_x + col * block_size, ghost_y + row * block_size, block_size, block_size), 1)

def draw_score(surface, score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(topleft=(10, 10))

    pygame.draw.rect(surface, GREY, (score_rect.x - 5, score_rect.y - 5, score_rect.width + 10, score_rect.height + 10))

    surface.blit(score_text, score_rect)

def draw_next_shape(surface, shape, color):
    preview_x = screen_width - 150
    preview_y = 50
    next_text = font.render(f"next shape", True, WHITE)
    next_rect = next_text.get_rect(topleft=(preview_x, preview_y + 135))
    pygame.draw.rect(surface, GREY, (next_rect.x - 5, next_rect.y - 5, next_rect.width + 10, next_rect.height + 10))
    surface.blit(next_text, next_rect)
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col] == 1:
                pygame.draw.rect(surface, color, (preview_x + col * block_size, preview_y + row * block_size, block_size, block_size))

def draw_stored_shape(surface, shape, color):
    stored_x = screen_width - 150
    stored_y = 300
    store_text = font.render(f"stored shape", True, WHITE)
    store_rect = store_text.get_rect(topleft=(stored_x, stored_y + 135))
    pygame.draw.rect(surface, GREY, (store_rect.x - 5, store_rect.y - 5, store_rect.width + 10, store_rect.height + 10))
    surface.blit(store_text, store_rect)
    if stored_shape == None:
        pass
    else:
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] == 1:
                    pygame.draw.rect(surface, color, (stored_x + col * block_size, stored_y + row * block_size, block_size, block_size))


def lock_shape(shape, offset_x, offset_y, color):
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col] == 1:
                grid[(offset_y // block_size) + row][(offset_x // block_size) + col] = color
                
                # Add particles
                for _ in range(5):
                    particle_system.add_particle(
                        (offset_x // block_size + col) * block_size + block_size // 2,
                        (offset_y // block_size + row) * block_size + block_size // 2,
                        color
                    )
                    global can_store
                    can_store = True

def can_rotate(shape, offset_x, offset_y, grid):
    rotated_shape = rotate_shape(shape)

    for row in range(len(rotated_shape)):
        for col in range(len(rotated_shape[row])):
            if rotated_shape[row][col] == 1:
                new_x = (offset_x // block_size) + col
                new_y = (offset_y // block_size) + row

                if new_x < 0 or new_x >= len(grid[0]) or new_y >= len(grid):
                    return False
                
                if grid[new_y][new_x] != 0:
                    return False
                
    return True

 

def draw_main_menu(surface):
    surface.fill(BLACK)
    title_font = pygame.font.SysFont("Arial", 48)
    menu_font = pygame.font.SysFont("Arial", 32)

    title_surface = title_font.render("Tetris", True, WHITE)
    start_surface = menu_font.render("Start Game", True, WHITE)
    exit_surface = menu_font.render("Exit", True, WHITE)
    
    surface.blit(title_surface, (screen_width // 2 - title_surface.get_width() // 2, 150))
    surface.blit(start_surface, (screen_width // 2 - start_surface.get_width() // 2, 250))
    surface.blit(exit_surface, (screen_width // 2 - exit_surface.get_width() // 2, 300))
'''
def handle_main_menu_input():
    global state 
    keys = pygame.ket.get_pressed()

    if keys[pygame.K_RETURN]:
        state = GAME 

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()
'''        



def check_game_over():
    for row in range(len(current_shape)):
        for col in range(len(current_shape[row])):
            if current_shape[row][col] == 1 and grid[row][(offset_x // block_size) + col] != 0:
                return True
    return False


def new_shape():
    index = random.randint(0, len(shapes) - 1)
    shape = shapes[index]
    color = shape_colors[index]
    return shape, color, index 

def draw_shadow(surface, x, y ,width, height):
    shadow_color = (50, 50, 50, 150)
    pygame.draw.rect(surface, shadow_color, (x + 5, y + 5, width, height))

def draw_gradient(surface, x, y, width, height, color1, color2):
    for i in range(height):
        ratio = i / height
        color = (
            int(color1[0] * (1 - ratio) + color2[0] * ratio),
            int(color1[1] * (1 - ratio) + color2[1] * ratio),
            int(color1[2] * (1 - ratio) + color2[2] * ratio),
        )
        pygame.draw.line(surface, color, (x, y + i), (x + width, y + i))



def clear_lines():
    global score

    full_rows = []
    for row in range(rows):
        if all(grid[row][col] != 0 for col in range(columns)):
            full_rows.append(row)

    lines_cleared = len(full_rows)

    if lines_cleared > 0:
        score_increment = [0, 100, 300, 500, 800]
        score += score_increment[lines_cleared]

    for row in full_rows:
        for col in range(columns):
            for _ in range(3):
                particle_system.add_particle(
                    (col * block_size) + (block_size // 2),
                    (row * block_size) + (block_size // 2),
                    grid[row][col]
                )
        
        del grid[row]
        grid.insert(0, [0 for _ in range(columns)])

    return lines_cleared

def draw_held_shape(surface, shape, color):
    if shape is not None:
        preview_x = screen_width - 100
        preview_y = 150
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] == 1:
                    pygame.draw.rect(surface, color, (preview_x + col * block_size, preview_y + row * block_size, block_size, block_size))


def rotate_shape(shape):
    return [list(row) for row in zip(*shape[::-1])]

current_shape, current_color, current_shape_index = new_shape() 


next_shape, next_color, next_shape_index = new_shape()


offset_x = 3 * block_size
offset_y = 0

fall_speed = 1000
last_fall_time = pygame.time.get_ticks()
speed_increase_interval = 10000
start_fall_speed = 1000
speed_multiplier = 0.9
min_fall_speed = 200
shape_speed = block_size
level = 1
lines_cleared_total = 0
lines_per_level = 10

lines_cleared = clear_lines()
if lines_cleared > 0:
    if lines_cleared == 1:
        score += 100
    if lines_cleared == 2:
        score += 300
    if lines_cleared == 3:
        score += 500
    if lines_cleared == 4:
        score += 800

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if offset_x > 0 and not any(grid[(offset_y // block_size) + row][(offset_x // block_size) + col - 1] != 0
                                            for row in range(len(current_shape))
                                            for col in range(len(current_shape[row]))
                                            if current_shape[row][col] == 1):
                    offset_x -= block_size

            if event.key == pygame.K_UP:
                if can_rotate(current_shape, offset_x, offset_y, grid):
                    rotated_shape = rotate_shape(current_shape)

                    if offset_x + len(rotated_shape[0]) * block_size <= screen_width and \
                    offset_y + len(rotated_shape) * block_size <= screen_height and \
                    not any(grid[(offset_y // block_size) + row][(offset_x // block_size) + col] == 1
                            for row in range(len(rotated_shape))
                            for col in range(len(rotated_shape[row]))
                            if rotated_shape[row][col] == 1):
                        current_shape = rotated_shape



            if event.key == pygame.K_RIGHT:
                if offset_x + len(current_shape[0]) * block_size < screen_width:
                    can_move = True
                    for row in range(len(current_shape)):
                        for col in range(len(current_shape[row])):
                            if current_shape[row][col] == 1:
                                new_col = (offset_x // block_size) + col + 1
                                new_row = (offset_y // block_size) + row
                                if new_col >= len(grid[0]) or grid[new_row][new_col] != 0:
                                    can_move = False
                                    break
                        if not can_move:
                            break
                    

                    if can_move:
                        offset_x += block_size

                
            if event.key == pygame.K_DOWN:
                if (offset_y // block_size) + len(current_shape) < rows and \
                not any(grid[(offset_y // block_size) + row + 1][(offset_x // block_size) + col] != 0
                        for row in range(len(current_shape))
                        for col in range(len(current_shape[row]))
                        if current_shape[row][col] == 1):
                    offset_y += block_size
                else:
                    lock_shape(current_shape, offset_x, offset_y, current_color)

                    lines_cleared = clear_lines()
                    current_shape, current_color, current_shape_index = next_shape, next_color, next_shape_index
                    next_shape, next_color, next_shape_index = new_shape()

                    offset_x = 3 * block_size
                    offset_y = 0

            if event.key == pygame.K_SPACE:
                offset_y = calculate_ghost_position(current_shape, offset_x, offset_y)
                lock_shape(current_shape, offset_x, offset_y, current_color)


                lines_cleared = clear_lines()
                current_shape, current_color, current_shape_index = next_shape, next_color, next_shape_index
                next_shape, next_color, next_shape_index = new_shape() 

                offset_x = 3 * block_size
                offset_y = 0

            if event.key == pygame.K_c and can_store:
                if stored_shape is None:

                    stored_shape = current_shape
                    stored_color = current_color
                
                    current_shape, current_color, current_shape_index = new_shape()  
                else:  
                    current_shape, current_color, stored_shape, stored_color = (
                        stored_shape, stored_color, current_shape, current_color
                    )
                    
                can_store = False


    current_time = pygame.time.get_ticks()
    if current_time - last_fall_time > fall_speed:
        offset_y += block_size
        last_fall_time = current_time

        if (offset_y // block_size) + len(current_shape) > rows or \
            any(grid[(offset_y // block_size) + row][(offset_x // block_size) + col] != 0
                for row in range(len(current_shape))
                for col in range(len(current_shape[row]))
                if current_shape[row][col] == 1):
            offset_y -= block_size
            lock_shape(current_shape, offset_x, offset_y, current_color)
            lines_cleared = clear_lines()

           
            current_shape, current_color, current_shape_index = next_shape, next_color, next_shape_index
            next_shape, next_color, next_shape_index = new_shape()
            offset_x = 3 * block_size
            offset_y = 0

            if check_game_over():
                print("Game Over")
                running = False



    if offset_y + len(current_shape) * block_size >= screen_height:
        offset_y = screen_height - len(current_shape) * block_size

    lines_cleared = clear_lines()
    if lines_cleared > 0:
        if lines_cleared == 1:
            score += 100
        if lines_cleared == 2:
            score += 300
        if lines_cleared == 3:
            score += 500
        if lines_cleared == 4:
            score += 800

    if lines_cleared > 0:
        lines_cleared_total += lines_cleared

        if lines_cleared_total >= level * lines_per_level:
            level += 1
            print(f"Level up! Now on level {level}")

        fall_speed = max(start_fall_speed - (level - 1) * 100, min_fall_speed)

    ghost_y = calculate_ghost_position(current_shape, offset_x, offset_y)

    screen.fill(BLACK)

    draw_grid(screen)
    
    particle_system.update()

    particle_system.draw(screen)

    draw_next_shape(screen, next_shape, next_color)


    draw_ghost_piece(screen, current_shape, offset_x, ghost_y)

    draw_shape(screen, current_shape, offset_x, offset_y, current_color)

    draw_next_shape(screen, next_shape, next_color)

        # Draw current shape
    draw_shape(screen, current_shape, offset_x, offset_y, current_color)
    ghost_y = calculate_ghost_position(current_shape, offset_x, offset_y)
    draw_ghost_piece(screen, current_shape, offset_x, ghost_y)

    # Draw the next shape
    draw_next_shape(screen, next_shape, next_color)

    draw_stored_shape(screen, stored_shape,stored_color)

    # Draw score
    draw_score(screen, score)


    """
    if current_time // speed_increase_interval > last_fall_time // speed_increase_interval:
        fall_speed = max(fall_speed * speed_multiplier, min_fall_speed)
    """
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    for row in range(rows):
        for col in range(columns):
            if grid[row][col] != 0:
                pygame.draw.rect(screen, grid[row][col], (col * block_size, row * block_size, block_size, block_size))
                border_color = (0, 0, 0)
                border_rect = pygame.Rect(col * block_size, row * block_size, block_size, block_size)
                pygame.draw.rect(screen, border_color, border_rect, 2)

    """
    if not shape_locked:
        draw_shape(screen, current_shape, offset_x, offset_y, current_color)
    """
    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
sys.exit()