import pygame
import random
from pygame.locals import *

pygame.init()

#creating the Game window
GAME_WIDTH = 800
GAME_HEIGHT = 600
SCREEN_SIZE = (GAME_WIDTH,GAME_HEIGHT)
GAME_WINDOW = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Bird Hunter')
PADDING_Y = 50

#Colour variables
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255, 255, 0)

# number of milliseconds before another bullet is fired
BULLET_COOLDOWN = 500

#timestamp of last bullet fired 
LAST_BULLET_TIME = pygame.time.get_ticks()

#time when the next bird will spawn
NEXT_BIRD = pygame.time.get_ticks()


# function for resizing an image
def scale_image(image, NEW_WIDTH):
	IMAGE_SCALE = NEW_WIDTH/image.get_rect().width
	NEW_HEIGHT = image.get_rect().height * IMAGE_SCALE
	scaled_size = (NEW_WIDTH, NEW_HEIGHT)
	return pygame.transform.scale(image, scaled_size)

#load background image
bg=pygame.image.load('bg.png').convert_alpha()
bg = scale_image(bg, GAME_WIDTH)
bg_scroll = 0 

#load and scale the sirplane images
AIRPLANE_IMAGES = []
for i in range(2):
	AIRPLANE_IMAGE = pygame.image.load(f'fly{i}.png').convert_alpha()
	AIRPLANE_IMAGE = scale_image(AIRPLANE_IMAGE, 70)
	AIRPLANE_IMAGES.append(AIRPLANE_IMAGE)

# Loading and scaling the heart umages for representing health
HEART_IMAGES = []
HEART_IMAGE_INDEX =0
for i in range(8):
	HEART_IMAGE = pygame.image.load(f'heart{i}.png').convert_alpha()
	HEART_IMAGE = scale_image(HEART_IMAGE,30)
	HEART_IMAGES.append(HEART_IMAGE)


#List of different bird colors
BIRD_COLOURS = ['blue','grey','red','yellow']

#Dictionary of lists of bird images
BIRD_IMAGES = {}
for COLOR in BIRD_COLOURS:

	#add a new list to the dictionary
	BIRD_IMAGES[COLOR] = []

	#populating the list with images of birds of the same color
	for i in range(4):
		#load and scale bird images
		BIRD_IMAGE = pygame.image.load(f'{COLOR}{i}.png').convert_alpha()
		BIRD_IMAGE = scale_image(BIRD_IMAGE, 50)

		#horizontally flip the image to make the bird face left
		BIRD_IMAGE = pygame.transform.flip(BIRD_IMAGE, True, False) 

		#add the image to the list of its color in the dictionary
		BIRD_IMAGES[COLOR].append(BIRD_IMAGE)


class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x=x
		self.y=y 

		self.lives =3
		self.score =0

		#index of the image to be displayed
		self.IMAGE_Index = 0

		#angle of the image
		self.IMAGE_angle =0

	def update(self):
		#determine next image to display
		self.IMAGE_Index += 1
		if self.IMAGE_Index >= len(AIRPLANE_IMAGES):
			self.IMAGE_Index = 0

		#assigning of the next image
		self.image =AIRPLANE_IMAGES[self.IMAGE_Index]
		self.rect = self.image.get_rect()

		#update the angle of image
		self.image = pygame.transform.rotate(self.image, self.IMAGE_angle)
		self.rect.x = self.x 
		self.rect.y = self.y 

		if pygame.sprite.spritecollide(self, bird_group, True):
			self.lives -=1

