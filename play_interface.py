import json as js
import os
import numpy as np
import pygame as pg
import time
#Malody的'beat'的格式为[x,y,z],代表第x+y/z拍(?)
#
def note_load(note_file,bpm,screen,clock,note_current,rect_note_current,sp,start_time,fall_speed,rank_level_judge):
	#
	length = len(note_file) #note的个数+1(Malody的note信息里面多了一个配置信息)
	bar_delta = 60.0/bpm*4 #一小节的时长
	s_height = pg.Surface.get_height(screen) #获取窗口宽度

	# 获取当前小节位置(基于开始时间)
	current_time = pg.time.get_ticks()/1000.0-start_time #获取当前时间
	current_beat = current_time / bar_delta * 4  # 转换为拍数


	sp = note_judge(note_file,note_current,rect_note_current,current_beat,bar_delta,sp,length,fall_speed,screen) #文件指针，用于查询note的信息

	i = 0
	flag = 0
	while i < len(note_current): #判断是不是读完了note
		column = note_current[i]['column'] #获取note_current中第i+1个note在哪一列
		note_info = note_current[i]['beat'] 
		note_beat = note_info[0] + note_info[1]/note_info[2] #计算拍数x+y/z
		note_time = note_beat/4 * bar_delta #计算该note对应的出现时间
		time_diff = current_time - note_time #计算当前播放时间与该note出现时间之差(显示判断条件)

		if(rect_note_current[i].y > s_height-50):
			rank_level_judge[3] += 1
			last_text_rect = text_draw('miss',screen)
			flag = 1
			note_draw(column,rect_note_current[i],time_diff,fall_speed,screen,flag)
		
		result = note_draw(column,rect_note_current[i],time_diff,fall_speed,screen,flag)	
		if(result == None):
			del note_current[i]
			del rect_note_current[i]
			flag = 0
		else: 
			rect_note_current[i] = result
			i += 1
	clock.tick(100) #维持帧率
	return sp
#
#判断是否要将note加入到note_current中并且给要加入的note初始化rect对象(pygame里面的矩形对象)
def note_judge(note_file,note_current,rect_note_current,current_beat,bar_delta,sp,length,fall_speed,screen):
	while(sp < length):
		tail_note = note_file[sp] #sp指向当前未放入的第一个note
		tail_note_info = tail_note['beat'] 
		tail_note_bar = tail_note_info[0] + tail_note_info[1]/tail_note_info[2] #读取拍数x+y/z
		if(current_beat <= tail_note_bar < current_beat + 8): #如果note的拍数是>当前拍数且<当前拍数+8考虑存入
			#判断当前接收的note是否已经存入
			note_already_added = False
			for existing_note in note_current:
				if(existing_note['beat'] == tail_note_info and existing_note['column'] == tail_note['column']):
					note_already_added = True
					break
            #  
            #如果未存入就存到note_current里  
			if(not note_already_added):
				long_note_flag = 'endbeat' in tail_note #判断tail_note是否是长条
				note_current.append(tail_note) 
			#
			#初始化加入的note的rect对象(不会重复初始化)
				if(not long_note_flag): #正常note初始化rect对象
					s_width = pg.Surface.get_width(screen)
					s_height = pg.Surface.get_height(screen)
					rect = pg.Rect(0,-100,80,10) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
					column_positions = [ #列的位置
						s_width/2-3*50,
						s_width/2-1*50,
						s_width/2+1*50,
						s_width/2+3*50
					]
					rect.centerx = column_positions[tail_note['column']] #矩形中心横坐标
					rect_note_current.append(rect)
				else: #长条初始化rect对象
					end_note_info = tail_note['endbeat'] #获取长条结尾note
					end_note_bar = end_note_info[0] + end_note_info[1]/end_note_info[2] #计算长条结尾note拍数
					note_length = (end_note_bar - tail_note_bar)/4*bar_delta*fall_speed #计算长条长度
					s_width = pg.Surface.get_width(screen)
					s_height = pg.Surface.get_height(screen)
					rect = pg.Rect(0,-100-note_length/2,80,note_length) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
					column_positions = [ #列的位置
						s_width/2-3*50,
						s_width/2-1*50,
						s_width/2+1*50,
						s_width/2+3*50
					]
					rect.centerx = column_positions[tail_note['column']] #矩形中心横坐标
					rect_note_current.append(rect)
			sp += 1
		elif(tail_note_bar >= current_beat + 8): break #如果下一个note的拍数比当前拍数+8还大则直接退出(减运算量)
		elif(sp == length -1): return -1 #note数据读取完毕
	return sp	
