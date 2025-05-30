# game.py - Version avec boss spawn dynamique et dégâts corrigés
import pygame
from player import Player
from world import World
from enemy import Enemy
from boss import Boss, BossProjectile
from ui import UI
from loot import Chest
from menu import InventoryMenu
import time
import math
import random

class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Screen shake
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_start_time = 0
    
    def follow_player(self, player, world):
        self.x = player.x - self.screen_width // 2
        self.y = player.y - self.screen_height // 2
        
        max_x = world.width * world.tile_size - self.screen_width
        max_y = world.height * world.tile_size - self.screen_height
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))
        
        self.apply_screen_shake()
    
    def start_screen_shake(self, intensity=10, duration=0.3):
        """Démarre un tremblement d'écran"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_start_time = time.time()
    
    def apply_screen_shake(self):
        """Applique le tremblement d'écran"""
        current_time = time.time()
        if current_time - self.shake_start_time < self.shake_duration:
            progress = (current_time - self.shake_start_time) / self.shake_duration
            current_intensity = self.shake_intensity * (1 - progress)
            
            shake_x = random.randint(-int(current_intensity), int(current_intensity))
            shake_y = random.randint(-int(current_intensity), int(current_intensity))
            
            self.x += shake_x
            self.y += shake_y

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.world = World(100, 80)
        self.player = Player(320, 320)
        self.player.set_game_reference(self)
        self.camera = Camera(screen.get_width(), screen.get_height())
        self.ui = UI(screen.get_width(), screen.get_height())
        self.projectiles = []
        self.player_projectiles = []
        
        # NOUVEAU: Système de boss spawn dynamique
        self.bosses = []  # Liste des boss actuellement actifs
        self.boss_projectiles = []
        self.spawned_bosses = {"boss": False, "secret": False}  # Track des boss déjà spawnés
        
        # Associer chaque ennemi à sa salle
        self.room_enemies = {
            "spawn": [],
            "room1": [],
            "room2": [],
            "central": [],
            "right": [],
            "big": [],
            "bottom": [],
            "boss": [],
            "secret": []
        }
        
        # Créer seulement les ennemis normaux
        self.create_enemies()
        
        # Interaction avec les portes
        self.near_door = None
        self.door_interaction_distance = 80

        self.chests = []
        self.player_skills = []  
        self.equipped_skills = []
        self.player_weapon = None

        # Positions des coffres
        self.chest_positions = {
            "room1": (1024, 450),
            "room2": (1764, 350),
            "central": (900, 1200),
            "right": (1604, 1000),
            "big": (2440, 900),
            "bottom": (600, 2000),
            "boss": (1700, 1800),
            "secret": (2604, 1900)
        }

        self.menu = InventoryMenu(screen.get_width(), screen.get_height())
        self.equipped_skills = [None, None, None, None]
        
        self.player_has_dash = False
        
        # Messages de loot
        self.loot_message = None
        self.loot_message_time = 0
        self.loot_message_duration = 3.0
        
        # Effets visuels
        self.particles = []
    
    def spawn_boss_if_needed(self, room_name):
        """Spawn un boss quand le joueur entre dans sa salle pour la première fois"""
        if room_name == "boss" and not self.spawned_bosses["boss"]:
            print("🔥 SPAWNING BOSS PRINCIPAL 🔥")
            boss_room = self.world.rooms["boss"]
            boss_center_x = (boss_room["x"] + boss_room["w"]//2) * self.world.tile_size
            boss_center_y = (boss_room["y"] + boss_room["h"]//2) * self.world.tile_size
            
            main_boss = Boss(boss_center_x - 32, boss_center_y - 32, "main", self.world)
            self.bosses.append(main_boss)
            self.spawned_bosses["boss"] = True
            
            # Effet visuel de spawn
            self.camera.start_screen_shake(20, 1.0)
            self.show_loot_message("🔥 GARDIEN DES PROFONDEURS APPARAÎT ! 🔥", (255, 0, 0))
            print(f"Boss principal spawné en ({boss_center_x}, {boss_center_y})")
            
        elif room_name == "secret" and not self.spawned_bosses["secret"]:
            print("👻 SPAWNING BOSS SECRET 👻")
            secret_room = self.world.rooms["secret"]
            secret_center_x = (secret_room["x"] + secret_room["w"]//2) * self.world.tile_size
            secret_center_y = (secret_room["y"] + secret_room["h"]//2) * self.world.tile_size
            
            secret_boss = Boss(secret_center_x - 32, secret_center_y - 32, "secret", self.world)
            self.bosses.append(secret_boss)
            self.spawned_bosses["secret"] = True
            
            # Effet visuel de spawn
            self.camera.start_screen_shake(20, 1.0)
            self.show_loot_message("👻 SEIGNEUR DES OMBRES APPARAÎT ! 👻", (150, 0, 150))
            print(f"Boss secret spawné en ({secret_center_x}, {secret_center_y})")
    
    def create_enemies(self):
        self.enemies = []
        
        # === SALLE 1 CORRIGÉE (22, 8, 20, 18) ===
        room1_enemies = [
            Enemy(1024, 540, "stationary"), Enemy(1104, 480, "stationary"),
            Enemy(754, 300, "patrol"), Enemy(1284, 300, "patrol"),
            Enemy(754, 780, "patrol"), Enemy(1284, 780, "patrol"),
            Enemy(854, 350, "normal"), Enemy(1004, 350, "normal"),
            Enemy(1154, 350, "normal"), Enemy(854, 700, "normal"),
            Enemy(1004, 700, "normal"), Enemy(1154, 700, "normal"),
        ]
        self.enemies.extend(room1_enemies)
        self.room_enemies["room1"] = room1_enemies
        
        # === SALLE 2 CORRIGÉE (45, 5, 18, 15) ===
        room2_enemies = [
            Enemy(1728, 400, "stationary"),
            Enemy(1490, 200, "patrol"), Enemy(1940, 200, "patrol"),
            Enemy(1490, 580, "patrol"), Enemy(1940, 580, "patrol"),
            Enemy(1590, 280, "normal"), Enemy(1690, 280, "normal"),
            Enemy(1790, 280, "normal"), Enemy(1590, 520, "normal"),
            Enemy(1690, 520, "normal"), Enemy(1790, 520, "normal"),
        ]
        self.enemies.extend(room2_enemies)
        self.room_enemies["room2"] = room2_enemies
        
        # === SALLE CENTRALE (15, 30, 25, 20) ===
        central_enemies = [
            Enemy(720, 1200, "stationary"), Enemy(880, 1200, "stationary"),
            Enemy(1040, 1200, "stationary"), Enemy(880, 1080, "stationary"),
            Enemy(880, 1320, "stationary"), Enemy(520, 1000, "patrol"),
            Enemy(520, 1400, "patrol"), Enemy(1220, 1000, "patrol"),
            Enemy(1220, 1400, "patrol"), Enemy(700, 980, "patrol"),
            Enemy(1000, 980, "patrol"), Enemy(600, 1100, "normal"),
            Enemy(760, 1100, "normal"), Enemy(1000, 1100, "normal"),
            Enemy(1160, 1100, "normal"), Enemy(600, 1300, "normal"),
            Enemy(760, 1300, "normal"), Enemy(1000, 1300, "normal"),
            Enemy(1160, 1300, "normal"),
        ]
        self.enemies.extend(central_enemies)
        self.room_enemies["central"] = central_enemies
        
        # === SALLE DROITE CORRIGÉE (42, 25, 20, 15) ===
        right_enemies = [
            Enemy(1664, 1040, "stationary"),
            Enemy(1384, 840, "patrol"), Enemy(1924, 840, "patrol"),
            Enemy(1384, 1240, "patrol"), Enemy(1924, 1240, "patrol"),
            Enemy(1504, 920, "normal"), Enemy(1624, 920, "normal"),
            Enemy(1744, 920, "normal"), Enemy(1504, 1160, "normal"),
            Enemy(1624, 1160, "normal"), Enemy(1744, 1160, "normal"),
        ]
        self.enemies.extend(right_enemies)
        self.room_enemies["right"] = right_enemies
        
        # === GRANDE SALLE CORRIGÉE (65, 20, 25, 25) ===
        big_enemies = [
            Enemy(2320, 900, "stationary"), Enemy(2480, 900, "stationary"),
            Enemy(2640, 900, "stationary"), Enemy(2400, 780, "stationary"),
            Enemy(2400, 1020, "stationary"), Enemy(2560, 780, "stationary"),
            Enemy(2560, 1020, "stationary"), Enemy(2120, 680, "patrol"),
            Enemy(2820, 680, "patrol"), Enemy(2120, 1380, "patrol"),
            Enemy(2820, 1380, "patrol"), Enemy(2120, 900, "patrol"),
            Enemy(2820, 900, "patrol"), Enemy(2200, 800, "normal"),
            Enemy(2280, 800, "normal"), Enemy(2440, 800, "normal"),
            Enemy(2600, 800, "normal"), Enemy(2680, 800, "normal"),
            Enemy(2200, 1000, "normal"), Enemy(2280, 1000, "normal"),
            Enemy(2440, 1000, "normal"), Enemy(2600, 1000, "normal"),
            Enemy(2680, 1000, "normal"),
        ]
        self.enemies.extend(big_enemies)
        self.room_enemies["big"] = big_enemies
        
        # === SALLE BAS-GAUCHE (10, 55, 20, 15) ===
        bottom_enemies = [
            Enemy(640, 2000, "stationary"),
            Enemy(360, 1800, "patrol"), Enemy(920, 1800, "patrol"),
            Enemy(360, 2200, "patrol"), Enemy(920, 2200, "patrol"),
            Enemy(480, 1880, "normal"), Enemy(600, 1880, "normal"),
            Enemy(720, 1880, "normal"), Enemy(480, 2120, "normal"),
            Enemy(600, 2120, "normal"), Enemy(720, 2120, "normal"),
        ]
        self.enemies.extend(bottom_enemies)
        self.room_enemies["bottom"] = bottom_enemies
        
        # === SALLE BOSS (40, 50, 30, 20) - RÉDUITE car boss présent ===
        boss_enemies = [
            Enemy(1520, 1840, "stationary"), Enemy(1680, 1840, "stationary"),
            Enemy(1840, 1840, "stationary"), Enemy(2000, 1840, "stationary"),
            Enemy(1600, 1720, "patrol"), Enemy(1920, 1720, "patrol"),
            Enemy(1400, 1720, "normal"), Enemy(1560, 1720, "normal"),
            Enemy(1800, 1720, "normal"), Enemy(1960, 1720, "normal"),
        ]
        self.enemies.extend(boss_enemies)
        self.room_enemies["boss"] = boss_enemies
        
        # === SALLE SECRET - RÉDUITE car boss secret présent ===
        secret_enemies = [
            Enemy(2544, 1840, "stationary"),
            Enemy(2384, 1840, "normal"), Enemy(2784, 1840, "normal"),
        ]
        self.enemies.extend(secret_enemies)
        self.room_enemies["secret"] = secret_enemies
    
    def check_room_cleared(self, room_name):
        """Vérifie si tous les ennemis d'une salle sont morts"""
        if room_name not in self.room_enemies:
            return True
        
        for enemy in self.room_enemies[room_name]:
            if enemy.alive:
                return False
        return True
    
    def check_door_interaction(self):
        """Vérifie si le joueur peut interagir avec une porte"""
        current_room = self.world.get_player_room(self.player.x, self.player.y)
        
        if not current_room:
            return None
        
        for door in self.world.doors:
            if door["from"] == current_room or door["to"] == current_room:
                corridor = door["corridor"]
                
                # Position spéciale pour la porte right→boss
                if door["from"] == "right" and door["to"] == "boss":
                    door_center_x = corridor[0] * self.world.tile_size + 16
                    door_center_y = corridor[1] * self.world.tile_size + 16
                else:
                    door_center_x = (corridor[0] + corridor[2]//2) * self.world.tile_size
                    door_center_y = (corridor[1] + corridor[3]//2) * self.world.tile_size
                
                player_center_x = self.player.x + self.player.width//2
                player_center_y = self.player.y + self.player.height//2
                
                distance = ((player_center_x - door_center_x)**2 + (player_center_y - door_center_y)**2)**0.5
                
                if distance <= self.door_interaction_distance:
                    if door["from"] == current_room:
                        target_room = door["to"]
                    else:
                        target_room = door["from"]
                    
                    if self.check_room_cleared(current_room):
                        return {"door": door, "can_open": True, "to_room": target_room}
                    else:
                        alive_count = sum(1 for enemy in self.room_enemies[current_room] if enemy.alive)
                        return {"door": door, "can_open": False, 
                            "reason": f"Éliminez tous les ennemis d'abord ! ({alive_count} restants)"}
        
        return None
    
    def check_critical_hit(self):
        """Vérifie si l'attaque est critique"""
        crit_skill = None
        for skill in self.equipped_skills:
            if skill and skill.effect_type == "crit":
                crit_skill = skill
                break
        
        if crit_skill:
            import random
            return random.random() < crit_skill.effect_value
        return False
    
    def update(self):
        keys = pygame.key.get_pressed()
        if not self.player.alive and keys[pygame.K_r]:
            self.restart_game()
            return
        
        # NOUVEAU: Vérifier si on doit spawn un boss
        current_room = self.world.get_player_room(self.player.x, self.player.y)
        if current_room in ["boss", "secret"] and self.world.rooms[current_room]["unlocked"]:
            self.spawn_boss_if_needed(current_room)
        
        self.update_player()
        
        # Update ennemis normaux
        for enemy in self.enemies:
            enemy.update(self.player, self.world, self.enemies, self.projectiles)
        
        # Update boss actifs seulement
        for boss in self.bosses:
            if boss.alive:
                boss.update(self.player, self.world, self.boss_projectiles)
                
                # Screen shake lors des attaques spéciales
                current_time = time.time()
                if (current_time - boss.last_special_time < 0.5 and 
                    current_time - boss.last_special_time > 0.4):
                    self.camera.start_screen_shake(15, 0.4)
        
        # Update projectiles
        self.projectiles = [proj for proj in self.projectiles 
                        if proj.update(self.player, self.world)]
        
        self.player_projectiles = [proj for proj in self.player_projectiles 
                                if proj.update(self.world, self.enemies)]
        
        self.boss_projectiles = [proj for proj in self.boss_projectiles 
                               if proj.update(self.world)]
        
        # Collisions projectiles → joueur
        for projectile in self.projectiles[:]:
            if projectile.rect.colliderect(self.player.rect):
                if self.check_dodge():
                    print("Esquive réussie !")
                    self.show_loot_message("Esquive !", (0, 255, 255))
                else:
                    self.player.take_damage(10)
                self.projectiles.remove(projectile)
        
        # Collisions projectiles de boss → joueur
        for projectile in self.boss_projectiles[:]:
            if projectile.rect.colliderect(self.player.rect):
                if self.check_dodge():
                    print("Esquive de projectile boss !")
                    self.show_loot_message("Esquive Boss !", (0, 255, 255))
                else:
                    self.player.take_damage(projectile.damage)
                    print(f"Boss projectile touche pour {projectile.damage} dégâts")
                self.boss_projectiles.remove(projectile)
        
        # Collisions joueur → boss (contact direct)
        for boss in self.bosses:
            if boss.alive and boss.rect.colliderect(self.player.rect):
                current_time = time.time()
                if current_time - self.player.last_damage_time > self.player.damage_cooldown:
                    self.player.take_damage(25)
                    print("Contact direct avec boss !")
        
        # CORRECTION: Collisions projectiles joueur → boss
        for projectile in self.player_projectiles[:]:
            for boss in self.bosses:
                if boss.alive and projectile.rect.colliderect(boss.rect):
                    if boss.take_damage(projectile.damage):
                        print(f"Projectile touche {boss.name} pour {projectile.damage} dégâts")
                        self.camera.start_screen_shake(5, 0.2)
                        if not boss.alive:
                            self.show_loot_message(f"{boss.name} VAINCU!", (255, 215, 0))
                            self.camera.start_screen_shake(20, 1.0)
                    self.player_projectiles.remove(projectile)
                    break
        
        # CORRECTION: Collisions attaques au corps à corps → boss
        if hasattr(self.player, 'last_attack_time'):
            current_time = time.time()
            if current_time - self.player.last_attack_time < 0.1:  # Dans les 0.1s après une attaque
                # Vérifier si une arme à distance a été utilisée
                weapon_is_ranged = (self.player_weapon and 
                                  self.player_weapon.weapon_type == "bow")
                
                # Seulement pour les attaques au corps à corps
                if not weapon_is_ranged:
                    player_center_x = self.player.x + self.player.width/2
                    player_center_y = self.player.y + self.player.height/2
                    
                    for boss in self.bosses:
                        if boss.alive:
                            boss_center_x = boss.x + boss.width/2
                            boss_center_y = boss.y + boss.height/2
                            
                            dx = boss_center_x - player_center_x
                            dy = boss_center_y - player_center_y
                            distance = math.sqrt(dx*dx + dy*dy)
                            
                            if distance <= self.player.attack_range:
                                # Calculer les dégâts avec critique
                                damage = self.player.attack_damage
                                is_critical = False
                                
                                if self.check_critical_hit():
                                    damage *= 2
                                    is_critical = True
                                    self.show_loot_message("CRITIQUE !", (255, 255, 0))
                                
                                if boss.take_damage(damage):
                                    if is_critical:
                                        print(f"Coup critique sur {boss.name} ! {damage} dégâts")
                                    else:
                                        print(f"Attaque corps à corps sur {boss.name} : {damage} dégâts")
                                    
                                    self.camera.start_screen_shake(8, 0.3)
                                    if not boss.alive:
                                        self.show_loot_message(f"{boss.name} VAINCU!", (255, 215, 0))
                                        self.camera.start_screen_shake(25, 1.2)
        
        self.near_door = self.check_door_interaction()
        self.camera.follow_player(self.player, self.world)

        for room_name in self.room_enemies.keys():
            if room_name != "spawn":
                self.spawn_chest_if_room_cleared(room_name)
        
        self.check_chest_interaction()
        self.update_particles()
    
    def update_particles(self):
        """Met à jour les particules d'effets visuels"""
        # Particules autour des boss vivants
        for boss in self.bosses:
            if boss.alive and random.random() < 0.3:
                offset_x = random.randint(-40, 40)
                offset_y = random.randint(-40, 40)
                particle = {
                    "x": boss.x + boss.width//2 + offset_x,
                    "y": boss.y + boss.height//2 + offset_y,
                    "velocity_x": random.uniform(-20, 20),
                    "velocity_y": random.uniform(-20, 20),
                    "lifetime": random.uniform(1.0, 2.0),
                    "creation_time": time.time(),
                    "color": boss.color if boss.boss_type == "main" else (150, 0, 150),
                    "size": random.randint(2, 4)
                }
                self.particles.append(particle)
        
        # Update et nettoyage des particules
        current_time = time.time()
        self.particles = [p for p in self.particles 
                         if current_time - p["creation_time"] < p["lifetime"]]
        
        # Déplacer les particules
        for particle in self.particles:
            dt = 1/60
            particle["x"] += particle["velocity_x"] * dt
            particle["y"] += particle["velocity_y"] * dt
    
    def update_player(self):
        """Met à jour le joueur avec gestion des compétences améliorée"""
        self.player.update(self.world, self.enemies, self.player_weapon, self.player_projectiles)
        
        self.apply_berserker_effect()
        self.check_vampire_healing()
    
    def apply_berserker_effect(self):
        """Applique l'effet Berserker si HP < 50%"""
        base_damage = 15  # Dégâts de base du joueur
        weapon_bonus = self.player_weapon.damage_bonus if self.player_weapon else 0
        
        berserker_skill = None
        for skill in self.equipped_skills:
            if skill and skill.effect_type == "berserker":
                berserker_skill = skill
                break
        
        if berserker_skill and self.player.hp < self.player.max_hp * 0.5:
            berserker_damage = int((base_damage + weapon_bonus) * berserker_skill.effect_value)
            self.player.attack_damage = base_damage + weapon_bonus + berserker_damage
        else:
            self.player.attack_damage = base_damage + weapon_bonus
    
    def check_vampire_healing(self):
        """Vérifie si des ennemis sont morts pour le vampirisme"""
        vampire_skill = None
        for skill in self.equipped_skills:
            if skill and skill.effect_type == "vampire":
                vampire_skill = skill
                break
        
        if vampire_skill:
            dead_enemies = sum(1 for enemy in self.enemies if not enemy.alive)
            dead_bosses = sum(1 for boss in self.bosses if not boss.alive)
            total_dead = dead_enemies + dead_bosses
            
            if not hasattr(self, 'last_dead_count'):
                self.last_dead_count = 0
            
            if total_dead > self.last_dead_count:
                kills = total_dead - self.last_dead_count
                heal_amount = kills * vampire_skill.effect_value
                old_hp = self.player.hp
                self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
                
                if self.player.hp > old_hp:
                    self.show_loot_message(f"Vampirisme: +{self.player.hp - old_hp} HP", (255, 100, 100))
                
                self.last_dead_count = total_dead
    
    def check_dodge(self):
        """Vérifie si le joueur esquive l'attaque"""
        dodge_skill = None
        for skill in self.equipped_skills:
            if skill and skill.effect_type == "dodge":
                dodge_skill = skill
                break
        
        if dodge_skill:
            import random
            return random.random() < dodge_skill.effect_value
        return False
    
    def all_bosses_defeated(self):
        """Vérifie si TOUS les boss (les 2) ont été spawnés ET vaincus"""
        # Les deux boss doivent avoir été spawnés
        if not (self.spawned_bosses["boss"] and self.spawned_bosses["secret"]):
            return False
        
        # Et ils doivent tous être morts
        return len(self.bosses) >= 2 and all(not boss.alive for boss in self.bosses)
    
    def restart_game(self):
        self.player = Player(320, 320)
        self.player.set_game_reference(self)
        self.projectiles = []
        self.player_projectiles = []
        
        # Reset système de boss
        self.bosses = []
        self.boss_projectiles = []
        self.spawned_bosses = {"boss": False, "secret": False}
        
        self.chests = []
        self.equipped_skills = [None, None, None, None]
        self.player_weapon = None
        self.player_has_dash = False
        
        self.last_dead_count = 0
        self.loot_message = None
        self.particles = []
        
        for room_name in self.world.rooms:
            if room_name != "spawn":
                self.world.rooms[room_name]["unlocked"] = False
        
        for enemy in self.enemies:
            enemy.reset()
        
        self.world.update_doors()
    
    def draw(self):
        self.screen.fill((30, 30, 30))
        self.world.draw_world(self.screen, self.camera)
        
        # Dessiner les ennemis normaux
        for enemy in self.enemies:
            if self.is_enemy_visible(enemy):
                enemy.draw(self.screen, self.camera.x, self.camera.y)
        
        # Dessiner les boss actifs
        for boss in self.bosses:
            if self.is_boss_visible(boss):
                boss.draw(self.screen, self.camera.x, self.camera.y)
        
        # Dessiner tous les projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen, self.camera.x, self.camera.y)
        
        for projectile in self.player_projectiles:
            projectile.draw(self.screen, self.camera.x, self.camera.y)
        
        for projectile in self.boss_projectiles:
            projectile.draw(self.screen, self.camera.x, self.camera.y)
        
        # Dessiner les particules
        self.draw_particles()
        
        for chest in self.chests:
            chest.draw(self.screen, self.camera.x, self.camera.y)
        
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Interface utilisateur
        if self.near_door and not self.menu.is_open and not self.menu.showing_loot:
            if self.near_door["can_open"]:
                message = f"Appuyez sur F pour ouvrir vers {self.near_door.get('to_room', 'salle')}"
                color = (0, 255, 0)
            else:
                message = self.near_door["reason"]
                color = (255, 100, 100)
            
            font = pygame.font.Font(None, 36)
            text = font.render(message, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 100))
            
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)
            bg_surface.fill((0, 0, 0))
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(text, text_rect)
        
        self.draw_loot_message()
        
        # Interface utilisateur avec boss actifs
        self.ui.draw_hud(self.screen, self.player, self.enemies, self.player_weapon, self.bosses)
        
        self.menu.draw(self.screen, self.equipped_skills)
    
    def draw_particles(self):
        """Dessine les particules d'effets visuels"""
        current_time = time.time()
        for particle in self.particles:
            # Calculer l'alpha basé sur la durée de vie restante
            time_ratio = (current_time - particle["creation_time"]) / particle["lifetime"]
            alpha = int(255 * (1 - time_ratio))
            
            if alpha > 0:
                screen_x = particle["x"] - self.camera.x
                screen_y = particle["y"] - self.camera.y
                
                # Créer une surface avec transparence
                particle_surface = pygame.Surface((particle["size"], particle["size"]))
                particle_surface.set_alpha(alpha)
                particle_surface.fill(particle["color"])
                
                self.screen.blit(particle_surface, (screen_x, screen_y))

    def draw_loot_message(self):
        """Dessine le message de loot temporaire"""
        current_time = time.time()
        if self.loot_message and (current_time - self.loot_message_time) < self.loot_message_duration:
            font = pygame.font.Font(None, 48)
            text = font.render(self.loot_message["text"], True, self.loot_message["color"])
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 200))
            
            bg_rect = text_rect.inflate(40, 20)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(200)
            bg_surface.fill((0, 0, 0))
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(text, text_rect)
        elif self.loot_message:
            self.loot_message = None

    def show_loot_message(self, text, color=(255, 255, 255)):
        """Affiche un message temporaire"""
        self.loot_message = {"text": text, "color": color}
        self.loot_message_time = time.time()

    def is_enemy_visible(self, enemy):
        """Détermine si un ennemi doit être visible"""
        enemy_room = self.world.get_player_room(enemy.x, enemy.y)
        
        if enemy_room and self.world.rooms.get(enemy_room, {}).get("unlocked", False):
            return True
        
        enemy_tile_x = int(enemy.x // self.world.tile_size)
        enemy_tile_y = int(enemy.y // self.world.tile_size)
        
        for door in self.world.doors:
            corridor = door["corridor"]
            if (corridor[0] <= enemy_tile_x < corridor[0] + corridor[2] and
                corridor[1] <= enemy_tile_y < corridor[1] + corridor[3]):
                from_room = self.world.rooms[door["from"]]
                to_room = self.world.rooms[door["to"]]
                return from_room["unlocked"] or to_room["unlocked"]
        
        return False
    
    def is_boss_visible(self, boss):
        """Détermine si un boss doit être visible"""
        boss_room = self.world.get_player_room(boss.x, boss.y)
        
        # Les boss sont visibles seulement si leur salle est déverrouillée
        if boss_room and self.world.rooms.get(boss_room, {}).get("unlocked", False):
            return True
        
        return False

    def handle_key_press(self, key):
        """Gérer les pressions de touches depuis main.py"""
        
        if self.menu.showing_loot:
            result = self.menu.handle_loot_input(key, self.equipped_skills)
            if result == "cancel":
                return
            elif result and result["action"] == "equip":
                self.equip_skill(result["item"], result["slot"])
            return
        
        if key == pygame.K_i:
            self.menu.toggle_inventory()
            return
        
        if self.menu.is_open:
            return
        
        if key == pygame.K_f:
            if self.near_door and self.near_door["can_open"]:
                current_room = self.world.get_player_room(self.player.x, self.player.y)
                if current_room == self.near_door["door"]["to"]:
                    target_room = self.near_door["door"]["from"]
                else:
                    target_room = self.near_door["door"]["to"]
                
                self.world.unlock_room(target_room)
                print(f"Porte ouverte ! Salle {target_room} déverrouillée depuis {current_room}")
                self.near_door = None
        
        elif key == pygame.K_h and self.equipped_skills[0]:
            self.use_skill(self.equipped_skills[0])
        elif key == pygame.K_j and self.equipped_skills[1]:
            self.use_skill(self.equipped_skills[1])
        elif key == pygame.K_k and self.equipped_skills[2]:
            self.use_skill(self.equipped_skills[2])
        elif key == pygame.K_l and self.equipped_skills[3]:
            self.use_skill(self.equipped_skills[3])

    def spawn_chest_if_room_cleared(self, room_name):
        """Fait apparaître un coffre si la salle est nettoyée"""
        if (self.check_room_cleared(room_name) and 
            room_name in self.chest_positions and
            not any(chest.x == self.chest_positions[room_name][0] for chest in self.chests)):
            
            chest_x, chest_y = self.chest_positions[room_name]
            new_chest = Chest(chest_x, chest_y)
            self.chests.append(new_chest)
            print(f"Coffre apparu dans {room_name} !")

    def check_chest_interaction(self):
        """Vérifie l'interaction avec les coffres"""
        for chest in self.chests:
            if not chest.opened:
                distance = ((self.player.x - chest.x)**2 + (self.player.y - chest.y)**2)**0.5
                if distance <= 50:  
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:  
                        loot = chest.open(self.player)
                        if loot:
                            self.handle_loot(loot)

    def handle_loot(self, loot):
        """Gère le loot obtenu"""
        if hasattr(loot, 'effect_type'):
            self.menu.show_loot_selection(loot)
        elif hasattr(loot, 'weapon_type'):
            self.menu.show_loot_selection(loot)
        else:
            self.use_potion(loot)
            self.show_loot_message(f"{loot} utilisée !", (0, 255, 0))

    def equip_skill(self, skill, slot):
        """Équipe une compétence dans un slot"""
        if hasattr(skill, 'effect_type'):
            old_skill = self.equipped_skills[slot]
            self.equipped_skills[slot] = skill
            skill.key_binding = ['H', 'J', 'K', 'L'][slot]
            
            self.apply_passive_effects()
            
            print(f"Compétence {skill.name} équipée sur {skill.key_binding}")
            if old_skill:
                print(f"Ancienne compétence {old_skill.name} remplacée")
        
        elif hasattr(skill, 'weapon_type'):
            self.player_weapon = skill
            self.apply_passive_effects()
            print(f"Arme équipée : {skill.name}")
        
        else:
            self.use_potion(skill)
            self.show_loot_message(f"{skill} utilisée !", (0, 255, 0))

    def apply_passive_effects(self):
        """Applique les effets passifs des compétences équipées"""
        print("Application des effets passifs...")
        
        base_speed = 3
        base_stamina = 50  
        base_range = 35    
        base_damage = 15   # Corrigé pour correspondre aux dégâts dans player.py
        
        self.player.speed = base_speed
        self.player.max_stamina = base_stamina
        self.player.attack_range = base_range
        self.player.attack_damage = base_damage
        
        if hasattr(self.player, 'dash_distance'):
            delattr(self.player, 'dash_distance')
            delattr(self.player, 'dash_stamina_cost')
            delattr(self.player, 'dash_cooldown')
            delattr(self.player, 'last_dash_time')
            delattr(self.player, 'is_dashing')
            delattr(self.player, 'dash_duration')
            delattr(self.player, 'dash_start_time')
            delattr(self.player, 'dash_direction')
        
        self.player_has_dash = False
        
        for i, skill in enumerate(self.equipped_skills):
            if skill:
                print(f"Applique compétence {skill.name} (slot {i})")
                if skill.effect_type == "speed":
                    old_speed = self.player.speed
                    self.player.speed *= (1 + skill.effect_value)
                    print(f"Vitesse: {old_speed} -> {self.player.speed}")
                elif skill.effect_type == "stamina":
                    old_stamina = self.player.max_stamina
                    self.player.max_stamina += skill.effect_value
                    print(f"Stamina max: {old_stamina} -> {self.player.max_stamina}")
                elif skill.effect_type == "dash":
                    self.player.dash_distance = 150
                    self.player.dash_stamina_cost = 50
                    self.player.dash_cooldown = 1.0
                    self.player.last_dash_time = 0
                    self.player.is_dashing = False
                    self.player.dash_duration = 0.2
                    self.player.dash_start_time = 0
                    self.player.dash_direction = (0, 0)
                    self.player_has_dash = True
                    print("Dash activé!")
        
        if self.player_weapon:
            print(f"Applique arme: {self.player_weapon.name}")
            old_damage = self.player.attack_damage
            self.player.attack_damage += self.player_weapon.damage_bonus
            print(f"Dégâts: {old_damage} -> {self.player.attack_damage}")
            
            if self.player_weapon.weapon_type == "sword":
                old_range = self.player.attack_range
                self.player.attack_range += self.player_weapon.range_bonus
                print(f"Portée: {old_range} -> {self.player.attack_range}")
        
        self.player.stamina = min(self.player.stamina, self.player.max_stamina)
        print(f"Stats finales - Vitesse: {self.player.speed}, Dégâts: {self.player.attack_damage}, Portée: {self.player.attack_range}")

    def use_skill(self, skill):
        """Utilise une compétence active"""
        if skill.effect_type == "dash" and self.player_has_dash:
            success = self.player.dash(self.world)
            if success:
                self.show_loot_message("Dash !", (255, 255, 0))

    def use_potion(self, potion_name):
        """Utilise une potion"""
        if potion_name == "Potion de Vie":
            old_hp = self.player.hp
            self.player.hp = min(self.player.max_hp, self.player.hp + 50)
            heal_amount = self.player.hp - old_hp
            print(f"HP restaurés: +{heal_amount}")
        elif potion_name == "Potion Complète":
            self.player.hp = self.player.max_hp
            self.player.stamina = self.player.max_stamina
            print("HP et Stamina au maximum !")