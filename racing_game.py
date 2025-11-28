import pygame
import os
import math
import random
import time

# ====================================================================
# 1. KONFIGURACJA I INICJALIZACJA
# ====================================================================

# Ustawienia Okna
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60 

# Kolory
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
OFF_TRACK_PENALTY = -1.0 # Efekt spowolnienia po wyjechaniu z toru

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Racing 2D - Kacper Zabiegała")
clock = pygame.time.Clock()

# Czcionki
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# ZDARZENIA (Punkt 9: Element pojawia się co 10 sekund)
ITEM_GENERATION_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ITEM_GENERATION_EVENT, 10000) 

# --- ZASOBY (Ścieżki i Opcje) ---
CAR_OPTIONS = {
    'RED': 'car_red.png',
    'BLUE': 'car_blue.png',
}
TRACK_OPTIONS = [
    {'name': 'Tor Startowy', 'file': 'track1.png', 'start': (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)},
    {'name': 'Tor Testowy', 'file': 'track2.png', 'start': (150, 50)},
]

# ====================================================================
# 2. FUNKCJE POMOCNICZE
# ====================================================================

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def display_time(screen, start_time, font, is_game_over):
    """Liczenie czasu przejazdu (Punkt 13)."""
    elapsed_time = time.time() - start_time
    time_text = f"Czas: {elapsed_time:.2f} s"
    draw_text(screen, time_text, font, WHITE, 10, 10)
    
