import json as js
import os
import numpy as np
import pygame as pg
import time

# 调试用：打印列表中的每个元素（包裹尖括号）
def list_debug_check(target_list):
    list_length = len(target_list)
    for i in range(0, list_length, 1):
        print("<", target_list[i], ">", " ")
        print("\n")

# 初始化指定维度的二维列表（每个元素是空list）
def list_space_initialize(target_list, dimension):
    for i in range(0, dimension, 1):
        temp = list()
        target_list.append(temp)

# 将谱面 note 的节拍时间（beat）转换为秒（出现时间），并按列分发到 note_storage
# note_storage: [col0:[], col1:[], col2:[], col3:[]]
def note_time_initialize(note_storage, note, screen):
    length = len(note)  # Malody 的 note 数组最后可能带配置项，故这里用 length-1
    s_height = pg.Surface.get_height(screen)

    for i in range(0, length-1, 1):
        # beat: [小节, 拍子分子, 拍子分母]
        # 将 beat 转为“拍数值”：beat_value = measure + beat_num/denominator
        # 然后用 beat_delta(一拍时长)计算出现时间（秒）
        note_appear_time = (note[i]['beat'][0] + note[i]['beat'][1] / note[i]['beat'][2]) * beat_delta
        # 按列编号归档到对应列表
        note_storage[note[i]['column']].append(note_appear_time)

# 计算第一条音符抵达判定线的时间，用于精确触发音乐播放（与下落时间对齐）
def first_note_time_calculate(note, bpm, s_height, fall_speed, beat_delta, offset):
    first_note_beat = note[0]['beat']  # 第一条音符的 beat
    first_note_beat_value = first_note_beat[1] / first_note_beat[2]  # 只取第一条的拍子内分数部分（原逻辑）
    # 出现时间（秒）
    first_note_appear_time = first_note_beat_value * beat_delta
    # 计算从出现到抵达判定线所需时间：（判定线高度=屏幕高度 - 100）
    # 再叠加音频文件的 offset（ms -> s）
    arrival_time = first_note_appear_time + (s_height - 100) / fall_speed + offset / 1000
    return arrival_time

# 为每条音符创建一个矩形（pygame.Rect），用于渲染与位移：
# - 常规 note：高度 10 的短矩形
# - 长条 note：高度为 (endbeat - beat) * beat_delta * fall_speed，初始 y 在屏幕上方
def note_rect_initialize(note, rect_note_storage, screen, column_note_positions, beat_delta, fall_speed):
    length = len(note)
    s_width = pg.Surface.get_width(screen)
    s_height = pg.Surface.get_height(screen)
    note_type = 1  # 1=短note，0=长note

    for i in range(0, length-1, 1):
        # 判断是否为长条（是否有 endbeat）
        if ('endbeat' in note[i]):
            note_type = 0
        else:
            note_type = 1

        if (note_type):
            # 短音符：宽80，高10；初始 y 在可视区域上方
            rect = pg.Rect(0, -110, 80, 10)
            rect.centerx = column_note_positions[note[i]['column']]
            rect_note_storage[note[i]['column']].append(rect)
        else:
            # 长音符：高度与持续时间成正比；初始 y 更高以保证先行预渲染
            head_note_info = note[i]['beat']
            head_note_beat = head_note_info[0] + head_note_info[1] / head_note_info[2]
            end_note_info = note[i]['endbeat']
            end_note_beat = end_note_info[0] + end_note_info[1] / end_note_info[2]
            note_length = (end_note_beat - head_note_beat) * beat_delta * fall_speed
            rect = pg.Rect(0, -100 - note_length, 80, note_length)
            rect.centerx = column_note_positions[note[i]['column']]
            rect_note_storage[note[i]['column']].append(rect)

