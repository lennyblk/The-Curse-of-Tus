# loot.py - Suppression des potions de stamina
import pygame
import random
import time

class Skill:
    def __init__(self, name, description, effect_type, effect_value, key_binding=None):
        self.name = name
        self.description = description
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.key_binding = key_binding  # H, J, K, L
        self.equipped = False

class Weapon:
    def __init__(self, name, weapon_type, damage_bonus=0, range_bonus=0):
        self.name = name
        self.weapon_type = weapon_type
        self.damage_bonus = damage_bonus
        self.range_bonus = range_bonus

class Chest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.opened = False
        self.contents = None
        # Ne pas générer le loot à la création, mais à l'ouverture
        self.loot_generated = False
    
    def generate_loot(self):
        """Génère un loot aléatoire - Version corrigée pour vraie aléatoire"""
        if self.loot_generated:
            return  # Déjà généré
        
        # Utiliser une combinaison unique pour chaque coffre
        unique_seed = hash((self.x, self.y, time.time()))
        random.seed(unique_seed & 0x7FFFFFFF)  # Garder positif
        
        print(f"Génération loot pour coffre en ({self.x}, {self.y}) avec seed {unique_seed}")
        
        # Choix du type de loot
        loot_type = random.choice(["skill", "weapon", "potion"])
        print(f"Type choisi: {loot_type}")
        
        if loot_type == "skill":
            skills = [
                Skill("Vitesse", "+20% vitesse de déplacement", "speed", 0.2),
                Skill("Dash", "Permet de dasher (touche sélectionnée)", "dash", True),
                Skill("Esquive", "15% chance d'éviter dégâts", "dodge", 0.15),
                Skill("Berserker", "+50% dégâts si HP < 50%", "berserker", 0.5),
                Skill("Endurance", "+50 stamina max", "stamina", 50),
                Skill("Critique", "25% chance dégâts x2", "crit", 0.25),
                Skill("Vampirisme", "+10 HP par ennemi tué", "vampire", 10)
            ]
            self.contents = random.choice(skills)
            print(f"Compétence choisie: {self.contents.name}")
        
        elif loot_type == "weapon":
            weapons = [
                Weapon("Arc Elfique", "bow", damage_bonus=10, range_bonus=100),
                Weapon("Épée Runique", "sword", damage_bonus=15, range_bonus=30),
                Weapon("Arc de Précision", "bow", damage_bonus=5, range_bonus=150),
                Weapon("Lame Maudite", "sword", damage_bonus=20, range_bonus=30)
            ]
            self.contents = random.choice(weapons)
            print(f"Arme choisie: {self.contents.name} ({self.contents.weapon_type})")
        
        else:  # potion
            potions = ["Potion de Vie", "Potion Complète"]
            self.contents = random.choice(potions)
            print(f"Potion choisie: {self.contents}")
        
        self.loot_generated = True
        # Remettre le random à un état normal
        random.seed()
    
    def open(self, player):
        if self.opened:
            return None
        
        # Générer le loot au moment de l'ouverture pour plus d'aléatoire
        if not self.loot_generated:
            self.generate_loot()
        
        self.opened = True
        return self.contents
    
    def draw(self, screen, camera_x, camera_y):
        if not self.opened:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            # Coffre fermé
            pygame.draw.rect(screen, (139, 69, 19), (screen_x, screen_y, self.width, self.height))
            pygame.draw.rect(screen, (101, 67, 33), (screen_x, screen_y, self.width, self.height), 3)
            
            # Serrure dorée
            pygame.draw.circle(screen, (255, 215, 0), (int(screen_x + 16), int(screen_y + 20)), 4)
        else:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            # Coffre ouvert
            pygame.draw.rect(screen, (160, 82, 45), (screen_x, screen_y, self.width, self.height))
            pygame.draw.rect(screen, (101, 67, 33), (screen_x, screen_y, self.width, self.height), 2)