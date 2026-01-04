import json as js
import os
import numpy as np
import pygame as pg
import time
import shared_state
import sys

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

def slider_draw(screen,value,label,rect_text_use,font,slider_volume_rect,slider_offset_rect):
	width = pg.Surface.get_width(screen)
	height = pg.Surface.get_height(screen)
	if(label == 'volume'):
		# 获取continue和quit按钮的矩形
		# rect_text_use[2]是continue, rect_text_use[4]是quit
		continue_rect = rect_text_use[2]
		quit_rect = rect_text_use[4]
		
		# 滑动条的左端与continue左端对齐，右端与quit右端对齐
		slider_left = continue_rect.left
		slider_right = quit_rect.right
		slider_width = (slider_right - slider_left)*value/100
		
		# 滑动条的高度与音量文本的高度相同
		slider_height = rect_text_use[0].height
		
		# 滑动条的y位置与音量文本对齐
		slider_y = rect_text_use[0].y
		
		# 创建滑动条矩形
		slider_rect = pg.Rect(slider_left, slider_y, slider_width, slider_height)

		volume_image = font.render(str(value), True, 'white')
		volume_rect = volume_image.get_rect()
		volume_rect.x = slider_right+20
		volume_rect.y = slider_rect.y
		
		slider_volume_rect.append(slider_rect)
		slider_volume_rect.append(volume_rect)
		# 绘制滑动条背景
		pg.draw.rect(screen, 'white', slider_rect)
		surface = pg.display.get_surface()
		if surface is not None:
			surface.blit(volume_image, volume_rect)

	elif(label == 'local offset'):
		# 获取continue和quit按钮的矩形
		# rect_text_use[2]是continue, rect_text_use[4]是quit
		continue_rect = rect_text_use[2]
		quit_rect = rect_text_use[4]
		
		# 滑动条的左端与continue左端对齐，右端与quit右端对齐
		slider_left = continue_rect.left
		slider_right = quit_rect.right
		slider_width = slider_right - slider_left
		
		# 滑动条的高度与本地偏移文本的高度相同
		slider_height = rect_text_use[1].height
		
		# 滑动条的y位置与本地偏移文本对齐
		slider_y = rect_text_use[1].y
		
		# 创建滑动条矩形
		slider_rect = pg.Rect(slider_left,slider_y,slider_width,slider_height)
		slider_left_rect = pg.Rect(slider_left, slider_y, slider_width*(0.5+value/2000), slider_height)
		slider_right_rect = pg.Rect(slider_left+slider_width*(0.5+value/2000),slider_y,slider_width*(0.5-value/2000),slider_height)
		
		offset_image = font.render(str(value), True, 'white')
		offset_rect = offset_image.get_rect()
		offset_rect.x = slider_right+20
		offset_rect.y = slider_rect.y
		
		slider_offset_rect.append(slider_rect)
		slider_offset_rect.append(offset_rect)
		# 绘制滑动条背景
		pg.draw.rect(screen, 'white', slider_left_rect)
		pg.draw.rect(screen,'blue',slider_right_rect)
		surface = pg.display.get_surface()
		if surface is not None:
			surface.blit(offset_image, offset_rect)

def slider_clear(screen,label,slider_volume_rect,slider_offset_rect):
	if(label == 'volume'):
		for i in range(0,2,1):
			pg.draw.rect(screen,'black',slider_volume_rect[i])
		for i in range(0,len(slider_volume_rect),1):
			del slider_volume_rect[0]
	elif(label == 'local offset'):
		for i in range(0,2,1):
			pg.draw.rect(screen,'black',slider_offset_rect[i])
		for i in range(0,len(slider_offset_rect),1):
			del slider_offset_rect[0]

