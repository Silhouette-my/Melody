import json as js
import os
import numpy as py
import pygame as pg
def flag_judge(flag_now,file_play_len):
	if(flag_now == -1 or flag_now == file_play_len-1):
		return 0;
	else: return 1;

def text_draw(title_flag, font, screen_size, size_select):
	text = title_song[title_flag]
	text_image = font.render(text,True,'white')
	text_rect = text_image.get_rect()
	text_rect.center = (screen_size[size_select][0]//2,screen_size[size_select][1]//2)
	screen.blit(text_image,text_rect)
	return text_rect 
def text_replace(screen,last_rect):
	pg.draw.rect(surface = screen, color = 'black',rect = last_rect[0])

pg.init()
root = os.getcwd()
path = os.listdir(root)
file_play = list()
title_song = list()
for p in path:
	type_file = os.path.splitext(p)
	if(type_file[1] == '.json'):
		file_play.append(p)
#上面这部分是搜寻Melody这个文件夹下的.json文件并保存到file_play列表里面
for i in range(0,len(file_play),1):
	use_file = file_play[i]
	with open(use_file,'r',encoding = 'utf-8') as file:
		get_content = js.load(file)
	title_song.append(get_content['meta']['song']['title'])

screen_size = [(800,600),(1280,760),(1920,1080)]
size_select = 0
screen = pg.display.set_mode(screen_size[size_select])

clock = pg.time.Clock()
title_flag = 0
last_rect = [(0,0)]

font = pg.font.SysFont(None,36)
last_rect[0] = text_draw(title_flag,font,screen_size,size_select)

isRunning = True

while isRunning:
	for ev in pg.event.get():
		bool_down = flag_judge(title_flag,len(title_song))
		bool_up = flag_judge(title_flag,len(title_song)+1)
		if(ev.type == pg.QUIT):
			isRunning = False
			break
		elif(ev.type == pg.KEYDOWN):
			if(ev.key == pg.K_DOWN and bool_down):
				if(last_rect[0] != (0,0)):
					text_replace(screen,last_rect)
				title_flag += 1
				last_rect[0] = text_draw(title_flag,font,screen_size,size_select)
				break
			elif(ev.key == pg.K_UP and bool_up):
				if(last_rect[0] != (0,0)):
					text_replace(screen,last_rect)
				title_flag -= 1
				last_rect[0] = text_draw(title_flag,font,screen_size,size_select)
				break



	pg.display.update()
	clock.tick(60)


pg.quit()








