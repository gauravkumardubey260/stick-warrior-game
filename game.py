import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stick Warrior - Beat the Enemies!")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5
        self.health = 100
        self.attack_range = 80
        self.attack_cooldown = 0
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        
        # Keep player in bounds
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))
        
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 15
            return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2
        self.health = 30
        
    def update(self, player):
        # Move towards player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed
    
    def take_damage(self, damage):
        self.health -= damage

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.score = 0
        self.wave = 1
        self.enemy_spawn_timer = 0
        self.enemies_in_wave = 3
        self.enemies_killed = 0
        self.running = True
        
    def spawn_enemy(self):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, 200)
        enemy = Enemy(x, y)
        self.enemies.add(enemy)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player.attack():
                        self.check_attack()
    
    def check_attack(self):
        for enemy in self.enemies:
            distance = math.sqrt((self.player.rect.centerx - enemy.rect.centerx)**2 + 
                               (self.player.rect.centery - enemy.rect.centery)**2)
            if distance < self.player.attack_range:
                enemy.take_damage(30)
                if enemy.health <= 0:
                    enemy.kill()
                    self.score += 10
                    self.enemies_killed += 1
    
    def update(self):
        self.player.update()
        self.enemies.update(self.player)
        
        # Spawn enemies
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 60 and len(self.enemies) < self.enemies_in_wave:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
        
        # Check if wave is complete
        if self.enemies_killed >= self.enemies_in_wave and len(self.enemies) == 0:
            self.wave += 1
            self.enemies_in_wave += 2
            self.enemies_killed = 0
        
        # Check collisions with enemies (take damage)
        for enemy in self.enemies:
            if pygame.sprite.spritecollide(self.player, pygame.sprite.Group(enemy), False):
                self.player.take_damage(0.1)
        
        # Game over
        if self.player.health <= 0:
            self.running = False
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw player
        screen.blit(self.player.image, self.player.rect)
        
        # Draw stick (weapon)
        if self.player.attack_cooldown > 0:
            pygame.draw.line(screen, YELLOW, 
                           (self.player.rect.centerx, self.player.rect.centery),
                           (self.player.rect.centerx + 50, self.player.rect.centery), 5)
        
        # Draw enemies
        for enemy in self.enemies:
            screen.blit(enemy.image, enemy.rect)
        
        # Draw UI
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        wave_text = font.render(f"Wave: {self.wave}", True, BLACK)
        health_text = font.render(f"Health: {int(self.player.health)}", True, BLACK)
        
        screen.blit(score_text, (10, 10))
        screen.blit(wave_text, (10, 50))
        screen.blit(health_text, (10, 90))
        
        # Draw attack cooldown
        if self.player.attack_cooldown > 0:
            cooldown_text = font.render("Attacking...", True, RED)
            screen.blit(cooldown_text, (SCREEN_WIDTH - 200, 10))
        else:
            ready_text = font.render("Press SPACE to Attack", True, GREEN)
            screen.blit(ready_text, (SCREEN_WIDTH - 300, 10))
        
        pygame.display.flip()
    
    def show_game_over(self):
        screen.fill(BLACK)
        game_over_text = font.render(f"GAME OVER! Final Score: {self.score}", True, RED)
        wave_text = font.render(f"Waves Survived: {self.wave}", True, WHITE)
        restart_text = font.render("Press SPACE to Restart or Q to Quit", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100))
        screen.blit(wave_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 100))
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True
                    if event.key == pygame.K_q:
                        return False
            clock.tick(60)
    
    def run(self):
        while True:
            self.running = True
            self.player = Player()
            self.enemies.empty()
            self.score = 0
            self.wave = 1
            self.enemies_in_wave = 3
            self.enemies_killed = 0
            self.enemy_spawn_timer = 0
            
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                clock.tick(60)
            
            if not self.show_game_over():
                break
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
