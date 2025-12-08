import json as js
with open('1709823572.json',encoding = 'utf-8') as file:
	get_content = js.load(file)
	#print(get_content)
note_read = get_content['note'];
print(type(note_read))
print(note_read[0])






