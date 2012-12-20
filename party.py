import os, pygame, random
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
size = width, height = 400, 300
score_width = 20

#functions to create our resources
def load_image(name, name2=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
        if name2:
            image1 = image.convert_alpha()
            image2 = pygame.image.load(os.path.join(data_dir, name2))
            image2 = image2.convert_alpha()
            w = max(image2.get_width(), image1.get_width())
            h = max(image2.get_height(), image1.get_height())
            image = pygame.Surface((w,h), pygame.SRCALPHA, 32)
            image = image.convert_alpha()
            image.blit(image2, (1,1))
            image.blit(image1, (round(w/2 - image1.get_width()/2), 1))
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert_alpha()
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound

class Tanya(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('party-tanya.png')
    
    def update(self):
        "move tanya based on mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos

    def drink(self, targets):
        return self.rect.collidelist([t.rect for t in targets])

    def check(self, foes):
        return self.rect.collidelist([f.rect for f in foes]) >= 0

class Partier(pygame.sprite.Sprite):
    def __init__(self, img_name, friendliness):
        self.friendliness = friendliness
        friendliness_img = friendliness + '.png'
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img_name, friendliness_img)
        screen = pygame.display.get_surface()
        self.rect.topleft = (random.randrange(width-self.rect.width),
                             random.randrange(height-self.rect.height))
        self.rightspeed = ((-1)**random.randrange(2))*random.randrange(1,3)
        self.downspeed = ((-1)**random.randrange(2))*random.randrange(1,3)
        self.talking = 0

    def update(self):
        if self.talking:
            self._still()
        else:
            self._wander()

    def _wander(self):
        newpos = self.rect.move(self.rightspeed, self.downspeed)
        if self.rect.left < 0 or self.rect.right > width:
            self.rightspeed = -self.rightspeed
            newpos = self.rect.move(self.rightspeed, self.downspeed)
        if self.rect.top < 0 or self.rect.bottom > height:
            self.downspeed = -self.downspeed
            newpos = self.rect.move(self.rightspeed, self.downspeed)
        self.rect = newpos

    def _still(self):
        self.talking += 1
        if self.talking >= 300:
            self.talking = 0

class Drink(pygame.sprite.Sprite):
    def __init__(self, img_name):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(img_name)
        screen = pygame.display.get_surface()
        self.rect.topleft = (random.randrange(width-self.rect.width),
                             random.randrange(height-self.rect.height))
        self.drunk = 0

    def update(self):
        if self.drunk:
            self.rect.topleft = width, height

class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()
        self.score = 0
        self.font = pygame.font.Font(None, 24)
        self.image = self.font.render(str(self.score), 1, (10, 10, 10))
        self.rect = self.image.get_rect()
        self.rect.topleft = width - 30, height - 30

    def update(self):
        self.image = self.font.render(str(self.score), 1, (10, 10, 10))

    def add(self, amount):
        self.score += amount

    def subtract(self, amount):
        self.score -= amount
        

def main():
#initialize everything
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Party')
    pygame.mouse.set_visible(0)

#create the background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((192, 192, 192))

#put text on the background
    if pygame.font:
        font = pygame.font.Font(None, 14)
        linespace = 0
        for line in ["You're at a party! Click on drinks "
                     "and spend time near friends to increase ",
                     "your score. But stay clear of your "
                     "enemies! Foes have fire behind them to ",
                     "show that you really don't want "
                     "to talk to them. At 500 points, you win!"]:
            text = font.render(line, 1, (10, 10, 10))
            textpos = text.get_rect(centerx=(width - score_width)/2,
                                    y=(height - 30 + linespace))
            background.blit(text, textpos)
            linespace += 8

#display the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#prepare game objects
    tanya = Tanya()
    drinks = [Drink(img) for img in ['beer-bottle.png',
                                     'beer-can.png',
                                     'martini.png',
                                     'red-cup.png',
                                     'wine.png']]
    partier_images = ['party-girl-pink.png',
                      'party-girl-yellow.png',
                      'party-girl-blue.png',
                      'party-girl-gray.png',
                      'party-boy-gray.png',
                      'party-boy-black.png',
                      'party-boy-red.png',
                      'party-boy-blue.png']
    partier_friendliness = ['friend']*4 + ['foe']*4
    random.shuffle(partier_friendliness)
    partiers = [Partier(partier_images[i], partier_friendliness[i]) 
                for i in range(len(partier_images))]
    score = Score()
    allsprites = pygame.sprite.RenderPlain(( partiers + 
                                             drinks + 
                                             [tanya, score] ))
    foes = filter( (lambda p: p.friendliness == 'foe'), partiers)
    friends = filter( (lambda p: p.friendliness == 'friend'), partiers)
    clock = pygame.time.Clock()

#main loop
    while 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                d = tanya.drink(drinks) #the drink tanya clicked on
                if d >= 0:
                    drinks[d].drunk = 1
                    score.add(100)

        if score.score < 500:
            if tanya.check(foes):
                score.subtract(10)

            if tanya.check(friends):
                score.add(2)

            allsprites.update()
            #draw everything
            screen.blit(background, (0, 0))
            allsprites.draw(screen)

        else:
            score.score = 500
            font = pygame.font.Font(None, 36)
            text = font.render( "YOU WIN!!", 1, (250, 0, 0))
            textpos = text.get_rect(centerx=width/2,
                                    y=height/2)
            screen.blit(background, (0, 0))
            allsprites.draw(screen)
            screen.blit(text, textpos)

        pygame.display.flip()

    pygame.quit()

#game over

if __name__ == '__main__':
    main()
