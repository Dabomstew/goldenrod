# check the statistical averages for !handout

import random

handoutbal = 0
maxho = 0
saidPlease = False
freq = {}

for i in xrange(1, 10000001):
    handout = 0
    while True:
        doContinue = False
        if handout >= 10:
            randRoll = random.randint(0, 10)
            doContinue = (randRoll == 10) or (random.randint(1, 100) == 1) # preserve 1/10 chance of continuing [1/11 + 10/11*1/100]
        else:
            randRoll = random.randint(1, 10)
            doContinue = (randRoll == 10)
        
        if saidPlease:
            randRoll = max(randRoll, random.randint(0, 8))
        
        if doContinue:
            handout = handout + 10
        else:
            handout = handout + randRoll
            break
            
    if random.randint(1,256) == 256:
        handout = 0
        
    if handout in freq:
        freq[handout] += 1
    else:
        freq[handout] = 1
        
    handoutbal = handoutbal + handout
    maxho = max(maxho, handout)
            
print handoutbal
print maxho
print freq