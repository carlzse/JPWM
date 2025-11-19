
import pygame
import os
import math 

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60 

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Racing 2D - Kacper Zabiegała")
clock = pygame.time.Clock()

class PlayerCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        try:
            self.original_image = pygame.image.load(os.path.join('.', 'car.png')).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 30))
        except pygame.error:
            
            print("Błąd: Nie znaleziono 'car.png'. Użyto tymczasowego prostokąta.")
            self.original_image = pygame.Surface((50, 30), pygame.SRCALPHA)
            self.original_image.fill(RED) 
            
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        
     
        self.max_speed = 5.0
        self.acceleration = 0.2
        self.deceleration = 0.1
        self.turning_speed = 3.5 

        self.speed = 0.0
        self.angle = 0.0
        
        self.pos = pygame.math.Vector2(self.rect.center) 
        
    def update(self):
        
        radians = math.radians(self.angle)
        
        self.pos.x += self.speed * math.sin(radians)
        self.pos.y -= self.speed * math.cos(radians)
        
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


    def handle_input(self, pressed_keys):
        """Obsługuje wciśnięte klawisze i aktualizuje prędkość/kąt."""
        
       
        if pressed_keys[pygame.K_LEFT]:
            self.angle += self.turning_speed
        if pressed_keys[pygame.K_RIGHT]:
            self.angle -= self.turning_speed

        if pressed_keys[pygame.K_UP]:
           
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
        
        elif pressed_keys[pygame.K_DOWN]:
           
            self.speed -= self.deceleration
           
            if self.speed < -self.max_speed / 2:
                 self.speed = -self.max_speed / 2
        
        else:
           
            if self.speed > 0:
                self.speed -= self.deceleration / 2
                if self.speed < 0.1: 
                    self.speed = 0
            elif self.speed < 0:
                self.speed += self.deceleration / 2
                if self.speed > -0.1: 
                    self.speed = 0

try:
    track_image = pygame.image.load(os.path.join('.', 'track.png')).convert()
    track_image = pygame.transform.scale(track_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    print("Błąd: Nie znaleziono 'track.png'. Użyto zielonego tła.")
    track_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    track_image.fill(GREEN) 


all_sprites = pygame.sprite.Group()
player = PlayerCar()
all_sprites.add(player)

def game_loop():
    global running
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pressed_keys = pygame.key.get_pressed()
        player.handle_input(pressed_keys)


        all_sprites.update()
        
        screen.blit(track_image, (0, 0)) 
        all_sprites.draw(screen) 

        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()