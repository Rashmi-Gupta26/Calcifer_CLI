# 🔥 Calcifer CLI - Data Flow Diagrams

## 1. System Overview DFD

```
                                    ┌─────────────────┐
                                    │      USER       │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
            ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
            │  Food Name    │       │    Weight     │       │   Settings    │
            │  Serving Size │       │     (kg)      │       │    Changes    │
            └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
                    │                       │                       │
                    ▼                       ▼                       ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │                     CALCIFER CLI APPLICATION                       │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
        │  │   Input     │  │  Nutrient   │  │    Calc     │  │   Data    │ │
        │  │  Handler    │→ │  Processor  │→ │   Engine    │→ │  Logger   │ │
        │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
        └───────────────────────────────────────────────────────────────────┘
                    │                       │                       │
                    ▼                       ▼                       ▼
            ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
            │  food_log.csv │       │ weight_log.csv│       │  config.json  │
            └───────────────┘       └───────────────┘       └───────────────┘
```

---

## 2. Food Logging Data Flow

```
┌──────────┐
│   USER   │
└────┬─────┘
     │ food name, serving size
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FOOD LOGGING PIPELINE                              │
│                                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                  │
│  │   Input     │ ───▶ │   API       │ ───▶ │   Food      │                  │
│  │   Handler   │      │   Manager   │      │   Selector  │                  │
│  └─────────────┘      └──────┬──────┘      └──────┬──────┘                  │
│                              │                    │                          │
│                              ▼                    │                          │
│                     ┌────────────────┐            │                          │
│                     │  USDA API      │            │                          │
│                     │  ────────────  │            │                          │
│                     │  Open Food     │            │                          │
│                     │  Facts API     │            │                          │
│                     └────────────────┘            │                          │
│                                                   │                          │
│  ┌─────────────┐      ┌─────────────┐      ┌─────┴───────┐                  │
│  │   CSV       │ ◀─── │   Nutrient  │ ◀─── │   Serving   │                  │
│  │   Logger    │      │   Scaler    │      │   Handler   │                  │
│  └──────┬──────┘      └─────────────┘      └─────────────┘                  │
└─────────│───────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────┐
│  food_log.csv   │
│  ─────────────  │
│  date           │
│  time           │
│  food_name      │
│  meal_type      │
│  calories       │
│  protein        │
│  carbs          │
│  fat            │
└─────────────────┘
```

---

## 3. API Data Flow

```
┌──────────────┐
│  Food Query  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                      API MANAGER                              │
│                                                               │
│   ┌─────────────────────────────────────────────────────┐    │
│   │              USDA FoodData Central                   │    │
│   │   URL: api.nal.usda.gov/fdc/v1/foods/search         │    │
│   │   API Key: Required                                  │    │
│   │   Data: per 100g                                    │    │
│   └──────────────────────┬──────────────────────────────┘    │
│                          │                                    │
│                          ▼                                    │
│                   ┌─────────────┐                             │
│                   │  Results?   │                             │
│                   └──────┬──────┘                             │
│                    YES   │   NO                               │
│                    ┌─────┴─────┐                              │
│                    │           │                              │
│                    ▼           ▼                              │
│             ┌───────────┐  ┌─────────────────────────────┐   │
│             │  Return   │  │   Open Food Facts (Fallback) │   │
│             │  Results  │  │   URL: world.openfoodfacts.org│  │
│             └───────────┘  │   API Key: Not required       │  │
│                            │   Data: per 100g              │  │
│                            └──────────────┬────────────────┘  │
│                                           │                   │
│                                           ▼                   │
│                                    ┌─────────────┐            │
│                                    │   Return    │            │
│                                    │   Results   │            │
│                                    └─────────────┘            │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────┐
│           NORMALIZED FOOD DATA              │
│  ─────────────────────────────────────────  │
│  name, brand, category, source              │
│  calories, protein, carbs, fat              │
│  fiber, sugar, sodium                       │
│  serving_size (100), serving_unit (g)       │
└────────────────────────────────────────────┘
```

---

## 4. Nutrient Scaling Formula

```
┌─────────────────────────────────────────────────────────────┐
│                    NUTRIENT SCALING                          │
│                                                              │
│   Input:                                                     │
│   ├─ base_value (per 100g from API)                         │
│   └─ user_serving (grams entered by user)                   │
│                                                              │
│   Formula:                                                   │
│   scaled_value = base_value × (user_serving / 100)          │
│                                                              │
│   Example:                                                   │
│   ├─ Apple: 52 kcal per 100g                                │
│   ├─ User enters: 150g                                      │
│   └─ Result: 52 × (150/100) = 78 kcal                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Metabolic Calculation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 METABOLIC CALCULATIONS                       │
│                                                              │
│   INPUT DATA                                                 │
│   ├─ weight (kg)                                            │
│   ├─ height (cm)                                            │
│   ├─ age (years)                                            │
│   ├─ sex (1=Male, 2=Female)                                 │
│   └─ activity_level (1-4)                                   │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ STEP 1: Calculate BMR (Mifflin-St Jeor)             │   │
│   │                                                      │   │
│   │ Male:   BMR = 10×weight + 6.25×height - 5×age + 5   │   │
│   │ Female: BMR = 10×weight + 6.25×height - 5×age - 161 │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ STEP 2: Calculate TDEE                              │   │
│   │                                                      │   │
│   │ TDEE = BMR × Activity Multiplier                    │   │
│   │                                                      │   │
│   │ Multipliers:                                        │   │
│   │ ├─ Sedentary: 1.2                                   │   │
│   │ ├─ Light: 1.375                                     │   │
│   │ ├─ Moderate: 1.55                                   │   │
│   │ └─ High: 1.725                                      │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ STEP 3: Calculate Macros                            │   │
│   │                                                      │   │
│   │ Protein: TDEE × 0.25 / 4 (g)                        │   │
│   │ Carbs:   TDEE × 0.45 / 4 (g)                        │   │
│   │ Fat:     TDEE × 0.25 / 9 (g)                        │   │
│   │ Fiber:   28g (fixed)                                │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ STEP 4: Calculate BMI                               │   │
│   │                                                      │   │
│   │ BMI = weight / (height_m)²                          │   │
│   │                                                      │   │
│   │ Categories:                                         │   │
│   │ ├─ < 18.5: Underweight                              │   │
│   │ ├─ 18.5-24.9: Healthy                               │   │
│   │ ├─ 25-29.9: Overweight                              │   │
│   │ └─ ≥ 30: Obese                                      │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Data Storage Structure

```
Log/
├── config.json          (User Profile & Settings)
│   ├── name
│   ├── age
│   ├── sex
│   ├── height
│   ├── weight
│   ├── activity_level
│   ├── calorie_goal
│   ├── protein_goal
│   ├── carbs_goal
│   ├── fat_goal
│   ├── fiber_goal
│   └── bmi
│
├── food_log.csv         (Food Entry History)
│   ├── date
│   ├── time
│   ├── food_name
│   ├── meal_type
│   ├── calories
│   ├── protein
│   ├── carbs
│   └── fat
│
└── weight_log.csv       (Weight Tracking)
    ├── date
    ├── time
    └── weight
```

---

_"Data flows like heat through the furnace."_ 🔥
