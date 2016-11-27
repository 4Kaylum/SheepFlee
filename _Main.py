import pygame
from random import randint as rnum
from math import sqrt, atan2, degrees, sin, radians

'''
* Sheep must flee from the mouse
'''

_GlobalWindowMaxSize = [500, 500]
_GlobalDefaultBackground = [39, 95, 32]  # [255, 255, 255]


class Sheep(pygame.sprite.Sprite):
    '''Fuck you I'm making a better sheep game'''
    sheepLabel = 0  # This is the she sheep can be labelled

    def __init__(self, *, size=15, center=[0, 0], colour=[0, 0, 0], border=1):
        '''Create the sheep object'''
        super().__init__()  # Init the class' Pygame sprite process

        # Store anything relevant
        self.center = center
        self.colour = colour
        self.border = border
        self.label = Sheep.sheepLabel

        # Generate the actual image
        self.image = pygame.Surface([size, size])
        self.rect = self.image.get_rect()
        self.backgroundImage = pygame.Surface(
            [size - (2 * border), size - (2 * border)])
        self.backgroundRect = self.backgroundImage.get_rect()
        self.rect.center = self.backgroundRect.center = self.center

        # Increment the sheep label for the other sheepies to enjoy
        Sheep.sheepLabel += 1

    def drawSheepCircle(self, window):
        '''Draw self to screen - is own function to directly use draw function'''
        pygame.draw.ellipse(window, [255, 255, 255], self.backgroundRect, 0)
        pygame.draw.ellipse(window, self.colour, self.rect, self.border)
        z, y = self.makeFont()
        window.blit(z, y)

    def distanceFromPoint(self, point):
        '''Gives the distance of the center of the sheep from a point'''
        distance = sqrt((self.center[0] - point[0])**2 +
                        (self.center[1] - point[1])**2)
        return distance

    def moveSheep(self, point, adjust=False):
        '''Moves the center of the sheep to a particular point'''
        if adjust:
            point = [point[0] + self.center[0], point[1] + self.center[1]]
        self.rect.center = self.backgroundRect.center = point
        self.center = point

    def mouseProximity(self):
        '''Sees if the mouse is close enough for the sheep to want to move'''
        if self.distanceFromPoint(pygame.mouse.get_pos()) <= 50:
            # print('too close {}'.format(rnum(0,100)))
            self.flee()
            # return True
        return False

    def flee(self):
        '''Move the sheep as according to the flee functionality'''
        mus = pygame.mouse.get_pos()
        # Gives the angle from which to reverse at
        angle = self.angleFromPoint(mus)
        moveBy = self.moveAngle(-5, angle)
        print(moveBy)
        self.moveSheep(moveBy, True)

    def moveAngle(self, amountToMove, angleToMove):
        '''Gives the change in x and y you need to move by an amount at a given angle'''
        # Make sure the x and y are the correct polarity
        quadrant = 0
        while angleToMove > 90:
            angleToMove -= 90
            quadrant += 1

        # Use sine rule to get correct distances
        x = amountToMove * sin(radians(180 - (angleToMove + 90)))
        y = amountToMove * sin(radians(angleToMove))

        # Correct the polarity
        x = x * {0: -1, 1: -1, 2: 1, 3: 1}[quadrant]
        y = y * {0: -1, 1: 1, 2: 1, 3: -1}[quadrant]

        # Return to user
        return x, y

    def makeFont(self, *, size=20, colour=[0, 0, 0]):
        '''Draw font onto the screen at a given coordinate'''
        font = pygame.font.Font(None, size)
        text = font.render(str(self.label), 1, colour)
        text.get_rect().center = self.center
        return text, self.getOffsetCenter(text)

    def getOffsetCenter(self, textObject):
        '''Used by makeFont in order to get the offset needed
        to add the text in the right position'''
        c = self.center
        w, h = textObject.get_rect().width, textObject.get_rect().height
        return [c[0] - (w / 2), c[1] - (h / 2)]

    def angleFromPoint(self, point):
        '''Gives the angle between two different points'''
        dy = self.center[1] - point[1]
        dx = self.center[0] - point[0]
        z = atan2(dx, dy)
        return degrees(z) if z > 0 else 360 - abs(degrees(z))


