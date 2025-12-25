import json as js
import os
import numpy as np
import pygame as pg
import time

def note_load(column_storage,note,screen,bar_delta):
	length = len(note_file) #note的个数+1(Malody的note信息里面多了一个配置信息)
	s_height = pg.Surface.get_height(screen) #获取窗口宽度

	column0 = list()
	column1 = list()
	column2 = list()
	column3 = list()

	for i in range(0,length-1,1):
		if(note['column'] == 0):
			

pg.init() #pygame初始化

#读取铺面文件所在路径
root = os.getcwd()
path = os.listdir(root)
file_play = list()
song_player = list()
song_player_name = list()
column_storage = list()
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
note = get_content['note'] #提取note信息

title_song = get_content['meta']['song']['title']
for i in range(0,len(song_player),1):
	if(song_player_name[i] == title_song):
		pg.mixer.music.load(song_player[i]) 
		break

first_note_beat = note[0]['beat']  # 获取第一个note的拍数信息
first_note_beat_value = first_note_beat[0] + first_note_beat[1]/first_note_beat[2]
# 转换为时间
bar_delta = 60.0/bpm * 4  # 一小节时长
first_note_appear_time = first_note_beat_value/4 * bar_delta  # note出现的时间
# 计算到达判定线的时间
arrival_time = first_note_appear_time + s_height/fall_speed

#
screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
size_select = 0 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
screen = pg.display.set_mode(screen_size[size_select])
#初始化窗口

background = pg.Surface(screen.get_size())
background.fill((30, 30, 30))
s_width = pg.Surface.get_width(screen)
s_height = pg.Surface.get_height(screen)
column_positions = [
	s_width/2-3*50,
	s_width/2-1*50,
	s_width/2+1*50,
	s_width/2+3*50,
	s_width/2+5*50
]
keyboard_map_use = [pg.K_a, pg.K_s, pg.K_k, pg.K_l]

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
			#note_keyboard_judge(ev.key,note_current,rect_note_current,start_time,fall_speed,screen,rank_level_judge)
	if(pg.time.get_ticks()/1000-start_time >= arrival_time and not music_play_flag):
		pg.mixer.music.play()
		music_play_flag = True
	screen.blit(background, (0, 0))
    
    # 绘制判定线
	for pos in column_positions:
		pg.draw.line(screen, (100, 100, 100), (pos-50, 0), (pos-50, s_height), 2)
    
    # 绘制主要的判定线（note应该到达的位置）
	pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)
	pg.display.update()
	clock.tick(100) #两次循环间隔(等价于100帧,保证按键有不响应期)

pg.quit()
#主程序