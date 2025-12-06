from abc import ABC, abstractmethod

class Hero(ABC):  # Abstraction
    @abstractmethod
    def attack(self):
        pass

class Batman(Hero):
    def attack(self):
        print("Batman attacks with bats")

class Superman(Hero):
    def attack(self):
        print("Superman attacks with lazer vision")

class SuperHero:
    def __init__(self, hero: Hero):  # The Dependency is an Abstraction
        self.hero = hero

    def perform_attack(self):
        self.hero.attack()

# Usage
batman = Batman()
superman = Superman()
 
# Now we can use any hero that implements the 'Hero' Abstraction class
super_hero1 = SuperHero(batman)
super_hero2 = SuperHero(superman)