import json as js
import os
import numpy as py
import pygame as pg
#保证0<=title_flag<=曲目个数-1(防数组超界)
def flag_judge(flag_now,file_play_len,lower):
	if(flag_now == lower or flag_now == file_play_len-1):
		return 0;
	else: return 1;

#在屏幕正中心绘制文字
def text_draw(title_flag,font,screen_size,size_select):
	text = title_song[title_flag]
	text_image = font.render(text,True,'white')
	text_rect = text_image.get_rect()
	if isinstance(screen_size, (list, tuple)) and len(screen_size) == 2 and isinstance(screen_size[0], int):
		width, height = screen_size
	else:
		width, height = screen_size[size_select]
	text_rect.center = (width//2,height//2)
	surface = pg.display.get_surface()
	if surface is not None:
		surface.blit(text_image,text_rect)
	return text_rect
def attention_draw(screen,screen_size,size_select):
	font_attention = pg.font.SysFont(None,30)
	attention = "Press 'Enter' to start"
	attention_image = font_attention.render(attention,True,'white')
	attention_rect = attention_image.get_rect()
	if isinstance(screen_size, (list, tuple)) and len(screen_size) == 2 and isinstance(screen_size[0], int):
		width, height = screen_size
	else:
		width, height = screen_size[size_select]
	attention_rect.center = (width//2,height//2+50)

	blink_time = pg.time.get_ticks()/1000 #???????????????????????????(????????????)???????????????
	blink_speed = 1.5 #???????????????????????????
	blink_duration = 0.8 #?????????????????????????????????
	if(blink_time % blink_speed < blink_duration):
		screen.blit(attention_image,attention_rect)
	else:
		text_replace(screen,attention_rect)
def text_replace(screen,last_rect):
	pg.draw.rect(surface = screen, color = 'black',rect = last_rect)

#
pg.init()
root = os.getcwd()
path = os.listdir(root)
file_play = list()
title_song = list()
for p in path:
	type_file = os.path.splitext(p)
	if(type_file[1] == '.json'):
		file_play.append(p)
#这部分是搜寻Melody这个文件夹下的.json文件并保存到file_play列表里面
#
for i in range(0,len(file_play),1):
	use_file = file_play[i]
	with open(use_file,'r',encoding = 'utf-8') as file:
		get_content = js.load(file)
	title_song.append(get_content['meta']['song']['title'])
#将.json文件中保存的曲目标题信息提取并保存到title_song列表中
#
if __name__ == "__main__":
	screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
	size_select = 0 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
	screen = pg.display.set_mode(screen_size[size_select])
	#初始化窗口
	#
	clock = pg.time.Clock()	#计时器
	title_flag = 0 #反映选中曲目在曲目列表内的序号
	last_rect = [(0,0)] #存储上一次显示文字的矩形区域
	font = pg.font.SysFont(None,50) #字体数据初始化
	#要用的变量初始化
	#
	last_rect[0] = text_draw(title_flag,font,screen_size,size_select) #绘制曲目列表内第一首歌的标题
	#
	#
	isRunning = True
	
	while isRunning:
		for ev in pg.event.get():
			bool_down = flag_judge(title_flag,len(title_song),-1)
			bool_up = flag_judge(title_flag,len(title_song)+1,0)
			if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
				isRunning = False
				break
			elif(ev.type == pg.KEYDOWN): #按向下键时显示下一个曲目
				if(ev.key == pg.K_DOWN and bool_down):
					if(last_rect[0] != (0,0)): #判断上一次是否绘制了标题，如果绘制就先覆盖掉它
						text_replace(screen,last_rect[0])
					title_flag += 1
					last_rect[0] = text_draw(title_flag,font,screen_size,size_select)
					break
				elif(ev.key == pg.K_UP and bool_up): #按向上键时显示上一个曲目
					if(last_rect[0] != (0,0)):
						text_replace(screen,last_rect[0])
					title_flag -= 1
					last_rect[0] = text_draw(title_flag,font,screen_size,size_select)
					break
		attention_draw(screen,screen_size,size_select)
		pg.display.update() #更新屏幕
		clock.tick(60) #两次循环间隔(等价于60帧,保证按键有不响应期)
	
	
	pg.quit()
	#主程序