# 在当前时间窗口内，将“将要出现的音符”加入到 note_current / rect_note_current（活动队列），供渲染
def note_judge(note, note_storage, note_read_sp, rect_note_storage,
               note_current, rect_note_current, current_time, s_height, fall_speed):
    delta_t = s_height / fall_speed  # 屏幕高度对应的时间（秒），用作“预读取窗口”
    for i in range(0, 4, 1):
        length_time_list = len(note_storage[i])
        sp_prev = note_read_sp[i]  # 每列独立的读取指针（避免重复入队）
        for j in range(sp_prev, length_time_list, 1):
            appear_t = note_storage[i][j]
            # 将在预窗口内的音符放入活动队列
            if (appear_t - current_time <= delta_t):
                note_current[i].append(appear_t)
                rect_note_current[i].append(rect_note_storage[i][j])
                note_read_sp[i] += 1
            elif (appear_t - current_time > delta_t):
                break

# 渲染当前队列的音符并计算其 y 坐标（按时间差与速度决定）
# 同时负责清理移出屏幕的音符
def note_draw(note, note_storage, note_read_sp, rect_note_storage,
              note_current, rect_note_current, note_duration_time, screen, fall_speed):
    s_height = pg.Surface.get_height(screen)
    current_time = pg.time.get_ticks() / 1000.0 - start_time

    # 先将“将到达的”音符加入渲染队列
    note_judge(note, note_storage, note_read_sp, rect_note_storage,
               note_current, rect_note_current, current_time, s_height, fall_speed)

    # 对每列进行逐条渲染与位置更新
    for i in range(0, 4, 1):
        j = 0
        while j < len(rect_note_current[i]):
            rect_note = rect_note_current[i][j]
            note_time = note_current[i][j]

            if (rect_note.y <= s_height):
                time_diff = note_time - current_time  # 距出现（抵线）的剩余时间（秒）
                # 用背景色覆盖上次渲染残留（避免拖影）
                pg.draw.rect(screen, (30, 30, 30), rect_note, 0)

                # 如果是长条且玩家已按下（note_duration_time 非 0），让头部对齐判定线
                if (rect_note.height > 10 and note_duration_time[i] != 0):
                    rect_note.y = (s_height - 100) - rect_note.height
                else:
                    # 常规：y = 判定线相对位置 - time_diff * 速度
                    rect_note.y = (s_height - 100) - rect_note.height - time_diff * fall_speed

                # 只在可见窗口内才实际绘制（长条需要提前预渲染避免抖动/错误）
                if (time_diff >= -s_height / fall_speed):
                    pg.draw.rect(screen, 'white', rect_note, 0)
                j += 1

            elif (rect_note.y > s_height):
                # 移出屏幕则从活动队列删除（未按到的短条自然判为 miss 在按键判定里处理）
                del note_current[i][j]
                del rect_note_current[i][j]

# 判定等级与 combo 变化：根据时间偏差（ms）
# rank_level_judge: [Perfect, Good, Bad, Miss] 的累计计数
def rank_judge(judge_time_diff, key_use, screen, note_current, rect_note_current, rank_level_judge, combo):
    if (judge_time_diff <= 50):
        rank_level_judge[0] += 1
        combo += 1
        pg.draw.rect(screen, (30, 30, 30), rect_note_current[key_use][0], 0)
    elif (judge_time_diff <= 80):
        rank_level_judge[1] += 1
        combo += 1
        pg.draw.rect(screen, (30, 30, 30), rect_note_current[key_use][0], 0)
    elif (judge_time_diff <= 120):
        rank_level_judge[2] += 1
        combo = 0
        pg.draw.rect(screen, (30, 30, 30), rect_note_current[key_use][0], 0)
    else:
        rank_level_judge[3] += 1
        combo = 0
        pg.draw.rect(screen, (30, 30, 30), rect_note_current[key_use][0], 0)

