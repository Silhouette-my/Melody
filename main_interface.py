import json as js
import os
import numpy as py
import pygame as pg

#绘制主界面的start,settings,quit
MENU_ITEMS = ["Start", "Settings", "Exit"]

def _get_scale_factor(screen_size):
    """获取相对于800x600基准分辨率的缩放因子"""
    base_width, base_height = 800, 600
    width, height = screen_size
    
    # 计算宽高两个方向的缩放比例，取较小值以保证整体适配
    scale_w = width / base_width
    scale_h = height / base_height
    return min(scale_w, scale_h)

def screen_interface(screen,font):
	scale_factor = _get_scale_factor(pg.Surface.get_size(screen))
	font_size = int(50 * scale_factor)
	font = pg.font.SysFont(None, font_size) #字体数据初始化
	font_title = pg.font.SysFont(None, int(80*scale_factor))
	# 绘制主界面的菜单项（开始、设置、退出）
	text = MENU_ITEMS
	text_image = list()
	text_rect = list()
	s_width = pg.Surface.get_width(screen)
	s_height = pg.Surface.get_height(screen)
	mid_pos = (s_width//2,s_height//2)

	title = "Melody"
	title_image = font_title.render(title,True,'white')
	title_rect = title_image.get_rect()
	# 根据缩放因子调整水平间距
	spacing_multiplier = 2 * scale_factor

	y_offset = 28 *spacing_multiplier
	title_rect.center = (mid_pos[0],mid_pos[1] - y_offset)
	screen.blit(title_image,title_rect)
    # 先计算所有文本的宽度
	item_widths = []
	for item in text:
		text_surface = font.render(item, True, 'white')
		item_widths.append(text_surface.get_width())
    
    # 计算总宽度和间距
	total_width = sum(item_widths)
	spacing = s_width / 15 * scale_factor  # 使用固定比例的间距
    
    # 计算起始x位置，使整个菜单水平居中
	start_x = mid_pos[0] - (total_width + spacing * (len(text) - 1)) / 2
    
    # 绘制菜单项，保持均匀间距
	current_x = start_x
	for i, item in enumerate(text):
		text_images = font.render(item, True, 'white')
		text_rects = text_images.get_rect()
        
        # 设置文本位置
		text_rects.center = (current_x + item_widths[i]/2, mid_pos[1] + y_offset)
		screen.blit(text_images, text_rects)
        
		text_image.append(text_images)
		text_rect.append(text_rects)
        
        # 更新下一个项的位置：当前位置 + 文本宽度 + 间距
		current_x += item_widths[i] + spacing
	return text_rect

#绘制选项提示框
def button_border_draw(screen,text_rect,select_flag):
	scale_factor = _get_scale_factor(pg.Surface.get_size(screen))
	border_x = text_rect[select_flag].x-int(5 * scale_factor)
	border_y = text_rect[select_flag].y-int(5 * scale_factor)
	border_width = text_rect[select_flag].width+int(10 * scale_factor)
	border_height = text_rect[select_flag].height+int(10 * scale_factor)
	last_rect = pg.Rect(border_x, border_y, border_width, border_height) # 创建边框矩形
	border_color = 'white'
	border_line_width = max(1, int(scale_factor))
	pg.draw.rect(screen, border_color, last_rect, border_line_width)
	return last_rect

#清除上一次的选项提示框
def button_border_clear(screen,last_rect):
	pg.draw.rect(screen,'black',last_rect,1)

if __name__ == "__main__":
	pg.init()
	screen_size = [(800,600),(1280,760),(1920,1080)] #窗口大小规格
	size_select = 0 #窗口大小规格选择(还没做自己选择的功能，但可以在程序内手动改数值)
	button_select_flag = 0
	screen = pg.display.set_mode(screen_size[size_select], pg.RESIZABLE)
	#初始化窗口

	# 计算初始缩放因子
	scale_factor = _get_scale_factor(screen_size[size_select])
	#
	clock = pg.time.Clock()	#计时器
	base_font_size = 50
	font_size = int(base_font_size * scale_factor)
	font = pg.font.SysFont(None, font_size) #字体数据初始化
	text_rect = screen_interface(screen,font)
	last_rect = button_border_draw(screen,text_rect,button_select_flag)
	#要用的变量初始化
	
	isRunning = True
	
	while isRunning:
		for ev in pg.event.get():
			if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
				isRunning = False
				break
			elif(ev.type == pg.VIDEORESIZE): # 处理窗口大小调整事件
				screen = pg.display.set_mode(ev.size, pg.RESIZABLE)
				scale_factor = _get_scale_factor(ev.size)
                
                # 重新计算字体大小
				font_size = int(base_font_size * scale_factor)
				font = pg.font.SysFont(None, font_size)

				screen.fill((0, 0, 0))
				text_rect = screen_interface(screen,font,scale_factor)
				last_rect = button_border_draw(screen,text_rect,button_select_flag)
			elif(ev.type == pg.KEYDOWN): # 处理键盘按下事件
				if(ev.key == pg.K_RIGHT):
					if(button_select_flag < 2):
						button_border_clear(screen,last_rect)
						button_select_flag += 1
						last_rect = button_border_draw(screen,text_rect,button_select_flag)
					elif(button_select_flag >= 2):
						button_select_flag = 2
					break
				elif(ev.key == pg.K_LEFT):
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
