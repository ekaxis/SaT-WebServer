import string
import random

def keygen():
    u = ''
    for i in range(32):
        l = string.ascii_lowercase+'_@$&-!'+string.ascii_uppercase
        u+=l[random.randint(0, len(l)-1)]
    return u