# 键盘按压/释放判定（短 note 判一次、长 note 进入“锁定”并消耗高度）
# keyboard_statement: 0=按下，1=抬起
def note_keyboard_judge(keyboard_statement, keyboard_input, screen,
                        column_statement, column_lock_clock, note_duration_time,
                        note_current, rect_note_current, start_time, fall_speed,
                        rank_level_judge, combo):
    mapping_table = {
        pg.K_a: 0,
        pg.K_s: 1,
        pg.K_k: 2,
        pg.K_l: 3
    }
    if keyboard_input in mapping_table:
        key_use = mapping_table[keyboard_input]
    else:
        return

    s_height = pg.Surface.get_height(screen)
    current_time = pg.time.get_ticks() / 1000.0 - start_time

    if (keyboard_statement == 1):  # 键盘抬起：如果是长条锁定，释放并结算
        if (column_lock_clock[key_use] != 0):
            # 若提前松手（剩余长条时间 > 0.1s），则断 combo
            if (note_duration_time[key_use] - current_time >= 0.1):
                combo = 0
            # 从活动队列删除该条（结束长条）
            del note_current[key_use][0]
            del rect_note_current[key_use][0]
            column_lock_clock[key_use] = 0
        column_statement[key_use] = 1
        note_duration_time[key_use] = 0

    elif (keyboard_statement == 0):  # 键盘按下：短条直接判定，长条进入锁定
        # 若该列当前无可判定音符或音符尚未下落至判定区域（屏幕中上半部分），直接返回
        if (not len(rect_note_current[key_use])):
            return
        if (rect_note_current[key_use][0].y + rect_note_current[key_use][0].height <= s_height / 2):
            return

        if (rect_note_current[key_use][0].height == 10):
            # 短条：按下瞬间用当前时间差判定，删除队列元素
            judge_time_diff = np.fabs(note_current[key_use][0] - current_time) * 1000.0  # 转 ms 更直观
            rank_judge(judge_time_diff, key_use, screen, note_current, rect_note_current, rank_level_judge, combo)
            del note_current[key_use][0]
            del rect_note_current[key_use][0]
            column_statement[key_use] = 0
        elif (rect_note_current[key_use][0].height > 10):
            # 长条：记录需要“消耗”的总时长、锁定开始时间，后续在 long_note_height_change 持续缩短高度
            judge_time_diff = np.fabs(note_current[key_use][0] - current_time) * 1000.0
            note_duration_time[key_use] = rect_note_current[key_use][0].height / fall_speed
            column_lock_clock[key_use] = current_time
            rank_judge(judge_time_diff, key_use, screen, note_current, rect_note_current, rank_level_judge, combo)

# 长条在按住期间的高度消耗逻辑：以时间差 * 速度减少高度，直到 <=10 视为尾部到达
def long_note_height_change(key_use, screen, column_statement, column_lock_clock,
                            note_duration_time, note_current, rect_note_current, start_time, fall_speed):
    current_time = pg.time.get_ticks() / 1000.0 - start_time
    if (rect_note_current[key_use][0].height > 10):
        press_time = current_time - column_lock_clock[key_use]
        rect_note_current[key_use][0].height -= press_time * fall_speed
    elif (rect_note_current[key_use][0].height <= 10):
        # 长条消耗完成：清空状态并从活动队列删除
        note_duration_time[key_use] = 0
        column_lock_clock[key_use] = 0
        del note_current[key_use][0]
        del rect_note_current[key_use][0]


# ========= 全局数据结构初始化 =========

note_storage = list()          # 各列的音符出现时间（秒）列表
list_space_initialize(note_storage, 4)
rect_note_storage = list()     # 各列的预生成 Rect 列表（与 note_storage 对齐）
list_space_initialize(rect_note_storage, 4)

note_current = list()          # 当前窗口已入队的音符时间（秒），按列
list_space_initialize(note_current, 4)
rect_note_current = list()     # 当前窗口已入队的 Rect，按列
list_space_initialize(rect_note_current, 4)

note_read_sp = [0, 0, 0, 0]    # 每列读取指针，避免重复入队
column_statement = [0, 0, 0, 0]
column_lock_clock = [0, 0, 0, 0]
note_duration_time = [0, 0, 0, 0]  # 每列长条的总需消耗时长（秒）
rank_level_judge = [0, 0, 0, 0]    # 判定统计：Perfect/Good/Bad/Miss
combo = 0
fall_speed = 650               # 下落速度（像素/秒）
offset = 300                   # 音频偏移（ms）

pg.init()  # pygame 初始化

# 寻找当前目录下的谱面（json）与音频（ogg）
root = os.getcwd()
path = os.listdir(root)
file_play = list()
song_player = list()
song_player_name = list()

for p in path:
    file = os.path.splitext(p)
    if (file[1] == '.json'):
        file_play.append(p)
    elif (file[1] == '.ogg'):
        song_player.append(p)
        song_player_name.append(file[0])

