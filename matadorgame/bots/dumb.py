import random

class DumbBot():
    def guess(self, moves):
        number = ''
        rand = random.Random()
        for i in range(4):
            number += str(rand.randint(0, 9))
        return number
