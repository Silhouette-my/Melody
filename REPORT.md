# Melody 🎵

> A programming teamwork in ZJU

## 游戏简介

**Melody** 者，基于 **Pygame** 开发之音游也。

设四轨于屏，音随曲起，符自上而下坠；玩家执键 A / S / K / L，俟符临判线而击之，期与拍合，则中。

其旨在使人闻声知节，按之得趣。

---

## 项目亮点

* **完整的多场景流程**：主菜单 → 选曲 → 游戏 → 暂停 → 设置/校准，体验闭环清晰。
* **四轨按键玩法**：A / S / K / L 对应四条轨道，节奏紧凑，学习成本低，上手即打。
* **延迟校准**：考虑不同设备音频/输入延迟差异，通过跟拍校准提升判定准确度。
* **暂停回拍机制**：暂停返回时先播放 **8 声节拍器**，帮助重新找回节拍，避免“回来就掉链子”。
* **可维护的模块化组织**：按界面/功能拆分文件，逻辑职责清晰，便于课程作业展示与二次迭代。

---

## 操作指南

### 主菜单

* ↑ / ↓：切换菜单项
* Enter：确认

### 选曲界面

* ↑ / ↓：选择曲目
* Enter：开始游戏

### 游戏内

* **A / S / K / L**：四轨道击打
* **Esc**：暂停（进入暂停界面）

### 暂停界面

* ↑ / ↓：选择功能
* ← / →：调节 **音量 / 本地偏移**
* Enter：继续 / 重开 / 退出
* Esc：继续（返回游戏）

从暂停返回游戏时，会根据**当前节拍**先播放 **8 声节拍器**，再继续游戏。

### 设置界面

* **Master Volume**：主音量（左右调整）
* **Latency Calibration**：延迟校准（按提示跟节拍）

进入校准后先播放 **4 声节拍器**，随后音符开始下落并可按提示点击校准。

---

## 文件结构

* `main.py`：主流程与场景切换
* `main_interface.py`：主界面
* `song_selection.py`：选曲逻辑
* `setting.py`：设置与延迟校准
* `pause_interface.py`：暂停界面
* `play_interface_version2_final_version.py`：游戏主逻辑
* **Tip**：修改流速请在`play_interface_version2_final_version.py`中搜索fall_speed自行更改

## main.py 主流程与场景切换
作为主函数，main.py 以状态机的形式对各个状态的执行逻辑进行了规定

### 引入资源
开头先进行对库的引用和其它源代码文件的引用：
```
# 引入使用的库
import pygame
import time
import json
import os
import sys

# 引入已有的模块
import main_interface       # 主菜单
import song_selection       # 选曲界面
import setting              # 设置
import play_interface_version2_final_version as play #游戏主界面 
import shared_state         # 共享状态
```

### 状态机定义
然后是对状态机的各个状态进行规定：
```
STATE_MENU = "menu"     
STATE_SELECT = "select"
STATE_PLAY = "play"
STATE_RESULT = "result"
STATE_SETTING= "setting"
```
这些状态对应前面引入的模块和功能

### 初始化画面、状态和参数
这一部分完成了对游戏基础设置（字体、音量、分辨率、延迟）的初始化
```
def main():
    
    # pygame初始化
    pygame.init()   # pygame自带，对显示、事件、时间、音频、字体等模块进行初始化

    # 定义屏幕和字体
    screen = pygame.display.set_mode((800, 600))      
    font = pygame.font.SysFont(None, 50)    # 使用系统字体和英文以增强适配性，避免发生渲染错误（中文出现方框）

    # 初始化状态和参数
    state = STATE_MENU      # 设置主菜单状态
    title_flag = 0          #
    selected_song = None    # 初始化选歌
    master_volume = 1.0     # 全局音量
    current_latency = 0     # 初始化延迟值（个体差异）
    local_offset = 0        # 初始化本地延迟（机器差异）
    screen_size = (800, 600)    # 设置窗口分辨率


    if pygame.mixer.get_init():     # 如果音频模块已初始化
        pygame.mixer.music.set_volume(master_volume)    # 设置全局音量为前面初始化的结果
    shared_state.MASTER_VOLUME = master_volume  # 同步
```

