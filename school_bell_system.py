"""
SCHOOL BELL SYSTEM - MENU DRIVEN (NO GUI YET)

- Option 1: Bell mode  (uses ringBell scheduler)
- Option 2: Assembly mode (manual play based on today's day)
- Option 3: Announcement (placeholder for later)
- Option 4: Settings (change audio file paths)
- Option 5: About us
- Option 0: Exit

IMPORTANT:
- When CURRENT_MODE == "ASSEMBLY", ringBell() will NOT ring (even if running).
"""

import time
from datetime import datetime, date
import pygame

# --------------- GLOBAL MODE / FLAGS ---------------

CURRENT_MODE = "IDLE"   # IDLE / BELL / ASSEMBLY / ANNOUNCEMENT

def set_mode(mode: str):
    global CURRENT_MODE
    CURRENT_MODE = mode
    print(f"\n[MODE] Switched to: {CURRENT_MODE}\n")


# --------------- AUDIO HELPERS ---------------

_audio_inited = False

def init_audio():
    global _audio_inited
    if not _audio_inited:
        pygame.mixer.init()
        _audio_inited = True

def play_audio_blocking(path: str):
    """Play an audio file fully, blocking until finished."""
    init_audio()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)


# --------------- BELL SCHEDULER (OPTION 1) ---------------

def ringBell(schedule_list, audio_file='bell.mp3',
             check_interval=20, volume=0.8):
    """
    Simple bell scheduler:
    - schedule_list: ['08:30', '09:15', '10:00', ...] in 24h HH:MM format
    - audio_file: bell sound
    - check_interval: seconds between checks
    - volume: 0.0 .. 1.0
    NOTE:
    - Will NOT ring when CURRENT_MODE != "BELL"
      (so if you go to Assembly, no bells).
    - Press Ctrl+C to stop this loop and return to Bell Menu.
    """
    init_audio()
    pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    # parse schedule into (hour, minute)
    schedule = set()
    for t in schedule_list:
        try:
            h, m = map(int, t.split(":"))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
            schedule.add((h, m))
        except Exception:
            print(f"Warning: invalid time format '{t}', expected HH:MM")
    if not schedule:
        print("No valid times in schedule_list. Returning.")
        return

    print("Bell schedule (24h):", sorted(schedule))
    print("Bell scheduler started. Ctrl+C to stop and go back.\n")

    rung_today = set()
    today_date = date.today()

    try:
        while True:
            now = datetime.now()

            # reset at midnight
            if date.today() != today_date:
                today_date = date.today()
                rung_today.clear()

            # if not in BELL mode, don't ring, just wait
            if CURRENT_MODE != "BELL":
                time.sleep(check_interval)
                continue

            hm = (now.hour, now.minute)
            if hm in schedule and hm not in rung_today:
                print(f"[{now.strftime('%H:%M')}] Bell time.")
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                rung_today.add(hm)

            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nBell scheduler stopped (KeyboardInterrupt). Returning to Bell menu.\n")


# --------------- ASSEMBLY CONFIG (OPTION 2) ---------------

# Common files (you can change later in Settings)
NATIONAL_ANTHEM_FILE = "national_anthem.mp3"
ASSEMBLY_BELL_FILE = "bell.mp3"
EXTRA1_FILE = None      # you can set from Settings or leave None
EXTRA2_FILE = None

