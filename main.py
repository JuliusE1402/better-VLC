import pygame
import sys
from mutagen.mp3 import MP3
from tkinter import Tk, filedialog

RESOLUTION = (900, 600)
SLIDER_POS = (30, 140)
SLIDER_SIZE = (200, 10)
HANDLE_RADIUS = 15
TIME_BAR_POS = (30, 200)
WHITE = (255, 255, 255)
COLOR_LIGHT = (170, 170, 170)
BUTTON_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (31, 52, 56)
FONT_NAME = 'Corbel'
FONT_SIZE = 35

pygame.init()

icon = pygame.image.load('icon.png')
screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
pygame.display.set_caption("better VLC https://github.com/JuliusE1402")
pygame.display.set_icon(icon)
smallfont = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

current_volume = 0.5
initial_handle_x = SLIDER_POS[0] + current_volume * SLIDER_SIZE[0]
handle_pos = pygame.Vector2(initial_handle_x, SLIDER_POS[1])
audio = None
track_length = 0
pause = False
dragging = False
new_time_pos = 0
current_time_seconds = 0

pygame.mixer.music.set_volume(current_volume)

def play_track():
    global pause, current_time_seconds, new_time_pos
    if audio and not pause:
        current_time_seconds = 0
        new_time_pos = 0
        pygame.mixer.music.play(start=0)
    else:
        pygame.mixer.music.unpause()
        pause = False

def stop_track():
    global pause
    pygame.mixer.music.pause()
    pause = True

def select_file():
    global audio, track_length, pause, new_time_pos
    pygame.mixer.music.stop()
    Tk().withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        audio = MP3(file_path)
        track_length = audio.info.length
        pygame.mixer.music.load(file_path)
        pause = False
        new_time_pos = 0
        pygame.mixer.music.play(0)

def update_volume(pos):
    global current_volume
    current_volume = (pos - SLIDER_POS[0]) / SLIDER_SIZE[0]
    pygame.mixer.music.set_volume(current_volume)

def draw_interface():
    screen.fill(BACKGROUND_COLOR)
    draw_buttons()
    draw_time_bar()
    draw_volume_slider()
    pygame.display.update()

def draw_buttons():
    mouse = pygame.mouse.get_pos()
    width, height = screen.get_size()

    # Play/Stop button
    if width / 2 - 70 <= mouse[0] <= width / 2 + 70 and height / 1.25 <= mouse[1] <= height / 1.25 + 40:
        pygame.draw.rect(screen, COLOR_LIGHT, [width / 2 - 70, height / 1.25, 140, 40])
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, [width / 2 - 70, height / 1.25, 140, 40])

    if pygame.mixer.music.get_busy():
        text = smallfont.render("Stop", True, WHITE)
    else:
        text = smallfont.render("Play", True, WHITE)
    screen.blit(text, (width / 2 - 30, height / 1.25 + 5))

    # File select button
    if 30 <= mouse[0] <= 180 and 30 <= mouse[1] <= 70:
        pygame.draw.rect(screen, COLOR_LIGHT, [30, 30, 150, 40])
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, [30, 30, 150, 40])
    select_file_text = smallfont.render("Select File", True, WHITE)
    screen.blit(select_file_text, (35, 35))

def draw_time_bar():
    if audio:
        current_time_seconds = new_time_pos + max(pygame.mixer.music.get_pos() / 1000.0, 0)
        minutes = int(current_time_seconds // 60)
        seconds = int(current_time_seconds % 60)
        total_length = screen.get_width()
        current_length = (current_time_seconds / track_length) * total_length if track_length > 0 else 0
        pygame.draw.rect(screen, BUTTON_COLOR, [0, RESOLUTION[1] - 50, current_length, 50])
        time_text = smallfont.render(f'{minutes:02}:{seconds:02}', True, WHITE)
        screen.blit(time_text, (10, RESOLUTION[1] - 50))

def draw_volume_slider():
    pygame.draw.rect(screen, COLOR_LIGHT, (*SLIDER_POS, *SLIDER_SIZE))
    pygame.draw.circle(screen, BUTTON_COLOR, (int(handle_pos.x), int(handle_pos.y + SLIDER_SIZE[1]/2)), HANDLE_RADIUS)
    volume_text = smallfont.render("Volume:", True, WHITE)
    screen.blit(volume_text, (30, 90))

def check_click_on_time_bar(mouse_pos):
    global new_time_pos
    x, y = mouse_pos
    if y > RESOLUTION[1] - 50:
        percentage = x / RESOLUTION[0]
        new_time_pos = percentage * track_length
        pygame.mixer.music.play(start=new_time_pos)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        width, height = screen.get_size()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Play/Stop button
            if width / 2 - 70 <= mouse_x <= width / 2 + 70 and height / 1.25 <= mouse_y <= height / 1.25 + 40:
                if pygame.mixer.music.get_busy():
                    stop_track()
                else:
                    play_track()
            # File select button
            elif 30 <= mouse_x <= 180 and 30 <= mouse_y <= 70:
                select_file()
            # time bar
            elif mouse_y > RESOLUTION[1] - 50:
                check_click_on_time_bar((mouse_x, mouse_y))
            # Volume slider
            if handle_pos.distance_to((mouse_x, mouse_y)) <= HANDLE_RADIUS:
                dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        if dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            handle_pos.x = max(SLIDER_POS[0], min(mouse_x, SLIDER_POS[0] + SLIDER_SIZE[0]))
            update_volume(handle_pos.x)

    draw_interface()
    clock.tick(60)

pygame.quit()

