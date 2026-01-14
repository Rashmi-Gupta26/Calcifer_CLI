#!/usr/bin/env python3
"""
🔥 Calcifer CLI - Nutrition Tracking Application
A fire-demon-themed CLI app for tracking food, weight, and nutritional goals.
"""

import shutil
import subprocess
import sys
import os
import json
import csv
import time
import signal
import traceback
from datetime import datetime, date
from pathlib import Path

# ── FIX: Ensure correct working directory when double-clicked ────────────────
try:
    os.chdir(Path(__file__).parent.resolve())
except Exception:
    pass

# ── Ensure dependencies are installed (silently) ─────────────────
try:
    def ensure(pkg):
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            # Print status because this might take a moment
            print(f"🔥 Fueling up: Installing {pkg}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            except subprocess.CalledProcessError:
                # Fallback: try user install if system install fails permissions
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--user", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

    ensure("rich")
    ensure("simple-term-menu")
    ensure("requests")

    from rich.console import Console
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from simple_term_menu import TerminalMenu
    import requests

except Exception as e:
    print(f"\n❌ Critical Startup Error: {e}")
    traceback.print_exc()
    print("\nPress Enter to exit...")
    input()
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────
# Use local Log folder in the app directory
APP_DIR = Path(__file__).parent.resolve()
LOG_DIR = APP_DIR / "Log"
CONFIG_FILE = LOG_DIR / "config.json"
FOOD_LOG_FILE = LOG_DIR / "food_log.csv"
WEIGHT_LOG_FILE = LOG_DIR / "weight_log.csv"

# API Configuration
USDA_API_KEY = "Your USDA API Key"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
OFF_BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"

# Activity multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    1: ("Sedentary", 1.2),
    2: ("Light", 1.375),
    3: ("Moderate", 1.55),
    4: ("High", 1.725),
}

# ── ANSI helpers (truecolor) ───────────────────────────────────
RESET = "\u001b[0m"
console = Console()

def hex_fg(hex_color: str) -> str:
    """Convert #RRGGBB → ANSI truecolor foreground."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"\u001b[38;2;{r};{g};{b}m"

# ── Color rules (char → HEX) ───────────────────────────────────
HEX_COLORS = {
    "█": "#e63723",
    "▓": "#f09b3c",
    "░": "#f0f050",
    "@": "#000000",
    ".": "#ffffff",
    "#": "#e63723",
    **dict.fromkeys("╔═╗║╚╝", "#7a1c1c"),
}

REPLACE = dict.fromkeys("█▓░@.#", "█")

# ── Banner art ────────────────────────────────────────────────
BANNER = [
    "\n            ██",
    "          ██▓▓██",
    "    ██  ██▓▓▓▓▓▓██",
    "  ██▓▓██▓▓▓▓░░▓▓▓▓██",
    "  ██▓▓▓▓▓▓░░░░░░▓▓██  ██       ######╗ #####╗ ##╗      ######╗##╗#######╗#######╗######╗   ",
    "  ██▓▓▓▓▓▓░░░░░░▓▓▓▓████      ##╔════╝##╔══##╗##║     ##╔════╝##║##╔════╝##╔════╝##╔══##╗  ",
    "    ██▓▓░░░░░░░░░░▓▓▓▓██      ##║     #######║##║     ##║     ##║#####╗  #####╗  ######╔╝  ",
    "  ██▓▓..░░░░░░░░░░..▓▓██      ##║     ##╔══##║##║     ##║     ##║##╔══╝  ##╔══╝  ##╔══##╗  ",
    "  ██..@@..░░░░░░..@@..██      ╚######╗##║  ##║#######╗╚######╗##║##║     #######╗##║  ##║  ",
    "  ██▓▓..░░░░░░░░░░..▓▓██       ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝  ",
    "    ██▓▓░░██████░░▓▓██",
    "    ████▓▓▓▓▓▓▓▓▓▓████                   What you eat keeps the fire alive!",
    "        ██████████\n",
]

FC, EC = "#e63623", "#333333"  # bar colors

# ── Helper Functions ──────────────────────────────────────────────

def calcifer_print(text: str, delay: float = 0.03, newline: bool = True):
    """Print text with Calcifer's personality - character by character for effect."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    if newline:
        print()

def calcifer_say(lines: list, line_delay: float = 0.4):
    """Print multiple lines with delays between them."""
    for line in lines:
        calcifer_print(line, delay=0.02)
        time.sleep(line_delay)

