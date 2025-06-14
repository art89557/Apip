import tkinter as tk
from tkinter import messagebox
import random

# === Character Classes ===
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
        return f"{self.name} received {dmg_taken} damage! (HP: {self.hp})"

    def basic_attack(self, target):
        msg = f"{self.name} uses Basic Attack on {target.name}\n"
        msg += target.take_damage(self.atk)
        self.charge_energy(30)
        return msg

    def can_use_special(self):
        return self.energy >= 100

    def charge_energy(self, amount):
        self.energy = min(100, self.energy + amount)

class DPS(Character):
    def __init__(self, name):
        super().__init__(name, "DPS", 25, 80, 5)

class Tank(Character):
    def __init__(self, name):
        super().__init__(name, "Tank", 10, 130, 20)

class Healer(Character):
    def __init__(self, name):
        super().__init__(name, "Healer", 5, 100, 10)

    def heal(self, target):
        if not target.alive:
            return f"{target.name} is down! Cannot be healed."
        amount = 30
        target.hp = min(target.max_hp, target.hp + amount)
        return f"{self.name} heals {target.name} for {amount} HP."

# === Item Class ===
class Item:
    def __init__(self, name, bonus_atk=0, bonus_def=0):
        self.name = name
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def

# === Boss Class ===
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
        return f"Boss {self.name} took {dmg} damage! (HP: {self.hp})"

    def attack(self, target):
        return f"Boss attacks {target.name}\n" + target.take_damage(self.atk)

# === Game GUI ===
class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Boss Battle")
        self.root.configure(bg="#1e1e2f")

        self.all_characters = [
            DPS("Aether"), Tank("Brunt"), Healer("Mira"), DPS("Kael"),
            Tank("Wallie"), Healer("Nova")
        ]
        self.items = [Item("Sword", 5, 0), Item("Shield", 0, 5)]
        self.skill_points = 3
        self.max_skill_points = 5

        self.characters = []
        self.boss = None

        self.text = tk.Text(root, height=20, width=60, bg="#2d2d44", fg="white")
        self.text.pack(pady=10)

        self.text_scrollbar = tk.Scrollbar(root, command=self.text.yview)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=self.text_scrollbar.set)

        self.status = tk.Label(root, text="Choose a boss to start the game.", fg="white", bg="#1e1e2f")
        self.status.pack()

        self.frame_buttons = tk.Frame(root, bg="#1e1e2f")
        self.frame_buttons.pack(pady=10)

        self.reset_button = tk.Button(root, text="Restart Game", command=self.restart_game, bg="#444", fg="white")
        self.reset_button.pack(pady=5)

        self.stage_selection()

    def restart_game(self):
        self.characters.clear()
        self.boss = None
        self.skill_points = 3
        self.text.delete("1.0", tk.END)
        self.status.config(text="Choose a boss to start the game.")
        for widget in self.frame_buttons.winfo_children():
            widget.destroy()
        self.stage_selection()

    def stage_selection(self):
        self.text.insert(tk.END, "=== Choose Boss ===\n")
        bosses = [
            ("Infernal Dragon", 250, 18),
            ("Frozen Titan", 300, 15),
            ("Shadow Reaper", 200, 22)
        ]
        for name, hp, atk in bosses:
            btn = tk.Button(self.frame_buttons, text=name,
                            command=lambda n=name, h=hp, a=atk: self.select_boss(n, h, a),
                            bg="#3c3c5e", fg="white")
            btn.pack(fill="x", pady=2)

    def select_boss(self, name, hp, atk):
        self.boss = Boss(name, hp, atk)
        for widget in self.frame_buttons.winfo_children():
            widget.destroy()
        self.select_characters()

    def select_characters(self):
        self.text.insert(tk.END, "\n=== Choose 4 Characters ===\n")
        for i, c in enumerate(self.all_characters):
            btn = tk.Button(self.frame_buttons, text=f"{c.name} ({c.role})",
                            command=lambda i=i: self.add_character(i),
                            bg="#4a4a6a", fg="white")
            btn.pack(fill="x", pady=2)

    def add_character(self, index):
        char = self.all_characters[index]
        if char in self.characters:
            return
        self.characters.append(char)
        char.equip_item(self.items[len(self.characters) % len(self.items)])
        self.text.insert(tk.END, f"Added {char.name} to team.\n")
        self.text.see(tk.END)
        if len(self.characters) == 4:
            for widget in self.frame_buttons.winfo_children():
                widget.destroy()
            self.start_battle()

    def start_battle(self):
        self.text.insert(tk.END, "\n--- BATTLE START ---\n")
        self.text.see(tk.END)
        self.show_action_buttons()

    def show_action_buttons(self):
        for i, char in enumerate(self.characters):
            btn = tk.Button(self.frame_buttons, text=f"{char.name} Attack",
                            command=lambda i=i: self.player_action(i),
                            bg="#5c5c7a", fg="white")
            btn.pack(fill="x", pady=2)

    def player_action(self, index):
        char = self.characters[index]
        if not char.alive:
            self.text.insert(tk.END, f"{char.name} is down!\n")
            self.text.see(tk.END)
            return
        log = char.basic_attack(self.boss)
        self.skill_points = min(self.max_skill_points, self.skill_points + 1)
        self.status.config(text=f"Skill Points: {self.skill_points}")
        self.text.insert(tk.END, log + "\n")
        self.text.see(tk.END)

        if not self.boss.alive:
            self.text.insert(tk.END, "\nYou defeated the boss!\n")
            self.text.see(tk.END)
            self.end_game("Victory")
            return

        self.root.after(1000, self.boss_turn)

    def boss_turn(self):
        living = [c for c in self.characters if c.alive]
        if not living:
            self.end_game("Game Over")
            return
        target = random.choice(living)
        log = self.boss.attack(target)
        self.text.insert(tk.END, "\n" + log + "\n")
        self.text.see(tk.END)

        if all(not c.alive for c in self.characters):
            self.end_game("All characters are down. Game Over!")

    def end_game(self, message):
        for widget in self.frame_buttons.winfo_children():
            widget.config(state="disabled")
        self.status.config(text=message)
        messagebox.showinfo("Game End", message)

if __name__ == "__main__":
    root = tk.Tk()
    game = GameGUI(root)
    root.mainloop()