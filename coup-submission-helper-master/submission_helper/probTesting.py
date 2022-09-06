own = ["K", "A"]

import random

class deck:
    def __init__(self):
        unique_cards = ["K", "S", "D", "C", "A"]
        self.deck = []
        for c in unique_cards:
            for i in range(0,3):
                self.deck.append(c)
    
    def shuffle(self):
        random.shuffle(self.deck)
    
    def add_card(se)