def get_input(prompt: str, validator=None, error_msg: str = None) -> str:
    """Get validated input from user with Calcifer-style error messages."""
    while True:
        calcifer_print(prompt, delay=0.015)
        user_input = input("> ").strip()
        
        if not user_input:
            calcifer_print("Silence doesn't feed the fire. Answer properly.", delay=0.02)
            continue
            
        if validator:
            try:
                result = validator(user_input)
                return result
            except (ValueError, TypeError):
                if error_msg:
                    calcifer_print(error_msg, delay=0.02)
                else:
                    calcifer_print("That's not valid... Try again before I lose my temper.", delay=0.02)
        else:
            return user_input

def get_numeric_input(prompt: str, min_val=None, max_val=None) -> float:
    """Get a numeric input with validation."""
    def validate(x):
        val = float(x)
        if min_val is not None and val < min_val:
            raise ValueError()
        if max_val is not None and val > max_val:
            raise ValueError()
        return val
    return get_input(prompt, validate, "That's not a number... Try again before I lose my temper.")

def get_int_input(prompt: str, min_val=None, max_val=None) -> int:
    """Get an integer input with validation."""
    def validate(x):
        val = int(x)
        if min_val is not None and val < min_val:
            raise ValueError()
        if max_val is not None and val > max_val:
            raise ValueError()
        return val
    return get_input(prompt, validate, "That's not a valid number... Try again.")

def render_banner():
    """Render the colorful Calcifer banner."""
    rows, cols = shutil.get_terminal_size()
    needed_cols = max(len(line) for line in BANNER) + 6
    
    if needed_cols > cols:
        print(f"\x1b[8;{rows};{needed_cols}t", end="")
    
    for line in BANNER:
        print("".join(
            f"{hex_fg(HEX_COLORS[ch])}{REPLACE.get(ch, ch)}{RESET}"
            if ch in HEX_COLORS else ch
            for ch in line
        ))

def progress_bar(label: str, value: float, total: float, unit: str = "", width: int = 50) -> Text:
    """Create a single-line labeled progress bar."""
    value = min(value, total)  # Cap at 100%
    filled = int(width * value / total) if total > 0 else 0
    return (
        Text(f"{label}\t") +
        Text("━" * filled, style=f"bold {FC}") +
        Text("━" * (width - filled), style=EC) +
        Text(f"  {int(value * 100 / total) if total > 0 else 0}% | {value:.0f}/{total:.0f}{unit}")
    )

# ── Data Persistence ──────────────────────────────────────────────

def ensure_log_dir():
    """Create the Log directory if it doesn't exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """Load user configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def save_config(config: dict):
    """Save user configuration to file."""
    ensure_log_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def is_first_launch() -> bool:
    """Check if this is the first launch."""
    return not CONFIG_FILE.exists()

# ── Metabolic Calculations ────────────────────────────────────────

def calculate_bmr(weight: float, height: float, age: int, sex: int) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if sex == 1:  # Male
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:  # Female
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr: float, activity_level: int) -> float:
    """Calculate Total Daily Energy Expenditure."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, (None, 1.2))[1]
    return bmr * multiplier

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate Body Mass Index."""
    height_m = height / 100
    return weight / (height_m ** 2)

