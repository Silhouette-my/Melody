import json as js
import os
import numpy as np
import pygame as pg
import time

def list_debug_check(target_list):
	list_length = len(target_list)
	for i in range(0,list_length,1):
		print("<",target_list[i],">"," ")
		print("\n")
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

def first_note_time_calculate(note,bpm,s_height,fall_speed,beat_delta):
	first_note_beat = note[0]['beat']  # 获取第一个note的拍数信息
	first_note_beat_value = first_note_beat[0] + first_note_beat[1]/first_note_beat[2]
	# 转换为时间
	first_note_appear_time = first_note_beat_value * beat_delta  # note出现的时间
	# 计算到达判定线的时间
	arrival_time = first_note_appear_time + s_height/fall_speed
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

def note_draw(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,screen,fall_speed):
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
				pg.draw.rect(screen, (30, 30, 30), rect_note, 0) #用黑色矩形覆盖上一次显示的白色矩形
				rect_note.y = (s_height-100)-rect_note.height-time_diff*fall_speed
				if(time_diff >= -s_height/fall_speed): #只渲染会出现在屏幕里的note,且在其出现前就预渲染好(避免长条渲染出错)
					pg.draw.rect(screen,'white',rect_note,0)
				j += 1
			elif(rect_note.y > s_height):
				del note_current[i][j]
				del rect_note_current[i][j]
				#list_debug_check(note_current)
				#list_debug_check(rect_note_storage)
#

note_storage = list()
list_space_initialize(note_storage,4)
rect_note_storage = list()
list_space_initialize(rect_note_storage,4)

note_current = list()
list_space_initialize(note_current,4)
rect_note_current = list()
list_space_initialize(rect_note_current,4)

note_read_sp = [0,0,0,0]
rank_level_judge = [0,0,0,0]
fall_speed = 650

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
file_choose = file_play[1] #此处可手动更改铺面
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

first_arrival_time = first_note_time_calculate(note,bpm,s_height,fall_speed,beat_delta)
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
		#if(sp == -1):
			#if(ev.type == pg.KEYDOWN):
				#if(ev.key == pg.K_ESCAPE):
					#isRunning = False
					#break
		if(ev.type == pg.KEYDOWN):
			if(ev.key == pg.K_ESCAPE):
				isRunning = False
				break
		#if(ev.type == pg.KEYDOWN):
			#note_keyboard_judge(ev.key,note_current,rect_note_storage,start_time,fall_speed,screen,rank_level_judge)
	if(pg.time.get_ticks()/1000-start_time >= first_arrival_time and not music_play_flag):
		pg.mixer.music.play()
		music_play_flag = True
	screen.blit(background, (0, 0))
    
    # 绘制判定线
	for pos in column_line_positions:
		pg.draw.line(screen, (100, 100, 100), (pos-50, 0), (pos-50, s_height), 2)
    
    # 绘制主要的判定线（note应该到达的位置）
	pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)
	note_draw(note,note_storage,note_read_sp,rect_note_storage,note_current,rect_note_current,screen,fall_speed)
	pg.display.update()
	clock.tick(100) #两次循环间隔(等价于100帧,保证按键有不响应期)

pg.quit()
#主程序