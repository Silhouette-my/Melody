import json as js
import os
import numpy as np
import pygame as pg
import time

def text_draw(screen,font,text_use,coordinate,rect_text_use):
	width = pg.Surface.get_width(screen)
	height = pg.Surface.get_height(screen)
	for i in range(len(text_use)):
		text = text_use[i]
		text_image = font.render(text, True, 'white')
		text_rect = text_image.get_rect()
        
        # 注意：这里x坐标应该是绝对坐标，不是比例
		x_pos = coordinate[i][0]
		y_pos = coordinate[i][1]
        
		if coordinate[i][2] == 'right':  # 右对齐
			text_rect.right = x_pos
			text_rect.centery = y_pos
		elif coordinate[i][2] == 'center':  # 居中
			text_rect.center = (x_pos, y_pos)
		rect_text_use.append(text_rect)
        
		surface = pg.display.get_surface()
		if surface is not None:
			surface.blit(text_image, text_rect)

def coordinate_calculate(width,height,font,coordinate_text_use):
	# 计算中间矩形区域（9宫格的正中间）
    # 中间矩形左上角坐标：(width/3, height/3)
    # 中间矩形尺寸：(width/3, height/3)
	center_rect_x = width / 3
	center_rect_y = height / 3
	center_rect_width = width / 3
	center_rect_height = height / 3
    
    # 计算文字坐标，格式：[x位置, y位置, 对齐方式]
    
    # 1. volume - 在中间矩形左侧，右对齐，y在矩形上1/4处
    # 右对齐的x坐标应该是中间矩形的左边界
	vol_x = center_rect_x
	vol_y = center_rect_y + center_rect_height * 1/3
	coordinate_text_use.append([vol_x, vol_y, 'right'])
    
    # 2. local offset - 在中间矩形左侧，右对齐，y在矩形上1/2处
	local_x = center_rect_x
	local_y = center_rect_y + center_rect_height * 2/3
	coordinate_text_use.append([local_x, local_y, 'right'])
    
    # 3. continue, restart, quit - 在中间矩形底部，均分，居中
	button_bottom_y = center_rect_y + center_rect_height  # 底部y坐标
    
    # 首先获取每个按钮文本的宽度，用于计算总宽度
	button_texts = ['continue', 'restart', 'quit']
	button_widths = []
	for text in button_texts:
		text_image = font.render(text, True, 'white')
		button_widths.append(text_image.get_width())
    
    # 计算三个按钮的总宽度和平均间隔
	total_buttons_width = sum(button_widths)
    
    # 在中间矩形内等间距排列三个按钮
    # 左侧起始位置：中间矩形左边界
	left_boundary = center_rect_x
    # 右侧结束位置：中间矩形右边界
	right_boundary = center_rect_x + center_rect_width
    # 可用总宽度：中间矩形宽度
	available_width = center_rect_width
    
    # 计算每个按钮之间的间距（按钮间有4个间隔：左边界-按钮1，按钮1-按钮2，按钮2-按钮3，按钮3-右边界）
    # 让所有间隔相等
	total_gap = available_width - total_buttons_width
	gap_width = total_gap / 4  # 4个间隔
    
    # 计算每个按钮的x位置
	current_x = left_boundary + gap_width
	button_positions = []
    
	for i in range(3):
        # 按钮的x中心位置 = current_x + 按钮宽度的一半
		button_center_x = current_x + button_widths[i] / 2
		button_positions.append(button_center_x)
        
        # 移动到下一个按钮的起始位置
		current_x += button_widths[i] + gap_width
    
    # 添加三个按钮的坐标
	for i in range(3):
		coordinate_text_use.append([button_positions[i], button_bottom_y, 'center'])

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

def slider_draw(screen,value,label,rect_text_use):
	if(label == 'volume'):


pg.init()

text_use = ['volume','local offset','continue','restart','quit']
coordinate_text_use = list()
rect_text_use = list()

#
if __name__ == "__main__":
	screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
	size_select = 1 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
	screen = pg.display.set_mode(screen_size[size_select])
	width, height = screen_size[size_select]
	#初始化窗口

	#
	clock = pg.time.Clock()	#计时器
	font = pg.font.SysFont(None,40) #字体数据初始化
	flag = 0
	coordinate_calculate(width,height,font,coordinate_text_use)
	text_draw(screen,font,text_use,coordinate_text_use,rect_text_use)
	last_rect = button_border_draw(screen,rect_text_use,flag)
	#要用的变量初始化

	for i in rect_text_use:
		print(i)
	#
	isRunning = True
	
	while isRunning:
		for ev in pg.event.get():
			if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
				isRunning = False
				break
			elif(ev.type == pg.KEYDOWN):
				if(ev.key == pg.K_DOWN):
					button_border_clear(screen,last_rect)
					flag = min(4,flag+1)
					last_rect = button_border_draw(screen,rect_text_use,flag)
				elif(ev.key == pg.K_UP):
					button_border_clear(screen,last_rect)
					flag = max(0,flag-1)
					last_rect = button_border_draw(screen,rect_text_use,flag)
				break

		pg.display.update() #更新屏幕
		clock.tick(60) #两次循环间隔(等价于60帧,保证按键有不响应期)
	
	
	pg.quit()
	#主程序