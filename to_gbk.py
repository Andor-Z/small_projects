import os
def get_filename():
	'''
	将目录中的文件全部改成gbk编码的文件，放在encode 文件夹中
	'''
	path = r'D:\BaiduYunDownload\6.00.1x Introduction to Computer Science and Programming Using Python\中文字幕 - 副本'
	newdir = path+'\\encoded'

	if os.path.exists(newdir):
		pass
	else:
		os.mkdir(path+'\\encoded')


	
	for root, dirs, files in os.walk(path):
		for name in files:
			filename = root + '\\' + name
			fo = open(filename, 'r',encoding = 'utf8',errors = 'ignore')
			fr = fo.read()
			print(type(fr))
			rfname = r'D:\BaiduYunDownload\6.00.1x Introduction to Computer Science and Programming Using Python\中文字幕 - 副本\encoded' + '\\'+name
			rf = open(rfname, 'w', encoding = 'gbk', errors = 'ignore')
			rf.write(str(fr))
			print(rfname)
			rf.close()
			fo.close


get_filename()

