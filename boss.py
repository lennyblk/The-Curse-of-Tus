# boss.py - Système de boss corrigé avec contraintes de salle
import pygame
import math
import time
import random

class BossProjectile:
    def __init__(self, x, y, velocity_x, velocity_y, projectile_type="normal"):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.projectile_type = projectile_type
        self.creation_time = time.time()
        self.lifetime = 6.0  # 6 secondes de vie
        
        # Propriétés selon le type
        if projectile_type == "boss_normal":
            self.width = 12
            self.height = 12
            self.color = (255, 100, 0)  # Orange vif
            self.damage = 20
        elif projectile_type == "boss_secret":
            self.width = 8
            self.height = 8
            self.color = (150, 0, 150)  # Violet
            self.damage = 15
        else:  # "explosive"
            self.width = 16
            self.height = 16
            self.color = (255, 0, 0)  # Rouge
            self.damage = 25
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.trail = []  # Pour les traînées visuelles
    
    def update(self, world):
        current_time = time.time()
        
        # Vérifier durée de vie
        if current_time - self.creation_time >= self.lifetime:
            return False
        
        # Ajouter position actuelle à la traînée
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:  # Limiter la traînée
            self.trail.pop(0)
        
        # Déplacer le projectile
        dt = 1/60
        new_x = self.x + self.velocity_x * dt
        new_y = self.y + self.velocity_y * dt
        
        # Vérifier collision avec les murs
        if self.check_collision(new_x, new_y, world):
            return False
        
        # Mettre à jour position
        self.x = new_x
        self.y = new_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        return True
    
    def check_collision(self, x, y, world):
        corners = [(x, y), (x + self.width, y), 
                  (x, y + self.height), (x + self.width, y + self.height)]
        
        for corner_x, corner_y in corners:
            grid_x = int(corner_x // world.tile_size)
            grid_y = int(corner_y // world.tile_size)
            
            if (0 <= grid_x < world.width and 0 <= grid_y < world.height and 
                world.map[grid_y][grid_x] == 1):
                return True
        return False
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Dessiner la traînée
        if self.projectile_type == "boss_secret":
            for i, (trail_x, trail_y) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail))) if self.trail else 0
                trail_screen_x = trail_x - camera_x
                trail_screen_y = trail_y - camera_y
                
                trail_surface = pygame.Surface((4, 4))
                trail_surface.set_alpha(alpha)
                trail_surface.fill(self.color)
                screen.blit(trail_surface, (trail_screen_x, trail_screen_y))
        
        # Dessiner le projectile principal
        if self.projectile_type == "boss_secret":
            # Losange pour boss secret
            points = [
                (screen_x + self.width//2, screen_y),
                (screen_x + self.width, screen_y + self.height//2),
                (screen_x + self.width//2, screen_y + self.height),
                (screen_x, screen_y + self.height//2)
            ]
            pygame.draw.polygon(screen, self.color, points)
        else:
            # Cercle pour boss principal
            center_x = int(screen_x + self.width//2)
            center_y = int(screen_y + self.height//2)
            pygame.draw.circle(screen, self.color, (center_x, center_y), self.width//2)
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), self.width//2, 2)


class Boss:
    def __init__(self, x, y, boss_type="main", world=None):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.width = 64
        self.height = 64
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.alive = True
        self.boss_type = boss_type
        self.world = world  # NOUVEAU: Référence au monde pour les contraintes
        
        # Stats selon le type - HP RÉDUITS
        if boss_type == "main":
            self.max_hp = 150  # RÉDUIT: 200 → 150
            self.name = "Gardien des Profondeurs"
            self.color = (150, 0, 0)
            self.speed = 1.5
        else:  # "secret"
            self.max_hp = 120  # TRÈS RÉDUIT: 250 → 120
            self.name = "Seigneur des Ombres"
            self.color = (75, 0, 75)
            self.speed = 2.0  # RÉDUIT: 2.5 → 2.0
        
        self.hp = self.max_hp
        
        # Déterminer la salle du boss - NOUVEAU
        self.room_bounds = self.get_room_bounds()
        
        # Système de phases
        self.phase = 1
        self.is_enraged = False
        
        # Patterns d'attaque
        self.attack_pattern = 0
        self.last_attack_time = 0
        self.attack_cooldown = 3.0
        self.last_special_time = 0
        self.special_cooldown = 8.0
        
        # Mouvement
        self.target_x = x
        self.target_y = y
        self.movement_timer = 0
        
        # Invulnérabilité
        self.last_damage_time = 0
        self.damage_cooldown = 0.3
        
        # Effets visuels
        self.pulse_timer = 0
        self.particles = []
        
        # Boss secret spécifique - COOLDOWN AUGMENTÉ
        if boss_type == "secret":
            self.teleport_cooldown = 8.0  # AUGMENTÉ: 5.0 → 8.0
            self.last_teleport_time = 0
            self.is_teleporting = False
            self.teleport_alpha = 255
    
    def get_room_bounds(self):
        """Détermine les limites de la salle du boss"""
        if not self.world:
            return None
        
        # Convertir position en tiles
        boss_tile_x = int(self.start_x // self.world.tile_size)
        boss_tile_y = int(self.start_y // self.world.tile_size)
        
        # Trouver la salle qui contient le boss
        for room_name, room_data in self.world.rooms.items():
            if (room_data["x"] <= boss_tile_x < room_data["x"] + room_data["w"] and
                room_data["y"] <= boss_tile_y < room_data["y"] + room_data["h"]):
                
                # Convertir en coordonnées pixel avec marge de sécurité
                bounds = {
                    "min_x": (room_data["x"] + 1) * self.world.tile_size,
                    "max_x": (room_data["x"] + room_data["w"] - 2) * self.world.tile_size,
                    "min_y": (room_data["y"] + 1) * self.world.tile_size,
                    "max_y": (room_data["y"] + room_data["h"] - 2) * self.world.tile_size,
                    "room_name": room_name
                }
                print(f"Boss {self.boss_type} confiné dans {room_name}: {bounds}")
                return bounds
        
        print(f"⚠️ ERREUR: Boss {self.boss_type} pas dans une salle identifiée!")
        return None
    
    def is_in_room_bounds(self, x, y):
        """Vérifie si une position est dans les limites de la salle"""
        if not self.room_bounds:
            return True  # Pas de contrainte si pas de limites
        
        return (self.room_bounds["min_x"] <= x <= self.room_bounds["max_x"] - self.width and
                self.room_bounds["min_y"] <= y <= self.room_bounds["max_y"] - self.height)
    
    def constrain_to_room(self, x, y):
        """Force une position à rester dans la salle"""
        if not self.room_bounds:
            return x, y
        
        constrained_x = max(self.room_bounds["min_x"], 
                           min(x, self.room_bounds["max_x"] - self.width))
        constrained_y = max(self.room_bounds["min_y"], 
                           min(y, self.room_bounds["max_y"] - self.height))
        
        return constrained_x, constrained_y
    
    def is_player_in_same_room(self, player):
        """Vérifie si le joueur est dans la même salle que le boss"""
        if not self.room_bounds:
            return False  # CHANGÉ: Si pas de contrainte, le boss n'agit PAS
        
        player_x = player.x + player.width/2
        player_y = player.y + player.height/2
        
        is_in_room = (self.room_bounds["min_x"] <= player_x <= self.room_bounds["max_x"] and
                     self.room_bounds["min_y"] <= player_y <= self.room_bounds["max_y"])
        
        if is_in_room:
            print(f"🎯 Joueur détecté dans la salle {self.room_bounds['room_name']} - Boss {self.boss_type} activé!")
        
        return is_in_room
    
    def update(self, player, world, projectiles):
        if not self.alive:
            return
        
        # NOUVEAU: Ne pas agir si le joueur n'est pas dans la même salle
        if not self.is_player_in_same_room(player):
            return
        
        current_time = time.time()
        
        # Vérifier passage en phase 2
        if not self.is_enraged and self.hp < self.max_hp * 0.5:
            self.enter_rage_mode()
        
        # Mouvement selon le type
        if self.boss_type == "main":
            self.update_tank_movement(player, world)
        else:
            self.update_teleport_movement(player, world, current_time)
        
        # Patterns d'attaque
        self.update_attacks(player, world, projectiles, current_time)
        
        # Effets visuels
        self.update_effects(current_time)
    
    def enter_rage_mode(self):
        """Phase 2 - Mode enragé"""
        self.is_enraged = True
        self.phase = 2
        self.attack_cooldown = 2.0  # Plus rapide
        self.special_cooldown = 5.0
        
        if self.boss_type == "secret":
            self.teleport_cooldown = 5.0  # Téléporte plus souvent en phase 2
        
        print(f"{self.name} devient enragé !")
    
    def update_tank_movement(self, player, world):
        """Mouvement du boss principal (tank) - AVEC CONTRAINTES"""
        current_time = time.time()
        
        if current_time - self.movement_timer > 4.0:
            self.movement_timer = current_time
            
            # Rester à distance moyenne du joueur
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 120:  # Trop loin
                target_x = player.x - 100 * (dx/distance)
                target_y = player.y - 100 * (dy/distance)
            elif distance < 80:  # Trop proche
                target_x = self.x - dx/distance * 60
                target_y = self.y - dy/distance * 60
            else:  # Distance correcte, bouger autour
                angle = random.random() * 2 * math.pi
                target_x = player.x + math.cos(angle) * 100
                target_y = player.y + math.sin(angle) * 100
            
            # NOUVEAU: Contraindre la cible aux limites de la salle
            self.target_x, self.target_y = self.constrain_to_room(target_x, target_y)
        
        # Mouvement vers la cible
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:
            move_x = (dx / distance) * self.speed
            move_y = (dy / distance) * self.speed
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            # NOUVEAU: Vérifier les contraintes de salle
            if (not self.check_collision(new_x, self.y, world) and 
                self.is_in_room_bounds(new_x, self.y)):
                self.x = new_x
            if (not self.check_collision(self.x, new_y, world) and 
                self.is_in_room_bounds(self.x, new_y)):
                self.y = new_y
            
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    
    def update_teleport_movement(self, player, world, current_time):
        """Mouvement du boss secret (téléportation) - AVEC CONTRAINTES"""
        # Téléportation SEULEMENT si le joueur est dans la même salle
        if (current_time - self.last_teleport_time >= self.teleport_cooldown and
            self.is_player_in_same_room(player)):
            self.teleport_near_player(player, world)
            self.last_teleport_time = current_time
        
        # Mouvement normal entre téléportations
        if not self.is_teleporting:
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 10:
                move_x = (dx / distance) * self.speed * 0.5  # Plus lent que téléportation
                move_y = (dy / distance) * self.speed * 0.5
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                # NOUVEAU: Vérifier les contraintes de salle
                if (not self.check_collision(new_x, self.y, world) and 
                    self.is_in_room_bounds(new_x, self.y)):
                    self.x = new_x
                if (not self.check_collision(self.x, new_y, world) and 
                    self.is_in_room_bounds(self.x, new_y)):
                    self.y = new_y
                
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
    
    def teleport_near_player(self, player, world):
        """Téléporte le boss secret près du joueur - DANS SA SALLE SEULEMENT"""
        if not self.is_player_in_same_room(player):
            print(f"❌ Téléportation annulée: joueur pas dans la salle du boss")
            return
        
        for attempt in range(20):  # Plus de tentatives
            angle = random.random() * 2 * math.pi
            distance = random.randint(80, 120)
            
            new_x = player.x + math.cos(angle) * distance
            new_y = player.y + math.sin(angle) * distance
            
            # NOUVEAU: Vérifier contraintes de salle ET collision
            if (not self.check_collision(new_x, new_y, world) and 
                self.is_in_room_bounds(new_x, new_y)):
                self.x = new_x
                self.y = new_y
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                
                # Effet de téléportation
                self.is_teleporting = True
                self.teleport_alpha = 100
                print(f"✅ Boss secret téléporté en ({new_x:.0f}, {new_y:.0f})")
                break
        else:
            print(f"❌ Échec téléportation après 20 tentatives")
    
    def update_attacks(self, player, world, projectiles, current_time):
        """Gestion des attaques selon le type de boss - SEULEMENT si joueur dans la salle"""
        if not self.is_player_in_same_room(player):
            return
        
        # Attaque normale
        if current_time - self.last_attack_time >= self.attack_cooldown:
            if self.boss_type == "main":
                self.main_boss_attack(player, projectiles)
            else:
                self.secret_boss_attack(player, projectiles)
            self.last_attack_time = current_time
        
        # Attaque spéciale
        if current_time - self.last_special_time >= self.special_cooldown:
            if self.boss_type == "main":
                self.main_boss_special(player, projectiles)
            else:
                self.secret_boss_special(player, projectiles)
            self.last_special_time = current_time
    
    def main_boss_attack(self, player, projectiles):
        """Attaque normale du boss principal - Salve en éventail"""
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Direction vers le joueur
        dx = player.x - center_x
        dy = player.y - center_y
        base_angle = math.atan2(dy, dx)
        
        # Éventail de projectiles
        num_projectiles = 5 if not self.is_enraged else 8
        spread = math.pi / 3  # 60 degrés
        
        for i in range(num_projectiles):
            angle = base_angle - spread/2 + (i * spread / (num_projectiles - 1))
            speed = 120
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            projectile = BossProjectile(center_x, center_y, vel_x, vel_y, "boss_normal")
            projectiles.append(projectile)
    
    def main_boss_special(self, player, projectiles):
        """Attaque spéciale du boss principal - Ondes de choc"""
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # 3 anneaux concentriques
        for ring in range(3):
            num_projectiles = 12 + ring * 4  # Plus de projectiles par anneau
            radius_speed = 80 + ring * 30  # Vitesses différentes
            
            for i in range(num_projectiles):
                angle = (i * 2 * math.pi) / num_projectiles
                vel_x = math.cos(angle) * radius_speed
                vel_y = math.sin(angle) * radius_speed
                
                projectile = BossProjectile(center_x, center_y, vel_x, vel_y, "explosive")
                projectiles.append(projectile)
        
        print(f"{self.name} lance une onde de choc !")
    
    def secret_boss_attack(self, player, projectiles):
        """Attaque normale du boss secret - Spirale"""
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        num_projectiles = 8 if not self.is_enraged else 12
        spiral_offset = time.time() * 2  # Rotation de la spirale
        
        for i in range(num_projectiles):
            angle = (i * 2 * math.pi / num_projectiles) + spiral_offset
            speed = 100
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            projectile = BossProjectile(center_x, center_y, vel_x, vel_y, "boss_secret")
            projectiles.append(projectile)
    
    def secret_boss_special(self, player, projectiles):
        """Attaque spéciale du boss secret - Mur balayant"""
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Direction vers le joueur pour orienter le mur
        dx = player.x - center_x
        dy = player.y - center_y
        player_angle = math.atan2(dy, dx)
        
        # Créer un mur de projectiles perpendiculaire à la direction du joueur
        wall_angle = player_angle + math.pi/2  # Perpendiculaire
        num_projectiles = 15
        
        for i in range(num_projectiles):
            # Position le long du mur
            wall_offset = (i - num_projectiles//2) * 20
            start_x = center_x + math.cos(wall_angle) * wall_offset
            start_y = center_y + math.sin(wall_angle) * wall_offset
            
            # Direction vers le joueur
            speed = 90
            vel_x = math.cos(player_angle) * speed
            vel_y = math.sin(player_angle) * speed
            
            projectile = BossProjectile(start_x, start_y, vel_x, vel_y, "boss_secret")
            projectiles.append(projectile)
        
        print(f"{self.name} lance un mur de projectiles !")
    
    def take_damage(self, damage):
        """Boss prend des dégâts"""
        current_time = time.time()
        if current_time - self.last_damage_time < self.damage_cooldown:
            return False
        
        self.last_damage_time = current_time
        self.hp -= damage
        
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            print(f"{self.name} vaincu !")
            return True
        
        print(f"{self.name} : {self.hp}/{self.max_hp} HP")
        return True
    
    def check_collision(self, x, y, world):
        """Vérification collision boss"""
        corners = [(x, y), (x + self.width, y), 
                  (x, y + self.height), (x + self.width, y + self.height)]
        
        for corner_x, corner_y in corners:
            grid_x = int(corner_x // world.tile_size)
            grid_y = int(corner_y // world.tile_size)
            
            if (0 <= grid_x < world.width and 0 <= grid_y < world.height and 
                world.map[grid_y][grid_x] == 1):
                return True
        return False
    
    def update_effects(self, current_time):
        """Met à jour les effets visuels"""
        self.pulse_timer += 1/60
        
        # Effet de téléportation pour boss secret
        if self.boss_type == "secret" and self.is_teleporting:
            self.teleport_alpha = min(255, self.teleport_alpha + 5)
            if self.teleport_alpha >= 255:
                self.is_teleporting = False
    
    def draw(self, screen, camera_x, camera_y):
        """Dessiner le boss avec tous ses effets"""
        if not self.alive:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Couleur avec effets
        color = self.color
        current_time = time.time()
        
        # Effet de pulsation
        pulse = math.sin(self.pulse_timer * 4) * 0.3 + 0.7
        color = (int(color[0] * pulse), int(color[1] * pulse), int(color[2] * pulse))
        
        # Effet enragé
        if self.is_enraged:
            color = (min(255, color[0] + 50), color[1], color[2])
        
        # Flash blanc quand touché
        if current_time - self.last_damage_time < 0.2:
            color = (255, 255, 255)
        
        # Dessiner le boss
        if self.boss_type == "secret":
            # Boss secret avec effet de transparence
            boss_surface = pygame.Surface((self.width, self.height))
            boss_surface.set_alpha(self.teleport_alpha if self.is_teleporting else 200)
            boss_surface.fill(color)
            screen.blit(boss_surface, (screen_x, screen_y))
        else:
            # Boss principal normal
            pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))
        
        # Bordure
        border_color = (255, 215, 0) if self.is_enraged else (255, 255, 255)
        pygame.draw.rect(screen, border_color, (screen_x, screen_y, self.width, self.height), 4)
        
        # SUPPRIMÉ: Plus de barre de vie au-dessus du boss car maintenant on a celle en bas style Elden Ring