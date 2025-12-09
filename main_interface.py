import json as js
import os
import numpy as py
import pygame as pg

def screen_interface(screen,font):
	start = "start"
	settings = "settings"
	quit = "quit"
	text = [start,settings,quit]
	text_image = list()
	text_rect = list()
	s_width = pg.Surface.get_width(screen)
	s_height = pg.Surface.get_height(screen)
	mid_pos = (s_width//2,s_height//2)
	for i in range(0,3,1):
		text_image.append(font.render(text[i],True,'white'))
		text_rect.append(text_image[i].get_rect())
		t_height = text_rect[i].height
		text_rect[i].center = (mid_pos[0],mid_pos[1]+(i-1)*2*t_height)
		screen.blit(text_image[i],text_rect[i])
	return text_rect

def button_border_draw(screen,text_rect,select_flag):
	border_x = text_rect[select_flag].x-5
	border_y = text_rect[select_flag].y-5
	border_width = text_rect[select_flag].width+10
	border_height = text_rect[select_flag].height+10
	last_rect = pg.Rect(border_x, border_y, border_width, border_height)
	border_color = 'white'
	border_line_width = 1
	pg.draw.rect(screen, border_color, last_rect, border_line_width)
	return last_rect

def button_border_clear(screen,last_rect):
	pg.draw.rect(screen,'black',last_rect,1)

pg.init()
screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
size_select = 0 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
button_select_flag = 0
screen = pg.display.set_mode(screen_size[size_select])
#初始化窗口
#
clock = pg.time.Clock()	#计时器
font = pg.font.SysFont(None,50) #字体数据初始化
text_rect = screen_interface(screen,font)
last_rect = button_border_draw(screen,text_rect,button_select_flag)
#要用的变量初始化

isRunning = True

while isRunning:
	for ev in pg.event.get():
		if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
			isRunning = False
			break
		elif(ev.type == pg.KEYDOWN):
			if(ev.key == pg.K_DOWN):
				if(button_select_flag < 2):
					button_border_clear(screen,last_rect)
					button_select_flag += 1
					last_rect = button_border_draw(screen,text_rect,button_select_flag)
				elif(button_select_flag >= 2):
					button_select_flag = 2
				break
			elif(ev.key == pg.K_UP):
				if(button_select_flag > 0):
					button_border_clear(screen,last_rect)
					button_select_flag -= 1
					last_rect = button_border_draw(screen,text_rect,button_select_flag)
				elif(button_select_flag <= 0):
					button_select_flag = 0
				break
	pg.display.update() #更新屏幕
	clock.tick(60) #两次循环间隔(等价于60帧,保证按键有不响应期)

pg.quit()