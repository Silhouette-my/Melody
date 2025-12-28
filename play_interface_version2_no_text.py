import json as js
import os
import numpy as np
import pygame as pg
import time

# 添加全局变量用于文字显示
display_text = None
text_display_start_time = 0
TEXT_DISPLAY_DURATION = 0.2  # 文字显示0.5秒
TEXT_WINDOW_PERIOD = 0.05     # 文字窗口期，窗口期内不改变显示的文字

def list_debug_check(target_list):
	list_length = len(target_list)
	for i in range(0,list_length,1):
		print("<",target_list[i],">"," ")
		print("\n")
#

def rank_check(rank_level_judge,last_time,start_time):
	current_time = pg.time.get_ticks()/1000 - start_time
	if(current_time - last_time >= 0.5):
		print(rank_level_judge)
		return current_time
	else:
		return last_time
#

def list_space_initialize(target_list,dimension):
	for i in range(0,dimension,1):
		temp = list()
		target_list.append(temp)
#

def note_time_initialize(note_storage,note,screen):
	length = len(note) #note的个数+1(Malody的note信息里面多了一个配置信息)
	s_height = pg.Surface.get_height(screen) #获取窗口宽度

	for i in range(0,length-1,1):
		note_appear_time = (note[i]['beat'][0]+note[i]['beat'][1]/note[i]['beat'][2])*beat_delta
		note_storage[note[i]['column']].append(note_appear_time)
#

def first_note_time_calculate(note,bpm,s_height,fall_speed,beat_delta,offset):
	first_note_beat = note[0]['beat']  # 获取第一个note的拍数信息
	first_note_beat_value = first_note_beat[1]/first_note_beat[2]
	# 转换为时间
	first_note_appear_time = first_note_beat_value * beat_delta  # note出现的时间
	# 计算到达判定线的时间
	arrival_time = first_note_appear_time + (s_height-100)/fall_speed + offset/1000
	return arrival_time
#

def note_rect_initialize(note,rect_note_storage,screen,column_note_positions,beat_delta,fall_speed):
	length = len(note)
	s_width = pg.Surface.get_width(screen)
	s_height = pg.Surface.get_height(screen)
	note_type = 1

	for i in range(0,length-1,1):
		if('endbeat' in note[i]):
			note_type = 0
		else:
			note_type = 1
		if(note_type):
			rect = pg.Rect(0,-110,80,10) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
			rect.centerx = column_note_positions[note[i]['column']] #矩形中心横坐标
			rect_note_storage[note[i]['column']].append(rect)
		elif(not note_type):
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
	delta_t = s_height/fall_speed
	for i in range(0,4,1):
		length_time_list = len(note_storage[i])
		sp_prev = note_read_sp[i]
		for j in range(sp_prev,length_time_list,1):
			note = note_storage[i][j]
			if(note-current_time <= delta_t):
				note_current[i].append(note)
				rect_note_current[i].append(rect_note_storage[i][j])
				note_read_sp[i] += 1
			elif(note-current_time > delta_t):
				break
#

def note_draw(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,rect_upper_note_current,note_duration_time,column_statement,column_lock_clock,screen,fall_speed):
	global display_text, text_display_start_time
	s_height = pg.Surface.get_height(screen)
	current_time = pg.time.get_ticks()/1000.0-start_time
	note_judge(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,current_time,s_height,fall_speed)
	for i in range(0,4,1):
		j = 0
		while j < len(rect_note_current[i]):
			rect_note = rect_note_current[i][j]
			note_time = note_current[i][j]
			if(rect_note.y <= s_height):
				time_diff = note_time - current_time
				pg.draw.rect(screen, (30, 30, 30), rect_note, 0) #用背景色色矩形覆盖上一次显示的白色矩形
				if(rect_note.height > 10):
					if(note_duration_time[i] > 0):
						long_note_ended = long_note_height_change(i,j,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,start_time,fall_speed)
						if long_note_ended:
                            # 长条结束，从队列中移除
							del note_current[i][j]
							del rect_note_current[i][j]
							note_duration_time[i] = 0
							column_lock_clock[i] = 0
							column_statement[i] = 1
							continue  # 跳过后续渲染和j的增加
					else:
						rect_note.y = (s_height-100)-rect_note.height-time_diff*fall_speed
				else:
					rect_note.y = (s_height-100)-rect_note.height-time_diff*fall_speed
				if(time_diff >= -s_height/fall_speed): #只渲染会出现在屏幕里的note,且在其出现前就预渲染好(避免长条渲染出错)
					pg.draw.rect(screen,'white',rect_note,0)
				j += 1
			elif(rect_note.y > s_height):
				if(rect_note.height == 10):
					rank_level_judge[3] += 1
					combo = 0
					display_text = 'miss'
					text_display_start_time = current_time					
                # 音符已过判定线，检查是否是长条
				elif(rect_note.height > 10 and note_duration_time[i] > 0):
                    # 长条未完成，判定为miss
					rank_level_judge[3] += 1
					combo = 0
					display_text = 'miss'
					text_display_start_time = current_time
				del note_current[i][j]
				del rect_note_current[i][j]
                # 如果删除的是长条，重置相关状态
				if(rect_note.height > 10):
					note_duration_time[i] = 0
					column_lock_clock[i] = 0
					column_statement[i] = 1
