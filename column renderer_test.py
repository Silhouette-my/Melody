#undone
import json as js
import os
import numpy as py
import pygame as pg
#Malody的'beat'的格式为[x,y,z],代表第x小节的第y/z份
#
<<<<<<< Updated upstream
def note_load(note_file,bpm,screen,clock,note_current,rect_note_current,start_time):
	#
	length = len(note_file) #note的个数+1(Malody的note信息里面多了一个配置信息)
	bar_delta = 60.0/bpm*4 #一小节的时长
	s_height = pg.Surface.get_height(screen) #获取窗口宽度

	# 获取当前小节位置（基于开始时间）
	current_time = pg.time.get_ticks()/1000.0-start_time
	current_beat = current_time / bar_delta * 4  # 转换为拍数

	note_judge(note_file,note_current,rect_note_current,current_beat,length,screen)

	i = 0
	while i < len(note_current): #判断是不是读完了note
		column = note_current[i]['column'] #获取note_current中第i+1个note在哪一列
		note_info = note_current[i]['beat']
		note_beat = note_info[0]*bar_delta + note_info[1]/note_info[2]
		note_time = note_beat/4 * bar_delta
		time_diff = current_time - note_time
		fall_speed = 800

		rect_note_current[i] = note_draw(column,rect_note_current[i],time_diff,fall_speed,screen)

		if(rect_note_current[i].y > s_height):  #如果note运动出窗口,将该note从note_current和rect_note_current中移除
			del note_current[i]
			del rect_note_current[i]
		else: i += 1
	clock.tick(100) #控制循环间隔时间，实现note在一个小节中y/z处的效果
=======
def note_load(note_file,bpm,screen,clock):
	length = len(note_file) #note的个数+1(Malody的note信息里面多了一个配置信息)
	bar_delta = 60/bpm #一小节的时长
	s_height = pg.Surface.get_height(screen) #获取窗口宽度
	sp = 0
	note_current = list();
	rect_note_current = list()
	while(sp != -1): #判断是不是读完了note
		present_time = pg.time.get_ticks()/1000 #获取从程序开始以来的持续时间
		bar_count = int(present_time/bar_delta) #计算现在在哪一个小节
		sp = note_judge(note_file,note_current,rect_note_current,bar_count,sp,length,screen)
		for i in range(0,len(note_current),1):
			column = note_current[i]['column'] #获取note_current中第i+1个note在哪一列
			note_bar_div = note_current[i]['beat'][1]/note_current[i]['beat'][2] #计算note_current中第i+1个note在一个小节中的y/z处
			rect_note_current[i] = note_draw(column,rect_note_current[i],screen)
			if(rect_note_current[i].y > s_height):  #如果note运动出窗口,将该note从note_current和rect_note_current中移除
				del note_current[i]
				del rect_note_current[i]
			clock.tick(bar_delta*note_bar_div*5) #控制循环间隔时间，实现note在一个小节中y/z处的效果
>>>>>>> Stashed changes
#
#判断是否要将note加入到note_current中并且给要加入的note初始化rect对象(pygame里面的矩形对象)
def note_judge(note_file,note_current,rect_note_current,current_beat,length,screen):
	for note in note_file:
		if 'beat' in note and 'column' in note:
			beat_info = note['beat']
			note_bar = beat_info[0] + beat_info[1] / beat_info[2]
		if(current_beat <= note_bar < current_beat + 8): #如果note的小节数是当前小节数+2就要存入
			note_already_added = False
			for existing_note in note_current:
				if(existing_note['beat'] == note['beat'] and existing_note['column'] == note['column']):
					note_already_added = True
					break
                
			if(not note_already_added):
				note_current.append(note) 

			#初始化加入的note的rect对象(不会重复初始化)
				s_width = pg.Surface.get_width(screen)
				s_height = pg.Surface.get_height(screen)