# Day config: Monday=0 ... Sunday=6
DAY_CONFIG = {
    0: {  # Monday
        "label": "English Day",
        "prayer": "english_prayer.mp3",
        "birthday": "english_birthday.mp3",
    },
    1: {  # Tuesday
        "label": "English Day",
        "prayer": "english_prayer.mp3",
        "birthday": "english_birthday.mp3",
    },
    2: {  # Wednesday
        "label": "Hindi Day",
        "prayer": "hindi_prayer.mp3",
        "birthday": "hindi_birthday.mp3",
    },
    3: {  # Thursday
        "label": "English Day",
        "prayer": "english_prayer.mp3",
        "birthday": "english_birthday.mp3",
    },
    4: {  # Friday
        "label": "Malayalam Day",
        "prayer": "malayalam_prayer.mp3",
        "birthday": "malayalam_birthday.mp3",
    },
    # 5,6 (Sat, Sun) left empty for now
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_today_assembly_config():
    """Return (day_index, day_name, config_dict) for today's assembly."""
    idx = datetime.now().weekday()  # 0-6
    day_name = DAY_NAMES[idx]
    if idx not in DAY_CONFIG:
        raise ValueError(f"No assembly config for {day_name} (index {idx}).")
    return idx, day_name, DAY_CONFIG[idx]


def ring_assembly_bell(duration=5):
    """Bell button inside Assembly screen (fixed 5 sec by default)."""
    init_audio()
    pygame.mixer.music.load(ASSEMBLY_BELL_FILE)
    pygame.mixer.music.play()
    time.sleep(duration)
    pygame.mixer.music.stop()


def assembly_menu():
    """Menu for Assembly mode (manual play)."""
    set_mode("ASSEMBLY")

    while True:
        try:
            idx, day_name, cfg = get_today_assembly_config()
        except ValueError as e:
            print(e)
            print("Press Enter to go back to main menu.")
            input()
            return

        print("========== ASSEMBLY MODE ==========")
        print(f"Today: {day_name} - {cfg.get('label','')}")
        print("Prayer file      :", cfg.get("prayer"))
        print("Birthday file    :", cfg.get("birthday"))
        print("National Anthem  :", NATIONAL_ANTHEM_FILE)
        print("Extra 1          :", EXTRA1_FILE or "(not set)")
        print("Extra 2          :", EXTRA2_FILE or "(not set)")
        print("-----------------------------------")
        print("1. Play Prayer")
        print("2. Play Happy Birthday")
        print("3. Play National Anthem")
        print("4. Play Extra Audio 1")
        print("5. Play Extra Audio 2")
        print("6. Ring Bell (5 sec)")
        print("0. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            print("\n[Assembly] Playing Prayer...\n")
            play_audio_blocking(cfg["prayer"])
        elif choice == "2":
            print("\n[Assembly] Playing Birthday song...\n")
            play_audio_blocking(cfg["birthday"])
        elif choice == "3":
            print("\n[Assembly] Playing National Anthem...\n")
            play_audio_blocking(NATIONAL_ANTHEM_FILE)
        elif choice == "4":
            if EXTRA1_FILE:
                print("\n[Assembly] Playing Extra Audio 1...\n")
                play_audio_blocking(EXTRA1_FILE)
            else:
                print("Extra Audio 1 not set.")
        elif choice == "5":
            if EXTRA2_FILE:
                print("\n[Assembly] Playing Extra Audio 2...\n")
                play_audio_blocking(EXTRA2_FILE)
            else:
                print("Extra Audio 2 not set.")
        elif choice == "6":
            print("\n[Assembly] Ringing bell for 5 seconds...\n")
            ring_assembly_bell(5)
        elif choice == "0":
            set_mode("IDLE")
            return
        else:
            print("Invalid choice, try again.\n")


# --------------- ANNOUNCEMENT PLACEHOLDER (OPTION 3) ---------------

def announcement_menu():
    """
    Placeholder for your future announcement system.
    You can later add:
    - choose announcement file
    - record announcement
    - play through speakers, etc.
    """
    set_mode("ANNOUNCEMENT")
    print("=== ANNOUNCEMENT MODE (placeholder) ===")
    print("Here you will add options for announcements later.")
    input("Press Enter to go back to main menu...")
    set_mode("IDLE")


# --------------- SETTINGS MENU (OPTION 4) ---------------

def settings_menu():
    """Allow changing file paths from menu (basic text version)."""
    global NATIONAL_ANTHEM_FILE, ASSEMBLY_BELL_FILE, EXTRA1_FILE, EXTRA2_FILE

    while True:
        print("========== SETTINGS ==========")
        print("1. Change National Anthem file")
        print("2. Change Assembly Bell file")
        print("3. Set Extra Audio 1")
        print("4. Set Extra Audio 2")
        print("5. Change Prayer/Birthday file for a specific day")
        print("0. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            path = input("Enter path/filename for National Anthem: ").strip()
            if path:
                NATIONAL_ANTHEM_FILE = path
        elif choice == "2":
            path = input("Enter path/filename for Assembly Bell: ").strip()
            if path:
                ASSEMBLY_BELL_FILE = path
        elif choice == "3":
            path = input("Enter path/filename for Extra Audio 1: ").strip()
            if path:
                EXTRA1_FILE = path
        elif choice == "4":
            path = input("Enter path/filename for Extra Audio 2: ").strip()
            if path:
                EXTRA2_FILE = path
        elif choice == "5":
            print("Which day?")
            print("0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun")
            try:
                d = int(input("Day index: ").strip())
            except ValueError:
                print("Invalid index.")
                continue
            if d not in DAY_CONFIG:
                DAY_CONFIG[d] = {"label": "", "prayer": "", "birthday": ""}
            new_prayer = input("New prayer file (blank = no change): ").strip()
            new_bday   = input("New birthday file (blank = no change): ").strip()
            new_label  = input("New label (blank = no change): ").strip()
            if new_prayer:
                DAY_CONFIG[d]["prayer"] = new_prayer
            if new_bday:
                DAY_CONFIG[d]["birthday"] = new_bday
            if new_label:
                DAY_CONFIG[d]["label"] = new_label
        elif choice == "0":
            return
        else:
            print("Invalid choice, try again.\n")


# --------------- ABOUT US (OPTION 5) ---------------

def about_us():
    print("========== ABOUT US ==========")
    print("Smart School Bell & Assembly System")
    print("Designed by Daniel (JOTHI WhatsApp Bell Bot project).")
    print("Python + pygame backend. GUI and WhatsApp API to be added later.")
    print("==============================")
    input("Press Enter to go back to main menu...")


# --------------- BELL MENU (OPTION 1) ---------------

def bell_menu():
    """Sub-menu for Bell mode."""
    set_mode("BELL")
    while True:
        print("========== BELL MODE ==========")
        print("1. Start bell scheduler with a fixed demo schedule")
        print("   (Edit code later to load real timetable or from file.)")
        print("0. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            # Example schedule – CHANGE THIS TO YOUR REAL SCHOOL TIMES
            demo_schedule = ["08:30", "09:30", "10:30", "11:30", "12:30", "13:30"]
            print("Starting bell scheduler with demo times:", demo_schedule)
            print("Remember: no bells will ring while you are in Assembly mode.")
            ringBell(demo_schedule, audio_file="bell.mp3", check_interval=20, volume=0.9)
        elif choice == "0":
            set_mode("IDLE")
            return
        else:
            print("Invalid choice, try again.\n")


# --------------- MAIN MENU ---------------

def main_menu():
    while True:
        print("========== MAIN MENU ==========")
        print("1. Bell")
        print("2. Assembly")
        print("3. Announcement")
        print("4. Settings")
        print("5. About us")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            bell_menu()
        elif choice == "2":
            assembly_menu()
        elif choice == "3":
            announcement_menu()
        elif choice == "4":
            settings_menu()
        elif choice == "5":
            about_us()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.\n")


if __name__ == "__main__":
    main_menu()
