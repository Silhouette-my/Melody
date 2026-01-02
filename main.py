import pygame
import time
import json
import os
import sys

# 引入你已有的模块
import main_interface       # 主菜单
import song_selection       # 选曲界面
import setting              # 设置
import play_interface_version2_no_text as play  # ?????no_text?
import shared_state

# ======================
# 1. 场景状态机
# ======================
STATE_MENU = "menu"
STATE_SELECT = "select"
STATE_PLAY = "play"
STATE_RESULT = "result"
STATE_SETTING= "setting"

# 屏幕参数

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont(None, 50)
    state = STATE_MENU
    selected_song = None
    master_volume = 1.0
    current_latency = 0
    screen_size = (800, 600)
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(master_volume)
    shared_state.MASTER_VOLUME = master_volume

    while True:
        if state == STATE_MENU:
            # 调用主菜单界面       
            screen.fill((0, 0, 0))
            text_rect = main_interface.screen_interface(screen, font)
            last_rect = main_interface.button_border_draw(screen, text_rect, 0)
            selected_index = 0
            esc_hold_start = None
            esc_short_action = None

            running = True
            while running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:  # Enter 进入选曲
                            if selected_index == 0:
                                state = STATE_SELECT
                                running = False
                            elif selected_index == 1:
                                state = STATE_SETTING
                                running = False
                            elif selected_index == 2:
                                return
                        elif ev.key == pygame.K_ESCAPE:
                            esc_hold_start = pygame.time.get_ticks()
                            esc_short_action = "quit"
                        # 上下键移动菜单
                        elif ev.key == pygame.K_DOWN or ev.key == pygame.K_UP:
                            if ev.key == pygame.K_DOWN and selected_index < len(text_rect) - 1:
                                main_interface.button_border_clear(screen, last_rect)
                                selected_index += 1
                                last_rect = main_interface.button_border_draw(screen, text_rect, selected_index)
                            elif ev.key == pygame.K_UP and selected_index > 0:
                                main_interface.button_border_clear(screen, last_rect)
                                selected_index -= 1
                                last_rect = main_interface.button_border_draw(screen, text_rect, selected_index)
                    elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
                        if esc_hold_start is not None and pygame.time.get_ticks() - esc_hold_start < 2000:
                            return
                        esc_hold_start = None
                        esc_short_action = None
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and esc_hold_start is not None:
                    if pygame.time.get_ticks() - esc_hold_start >= 2000:
                        pygame.quit()
                        sys.exit()
                elif not keys[pygame.K_ESCAPE]:
                    esc_hold_start = None
                pygame.display.update()

        elif state == STATE_SELECT:
            # 调用选曲界面    
            clock = pygame.time.Clock()
            title_flag = 0
            running = True
            esc_hold_start = None
            esc_short_action = None
            while running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:
                            # 确认选曲
                            selected_song = song_selection.file_play[title_flag]
                            state = STATE_PLAY
                            running = False
                        elif ev.key == pygame.K_ESCAPE:
                            esc_hold_start = pygame.time.get_ticks()
                            esc_short_action = "back"
                        elif ev.key == pygame.K_DOWN:
                            title_flag = min(title_flag+1, len(song_selection.file_play)-1)
                        elif ev.key == pygame.K_UP:
                            title_flag = max(title_flag-1, 0)
                    elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
                        if esc_hold_start is not None and pygame.time.get_ticks() - esc_hold_start < 2000:
                            state = STATE_MENU
                            running = False
                        esc_hold_start = None
                        esc_short_action = None
                screen.fill((0,0,0))
                song_selection.text_draw(title_flag, pygame.font.SysFont(None,50), screen_size, 0)
                song_selection.attention_draw(screen,screen_size,0)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and esc_hold_start is not None:
                    if pygame.time.get_ticks() - esc_hold_start >= 2000:
                        pygame.quit()
                        sys.exit()
                elif not keys[pygame.K_ESCAPE]:
                    esc_hold_start = None
                pygame.display.update()
                clock.tick(60)

        elif state == STATE_SETTING:
            settings = setting.run_settings(master_volume, current_latency, screen_size)
            if isinstance(settings, dict):
                if "master_volume" in settings:
                    master_volume = settings["master_volume"]
                    shared_state.MASTER_VOLUME = master_volume
                if "latency_ms" in settings:
                    current_latency = settings["latency_ms"]
                if "screen_size" in settings:
                    screen_size = settings["screen_size"]
            pygame.init()
            screen = pygame.display.set_mode(screen_size)
            font = pygame.font.SysFont(None, 50)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(master_volume)
            state = STATE_MENU
        elif state == STATE_PLAY:
            # 调用游戏逻辑 前往 play_interface
            master_volume = shared_state.MASTER_VOLUME
            result = play.run_game(selected_song, master_volume, current_latency, screen_size)
            if pygame.mixer.get_init():
                master_volume = pygame.mixer.music.get_volume()
                shared_state.MASTER_VOLUME = master_volume
            if result == "restart":
                continue
            pygame.init()
            screen = pygame.display.set_mode(screen_size)
            font = pygame.font.SysFont(None, 50)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(master_volume)
            state = STATE_RESULT

        elif state == STATE_RESULT:
            # 简单结果界面
            font = pygame.font.SysFont(None, 50)
            text = font.render("Game Over - Press Enter to return", True, 'white')
            rect = text.get_rect(center=screen.get_rect().center)
            screen.blit(text, rect)
            pygame.display.update()
            waiting = True
            esc_hold_start = None
            esc_short_action = None
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                        state = STATE_MENU
                        waiting = False
                    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        esc_hold_start = pygame.time.get_ticks()
                        esc_short_action = "back"
                    elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
                        if esc_hold_start is not None and pygame.time.get_ticks() - esc_hold_start < 2000:
                            state = STATE_MENU
                            waiting = False
                        esc_hold_start = None
                        esc_short_action = None
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and esc_hold_start is not None:
                    if pygame.time.get_ticks() - esc_hold_start >= 2000:
                        pygame.quit()
                        sys.exit()
                elif not keys[pygame.K_ESCAPE]:
                    esc_hold_start = None

if __name__ == "__main__":
    main()
