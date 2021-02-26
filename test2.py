from os import listdir
from os.path import isfile, join, abspath
mypath = 'tt'
onlyfiles = [abspath(f) for f in listdir(mypath) if isfile(join(mypath, f))]
pass