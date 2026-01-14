# 🔥 Calcifer CLI

A fire-demon-themed nutrition tracking CLI application built with Python. Track your food intake, monitor weight, and manage your nutritional goals with the sassy guidance of Calcifer, your personal fire demon.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **🔥 Feed the Fire** - Log food with automatic nutritional lookup via USDA & Open Food Facts APIs
- **⚖️ Weigh the Flame** - Track your weight with personalized commentary
- **⚙️ Tune the Furnace** - Customize your goals and personal settings
- **❓ Ask Calcifer** - Get status updates, explanations, and guidance
- **📊 Daily Summary** - See your daily progress on exit

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Calcifer_CLI_app.git
cd Calcifer_CLI_app
```

2. Run the application:

```bash
python3 Calcifer.py
```

Dependencies are automatically installed on first run:

- `rich` - Terminal formatting and progress bars
- `simple-term-menu` - Interactive menu system
- `requests` - API calls

## 📖 Usage

### First Launch

On first launch, Calcifer will guide you through an onboarding process:

1. Enter your name
2. Provide your age, biological sex, height, and weight
3. Select your activity level
4. Receive your personalized daily targets

### Main Menu

```
Calcifer's Control Panel:

❱ 1. Feed the Fire        (Log Food)
  2. Weigh the Flame      (Log Weight)
  3. Tune the Furnace     (User Settings)
  4. Ask Calcifer         (Help)
  5. Exit
```

### Logging Food

1. Select "Feed the Fire"
2. Enter a food name (e.g., "apple", "chicken breast")
3. Select from search results
4. View detailed nutritional information
5. Enter serving size in grams
6. Select meal type and confirm

### Logging Weight

1. Select "Weigh the Flame"
2. Enter your current weight in kg
3. Receive personalized feedback based on weight changes

## 📁 Project Structure

```
Calcifer_CLI_app/
├── Calcifer.py     # Main application file
├── Log/                 # Data storage directory
│   ├── config.json      # User profile and settings
│   ├── food_log.csv     # Food entry history
│   └── weight_log.csv   # Weight tracking history
└── Calcifer_doc/        # Documentation
    ├── README.md        # This file
    ├── STATE_DIAGRAMS.md
    ├── DATA_FLOW.md
    └── API_REFERENCE.md
```

## 🔧 Configuration

User data is stored locally in the `Log/` folder:

| File             | Purpose                           |
| ---------------- | --------------------------------- |
| `config.json`    | User profile, goals, and settings |
| `food_log.csv`   | Complete food logging history     |
| `weight_log.csv` | Weight tracking history           |

## 🧮 Calculations

### Basal Metabolic Rate (BMR)

Uses the Mifflin-St Jeor equation:

- **Male**: BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age + 5
- **Female**: BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age − 161

### Total Daily Energy Expenditure (TDEE)

TDEE = BMR × Activity Multiplier

| Activity Level | Multiplier |
| -------------- | ---------- |
| Sedentary      | 1.2        |
| Light          | 1.375      |
| Moderate       | 1.55       |
| High           | 1.725      |

### Macro Split

| Macro         | Percentage | Calories/gram |
| ------------- | ---------- | ------------- |
| Protein       | 25%        | 4 kcal/g      |
| Carbohydrates | 45%        | 4 kcal/g      |
| Fat           | 25%        | 9 kcal/g      |
| Fiber         | 28g/day    | -             |

## 🌐 APIs Used

### USDA FoodData Central

- **Best for**: Generic and whole foods
- **Data**: Government-maintained, highly reliable
- **Nutrients per**: 100g

### Open Food Facts

- **Best for**: Branded and packaged foods
- **Data**: Community-maintained, label-based
- **Fallback**: Used when USDA returns no results

## 🎭 Calcifer's Personality

Calcifer is a fire demon with a distinct personality:

- **Playful and sassy** - Expect witty commentary
- **Helpful but opinionated** - Clear guidance with attitude
- **Fire metaphors** - Your metabolism is the "flame", food is "fuel"

Example responses:

- Low calories: _"The fire's still hungry."_
- On target: _"Now that's a controlled burn."_
- Excess: _"Careful. I'm starting to smoke."_

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Calcifer from _Howl's Moving Castle_ by Studio Ghibli
- USDA FoodData Central for nutritional data
- Open Food Facts community for branded food data

---

_"What you eat keeps the fire alive!"_ 🔥
