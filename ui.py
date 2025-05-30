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
    
    def draw_hud(self, screen, player, enemies, weapon=None):
        if not player.alive:
            # Écran Game Over
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
        hp_y = self.screen_height - margin - 140
        stamina_y = self.screen_height - margin - 110
        
        # Barre de vie
        self.draw_bar(screen, margin, hp_y, bar_width, bar_height, 
                    player.hp, player.max_hp, (0, 255, 0))
        hp_text = self.font.render(f"HP: {int(player.hp)}/{player.max_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (margin + bar_width + 10, hp_y))
        
        # Barre de stamina
        self.draw_bar(screen, margin, stamina_y, bar_width, bar_height, 
                    player.stamina, player.max_stamina, (0, 100, 255))
        stamina_text = self.font.render(f"Stamina: {int(player.stamina)}/{player.max_stamina}", True, (255, 255, 255))
        screen.blit(stamina_text, (margin + bar_width + 10, stamina_y))
        
        # Stats du joueur
        stats_y = self.screen_height - margin - 80
        speed_text = self.font.render(f"Vitesse: {player.speed:.1f}", True, (255, 255, 255))
        screen.blit(speed_text, (margin, stats_y))
        
        damage_text = self.font.render(f"Attaque: {player.attack_damage}", True, (255, 255, 255))
        screen.blit(damage_text, (margin + 120, stats_y))
        
        range_text = self.font.render(f"Portée: {player.attack_range}", True, (255, 255, 255))
        screen.blit(range_text, (margin + 240, stats_y))
        
        # Arme équipée avec cooldown
        weapon_y = self.screen_height - margin - 55
        if weapon:
            if weapon.weapon_type == "bow":
                cooldown_text = f"Arc (Cooldown: {player.bow_cooldown}s)"
            else:
                cooldown_text = f"Épée (Cooldown: {player.melee_cooldown}s)"
            weapon_text = self.font.render(f"Arme: {weapon.name} - {cooldown_text}", True, (255, 215, 0))
            screen.blit(weapon_text, (margin, weapon_y))
        else:
            weapon_text = self.font.render(f"Arme: Poings (Cooldown: {player.melee_cooldown}s)", True, (200, 200, 200))
            screen.blit(weapon_text, (margin, weapon_y))
        
        # Contrôles
        controls = [
            "ZQSD or KEYS: Move",
            "Shift: Sprint", 
            "Space: Attack",
            "I: Inventaire"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font.render(control, True, (200, 200, 200))
            screen.blit(control_text, (self.screen_width - 200, margin + i * 25))