class Bullet(pygame.sprite.Sprite):
	
	def __init__(self, x,y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x 
		self.y = y 
		self.radius = 5
		self.rect = Rect(x,y,10,10)

	def draw(self):
		pygame.draw.circle(GAME_WINDOW, YELLOW, (self.x, self.y), self.radius)

	def update(self):
		# move the bullet to the right
		self.x += 2
		self.rect.x = self.x 
		self.rect.y = self.y 

		#remove bullet from sprite group when it goes off screen
		if self.x > GAME_WIDTH:
			self.kill()


class Bird(pygame.sprite.Sprite):
	
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		#starting on the right side of the game window
		self.x = GAME_WIDTH
		#selecting a random y coordinate
		self.y = random.randint(PADDING_Y, GAME_HEIGHT - PADDING_Y *2)
		#select a random color
		self.COLOR = random.choice(BIRD_COLOURS)
		#index of the image to be displayed
		self.IMAGE_Index = 0

		self.image = BIRD_IMAGES[self.COLOR][self.IMAGE_Index]
		self.rect = self.image.get_rect()
		self.rect.x = self.x 
		self.rect.y = self.y 

	def update(self):
		#move left
		self.x -= 2

		#determining next image to display
		self.IMAGE_Index += 0.25 
		if self.IMAGE_Index >= len(BIRD_IMAGES[self.COLOR]):
			self.IMAGE_Index = 0

		#assigning next image
		self.image = BIRD_IMAGES[self.COLOR][int(self.IMAGE_Index)]
		self.rect = self.image.get_rect()
		self.rect.x = self.x 
		self.rect.y = self.y 

		# check if bird collides with bullet
		if pygame.sprite.spritecollide(self, bullet_group, True):
			self.kill()
			player.score += 1

		#remove bird from sprite group when it goes off screen
		if self.x < 0:
			self.kill()



#creating the sprite groups
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

#create the player
PLAYER_X = 30
PLAYER_Y = GAME_HEIGHT // 2
player = Player(PLAYER_X, PLAYER_Y)
player_group.add(player)

#game loop
clock = pygame.time.Clock()
fps = 120
running = True
while  running:
	clock.tick(fps)
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

	KEYS = pygame.key.get_pressed()

	# to move the aeroplane using Arrow KEYS

	if KEYS[K_UP] and player.rect.top > PADDING_Y:
		player.y -= 2
		player.IMAGE_angle = 15
	elif KEYS[K_DOWN] and player.rect.bottom < GAME_HEIGHT - PADDING_Y:
		player.y += 2
		player.IMAGE_angle = -15
	else:
		player.IMAGE_angle = 0

	#shoot bullet with space bar
	if KEYS[K_SPACE] and LAST_BULLET_TIME + BULLET_COOLDOWN < pygame.time.get_ticks():
		bullet_x = player.x + player.image.get_width()
		bullet_y = player.y + player.image.get_height() // 2
		bullet = Bullet(bullet_x,bullet_y)
		bullet_group.add(bullet)
		LAST_BULLET_TIME = pygame.time.get_ticks()

	#spawn a new bird
	if NEXT_BIRD < pygame.time.get_ticks():
		bird = Bird()
		bird_group.add(bird)

		#randomly pick between 0 to 3 seconds when the next bird will spawn
		NEXT_BIRD = random.randint(pygame.time.get_ticks(), pygame.time.get_ticks() +3000 )


	# draw the background
	GAME_WINDOW.blit(bg, (0 - bg_scroll,0))
	GAME_WINDOW.blit(bg, (GAME_WIDTH - bg_scroll,0))
	bg_scroll += 1
	if bg_scroll == GAME_WIDTH:
		bg_scroll = 0

	#draw the player
	player_group.update()
	player_group.draw(GAME_WINDOW)

	#draw the bullets
	bullet_group.update()
	for bullet in bullet_group:
		bullet.draw()

	#draw the birds
	bird_group.update()
	bird_group.draw(GAME_WINDOW)

	#displaying the remaining lives
	for i in range(player.lives):
		HEART_IMAGE = HEART_IMAGES[int(HEART_IMAGE_INDEX)]
		heart_x = 10 + i*(HEART_IMAGE.get_width() + 10)
		heart_y = 10 
		GAME_WINDOW.blit(HEART_IMAGE, (heart_x,heart_y))
	HEART_IMAGE_INDEX += 0.1 
	if HEART_IMAGE_INDEX >= len(HEART_IMAGES):
		HEART_IMAGE_INDEX = 0

	font = pygame.font.Font(pygame.font.get_default_font(), 16)
	text = font.render(f'SCORE: {player.score}', True, BLACK)
	text_rect = text.get_rect()
	text_rect.center = (200, 20)
	GAME_WINDOW.blit(text, text_rect)

	pygame.display.update()

	# Game-Over Conditions
	while player.lives == 0:
		clock.tick(fps)
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
		GAMEOVER_STR = f'Game Over. Play Again (y or n)?'
		font = pygame.font.Font(pygame.font.get_default_font(),24)
		text = font.render(GAMEOVER_STR, True, RED)
		text_rect = text.get_rect()
		text_rect.center = (GAME_WIDTH/2, GAME_HEIGHT/2)
		GAME_WINDOW.blit(text, text_rect)

		keys = pygame.key.get_pressed()
		if keys[K_y]:
			#clear the sprite groups
			player_group.empty()
			bird_group.empty()
			bullet_group.empty()

			#reset the player
			player = Player(PLAYER_X, PLAYER_Y)
			player_group.add(player) 

		elif keys[K_n]:
			running = False
			break 

		pygame.display.update()


pygame.quit()