# game.py - Corrections pour le système de compétences
import pygame
from player import Player
from world import World
from enemy import Enemy
from ui import UI
from loot import Chest
from menu import InventoryMenu
import time

class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def follow_player(self, player, world):
        self.x = player.x - self.screen_width // 2
        self.y = player.y - self.screen_height // 2
        
        max_x = world.width * world.tile_size - self.screen_width
        max_y = world.height * world.tile_size - self.screen_height
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.world = World(100, 80)
        self.player = Player(320, 320)
        self.player.set_game_reference(self)  # Connecter le joueur au jeu
        self.camera = Camera(screen.get_width(), screen.get_height())
        self.ui = UI(screen.get_width(), screen.get_height())
        self.projectiles = []  # Projectiles des ennemis
        self.player_projectiles = []  # Projectiles du joueur
        
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
        
        # Créer les ennemis et les assigner aux salles
        self.create_enemies()
        
        # Interaction avec les portes
        self.near_door = None
        self.door_interaction_distance = 80

        self.chests = []
        self.player_skills = []  
        self.equipped_skills = []  # 4 compétences équipées max
        self.player_weapon = None

        # Positions des coffres (apparaissent après nettoyage des salles)
        self.chest_positions = {
            "room1": (1200, 450),
            "room2": (1900, 350),
            "central": (900, 1200),
            "right": (1700, 1000),
            "big": (2600, 900),
            "bottom": (600, 2000),
            "boss": (1700, 1800),
            "secret": (2700, 1900)
        }

        self.menu = InventoryMenu(screen.get_width(), screen.get_height())
        self.equipped_skills = [None, None, None, None]  # H, J, K, L
        
        # Le joueur commence sans dash (doit le looter)
        self.player_has_dash = False
        
        # Messages de loot
        self.loot_message = None
        self.loot_message_time = 0
        self.loot_message_duration = 3.0  # 3 secondes
    
    def create_enemies(self):
        self.enemies = []
        
        # === SALLE 1 (25, 8, 20, 18) ===
        room1_enemies = [
            Enemy(1120, 540, "stationary"), Enemy(1200, 480, "stationary"),
            Enemy(850, 300, "patrol"), Enemy(1380, 300, "patrol"),
            Enemy(850, 780, "patrol"), Enemy(1380, 780, "patrol"),
            Enemy(950, 350, "normal"), Enemy(1100, 350, "normal"),
            Enemy(1250, 350, "normal"), Enemy(950, 700, "normal"),
            Enemy(1100, 700, "normal"), Enemy(1250, 700, "normal"),
        ]
        self.enemies.extend(room1_enemies)
        self.room_enemies["room1"] = room1_enemies
        
        # === SALLE 2 (50, 5, 18, 15) ===
        room2_enemies = [
            Enemy(1888, 400, "stationary"),
            Enemy(1650, 200, "patrol"), Enemy(2100, 200, "patrol"),
            Enemy(1650, 580, "patrol"), Enemy(2100, 580, "patrol"),
            Enemy(1750, 280, "normal"), Enemy(1850, 280, "normal"),
            Enemy(1950, 280, "normal"), Enemy(1750, 520, "normal"),
            Enemy(1850, 520, "normal"), Enemy(1950, 520, "normal"),
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
        
        # === SALLE DROITE (45, 25, 20, 15) ===
        right_enemies = [
            Enemy(1760, 1040, "stationary"),
            Enemy(1480, 840, "patrol"), Enemy(2020, 840, "patrol"),
            Enemy(1480, 1240, "patrol"), Enemy(2020, 1240, "patrol"),
            Enemy(1600, 920, "normal"), Enemy(1720, 920, "normal"),
            Enemy(1840, 920, "normal"), Enemy(1600, 1160, "normal"),
            Enemy(1720, 1160, "normal"), Enemy(1840, 1160, "normal"),
        ]
        self.enemies.extend(right_enemies)
        self.room_enemies["right"] = right_enemies
        
        # === GRANDE SALLE (70, 20, 25, 25) ===
        big_enemies = [
            Enemy(2480, 900, "stationary"), Enemy(2640, 900, "stationary"),
            Enemy(2800, 900, "stationary"), Enemy(2560, 780, "stationary"),
            Enemy(2560, 1020, "stationary"), Enemy(2720, 780, "stationary"),
            Enemy(2720, 1020, "stationary"), Enemy(2280, 680, "patrol"),
            Enemy(2980, 680, "patrol"), Enemy(2280, 1380, "patrol"),
            Enemy(2980, 1380, "patrol"), Enemy(2280, 900, "patrol"),
            Enemy(2980, 900, "patrol"), Enemy(2360, 800, "normal"),
            Enemy(2440, 800, "normal"), Enemy(2600, 800, "normal"),
            Enemy(2760, 800, "normal"), Enemy(2840, 800, "normal"),
            Enemy(2360, 1000, "normal"), Enemy(2440, 1000, "normal"),
            Enemy(2600, 1000, "normal"), Enemy(2760, 1000, "normal"),
            Enemy(2840, 1000, "normal"),
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
        
        # === SALLE BOSS (40, 50, 30, 20) ===
        boss_enemies = [
            Enemy(1520, 1840, "stationary"), Enemy(1680, 1840, "stationary"),
            Enemy(1840, 1840, "stationary"), Enemy(2000, 1840, "stationary"),
            Enemy(1600, 1720, "stationary"), Enemy(1760, 1720, "stationary"),
            Enemy(1920, 1720, "stationary"), Enemy(1600, 1960, "stationary"),
            Enemy(1760, 1960, "stationary"), Enemy(1920, 1960, "stationary"),
            Enemy(1320, 1640, "patrol"), Enemy(2180, 1640, "patrol"),
            Enemy(1320, 2200, "patrol"), Enemy(2180, 2200, "patrol"),
            Enemy(1320, 1920, "patrol"), Enemy(2180, 1920, "patrol"),
            Enemy(1400, 1720, "normal"), Enemy(1480, 1720, "normal"),
            Enemy(1560, 1720, "normal"), Enemy(1640, 1720, "normal"),
            Enemy(1720, 1720, "normal"), Enemy(1800, 1720, "normal"),
            Enemy(1880, 1720, "normal"), Enemy(1960, 1720, "normal"),
            Enemy(2040, 1720, "normal"), Enemy(1400, 1960, "normal"),
            Enemy(1480, 1960, "normal"), Enemy(1560, 1960, "normal"),
            Enemy(1640, 1960, "normal"), Enemy(1720, 1960, "normal"),
            Enemy(1800, 1960, "normal"), Enemy(1880, 1960, "normal"),
            Enemy(1960, 1960, "normal"), Enemy(2040, 1960, "normal"),
        ]
        self.enemies.extend(boss_enemies)
        self.room_enemies["boss"] = boss_enemies
        
        # === SALLE SECRÈTE (75, 50, 20, 20) ===
        secret_enemies = [
            Enemy(2640, 1840, "stationary"),
            Enemy(2720, 1760, "patrol"), Enemy(2720, 1920, "patrol"),
            Enemy(2480, 1840, "normal"), Enemy(2560, 1840, "normal"),
            Enemy(2800, 1840, "normal"), Enemy(2880, 1840, "normal"),
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
        
        # Vérifier chaque porte
        for door in self.world.doors:
            if door["from"] == current_room:
                corridor = door["corridor"]
                # Position du centre du couloir en pixels
                door_center_x = (corridor[0] + corridor[2]//2) * self.world.tile_size
                door_center_y = (corridor[1] + corridor[3]//2) * self.world.tile_size
                
                # Distance joueur-porte
                player_center_x = self.player.x + self.player.width//2
                player_center_y = self.player.y + self.player.height//2
                
                distance = ((player_center_x - door_center_x)**2 + (player_center_y - door_center_y)**2)**0.5
                
                if distance <= self.door_interaction_distance:
                    to_room = door["to"]
                    # Vérifier si la salle actuelle est nettoyée
                    if self.check_room_cleared(current_room):
                        return {"door": door, "can_open": True, "to_room": to_room}
                    else:
                        alive_count = sum(1 for enemy in self.room_enemies[current_room] if enemy.alive)
                        return {"door": door, "can_open": False, 
                            "reason": f"Éliminez tous les ennemis d'abord ! ({alive_count} restants)"}
        
        return None
    
    def update(self):
        keys = pygame.key.get_pressed()
        if not self.player.alive and keys[pygame.K_r]:
            self.restart_game()
            return
        
        # Update du joueur avec système amélioré
        self.update_player()
        
        for enemy in self.enemies:
            enemy.update(self.player, self.world, self.enemies, self.projectiles)
        
        self.projectiles = [proj for proj in self.projectiles 
                        if proj.update(self.player, self.world)]
        
        # Mettre à jour les projectiles du joueur
        self.player_projectiles = [proj for proj in self.player_projectiles 
                                if proj.update(self.world, self.enemies)]
        
        for projectile in self.projectiles[:]:
            if projectile.rect.colliderect(self.player.rect):
                # Vérifier esquive
                if self.check_dodge():
                    print("Esquive réussie !")
                    self.show_loot_message("Esquive !", (0, 255, 255))
                else:
                    self.player.take_damage(10)
                self.projectiles.remove(projectile)
        
        # Vérifier interaction avec portes
        self.near_door = self.check_door_interaction()
        self.camera.follow_player(self.player, self.world)

        # Vérifier si des coffres doivent apparaître
        for room_name in self.room_enemies.keys():
            if room_name != "spawn":
                self.spawn_chest_if_room_cleared(room_name)
        
        # Vérifier interaction avec coffres
        self.check_chest_interaction()
    
    def update_player(self):
        """Met à jour le joueur avec gestion des compétences améliorée"""
        self.player.update(self.world, self.enemies, self.player_weapon, self.player_projectiles)
        
        # Appliquer berserker en temps réel
        self.apply_berserker_effect()
        
        # Vérifier vampirisme sur kills
        self.check_vampire_healing()
    
    def apply_berserker_effect(self):
        """Applique l'effet Berserker si HP < 50%"""
        berserker_skill = None
        for skill in self.equipped_skills:
            if skill and skill.effect_type == "berserker":
                berserker_skill = skill
                break
        
        if berserker_skill and self.player.hp < self.player.max_hp * 0.5:
            # Calculer les dégâts de base (sans berserker)
            base_damage = 25  # Dégâts de base
            weapon_bonus = self.player_weapon.damage_bonus if self.player_weapon else 0
            
            # Appliquer bonus berserker
            berserker_damage = int((base_damage + weapon_bonus) * berserker_skill.effect_value)
            self.player.attack_damage = base_damage + weapon_bonus + berserker_damage
        else:
            # Recalculer les dégâts normaux
            base_damage = 25
            weapon_bonus = self.player_weapon.damage_bonus if self.player_weapon else 0
            self.player.attack_damage = base_damage + weapon_bonus
    
    def check_vampire_healing(self):
        """Vérifie si des ennemis sont morts pour le vampirisme"""
        vampire_skill = None
        for skill in self.equipped_skills:
            if skill and skill.effect_type == "vampire":
                vampire_skill = skill
                break
        
        if vampire_skill:
            # Compter les ennemis morts depuis la dernière vérification
            dead_enemies = sum(1 for enemy in self.enemies if not enemy.alive)
            if not hasattr(self, 'last_dead_count'):
                self.last_dead_count = 0
            
            if dead_enemies > self.last_dead_count:
                kills = dead_enemies - self.last_dead_count
                heal_amount = kills * vampire_skill.effect_value
                old_hp = self.player.hp
                self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
                
                if self.player.hp > old_hp:
                    self.show_loot_message(f"Vampirisme: +{self.player.hp - old_hp} HP", (255, 100, 100))
                
                self.last_dead_count = dead_enemies
    
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
    
    def restart_game(self):
        self.player = Player(320, 320)
        self.player.set_game_reference(self)  # Reconnecter après restart
        self.projectiles = []
        self.player_projectiles = []  # Reset projectiles joueur
        
        # Reset des coffres
        self.chests = []
        
        # Reset des compétences
        self.equipped_skills = [None, None, None, None]
        self.player_weapon = None
        self.player_has_dash = False
        
        # Reset compteurs
        self.last_dead_count = 0
        self.loot_message = None
        
        # Réinitialiser toutes les salles sauf spawn
        for room_name in self.world.rooms:
            if room_name != "spawn":
                self.world.rooms[room_name]["unlocked"] = False
        
        # Remettre tous les ennemis en vie
        for enemy in self.enemies:
            enemy.reset()
        
        self.world.update_doors()
    
    def draw(self):
        self.screen.fill((30, 30, 30))
        self.world.draw_world(self.screen, self.camera)
        
        for enemy in self.enemies:
            if self.is_enemy_visible(enemy):
                enemy.draw(self.screen, self.camera.x, self.camera.y)
        
        for projectile in self.projectiles:
            projectile.draw(self.screen, self.camera.x, self.camera.y)
        
        # Dessiner projectiles du joueur
        for projectile in self.player_projectiles:
            projectile.draw(self.screen, self.camera.x, self.camera.y)
        
        for chest in self.chests:
            chest.draw(self.screen, self.camera.x, self.camera.y)
        
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Messages de porte (seulement si pas de menu)
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
        
        # Message de loot
        self.draw_loot_message()
        
        # CHANGER CETTE LIGNE :
        self.ui.draw_hud(self.screen, self.player, self.enemies, self.player_weapon)
        
        # Dessiner les menus par-dessus tout
        self.menu.draw(self.screen, self.equipped_skills)

    def draw_loot_message(self):
        """Dessine le message de loot temporaire"""
        current_time = time.time()
        if self.loot_message and (current_time - self.loot_message_time) < self.loot_message_duration:
            font = pygame.font.Font(None, 48)
            text = font.render(self.loot_message["text"], True, self.loot_message["color"])
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 200))
            
            # Fond semi-transparent
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
        
        # Si dans une salle déverrouillée
        if enemy_room and self.world.rooms.get(enemy_room, {}).get("unlocked", False):
            return True
        
        # Si dans un couloir entre deux salles déverrouillées
        enemy_tile_x = int(enemy.x // self.world.tile_size)
        enemy_tile_y = int(enemy.y // self.world.tile_size)
        
        for door in self.world.doors:
            corridor = door["corridor"]
            if (corridor[0] <= enemy_tile_x < corridor[0] + corridor[2] and
                corridor[1] <= enemy_tile_y < corridor[1] + corridor[3]):
                # Dans un couloir - vérifier si au moins une salle connectée est déverrouillée
                from_room = self.world.rooms[door["from"]]
                to_room = self.world.rooms[door["to"]]
                return from_room["unlocked"] or to_room["unlocked"]
        
        return False

    def handle_key_press(self, key):
        """Gérer les pressions de touches depuis main.py"""
        
        # Gestion du menu de loot
        if self.menu.showing_loot:
            result = self.menu.handle_loot_input(key, self.equipped_skills)
            if result == "cancel":
                return
            elif result and result["action"] == "equip":
                self.equip_skill(result["item"], result["slot"])
            return
        
        # Inventaire
        if key == pygame.K_i:
            self.menu.toggle_inventory()
            return
        
        # Si inventaire ouvert, pas d'autres actions
        if self.menu.is_open:
            return
        
        # Portes
        if key == pygame.K_f:
            if self.near_door and self.near_door["can_open"]:
                to_room = self.near_door["door"]["to"]
                self.world.unlock_room(to_room)
                self.near_door = None
        
        # Compétences équipées (HJKL)
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
        if hasattr(loot, 'effect_type'):  # Compétence
            self.menu.show_loot_selection(loot)
        elif hasattr(loot, 'weapon_type'):  # Arme
            self.menu.show_loot_selection(loot)
        else:  # C'est une potion
            self.use_potion(loot)
            self.show_loot_message(f"{loot} utilisée !", (0, 255, 0))

    # Compétences
    
    def equip_skill(self, skill, slot):
        """Équipe une compétence dans un slot"""
        if hasattr(skill, 'effect_type'):  # C'est une compétence
            old_skill = self.equipped_skills[slot]
            self.equipped_skills[slot] = skill
            skill.key_binding = ['H', 'J', 'K', 'L'][slot]
            
            # Appliquer les effets passifs
            self.apply_passive_effects()
            
            print(f"Compétence {skill.name} équipée sur {skill.key_binding}")
            if old_skill:
                print(f"Ancienne compétence {old_skill.name} remplacée")
        
        elif hasattr(skill, 'weapon_type'):  # Arme
            self.player_weapon = skill
            self.apply_passive_effects()  # Réappliquer tous les effets
            print(f"Arme équipée : {skill.name}")
        
        else:  # Potion
            self.use_potion(skill)
            self.show_loot_message(f"{skill} utilisée !", (0, 255, 0))

    def apply_passive_effects(self):
        """Applique les effets passifs des compétences équipées"""
        print("Application des effets passifs...")  # Debug
        
        # Réinitialiser les stats aux valeurs de base
        base_speed = 3
        base_stamina = 100
        base_range = 50
        base_damage = 25
        
        self.player.speed = base_speed
        self.player.max_stamina = base_stamina
        self.player.attack_range = base_range
        self.player.attack_damage = base_damage
        
        # Réinitialiser le dash
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
        
        # Appliquer les bonus des compétences équipées
        for i, skill in enumerate(self.equipped_skills):
            if skill:
                print(f"Applique compétence {skill.name} (slot {i})")  # Debug
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
                # NOTE: berserker, dodge, crit, vampire sont gérés en temps réel
        
        # Appliquer les bonus d'arme
        if self.player_weapon:
            print(f"Applique arme: {self.player_weapon.name}")
            old_damage = self.player.attack_damage
            self.player.attack_damage += self.player_weapon.damage_bonus
            print(f"Dégâts: {old_damage} -> {self.player.attack_damage}")
            
            if self.player_weapon.weapon_type == "sword":
                old_range = self.player.attack_range
                self.player.attack_range += self.player_weapon.range_bonus  # Utilise le bonus de l'arme
                print(f"Portée: {old_range} -> {self.player.attack_range}")
            # Les arcs n'ajoutent PAS de portée d'attaque au corps à corps
        
        # Ajuster la stamina actuelle si nécessaire
        self.player.stamina = min(self.player.stamina, self.player.max_stamina)
        print(f"Stats finales - Vitesse: {self.player.speed}, Dégâts: {self.player.attack_damage}, Portée: {self.player.attack_range}")

    def use_skill(self, skill):
        """Utilise une compétence active"""
        if skill.effect_type == "dash" and self.player_has_dash:
            success = self.player.dash(self.world)
            if success:
                self.show_loot_message("Dash !", (255, 255, 0))
        # Les autres compétences sont passives pour l'instant

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