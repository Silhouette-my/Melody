#undone
import json as js
import os
import numpy as py
import pygame as pg

def column_renderer(file,column,bpm,screen):
	bar_delta = 60/bpm
	present_time = pg.time.get_ticks()/1000

pg.init()
root = os.getcwd()
path = os.listdir(root)
file_play = list()
for p in path:
	type_file = os.path.splitext(p)
	if(type_file[1] == '.json'):
		file_play.append(p)
file_choose = file_play[0]
with open(file_choose,'r',encoding = 'utf-8') as file:
	get_content = js.load(file)
bpm = get_content['time']['bpm']
#
screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
size_select = 0 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
screen = pg.display.set_mode(screen_size[size_select])
#初始化窗口
clock = pg.time.Clock()	#计时器
isRunning = True

while isRunning:
	for ev in pg.event.get():
		if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
			isRunning = False
			break
	pg.display.update() #更新屏幕
	clock.tick(60) #两次循环间隔(等价于60帧,保证按键有不响应期)


pg.quit()
#主程序