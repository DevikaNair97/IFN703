import os
import py7zr

path = os. getcwd()
# print(path)
archive = py7zr.SevenZipFile(path + '/sample5.7z')
archive.extractall(path)
archive.close()


