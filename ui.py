import pygame
import time
import math

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        self.boss_font = pygame.font.Font(None, 32)  # NOUVEAU: Police pour boss
    
    def draw_bar(self, screen, x, y, width, height, current, maximum, color, bg_color=(50, 50, 50)):
        # Fond de la barre
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        
        # Barre de remplissage
        if maximum > 0:
            fill_width = int((current / maximum) * width)
            pygame.draw.rect(screen, color, (x, y, fill_width, height))
        
        # Bordure
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
    
    def draw_hud(self, screen, player, enemies, weapon=None, bosses=None):
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
        
        # NOUVEAU: Informations des boss (style Elden Ring en bas)
        if bosses:
            self.draw_boss_status(screen, bosses, player)
        
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
    
    def draw_boss_status(self, screen, bosses, player):
        """Affiche le statut des boss vivants en style Elden Ring (en bas de l'écran)"""
        current_time = time.time()
        boss_count = 0
        
        for boss in bosses:
            if not boss.alive:
                continue
            
            # NOUVEAU: Seulement afficher les boss dans la même salle que le joueur
            if not boss.is_player_in_same_room(player):
                continue
            
            # Position en bas de l'écran, style Elden Ring
            margin = 30
            bar_y = self.screen_height - margin - 60 - (boss_count * 80)
            
            # Barre de boss très large (style Elden Ring)
            bar_width = self.screen_width - 2 * margin
            bar_height = 20
            bar_x = margin
            
            # Nom du boss au-dessus de la barre
            name_y = bar_y - 35
            
            # Couleur selon la phase
            if boss.is_enraged:
                name_color = (255, 100, 100)  # Rouge vif en phase 2
                bar_glow_color = (255, 50, 50)
            else:
                name_color = (255, 215, 0)  # Doré en phase 1
                bar_glow_color = (255, 215, 0)
            
            # Effet de glow derrière le nom
            glow_surface = pygame.Surface((bar_width, 40))
            glow_surface.set_alpha(30)
            glow_surface.fill(bar_glow_color)
            screen.blit(glow_surface, (bar_x, name_y - 5))
            
            # Nom du boss centré
            boss_name = f"{boss.name}"
            if boss.is_enraged:
                boss_name += " - PHASE 2"
            
            name_text = self.boss_font.render(boss_name, True, name_color)
            name_rect = name_text.get_rect(center=(self.screen_width//2, name_y + 10))
            screen.blit(name_text, name_rect)
            
            # Barre de vie principale avec effet de glow
            health_ratio = boss.hp / boss.max_hp
            
            # Fond noir avec bordure
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Couleur de la barre selon les HP
            if health_ratio > 0.6:
                health_color = (255, 215, 0)  # Doré
            elif health_ratio > 0.3:
                health_color = (255, 165, 0)  # Orange
            else:
                health_color = (255, 69, 0)   # Rouge-orange
            
            # Effet de pulsation pour boss enragé
            if boss.is_enraged:
                pulse = math.sin(current_time * 8) * 0.3 + 0.7
                health_color = (
                    int(health_color[0] * pulse),
                    int(health_color[1] * pulse),
                    int(health_color[2] * pulse)
                )
            
            # Barre de vie avec effet de glow
            if health_ratio > 0:
                health_width = int(bar_width * health_ratio)
                
                # Glow derrière la barre
                glow_surface = pygame.Surface((health_width + 10, bar_height + 10))
                glow_surface.set_alpha(60)
                glow_surface.fill(health_color)
                screen.blit(glow_surface, (bar_x - 5, bar_y - 5))
                
                # Barre principale
                pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
                
                # Highlight sur le dessus
                highlight_color = (min(255, health_color[0] + 50), 
                                 min(255, health_color[1] + 50), 
                                 min(255, health_color[2] + 50))
                pygame.draw.rect(screen, highlight_color, (bar_x, bar_y, health_width, bar_height//3))
            
            # Texte HP sur la barre
            hp_text = f"{int(boss.hp)} / {boss.max_hp}"
            hp_render = self.font.render(hp_text, True, (255, 255, 255))
            hp_rect = hp_render.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
            
            # Ombre du texte
            shadow_render = self.font.render(hp_text, True, (0, 0, 0))
            screen.blit(shadow_render, (hp_rect.x + 2, hp_rect.y + 2))
            screen.blit(hp_render, hp_rect)
            
            # Icône du boss à gauche
            icon_size = 30
            icon_x = bar_x - icon_size - 10
            icon_y = bar_y - 5
            
            if boss.boss_type == "main":
                # Icône couronne pour le gardien
                pygame.draw.polygon(screen, (255, 215, 0), [
                    (icon_x + 5, icon_y + 25),
                    (icon_x + 15, icon_y + 5),
                    (icon_x + 25, icon_y + 25),
                    (icon_x + 20, icon_y + 30),
                    (icon_x + 10, icon_y + 30)
                ])
            else:
                # Icône mystique pour le seigneur
                pygame.draw.circle(screen, (150, 0, 150), (icon_x + 15, icon_y + 15), 12)
                pygame.draw.circle(screen, (255, 100, 255), (icon_x + 15, icon_y + 15), 8)
            
            boss_count += 1
    
    def draw_victory_screen(self, screen):
        """Affiche l'écran de victoire quand tous les boss sont vaincus"""
        # Fond semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Texte de victoire
        victory_text = self.big_font.render("VICTOIRE !", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        screen.blit(victory_text, victory_rect)
        
        # Sous-texte
        sub_text = self.boss_font.render("Tous les gardiens ont été vaincus", True, (255, 255, 255))
        sub_rect = sub_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
        screen.blit(sub_text, sub_rect)
        
        # Instructions
        restart_text = self.font.render("Appuyez sur R pour recommencer", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
        screen.blit(restart_text, restart_rect)
    
    def draw_boss_warning(self, screen, boss_name):
        """Affiche un avertissement quand un boss apparaît"""
        # Effet de flash rouge
        flash_surface = pygame.Surface((self.screen_width, self.screen_height))
        flash_surface.set_alpha(50)
        flash_surface.fill((255, 0, 0))
        screen.blit(flash_surface, (0, 0))
        
        # Texte d'avertissement
        warning_text = self.big_font.render(f"⚠️ {boss_name} APPARAÎT ⚠️", True, (255, 255, 0))
        warning_rect = warning_text.get_rect(center=(self.screen_width//2, 150))
        
        # Fond noir pour le texte
        bg_rect = warning_rect.inflate(40, 20)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(200)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, bg_rect)
        
        # Bordure dorée
        pygame.draw.rect(screen, (255, 215, 0), bg_rect, 4)
        
        # Texte
        screen.blit(warning_text, warning_rect)