### 主循环
对各个状态机的执行进行了定义

#### 主菜单
##### 初始化
初始化屏幕、界面选择相关以及 ESC 的判定

```
 while True:
        if state == STATE_MENU:
            # 调用主菜单界面       
            screen.fill((0, 0, 0))  # 填充屏幕为全黑
            text_rect = main_interface.screen_interface(screen, font)   
            # 调用主界面中的函数绘制UI
            last_rect = main_interface.button_border_draw(screen, text_rect, 0)
            # 绘制按钮的高亮边框
            selected_index = 0  # 初始化“选中的按钮”索引为第一个按钮

            # 初始化esc操作
            esc_hold_start = None   
            esc_short_action = None
```

##### 主状态
根据不同按钮定义不同行为
关闭按钮：退出
Enter：确认
上下键：选择
ESC：短按返回，长按退出

```
            running = True
            while running:  # 游戏进行中
                for ev in pygame.event.get():   # 遍历所有事件

                    if ev.type == pygame.QUIT:  # 用户点击关闭按钮
                        # pygame常用的退出
                        pygame.quit()   # 释放pygame模块
                        sys.exit()      # 退出程序

                    elif ev.type == pygame.KEYDOWN:    # 用户按下键盘

                        if ev.key == pygame.K_RETURN:  # Enter 进入选曲
                            if selected_index == 0:     # 进入选曲界面
                                state = STATE_SELECT
                                running = False
                            elif selected_index == 1:   # 进入设置界面
                                state = STATE_SETTING
                                running = False
                            elif selected_index == 2:   # 返回上一层
                                return
                        
                        elif ev.key == pygame.K_ESCAPE:     # ESC键
                            esc_hold_start = pygame.time.get_ticks()    # 记录按下时间区分长按短按
                            esc_short_action = "quit"   #   如果短按就退出
                        
                        elif ev.key == pygame.K_DOWN or ev.key == pygame.K_UP:  # 上下键移动菜单
                            if ev.key == pygame.K_DOWN and selected_index < len(text_rect) - 1:     # 下移（不在边界）
                                main_interface.button_border_clear(screen, last_rect)   # 清除旧高亮边框
                                selected_index += 1
                                last_rect = main_interface.button_border_draw(screen, text_rect, selected_index)    # 重新绘制高亮边框
                            
                            elif ev.key == pygame.K_UP and selected_index > 0:  #上移（不到边界）
                                main_interface.button_border_clear(screen, last_rect)
                                selected_index -= 1
                                last_rect = main_interface.button_border_draw(screen, text_rect, selected_index)

                    elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE: #松开ESC
                        if esc_hold_start is not None and pygame.time.get_ticks() - esc_hold_start < 2000:  # 短按小于两秒，返回上一级
                            return
                        
                        # 长按则清空状态
                        esc_hold_start = None
                        esc_short_action = None

                # 持续检测ESC按键状态
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and esc_hold_start is not None:
                    if pygame.time.get_ticks() - esc_hold_start >= 2000:    
                    # 长按大于两秒，退出
                        pygame.quit()
                        sys.exit()
                elif not keys[pygame.K_ESCAPE]:
                    esc_hold_start = None   # 松开ESC就退出
                pygame.display.update()     # 更新屏幕
```

#### 选曲界面
##### 初始化
```
elif state == STATE_SELECT:
            # 调用选曲界面    
            clock = pygame.time.Clock() # 创建控制帧率的时钟对象
            running = True
            # 初始化ESC检测
            esc_hold_start = None
            esc_short_action = None
```

