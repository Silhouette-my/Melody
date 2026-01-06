import json as js
import os
import numpy as np
import pygame as pg
import pause_interface
import time

# 添加全局变量用于文字显示
display_text = None
combo = 0
text_display_start_time = 0
TEXT_DISPLAY_DURATION = 0.2  # 文字显示0.5秒
TEXT_WINDOW_PERIOD = 0.05     # 文字窗口期，窗口期内不改变显示的文字

# 记分器全局变量
score = 0
max_combo = 0
judge_weight = [100, 50, 20, 10]  # 不同评价的分数
time_offset_sec = 0.0
last_combo_time = 0  # 上次连击变化的时间
rank_level_judge = [0, 0, 0, 0]  # 不同等级统计，perfect,good,bad,miss

def list_debug_check(target_list):
    list_length = len(target_list)
    for i in range(0,list_length,1):
        print("<",target_list[i],">"," ")
        print("\n")
#

def rank_check(rank_level_judge,last_time,start_time):
    current_time = pg.time.get_ticks()/1000 - start_time + time_offset_sec
    if(current_time - last_time >= 0.5):
        print(rank_level_judge)
        return current_time
    else:
        return last_time
#

def end_judge(note,note_read_sp):
    """判断游戏是否结束：检查所有音符是否都已处理"""
    length_sum = len(note)-1
    use_sum = 0
    for i in range(0,4,1):
        use_sum += note_read_sp[i]
    if(use_sum == length_sum):
        return 1
    else:
        return 0
#

def list_space_initialize(target_list,dimension):
    """初始化二维列表：创建dimension个空列表"""
    for i in range(0,dimension,1):
        temp = list()
        target_list.append(temp)
#

def note_time_initialize(note_storage,note,screen):
    """初始化音符时间存储：将每个音符的出现时间按列存储"""
    length = len(note) #note的个数+1(Malody的note信息里面多了一个配置信息)
    s_height = pg.Surface.get_height(screen) #获取窗口宽度

    for i in range(0,length-1,1):
        note_appear_time = (note[i]['beat'][0]+note[i]['beat'][1]/note[i]['beat'][2])*beat_delta
        note_storage[note[i]['column']].append(note_appear_time)
#

def first_note_time_calculate(note,bpm,s_height,fall_speed,beat_delta,offset):
    """计算第一个音符到达判定线的时间"""
    first_note_beat = note[0]['beat']  # 获取第一个note的拍数信息
    first_note_beat_value = first_note_beat[1]/first_note_beat[2]
    # 转换为时间
    first_note_appear_time = first_note_beat_value * beat_delta  # note出现的时间
    # 计算到达判定线的时间
    arrival_time = first_note_appear_time + (s_height-100)/fall_speed + offset/1000
    return arrival_time
#

def note_rect_initialize(note,rect_note_storage,screen,column_note_positions,beat_delta,fall_speed):
    """初始化音符矩形：根据音符信息创建对应的矩形对象"""
    length = len(note)
    s_width = pg.Surface.get_width(screen)
    s_height = pg.Surface.get_height(screen)
    note_type = 1

    for i in range(0,length-1,1):
        if('endbeat' in note[i]):
            note_type = 0
        else:
            note_type = 1
        if(note_type): # 普通音符
            rect = pg.Rect(0,-110,80,10) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
            rect.centerx = column_note_positions[note[i]['column']] #矩形中心横坐标
            rect_note_storage[note[i]['column']].append(rect)
        elif(not note_type): # 长条音符
            head_note_info = note[i]['beat']
            head_note_beat = head_note_info[0] + head_note_info[1]/head_note_info[2]
            end_note_info = note[i]['endbeat'] #获取长条结尾note
            end_note_beat = end_note_info[0] + end_note_info[1]/end_note_info[2] #计算长条结尾note拍数
            note_length = (end_note_beat - head_note_beat)*beat_delta*fall_speed #计算长条长度
            rect = pg.Rect(0,-100-note_length,80,note_length) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
            rect.centerx = column_note_positions[note[i]['column']] #矩形中心横坐标
            rect_note_storage[note[i]['column']].append(rect)
