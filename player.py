import pygame
import math
import time

class PlayerProjectile:
    def __init__(self, x, y, dx, dy, damage, max_range):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.speed = 200  
        self.lifetime = 3.0  # 3 secondes de vie
        self.creation_time = time.time()
        self.damage = damage
        self.max_range = max_range
        self.width = 6
        self.height = 6
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Direction normalisée
        self.velocity_x = dx * self.speed
        self.velocity_y = dy * self.speed
    
    def update(self, world, enemies):
        current_time = time.time()
        
        # Vérifier si le projectile doit disparaître
        if current_time - self.creation_time >= self.lifetime:
            return False
        
        # Déplacer le projectile
        dt = 1/60  # 60 FPS
        new_x = self.x + self.velocity_x * dt
        new_y = self.y + self.velocity_y * dt
        
        # Vérifier la portée max
        distance = math.sqrt((new_x - self.start_x)**2 + (new_y - self.start_y)**2)
        if distance > self.max_range:
            return False
        
        # Vérifier collision avec les murs
        if self.check_collision(new_x, new_y, world):
            return False  # Détruire si collision mur
        
        # Mettre à jour la position
        self.x = new_x
        self.y = new_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Collision avec les ennemis
        for enemy in enemies:
            if enemy.alive and self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                print(f"Flèche touche ennemi : {self.damage} dégâts")
                return False  # Détruire après impact
        
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
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        pygame.draw.circle(screen, (0, 255, 255), (screen_x + 3, screen_y + 3), 3)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 27
        self.height = 27
        self.speed = 3
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Stats de combat ÉQUILIBRÉES CORRIGÉES
        self.max_hp = 250
        self.hp = self.max_hp
        self.max_stamina = 50  # Gardé à 50
        self.stamina = self.max_stamina
        self.attack_damage = 15  # RÉDUIT : 25 → 15 pour ne pas one-shot
        self.attack_range = 35  # Réduit aussi un peu
        
        # Timers - Cooldowns différents selon l'arme
        self.last_attack_time = 0
        self.melee_cooldown = 0.5
        self.bow_cooldown = 1.2
        self.last_damage_time = 0
        self.damage_cooldown = 1.0

        self.alive = True
        self.game_ref = None
    
    def set_game_reference(self, game):
        """Permet au joueur d'accéder aux méthodes de vérification du jeu"""
        self.game_ref = game
    
    def update(self, world, enemies=None, weapon=None, player_projectiles=None):
        if not self.alive:
            return
        
        current_time = time.time()
        
        # Gestion du dash SEULEMENT si les attributs existent
        if hasattr(self, 'is_dashing') and self.is_dashing:
            # Vérifier si le dash est terminé
            if current_time - self.dash_start_time >= self.dash_duration:
                self.is_dashing = False
            else:
                # Mouvement de dash
                dash_speed = self.dash_distance / self.dash_duration
                dx = self.dash_direction[0] * dash_speed * (1/60)
                dy = self.dash_direction[1] * dash_speed * (1/60)
                
                new_x = self.x + dx
                new_y = self.y + dy
                
                if not self.check_collision(new_x, self.y, world):
                    self.x = new_x
                if not self.check_collision(self.x, new_y, world):
                    self.y = new_y
                
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                return  # Skip le mouvement normal pendant le dash
        
        # Mouvement normal (seulement si pas en dash)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Sprint (consomme stamina)
        is_sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0
        current_speed = self.speed * 1.5 if is_sprinting else self.speed
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            dx = (dx / length) * current_speed
            dy = (dy / length) * current_speed
            
            # Consommer stamina si sprint
            if is_sprinting:
                self.stamina -= 30 * (1/60)
        
        # Régénération stamina (seulement si pas de sprint)
        if not is_sprinting:
            self.stamina = min(self.max_stamina, self.stamina + 50 * (1/60))
        
        # Mouvement avec collision
        new_x = self.x + dx
        new_y = self.y + dy
        
        if not self.check_collision(new_x, self.y, world):
            self.x = new_x
        if not self.check_collision(self.x, new_y, world):
            self.y = new_y
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Gestion de l'attaque - CORRECTION: ne plus utiliser self.attack_cooldown
        if keys[pygame.K_SPACE] and enemies:
            self.attack(enemies, weapon, player_projectiles)
    
    def attack(self, enemies, weapon=None, player_projectiles=None):
        current_time = time.time()
        
        # Cooldown différent selon l'arme
        if weapon and weapon.weapon_type == "bow":
            attack_cooldown = self.bow_cooldown
        else:
            attack_cooldown = self.melee_cooldown
        
        if current_time - self.last_attack_time < attack_cooldown:
            return False
        
        self.last_attack_time = current_time
        self.last_weapon_used = weapon  # Tracker la dernière arme utilisée
        
        print(f"=== ATTAQUE ===")
        print(f"Arme: {weapon.name if weapon else 'Aucune'}")
        print(f"Type: {weapon.weapon_type if weapon else 'corps à corps'}")
        print(f"Cooldown utilisé: {attack_cooldown}")
        print(f"Projectiles liste: {player_projectiles is not None}")
        if player_projectiles is not None:
            print(f"Nb projectiles actuels: {len(player_projectiles)}")
        
        # Si c'est un arc, tirer une flèche
        if weapon and weapon.weapon_type == "bow":
            if player_projectiles is not None:
                success = self.shoot_arrow(weapon, player_projectiles)
                print(f"Tir réussi: {success}")
                return success
            else:
                print("ERREUR: Liste de projectiles manquante pour l'arc !")
                return False
        else:
            # Attaque au corps à corps normale
            print("Attaque corps à corps")
            attacked_enemies = []
            for enemy in enemies:
                if not enemy.alive:
                    continue
                    
                dx = enemy.x + enemy.width/2 - (self.x + self.width/2)
                dy = enemy.y + enemy.height/2 - (self.y + self.height/2)
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= self.attack_range:
                    # Calculer les dégâts avec critique
                    damage = self.attack_damage
                    is_critical = False
                    
                    # Vérifier coup critique
                    if self.game_ref and self.game_ref.check_critical_hit():
                        damage *= 2
                        is_critical = True
                        self.game_ref.show_loot_message("CRITIQUE !", (255, 255, 0))
                    
                    enemy.take_damage(damage)
                    attacked_enemies.append(enemy)
                    
                    # Affichage des dégâts
                    if is_critical:
                        print(f"Coup critique ! {damage} dégâts")
                    else:
                        print(f"{damage} dégâts")
            
            return len(attacked_enemies) > 0
        
    def shoot_arrow(self, weapon, player_projectiles):
        """Tire une salve de projectiles à 360° avec l'arc - Version simplifiée"""
        print(f"=== TIR D'ARC AVEC {weapon.name} ===")
        
        # Calculer les dégâts
        arrow_damage = weapon.damage_bonus + self.attack_damage
        arrow_range = weapon.range_bonus + 150  # Portée de base des flèches
        
        # Vérifier coup critique
        if self.game_ref and self.game_ref.check_critical_hit():
            arrow_damage *= 2
            self.game_ref.show_loot_message("FLÈCHES CRITIQUES !", (255, 255, 0))
            print("CRITIQUE !")
        
        # Créer 8 projectiles à 360°
        num_arrows = 8
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        for i in range(num_arrows):
            # Angle en radians
            angle = (i * 2 * math.pi) / num_arrows
            dx = math.cos(angle)
            dy = math.sin(angle)
            
            print(f"Créé flèche {i+1}: angle={angle:.2f}, dx={dx:.2f}, dy={dy:.2f}")
            
            # Créer le projectile (copie de la logique des ennemis)
            arrow = PlayerProjectile(
                center_x - 3,  # Centrer le projectile
                center_y - 3,
                dx, dy,
                arrow_damage,
                arrow_range
            )
            player_projectiles.append(arrow)
        
        print(f"Créé {num_arrows} flèches de {arrow_damage} dégâts, portée {arrow_range}")
        print(f"Total projectiles joueur: {len(player_projectiles)}")
        return True
    
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
        """Empêche le joueur de traverser les portes fermées - LOGIQUE FINALE CORRIGÉE"""
        player_tile_x = int(x // world.tile_size)
        player_tile_y = int(y // world.tile_size)
        
        # D'abord, déterminer la salle actuelle du joueur
        current_room = world.get_player_room(self.x, self.y)
        
        for door in world.doors:
            corridor = door["corridor"]
            from_room = world.rooms[door["from"]]
            to_room = world.rooms[door["to"]]
            
            # Si le joueur essaie d'entrer dans le couloir
            if (corridor[0] <= player_tile_x < corridor[0] + corridor[2] and
                corridor[1] <= player_tile_y < corridor[1] + corridor[3]):
                
                # CAS 1: Si les DEUX salles sont déverrouillées -> PASSAGE LIBRE (porte verte)
                if from_room["unlocked"] and to_room["unlocked"]:
                    print(f"Porte verte {door['from']} ↔ {door['to']} - Passage libre")
                    return False  # Pas de collision = passage autorisé
                
                # Déterminer vers quelle salle le joueur essaie d'aller
                if current_room == door["from"]:
                    # Le joueur va de "from" vers "to"
                    target_room_name = door["to"]
                    target_room = to_room
                    origin_room = from_room
                elif current_room == door["to"]:
                    # Le joueur va de "to" vers "from"
                    target_room_name = door["from"]
                    target_room = from_room
                    origin_room = to_room
                else:
                    # Le joueur n'est dans aucune des salles connectées
                    print(f"Joueur dans couloir sans salle d'origine identifiée - Bloquer")
                    return True
                
                # CAS 2: Si la salle d'origine n'est pas déverrouillée -> BLOQUER
                if not origin_room["unlocked"]:
                    print(f"Salle d'origine {current_room} non déverrouillée - Bloquer")
                    return True
                
                # CAS 3: Si la salle de destination n'est pas déverrouillée -> BLOQUER
                # (Le joueur doit d'abord nettoyer sa salle actuelle et utiliser F pour ouvrir)
                if not target_room["unlocked"]:
                    print(f"Salle destination {target_room_name} fermée - Bloquer passage")
                    return True
                
                # CAS 4: Si on arrive ici, les deux salles sont déverrouillées -> PERMETTRE
                print(f"Passage autorisé de {current_room} vers {target_room_name}")
                return False
        
        return False  # Pas dans un couloir = pas de collision de porte
    
    
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
            
            # Cercle d'attaque seulement pour les attaques au corps à corps (pas les arcs)
            if (current_time - self.last_attack_time < 0.1 and 
                hasattr(self, 'last_weapon_used') and 
                (not self.last_weapon_used or self.last_weapon_used.weapon_type != "bow")):
                center_x = screen_x + self.width // 2
                center_y = screen_y + self.height // 2
                pygame.draw.circle(screen, (255, 255, 0), (int(center_x), int(center_y)), 
                                 self.attack_range, 2)
                
    # Compétences

    def dash(self, world):
        """Effectue un dash dans la direction du mouvement"""
        # Vérifier si le joueur a la capacité de dash
        if not hasattr(self, 'dash_distance'):
            return False
        
        current_time = time.time()
        
        # Vérifier cooldown et stamina
        if (current_time - self.last_dash_time < self.dash_cooldown or 
            self.stamina < self.dash_stamina_cost or 
            self.is_dashing):
            return False
        
        # Déterminer la direction du dash
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Si aucune direction, dash vers la droite par défaut
        if dx == 0 and dy == 0:
            dx = 1
        
        # Normaliser la direction
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            dx = dx / length
            dy = dy / length
        
        # Consommer stamina et commencer le dash
        self.stamina -= self.dash_stamina_cost
        self.last_dash_time = current_time
        self.is_dashing = True
        self.dash_start_time = current_time
        self.dash_direction = (dx, dy)
        
        return True