def run_pause(screen, current_volume, current_offset):
	width = pg.Surface.get_width(screen)
	height = pg.Surface.get_height(screen)
	clock = pg.time.Clock()
	font_size = [30,40,60]
	screen_sizes = [(800,600),(1280,760),(1920,1080)]
	font_size_use = None
	for i in range(0,3,1):
		size = screen_sizes[i]
		if(size == pg.Surface.get_size(screen)):
			font_size_use = font_size[i]
			break
	font = pg.font.SysFont(None,font_size_use)
	screen.fill((0, 0, 0))

	text_use = ['volume','local offset','continue','restart','quit']
	coordinate_text_use = list()
	rect_text_use = list()
	slider_volume_rect = list()
	slider_offset_rect = list()
	volume = max(0, min(100, int(round(shared_state.MASTER_VOLUME * 100))))
	offset = int(current_offset)
	flag = 0

	coordinate_calculate(width,height,font,coordinate_text_use)
	text_draw(screen,font,text_use,coordinate_text_use,rect_text_use)
	slider_draw(screen,volume,'volume',rect_text_use,font,slider_volume_rect,slider_offset_rect)
	slider_draw(screen,offset,'local offset',rect_text_use,font,slider_volume_rect,slider_offset_rect)
	last_rect = button_border_draw(screen,rect_text_use,flag)
	last_update_time = 0
	key_update_delay = 80
	action = "resume"
	esc_hold_start = None

	isRunning = True
	while isRunning:
		current_time = pg.time.get_ticks()
		for ev in pg.event.get():
			if(ev.type == pg.QUIT):
				pg.quit()
				sys.exit()
			elif(ev.type == pg.KEYDOWN):
				if(ev.key == pg.K_ESCAPE):
					esc_hold_start = pg.time.get_ticks()
				elif(ev.key == pg.K_DOWN):
					button_border_clear(screen,last_rect)
					flag = min(4,flag+1)
					last_rect = button_border_draw(screen,rect_text_use,flag)
				elif(ev.key == pg.K_UP):
					button_border_clear(screen,last_rect)
					flag = max(0,flag-1)
					last_rect = button_border_draw(screen,rect_text_use,flag)
				elif(ev.key == pg.K_RETURN):
					if(flag == 2):
						action = "resume"
					elif(flag == 3):
						action = "restart"
					elif(flag == 4):
						action = "quit"
					isRunning = False
					break
			elif(ev.type == pg.KEYUP and ev.key == pg.K_ESCAPE):
				if esc_hold_start is not None and pg.time.get_ticks() - esc_hold_start < 2000:
					action = "resume"
					isRunning = False
					break
				esc_hold_start = None
		if(current_time - last_update_time > key_update_delay):
			keys = pg.key.get_pressed()
			if keys[pg.K_RIGHT]:
				if(flag == 0):
					slider_clear(screen,'volume',slider_volume_rect,slider_offset_rect)
					volume = min(100,volume+1)
					slider_draw(screen,volume,'volume',rect_text_use,font,slider_volume_rect,slider_offset_rect)
					if pg.mixer.get_init():
						pg.mixer.music.set_volume(volume/100)
					shared_state.MASTER_VOLUME = volume / 100.0
				elif(flag == 1):
					slider_clear(screen,'local offset',slider_volume_rect,slider_offset_rect)
					offset = min(1000,offset+10)
					slider_draw(screen,offset,'local offset',rect_text_use,font,slider_volume_rect,slider_offset_rect)
			elif keys[pg.K_LEFT]:
				if(flag == 0):
					slider_clear(screen,'volume',slider_volume_rect,slider_offset_rect)
					volume = max(0,volume-1)
					slider_draw(screen,volume,'volume',rect_text_use,font,slider_volume_rect,slider_offset_rect)
					if pg.mixer.get_init():
						pg.mixer.music.set_volume(volume/100)
					shared_state.MASTER_VOLUME = volume / 100.0
				elif(flag == 1):
					slider_clear(screen,'local offset',slider_volume_rect,slider_offset_rect)
					offset = max(-1000,offset-10)
					slider_draw(screen,offset,'local offset',rect_text_use,font,slider_volume_rect,slider_offset_rect)
			last_update_time = current_time
		keys = pg.key.get_pressed()
		if keys[pg.K_ESCAPE] and esc_hold_start is not None:
			if pg.time.get_ticks() - esc_hold_start >= 2000:
				pg.quit()
				sys.exit()
		elif not keys[pg.K_ESCAPE]:
			esc_hold_start = None

		pg.display.update()
		clock.tick(60)

	shared_state.MASTER_VOLUME = volume / 100.0
	return action, volume/100.0, offset

pg.init()

text_use = ['volume','local offset','continue','restart','quit']
coordinate_text_use = list()
rect_text_use = list()
slider_volume_rect = list()
slider_offset_rect = list()
volume = 50
offset = 0

#
if __name__ == "__main__":
	screen_size = [(800,600),(1280,760),(1920,1080)] #??????????????????
	size_select = 1 #????????????????????????(?????????????????????????????????????????????????????????????????????)
	screen = pg.display.set_mode(screen_size[size_select])
	run_pause(screen, 0.5, 0)
	pg.quit()