#

def note_judge(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,current_time,s_height,fall_speed):
    """音符判定：检查哪些音符应该进入当前可见区域"""
    delta_t = s_height/fall_speed # 音符从出现到到达判定线所需时间
    for i in range(0,4,1):
        length_time_list = len(note_storage[i])
        sp_prev = note_read_sp[i] # 该列已读取的音符索引
        for j in range(sp_prev,length_time_list,1):
            note = note_storage[i][j]
            if(note-current_time <= delta_t): # 如果音符应该进入屏幕
                note_current[i].append(note) # 添加到当前时间列表
                rect_note_current[i].append(rect_note_storage[i][j]) # 添加到当前矩形列表
                note_read_sp[i] += 1 # 更新已读取索引
            elif(note-current_time > delta_t): # 如果音符还没到出现时间
                break
#

def note_draw(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,rect_upper_note_current,note_duration_time,column_statement,column_lock_clock,screen,fall_speed):
    """绘制音符：更新音符位置并绘制到屏幕上"""
    global display_text, text_display_start_time, combo, rank_level_judge
    s_height = pg.Surface.get_height(screen)
    current_time = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec
    # 首先判定哪些音符应该进入当前可见区域
    note_judge(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,current_time,s_height,fall_speed)
    for i in range(0,4,1):
        j = 0
        while j < len(rect_note_current[i]):
            # 安全检查
            if j >= len(rect_note_current[i]):
                break
                
            rect_note = rect_note_current[i][j]
            note_time = note_current[i][j]
            
            if rect_note.y <= s_height:
                time_diff = note_time - current_time
                
                # 清除旧位置
                pg.draw.rect(screen, (30, 30, 30), rect_note, 0)
                
                if rect_note.height > 10 and note_duration_time[i] > 0 and j == 0:
                    # 处理被按下的长条
                    # 计算从按压开始到现在的总时间
                    elapsed_press_time = current_time - column_lock_clock[i]
                    column_lock_clock[i] = current_time
                    new_rect, ended = long_note_height_change(i, rect_note, elapsed_press_time, fall_speed)
                    
                    if ended:
                        # 长条结束
                        del note_current[i][j]
                        del rect_note_current[i][j]
                        note_duration_time[i] = 0
                        column_lock_clock[i] = 0
                        column_statement[i] = 1
                        continue
                    else:
                        # 更新长条
                        rect_note_current[i][j] = new_rect
                        rect_note = new_rect
                else:
                    # 普通音符或未被按下的长条
                    rect_note.y = (s_height - 100) - rect_note.height - time_diff * fall_speed
                
                # 绘制
                if time_diff >= -s_height/fall_speed:
                    pg.draw.rect(screen, 'white', rect_note, 0)
                
                j += 1
            else:
                # 音符已超出屏幕
                rank_level_judge[3] += 1
                combo = 0
                display_text = 'miss'
                text_display_start_time = current_time
                
                del note_current[i][j]
                del rect_note_current[i][j]
                
                if rect_note.height > 10:
                    note_duration_time[i] = 0
                    column_lock_clock[i] = 0
                    column_statement[i] = 1
#

def rank_judge(judge_time_diff,key_use,screen,note_current,rect_note_current,current_time,lock_time,rank_level_judge):
    """评价判定：根据时间差判定perfect/good/bad/miss"""
    global display_text, text_display_start_time, combo, score, max_combo
    # 检查是否在窗口期内，如果是则保持原有文字不改变
    current_display_time = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec
    text_change = True
    if display_text is not None and (current_display_time - text_display_start_time) < TEXT_WINDOW_PERIOD:
        text_change = False  # 窗口期内不改变文字
    if(judge_time_diff <= 50/1000):
        rank_level_judge[0] += 1
        combo += 1
        score += judge_weight[0] + combo * 10  # 计算perfect分数
        pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
        if text_change:
            display_text = 'perfect'
            text_display_start_time = current_display_time
    elif(judge_time_diff <= 80/1000):
        rank_level_judge[1] += 1
        combo += 1
        score += judge_weight[1] + combo * 5  # 计算good分数
        pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
        if text_change:
            display_text = 'good'
            text_display_start_time = current_display_time
    elif(judge_time_diff <= 120/1000):
        rank_level_judge[2] += 1
        combo = 0
        score += judge_weight[2]  # 计算bad分数
        pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
        if text_change:
            display_text = 'bad'
            text_display_start_time = current_display_time
    else:
        rank_level_judge[3] += 1
        combo = 0
        score += judge_weight[3]  # 计算miss分数
        pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
        if text_change:
            display_text = 'miss'
            text_display_start_time = current_display_time
    
    # 更新最大连击数
    if combo > max_combo:
        max_combo = combo