##### 主状态
和主菜单一样的逻辑
```
            while running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_RETURN:
                            # 确认选曲
                            selected_song = song_selection.file_play[title_flag]    # 导入选歌模块中的函数选歌
                            state = STATE_PLAY  # 跳转到游玩模块
                            running = False

                        elif ev.key == pygame.K_ESCAPE: # ESC 短按返回
                            esc_hold_start = pygame.time.get_ticks()
                            esc_short_action = "back"
                        
                        # 上下切换
                        elif ev.key == pygame.K_DOWN:
                            title_flag = min(title_flag+1, len(song_selection.file_play)-1)

                        elif ev.key == pygame.K_UP:
                            title_flag = max(title_flag-1, 0)

                    # ESC判定
                    elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
                        if esc_hold_start is not None and pygame.time.get_ticks() - esc_hold_start < 2000:
                            state = STATE_MENU
                            running = False
                        esc_hold_start = None
                        esc_short_action = None
                
                # 界面渲染
                screen.fill((0,0,0))
                song_selection.text_draw(title_flag, pygame.font.SysFont(None,50), screen_size, 0)  # 绘制列表文字
                song_selection.attention_draw(screen,screen_size,0) #高亮选中歌曲

                # 检测ESC
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and esc_hold_start is not None:
                    if pygame.time.get_ticks() - esc_hold_start >= 2000:
                        pygame.quit()
                        sys.exit()
                elif not keys[pygame.K_ESCAPE]:
                    esc_hold_start = None

                # 刷新，帧率设为60
                pygame.display.update()
                clock.tick(60)
```

#### 设置界面
通过维护字典 settings 存储用户的设置，更新并将其传入，并根据设置调整参数。
```
elif state == STATE_SETTING:
            # 调用设置模块，返回字典 settings
            settings = setting.run_settings(master_volume, current_latency, screen_size)

            if isinstance(settings, dict):  # 检查settings是不是字典
                # 传入更新的变量
                if "master_volume" in settings:
                    master_volume = settings["master_volume"]
                    shared_state.MASTER_VOLUME = master_volume
                if "latency_ms" in settings:
                    current_latency = settings["latency_ms"]
                if "screen_size" in settings:
                    screen_size = settings["screen_size"]
            
            # 用新的屏幕分辨率重新初始化
            pygame.init()
            screen = pygame.display.set_mode(screen_size)
            font = pygame.font.SysFont(None, 50)

            # 更新新的音量
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(master_volume)

            state = STATE_MENU  #返回主菜单
```

#### 游玩界面
##### 读取 json
从目录下保存的歌曲 json（谱面）中获取相关信息

```
 elif state == STATE_PLAY:

            master_volume = shared_state.MASTER_VOLUME  # 从共享状态中获取音量值

            # 读取选中的歌曲json
            with open(selected_song,'r') as f:  # 以只读模式打开，文件对象赋值给f
                get_content = json.load(f)      # 从json中读取数据并解析成python对象
                note_file = get_content['note'] # 读取note
                length_temp = len(note_file)    # 读取音符数（用来找到最后一个）
                local_offset = note_file[length_temp-1]['offset']   #根据最后一个音符确定本地偏移量
```

##### 调用游玩模块，更新音量

```            
            result,new_local_offset = play.run_game(selected_song, master_volume, current_latency, local_offset, screen_size)   # 调用游玩模块
            
            # 更新音量
            if pygame.mixer.get_init():
                master_volume = pygame.mixer.music.get_volume()
                shared_state.MASTER_VOLUME = master_volume
```

##### 处理重新开始部分
重新加载 json，更新本地偏移

```         
            # 重新开始
            if result == "restart":
                with open(selected_song,'r') as f:
                    data = json.load(f)
                    length_temp = len(data['note'])
                    data['note'][length_temp-1]['offset'] = new_local_offset    # 更新此时最后一个音符的偏移量（因为打到一半偏移量会变）
                with open(selected_song,'w') as f:
                    json.dump(data,f)   # 将其写回文件
                local_offset = new_local_offset     # 更新本地偏移
                continue    # 回到循环开头，即继续运行
```

##### 结束后收拾
```
            # 游戏结束后重置环境
            pygame.init()
            screen = pygame.display.set_mode(screen_size)
            font = pygame.font.SysFont(None, 50)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(master_volume)
            state = STATE_SELECT    # 回到select
```

#### 结果界面（并未启用，留作更新内容）
##### 初始化

```
# STATE_RESULT可删/留着做标准结果呈现界面
        elif state == STATE_RESULT:
            # 简单结果界面
            font = pygame.font.SysFont(None, 50)
            text = font.render("Game Over - Press Enter to return", True, 'white')
            rect = text.get_rect(center=screen.get_rect().center)
            screen.blit(text, rect)
            pygame.display.update()
            waiting = True  # 等待
            esc_hold_start = None
            esc_short_action = None
```