file_choose = file_play[1]  # 选用的谱面文件（可改）
with open(file_choose, 'r', encoding='utf-8') as file:
    get_content = js.load(file)

bpm = get_content['time'][0]['bpm']  # BPM
beat_delta = 60.0 / bpm              # 一拍时长：秒
note = get_content['note']           # 谱面 note 列表

# 找到匹配歌曲音频（根据 meta.song.title 比对 .ogg 文件名）
title_song = get_content['meta']['song']['title']
for i in range(0, len(song_player), 1):
    if (song_player_name[i] == title_song):
        pg.mixer.music.load(song_player[i])
        break

# 画面与列布局
screen_size = [(800, 600), (1280, 760), (1920, 1080)]
size_select = 0
screen = pg.display.set_mode(screen_size[size_select])

background = pg.Surface(screen.get_size())
background.fill((30, 30, 30))
s_width = pg.Surface.get_width(screen)
s_height = pg.Surface.get_height(screen)

# 判定线垂直分割线（用于参考）
column_line_positions = [
    s_width / 2 - 3 * 50,
    s_width / 2 - 1 * 50,
    s_width / 2 + 1 * 50,
    s_width / 2 + 3 * 50,
    s_width / 2 + 5 * 50
]
# 每列音符的中心 x 坐标（与上面的线错位，便于可视）
column_note_positions = [
    s_width / 2 - 3 * 50,
    s_width / 2 - 1 * 50,
    s_width / 2 + 1 * 50,
    s_width / 2 + 3 * 50
]
keyboard_map_use = [pg.K_a, pg.K_s, pg.K_k, pg.K_l]

# 计算音乐播放的精确起点（让第一条音符到判定线时音乐刚好开始）
first_arrival_time = first_note_time_calculate(note, bpm, s_height, fall_speed, beat_delta, offset)
# 初始化时间与 Rect 数据
note_time_initialize(note_storage, note, screen)
note_rect_initialize(note, rect_note_storage, screen, column_note_positions, beat_delta, fall_speed)

clock = pg.time.Clock()
isRunning = True
music_play_flag = False
start_time = pg.time.get_ticks() / 1000.0  # 记录启动时间（秒）

# ========= 主循环 =========
while isRunning:
    for ev in pg.event.get():
        if (ev.type == pg.QUIT):
            isRunning = False
            break
        if (ev.type == pg.KEYDOWN):
            if (ev.key == pg.K_ESCAPE):
                isRunning = False
                break
        # 按下/抬起事件进入键盘判定
        if (ev.type == pg.KEYDOWN):
            note_keyboard_judge(0, ev.key, screen, column_statement, column_lock_clock,
                                note_duration_time, note_current, rect_note_current,
                                start_time, fall_speed, rank_level_judge, combo)
        if (ev.type == pg.KEYUP):
            note_keyboard_judge(1, ev.key, screen, column_statement, column_lock_clock,
                                note_duration_time, note_current, rect_note_current,
                                start_time, fall_speed, rank_level_judge, combo)

    # 到达第一条音符应抵达的时刻，播放音乐（一次性）
    if (pg.time.get_ticks() / 1000 - start_time >= first_arrival_time and not music_play_flag):
        pg.mixer.music.play()
        music_play_flag = True

    # 背景
    screen.blit(background, (0, 0))

    # 列分割线
    for pos in column_line_positions:
        pg.draw.line(screen, (100, 100, 100), (pos - 50, 0), (pos - 50, s_height), 2)

    # 判定线（音符应该抵达的位置，底部向上 100px）
    pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)

    # 按住长条时，持续消耗高度
    for i in range(0, 4):
        if (column_lock_clock[i]):
            long_note_height_change(i, screen, column_statement, column_lock_clock,
                                    note_duration_time, note_current, rect_note_current,
                                    start_time, fall_speed)

    # 渲染音符并更新位置/清除离屏
    note_draw(note, note_storage, note_read_sp, rect_note_storage,
              note_current, rect_note_current, note_duration_time,
              screen, fall_speed)

    pg.display.update()
    clock.tick(100)  # 100 FPS

pg.quit()
# 主程序结束