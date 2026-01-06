import json as js
import os
import numpy as py
import pygame as pg

def _get_scale_factor(screen_size):
    """获取相对于800x600基准分辨率的缩放因子"""
    base_width, base_height = 800, 600
    width, height = screen_size
    
    # 计算宽高两个方向的缩放比例，取较小值以保证整体适配
    scale_w = width / base_width
    scale_h = height / base_height
    return min(scale_w, scale_h)

def flag_judge(flag_now,file_play_len,lower):
	"""判断当前选中的曲目索引是否到达边界"""
	if(flag_now == lower or flag_now == file_play_len-1):
		return 0;
	else: return 1;

def text_draw(title_flag,font,screen_size,size_select):
	"""在屏幕正中心绘制当前选中的曲目标题"""
	scale_factor = _get_scale_factor(screen_size)
	base_font_size = 50
	font_size = int(base_font_size * scale_factor)
	font = pg.font.SysFont(None, font_size)
	text = title_song[title_flag]
	text_image = font.render(text,True,'white')
	text_rect = text_image.get_rect()

	# 计算屏幕中心位置
	if isinstance(screen_size, (list, tuple)) and len(screen_size) == 2 and isinstance(screen_size[0], int):
		width, height = screen_size
	else:
		width, height = screen_size[size_select]
	text_rect.center = (width//2,height//2)

	# 获取当前显示表面并绘制文字
	surface = pg.display.get_surface()
	if surface is not None:
		surface.blit(text_image,text_rect)
	return text_rect

def attention_draw(screen,screen_size,size_select):
	"""绘制闪烁的提示文字（按Enter开始）"""
	scale_factor = _get_scale_factor(pg.Surface.get_size(screen))
	base_font_size = 30
	font_size = int(base_font_size * scale_factor)
	font_attention = pg.font.SysFont(None, font_size)
	attention = "Press 'Enter' to start"
	attention_image = font_attention.render(attention,True,'white')
	attention_rect = attention_image.get_rect()

	# 计算屏幕中心位置
	if isinstance(screen_size, (list, tuple)) and len(screen_size) == 2 and isinstance(screen_size[0], int):
		width, height = screen_size
	else:
		width, height = screen_size[size_select]
	y_offset = int(50 * scale_factor)
	attention_rect.center = (width//2,height//2+y_offset)

	# 闪烁效果：使用时间控制显示/隐藏
	blink_time = pg.time.get_ticks()/1000
	blink_speed = 1.5 # 闪烁周期（秒）
	blink_duration = 0.8 # 显示持续时间（秒）
	if(blink_time % blink_speed < blink_duration):
		screen.blit(attention_image,attention_rect) # 显示提示文字
	else:
		text_replace(screen,attention_rect) # 隐藏提示文字（用背景色覆盖）

def text_replace(screen,last_rect):
	"""用黑色背景覆盖指定矩形区域（清除文字）"""
	pg.draw.rect(surface = screen, color = 'black',rect = last_rect)

#
pg.init()
# 获取当前工作目录
root = os.getcwd()
path = os.listdir(root)

# 初始化存储列表
file_play = [] # 存储谱面文件路径
title_song = [] # 存储曲目标题

for p in path:
    type_file = os.path.splitext(p) # 分割文件名和扩展名
    if type_file[1] == '.json': # 如果是json文件
        try:
            with open(p, 'r', encoding='utf-8') as file:
                get_content = js.load(file) # 加载json文件

            # 从json中提取曲目标题
            title = get_content.get('meta', {}).get('song', {}).get('title')
            if title:
                file_play.append(p) # 保存文件路径
                title_song.append(title) # 保存曲目标题
            else:
                print(f"⚠️ 跳过无标题文件: {p}")
        except Exception as e:
            print(f"⚠️ 跳过解析失败文件: {p}, 错误: {e}")

print(f"✅ 成功加载 {len(title_song)} 首曲目")
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
	current_size = screen_size[size_select]
	screen = pg.display.set_mode(current_size, pg.RESIZABLE)
	#初始化窗口
	#
	clock = pg.time.Clock()	#计时器
	title_flag = 0 #反映选中曲目在曲目列表内的序号
	last_rect = [(0,0)] #存储上一次显示文字的矩形区域
	font = pg.font.SysFont(None,50) #字体数据初始化
	#要用的变量初始化
	#
	last_rect[0] = text_draw(title_flag,font,current_size,size_select) #绘制曲目列表内第一首歌的标题
	#
	#
	isRunning = True
	
	while isRunning:
		for ev in pg.event.get():
			# 检查边界条件
			bool_down = flag_judge(title_flag,len(title_song),-1)
			bool_up = flag_judge(title_flag,len(title_song)+1,0)
			if(ev.type == pg.QUIT): # 处理窗口关闭事件
				isRunning = False
				break
			elif(ev.type == pg.VIDEORESIZE): # 处理窗口大小调整事件
				current_size = ev.size # 更新当前窗口尺寸
				screen = pg.display.set_mode(current_size, pg.RESIZABLE) # 调整窗口大小
				screen.fill((0, 0, 0)) # 清屏为黑色
				last_rect[0] = text_draw(title_flag,font,current_size,size_select)
			elif(ev.type == pg.KEYDOWN): # 处理键盘按下事件
				if(ev.key == pg.K_DOWN and bool_down): # 向下键：选择下一首曲目
					if(last_rect[0] != (0,0)): #判断上一次是否绘制了标题，如果绘制就先覆盖掉它
						text_replace(screen,last_rect[0])
					title_flag += 1
					last_rect[0] = text_draw(title_flag,font,current_size,size_select)
					break
				elif(ev.key == pg.K_UP and bool_up): # 向上键：选择上一首曲目
					if(last_rect[0] != (0,0)):
						text_replace(screen,last_rect[0])
					title_flag -= 1
					last_rect[0] = text_draw(title_flag,font,current_size,size_select)
					break
		attention_draw(screen,current_size,size_select)
		pg.display.update() #更新屏幕
		clock.tick(60) #两次循环间隔(等价于60帧,保证按键有不响应期)
	
	pg.quit()
	#主程序