##### 反应
退出按钮：退出
Enter：回到主菜单
ESC：短按返回，长按退出

```
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                        state = STATE_MENU
                        waiting = False
                    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        esc_hold_start = pygame.time.get_ticks()
                        esc_short_action = "back"
                    elif ev.type == pygame.KEYUP and ev.key == pygame.K_ESCAPE:
                        if esc_hold_start is not None and pygame.time.get_ticks() - esc_hold_start < 2000:
                            state = STATE_MENU
                            waiting = False
                        esc_hold_start = None
                        esc_short_action = None
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and esc_hold_start is not None:
                    if pygame.time.get_ticks() - esc_hold_start >= 2000:
                        pygame.quit()
                        sys.exit()
                elif not keys[pygame.K_ESCAPE]:
                    esc_hold_start = None
```

### 结尾
```
if __name__ == "__main__":
    main()
```
防止被别的函数调用

## pause_interface.py 暂停界面

### 引入库
```
import json as js
import os
import numpy as np
import pygame as pg
import time
import shared_state
import sys
```

### text_draw 逐条渲染文本
#### 传入参数
`def text_draw(screen,font,text_use,coordinate,rect_text_use):`
- screen：屏幕上对象
- font：渲染文本使用的字体
- text_use：需要绘制的文本内容列表
- coordinate：坐标与对齐方式列表
- rect_text_use：外部传入，文本的Rect(位置和大小)

#### 函数体
根据参数渲染文本、确定位置并画到screen上
```
# 获取屏幕的宽高
width = pg.Surface.get_width(screen)    
height = pg.Surface.get_height(screen)

# 遍历文本进行渲染
for i in range(len(text_use)):
	text = text_use[i]
	text_image = font.render(text, True, 'white')   # True意为使用抗锯齿
	text_rect = text_image.get_rect()
        
    # 注意：这里x坐标应该是绝对坐标，不是比例
	x_pos = coordinate[i][0]
	y_pos = coordinate[i][1]
        
	if coordinate[i][2] == 'right':  # 右对齐
		text_rect.right = x_pos
		text_rect.centery = y_pos
	elif coordinate[i][2] == 'center':  # 居中
		text_rect.center = (x_pos, y_pos)
    
	rect_text_use.append(text_rect) # 将每个文本的最终位置矩形保存到rect_text_use

    # 绘制到surface（即被创建的 screen）    
	surface = pg.display.get_surface()
	if surface is not None:
		surface.blit(text_image, text_rect) #把text_image 画到 text_rect 标记的区域
```

### coordinate_calculate 计算位置和对齐方式
#### 传入参数
`def coordinate_calculate(width,height,font,coordinate_text_use):`
- width：屏幕宽度
- height：屏幕高度
- font：使用字体
- coordinate_text_use：存储得到的坐标格式

#### 函数体
根据得到的宽和高计算按钮的位置，将其存入coordinate_text_use

```
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
    
    # 让每个按钮之间的间距相等（按钮间有4个间隔：左边界-按钮1，按钮1-按钮2，按钮2-按钮3，按钮3-右边界）
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
```

### button_border_draw 绘制高亮框并返回
#### 传入参数
`def button_border_draw(screen,text_rect,select_flag):`
- screen
- text_rect：select_draw 生成的存放所有文本矩形的列表
- select_flag：当前选中文本的索引

#### 函数体
```
    # 扩展边界，这样边框不紧贴文字，更加美观
    border_x = text_rect[select_flag].x-5
	border_y = text_rect[select_flag].y-5
	border_width = text_rect[select_flag].width+10
	border_height = text_rect[select_flag].height+10

    # 创建边框矩形对象
	last_rect = pg.Rect(border_x, border_y, border_width, border_height)

    # 绘制边框
	border_color = 'white'
	border_line_width = 1   # 指定宽度，避免变成填充
	pg.draw.rect(screen, border_color, last_rect, border_line_width)

	return last_rect    # 返回边框矩形
```

### button_border_clear 清除高亮框（改成黑色）
```
def button_border_clear(screen,last_rect):
	pg.draw.rect(screen,'black',last_rect,1)
```