#

def rank_judge(judge_time_diff,key_use,screen,note_current,rect_note_current,current_time,lock_time,rank_level_judge,combo):
	global display_text, text_display_start_time
	# 检查是否在窗口期内，如果是则保持原有文字不改变
	current_display_time = pg.time.get_ticks()/1000.0 - start_time
	if display_text is not None and (current_display_time - text_display_start_time) < TEXT_WINDOW_PERIOD:
		return  # 窗口期内不改变文字
	if(judge_time_diff <= 50/1000):
		rank_level_judge[0] += 1
		combo += 1
		pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
		display_text = 'perfect'
		text_display_start_time = current_display_time
	elif(judge_time_diff <= 80/1000):
		rank_level_judge[1] += 1
		combo += 1
		pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
		display_text = 'good'
		text_display_start_time = current_display_time
	elif(judge_time_diff <= 120/1000):
		rank_level_judge[2] += 1
		combo = 0
		pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
		display_text = 'bad'
		text_display_start_time = current_display_time
	else:
		rank_level_judge[3] += 1
		combo = 0
		pg.draw.rect(screen,(30, 30, 30),rect_note_current[key_use][0],0)
		display_text = 'miss'
		text_display_start_time = current_display_time
#

def note_keyboard_judge(keyboard_statement,keyboard_input,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,lock_time,start_times,fall_speed,rank_level_judge,combo):
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
	current_time = pg.time.get_ticks()/1000.0-start_time	

	if(keyboard_statement == 0):
		if(not len(rect_note_current[key_use])):
			return
		if(rect_note_current[key_use][0].y+rect_note_current[key_use][0].height <= s_height/2):
			return
		if(rect_note_current[key_use][0].height == 10):
			judge_time_diff = np.fabs(note_current[key_use][0]-current_time)
			rank_judge(judge_time_diff,key_use,screen,note_current,rect_note_current,current_time,lock_time,rank_level_judge,combo)
			if(len(note_current[key_use]) > 0):
				del note_current[key_use][0]
			if(len(rect_note_current[key_use]) > 0):
				del rect_note_current[key_use][0]
			column_statement[key_use] = 0
		elif(rect_note_current[key_use][0].height > 10):
			judge_time_diff = np.fabs(note_current[key_use][0]-current_time)
			note_duration_time[key_use] = rect_note_current[key_use][0].height/fall_speed
			column_lock_clock[key_use] = current_time
			rank_judge(judge_time_diff,key_use,screen,note_current,rect_note_current,current_time,lock_time,rank_level_judge,combo)
	elif(keyboard_statement == 1):
		if(column_lock_clock[key_use] != 0):
			if(len(rect_note_current[key_use]) > 0 and rect_note_current[key_use][0].height > 10):
				if(note_duration_time[key_use]-current_time > 0.1):
					combo = 0
				if(len(note_current[key_use]) > 0):
					del note_current[key_use][0]
				if(len(rect_note_current[key_use]) > 0):
					del rect_note_current[key_use][0]
				note_duration_time[key_use] = 0
				column_lock_clock[key_use] = 0
				column_statement[key_use] = 1
#

def long_note_height_change(key_use,label,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,start_time,fall_speed):
	#rect = pg.Rect(rect_note_current[key_use][label].x,rect_note_current[key_use][label].y+rect_note_current[key_use][label].height,80,10)
	current_time = pg.time.get_ticks()/1000.0 - start_time
	if(rect_note_current[key_use][label].height > 10):
		press_time = current_time - column_lock_clock[key_use]
		height_reduced = press_time * fall_speed
		original_height = rect_note_current[key_use][label].height
		#rect_note_current[key_use][label].y += press_time*fall_speed
		#rect_note_current[key_use][label].height = max(10,rect.y-rect_note_current[key_use][label].y)
		rect_note_current[key_use][label].height = max(10, rect_note_current[key_use][label].height - height_reduced)
		height_change = original_height - rect_note_current[key_use][label].height
		rect_note_current[key_use][label].y += height_change
		for j in range(label + 1, len(rect_note_current[key_use])):
			rect_note_current[key_use][j].y += height_change
        
		column_lock_clock[key_use] = current_time
		column_statement[key_use] = 1
        # 检查长条是否结束（高度<=10）
		if rect_note_current[key_use][label].height <= 10:
            # 长条结束，准备清理
			return True
	elif rect_note_current[key_use][label].height <= 10:
        # 长条已经结束
		return True
	return False
