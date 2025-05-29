# game.py
import pygame
from player import Player
from world import World
from enemy import Enemy
from ui import UI

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
        self.camera = Camera(screen.get_width(), screen.get_height())
        self.ui = UI(screen.get_width(), screen.get_height())
        self.projectiles = []
        
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
        
        self.player.update(self.world, self.enemies)
        
        for enemy in self.enemies:
            enemy.update(self.player, self.world, self.enemies, self.projectiles)
        
        self.projectiles = [proj for proj in self.projectiles 
                        if proj.update(self.player, self.world)]
        
        for projectile in self.projectiles[:]:
            if projectile.rect.colliderect(self.player.rect):
                self.player.take_damage(10)
                self.projectiles.remove(projectile)
        
        # Vérifier interaction avec portes
        self.near_door = self.check_door_interaction()
        self.camera.follow_player(self.player, self.world)
    
    def restart_game(self):
        self.player = Player(320, 320)
        self.projectiles = []
        
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
        
        # Dessiner seulement les ennemis dans les salles déverrouillées
        for enemy in self.enemies:
            if self.is_enemy_visible(enemy):
                enemy.draw(self.screen, self.camera.x, self.camera.y)
    
        for projectile in self.projectiles:
            projectile.draw(self.screen, self.camera.x, self.camera.y)
        
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Message d'interaction avec porte - CORRIGER ICI
        if self.near_door:
            if self.near_door["can_open"]:
                message = f"Appuyez sur F pour ouvrir vers {self.near_door.get('to_room', 'salle')}"
                color = (0, 255, 0)
            else:
                message = self.near_door["reason"]
                color = (255, 100, 100)
            
            font = pygame.font.Font(None, 36)
            text = font.render(message, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 100))
            
            # Fond semi-transparent
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)
            bg_surface.fill((0, 0, 0))
            self.screen.blit(bg_surface, bg_rect)  # CHANGER screen en self.screen
            
            self.screen.blit(text, text_rect)
        
        self.ui.draw_hud(self.screen, self.player, self.enemies)

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
        
        if key == pygame.K_f:
            print(f"F pressé ! near_door = {self.near_door}")  # Debug
            if self.near_door:
                print(f"Can open: {self.near_door.get('can_open', 'Unknown')}")
                if self.near_door["can_open"]:
                    to_room = self.near_door["door"]["to"]
                    print(f"Tentative d'ouverture vers {to_room}")
                    self.world.unlock_room(to_room)
                    print(f"Porte ouverte vers {to_room} !")  
                    self.near_door = None
                else:
                    print(f"Porte non ouvrable: {self.near_door.get('reason', 'Raison inconnue')}")
            else:
                print("Aucune porte à proximité")