#

def note_keyboard_judge(keyboard_statement,keyboard_input,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,lock_time,start_times,fall_speed,rank_level_judge):
    """键盘事件处理：处理按键按下和释放事件"""
    global combo, score
    mapping_table = {pg.K_a: 0,
                     pg.K_s: 1,
                     pg.K_k: 2,
                     pg.K_l: 3}
    if keyboard_input in mapping_table:
        key_use = mapping_table[keyboard_input]
    else:
        return

    s_height = pg.Surface.get_height(screen)
    rank_time_diff = [50,80,120,200]
    current_time = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec	

    if(keyboard_statement == 0):
        if(not len(rect_note_current[key_use])): # 如果该轨道没有音符
            return
        if(rect_note_current[key_use][0].y+rect_note_current[key_use][0].height <= s_height/2): # 如果音符还没到判定区域
            return
        if(rect_note_current[key_use][0].height == 10): # 普通音符
            judge_time_diff = np.fabs(note_current[key_use][0]-current_time) # 计算时间差
            rank_judge(judge_time_diff,key_use,screen,note_current,rect_note_current,current_time,lock_time,rank_level_judge)
            # 删除已判定的音符
            if(len(note_current[key_use]) > 0):
                del note_current[key_use][0]
            if(len(rect_note_current[key_use]) > 0):
                del rect_note_current[key_use][0]
            column_statement[key_use] = 0 # 重置轨道状态

        elif(rect_note_current[key_use][0].height > 10): # 长条音符
            judge_time_diff = np.fabs(note_current[key_use][0]-current_time)
            note_duration_time[key_use] = rect_note_current[key_use][0].height/fall_speed # 计算长条持续时间
            column_lock_clock[key_use] = current_time # 记录按压开始时间
            rank_judge(judge_time_diff,key_use,screen,note_current,rect_note_current,current_time,lock_time,rank_level_judge)
    elif(keyboard_statement == 1): # 按键释放事件
        if(column_lock_clock[key_use] != 0): # 如果之前有按压长条
            if(len(rect_note_current[key_use]) > 0 and rect_note_current[key_use][0].height > 10): 
                if(note_duration_time[key_use]-current_time > 0.1): # 如果提前释放长条
                    combo = 0 # 连击中断
                # 删除长条音符
                if(len(note_current[key_use]) > 0):
                    del note_current[key_use][0]
                if(len(rect_note_current[key_use]) > 0):
                    del rect_note_current[key_use][0]
                note_duration_time[key_use] = 0 # 重置持续时间
                column_lock_clock[key_use] = 0 # 重置锁定时间
                column_statement[key_use] = 1 # 设置轨道状态
#

def long_note_height_change(col_idx, rect_note, elapsed_press_time, fall_speed):
    """长条音符高度变化：根据按压时间缩短长条长度"""
    if rect_note.height <= 10:
        return None, True  # 已经结束
    
    # 计算总缩短高度
    total_height_reduced = elapsed_press_time * fall_speed
    
    # 创建新rect
    new_rect = rect_note.copy()
    original_bottom = rect_note.y + rect_note.height
    
    # 计算新高度
    new_height = max(10, rect_note.height - total_height_reduced)
    
    # 更新新rect
    new_rect.height = new_height
    new_rect.y = original_bottom - new_height  # 保持底部不变
    
    # 检查是否结束
    ended = new_height <= 10
    
    return new_rect, ended
