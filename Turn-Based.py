import random

# === Superclass & Subclass Karakter ===

class Character:
    def __init__(self, name, role, atk, hp, defense):
        self.name = name
        self.role = role
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.energy = 0
        self.item = None
        self.alive = True

    def equip_item(self, item):
        self.item = item
        self.atk += item.bonus_atk
        self.defense += item.bonus_def

    def take_damage(self, dmg):
        dmg_taken = max(dmg - self.defense, 0)
        self.hp -= dmg_taken
        if self.hp <= 0:
            self.alive = False
            self.hp = 0
        print(f"{self.name} received {dmg_taken} damage! (HP: {self.hp})")

    def basic_attack(self, target):
        print(f"{self.name} uses Basic Attack on {target.name}")
        target.take_damage(self.atk)
        return 1  # gain 1 skill point

    def can_use_special(self):
        return self.energy >= 100

    def charge_energy(self, amount):
        self.energy = min(100, self.energy + amount)

    def __str__(self):
        return f"{self.name} ({self.role}) | HP: {self.hp} | Energy: {self.energy}"

# Role Spesifik Subclass
class DPS(Character):
    def __init__(self, name):
        super().__init__(name, "DPS", atk=25, hp=80, defense=5)

class SubDPS(Character):
    def __init__(self, name):
        super().__init__(name, "Sub DPS", atk=20, hp=90, defense=8)

class Tank(Character):
    def __init__(self, name):
        super().__init__(name, "Tank", atk=10, hp=130, defense=20)

class Support(Character):
    def __init__(self, name):
        super().__init__(name, "Support", atk=8, hp=100, defense=10)

class Healer(Character):
    def __init__(self, name):
        super().__init__(name, "Healer", atk=5, hp=100, defense=10)

    def heal(self, target):
        if not target.alive:
            print(f"{target.name} cannot be healed. They are down!")
            return
        heal_amount = 30
        target.hp = min(target.max_hp, target.hp + heal_amount)
        print(f"{self.name} heals {target.name} for {heal_amount} HP.")

class Debuffer(Character):
    def __init__(self, name):
        super().__init__(name, "Debuffer", atk=7, hp=90, defense=10)

    def weaken(self, target):
        target.atk = max(1, target.atk - 5)
        print(f"{self.name} weakens {target.name}'s ATK!")

# Item
class Item:
    def __init__(self, name, bonus_atk=0, bonus_def=0):
        self.name = name
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def

# Boss
class Boss:
    def __init__(self, name, hp, atk):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.alive = True

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            self.hp = 0
        print(f"Boss {self.name} took {dmg} damage! (HP: {self.hp})")

    def attack(self, target):
        print(f"Boss attacks {target.name}")
        target.take_damage(self.atk)

# Game Manager
class GameManager:
    def __init__(self):
        self.characters = []
        self.skill_points = 3
        self.max_skill_points = 5
        self.boss = None
        self.items = [
            Item("Sword", bonus_atk=5),
            Item("Shield", bonus_def=5),
            Item("Lance", bonus_atk=3, bonus_def=2)
        ]
        self.all_characters = [
            DPS("Aether"), SubDPS("Kael"), Tank("Brunt"),
            Support("Sera"), Healer("Mira"), Debuffer("Hexa"),
            DPS("Zion"), Tank("Wallie"), SubDPS("Nix"), Healer("Nova")
        ]

    def choose_stage(self):
        print("=== Choose Stage ===")
        stages = {
            1: Boss("Infernal Dragon", 250, 18),
            2: Boss("Frozen Titan", 300, 15),
            3: Boss("Shadow Reaper", 200, 22),
        }
        for key in stages:
            print(f"{key}. {stages[key].name}")
        choice = int(input("Enter stage (1-3): "))
        self.boss = stages[choice]

    def choose_characters(self):
        print("=== Choose Your Team (4 Characters) ===")
        for i, c in enumerate(self.all_characters):
            print(f"{i + 1}. {c.name} ({c.role})")

        while len(self.characters) < 4:
            idx = int(input("Pick character number: ")) - 1
            char = self.all_characters[idx]
            self.characters.append(char)

            print("Choose item to equip:")
            for j, item in enumerate(self.items):
                print(f"{j + 1}. {item.name}")
            item_idx = int(input("Pick item: ")) - 1
            char.equip_item(self.items[item_idx])

    def play_turn(self):
        for char in self.characters:
            if not char.alive:
                continue
            print(f"\n{char}")
            print(f"Skill Points: {self.skill_points}")
            print("1. Basic Attack (gain 1 SP)")
            print("2. Skill (cost 1 SP)")
            print("3. Special (needs 100 energy)")
            choice = input("Choose action: ")

            if choice == '1':
                self.skill_points = min(self.max_skill_points, self.skill_points + char.basic_attack(self.boss))
                char.charge_energy(30)
            elif choice == '2' and self.skill_points > 0:
                if isinstance(char, Healer):
                    target = self.select_ally()
                    char.heal(target)
                elif isinstance(char, Debuffer):
                    char.weaken(self.boss)
                else:
                    print(f"{char.name} uses Skill!")
                    self.boss.take_damage(char.atk + 10)
                self.skill_points -= 1
                char.charge_energy(15)
            elif choice == '3' and char.can_use_special():
                print(f"{char.name} uses SPECIAL!!")
                self.boss.take_damage(char.atk * 2)
                char.energy = 0
            else:
                print("Invalid or not enough points.")

    def select_ally(self):
        print("Select ally:")
        for i, char in enumerate(self.characters):
            print(f"{i + 1}. {char.name} (HP: {char.hp})")
        idx = int(input("Choose: ")) - 1
        return self.characters[idx]

    def enemy_turn(self):
        print("\n=== Boss Turn ===")
        living = [c for c in self.characters if c.alive]
        target = random.choice(living)
        self.boss.attack(target)

    def check_win(self):
        if not self.boss.alive:
            print("You defeated the boss!")
            return True
        if all(not c.alive for c in self.characters):
            print("All characters are down. Game Over!")
            return True
        return False

    def start(self):
        self.choose_stage()
        self.choose_characters()
        print("\n--- BATTLE START ---\n")
        while True:
            self.play_turn()
            if self.check_win():
                break
            self.enemy_turn()
            if self.check_win():
                break

if __name__ == "__main__":
    game = GameManager()
    game.start()
