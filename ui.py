# ui.py
import pygame

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
    
    def draw_bar(self, screen, x, y, width, height, current, maximum, color, bg_color=(50, 50, 50)):
        # Fond de la barre
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        
        # Barre de remplissage
        if maximum > 0:
            fill_width = int((current / maximum) * width)
            pygame.draw.rect(screen, color, (x, y, fill_width, height))
        
        # Bordure
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
    
    def draw_hud(self, screen, player, enemies):
        if not player.alive:
            # Écran Game Over (reste pareil)
            game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.font.render("Appuyez sur R pour recommencer", True, (255, 255, 255))
            
            game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
            
            screen.blit(game_over_text, game_over_rect)
            screen.blit(restart_text, restart_rect)
            return
        
        # HUD en bas à gauche
        margin = 20
        bar_width = 200
        bar_height = 20
        
        # Position en bas à gauche
        hp_y = self.screen_height - margin - 100  # 120 pixels du bas
        stamina_y = self.screen_height - margin - 60  # 60 pixels du bas
        
        # Barre de vie (VERTE maintenant)
        self.draw_bar(screen, margin, hp_y, bar_width, bar_height, 
                    player.hp, player.max_hp, (0, 255, 0))  # Vert au lieu de rouge
        
        # Barre de stamina
        self.draw_bar(screen, margin, stamina_y, bar_width, bar_height, 
                    player.stamina, player.max_stamina, (0, 100, 255))
        
        # Compteur d'ennemis (en bas aussi)
        alive_enemies = sum(1 for enemy in enemies if enemy.alive)
        total_enemies = len(enemies)
        killed_enemies = total_enemies - alive_enemies
        
        enemy_text = self.font.render(f"Ennemis tués: {killed_enemies}/{total_enemies}", True, (255, 255, 255))
        screen.blit(enemy_text, (margin, self.screen_height - margin - 15))  # Tout en bas
        
        # Contrôles (restent en haut à droite)
        controls = [
            "ZQSD or KEYS: Move",
            "Shift: Sprint",
            "Space: Attack"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font.render(control, True, (200, 200, 200))
            screen.blit(control_text, (self.screen_width - 200, margin + i * 25))