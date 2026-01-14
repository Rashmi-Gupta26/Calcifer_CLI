# 🔥 Calcifer CLI - State Diagrams

## 1. High-Level Application Flow

```
START
 │
 ├─ Config Exists?
 │   ├─ NO  → ONBOARDING → MAIN_MENU
 │   └─ YES → MAIN_MENU
 │
 └─ EXIT → DAILY_SUMMARY → END
```

## 2. Onboarding Flow

```
ONBOARDING_START
 │
 ├─ Display Banner (1.5s pause)
 ├─ Calcifer Introduction
 │
 ├─ GET_NAME → "What should I call you?"
 ├─ GET_AGE → "How many years...?"
 ├─ GET_SEX → [1] Male [2] Female [3] Prefer not
 ├─ GET_HEIGHT → "How tall? (cm)"
 ├─ GET_WEIGHT → "Weight? (kg)"
 ├─ GET_ACTIVITY → [1-4] Activity level
 │
 ├─ CALCULATE (BMR → TDEE → Macros)
 ├─ DISPLAY_TARGETS
 ├─ SAVE_CONFIG (Log/config.json)
 ├─ LOG_INITIAL_WEIGHT
 │
 └─ → MAIN_MENU
```

## 3. Main Menu State

```
MAIN_MENU
 │
 ├─ 1. Feed the Fire     → LOG_FOOD → MAIN_MENU
 ├─ 2. Weigh the Flame   → LOG_WEIGHT → MAIN_MENU
 ├─ 3. Tune the Furnace  → SETTINGS_MENU → MAIN_MENU
 ├─ 4. Ask Calcifer      → HELP_MENU → MAIN_MENU
 └─ 5. Exit              → DAILY_SUMMARY → END
```

## 4. Food Logging Flow (Feed the Fire)

```
LOG_FOOD
 │
 ├─ GET_FOOD_NAME ("Name the food")
 ├─ SHOW_SPINNER ("🔥 Consulting the flames...")
 ├─ API_SEARCH (USDA → Open Food Facts fallback)
 │   ├─ No Results → Error → MAIN_MENU
 │   └─ Results Found ↓
 │
 ├─ SELECT_FOOD (menu with brand info)
 │   └─ Cancel → MAIN_MENU
 │
 ├─ DISPLAY_FOOD_DETAILS
 │   ├─ Raw Food Data (name, brand, category, source)
 │   └─ Nutritional Info (calories, protein, carbs, sugar, fat, fiber, sodium)
 │
 ├─ GET_SERVING_SIZE ("How many grams?")
 ├─ SCALE_NUTRIENTS (value × serving/100)
 ├─ SELECT_MEAL_TYPE (Breakfast/Lunch/Dinner/Snack)
 ├─ CONFIRM_LOG ("Log this? [Y/n]")
 │   ├─ No → MAIN_MENU
 │   └─ Yes ↓
 │
 ├─ WRITE_TO_CSV (food_log.csv)
 ├─ SHOW_CONFIRMATION + Commentary
 │
 └─ → MAIN_MENU
```

## 5. Weight Logging Flow

```
LOG_WEIGHT
 │
 ├─ DISPLAY_INTRO ("Moment of truth...")
 ├─ GET_WEIGHT ("Enter weight in kg")
 ├─ LOG_TO_CSV (weight_log.csv)
 ├─ UPDATE_CONFIG (weight, BMI)
 ├─ SAVE_CONFIG
 │
 ├─ SHOW_CONFIRMATION
 ├─ COMMENTARY (based on change)
 │   ├─ Increase: "Heavier flame. Happens."
 │   ├─ Decrease: "Lighter. Someone's behaving."
 │   └─ Same: "Stable. I like predictable fires."
 │
 └─ → MAIN_MENU
```

## 6. Settings Menu (Tune the Furnace)

```
SETTINGS_MENU
 │
 ├─ 1. Update Details → UPDATE_DETAILS_SUBMENU
 │   ├─ Age → Update → SAVE
 │   ├─ Height → Update → CALC_BMI → SAVE
 │   ├─ Weight → Update → CALC_BMI → LOG → SAVE
 │   ├─ Gender → Update → SAVE
 │   └─ Back → SETTINGS_MENU
 │
 ├─ 2. Change Activity → SELECT [1-4] → SAVE → SETTINGS_MENU
 ├─ 3. Change Goal → GET_NEW_GOAL → SAVE → SETTINGS_MENU
 ├─ 4. Recalculate → CONFIRM → RECALC_ALL → SAVE → SETTINGS_MENU
 │
 └─ 5. Back → MAIN_MENU
```

## 7. Help Menu (Ask Calcifer)

```
HELP_MENU
 │
 ├─ 1. Today's Status
 │   └─ Display: Calories, BMI, Weight, Activity
 │
 ├─ 2. What does BMI mean?
 │   └─ "BMI is a blunt tool. Useful, not sacred."
 │
 ├─ 3. How are calories calculated?
 │   └─ "I calculate your base burn. Then I factor movement."
 │
 ├─ 4. How to use daily?
 │   └─ "Log what you eat • Check in • Don't obsess • Be consistent"
 │
 └─ 5. Back → MAIN_MENU
```

## 8. Exit Flow

```
EXIT_REQUEST (Menu or Ctrl+C)
 │
 ├─ LOAD_TODAY_DATA (calories, weight, BMI)
 │
 ├─ DISPLAY_SUMMARY
 │   └─ 🔥 Daily Fire Report — {date}
 │       • Calories: {current} / {goal}
 │       • Status: {status}
 │       • BMI: {value} ({category})
 │       • Last Weight: {weight} kg
 │
 ├─ CLOSING_COMMENTARY (based on ratio)
 │   ├─ ratio < 0.7: "The fire's still hungry."
 │   ├─ 0.7 ≤ r ≤ 1.1: "Now that's a controlled burn."
 │   └─ ratio > 1.1: "We survived. Tomorrow, less chaos."
 │
 ├─ GOODBYE_MESSAGE
 │   └─ "Rest up, {name}. I'll keep the embers warm."
 │
 └─ END
```

---

_"If Calcifer always knows what state he's in, the fire never gets out of control."_ 🔥
