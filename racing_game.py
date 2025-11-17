
import pygame
import os


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Racing 2D - Kacper Zabiegała")

clock = pygame.time.Clock()


class PlayerCar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.original_image = pygame.image.load(os.path.join('.', 'car.png')).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (50, 30))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        
        self.speed = 0
        self.angle = 0
    
try:
    track_image = pygame.image.load(os.path.join('.', 'track.png')).convert()
    track_image = pygame.transform.scale(track_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Błąd ładowania obrazu toru: {e}. Upewnij się, że plik 'track.png' istnieje.")
    track_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    track_image.fill(GREEN)



all_sprites = pygame.sprite.Group()
player = PlayerCar()
all_sprites.add(player)

# --- 6. GŁÓWNA PĘTLA GRY ---
def game_loop():
    global running
    running = True
    while running:
    
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.blit(track_image, (0, 0)) 
        all_sprites.draw(screen) 

        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()