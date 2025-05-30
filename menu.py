import pygame

class InventoryMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        self.is_open = False
        
        # État du menu
        self.showing_loot = False
        self.new_loot = None
        self.selected_slot = 0  # 0=H, 1=J, 2=K, 3=L
    
    def toggle_inventory(self):
        """Ouvre/ferme l'inventaire"""
        self.is_open = not self.is_open
        if not self.is_open:
            self.showing_loot = False
            self.new_loot = None
    
    def show_loot_selection(self, loot):
        """Affiche l'écran de sélection de loot"""
        self.showing_loot = True
        self.new_loot = loot
        self.selected_slot = 0
    
    def draw_inventory(self, screen, equipped_skills):
        """Dessine l'inventaire principal"""
        if not self.is_open:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Panneau d'inventaire
        panel_width = 600
        panel_height = 400
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Titre
        title = self.big_font.render("INVENTAIRE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, panel_y + 40))
        screen.blit(title, title_rect)
        
        # Compétences équipées
        slot_keys = ['H', 'J', 'K', 'L']
        for i, key in enumerate(slot_keys):
            slot_x = panel_x + 50 + i * 130
            slot_y = panel_y + 100
            
            # Slot
            pygame.draw.rect(screen, (60, 60, 60), (slot_x, slot_y, 100, 80))
            pygame.draw.rect(screen, (200, 200, 200), (slot_x, slot_y, 100, 80), 2)
            
            # Touche
            key_text = self.font.render(key, True, (255, 255, 255))
            screen.blit(key_text, (slot_x + 5, slot_y + 5))
            
            # Compétence
            if i < len(equipped_skills) and equipped_skills[i]:
                skill = equipped_skills[i]
                name_text = self.font.render(skill.name[:8], True, (255, 255, 255))
                screen.blit(name_text, (slot_x + 5, slot_y + 30))
        
        # Instructions
        instructions = [
            "I : Fermer l'inventaire",
            "HJKL : Utiliser les compétences"
        ]
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (panel_x + 20, panel_y + 300 + i * 25))
    
    def draw_loot_selection(self, screen, equipped_skills):
        """Dessine l'écran de sélection de loot"""
        if not self.showing_loot or not self.new_loot:
            return
        
        # Fond semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Panneau principal
        panel_width = 700
        panel_height = 500
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, (30, 30, 60), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (255, 215, 0), (panel_x, panel_y, panel_width, panel_height), 4)
        
        # Nouvel objet
        title = self.big_font.render("NOUVEL OBJET TROUVÉ !", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.screen_width // 2, panel_y + 40))
        screen.blit(title, title_rect)
        
        # Info de l'objet
        if hasattr(self.new_loot, 'effect_type'):  # Compétence
            name_text = self.big_font.render(self.new_loot.name, True, (255, 255, 255))
            desc_text = self.font.render(self.new_loot.description, True, (200, 200, 200))
            
            name_rect = name_text.get_rect(center=(self.screen_width // 2, panel_y + 100))
            desc_rect = desc_text.get_rect(center=(self.screen_width // 2, panel_y + 140))
            
            screen.blit(name_text, name_rect)
            screen.blit(desc_text, desc_rect)
            
            # Slots de compétences
            slot_keys = ['H', 'J', 'K', 'L']
            for i, key in enumerate(slot_keys):
                slot_x = panel_x + 80 + i * 130
                slot_y = panel_y + 200
                
                # Couleur selon sélection
                if i == self.selected_slot:
                    color = (255, 215, 0)
                    bg_color = (60, 60, 100)
                else:
                    color = (200, 200, 200)
                    bg_color = (40, 40, 40)
                
                pygame.draw.rect(screen, bg_color, (slot_x, slot_y, 100, 80))
                pygame.draw.rect(screen, color, (slot_x, slot_y, 100, 80), 3)
                
                # Touche
                key_text = self.font.render(key, True, color)
                screen.blit(key_text, (slot_x + 5, slot_y + 5))
                
                # Compétence actuelle
                if i < len(equipped_skills) and equipped_skills[i]:
                    skill = equipped_skills[i]
                    name_text = self.font.render(skill.name[:8], True, (255, 255, 255))
                    screen.blit(name_text, (slot_x + 5, slot_y + 30))
                else:
                    empty_text = self.font.render("Vide", True, (100, 100, 100))
                    screen.blit(empty_text, (slot_x + 5, slot_y + 30))
            
            # Instructions
            instructions = [
                f"ZQSD : Sélectionner slot ({slot_keys[self.selected_slot]} sélectionné)",
                "Entrée : Équiper la compétence",
                "Échap : Ignorer"
            ]
            for i, instruction in enumerate(instructions):
                text = self.font.render(instruction, True, (200, 200, 200))
                screen.blit(text, (panel_x + 20, panel_y + 350 + i * 25))
        
        elif hasattr(self.new_loot, 'weapon_type'):  # ARME - CORRECTION ICI
            name_text = self.big_font.render(self.new_loot.name, True, (255, 255, 255))
            
            # Affichage des bonus selon le type d'arme
            if self.new_loot.weapon_type == "bow":
                weapon_desc = f"Dégâts: +{self.new_loot.damage_bonus} | Portée flèches: +{self.new_loot.range_bonus}"
            elif self.new_loot.weapon_type == "sword":
                weapon_desc = f"Dégâts: +{self.new_loot.damage_bonus} | Portée attaque: +{self.new_loot.range_bonus}"
            else:
                weapon_desc = f"Dégâts: +{self.new_loot.damage_bonus}"
            
            desc_text = self.font.render(weapon_desc, True, (200, 200, 200))
            
            name_rect = name_text.get_rect(center=(self.screen_width // 2, panel_y + 100))
            desc_rect = desc_text.get_rect(center=(self.screen_width // 2, panel_y + 140))
            
            screen.blit(name_text, name_rect)
            screen.blit(desc_text, desc_rect)
            
            instruction = self.font.render("Entrée : Équiper / Échap : Ignorer", True, (200, 200, 200))
            instruction_rect = instruction.get_rect(center=(self.screen_width // 2, panel_y + 400))
            screen.blit(instruction, instruction_rect)
        
        else:  # Potion - traitement différent
            name_text = self.big_font.render(str(self.new_loot), True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(self.screen_width // 2, panel_y + 100))
            screen.blit(name_text, name_rect)
            
            instruction = self.font.render("Entrée : Prendre / Échap : Ignorer", True, (200, 200, 200))
            instruction_rect = instruction.get_rect(center=(self.screen_width // 2, panel_y + 400))
            screen.blit(instruction, instruction_rect)
    
    def handle_loot_input(self, key, equipped_skills):
        """Gère les inputs dans l'écran de loot"""
        if not self.showing_loot:
            return None
        
        if key == pygame.K_ESCAPE:
            self.showing_loot = False
            self.new_loot = None
            return "cancel"
        
        elif key == pygame.K_RETURN:
            result = {"action": "equip", "slot": self.selected_slot, "item": self.new_loot}
            self.showing_loot = False
            self.new_loot = None
            return result
        
        elif key == pygame.K_q:  # Gauche
            self.selected_slot = (self.selected_slot - 1) % 4
        elif key == pygame.K_d:  # Droite
            self.selected_slot = (self.selected_slot + 1) % 4
        
        return None
    
    def draw(self, screen, equipped_skills):
        """Dessine l'interface appropriée"""
        if self.showing_loot:
            self.draw_loot_selection(screen, equipped_skills)
        elif self.is_open:
            self.draw_inventory(screen, equipped_skills)