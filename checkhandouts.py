# check the statistical averages for !handout

import random

handoutbal = 0
maxho = 0
for i in xrange(1, 101):
    handout = 0
    while True:
        randRoll = random.randint(2, 10)
        handout = handout + randRoll
        if randRoll != 10:
            break
    handoutbal = handoutbal + handout
    maxho = max(maxho, handout)
            
print handoutbal
print maxho