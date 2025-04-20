import os
import random
import tkinter as tk
from tkinter import messagebox
import winsound
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FOLDER = os.path.join(BASE_DIR, "PickSounds")
IMAGE_FOLDER = os.path.join(BASE_DIR, "Images")
IMAGE_SIZE = (150, 150)

class TeamGenerator:
    def __init__(self, master):
        self.master = master
        master.title("5v5 Team Generator")
        self.sounds_muted = False
        self.last_overflow = []
        master.grid_columnconfigure(0, weight=1, uniform="col")
        master.grid_columnconfigure(1, weight=1, uniform="col")
        master.grid_columnconfigure(2, weight=2, uniform="col")
        master.grid_columnconfigure(3, weight=1, uniform="col")
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)
        self.all_players = ["Alejandro","Master", "Chepo","Chocosexy", "David", "Gianca", "Guachiman", "Katamakiavelico", "Kevin", "lobothunder", "Mauricio", "Motaro", "Shayam", "Silversurfer", "Sticks", "Tenshi", "JeanPaul", "Jktortuga", "Yair"]
        self.selected_players = []
        self.last_team = []
        self.overflow = []
        self.team1_assignments = []
        self.team2_assignments = []
        self.player_images = {}
        for player in self.all_players:
            image_obj = None
            for ext in (".png", ".jpeg", ".jpg"):
                image_path = os.path.join(IMAGE_FOLDER, f"{player}{ext}")
                if os.path.exists(image_path):
                    try:
                        im = Image.open(image_path)
                        try:
                            resample_method = Image.Resampling.LANCZOS
                        except AttributeError:
                            resample_method = Image.ANTIALIAS
                        im = im.resize(IMAGE_SIZE, resample_method)
                        image_obj = ImageTk.PhotoImage(im)
                        break
                    except Exception as e:
                        print(f"Error loading image for {player} from {image_path}: {e}")
            self.player_images[player] = image_obj
        self.available_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.available_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(self.available_frame, text="Available Players", font=("Arial", 12, "bold")).pack(pady=5)
        self.listbox_available = tk.Listbox(self.available_frame, height=15)
        self.listbox_available.pack(fill="both", expand=True, padx=5, pady=5)
        for player in self.all_players:
            self.listbox_available.insert(tk.END, player)
        self.listbox_available.bind("<<ListboxSelect>>", self.add_player)
        self.selected_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.selected_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(self.selected_frame, text="Selected Players (Double-click to remove)", font=("Arial", 12, "bold")).pack(pady=5)
        self.listbox_selected = tk.Listbox(self.selected_frame, height=15)
        self.listbox_selected.pack(fill="both", expand=True, padx=5, pady=5)
        self.listbox_selected.bind("<Double-Button-1>", self.remove_player)
        self.randomize_button = tk.Button(master, text="Randomize Teams", command=self.randomize_teams, font=("Arial", 12, "bold"))
        self.randomize_button.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        self.clear_button = tk.Button(master, text="Clear Selections", command=self.clear_selections, font=("Arial", 12, "bold"))
        self.clear_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        self.teams_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.teams_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")
        tk.Label(self.teams_frame, text="Team 1", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Label(self.teams_frame, text="Team 2", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.teams_frame.grid_columnconfigure(0, weight=1)
        self.teams_frame.grid_columnconfigure(1, weight=1)
        for i in range(6):
            self.teams_frame.grid_rowconfigure(i, weight=1)
        self.team1_slots = []
        self.team2_slots = []
        for i in range(5):
            self._create_team_slot(i+1, "team1", 0)
            self._create_team_slot(i+6, "team2", 1)
        self.extras_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.extras_frame.grid(row=0, column=3, rowspan=3, padx=10, pady=10, sticky="nsew")
        tk.Label(self.extras_frame, text="Overflow Players", font=("Arial", 12, "bold")).pack(pady=5)
        self.reveal_all_button = tk.Button(self.extras_frame, text="Reveal All", command=self.reveal_all_sequence, font=("Arial", 12, "bold"))
        self.reveal_all_button.pack(pady=5, fill="x")
        self.overflow_buttons_frame = tk.Frame(self.extras_frame)
        self.overflow_buttons_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.mute_button = tk.Button(self.extras_frame, text="Mute Sounds", command=self.toggle_mute, font=("Arial", 12, "bold"))
        self.mute_button.pack(pady=5, fill="x")
    def _create_team_slot(self, slot_number, team, column):
        idx = slot_number - 1 if team == "team1" else slot_number - 6
        slot_frame = tk.Frame(self.teams_frame, relief="solid", borderwidth=2, bg="darkblue")
        slot_frame.grid(row=idx+1, column=column, padx=5, pady=5, sticky="nsew")
        img_label = tk.Label(slot_frame, text=str(slot_number), bg="darkblue")
        img_label.pack(side="top", fill="both", expand=True)
        name_label = tk.Label(slot_frame, text=str(slot_number), bg="darkblue", fg="white", font=("Arial", 12, "bold"))
        name_label.pack(side="top", fill="x")
        for widget in (slot_frame, img_label, name_label):
            widget.bind("<Button-1>", self._make_reveal_handler(team, idx))
        slot_data = {"frame": slot_frame, "img_label": img_label, "name_label": name_label, "number": str(slot_number)}
        if team == "team1":
            self.team1_slots.append(slot_data)
        else:
            self.team2_slots.append(slot_data)
    def _make_reveal_handler(self, team, idx):
        def handler(event):
            self.reveal_team_player(team, idx)
        return handler
    def _make_overflow_handler(self, player, slot):
        def handler(event):
            self.reveal_overflow_player(player, slot)
        return handler
    def add_player(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            player = event.widget.get(index)
            if player not in self.selected_players:
                self.selected_players.append(player)
                self.listbox_selected.insert(tk.END, player)
    def remove_player(self, event):
        selection = self.listbox_selected.curselection()
        if selection:
            index = selection[0]
            player = self.listbox_selected.get(index)
            confirm = messagebox.askyesno("Confirm Removal", f"Remove player '{player}' from selections?")
            if confirm:
                self.selected_players.remove(player)
                self.listbox_selected.delete(index)
    def clear_selections(self):
        self.selected_players = []
        self.listbox_selected.delete(0, tk.END)
        self.last_team = []
        self.overflow = []
        self.team1_assignments = []
        self.team2_assignments = []
        self.last_overflow = []
        for slot in self.team1_slots + self.team2_slots:
            slot["img_label"].config(text=slot["number"], image="", bg="darkblue")
            slot["name_label"].config(text=slot["number"], bg="darkblue", fg="white")
            for widget in (slot["frame"], slot["img_label"], slot["name_label"]):
                widget.unbind("<Button-1>")
        self.update_overflow()
    def randomize_teams(self):
        if not self.selected_players:
            messagebox.showwarning("Warning", "No players selected!")
            return
        pool = self.selected_players.copy()
        forced = [p for p in self.last_overflow if p in pool]
        for p in forced:
            if p in pool:
                pool.remove(p)
        remaining_slots = 10 - len(forced)
        if remaining_slots < 0:
            main = random.sample(forced, 10)
        else:
            if remaining_slots > len(pool):
                rnd = pool[:]
            else:
                rnd = random.sample(pool, remaining_slots)
            main = forced + rnd
        if len(self.selected_players) <= 10:
            main = random.sample(self.selected_players, len(self.selected_players))
            overflow = []
        else:
            overflow = [p for p in self.selected_players if p not in main]
            random.shuffle(main)
        if len(main) >= 10:
            self.team1_assignments = main[:5]
            self.team2_assignments = main[5:10]
        else:
            half = len(main) // 2
            self.team1_assignments = main[:half]
            self.team2_assignments = main[half:]
        self.last_overflow = overflow
        for i, slot in enumerate(self.team1_slots):
            slot["img_label"].config(text=slot["number"], image="", bg="darkblue")
            slot["name_label"].config(text=slot["number"], bg="darkblue", fg="white")
            for widget in (slot["frame"], slot["img_label"], slot["name_label"]):
                widget.bind("<Button-1>", self._make_reveal_handler("team1", i))
        for i, slot in enumerate(self.team2_slots):
            slot["img_label"].config(text=slot["number"], image="", bg="darkblue")
            slot["name_label"].config(text=slot["number"], bg="darkblue", fg="white")
            for widget in (slot["frame"], slot["img_label"], slot["name_label"]):
                widget.bind("<Button-1>", self._make_reveal_handler("team2", i))
        self.update_overflow()
    def reveal_team_player(self, team, idx):
        if team == "team1":
            if idx >= len(self.team1_assignments):
                return
            player = self.team1_assignments[idx]
            slot = self.team1_slots[idx]
        else:
            if idx >= len(self.team2_assignments):
                return
            player = self.team2_assignments[idx]
            slot = self.team2_slots[idx]
        if slot["name_label"].cget("text") != slot["number"]:
            return
        player_img = self.player_images.get(player)
        slot["img_label"].config(image=player_img, text="", bg="lightgray")
        slot["name_label"].config(text=player, bg="lightgray", fg="black")
        for widget in (slot["frame"], slot["img_label"], slot["name_label"]):
            widget.unbind("<Button-1>")
        if not self.sounds_muted:
            sound_file = os.path.join(SOUND_FOLDER, f"{player}.wav")
            try:
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Error playing sound for {player}: {e}")
    def check_all_special_sounds(self):
        if any(slot["name_label"].cget("text") == slot["number"] for slot in self.team1_slots) or any(slot["name_label"].cget("text") == slot["number"] for slot in self.team2_slots):
            self.master.after(500, self.check_all_special_sounds)
            return
        t1 = self.get_special_sounds_for_team("team1")
        t2 = self.get_special_sounds_for_team("team2")
        
        self.play_sequential_special_sounds(t1, callback=lambda: self.play_sequential_special_sounds(t2))
    def get_special_sounds_for_team(self, team):
        if team == "team1":
            assignments = self.team1_assignments
        else:
            assignments = self.team2_assignments
        team_set = {name.lower() for name in assignments if isinstance(name, str)}
        sounds = []
        if {"jktortuga", "katamakiavelico", "lobothunder"}.issubset(team_set):
            sounds.append("katathundergringa.wav")
        if {"katamakiavelico", "lobothunder"}.issubset(team_set) and "jktortuga" not in team_set:
            sounds.append("katathunder.wav")
        if {"sticks", "david", "silversurfer"}.issubset(team_set):
            sounds.append("duomediocreynovia.wav")
        if {"sticks", "david"}.issubset(team_set) and "silversurfer" not in team_set:
            sounds.append("duomediocre.wav")
        if {"alejandro", "chocosexy", "chepo"}.issubset(team_set):
            sounds.append("lasprimas.wav")
        if {"gianca", "david", "kevin"}.issubset(team_set):
            sounds.append("teamvalorant.wav")   
        if {"david", "kevin"}.issubset(team_set):
            sounds.append("venezolanoycolombiano.wav")       
        if {"alejandro", "katamakiavelico"}.issubset(team_set):
            sounds.append("comoquedolamoto.wav")       
        return sounds
    def play_sequential_special_sounds(self, sounds, index=0, callback=None):
        if index >= len(sounds):
            if callback:
                callback()
            return
        sound = sounds[index]
        if not self.sounds_muted:
            sound_file = os.path.join(SOUND_FOLDER, sound)
            if os.path.exists(sound_file):
                try:
                    winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception as e:
                    print(f"Error playing special sound {sound}: {e}")
            else:
                print(f"Sound file {sound_file} not found.")
        self.master.after(2000, lambda: self.play_sequential_special_sounds(sounds, index+1, callback))
    def update_overflow(self):
        for widget in self.overflow_buttons_frame.winfo_children():
            widget.destroy()
        columns = 3
        for idx, player in enumerate(self.last_overflow):
            slot_frame = tk.Frame(self.overflow_buttons_frame, relief="solid", borderwidth=2, bg="darkblue")
            slot_frame.grid(row=idx // columns, column=idx % columns, padx=5, pady=5, sticky="nsew")
            slot_number = idx + 1
            img_label = tk.Label(slot_frame, text=str(slot_number), bg="darkblue")
            img_label.pack(side="top", fill="both", expand=True)
            name_label = tk.Label(slot_frame, text=str(slot_number), bg="darkblue", fg="white", font=("Arial", 12, "bold"))
            name_label.pack(side="top", fill="x")
            for widget in (slot_frame, img_label, name_label):
                widget.bind("<Button-1>", self._make_overflow_handler(player, slot_frame))
        for col in range(columns):
            self.overflow_buttons_frame.grid_columnconfigure(col, weight=1)
        num_rows = (len(self.last_overflow) + columns - 1) // columns
        for row in range(num_rows):
            self.overflow_buttons_frame.grid_rowconfigure(row, weight=1)
    def reveal_overflow_player(self, player, slot_frame):
        player_img = self.player_images.get(player)
        children = slot_frame.winfo_children()
        if len(children) >= 2:
            img_label = children[0]
            name_label = children[1]
            img_label.config(image=player_img, text="", bg="lightgray")
            name_label.config(text=player, bg="lightgray", fg="black")
        else:
            for widget in slot_frame.winfo_children():
                widget.config(text=player)
        for widget in slot_frame.winfo_children():
            widget.unbind("<Button-1>")
        slot_frame.unbind("<Button-1>")
        if not self.sounds_muted:
            sound_file = os.path.join(SOUND_FOLDER, f"{player}.wav")
            try:
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Error playing sound for {player}: {e}")
    def toggle_mute(self):
        self.sounds_muted = not self.sounds_muted
        if self.sounds_muted:
            self.mute_button.config(text="Unmute Sounds")
        else:
            self.mute_button.config(text="Mute Sounds")
    def reveal_all_sequence(self):
        all_slots = []
        overflow_children = self.overflow_buttons_frame.winfo_children()
        for idx, player in enumerate(self.last_overflow):
            if idx < len(overflow_children):
                all_slots.append(("overflow", player, overflow_children[idx]))
        for idx, slot in enumerate(self.team1_slots):
            all_slots.append(("team1", idx, slot))
        for idx, slot in enumerate(self.team2_slots):
            all_slots.append(("team2", idx, slot))
        self.reveal_next_slot(0, all_slots)
    def reveal_next_slot(self, index, all_slots):
        if index >= len(all_slots):
            self.master.after(500, self.check_all_special_sounds)
            return
        slot_type, ref, slot_info = all_slots[index]
        if slot_type == "overflow":
            self.reveal_overflow_player(ref, slot_info)
        else:
            self.reveal_team_player(slot_type, ref)
        self.master.after(1800, lambda: self.reveal_next_slot(index+1, all_slots))

if __name__ == "__main__":
    root = tk.Tk()
    app = TeamGenerator(root)
    root.mainloop()