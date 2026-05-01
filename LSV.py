class Bird:
    def fly(self):
        return "Flying"

class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying"
    
class Ostrich(Bird):
    def fly(self):
        return "Ostrich cannot fly"    

def make_bird_fly(bird: Bird):
    print(bird.fly())

make_bird_fly(Sparrow())
make_bird_fly(Ostrich())