#

def text_draw(screen):
    """绘制评价文字和连击数（带淡出效果）"""
    global display_text, text_display_start_time, combo
    if display_text is None:
        return
        
    current_display_time = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec
    
    # 检查是否超过显示时间
    if current_display_time - text_display_start_time > TEXT_DISPLAY_DURATION:
        display_text = None
        return
    
    # 计算透明度（淡出效果，最后0.1秒开始淡出）
    time_passed = current_display_time - text_display_start_time
    alpha_value = 255
    if time_passed > TEXT_DISPLAY_DURATION - 0.1:
        fade_ratio = (TEXT_DISPLAY_DURATION - time_passed) / 0.1
        alpha_value = int(255 * fade_ratio)
    
    # 绘制文字
    s_width = pg.Surface.get_width(screen)
    s_height = pg.Surface.get_height(screen)
    font = pg.font.SysFont(None, 57)
    
    # 根据文字内容设置颜色
    if display_text == 'perfect':
        color = (255, 255, 0)  # 黄色
    elif display_text == 'good':
        color = (0, 255, 0)    # 绿色
    elif display_text == 'bad':
        color = (255, 165, 0)  # 橙色
    elif display_text == 'miss':
        color = (255, 0, 0)    # 红色
    else:
        color = (255, 255, 255)  # 白色

    num_text = str(combo)
    num_image = font.render(num_text,True,'white')
    text_image = font.render(display_text,True,color)
    num_image.set_alpha(alpha_value)
    text_image.set_alpha(alpha_value)
    num_rect = num_image.get_rect()
    text_rect = text_image.get_rect()
    text_rect.center = (s_width//2,s_height//3)
    num_rect.center = (s_width//2,s_height//3+text_rect.height)
    screen.blit(num_image,num_rect)
    screen.blit(text_image,text_rect)
#

def draw_score_display(screen):
    """绘制左上角的分数显示面板"""
    global score, combo, max_combo, rank_level_judge
    
    s_width = pg.Surface.get_width(screen)
    score_font = pg.font.SysFont(None, 20)
    
    # 绘制分数显示
    score_text = score_font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (20, 20))
    
    # 绘制连击显示
    combo_color = (255, 100, 100) if combo >= 10 else (255, 255, 255)
    combo_text = score_font.render(f'Combo: {combo}', True, combo_color)
    screen.blit(combo_text, (20, 60))
    
    # 绘制最大连击显示
    max_combo_text = score_font.render(f'Max Combo: {max_combo}', True, (200, 200, 255))
    screen.blit(max_combo_text, (20, 100))
    
    # 绘制评价统计显示
    judge_text = score_font.render(
        f'P: {rank_level_judge[0]} G: {rank_level_judge[1]} B: {rank_level_judge[2]} M: {rank_level_judge[3]}',
        True, (255, 255, 255))
    screen.blit(judge_text, (20, 140))
    
    # 绘制准确率显示
    total_hits = sum(rank_level_judge)
    if total_hits > 0:
        accuracy = (rank_level_judge[0] + rank_level_judge[1] * 0.5) / total_hits * 100
        acc_text = score_font.render(f'Accuracy: {accuracy:.2f}%', True, (150, 255, 150))
        screen.blit(acc_text, (20, 180))
#

def reset_game_state():
    """重置所有游戏状态变量"""
    global display_text, combo, text_display_start_time, score, max_combo, rank_level_judge
    
    display_text = None
    combo = 0
    text_display_start_time = 0
    score = 0
    max_combo = 0
    rank_level_judge = [0, 0, 0, 0]

def draw_progress_bar(screen, current_time, total_time, music_duration=None):
    """绘制进度条"""
    s_width = pg.Surface.get_width(screen)
    s_height = pg.Surface.get_height(screen)
    
    # 进度条位置和尺寸
    bar_height = 8
    bar_y = s_height - 20  # 距离底部20像素
    bar_width = s_width - 40  # 左右各留20像素边距
    bar_x = 20
    
    # 如果没有提供总时长，使用最后一个音符的时间计算
    if total_time <= 0:
        return True
    
    # 计算进度百分比
    progress = min(1.0, max(0.0, current_time / total_time))
    
    # 绘制进度条背景
    pg.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), 0)
    
    # 绘制进度条前景
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        # 使用渐变色：从绿色到橙色
        color = (
            int(255 * (1 - progress) + 0 * progress),  # 红色分量
            int(255 * (1 - progress) + 165 * progress),  # 绿色分量
            0  # 蓝色分量
        )
        pg.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height), 0)
    
    # 绘制进度条边框
    pg.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 1)
    
    # 绘制当前时间和总时间文本
    time_font = pg.font.SysFont(None, 16)
    
    # 格式化时间显示 (分钟:秒)
    current_min = int(current_time) // 60
    current_sec = int(current_time) % 60
    total_min = int(total_time) // 60
    total_sec = int(total_time) % 60
    
    time_text = f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}"
    time_surface = time_font.render(time_text, True, (255, 255, 255))
    time_rect = time_surface.get_rect()
    time_rect.center = (s_width // 2, bar_y - 10)  # 在进度条上方居中显示
    
    screen.blit(time_surface, time_rect)
    
    # 绘制进度百分比
    percent_text = f"{progress * 100:.1f}%"
    percent_surface = time_font.render(percent_text, True, (200, 200, 255))
    percent_rect = percent_surface.get_rect()
    percent_rect.right = bar_x + bar_width - 5
    percent_rect.top = bar_y - 12

    if(progress >= 1.0):
        return True
    elif(progress <1.0):
        return False
    screen.blit(percent_surface, percent_rect)
#

def run_game(file_path=None, master_volume=1.0, current_latency=0, local_offset = 0, screen_size=None):
    global beat_delta, start_time, rank_level_judge, score, max_combo, combo, time_offset_sec
    
    # 重置分数相关全局变量
    reset_game_state()
    
    note_storage = list()  # 存储所有音符的时间
    list_space_initialize(note_storage,4)
    rect_note_storage = list() # 存储所有音符的矩形
    list_space_initialize(rect_note_storage,4)

    note_current = list() # 存储当前可见的音符时间
    list_space_initialize(note_current,4)
    rect_note_current = list() # 存储当前可见的音符矩形
    list_space_initialize(rect_note_current,4)
    rect_upper_note_current = list() # 存储当前可见的上层音符矩形（长条用）
    list_space_initialize(rect_upper_note_current,4)

    # 初始化各种状态变量
    note_read_sp = [0,0,0,0] # 各轨道已读取的音符索引
    column_statement = [0,0,0,0] # 各轨道的按键状态（0=未按下，1=已按下）
    column_lock_clock = [0,0,0,0] # 各轨道的按键锁定时间
    note_duration_time = [0,0,0,0] # 各轨道长条的剩余持续时间
    last_time = 0
    lock_time = 0
    fall_speed = 750 # 音符下落速度（像素/秒）
    final_offset_ms = current_latency + local_offset # 最终偏移量
    time_offset_sec = final_offset_ms / 1000.0
    offset = final_offset_ms

    pg.init() #pygame初始化
    # 设置主音量
    if pg.mixer.get_init():
        pg.mixer.music.set_volume(master_volume)

    #读取铺面文件所在路径
    root = os.getcwd()
    path = os.listdir(root)
    file_play = list()
    song_player = list()
    song_player_name = list()
    #
    #找到铺面文件并打开提取bpm和音符信息
    for p in path:
        file = os.path.splitext(p)
        if(file[1] == '.json'):
            file_play.append(p) # 谱面文件
        elif(file[1] == '.ogg'):
            song_player.append(p) # 音乐文件
            song_player_name.append(file[0]) # 音乐文件名（不含扩展名）
    # 选择谱面文件
    if file_path is not None:
        file_choose = file_path
    elif file_play:
        file_choose = file_play[0]
    else:
        return None, local_offset # 没有谱面文件，返回
    # 加载谱面文件
    with open(file_choose,'r',encoding = 'utf-8') as file:
        get_content = js.load(file)
    bpm = get_content['time'][0]['bpm'] #提取bpm信息
    beat_delta = 60.0/bpm # 一小节时长
    note = get_content['note'] # 提取音符信息
    beat_interval_ms = int(beat_delta * 1000) # 每拍时长（毫秒）
    # 创建节拍器音效
    metronome_sound = None
    if pg.mixer.get_init():
        sample_rate = 44100
        freq = 880 # 频率880Hz
        duration = 0.06 # 持续时间60ms
        length = int(sample_rate * duration)
        buf = bytearray(length * 2)
        for i in range(length):
            sample = 16000 if (i * freq * 2 // sample_rate) % 2 == 0 else -16000 # 方波
            buf[i * 2:i * 2 + 2] = int(sample).to_bytes(2, byteorder="little", signed=True)
        metronome_sound = pg.mixer.Sound(buffer=bytes(buf))


    title_song = get_content['meta']['song']['title'] # 获取歌曲标题
    # 加载音乐文件
    for i in range(0,len(song_player),1):
        if(song_player_name[i] == title_song):
            pg.mixer.music.load(song_player[i]) 
            break

    def build_result():
        """构建游戏结果数据"""
        total_hits = sum(rank_level_judge)
        if total_hits > 0:
            accuracy = (rank_level_judge[0] + rank_level_judge[1] * 0.5) / total_hits * 100
        else:
            accuracy = 0.0
        return {
            'title': title_song,
            'score': score,
            'max_combo': max_combo,
            'perfect': rank_level_judge[0],
            'good': rank_level_judge[1],
            'bad': rank_level_judge[2],
            'miss': rank_level_judge[3],
            'accuracy': accuracy,
        }

    # 创建游戏窗口
    if screen_size is None:
        screen_sizes = [(800,600),(1280,760),(1920,1080)]
        size_select = 0
        screen = pg.display.set_mode(screen_sizes[size_select], pg.RESIZABLE)
    else:
        screen = pg.display.set_mode(screen_size, pg.RESIZABLE)

    # 创建背景表面
    background = pg.Surface(screen.get_size())
    background.fill((30, 30, 30))
    s_width = pg.Surface.get_width(screen)
    s_height = pg.Surface.get_height(screen)

    # 轨道线位置（5条竖线，4个轨道）
    column_line_positions = [
        s_width/2-3*50,
        s_width/2-1*50,
        s_width/2+1*50,
        s_width/2+3*50,
        s_width/2+5*50
    ]
    # 音符位置（4个轨道的中心位置）
    column_note_positions = [
        s_width/2-3*50,
        s_width/2-1*50,
        s_width/2+1*50,
        s_width/2+3*50
    ]
    keyboard_map_use = [pg.K_a, pg.K_s, pg.K_k, pg.K_l]

    first_arrival_time = first_note_time_calculate(note,bpm,s_height,fall_speed,beat_delta,offset) # 计算第一个音符到达时间
    # 初始化音符数据
    note_time_initialize(note_storage,note,screen)
    note_rect_initialize(note,rect_note_storage,screen,column_note_positions,beat_delta,fall_speed)
    
    # 计算总时间（基于最后一个音符）
    # 找到所有轨道中最后一个音符的时间
    last_note_time = 0
    for column in note_storage:
        if column:
            column_max = max(column)
            if column_max > last_note_time:
                last_note_time = column_max
    
    # 计算总时间：最后一个音符出现的时间 + 下落时间 + 2秒缓冲
    total_time = last_note_time + (s_height-100)/fall_speed + 2.0

    # 初始化各种控制变量
    clock = pg.time.Clock()	#计时器
    isRunning = True
    music_play_flag = False
    isDoing = True
    start_time = pg.time.get_ticks()/1000.0
    resume_metronome_active = False
    resume_start_ms = 0
    resume_beat_index = 0
    resume_total_beats = 8
    freeze_elapsed = None
    isEnd = False
    isProgressEnd = False
    end_start_ms = None
    esc_hold_start = None
    auto_play_enabled = False
    auto_play_msg = None
    auto_play_msg_time = 0
    auto_play_hold = [False, False, False, False]

    while isRunning:
        # 处理事件
        for ev in pg.event.get():
            if(ev.type == pg.QUIT): # 窗口关闭事件
                keys = pg.key.get_pressed()
                if keys[pg.K_ESCAPE] and not isEnd:
                    if esc_hold_start is None:
                        esc_hold_start = pg.time.get_ticks()
                    continue
                isRunning = False
                break
            if ev.type == pg.VIDEORESIZE: # 窗口大小调整事件
                screen = pg.display.set_mode(ev.size, pg.RESIZABLE)
                background = pg.Surface(screen.get_size())
                background.fill((30, 30, 30))
                s_width = pg.Surface.get_width(screen)
                s_height = pg.Surface.get_height(screen)
                # 重新计算轨道位置
                column_line_positions = [
                    s_width/2-3*50,
                    s_width/2-1*50,
                    s_width/2+1*50,
                    s_width/2+3*50,
                    s_width/2+5*50
                ]
                column_note_positions = [
                    s_width/2-3*50,
                    s_width/2-1*50,
                    s_width/2+1*50,
                    s_width/2+3*50
                ]
                # 更新所有音符位置
                for col in range(0,4):
                    for rect in rect_note_storage[col]:
                        rect.centerx = column_note_positions[col]
                    for rect in rect_note_current[col]:
                        rect.centerx = column_note_positions[col]
                    for rect in rect_upper_note_current[col]:
                        rect.centerx = column_note_positions[col]
            if(ev.type == pg.KEYDOWN): # 键盘按下事件
                if(ev.key == pg.K_ESCAPE): # ESC键
                    if isProgressEnd: # 如果游戏已结束(基于进度条结束判断)
                        isRunning = False
                        return build_result(), local_offset
                        break
                    esc_hold_start = pg.time.get_ticks() # 开始计时
                elif(ev.key == pg.K_q): # Q键：切换自动播放
                    auto_play_enabled = not auto_play_enabled
                    auto_play_msg = "AUTO PLAY ON" if auto_play_enabled else "AUTO PLAY OFF"
                    auto_play_msg_time = pg.time.get_ticks()
            if(ev.type == pg.KEYUP and ev.key == pg.K_ESCAPE): # ESC键释放事件
                if esc_hold_start is not None:
                    if pg.time.get_ticks() - esc_hold_start < 2000 and not isEnd:
                        freeze_elapsed = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec
                        if pg.mixer.get_init():
                            pg.mixer.music.pause()
                        action, master_volume, local_offset = pause_interface.run_pause(screen, master_volume, local_offset) # 显示暂停界面
                        #更新音量、偏移
                        if pg.mixer.get_init():
                            pg.mixer.music.set_volume(master_volume)
                        final_offset_ms = current_latency + local_offset
                        time_offset_sec = final_offset_ms / 1000.0
                        resume_metronome_active = True
                        resume_start_ms = pg.time.get_ticks()
                        resume_beat_index = 0
                        #处理暂停界面中的continue、restart和quit事件
                        if action == "quit": #退出游玩
                            return None, local_offset
                            isRunning = False
                            break
                        if action == "restart": #重新开始
                            return "restart",local_offset
                    elif not isEnd: # 长按esc：返回结果
                        if pg.mixer.get_init():
                            pg.mixer.music.stop()
                        return build_result(), local_offset
                esc_hold_start = None
            if(ev.type == pg.KEYDOWN): # 普通按键按下
                note_keyboard_judge(0,ev.key,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,lock_time,start_time,fall_speed,rank_level_judge)
            if(ev.type == pg.KEYUP): # 普通按键释放
                note_keyboard_judge(1,ev.key,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,lock_time,start_time,fall_speed,rank_level_judge)

        # ESC键长按处理（2秒退出）
        now_ms = pg.time.get_ticks()
        if esc_hold_start is not None and now_ms - esc_hold_start >= 2000 and not isEnd:
            if pg.mixer.get_init():
                pg.mixer.music.stop()
            return build_result(), local_offset

        # 恢复节拍器处理（暂停后恢复时播放节拍器）
        if resume_metronome_active:
            start_time = pg.time.get_ticks()/1000.0 + time_offset_sec - freeze_elapsed
            if metronome_sound is not None:
                if now_ms - resume_start_ms >= resume_beat_index * beat_interval_ms and resume_beat_index < resume_total_beats:
                    metronome_sound.play()
                    resume_beat_index += 1
            if resume_beat_index >= resume_total_beats:
                resume_metronome_active = False
                freeze_elapsed = None
                if pg.mixer.get_init():
                    pg.mixer.music.unpause()

        # 音乐开始播放控制
        if(pg.time.get_ticks()/1000 - start_time + time_offset_sec >= first_arrival_time and not music_play_flag and not resume_metronome_active):
            pg.mixer.music.play()
            music_play_flag = True
        screen.blit(background, (0, 0))
        
        # 绘制判定线
        for pos in column_line_positions:
            pg.draw.line(screen, (100, 100, 100), (pos-50, 0), (pos-50, s_height), 2)
        
        # 绘制主要的判定线（note应该到达的位置）
        pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)

        note_draw(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,rect_upper_note_current,note_duration_time,column_statement,column_lock_clock,screen,fall_speed)

        # 自动播放功能
        if auto_play_enabled:
            current_time = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec
            for lane in range(0,4):
                if auto_play_hold[lane]:
                    if note_duration_time[lane] <= 0 or (current_time - column_lock_clock[lane]) >= note_duration_time[lane]:
                        note_keyboard_judge(1, keyboard_map_use[lane], screen, column_statement, column_lock_clock, note_duration_time, note_current, rect_note_current, rect_upper_note_current, lock_time, start_time, fall_speed, rank_level_judge)
                        auto_play_hold[lane] = False
                    continue
                if len(note_current[lane]) > 0:
                    if abs(note_current[lane][0] - current_time) <= 0.02:
                        note_keyboard_judge(0, keyboard_map_use[lane], screen, column_statement, column_lock_clock, note_duration_time, note_current, rect_note_current, rect_upper_note_current, lock_time, start_time, fall_speed, rank_level_judge)
                        if note_duration_time[lane] > 0:
                            auto_play_hold[lane] = True
        
        # 绘制左上角记分器
        draw_score_display(screen)
        
        current_time = pg.time.get_ticks()/1000.0 - start_time + time_offset_sec
        #进度条结束判断
        if(not isProgressEnd):
            isProgressEnd = draw_progress_bar(screen, current_time, total_time)
        else:
            isProgressEnd = draw_progress_bar(screen,total_time,total_time)
        
        text_draw(screen) # 绘制评价文字

         # 绘制自动播放提示
        if auto_play_msg is not None:
            if pg.time.get_ticks() - auto_play_msg_time <= 1000:
                msg_font = pg.font.SysFont(None, 28)
                msg_image = msg_font.render(auto_play_msg, True, (200, 200, 200))
                msg_rect = msg_image.get_rect()
                msg_rect.center = (s_width // 2, 24)
                screen.blit(msg_image, msg_rect)
            else:
                auto_play_msg = None

        # 音符读取结束判断
        if(not(end_judge(note,note_read_sp) and len(note_current))):
            last_time = rank_check(rank_level_judge,last_time,start_time)
        elif(isDoing == True):
            isEnd = True
            print(len(note)-1)
            combo = 0
            isDoing = False

        # 进度条结束后停止音乐
        if isProgressEnd:
            if pg.mixer.get_init():
                pg.mixer.music.stop()

        pg.display.update()
        clock.tick(100) #两次循环间隔(等价于100帧,保证按键有不响应期)

    pg.quit()
    #主程序

if __name__ == "__main__":
    run_game()