### slider_draw 绘制滑动条
#### 传入参数
`def slider_draw(screen,value,label,rect_text_use,font,slider_volume_rect,slider_offset_rect):`
- screen
- value：滑动条当前数值
- label：滑动条标签（volume or offset）
- rect_text_use
- font
- slider_volume_rect：存放音量条相关矩形
- slider_offset_rect：存放偏移调相关矩形

#### 函数体
```
    # 获取宽高
    width = pg.Surface.get_width(screen)
	height = pg.Surface.get_height(screen)

    #绘制音量条
	if(label == 'volume'):
		# 获取continue和quit按钮的矩形，rect_text_use[2]是continue, rect_text_use[4]是quit
		continue_rect = rect_text_use[2]
		quit_rect = rect_text_use[4]
		
		# 滑动条的左端与continue左端对齐，右端与quit右端对齐
		slider_left = continue_rect.left
		slider_right = quit_rect.right

        # 计算宽度（百分比）
		slider_width = (slider_right - slider_left)*value/100
		
		# 滑动条的高度与音量文本的高度相同，y位置与音量文本对齐
		slider_height = rect_text_use[0].height
		slider_y = rect_text_use[0].y
		
		# 创建滑动条矩形
		slider_rect = pg.Rect(slider_left, slider_y, slider_width, slider_height)

		# 渲染创建数值矩形
        volume_image = font.render(str(value), True, 'white')
		volume_rect = volume_image.get_rect()
		volume_rect.x = slider_right+20     # 在滑动条右侧显示数值
		volume_rect.y = slider_rect.y
		
        # 把滑动条和数值矩形保存到列表
		slider_volume_rect.append(slider_rect)
		slider_volume_rect.append(volume_rect)

		# 绘制滑动条和数值矩形
		pg.draw.rect(screen, 'white', slider_rect)
		surface = pg.display.get_surface()
		if surface is not None:
			surface.blit(volume_image, volume_rect)

    # 绘制偏移条（几乎同上）
	elif(label == 'local offset'):
		continue_rect = rect_text_use[2]
		quit_rect = rect_text_use[4]
		
		slider_left = continue_rect.left
		slider_right = quit_rect.right
		slider_width = slider_right - slider_left
		
		slider_height = rect_text_use[1].height
		slider_y = rect_text_use[1].y
		
		# 创建滑动条矩形
		slider_rect = pg.Rect(slider_left,slider_y,slider_width,slider_height)

        # 分割左右部分
		slider_left_rect = pg.Rect(slider_left, slider_y, slider_width*(0.5+value/2000), slider_height)
		slider_right_rect = pg.Rect(slider_left+slider_width*(0.5+value/2000),slider_y,slider_width*(0.5-value/2000),slider_height)
		
        # 渲染创建数值矩形
		offset_image = font.render(str(value), True, 'white')
		offset_rect = offset_image.get_rect()
		offset_rect.x = slider_right+20
		offset_rect.y = slider_rect.y
		
		slider_offset_rect.append(slider_rect)
		slider_offset_rect.append(offset_rect)

		# 绘制偏移条和数值矩形
		pg.draw.rect(screen, 'white', slider_left_rect)
		pg.draw.rect(screen,'blue',slider_right_rect)
		surface = pg.display.get_surface()
		if surface is not None:
			surface.blit(offset_image, offset_rect)
```

### slider_clear 清除滑动条
```
def slider_clear(screen,label,slider_volume_rect,slider_offset_rect):
	if(label == 'volume'):
		for i in range(0,2,1):
			pg.draw.rect(screen,'black',slider_volume_rect[i])  # 涂黑
		for i in range(0,len(slider_volume_rect),1):
			del slider_volume_rect[0]   # 清空矩形列表
    
    # 下面同上
	elif(label == 'local offset'):
		for i in range(0,2,1):
			pg.draw.rect(screen,'black',slider_offset_rect[i])
		for i in range(0,len(slider_offset_rect),1):
			del slider_offset_rect[0]
```

### run_pause 暂停核心函数
#### 传入参数
`def run_pause(screen, current_volume, current_offset):`
- screen
- current_volume：字面意思
- current_offset：同上