def get_bmi_status(bmi: float) -> str:
    """Get BMI status description."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Healthy"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def calculate_macros(calories: float) -> dict:
    """Calculate macro nutrient targets."""
    return {
        "protein": int(calories * 0.25 / 4),  # 25% of calories, 4 cal/g
        "carbs": int(calories * 0.45 / 4),    # 45% of calories, 4 cal/g
        "fat": int(calories * 0.25 / 9),       # 25% of calories, 9 cal/g
        "fiber": 28,  # Standard recommendation
    }

# ── CSV Logging ───────────────────────────────────────────────────

def log_food_entry(food_name: str, meal_type: str, calories: float, protein: float, carbs: float, fat: float):
    """Log a food entry to CSV."""
    ensure_log_dir()
    file_exists = FOOD_LOG_FILE.exists()
    
    with open(FOOD_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "time", "food_name", "meal_type", "calories", "protein", "carbs", "fat"])
        writer.writerow([
            date.today().isoformat(),
            datetime.now().strftime("%H:%M"),
            food_name,
            meal_type,
            round(calories, 1),
            round(protein, 1),
            round(carbs, 1),
            round(fat, 1),
        ])

def log_weight_entry(weight: float):
    """Log a weight entry to CSV."""
    ensure_log_dir()
    file_exists = WEIGHT_LOG_FILE.exists()
    
    with open(WEIGHT_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "time", "weight"])
        writer.writerow([
            date.today().isoformat(),
            datetime.now().strftime("%H:%M"),
            round(weight, 1),
        ])

def get_todays_calories() -> float:
    """Get total calories logged today."""
    if not FOOD_LOG_FILE.exists():
        return 0.0
    
    today = date.today().isoformat()
    total = 0.0
    
    with open(FOOD_LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] == today:
                total += float(row["calories"])
    
    return total

def get_todays_macros() -> dict:
    """Get total macros logged today."""
    if not FOOD_LOG_FILE.exists():
        return {"protein": 0, "carbs": 0, "fat": 0}
    
    today = date.today().isoformat()
    totals = {"protein": 0.0, "carbs": 0.0, "fat": 0.0}
    
    with open(FOOD_LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] == today:
                totals["protein"] += float(row["protein"])
                totals["carbs"] += float(row["carbs"])
                totals["fat"] += float(row["fat"])
    
    return totals

def get_last_weight() -> float:
    """Get the last logged weight."""
    if not WEIGHT_LOG_FILE.exists():
        return None
    
    last_weight = None
    with open(WEIGHT_LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            last_weight = float(row["weight"])
    
    return last_weight

def get_previous_weight() -> float:
    """Get the second-to-last logged weight for comparison."""
    if not WEIGHT_LOG_FILE.exists():
        return None
    
    weights = []
    with open(WEIGHT_LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            weights.append(float(row["weight"]))
    
    if len(weights) >= 2:
        return weights[-2]
    return None

# ── API Integration ───────────────────────────────────────────────

# Calcifer-themed spinner messages
SPINNER_MESSAGES = [
    "🔥 Consulting the flames...",
    "🔥 Searching the fire's memory...",
    "🔥 Heating up the data...",
    "🔥 Stoking the coals for answers...",
]

def search_with_spinner(query: str) -> list:
    """Search for food with a Calcifer-themed spinner."""
    import random
    spinner_msg = random.choice(SPINNER_MESSAGES)
    
    results = []
    
    with Progress(
        SpinnerColumn("dots12"),
        TextColumn("[bold red]{task.description}[/bold red]"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task(spinner_msg, total=None)
        
        # Try USDA first
        results = search_usda(query)
        
        if not results:
            progress.update(task, description="🔥 Checking the backup flames...")
            results = search_open_food_facts(query)
    
    return results

def search_usda(query: str) -> list:
    """Search USDA FoodData Central API."""
    try:
        response = requests.get(
            f"{USDA_BASE_URL}/foods/search",
            params={
                "api_key": USDA_API_KEY,
                "query": query,
                "pageSize": 5,
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            foods = []
            for item in data.get("foods", [])[:5]:
                nutrients = {n["nutrientName"]: n.get("value", 0) for n in item.get("foodNutrients", [])}
                # Get additional nutrients for more detail
                fiber = nutrients.get("Fiber, total dietary", 0)
                sugar = nutrients.get("Sugars, total including NLEA", nutrients.get("Total Sugars", 0))
                sodium = nutrients.get("Sodium, Na", 0)
                
                foods.append({
                    "name": item.get("description", query),
                    "brand": item.get("brandName", item.get("brandOwner", "Generic")),
                    "category": item.get("foodCategory", "Unknown"),
                    "source": "USDA",
                    "calories": nutrients.get("Energy", 0),
                    "protein": nutrients.get("Protein", 0),
                    "carbs": nutrients.get("Carbohydrate, by difference", 0),
                    "fat": nutrients.get("Total lipid (fat)", 0),
                    "fiber": fiber,
                    "sugar": sugar,
                    "sodium": sodium,
                    "serving_size": 100,
                    "serving_unit": "g",
                })
            return foods
    except Exception:
        pass
    return []

def search_open_food_facts(query: str) -> list:
    """Search Open Food Facts API."""
    try:
        response = requests.get(
            OFF_BASE_URL,
            params={
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 5,
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            foods = []
            for item in data.get("products", [])[:5]:
                nutrients = item.get("nutriments", {})
                foods.append({
                    "name": item.get("product_name", query) or query,
                    "brand": item.get("brands", "Unknown"),
                    "category": item.get("categories_tags", ["Unknown"])[0] if item.get("categories_tags") else "Unknown",
                    "source": "Open Food Facts",
                    "calories": nutrients.get("energy-kcal_100g", 0) or 0,
                    "protein": nutrients.get("proteins_100g", 0) or 0,
                    "carbs": nutrients.get("carbohydrates_100g", 0) or 0,
                    "fat": nutrients.get("fat_100g", 0) or 0,
                    "fiber": nutrients.get("fiber_100g", 0) or 0,
                    "sugar": nutrients.get("sugars_100g", 0) or 0,
                    "sodium": nutrients.get("sodium_100g", 0) or 0,
                    "serving_size": 100,
                    "serving_unit": "g",
                })
            return foods
    except Exception:
        pass
    return []

def search_food(query: str) -> list:
    """Search for food using both APIs with fallback."""
    return search_with_spinner(query)

def display_food_details(food: dict):
    """Display detailed food information in a nice table."""
    console.print(f"\n[bold yellow]📋 RAW FOOD DATA[/bold yellow]")
    console.print(f"[dim]Source: {food.get('source', 'Unknown')}[/dim]")
    
    # Create a table for raw data
    table = Table(show_header=True, header_style="bold red")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Name", food.get('name', 'Unknown'))
    table.add_row("Brand", str(food.get('brand', 'Generic')))
    table.add_row("Category", str(food.get('category', 'Unknown')))
    table.add_row("Serving Size", f"{food.get('serving_size', 100)}{food.get('serving_unit', 'g')}")
    
    console.print(table)
    
    # Nutritional info table
    console.print(f"\n[bold yellow]🔥 NUTRITIONAL INFO (per 100g)[/bold yellow]")
    
    nutri_table = Table(show_header=True, header_style="bold red")
    nutri_table.add_column("Nutrient", style="cyan")
    nutri_table.add_column("Amount", justify="right", style="white")
    
    nutri_table.add_row("🔥 Calories", f"{food.get('calories', 0):.1f} kcal")
    nutri_table.add_row("🥩 Protein", f"{food.get('protein', 0):.1f} g")
    nutri_table.add_row("🍞 Carbohydrates", f"{food.get('carbs', 0):.1f} g")
    nutri_table.add_row("  └─ Sugar", f"{food.get('sugar', 0):.1f} g")
    nutri_table.add_row("🥑 Fat", f"{food.get('fat', 0):.1f} g")
    nutri_table.add_row("🌾 Fiber", f"{food.get('fiber', 0):.1f} g")
    nutri_table.add_row("🧂 Sodium", f"{food.get('sodium', 0):.1f} mg")
    
    console.print(nutri_table)

# ── Onboarding Flow ───────────────────────────────────────────────

def run_onboarding() -> dict:
    """Run the first-launch onboarding flow."""
    render_banner()
    time.sleep(1.5)
    
    # Introduction
    print()
    calcifer_say([
        "Oi. Yeah, you.",
        "I'm Calcifer — the fire that keeps this whole operation running.",
        "",
        "If I'm going to keep you healthy,",
        "I need to know what I'm working with.",
    ])
    
    print()
    calcifer_say([
        "Don't worry.",
        "I'll do the math.",
        "You just answer honestly.",
    ])
    
    print()
    
    # Get user data
    # Name
    name = get_input("First things first.\nWhat should I call you?")
    calcifer_say([f"Right then. {name} it is.", "Try not to make this difficult."])
    print()
    
    # Age
    age = get_int_input(f"How many years has this body been walking the earth, {name}?", 1, 120)
    calcifer_say(["Hmm. Not brand new, not falling apart.", "Good."])
    print()
    
    # Sex
    print("I need this for the calculations.")
    print("What's your biological sex?\n")
    sex_menu = TerminalMenu(
        ["1. Male", "2. Female", "3. Prefer not to say"],
        menu_cursor="❱ ",
        menu_cursor_style=("bold", "fg_red"),
        menu_highlight_style=("bold", "fg_red"),
    )
    sex_choice = sex_menu.show()
    sex = sex_choice + 1 if sex_choice is not None else 3
    if sex == 3:
        sex = 1  # Default to male formula if not specified
    calcifer_say(["Got it.", "Numbers care about biology, not vibes."])
    print()
    
    # Height
    height = get_numeric_input("How tall are we working with?\n(Use cm)", 50, 300)
    calcifer_say(["Alright.", "Noted."])
    print()
    
    # Weight
    weight = get_numeric_input("And finally…\nWhat's your current weight?\n(kg)", 20, 500)
    calcifer_say(["Recorded.", "The flame now has a baseline."])
    print()
    
    # Activity level
    print("One more thing. How active are you?")
    activity_menu = TerminalMenu(
        [f"{i}. {name}" for i, (name, _) in ACTIVITY_MULTIPLIERS.items()],
        menu_cursor="❱ ",
        menu_cursor_style=("bold", "fg_red"),
        menu_highlight_style=("bold", "fg_red"),
    )
    activity_choice = activity_menu.show()
    activity_level = activity_choice + 1 if activity_choice is not None else 1
    calcifer_say(["Alright.", "I'll burn accordingly."])
    print()
    
    # Calculate
    print()
    calcifer_say([
        "Warming up the flame...",
        "Balancing fuel ratios...",
        "Running the numbers...",
    ], line_delay=0.5)
    
    bmr = calculate_bmr(weight, height, int(age), sex)
    tdee = calculate_tdee(bmr, activity_level)
    calories = int(tdee)
    macros = calculate_macros(calories)
    bmi = calculate_bmi(weight, height)
    
    print()
    calcifer_say([
        f"All set, {name}.",
        "",
        "I've tuned the fire to your body:",
        "• Daily calorie target ready",
        "• Macro balance prepared",
        "• Flame monitoring online",
    ])
    
    print()
    console.print(f"[bold]🔥 Daily Energy[/bold]\n   Calories : {calories} kcal\n")
    console.print(f"[bold]🥩 Protein[/bold]\n   {macros['protein']} g   — for strength and recovery\n")
    console.print(f"[bold]🍞 Carbohydrates[/bold]\n   {macros['carbs']} g     — your main fuel source\n")
    console.print(f"[bold]🥑 Fats[/bold]\n   {macros['fat']} g       — long-burning energy\n")
    console.print(f"[bold]🌾 Fiber[/bold]\n   {macros['fiber']} g     — for digestion and balance\n")
    
    print()
    calcifer_say([
        "These aren't rules.",
        "They're guides.",
        "",
        "Hit them often, miss them sometimes —",
        "I'll help you adjust as you go.",
        "",
        "Whenever you're ready,",
        "let's feed the fire.",
    ])
    
    # Save config
    config = {
        "name": name,
        "age": int(age),
        "sex": sex,
        "height": height,
        "weight": weight,
        "activity_level": activity_level,
        "calorie_goal": calories,
        "protein_goal": macros["protein"],
        "carbs_goal": macros["carbs"],
        "fat_goal": macros["fat"],
        "fiber_goal": macros["fiber"],
        "bmi": round(bmi, 1),
    }
    save_config(config)
    
    # Log initial weight
    log_weight_entry(weight)
    
    print()
    input("Press Enter to open Calcifer's Control Panel...")
    
    return config

# ── Main Menu Display ─────────────────────────────────────────────

def display_dashboard(config: dict):
    """Display the main dashboard with progress bars."""
    render_banner()
    
    name = config["name"]
    calorie_goal = config["calorie_goal"]
    current_cals = get_todays_calories()
    macros = get_todays_macros()
    last_weight = get_last_weight() or config["weight"]
    bmi = calculate_bmi(last_weight, config["height"])
    bmi_status = get_bmi_status(bmi)
    
    # Generate status message
    if current_cals < calorie_goal * 0.5:
        status_msg = "your flame's steady but a little hungry."
    elif current_cals < calorie_goal * 0.9:
        status_msg = "the fire's burning nicely today."
    elif current_cals <= calorie_goal * 1.1:
        status_msg = "now that's a controlled burn!"
    else:
        status_msg = "careful, I'm starting to smoke."
    
    console.print(f"\n[bold]{name}[/bold], {status_msg}")
    console.print(f"BMI is in a {bmi_status.lower()} range, last weight [bold]{last_weight:.1f}[/bold] kg.")
    console.print("Toss on some fuel — Calcifer doesn't work for free.\n")
    
    # Progress bars
    console.print(progress_bar("Total Calories", current_cals, calorie_goal, " kCal", 60), "\n")
    
    console.print(
        progress_bar("Carbs", macros["carbs"], config["carbs_goal"], "g", 24), "\t",
        progress_bar("Fat", macros["fat"], config["fat_goal"], "g", 24), "\n"
    )
    
    console.print(
        progress_bar("Protein", macros["protein"], config["protein_goal"], "g", 24), "\t",
        progress_bar("Fiber", 0, config["fiber_goal"], "g", 24), "\n"
    )
    
    print()

# ── Menu Actions ──────────────────────────────────────────────────

def feed_the_fire(config: dict):
    """Food logging flow."""
    name = config["name"]
    calorie_goal = config["calorie_goal"]
    
    print()
    calcifer_say([f"Alright, {name}.", "What are we throwing into the fire?"])
    print()
    
    food_query = get_input("Name the food.")
    print()
    
    # Search for food with spinner
    results = search_food(food_query)
    
    if not results:
        calcifer_say(["Hmm. I couldn't find that in my records.", "Try something else."])
        input("\nPress Enter to continue...")
        return
    
    calcifer_print(f"Found {len(results)} result(s). Take your pick.")
    print()
    
    # Let user select from results - show more info
    print("Select the food:\n")
    menu_items = []
    for i, r in enumerate(results):
        name = r['name'][:40] if r['name'] else 'Unknown'
        brand = r.get('brand', 'Generic')
        brand = brand[:15] if brand else 'Generic'
        cals = r.get('calories', 0)
        menu_items.append(f"{i+1}. {name} [{brand}] ({cals:.0f} kcal/100g)")
    menu_items.append("Cancel")
    
    food_menu = TerminalMenu(
        menu_items,
        menu_cursor="❱ ",
        menu_cursor_style=("bold", "fg_red"),
        menu_highlight_style=("bold", "fg_red"),
    )
    choice = food_menu.show()
    
    if choice is None or choice >= len(results):
        return
    
    selected = results[choice]
    
    # Display detailed raw food data first
    display_food_details(selected)
    print()
    
    # Get serving size
    serving = get_numeric_input("How many grams?", 1, 5000)
    
    # Scale nutrients
    scale = serving / 100
    calories = selected["calories"] * scale
    protein = selected["protein"] * scale
    carbs = selected["carbs"] * scale
    fat = selected["fat"] * scale
    
    print()
    print(f"That's {calories:.0f} kcal | P: {protein:.1f}g | C: {carbs:.1f}g | F: {fat:.1f}g")
    print()
    
    # Select meal type
    print("What meal is this?")
    meal_menu = TerminalMenu(
        ["1. Breakfast", "2. Lunch", "3. Dinner", "4. Snack"],
        menu_cursor="❱ ",
        menu_cursor_style=("bold", "fg_red"),
        menu_highlight_style=("bold", "fg_red"),
    )
    meal_choice = meal_menu.show()
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    meal_type = meal_types[meal_choice] if meal_choice is not None else "Snack"
    
    # Confirm
    print()
    print("Log this entry? [Y/n]")
    confirm = input("> ").strip().lower()
    
    if confirm != "n":
        log_food_entry(selected["name"], meal_type, calories, protein, carbs, fat)
        current = get_todays_calories()
        print()
        calcifer_say(["Added to the fire.", f"Today's total: {current:.0f} / {calorie_goal} kcal"])
        
        # Commentary
        ratio = current / calorie_goal
        if ratio < 0.5:
            calcifer_print("Plenty of room left. The flame's still hungry.")
        elif ratio <= 1.0:
            calcifer_print("Now that's a controlled burn.")
        else:
            calcifer_print("Careful. I'm starting to smoke.")
    
    print()
    input("Press Enter to continue...")

def weigh_the_flame(config: dict):
    """Weight logging flow."""
    name = config["name"]
    
    print()
    calcifer_say([f"Moment of truth, {name}.", "Let's see what gravity thinks today."])
    print()
    
    weight = get_numeric_input("Enter your current weight.\n(kg)", 20, 500)
    
    prev_weight = get_last_weight()
    log_weight_entry(weight)
    
    # Update config with new weight
    config["weight"] = weight
    config["bmi"] = round(calculate_bmi(weight, config["height"]), 1)
    save_config(config)
    
    print()
    calcifer_say(["Recorded.", f"Last known weight: {weight:.1f} kg"])
    
    # Commentary based on change
    if prev_weight:
        diff = weight - prev_weight
        if diff > 0.5:
            calcifer_print("Heavier flame. Happens.")
        elif diff < -0.5:
            calcifer_print("Lighter. Someone's behaving.")
        else:
            calcifer_print("Stable. I like predictable fires.")
    
    print()
    input("Press Enter to continue...")

def tune_the_furnace(config: dict):
    """Settings menu."""
    while True:
        print()
        calcifer_say(["Ah. Adjustments.", "Let's fiddle with the knobs."])
        print()
        
        settings_menu = TerminalMenu(
            [
                "1. Update personal details",
                "2. Change activity level",
                "3. Change calorie goal",
                "4. Recalculate everything",
                "5. Back",
            ],
            menu_cursor="❱ ",
            menu_cursor_style=("bold", "fg_red"),
            menu_highlight_style=("bold", "fg_red"),
        )
        choice = settings_menu.show()
        
        if choice == 0:  # Update personal details
            update_details_menu(config)
        elif choice == 1:  # Change activity level
            print()
            print("How active are we being these days?\n")
            activity_menu = TerminalMenu(
                [f"{i}. {name}" for i, (name, _) in ACTIVITY_MULTIPLIERS.items()],
                menu_cursor="❱ ",
                menu_cursor_style=("bold", "fg_red"),
                menu_highlight_style=("bold", "fg_red"),
            )
            new_level = activity_menu.show()
            if new_level is not None:
                config["activity_level"] = new_level + 1
                save_config(config)
                calcifer_say(["Alright.", "I'll burn accordingly."])
                input("\nPress Enter to continue...")
        elif choice == 2:  # Change calorie goal
            print()
            print(f"Current daily target: {config['calorie_goal']} kcal")
            new_goal = get_int_input("What's the new target?", 500, 10000)
            config["calorie_goal"] = new_goal
            save_config(config)
            calcifer_say(["Understood.", "I'll aim the flame there."])
            input("\nPress Enter to continue...")
        elif choice == 3:  # Recalculate everything
            print()
            print("This will redo all the math.")
            print("Old numbers go in the fire.\n")
            confirm_menu = TerminalMenu(
                ["1. Do it", "2. Never mind"],
                menu_cursor="❱ ",
                menu_cursor_style=("bold", "fg_red"),
                menu_highlight_style=("bold", "fg_red"),
            )
            if confirm_menu.show() == 0:
                recalculate_all(config)
                calcifer_say(["Done.", "Fresh numbers. Fresh fire."])
                input("\nPress Enter to continue...")
        else:  # Back
            break

def update_details_menu(config: dict):
    """Update personal details sub-menu."""
    while True:
        print()
        print("What's changed since last time?\n")
        details_menu = TerminalMenu(
            [
                f"1. Age (current: {config['age']})",
                f"2. Height (current: {config['height']} cm)",
                f"3. Weight (current: {config['weight']:.1f} kg)",
                "4. Gender",
                "5. Back",
            ],
            menu_cursor="❱ ",
            menu_cursor_style=("bold", "fg_red"),
            menu_highlight_style=("bold", "fg_red"),
        )
        choice = details_menu.show()
        
        if choice == 0:  # Age
            config["age"] = get_int_input("New age?", 1, 120)
            save_config(config)
            calcifer_say(["Updated.", "The fire has been retuned."])
        elif choice == 1:  # Height
            config["height"] = get_numeric_input("New height (cm)?", 50, 300)
            config["bmi"] = round(calculate_bmi(config["weight"], config["height"]), 1)
            save_config(config)
            calcifer_say(["Updated.", "The fire has been retuned."])
        elif choice == 2:  # Weight
            config["weight"] = get_numeric_input("New weight (kg)?", 20, 500)
            config["bmi"] = round(calculate_bmi(config["weight"], config["height"]), 1)
            log_weight_entry(config["weight"])
            save_config(config)
            calcifer_say(["Updated.", "The fire has been retuned."])
        elif choice == 3:  # Gender
            print()
            sex_menu = TerminalMenu(
                ["1. Male", "2. Female"],
                menu_cursor="❱ ",
                menu_cursor_style=("bold", "fg_red"),
                menu_highlight_style=("bold", "fg_red"),
            )
            new_sex = sex_menu.show()
            if new_sex is not None:
                config["sex"] = new_sex + 1
                save_config(config)
                calcifer_say(["Updated.", "The fire has been retuned."])
        else:  # Back
            break
        
        if choice != 4:
            input("\nPress Enter to continue...")

def recalculate_all(config: dict):
    """Recalculate all metabolic values."""
    bmr = calculate_bmr(config["weight"], config["height"], config["age"], config["sex"])
    tdee = calculate_tdee(bmr, config["activity_level"])
    calories = int(tdee)
    macros = calculate_macros(calories)
    bmi = calculate_bmi(config["weight"], config["height"])
    
    config["calorie_goal"] = calories
    config["protein_goal"] = macros["protein"]
    config["carbs_goal"] = macros["carbs"]
    config["fat_goal"] = macros["fat"]
    config["fiber_goal"] = macros["fiber"]
    config["bmi"] = round(bmi, 1)
    
    save_config(config)

def ask_calcifer(config: dict):
    """Help menu."""
    while True:
        print()
        calcifer_say(["Questions?", "Try to keep them sensible."])
        print()
        
        help_menu = TerminalMenu(
            [
                "1. Today's status",
                "2. What does BMI mean?",
                "3. How are my calories calculated?",
                "4. How should I use this app daily?",
                "5. Back",
            ],
            menu_cursor="❱ ",
            menu_cursor_style=("bold", "fg_red"),
            menu_highlight_style=("bold", "fg_red"),
        )
        choice = help_menu.show()
        
        if choice == 0:  # Today's status
            show_todays_status(config)
        elif choice == 1:  # BMI explanation
            print()
            calcifer_say([
                "BMI is a blunt tool.",
                "Useful, not sacred.",
                "",
                "It helps me estimate how hard to burn.",
                "That's it.",
            ])
            input("\nPress Enter to continue...")
        elif choice == 2:  # Calorie calculation
            print()
            calcifer_say([
                "I calculate your base burn.",
                "Then I factor movement.",
                "Then I adjust for goals.",
                "",
                "Science first.",
                "Magic second.",
            ])
            input("\nPress Enter to continue...")
        elif choice == 3:  # Daily usage
            print()
            calcifer_say([
                "Use me like this:",
                "",
                "• Log what you eat",
                "• Check in once or twice",
                "• Don't obsess",
                "• Be consistent",
                "",
                "That's how fires last.",
            ])
            input("\nPress Enter to continue...")
        else:  # Back
            break

def show_todays_status(config: dict):
    """Display today's status."""
    name = config["name"]
    calorie_goal = config["calorie_goal"]
    current_cals = get_todays_calories()
    last_weight = get_last_weight() or config["weight"]
    bmi = calculate_bmi(last_weight, config["height"])
    bmi_status = get_bmi_status(bmi)
    activity_name = ACTIVITY_MULTIPLIERS.get(config["activity_level"], ("Unknown", 1.0))[0]
    
    print()
    calcifer_say([f"Here's where things stand, {name}:"])
    print()
    print(f"• Calories: {current_cals:.0f} / {calorie_goal}")
    print(f"• BMI: {bmi:.1f} ({bmi_status})")
    print(f"• Last weight: {last_weight:.1f} kg")
    print(f"• Activity level: {activity_name}")
    print()
    calcifer_print("No explosions so far. Good job.")
    
    input("\nPress Enter to continue...")