#

def text_draw(screen):
	global display_text, text_display_start_time
	if display_text is None:
		return
        
	current_display_time = pg.time.get_ticks()/1000.0 - start_time
    
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

	text_image = font.render(display_text,True,color)
	text_image.set_alpha(alpha_value)
	text_rect = text_image.get_rect()
	text_rect.center = (s_width/2,s_height/3)
	screen.blit(text_image,text_rect)
#

note_storage = list()
list_space_initialize(note_storage,4)
rect_note_storage = list()
list_space_initialize(rect_note_storage,4)

note_current = list()
list_space_initialize(note_current,4)
rect_note_current = list()
list_space_initialize(rect_note_current,4)
rect_upper_note_current = list()
list_space_initialize(rect_upper_note_current,4)

note_read_sp = [0,0,0,0]
column_statement = [0,0,0,0]
column_lock_clock = [0,0,0,0]
note_duration_time = [0,0,0,0]
rank_level_judge = [0,0,0,0]
last_time = 0
lock_time = 0
combo = 0
fall_speed = 650
offset = 700

pg.init() #pygame初始化

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
		file_play.append(p)
	elif(file[1] == '.ogg'):
		song_player.append(p)
		song_player_name.append(file[0])
file_choose = file_play[0] #此处可手动更改铺面
with open(file_choose,'r',encoding = 'utf-8') as file:
	get_content = js.load(file)
bpm = get_content['time'][0]['bpm'] #提取bpm信息
beat_delta = 60.0/bpm # 一小节时长
note = get_content['note'] #提取note信息

title_song = get_content['meta']['song']['title']
for i in range(0,len(song_player),1):
	if(song_player_name[i] == title_song):
		pg.mixer.music.load(song_player[i]) 
		break

#
screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
size_select = 0 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
screen = pg.display.set_mode(screen_size[size_select])
#初始化窗口

background = pg.Surface(screen.get_size())
background.fill((30, 30, 30))
s_width = pg.Surface.get_width(screen)
s_height = pg.Surface.get_height(screen)
column_line_positions = [
	s_width/2-3*50,
	s_width/2-1*50,
	s_width/2+1*50,
	s_width/2+3*50,
	s_width/2+5*50
]
column_note_positions = [ #列的位置
	s_width/2-3*50,
	s_width/2-1*50,
	s_width/2+1*50,
	s_width/2+3*50
]
keyboard_map_use = [pg.K_a, pg.K_s, pg.K_k, pg.K_l]

first_arrival_time = first_note_time_calculate(note,bpm,s_height,fall_speed,beat_delta,offset)
note_time_initialize(note_storage,note,screen)
note_rect_initialize(note,rect_note_storage,screen,column_note_positions,beat_delta,fall_speed)

clock = pg.time.Clock()	#计时器
isRunning = True
music_play_flag = False
start_time = pg.time.get_ticks()/1000.0

while isRunning:
	for ev in pg.event.get():
		if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
			isRunning = False
			break
		if(ev.type == pg.KEYDOWN):
			if(ev.key == pg.K_ESCAPE):
				isRunning = False
				break
		if(ev.type == pg.KEYDOWN):
			note_keyboard_judge(0,ev.key,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,lock_time,start_time,fall_speed,rank_level_judge,combo)
		if(ev.type == pg.KEYUP):
			note_keyboard_judge(1,ev.key,screen,column_statement,column_lock_clock,note_duration_time,note_current,rect_note_current,rect_upper_note_current,lock_time,start_time,fall_speed,rank_level_judge,combo)
	if(pg.time.get_ticks()/1000-start_time >= first_arrival_time and not music_play_flag):
		pg.mixer.music.play()
		music_play_flag = True
	screen.blit(background, (0, 0))
    
    # 绘制判定线
	for pos in column_line_positions:
		pg.draw.line(screen, (100, 100, 100), (pos-50, 0), (pos-50, s_height), 2)
    
    # 绘制主要的判定线（note应该到达的位置）
	pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)

	note_draw(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,rect_upper_note_current,note_duration_time,column_statement,column_lock_clock,screen,fall_speed)
	text_draw(screen)
	last_time = rank_check(rank_level_judge,last_time,start_time)

	pg.display.update()
	clock.tick(100) #两次循环间隔(等价于100帧,保证按键有不响应期)

pg.quit()
#主程序