<<<<<<< Updated upstream
				rect = pg.Rect(0,-100,80,10) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
				column_positions = [
					s_width/2-3*50,
					s_width/2-1*50,
					s_width/2+1*50,
					s_width/2+3*50
				]
				rect.centerx = column_positions[note['column']]
=======
				rect = pg.Rect(0,0,40,10) #rect对象的格式为(x,y,width,height),(x,y)是矩形左上角的坐标,剩下的是长宽
>>>>>>> Stashed changes
				rect_note_current.append(rect)
#
#
def note_draw(column,last_rect,time_diff,fall_speed,screen):
    s_width = pg.Surface.get_width(screen)
    s_height = pg.Surface.get_height(screen)
    
    column_positions = [
        s_width/2-3*50,  
        s_width/2-1*50,  
        s_width/2+1*50, 
        s_width/2+3*50 
    ]
    
    # 清除上一帧的note
    pg.draw.rect(screen, (0, 0, 0), last_rect)
    
    # 更新位置（基于时间差和下落速度）
    last_rect.centerx = column_positions[column]
    last_rect.y = time_diff * fall_speed  # 从y=100开始下落
    
    # 绘制新的note
    if time_diff >= 0:  # 只绘制已经出现的note
        pg.draw.rect(screen, (255, 255, 255), last_rect)
    
    return last_rect		
#
#
note_current = []
rect_note_current = []

<<<<<<< Updated upstream
=======
				sp += 1
			elif(tail_note_bar > bar_count+2): break #如果note的小节数比当前小节数+2要大就退出循环(文件里note按小节从小到大顺序排列)
		return sp
	elif(sp == length-1): return -1 #相当于是读完了所有的note就让显示结束
#
#
def note_draw(column,last_rect,screen):
	s_width = pg.Surface.get_width(screen)
	s_height = pg.Surface.get_height(screen)
	rect = pg.Rect(0,0,40,10)
	if(last_rect == rect): #判断传输进来的note是否是第一次显示
		if(column == 0):
			last_rect.center = (s_width/2-3*25,0) #center是rect对象的隐藏属性，代表矩形中心的坐标
			pg.draw.rect(screen,'white',last_rect, 0)
			pg.display.update()
			return last_rect
		elif(column == 1):
			last_rect.center = (s_width/2-1*25,0)
			pg.draw.rect(screen,'white',last_rect, 0)
			pg.display.update()
			return last_rect
		elif(column == 2):
			last_rect.center = (s_width/2+1*25,0)
			pg.draw.rect(screen,'white',last_rect, 0)
			pg.display.update()
			return last_rect
		elif(column == 3):
			last_rect.center = (s_width/2+3*25,0)
			pg.draw.rect(screen,'white',last_rect, 0)
			pg.display.update()
			return last_rect
	elif(last_rect.y <= s_height):
		pg.draw.rect(screen,'black',last_rect,0) #用黑色矩形覆盖上一次显示的白色矩形
		last_rect.y += 30 #note的y坐标+5
		pg.draw.rect(screen,'white',last_rect,0)
		pg.display.update()
		return last_rect		
#
#	
>>>>>>> Stashed changes
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
file_choose = file_play[0]
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
    s_width/2+3*50
]

clock = pg.time.Clock()	#计时器
isRunning = True
start_time = pg.time.get_ticks()/1000.0

while isRunning:
	for ev in pg.event.get():
		if(ev.type == pg.QUIT): #保证点右上角的x退出时不会卡死
			isRunning = False
			break
	screen.blit(background, (0, 0))
    
    # 绘制判定线
	for pos in column_positions:
		pg.draw.line(screen, (100, 100, 100), (pos, 0), (pos, s_height), 2)
    
    # 绘制主要的判定线（note应该到达的位置）
	pg.draw.line(screen, (255, 200, 0), (0, s_height - 100), (s_width, s_height - 100), 3)
	note_load(note,bpm,screen,clock,note_current,rect_note_current,start_time)
	pg.display.update()
	clock.tick(100) #两次循环间隔(等价于60帧,保证按键有不响应期)

pg.quit()
#主程序