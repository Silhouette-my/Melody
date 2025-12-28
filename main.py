import pygame
import time
import json
import os

# 引入你已有的模块
import main_interface       # 主菜单
import song_selection       # 选曲界面
import play_interface_version2 as play  # 游戏逻辑（推荐用 version2）

# ======================
# 1. 场景状态机
# ======================
STATE_MENU = "menu"
STATE_SELECT = "select"
STATE_PLAY = "play"
STATE_RESULT = "result"

def main():
    state = STATE_MENU
    selected_song = None

    while True:
        if state == STATE_MENU:
            # 调用主菜单界面
            screen = pygame.display.set_mode((800, 600))
            font = pygame.font.SysFont(None, 50)
            text_rect = main_interface.screen_interface(screen, font)
            last_rect = main_interface.button_border_draw(screen, text_rect, 0)

            running = True
            while running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:  # Enter 进入选曲
                            state = STATE_SELECT
                            running = False
                        # 上下键移动菜单
                        elif ev.key == pygame.K_DOWN or ev.key == pygame.K_UP:
                            pass
                            # TODO
                pygame.display.update()

        elif state == STATE_SELECT:
            # 调用选曲界面
            screen = pygame.display.set_mode((800, 600))
            clock = pygame.time.Clock()
            title_flag = 0
            running = True
            while running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:
                            # 确认选曲
                            selected_song = song_selection.file_play[title_flag]
                            state = STATE_PLAY
                            running = False
                        elif ev.key == pygame.K_DOWN:
                            title_flag = min(title_flag+1, len(song_selection.file_play)-1)
                        elif ev.key == pygame.K_UP:
                            title_flag = max(title_flag-1, 0)
                screen.fill((0,0,0))
                song_selection.text_draw(title_flag, pygame.font.SysFont(None,50), (800,600), 0)
                song_selection.attention_draw(screen,(800,600),0)
                pygame.display.update()
                clock.tick(60)

        elif state == STATE_PLAY:
            # 调用游戏逻辑 前往 play_interface
            play.run_game(selected_song)  # 你需要在 play_interface_version2.py 里写一个 run_game(file_path)
            state = STATE_RESULT

        elif state == STATE_RESULT:
            # 简单结果界面
            screen = pygame.display.set_mode((800, 600))
            font = pygame.font.SysFont(None, 50)
            text = font.render("Game Over - Press Enter to return", True, 'white')
            rect = text.get_rect(center=(400,300))
            screen.blit(text, rect)
            pygame.display.update()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return
                    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                        state = STATE_MENU
                        waiting = False

if __name__ == "__main__":
    main()