#### 初始化
```
    # 获取宽高
    width = pg.Surface.get_width(screen)
	height = pg.Surface.get_height(screen)

	clock = pg.time.Clock() # 创建时钟对象控制帧率

	# 针对不同分辨率选择不同字号
    font_size = [30,40,60]
	screen_sizes = [(800,600),(1280,760),(1920,1080)]
	font_size_use = None
	for i in range(0,3,1):
		size = screen_sizes[i]
		if(size == pg.Surface.get_size(screen)):
			font_size_use = font_size[i]
			break
	font = pg.font.SysFont(None,font_size_use)
	screen.fill((0, 0, 0))      # 清屏

	# 文本与坐标初始化
    text_use = ['volume','local offset','continue','restart','quit']        # 菜单中文本
	coordinate_text_use = list()    # 坐标列表
	rect_text_use = list()          # 矩形列表
	slider_volume_rect = list()     # 滑动条矩形列表
	slider_offset_rect = list()

    # 初始化音量和偏移值
	volume = max(0, min(100, int(round(shared_state.MASTER_VOLUME * 100))))
	offset = int(current_offset)

	flag = 0    # 选中的菜单项索引

	coordinate_calculate(width,height,font,coordinate_text_use)     # 计算文本坐标
	text_draw(screen,font,text_use,coordinate_text_use,rect_text_use)       # 绘制文本

    # 绘制滑动条
	slider_draw(screen,volume,'volume',rect_text_use,font,slider_volume_rect,slider_offset_rect)
	slider_draw(screen,offset,'local offset',rect_text_use,font,slider_volume_rect,slider_offset_rect)

	last_rect = button_border_draw(screen,rect_text_use,flag)       # 绘制高亮框

    # 参数初始化
	last_update_time = 0    # 上次按键更新时间
	key_update_delay = 80   # 按键延迟（避免过快重复）
	action = "resume"       # 返回的操作（默认继续）
	esc_hold_start = None   # ESC按下时间
```

#### 主循环
```
	isRunning = True
	while isRunning:
		current_time = pg.time.get_ticks()

        # 处理键盘事件(同主菜单)
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
        
        # 按键检测
		if(current_time - last_update_time > key_update_delay):
			keys = pg.key.get_pressed()
			if keys[pg.K_RIGHT]:    # 右键（调节）
				if(flag == 0):      # 调节音量
					slider_clear(screen,'volume',slider_volume_rect,slider_offset_rect)
					volume = min(100,volume+1)
					slider_draw(screen,volume,'volume',rect_text_use,font,slider_volume_rect,slider_offset_rect)
					if pg.mixer.get_init():
						pg.mixer.music.set_volume(volume/100)
					shared_state.MASTER_VOLUME = volume / 100.0     # 同步音量

				elif(flag == 1):       # 调节偏移
					slider_clear(screen,'local offset',slider_volume_rect,slider_offset_rect)
					offset = min(1000,offset+10)
					slider_draw(screen,offset,'local offset',rect_text_use,font,slider_volume_rect,slider_offset_rect)

			elif keys[pg.K_LEFT]:   # 左键同理
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

			last_update_time = current_time     #更新修改时间

        # 检测ESC    
		keys = pg.key.get_pressed()
		if keys[pg.K_ESCAPE] and esc_hold_start is not None:
			if pg.time.get_ticks() - esc_hold_start >= 2000:
				pg.quit()
				sys.exit()
		elif not keys[pg.K_ESCAPE]:
			esc_hold_start = None

		pg.display.update()     # 刷新帧
		clock.tick(60)      # 限制帧率

	shared_state.MASTER_VOLUME = volume / 100.0
	return action, volume/100.0, offset     # 返回操作与设置
```

### 主函数
#### 定义与初始化
```
pg.init()

# 定义菜单内容和参数
text_use = ['volume','local offset','continue','restart','quit']
coordinate_text_use = list()
rect_text_use = list()
slider_volume_rect = list()
slider_offset_rect = list()
volume = 50
offset = 0
```

### 主程序
```
if __name__ == "__main__":      # 直接运行时才会执行
	screen_size = [(800,600),(1280,760),(1920,1080)] 
	size_select = 1     # 默认分辨率
	screen = pg.display.set_mode(screen_size[size_select])      # 创建screen
	run_pause(screen, 0.5, 0)   # 调用暂停
	pg.quit()
```