def show_daily_summary(config: dict):
    """Show daily summary on exit."""
    name = config["name"]
    calorie_goal = config["calorie_goal"]
    current_cals = get_todays_calories()
    last_weight = get_last_weight() or config["weight"]
    bmi = calculate_bmi(last_weight, config["height"])
    bmi_status = get_bmi_status(bmi)
    
    # Determine calorie status
    ratio = current_cals / calorie_goal if calorie_goal > 0 else 0
    if ratio < 0.7:
        calorie_status = "Under target"
    elif ratio <= 1.1:
        calorie_status = "On target"
    else:
        calorie_status = "Over target"
    
    print("\n" + "=" * 50)
    console.print(f"\n[bold]🔥 Daily Fire Report — {date.today().strftime('%B %d, %Y')}[/bold]\n")
    
    print(f"{name}, here's how the flame burned today:\n")
    print(f"• Calories: {current_cals:.0f} / {calorie_goal}")
    print(f"• Status: {calorie_status}")
    print(f"• BMI: {bmi:.1f} ({bmi_status})")
    print(f"• Last logged weight: {last_weight:.1f} kg")
    print()
    
    # Dynamic closing line
    if ratio < 0.7:
        calcifer_say(["The fire's still hungry.", "Tomorrow, feed it a bit better."])
    elif ratio <= 1.1:
        calcifer_say(["Now that's a controlled burn.", "I like days like this."])
    else:
        calcifer_say(["We survived.", "Tomorrow, less chaos."])
    
    print()
    calcifer_say([f"Rest up, {name}.", "I'll keep the embers warm."])
    print()

