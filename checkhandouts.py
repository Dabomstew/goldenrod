# check the statistical averages for !handout

import random

handoutbal = 0
maxho = 0
genwunmisses = 0
for i in xrange(1, 1000001):
    handout = 0
    while True:
        randRoll = random.randint(1, 10)
        handout = handout + randRoll
        if randRoll != 10:
            break
            
    if random.randint(1,256) == 256:
        handout = 0
        genwunmisses += 1
    handoutbal = handoutbal + handout
    maxho = max(maxho, handout)
            
print handoutbal
print maxho
print genwunmisses