class Block(pygame.sprite.Sprite):
    '''A plain coloured block that the window can draw'''

    def __init__(self, *, topleft, colour, dimensions):
        super().__init__()
        self.image = pygame.Surface(dimensions)
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.rect.x = topleft[0]
        self.rect.y = topleft[1]


# This is the list of borders at 5 pixels for the windowsize
_GlobalBorderSize = 10
_GlobalBorderColour = [0, 0, 0]
_GlobalBorder = [Block(topleft=[0, 0], dimensions=[_GlobalBorderSize, _GlobalWindowMaxSize[1]], colour=_GlobalBorderColour),
                 Block(topleft=[0, 0], dimensions=[
                       _GlobalWindowMaxSize[0], _GlobalBorderSize], colour=_GlobalBorderColour),
                 Block(topleft=[_GlobalWindowMaxSize[0] - _GlobalBorderSize, 0],
                       dimensions=[_GlobalBorderSize, _GlobalWindowMaxSize[1]], colour=_GlobalBorderColour),
                 Block(topleft=[0, _GlobalWindowMaxSize[1] - _GlobalBorderSize], dimensions=[_GlobalWindowMaxSize[0], _GlobalBorderSize], colour=_GlobalBorderColour)]


class Window():
    '''Create the window object on which to draw and check events'''

    def __init__(self, *, dimensions=_GlobalWindowMaxSize, title="None", fps=30):
        '''Create the window object'''
        pygame.init()  # Initialize the pygame module
        pygame.font.init()  # Initialize the pygame font module
        self.clock = pygame.time.Clock()  # Create the fpsTicker
        self.fps = fps

        # Create the window itself
        self.window = pygame.display.set_mode(dimensions)
        pygame.display.set_caption(title)
        self.window.fill(_GlobalDefaultBackground)
        self.borderImages = pygame.sprite.Group()
        for i in _GlobalBorder:
            self.borderImages.add(i)

        # Create the list of sheepies
        self.sheepList = pygame.sprite.Group()
        self.sheepArray = []

        # Store all the events of the last pass
        self.events = None
        self.run(tick=False)

    def drawBackground(self):
        '''Draws only the background onto the window'''
        self.window.fill(_GlobalDefaultBackground)
        self.borderImages.draw(self.window)

    def drawSheep(self):
        '''Draw the sheep onto the screen'''
        [i.drawSheepCircle(self.window) for i in self.sheepList]

    def drawAll(self):
        '''Run all of the class' draw functions'''
        self.drawBackground()
        pygame.draw.circle(
            self.window, [255, 0, 0], pygame.mouse.get_pos(), 50)  # Completely debug. I think.
        self.drawSheep()

    def newSheep(self, locationList, *, size=15, colour=[0, 0, 0], border=2):
        '''Create a list of sheep objects as given by a list of locations'''
        locationList = locationList if type(
            locationList) == list else [locationList]
        for i in locationList:
            self.sheepArray.append(
                Sheep(center=i, colour=colour, border=border, size=size))
            self.sheepList.add(self.sheepArray[-1])

    def randomNewSheep(self, amount=1, *, size=15, colour=[0, 0, 0], border=2):
        '''Creates a certain amount of random sheep, as given'''
        z = []
        for i in range(amount):
            z.append([rnum(5, _GlobalWindowMaxSize[0] - _GlobalBorderSize),
                      rnum(5, _GlobalWindowMaxSize[1] - _GlobalBorderSize)])
        self.newSheep(z, size=size, colour=colour, border=border)

    def checkQuit(self):
        '''Returns false if the user pressed quit'''
        for e in self.events:
            if e.type == pygame.QUIT:
                return False
        return True

    def run(self, update=True, *, tick=True, first=False):
        '''Allows the actual window to tick and run and stuff'''
        if first:
            self.randomNewSheep(1, size=30, border=3)
        if tick:
            self.clock.tick(self.fps)
        if update:
            self.drawAll()
            pygame.display.flip()
        self.events = pygame.event.get()
        [i.mouseProximity() for i in self.sheepList]


def run():
    '''Run the program'''
    window = Window()  # Create window
    window.run(first=True)
    while window.checkQuit():  # Check quit button not pressed
        window.run()  # Window's run function


if __name__ == '__main__':
    run()
    pygame.quit()
