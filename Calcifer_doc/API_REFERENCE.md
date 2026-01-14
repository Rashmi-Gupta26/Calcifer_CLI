# 🔥 Calcifer CLI - API Reference

## Overview

Calcifer uses two external APIs for food nutrition data with an automatic fallback mechanism.

---

## 1. USDA FoodData Central API

### Endpoint

```
GET https://api.nal.usda.gov/fdc/v1/foods/search
```

### Authentication

- **API Key Required**: Yes
- **Key Location**: Query parameter `api_key`

### Request Parameters

| Parameter  | Type   | Description                    |
| ---------- | ------ | ------------------------------ |
| `api_key`  | string | Your USDA API key              |
| `query`    | string | Food search term               |
| `pageSize` | int    | Number of results (default: 5) |

### Response Fields Used

| Field           | Description                |
| --------------- | -------------------------- |
| `description`   | Food name                  |
| `brandName`     | Brand name (if applicable) |
| `brandOwner`    | Brand owner                |
| `foodCategory`  | Food category              |
| `foodNutrients` | Array of nutrient data     |

### Nutrient Mapping

| API Field                      | Internal Field |
| ------------------------------ | -------------- |
| `Energy`                       | calories       |
| `Protein`                      | protein        |
| `Carbohydrate, by difference`  | carbs          |
| `Total lipid (fat)`            | fat            |
| `Fiber, total dietary`         | fiber          |
| `Sugars, total including NLEA` | sugar          |
| `Sodium, Na`                   | sodium         |

### Example Request

```bash
curl "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=YOUR_KEY&query=apple&pageSize=5"
```

---

## 2. Open Food Facts API

### Endpoint

```
GET https://world.openfoodfacts.org/cgi/search.pl
```

### Authentication

- **API Key Required**: No

### Request Parameters

| Parameter       | Type   | Description           |
| --------------- | ------ | --------------------- |
| `search_terms`  | string | Food search term      |
| `search_simple` | int    | Use simple search (1) |
| `action`        | string | Set to "process"      |
| `json`          | int    | Return JSON (1)       |
| `page_size`     | int    | Number of results     |

### Response Fields Used

| Field             | Description             |
| ----------------- | ----------------------- |
| `product_name`    | Food name               |
| `brands`          | Brand name              |
| `categories_tags` | Category tags array     |
| `nutriments`      | Nutritional data object |

### Nutrient Mapping

| API Field            | Internal Field |
| -------------------- | -------------- |
| `energy-kcal_100g`   | calories       |
| `proteins_100g`      | protein        |
| `carbohydrates_100g` | carbs          |
| `fat_100g`           | fat            |
| `fiber_100g`         | fiber          |
| `sugars_100g`        | sugar          |
| `sodium_100g`        | sodium         |

### Example Request

```bash
curl "https://world.openfoodfacts.org/cgi/search.pl?search_terms=apple&search_simple=1&action=process&json=1&page_size=5"
```

---

## 3. API Selection Logic

```
1. User enters food name
2. Query USDA API
3. If USDA returns results → Use USDA data
4. If USDA returns empty → Query Open Food Facts
5. If both fail → Show error message
```

---

## 4. Data Normalization

All API responses are normalized to this internal format:

```json
{
  "name": "Food Name",
  "brand": "Brand Name",
  "category": "Food Category",
  "source": "USDA or Open Food Facts",
  "calories": 0.0,
  "protein": 0.0,
  "carbs": 0.0,
  "fat": 0.0,
  "fiber": 0.0,
  "sugar": 0.0,
  "sodium": 0.0,
  "serving_size": 100,
  "serving_unit": "g"
}
```

---

## 5. Rate Limits & Timeouts

| Setting         | Value               |
| --------------- | ------------------- |
| Request Timeout | 10 seconds          |
| USDA Rate Limit | 3,600 requests/hour |
| OFF Rate Limit  | No strict limit     |

---

## 6. Error Handling

| Error               | Handling                    |
| ------------------- | --------------------------- |
| Network timeout     | Show error, prompt retry    |
| API error (4xx/5xx) | Fallback to second API      |
| No results          | Display "not found" message |
| Invalid response    | Skip entry, try next        |

---

_"The APIs fuel the fire with data."_ 🔥