def restart_game():
    """Resetuje stan gry po przejechaniu mety lub kolizji."""
    global player, opponent, all_sprites, items_group, track_manager
    
    # Zresetuj obiekty
    track_manager = TrackManager() 
    start_pos = track_manager.track_data[track_manager.current_track_index]['start']
    player = PlayerCar(start_pos)
    opponent = OpponentCar((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Wyczyść i dodaj do grup
    all_sprites.empty()
    items_group.empty()
    all_sprites.add(player)
    all_sprites.add(opponent)
    
    # Uruchom nową pętlę gry
    game_loop()


# ====================================================================
# 3. KLASY
# ====================================================================

class TrackManager:
    """Zarządza ładowaniem torów i detekcją kolizji z krawędzią (Punkt 10 i 14)."""
    def __init__(self):
        self.track_data = TRACK_OPTIONS
        self.current_track_index = 0
        self.image = self._load_track(self.track_data[self.current_track_index]['file'])

    def _load_track(self, filename):
        """Ładuje i skaluje obraz toru."""
        try:
            image = pygame.image.load(os.path.join('.', filename)).convert()
            image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return image
        except pygame.error:
            image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            image.fill(GRAY)
            return image
    
    def switch_track(self, index):
        """Zmienia aktywny tor (Punkt 14)."""
        self.current_track_index = index % len(self.track_data)
        self.image = self._load_track(self.track_data[self.current_track_index]['file'])
        return self.track_data[self.current_track_index]['start'] # Zwraca nową pozycję startową

    def check_off_track(self, car_pos):
        """Wykrywa wyjechanie poza tor na podstawie koloru piksela."""
        x, y = int(car_pos.x), int(car_pos.y)
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            color = self.image.get_at((x, y))
            r, g, b, a = color
            # Założenie: Jasne kolory (trawa/piasek) oznaczają poza tor
            if r > 150 and g > 150 and b > 150: 
                return True
        return False
        
    def check_finish_line(self, car_rect):
        """Wykrywa przejechanie mety (Punkt 12)."""
        # WARUNEK ZALEŻNY OD OBRAZU TORU. ZAKŁADAMY METĘ NA DOLE EKRANU.
        if car_rect.bottom > SCREEN_HEIGHT - 50 and car_rect.top < SCREEN_HEIGHT - 40:
             # Ogranicznik w osi X (centrum toru), aby uniknąć wykrycia na starcie
             if car_rect.centerx > SCREEN_WIDTH / 2 - 50 and car_rect.centerx < SCREEN_WIDTH / 2 + 50:
                 return True
        return False


class PlayerCar(pygame.sprite.Sprite):
    """Główny pojazd gracza (Punkt 1, 11, 13, 14)."""
    def __init__(self, start_pos):
        super().__init__()
        
        # Ładowanie wszystkich skórek (Punkt 13)
        self.car_index = 0
        self.original_images = {}
        for color, filename in CAR_OPTIONS.items():
            try:
                img = pygame.image.load(os.path.join('.', filename)).convert_alpha()
                self.original_images[color] = pygame.transform.scale(img, (50, 30))
            except pygame.error:
                temp_img = pygame.Surface((50, 30), pygame.SRCALPHA)
                temp_img.fill(RED if color == 'RED' else BLUE)
                self.original_images[color] = temp_img
                
        self.car_colors = list(CAR_OPTIONS.keys())
        self.current_color = self.car_colors[self.car_index]
        self.original_image = self.original_images[self.current_color]

        self.image = self.original_image
        self.rect = self.image.get_rect(center=start_pos)
        
        # Właściwości ruchu (Punkt 1, 11)
        self.max_speed = 5.0
        self.acceleration = 0.2
        self.deceleration = 0.1
        self.turning_speed = 3.5 

        self.speed = 0.0 
        self.angle = 0.0 
        self.pos = pygame.math.Vector2(start_pos) 
        
    def change_skin(self):
        """Zmienia wygląd pojazdu na następny w liście (Punkt 13)."""
        self.car_index = (self.car_index + 1) % len(self.car_colors)
        self.current_color = self.car_colors[self.car_index]
        self.original_image = self.original_images[self.current_color]
        
    def update(self):
        # Obliczenie ruchu
        radians = math.radians(self.angle)
        self.pos.x += self.speed * math.sin(radians)
        self.pos.y -= self.speed * math.cos(radians)
        
        # Ograniczenie pozycji (aby nie wychodził poza ekran)
        self.pos.x = max(20, min(self.pos.x, SCREEN_WIDTH - 20))
        self.pos.y = max(20, min(self.pos.y, SCREEN_HEIGHT - 20))
        
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Obrót grafiki
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


    def handle_input(self, pressed_keys):
        """Obsługuje wciśnięte klawisze (Punkt 11)."""
        
        # STEROWANIE KĄTEM
        if pressed_keys[pygame.K_LEFT]:
            self.angle += self.turning_speed
        if pressed_keys[pygame.K_RIGHT]:
            self.angle -= self.turning_speed

        # STEROWANIE PRĘDKOŚCIĄ
        if pressed_keys[pygame.K_UP]:
            self.speed += self.acceleration
            self.speed = min(self.speed, self.max_speed)
        
        elif pressed_keys[pygame.K_DOWN]:
            self.speed -= self.deceleration
            self.speed = max(self.speed, -self.max_speed / 2)
        
        else:
            # Automatyczne zwalnianie (tarcie)
            if abs(self.speed) > 0.1:
                self.speed -= math.copysign(self.deceleration / 2, self.speed)
            else:
                self.speed = 0.0

    def apply_effect(self, value):
        """Zmienia prędkość po zebraniu elementu lub wyjechaniu poza tor (Punkt 10)."""
        self.speed += value
        self.speed = min(self.speed, self.max_speed * 1.5)
        self.speed = max(self.speed, -self.max_speed / 2)


class SpecialItem(pygame.sprite.Sprite):
    """Element do zbierania (Bonus/Mankament) (Punkt 2, 3)."""
    def __init__(self, item_type):
        super().__init__()
        self.type = item_type 
        self.size = 30
        
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.effect_value = 0.0

        if self.type == 'BONUS':
            self.image.fill(YELLOW)
            self.effect_value = 1.5 # Przyspieszenie
        else: # PENALTY
            self.image.fill(BLUE)
            self.effect_value = -2.5 # Spowolnienie
            
        # Generowanie w losowej lokalizacji
        self.rect = self.image.get_rect(center=(
            random.randint(100, SCREEN_WIDTH - 100),
            random.randint(100, SCREEN_HEIGHT - 300)
        ))

class OpponentCar(pygame.sprite.Sprite):
    """Samochód przeszkoda (Punkt 5)."""
    def __init__(self, position):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join('.', 'car_opponent.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 40))
        except pygame.error:
            self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
            self.image.fill(BLUE) 
        
        self.rect = self.image.get_rect(center=position)
        # UWAGA: Ten samochód nie porusza się, jest stałą przeszkodą.


# ====================================================================
# 4. INICJALIZACJA OBIEKTÓW I GŁÓWNA PĘTLA GRY
# ====================================================================

# Inicjalizacja menedżera toru i pojazdów
track_manager = TrackManager()
start_pos = track_manager.track_data[track_manager.current_track_index]['start']
player = PlayerCar(start_pos)
opponent = OpponentCar((SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)) 

# Grupy Sprite'ów
all_sprites = pygame.sprite.Group()
items_group = pygame.sprite.Group() 
all_sprites.add(player)
all_sprites.add(opponent) 


def game_loop():
    global running
    running = True
    is_game_over = False
    game_start_time = time.time()
    
    # Zmienne HUD
    player_position = 1 # Prosta symulacja pozycji dla HUD (Punkt 13)

    while running:
        clock.tick(FPS)

        # 1. OBSŁUGA ZDARZEŃ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Generowanie elementu (Punkt 3)
            if event.type == ITEM_GENERATION_EVENT and not is_game_over:
                item_type = random.choice(['BONUS', 'PENALTY'])
                new_item = SpecialItem(item_type)
                items_group.add(new_item)
            
            # Sterowanie klawiszami (Zmiana toru/skinu/restart)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t and not is_game_over:
                    new_start_pos = track_manager.switch_track(track_manager.current_track_index + 1)
                    player.pos = pygame.math.Vector2(new_start_pos)
                    player.rect.center = new_start_pos
                
                if event.key == pygame.K_s and not is_game_over:
                    player.change_skin()
                    
                if event.key == pygame.K_r and is_game_over:
                    restart_game()
                    return 

        if not is_game_over:
            # Obsługa inputu sterowania samochodem (Punkt 11)
            pressed_keys = pygame.key.get_pressed()
            player.handle_input(pressed_keys)

            # 2. AKTUALIZACJA LOGIKI

            # --- Kolizje z torem (Wyjechanie z toru) (Punkt 10) ---
            if track_manager.check_off_track(player.pos):
                player.apply_effect(OFF_TRACK_PENALTY) 
                
            # --- Kolizje z elementami (Zbieranie) (Punkt 2) ---
            hit_items = pygame.sprite.spritecollide(player, items_group, True) 
            for item in hit_items:
                player.apply_effect(item.effect_value)
                
            # --- Kolizja z innym samochodem (Przegrana) (Punkt 5) ---
            if pygame.sprite.collide_rect(player, opponent):
                is_game_over = True
                game_end_reason = "Kolizja z innym samochodem! (PRZEGRANA)"

            # --- Meta (Wygrana) (Punkt 12) ---
            if track_manager.check_finish_line(player.rect):
                is_game_over = True
                game_end_reason = f"FINISH! Twój czas: {time.time() - game_start_time:.2f} s"
                
            
            # Aktualizacja pozycji
            all_sprites.update()
            items_group.update()
        
        # 3. RYSOWANIE
        screen.blit(track_manager.image, (0, 0)) # Rysowanie toru
        items_group.draw(screen) 
        all_sprites.draw(screen) 

        # Rysowanie Interfejsu (HUD) (Punkt 13)
        display_time(screen, game_start_time, font_medium, is_game_over)
        draw_text(screen, f"Prędkość: {player.speed:.1f}", font_small, WHITE, 10, 40)
        draw_text(screen, f"Tor: {track_manager.track_data[track_manager.current_track_index]['name']} (Klawisz T)", font_small, WHITE, 10, 60)
        draw_text(screen, f"Skin: {player.current_color} (Klawisz S)", font_small, WHITE, 10, 80)

        # Ekran KOŃCA GRY
        if is_game_over:
            draw_text(screen, "KONIEC GRY", font_large, RED, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
            draw_text(screen, game_end_reason, font_medium, YELLOW, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2)
            draw_text(screen, "Naciśnij R, aby zrestartować.", font_small, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)

        # 4. AKTUALIZACJA EKRANU
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()