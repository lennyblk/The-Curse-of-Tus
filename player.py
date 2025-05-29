# player.py
import pygame
import math
import time


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 27
        self.height = 27
        self.speed = 3
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Stats de combat
        self.max_hp = 400
        self.hp = self.max_hp
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.attack_damage = 25
        self.attack_range = 50
        
        # Timers
        self.last_attack_time = 0
        self.attack_cooldown = 0.5
        self.last_damage_time = 0
        self.damage_cooldown = 1.0  # 1 seconde d'invincibilité après dégâts
        
        self.alive = True
    
    def update(self, world, enemies=None):
        if not self.alive:
            return
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        # Mouvement (reste pareil)
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Sprint
        is_sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0
        current_speed = self.speed * 1.4 if is_sprinting else self.speed
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            dx = (dx / length) * current_speed
            dy = (dy / length) * current_speed
            
            if is_sprinting:
                self.stamina -= 40 * (1/60)
        
        # Régénération stamina
        if not is_sprinting:
            self.stamina = min(self.max_stamina, self.stamina + 20 * (1/60))
        
        # Mouvement avec collision
        new_x = self.x + dx
        new_y = self.y + dy
        
        if not self.check_collision(new_x, self.y, world):
            self.x = new_x
        if not self.check_collision(self.x, new_y, world):
            self.y = new_y
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Attaque - INDÉPENDANTE du mouvement
        if keys[pygame.K_SPACE] and enemies:
            self.attack(enemies)
    
    def attack(self, enemies):
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        
        # Attaquer tous les ennemis dans le rayon
        attacked_enemies = []
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            # Calculer distance
            dx = enemy.x + enemy.width/2 - (self.x + self.width/2)
            dy = enemy.y + enemy.height/2 - (self.y + self.height/2)
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= self.attack_range:
                enemy.take_damage(self.attack_damage)
                attacked_enemies.append(enemy)
        
        return len(attacked_enemies) > 0
    
    def take_damage(self, damage):
        current_time = time.time()
        if current_time - self.last_damage_time < self.damage_cooldown:
            return  # Invincible
        
        self.last_damage_time = current_time
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def check_collision(self, x, y, world):
        # Vérifier les 4 coins du joueur
        corners = [
            (x, y),
            (x + self.width, y),
            (x, y + self.height),
            (x + self.width, y + self.height)
        ]
        
        for corner_x, corner_y in corners:
            grid_x = int(corner_x // world.tile_size)
            grid_y = int(corner_y // world.tile_size)
            
            if (0 <= grid_x < world.width and 0 <= grid_y < world.height and 
                world.map[grid_y][grid_x] == 1):
                return True
        
        return self.check_door_collision(x, y, world)
    
    def check_door_collision(self, x, y, world):
        """Empêche le joueur de traverser les portes fermées"""
        player_tile_x = int(x // world.tile_size)
        player_tile_y = int(y // world.tile_size)
        
        for door in world.doors:
            corridor = door["corridor"]
            from_room = world.rooms[door["from"]]
            to_room = world.rooms[door["to"]]
            
            # Si le joueur est dans le couloir
            if (corridor[0] <= player_tile_x < corridor[0] + corridor[2] and
                corridor[1] <= player_tile_y < corridor[1] + corridor[3]):
                
                # Vérifier si les deux salles sont déverrouillées
                if not (from_room["unlocked"] and to_room["unlocked"]):
                    return True  # Collision = empêcher le passage
        
        return False
    
    def draw(self, screen, camera_x, camera_y):
        if self.alive:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            # Clignoter si invincible
            current_time = time.time()
            if current_time - self.last_damage_time < self.damage_cooldown:
                if int(current_time * 10) % 2:  # Clignotement
                    color = (150, 255, 150)
                else:
                    color = (0, 255, 0)
            else:
                color = (0, 255, 0)
            
            pygame.draw.rect(screen, color, (screen_x, screen_y, self.width, self.height))
            
            # Cercle d'attaque si on vient d'attaquer
            if current_time - self.last_attack_time < 0.1:
                center_x = screen_x + self.width // 2
                center_y = screen_y + self.height // 2
                pygame.draw.circle(screen, (255, 255, 0), (int(center_x), int(center_y)), 
                                 self.attack_range, 2)