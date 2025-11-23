import pygame
import os
import math
import random
import time

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60 

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Racing 2D - Kacper Zabiegała")
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

class PlayerCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        try:
            self.original_image = pygame.image.load(os.path.join('.', 'car.png')).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 30))
        except pygame.error:
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
        
        self.pos.x = max(20, min(self.pos.x, SCREEN_WIDTH - 20))
        self.pos.y = max(20, min(self.pos.y, SCREEN_HEIGHT - 20))
        
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def handle_input(self, pressed_keys):
        """Obsługuje wciśnięte klawisze."""
        
        if pressed_keys[pygame.K_LEFT]:
            self.angle += self.turning_speed
        if pressed_keys[pygame.K_RIGHT]:
            self.angle -= self.turning_speed

        if pressed_keys[pygame.K_UP]:
            self.speed += self.acceleration
            self.speed = min(self.speed, self.max_speed)
        
        elif pressed_keys[pygame.K_DOWN]:
            self.speed -= self.deceleration
            self.speed = max(self.speed, -self.max_speed / 2)
        
        else:
            if abs(self.speed) > 0.1:
                self.speed -= math.copysign(self.deceleration / 2, self.speed)
            else:
                self.speed = 0.0

    def apply_effect(self, value):
        """Zmienia prędkość po zebraniu elementu (Punkt 8)."""
        self.speed += value
        self.speed = min(self.speed, self.max_speed * 1.5)
        self.speed = max(self.speed, -self.max_speed / 2)


class SpecialItem(pygame.sprite.Sprite):
    def __init__(self, item_type):
        super().__init__()
        self.type = item_type 
        self.size = 30
        
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.effect_value = 0.0

        if self.type == 'BONUS':
            self.image.fill(YELLOW)
            self.effect_value = 1.5 
        else: 
            self.image.fill(BLUE)
            self.effect_value = -2.5 
        self.rect = self.image.get_rect(center=(
            random.randint(100, SCREEN_WIDTH - 100),
            random.randint(100, SCREEN_HEIGHT - 300)
        ))

try:
    track_image = pygame.image.load(os.path.join('.', 'track.png')).convert()
    track_image = pygame.transform.scale(track_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    print("Błąd: Nie znaleziono 'track.png'. Użyto zielonego tła.")
    track_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    track_image.fill(GREEN) 


def check_off_track(car_pos):
    """
    Wykrywa, czy samochód wyjechał poza tor (Punkt 10).
    Kolizja z torem jest realizowana poprzez sprawdzanie koloru piksela pod samochodem.
    Zakładamy, że tor ma konkretny kolor (np. szary/czarny), a obszar poza torem inny (np. zielony).
    
    UWAGA: Ta metoda wymaga, aby plik 'track.png' miał wyraźnie różne kolory:
           - Kolor toru (np. BLACK, DARK_GRAY)
           - Kolor otoczenia (np. GREEN, WHITE)
    """
    try:
        x, y = int(car_pos.x), int(car_pos.y)
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            color = track_image.get_at((x, y))
            
            r, g, b, a = color
            
            if r > 150 and g > 150 and b > 150: 
                return True
            if g > 200 and r < 100 and b < 100: 
                return True
            
        return False
    except IndexError:
        return True

def generate_item(items_group):
    """Generuje losowy element (Bonus lub Mankament) w losowej lokalizacji."""
    item_type = random.choice(['BONUS', 'PENALTY'])
    new_item = SpecialItem(item_type)
    items_group.add(new_item)


def display_time(screen, start_time, font):
    """Liczenie czasu przejazdu (Punkt 13)."""
    elapsed_time = time.time() - start_time
    time_text = f"Czas: {elapsed_time:.2f} s"
    text_surface = font.render(time_text, True, WHITE)
    screen.blit(text_surface, (10, 10))


all_sprites = pygame.sprite.Group()
items_group = pygame.sprite.Group() 
player = PlayerCar()
all_sprites.add(player)

game_start_time = time.time()
OFF_TRACK_PENALTY = -1.0 
ITEM_GENERATION_EVENT = pygame.USEREVENT + 1 
pygame.time.set_timer(ITEM_GENERATION_EVENT, 10000)

def game_loop():
    global running
    running = True
    is_game_over = False
    
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == ITEM_GENERATION_EVENT and not is_game_over:
                generate_item(items_group) 
        if not is_game_over:
            pressed_keys = pygame.key.get_pressed()
            player.handle_input(pressed_keys)


            if check_off_track(player.pos):
                player.apply_effect(OFF_TRACK_PENALTY) 
                
            hit_items = pygame.sprite.spritecollide(player, items_group, True) 
            for item in hit_items:
                player.apply_effect(item.effect_value)
                
            all_sprites.update()
            items_group.update()
        
        screen.blit(track_image, (0, 0)) 
        items_group.draw(screen) 
        all_sprites.draw(screen) 

        display_time(screen, game_start_time, font_small) 

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()