# ── Main Application Loop ─────────────────────────────────────────

def main():
    """Main application entry point."""
    # Check for first launch
    if is_first_launch():
        config = run_onboarding()
    else:
        config = load_config()
    
    # Set up graceful exit handler
    def signal_handler(sig, frame):
        show_daily_summary(config)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Main menu loop
    MENU = [
        ("Feed the Fire        (Log Food)", feed_the_fire),
        ("Weigh the Flame      (Log Weight)", weigh_the_flame),
        ("Tune the Furnace     (User Settings)", tune_the_furnace),
        ("Ask Calcifer         (Help)", ask_calcifer),
        ("Exit", None),
    ]
    
    while True:
        # Clear screen and show dashboard
        print("\033[2J\033[H", end="")  # Clear screen
        display_dashboard(config)
        
        # Show menu
        menu = TerminalMenu(
            [f"{n}. {label}" for n, (label, _) in enumerate(MENU, 1)],
            title="Calcifer's Control Panel:\n",
            menu_cursor="❱ ",
            menu_cursor_style=("bold", "fg_red"),
            menu_highlight_style=("bold", "fg_red"),
            status_bar="\n↑↓  |  Enter  |  Q Quit\n\n",
            status_bar_style=("fg_gray",),
        )
        
        choice = menu.show()
        
        if choice is None or choice == 4:  # Exit or Q pressed
            show_daily_summary(config)
            break
        else:
            # Execute selected action
            action = MENU[choice][1]
            if action:
                action(config)
                # Reload config in case it was updated
                config = load_config()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[bold red]🔥 Critical Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to close the fire...")
        input()