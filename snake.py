import pygame
import sys
import random
import math  # For bonus pulse

pygame.init()

# Window size (smaller, more like classic phones)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
LIGHT_RED = (255, 100, 100)      # Snake
DARK_RED = (200, 50, 50)
LIGHT_BLUE = (100, 200, 255)     # Regular food
DARK_BLUE = (50, 150, 255)       # Bonus
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)

BASE_SPEED = 10
SPEED_INCREASE = 0.3

class SnakeGame:
    def __init__(self):
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Nokia Snake - Classic Edition")
        except Exception as e:
            print(f"Display error: {e}")
            print("Try running as admin or updating graphics drivers.")
            sys.exit(1)
        
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 72)
        self.font_huge = pygame.font.Font(None, 96)
        
        self.reset_game()
    
    def reset_game(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x-1, start_y), (start_x-2, start_y)]
        self.direction = (1, 0)
        self.bonus_food = None
        self.bonus_timer = 0
        self.food = self.generate_food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.game_over = False
        self.paused = False
        self.speed = BASE_SPEED
    
    def load_high_score(self):
        try:
            with open("snake_highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("snake_highscore.txt", "w") as f:
                f.write(str(self.score))
    
    def generate_food(self):
        while True:
            food = (random.randint(2, GRID_WIDTH - 3), random.randint(2, GRID_HEIGHT - 3))
            if food not in self.snake and (self.bonus_food is None or food != self.bonus_food):
                return food
    
    def spawn_bonus_food(self):
        while True:
            bonus = (random.randint(2, GRID_WIDTH - 3), random.randint(2, GRID_HEIGHT - 3))
            if bonus not in self.snake and bonus != self.food:
                return bonus
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.direction = (1, 0)
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        return False
        return True
    
    def update_speed(self):
        self.speed = BASE_SPEED + (self.score // 100) * SPEED_INCREASE
        self.speed = min(self.speed, 25)
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        self.update_speed()
        
        if self.bonus_timer > 0:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                self.bonus_food = None
        
        head_x, head_y = self.snake[0]
        # Move head and wrap around the grid (classic Nokia-style)
        new_head_x = (head_x + self.direction[0]) % GRID_WIDTH
        new_head_y = (head_y + self.direction[1]) % GRID_HEIGHT
        new_head = (new_head_x, new_head_y)
        
        if new_head in self.snake:
            self.game_over = True
            self.save_high_score()
            return
        
        self.snake.insert(0, new_head)
        
        ate_bonus = False
        if self.bonus_food and new_head == self.bonus_food:
            self.score += 50
            self.bonus_food = None
            self.bonus_timer = 0
            ate_bonus = True
        
        elif new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            if self.score % 50 == 0:
                self.bonus_food = self.spawn_bonus_food()
                self.bonus_timer = 300  # ~5-10 seconds depending on speed
        else:
            self.snake.pop()
        
        if self.score % 50 == 0 and not ate_bonus:
            self.level += 1
    
    def draw_background(self):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            gray_intensity = int(20 + (y / SCREEN_HEIGHT) * 40)
            color = (gray_intensity, gray_intensity, gray_intensity)
            pygame.draw.rect(self.screen, color, (0, y, SCREEN_WIDTH, GRID_SIZE))
        
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)
    
    def draw_snake(self):
        for i, segment in enumerate(self.snake):
            x = segment[0] * GRID_SIZE + 2
            y = segment[1] * GRID_SIZE + 2
            w = GRID_SIZE - 4
            h = GRID_SIZE - 4
            alpha = max(100, 255 - (i * 20))
            body_color = (min(255, alpha), int(alpha * 0.4), int(alpha * 0.4))
            pygame.draw.rect(self.screen, body_color, (x, y, w, h))
            pygame.draw.rect(self.screen, DARK_RED, (x, y, w, h), 2)
        
        head = self.snake[0]
        hx = head[0] * GRID_SIZE + 1
        hy = head[1] * GRID_SIZE + 1
        hw = GRID_SIZE - 2
        hh = GRID_SIZE - 2
        pygame.draw.rect(self.screen, LIGHT_RED, (hx, hy, hw, hh))
        pygame.draw.rect(self.screen, WHITE, (hx, hy, hw, hh), 2)
        pygame.draw.rect(self.screen, (255, 150, 150), (hx+2, hy+2, hw-4, hh-4))
    
    def draw_food(self):
        fx = self.food[0] * GRID_SIZE + 3
        fy = self.food[1] * GRID_SIZE + 3
        fw = GRID_SIZE - 6
        fh = GRID_SIZE - 6
        pygame.draw.rect(self.screen, LIGHT_BLUE, (fx, fy, fw, fh))
        pygame.draw.rect(self.screen, DARK_BLUE, (fx+2, fy+2, fw-4, fh-4))
        pygame.draw.rect(self.screen, WHITE, (fx, fy, fw, fh), 2)
        
        if self.bonus_food and self.bonus_timer > 0:
            bx = self.bonus_food[0] * GRID_SIZE + 2
            by = self.bonus_food[1] * GRID_SIZE + 2
            bw = GRID_SIZE - 4
            bh = GRID_SIZE - 4
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.02)) * 0.3 + 0.7
            sparkle_size = int(bw * pulse)
            sx = bx + (bw - sparkle_size) // 2
            sy = by + (bh - sparkle_size) // 2
            pygame.draw.rect(self.screen, DARK_BLUE, (sx, sy, sparkle_size, sparkle_size))
            pygame.draw.rect(self.screen, LIGHT_BLUE, (sx+1, sy+1, sparkle_size-2, sparkle_size-2))
            pygame.draw.rect(self.screen, WHITE, (sx, sy, sparkle_size, sparkle_size), 2)
            
            bonus_font = pygame.font.Font(None, 20)
            bonus_text = bonus_font.render("50", True, WHITE)
            bonus_rect = bonus_text.get_rect(center=(bx + bw//2, by + bh//2))
            self.screen.blit(bonus_text, bonus_rect)
    
    def draw_ui(self):
        bar_height = 60
        pygame.draw.rect(self.screen, GRAY, (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, bar_height), 3)
        
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, LIGHT_RED)
        score_rect = score_text.get_rect(x=SCREEN_WIDTH - score_text.get_width() - 20, y=15)
        self.screen.blit(score_text, score_rect)
        
        hs_text = self.font_small.render(f"HI: {self.high_score}", True, WHITE)
        hs_rect = hs_text.get_rect(x=SCREEN_WIDTH - hs_text.get_width() - 20, y=50)
        self.screen.blit(hs_text, hs_rect)
        
        level_text = self.font_medium.render(f"L {self.level}", True, LIGHT_BLUE)
        self.screen.blit(level_text, (20, 15))
        
        speed_text = self.font_small.render(f"SPEED: {int(self.speed)}", True, WHITE)
        self.screen.blit(speed_text, (20, 50))
        
        status_y = SCREEN_HEIGHT - 50
        if self.paused:
            pause_text = self.font_large.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, status_y))
            self.screen.blit(pause_text, pause_rect)
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            go_title = self.font_huge.render("GAME OVER", True, LIGHT_RED)
            title_rect = go_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(go_title, title_rect)
            
            final_score = self.font_large.render(f"{self.score}", True, LIGHT_BLUE)
            final_rect = final_score.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(final_score, final_rect)
            
            if self.score == self.high_score:
                new_hs = self.font_medium.render("NEW HIGH SCORE!", True, WHITE)
                new_hs_rect = new_hs.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
                self.screen.blit(new_hs, new_hs_rect)
            
            inst1 = self.font_medium.render("R / ENTER / SPACE : RESTART", True, WHITE)
            inst2 = self.font_medium.render("ESC : QUIT", True, WHITE)
            self.screen.blit(inst1, (SCREEN_WIDTH//2 - inst1.get_width()//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(inst2, (SCREEN_WIDTH//2 - inst2.get_width()//2, SCREEN_HEIGHT//2 + 130))
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.screen.fill(BLACK)
            self.draw_background()
            self.draw_food()
            self.draw_snake()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(int(self.speed))
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()