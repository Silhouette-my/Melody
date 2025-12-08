import json as js
import os
import numpy as py
root = os.getcwd()
path = os.listdir(root)
file_play = list()
for p in path:
	type_file = os.path.splitext(p)
	#print(type_file[1])
	if(type_file[1] == '.json'):
		file_play.append(p)
for i in range(0,len(file_play),1):
	use_file = file_play[i]
	with open(use_file,'r',encoding = 'utf-8') as file:
		get_content = js.load(file)
		#print(get_content)
	meta_read = get_content['meta']
	note_read = get_content['note']
	print(meta_read,'\n')
	print(note_read)






