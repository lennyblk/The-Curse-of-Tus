# world.py - Couloir right→boss corrigé pour hitbox plus précise
import pygame
import random

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_size = 32
        self.map = [[0 for _ in range(width)] for _ in range(height)]
        
        # Système de salles avec coordonnées CORRIGÉES pour connectivité
        self.rooms = {
            "spawn": {"x": 5, "y": 5, "w": 15, "h": 12, "unlocked": True},
            "room1": {"x": 22, "y": 8, "w": 20, "h": 18, "unlocked": False},
            "room2": {"x": 45, "y": 5, "w": 18, "h": 15, "unlocked": False},
            "central": {"x": 15, "y": 30, "w": 25, "h": 20, "unlocked": False},
            "right": {"x": 42, "y": 25, "w": 20, "h": 15, "unlocked": False},
            "big": {"x": 65, "y": 20, "w": 25, "h": 25, "unlocked": False},
            "bottom": {"x": 10, "y": 55, "w": 20, "h": 15, "unlocked": False},
            "boss": {"x": 40, "y": 50, "w": 30, "h": 20, "unlocked": False},
            "secret": {"x": 72, "y": 50, "w": 20, "h": 20, "unlocked": False}
        }
        
        # Portes CORRIGÉES avec couloir right→boss plus précis
        self.doors = [
            {"from": "spawn", "to": "room1", "corridor": (20, 11, 2, 3)},
            {"from": "room1", "to": "room2", "corridor": (42, 14, 3, 2)},
            {"from": "room1", "to": "central", "corridor": (32, 26, 2, 4)},
            {"from": "central", "to": "right", "corridor": (40, 37, 2, 3)},
            {"from": "right", "to": "big", "corridor": (62, 32, 3, 2)},
            {"from": "central", "to": "bottom", "corridor": (27, 50, 2, 5)},
            {"from": "right", "to": "boss", "corridor": (52, 40, 2, 10)},  # CORRIGÉ: couloir plus court, porte plus proche
            {"from": "boss", "to": "secret", "corridor": (70, 60, 2, 2)}
        ]
        
        self.generate_world()
    
    def generate_world(self):
        # Créer le terrain plein de murs
        for x in range(self.width):
            for y in range(self.height):
                self.map[y][x] = 1
        
        # Créer toutes les salles
        for room_name, room_data in self.rooms.items():
            self.create_open_room(room_data["x"], room_data["y"], 
                                room_data["w"], room_data["h"])
        
        # TOUJOURS créer le couloir spawn → room1 (ouvert dès le début)
        self.create_corridor(20, 11, 2, 3)
        
        # Créer les autres couloirs selon les salles déverrouillées
        self.update_doors()
        self.add_obstacles()
    
    def create_open_room(self, start_x, start_y, width, height):
        for x in range(start_x, start_x + width):
            for y in range(start_y, start_y + height):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.map[y][x] = 0
    
    def create_corridor(self, start_x, start_y, width, height):
        for x in range(start_x, start_x + width):
            for y in range(start_y, start_y + height):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.map[y][x] = 0
    
    def update_doors(self):
        """Ouvre ou ferme les portes selon les salles déverrouillées"""
        for door in self.doors:
            # Skip le couloir spawn → room1 (géré dans generate_world)
            if door["from"] == "spawn" and door["to"] == "room1":
                continue
            
            from_room = self.rooms[door["from"]]
            to_room = self.rooms[door["to"]]
            corridor = door["corridor"]
            
            # Ouvrir le couloir si AU MOINS UNE des salles est déverrouillée
            if from_room["unlocked"] or to_room["unlocked"]:
                self.create_corridor(corridor[0], corridor[1], corridor[2], corridor[3])
            else:
                # Fermer le couloir (remettre des murs)
                for x in range(corridor[0], corridor[0] + corridor[2]):
                    for y in range(corridor[1], corridor[1] + corridor[3]):
                        if 0 <= x < self.width and 0 <= y < self.height:
                            self.map[y][x] = 1
    
    def unlock_room(self, room_name):
        """Déverrouille une salle et met à jour les portes"""
        if room_name in self.rooms:
            print(f"Salle {room_name} déverrouillée !")
            self.rooms[room_name]["unlocked"] = True
            self.update_doors()
    
    def get_player_room(self, player_x, player_y):
        """Retourne le nom de la salle où se trouve le joueur"""
        player_tile_x = int(player_x // self.tile_size)
        player_tile_y = int(player_y // self.tile_size)
        
        for room_name, room_data in self.rooms.items():
            if (room_data["x"] <= player_tile_x < room_data["x"] + room_data["w"] and
                room_data["y"] <= player_tile_y < room_data["y"] + room_data["h"]):
                return room_name
        return None
    
    def is_door_locked(self, player_x, player_y):
        """NOUVEAU: Vérifie si le joueur est dans un couloir de porte fermée"""
        player_tile_x = int(player_x // self.tile_size)
        player_tile_y = int(player_y // self.tile_size)
        
        for door in self.doors:
            corridor = door["corridor"]
            
            # Vérifier si le joueur est dans ce couloir
            if (corridor[0] <= player_tile_x < corridor[0] + corridor[2] and
                corridor[1] <= player_tile_y < corridor[1] + corridor[3]):
                
                from_room = self.rooms[door["from"]]
                to_room = self.rooms[door["to"]]
                
                # Si AUCUNE des deux salles n'est déverrouillée, bloquer
                if not from_room["unlocked"] and not to_room["unlocked"]:
                    return True
        
        return False
    
    def add_obstacles(self):
        # Piliers dans la grande salle (ajustés pour nouvelle position)
        obstacles = [(72, 25), (80, 25), (72, 35), (80, 35)]
        for x, y in obstacles:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.map[y][x] = 1
    
    def draw_world(self, screen, camera):
        start_x = max(0, int(camera.x // self.tile_size))
        end_x = min(self.width, int((camera.x + screen.get_width()) // self.tile_size + 1))
        start_y = max(0, int(camera.y // self.tile_size))
        end_y = min(self.height, int((camera.y + screen.get_height()) // self.tile_size + 1))
        
        # Dessiner les murs
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                if self.map[y][x] == 1:
                    screen_x = x * self.tile_size - camera.x
                    screen_y = y * self.tile_size - camera.y
                    pygame.draw.rect(screen, (100, 100, 100), 
                                (screen_x, screen_y, self.tile_size, self.tile_size))
        
        # Dessiner les portes
        self.draw_doors(screen, camera)
        
        # Dessiner le voile noir sur les salles verrouillées
        self.draw_locked_overlay(screen, camera)

    def draw_doors(self, screen, camera):
        """Dessine les portes avec couleurs plus claires pour la logique stricte"""
        for door in self.doors:
            corridor = door["corridor"]
            from_room = self.rooms[door["from"]]
            to_room = self.rooms[door["to"]]
            
            # EXCEPTION: Position spéciale pour la porte right→boss
            if door["from"] == "right" and door["to"] == "boss":
                # Placer la porte au DÉBUT du couloir (côté salle right)
                door_x = corridor[0] * self.tile_size + 16  # Centre en X
                door_y = corridor[1] * self.tile_size + 16  # Début en Y + petit offset
            else:
                # Position normale au centre du couloir pour les autres portes
                door_x = (corridor[0] + corridor[2]//2) * self.tile_size
                door_y = (corridor[1] + corridor[3]//2) * self.tile_size
            
            # NOUVELLE LOGIQUE DE COULEURS plus claire :
            if from_room["unlocked"] and to_room["unlocked"]:
                # Les deux salles sont ouvertes -> Vert (passage libre)
                door_color = (0, 255, 0)
                border_color = (255, 255, 255)
                status = "OUVERTE"
            elif from_room["unlocked"] and not to_room["unlocked"]:
                # Salle de départ ouverte, destination fermée -> Jaune (peut être ouverte avec F)
                door_color = (255, 255, 0)
                border_color = (0, 0, 0)
                status = "PEUT OUVRIR"
            elif not from_room["unlocked"] and to_room["unlocked"]:
                # Salle de départ fermée, destination ouverte -> Orange (accès depuis l'autre côté)
                door_color = (255, 165, 0)
                border_color = (0, 0, 0)
                status = "ACCÈS INVERSE"
            else:
                # Les deux salles fermées -> Rouge (bloquée)
                door_color = (255, 0, 0)
                border_color = (100, 100, 100)
                status = "FERMÉE"
            
            screen_x = door_x - camera.x
            screen_y = door_y - camera.y
            
            # Dessiner la porte avec un style plus visible
            door_size = 40
            
            # Fond de la porte
            pygame.draw.rect(screen, door_color, 
                            (screen_x - door_size//2, screen_y - door_size//2, door_size, door_size))
            
            # Bordure épaisse
            pygame.draw.rect(screen, border_color, 
                            (screen_x - door_size//2, screen_y - door_size//2, door_size, door_size), 4)
            
            # Trait noir vertical au centre (style porte) - seulement si accessible
            if status in ["OUVERTE", "PEUT OUVRIR", "ACCÈS INVERSE"]:
                pygame.draw.line(screen, (0, 0, 0), 
                            (screen_x, screen_y - door_size//2 + 4), 
                            (screen_x, screen_y + door_size//2 - 4), 3)
            
            # Poignée de porte
            pygame.draw.circle(screen, border_color, 
                            (int(screen_x + 8), int(screen_y)), 3)
            
            # Debug: afficher le statut (optionnel - à retirer en prod)
            if abs(screen_x) < 1200 and abs(screen_y) < 800:  # Seulement si visible
                font = pygame.font.Font(None, 16)
                status_text = font.render(f"{door['from']}→{door['to']}", True, (255, 255, 255))
                screen.blit(status_text, (screen_x - 30, screen_y + 25))
    
    def draw_locked_overlay(self, screen, camera):
        """Dessine un voile noir sur les salles non déverrouillées"""
        for room_name, room_data in self.rooms.items():
            if not room_data["unlocked"]:
                # Coordonnées de la salle en pixels
                room_pixel_x = room_data["x"] * self.tile_size
                room_pixel_y = room_data["y"] * self.tile_size
                room_pixel_w = room_data["w"] * self.tile_size
                room_pixel_h = room_data["h"] * self.tile_size
                
                # Position relative à la caméra
                screen_x = room_pixel_x - camera.x
                screen_y = room_pixel_y - camera.y
                
                # Dessiner le voile noir semi-transparent
                overlay_surface = pygame.Surface((room_pixel_w, room_pixel_h))
                overlay_surface.fill((0, 0, 0))
                overlay_surface.set_alpha(180)
                screen.blit(overlay_surface, (screen_x, screen_y))