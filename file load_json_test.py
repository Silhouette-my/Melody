import json as js
import os
import numpy as py
import pygame as pg
def flag_judge(flag_now,file_play_len):
	if(flag_now == -1 or flag_now == file_play_len-1):
		return 0;
	else: return 1;
def text_draw(title_flag,font):
	text = title_song[title_flag]
	text_image = font.render(text,True,'white')
	screen.blit(text_image,(350,250)) 
pg.init()
root = os.getcwd()
path = os.listdir(root)
file_play = list()
title_song = list()
for p in path:
	type_file = os.path.splitext(p)
	#print(type_file[1])
	if(type_file[1] == '.json'):
		file_play.append(p)
#上面这部分是搜寻Melody这个文件夹下的.json文件并保存到file_play列表里面
for i in range(0,len(file_play),1):
	use_file = file_play[i]
	with open(use_file,'r',encoding = 'utf-8') as file:
		get_content = js.load(file)
	title_song.append(get_content['meta']['song']['title'])

screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
title_flag = 0
font = pg.font.SysFont(None,36)
text_draw(title_flag,font)
isRunning = True
while isRunning:
	for ev in pg.event.get():
		_bool = flag_judge(title_flag,len(title_song))
		if(ev.type == pg.QUIT):
			isRunning = False
			break
		elif(ev.type == pg.KEYDOWN):
			if(ev.key == pg.K_DOWN and _bool):
				title_flag += 1
				text_draw(title_flag,font)
				break



	pg.display.update()
	clock.tick(60)


pg.quit()