#
#
def note_draw(column,last_rect,time_diff,fall_speed,screen,flag):
	if(flag):
		pg.draw.rect(screen,'black',last_rect, 0)
		return None
	else:
		s_height = pg.Surface.get_height(screen)
		if(last_rect.y <= s_height):
			pg.draw.rect(screen,'black',last_rect,0) #用黑色矩形覆盖上一次显示的白色矩形
			last_rect.y = time_diff*fall_speed
			if(time_diff >= -last_rect.height/fall_speed): #只渲染会出现在屏幕里的note,且在其出现前就预渲染好(避免长条渲染出错)
				pg.draw.rect(screen,'white',last_rect,0)
			return last_rect		
#
#
def note_keyboard_judge(keyboard_input,note_current,rect_note_current,start_time,fall_speed,screen,rank_level_judge):
	s_height = pg.Surface.get_height(screen)
	mapping_table = {pg.K_a: 0,
        			 pg.K_s: 1,
        			 pg.K_k: 2,
        			 pg.K_l: 3}
	rank_level = [40,50,80,200]

	if keyboard_input in mapping_table:
		keyboard_map = mapping_table[keyboard_input]
		isKeyuse = True
	else: isKeyuse = False

	if(isKeyuse):
		i = 0
		for note in note_current:
			if(rect_note_current[i].y < (s_height-100)/3*2):
				break
			if(note['column'] == keyboard_map):
				judge_time_diff = np.fabs((rect_note_current[i].y+100.0-s_height)/fall_speed*1000)
				if(judge_time_diff <= 50):
					rank_level_judge[0] += 1
					pg.draw.rect(screen,'black',rect_note_current[i],0)
					text_draw('prefect',screen)
					del note_current[i]
					del rect_note_current[i]
				elif(judge_time_diff <= 80):
					rank_level_judge[1] += 1
					pg.draw.rect(screen,'black',rect_note_current[i],0)
					text_draw('good',screen)
					del note_current[i]
					del rect_note_current[i]
				elif(judge_time_diff <= 120):
					rank_level_judge[2] += 1
					pg.draw.rect(screen,'black',rect_note_current[i],0)
					text_draw('bad',screen)
					del note_current[i]
					del rect_note_current[i]
				else:
					rank_level_judge[3] += 1
					pg.draw.rect(screen,'black',rect_note_current[i],0)
					text_draw('miss',screen)
					del note_current[i]
					del rect_note_current[i]
				pg.display.update()
				break
			else: i += 1

def text_draw(judge,screen):
	s_width = pg.Surface.get_width(screen)
	s_height = pg.Surface.get_height(screen)
	text = judge
	font = pg.font.SysFont(None,57)
	alpha_value = 180

	text_image = font.render(text,True,'gray')
	text_image.set_alpha(alpha_value)
	text_rect = text_image.get_rect()
	text_rect.center = (s_width/2,s_height/3)
	screen.blit(text_image,text_rect)

note_current = []
rect_note_current = []
rank_level_judge = [0,0,0,0]
sp = 0
fall_speed = 800 #下落速度	

pg.init()#pygame初始化
#读取铺面文件所在路径
root = os.getcwd()
path = os.listdir(root)
file_play = list()
#
#找到铺面文件并打开提取bpm和音符信息
for p in path:
	type_file = os.path.splitext(p)
	if(type_file[1] == '.json'):
		file_play.append(p)
file_choose = file_play[0] #此处可手动更改铺面
with open(file_choose,'r',encoding = 'utf-8') as file:
	get_content = js.load(file)
bpm = get_content['time'][0]['bpm'] #提取bpm信息
note = get_content['note'] #提取note信息
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
start_time = pg.time.get_ticks()/1000.0

while isRunning:
	for ev in pg.event.get():
		if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
			isRunning = False
			break
		if(sp == -1):
			isRunning = False
			break
		if(ev.type == pg.KEYDOWN):
			note_keyboard_judge(ev.key,note_current,rect_note_current,start_time,fall_speed,screen,rank_level_judge)
	screen.blit(background, (0, 0))
    
    # 绘制判定线
	for pos in column_positions:
		pg.draw.line(screen, (100, 100, 100), (pos-50, 0), (pos-50, s_height), 2)
    
    # 绘制主要的判定线（note应该到达的位置）
	pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)
	sp = note_load(note,bpm,screen,clock,note_current,rect_note_current,sp,start_time,fall_speed,rank_level_judge)
	pg.display.update()
	clock.tick(100) #两次循环间隔(等价于100帧,保证按键有不响应期)

pg.quit()
#主程序