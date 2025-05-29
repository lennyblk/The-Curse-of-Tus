# enemy.py
import pygame
import math
import time
import random

class Projectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.speed = 100  # pixels par seconde
        self.lifetime = 4.0  # 4 secondes
        self.creation_time = time.time()
        self.width = 8
        self.height = 8
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Direction vers la cible
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.velocity_x = (dx / distance) * self.speed
            self.velocity_y = (dy / distance) * self.speed
        else:
            self.velocity_x = 0
            self.velocity_y = 0
    
    def update(self, player, world):
        current_time = time.time()
        
        # Vérifier si le projectile doit disparaître
        if current_time - self.creation_time >= self.lifetime:
            return False
        
        # Recalculer la direction vers le joueur (missile qui suit)
        dx = player.x + player.width/2 - (self.x + self.width/2)
        dy = player.y + player.height/2 - (self.y + self.height/2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Mélanger direction actuelle et nouvelle direction pour un suivi fluide
            target_vel_x = (dx / distance) * self.speed
            target_vel_y = (dy / distance) * self.speed
            
            # Transition douce (20% nouvelle direction, 80% ancienne)
            self.velocity_x = self.velocity_x * 0.8 + target_vel_x * 0.2
            self.velocity_y = self.velocity_y * 0.8 + target_vel_y * 0.2
        
        # Déplacer le projectile
        dt = 1/60  # 60 FPS
        new_x = self.x + self.velocity_x * dt
        new_y = self.y + self.velocity_y * dt
        
        # Vérifier collision avec les murs
        if not self.check_collision(new_x, new_y, world):
            self.x = new_x
            self.y = new_y
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
        else:
            return False  # Détruire si collision mur
        
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
        pygame.draw.circle(screen, (255, 255, 0), 
                         (int(screen_x + self.width/2), int(screen_y + self.height/2)), 4)

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.width = 24
        self.height = 24
        self.speed = 3
        self.hp = 3
        self.max_hp = 3
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.alive = True
        
        # Stats d'attaque
        self.attack_damage = 15
        self.attack_cooldown = 1.5
        self.last_attack_time = 0
        
        # Type d'ennemi
        self.enemy_type = enemy_type
        self.patrol_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.patrol_distance = 0
        self.max_patrol_distance = random.randint(60, 120)
        
        # Pour les patrouilleurs qui deviennent agressifs
        self.is_aggressive = False
        self.detection_range = 100
        
        # Pour les ennemis à distance
        self.shoot_cooldown = 2.0  # Tire toutes les 2 secondes
        self.last_shoot_time = 0
        self.shoot_range = 150
    
    def update(self, player, world, other_enemies, projectiles):
        if not self.alive:
            return
        
        if self.enemy_type == "stationary":
            self.ranged_behavior(player, world, projectiles)
        elif self.enemy_type == "patrol":
            self.smart_patrol_behavior(player, world, other_enemies)
        else:  # "normal"
            self.follow_behavior(player, world, other_enemies)
    
    def ranged_behavior(self, player, world, projectiles):
        """Ennemi stationnaire qui tire des missiles"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Attaque au contact si très proche
        if distance <= 40:
            self.attack_player(player)
        # Tirer des missiles si dans la portée
        elif distance <= self.shoot_range:
            current_time = time.time()
            if current_time - self.last_shoot_time >= self.shoot_cooldown:
                self.last_shoot_time = current_time
                # Créer un projectile vers le joueur
                projectile = Projectile(
                    self.x + self.width/2, 
                    self.y + self.height/2,
                    player.x + player.width/2, 
                    player.y + player.height/2
                )
                projectiles.append(projectile)
    
    def smart_patrol_behavior(self, player, world, other_enemies):
        """Patrouille, mais suit le joueur si détecté"""
        dx_player = player.x - self.x
        dy_player = player.y - self.y
        player_distance = math.sqrt(dx_player*dx_player + dy_player*dy_player)
        
        # Devient agressif si le joueur est proche
        if player_distance <= self.detection_range:
            self.is_aggressive = True
        
        if self.is_aggressive:
            # Comportement de suivi (comme un ennemi normal)
            self.follow_behavior(player, world, other_enemies)
        else:
            # Comportement de patrouille normal
            if player_distance <= 40:
                self.attack_player(player)
            
            dx = self.patrol_direction[0] * self.speed * 0.5
            dy = self.patrol_direction[1] * self.speed * 0.5
            
            new_x = self.x + dx
            new_y = self.y + dy
            
            if (self.check_collision(new_x, new_y, world) or 
                self.patrol_distance >= self.max_patrol_distance or
                self.check_room_boundary(new_x, new_y, world)):  # AJOUTER ÇA
                self.patrol_direction = (-self.patrol_direction[0], -self.patrol_direction[1])
                self.patrol_distance = 0
            else:
                if (not self.check_enemy_collision(new_x, new_y, other_enemies) and
                    not self.check_player_collision(new_x, new_y, player)):
                    self.x = new_x
                    self.y = new_y
                    self.patrol_distance += abs(dx) + abs(dy)
            
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    
    def follow_behavior(self, player, world, other_enemies):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0 and distance < 200:
            if distance <= 40:
                self.attack_player(player)
            
            dx = (dx / distance) * self.speed
            dy = (dy / distance) * self.speed
            
            new_x = self.x + dx
            new_y = self.y + dy
            
            if (not self.check_collision(new_x, self.y, world) and 
                not self.check_enemy_collision(new_x, self.y, other_enemies) and
                not self.check_player_collision(new_x, self.y, player) and
                not self.check_room_boundary(new_x, self.y, world)):  
                self.x = new_x
                
            if (not self.check_collision(self.x, new_y, world) and 
                not self.check_enemy_collision(self.x, new_y, other_enemies) and
                not self.check_player_collision(self.x, new_y, player) and
                not self.check_room_boundary(self.x, new_y, world)):  
                self.y = new_y
            
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.hp = self.max_hp
        self.alive = True
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.patrol_distance = 0
        self.is_aggressive = False  # Reset de l'agressivité
        self.patrol_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    
    # ... (garder toutes les autres méthodes comme avant)
    def attack_player(self, player):
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        player.take_damage(self.attack_damage)
        return True
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
    
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
    
    def check_enemy_collision(self, x, y, other_enemies):
        temp_rect = pygame.Rect(x, y, self.width, self.height)
        
        for other in other_enemies:
            if other != self and other.alive:
                if temp_rect.colliderect(other.rect):
                    return True
        return False
    
    def check_player_collision(self, x, y, player):
        temp_rect = pygame.Rect(x, y, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        return temp_rect.colliderect(player_rect)
    
    def draw(self, screen, camera_x, camera_y):
        if self.alive:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            current_time = time.time()
            if current_time - self.last_attack_time < 0.2:
                if self.enemy_type == "stationary":
                    color = (255, 150, 0)
                elif self.enemy_type == "patrol":
                    color = (150, 100, 255) if not self.is_aggressive else (255, 100, 255)
                else:
                    color = (255, 100, 100)
            else:
                if self.enemy_type == "stationary":
                    color = (255, 100, 0)
                elif self.enemy_type == "patrol":
                    color = (100, 50, 200) if not self.is_aggressive else (200, 50, 200)
                else:
                    color = (255, 0, 0)
            
            pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))

    def check_room_boundary(self, x, y, world):
        """Empêche l'ennemi de sortir de sa salle d'origine"""
        # Convertir position en tiles
        tile_x = int(x // world.tile_size)
        tile_y = int(y // world.tile_size)
        
        # Trouver la salle d'origine
        start_tile_x = int(self.start_x // world.tile_size)
        start_tile_y = int(self.start_y // world.tile_size)
        
        for room_name, room_data in world.rooms.items():
            if (room_data["x"] <= start_tile_x < room_data["x"] + room_data["w"] and
                room_data["y"] <= start_tile_y < room_data["y"] + room_data["h"]):
                # Vérifier si la nouvelle position est toujours dans cette salle
                if (room_data["x"] <= tile_x < room_data["x"] + room_data["w"] and
                    room_data["y"] <= tile_y < room_data["y"] + room_data["h"]):
                    return False  # Pas de collision, reste dans la salle
                else:
                    return True   # Collision, sort de la salle
        
        return False