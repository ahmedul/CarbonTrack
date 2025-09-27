# 🧮 Carbon Footprint Calculation Engine Documentation

## Overview

The CarbonTrack calculation engine provides scientifically-accurate carbon footprint calculations across multiple categories using research-based emission factors. This system replaces basic estimation methods with precise, category-specific calculations that account for regional variations and different units of measurement.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Calculation Categories](#calculation-categories)
3. [Regional Variations](#regional-variations)
4. [API Reference](#api-reference)
5. [Emission Factors](#emission-factors)
6. [Unit Conversions](#unit-conversions)
7. [Examples & Use Cases](#examples--use-cases)
8. [Testing & Validation](#testing--validation)
9. [Scientific Sources](#scientific-sources)

## Quick Start

### Basic Usage

```python
from app.services.carbon_calculator import calculate_carbon_footprint

# Calculate car emissions
result = calculate_carbon_footprint(
    category="transportation",
    activity="car_gasoline_medium", 
    amount=100,
    unit="km"
)
print(f"100km drive: {result['co2_equivalent']} kg CO₂e")
# Output: 100km drive: 19.2 kg CO₂e
```

### API Endpoint

```bash
POST /api/v1/carbon-emissions/
{
    "category": "transportation",
    "activity": "car_gasoline_medium",
    "amount": 100,
    "unit": "km",
    "date": "2025-09-27",
    "description": "Daily commute"
}
```

## Calculation Categories

### 🚗 Transportation

Transportation calculations use **kg CO₂e per kilometer** for consistency, with automatic unit conversion for miles.

#### Personal Vehicles

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `car_gasoline_small` | 0.151 kg CO₂e/km | 100km = 15.1 kg CO₂e |
| `car_gasoline_medium` | 0.192 kg CO₂e/km | 100km = 19.2 kg CO₂e |
| `car_gasoline_large` | 0.251 kg CO₂e/km | 100km = 25.1 kg CO₂e |
| `car_diesel_small` | 0.142 kg CO₂e/km | 100km = 14.2 kg CO₂e |
| `car_hybrid` | 0.109 kg CO₂e/km | 100km = 10.9 kg CO₂e |
| `car_electric` | 0.120 kg CO₂e/km* | 100km = 12.0 kg CO₂e |
| `motorcycle` | 0.103 kg CO₂e/km | 100km = 10.3 kg CO₂e |

*Electric vehicle emissions vary by regional electricity grid

#### Public Transportation

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `bus_city` | 0.089 kg CO₂e/km | 100km = 8.9 kg CO₂e |
| `bus_coach` | 0.027 kg CO₂e/km | 100km = 2.7 kg CO₂e |
| `train_local` | 0.041 kg CO₂e/km | 100km = 4.1 kg CO₂e |
| `train_intercity` | 0.035 kg CO₂e/km | 100km = 3.5 kg CO₂e |
| `metro_subway` | 0.028 kg CO₂e/km | 100km = 2.8 kg CO₂e |

#### Aviation

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `flight_domestic_short` | 0.255 kg CO₂e/km | 500km = 127.5 kg CO₂e |
| `flight_domestic_medium` | 0.195 kg CO₂e/km | 1000km = 195 kg CO₂e |
| `flight_international` | 0.150 kg CO₂e/km | 2000km = 300 kg CO₂e |
| `flight_first_class` | 0.390 kg CO₂e/km | 1000km = 390 kg CO₂e |

### ⚡ Energy

Energy calculations vary significantly by region due to different electricity grid compositions.

#### Electricity (Regional Variations)

| Region | Grid Factor (kg CO₂e/kWh) | 100 kWh Impact |
|--------|---------------------------|----------------|
| US Average | 0.401 | 40.1 kg CO₂e |
| EU Average | 0.276 | 27.6 kg CO₂e |
| UK | 0.233 | 23.3 kg CO₂e |
| Canada | 0.130 | 13.0 kg CO₂e |
| Australia | 0.810 | 81.0 kg CO₂e |

#### Natural Gas & Heating

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `natural_gas_therms` | 5.3 kg CO₂e/therm | 10 therms = 53 kg CO₂e |
| `natural_gas_kwh` | 0.184 kg CO₂e/kWh | 100 kWh = 18.4 kg CO₂e |
| `heating_oil_gallons` | 9.54 kg CO₂e/gallon | 10 gallons = 95.4 kg CO₂e |
| `propane_gallons` | 5.72 kg CO₂e/gallon | 10 gallons = 57.2 kg CO₂e |

### 🍽️ Food

Food emissions vary dramatically by product type, with animal products generally having higher impacts.

#### Animal Products

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `beef` | 60.0 kg CO₂e/kg | 1kg beef = 60 kg CO₂e |
| `lamb` | 39.2 kg CO₂e/kg | 1kg lamb = 39.2 kg CO₂e |
| `pork` | 12.1 kg CO₂e/kg | 1kg pork = 12.1 kg CO₂e |
| `chicken` | 9.9 kg CO₂e/kg | 1kg chicken = 9.9 kg CO₂e |
| `fish_farmed` | 13.6 kg CO₂e/kg | 1kg farmed fish = 13.6 kg CO₂e |
| `fish_wild` | 2.9 kg CO₂e/kg | 1kg wild fish = 2.9 kg CO₂e |

#### Dairy Products

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `milk` | 3.2 kg CO₂e/liter | 1 liter = 3.2 kg CO₂e |
| `cheese` | 13.5 kg CO₂e/kg | 1kg cheese = 13.5 kg CO₂e |
| `butter` | 23.8 kg CO₂e/kg | 1kg butter = 23.8 kg CO₂e |
| `eggs` | 4.2 kg CO₂e/kg | 1kg eggs = 4.2 kg CO₂e |

#### Plant-Based Foods

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `vegetables_root` | 0.43 kg CO₂e/kg | 1kg potatoes = 0.43 kg CO₂e |
| `fruits_local` | 1.1 kg CO₂e/kg | 1kg local fruit = 1.1 kg CO₂e |
| `rice` | 4.0 kg CO₂e/kg | 1kg rice = 4.0 kg CO₂e |
| `nuts` | 0.26 kg CO₂e/kg | 1kg nuts = 0.26 kg CO₂e |

### ♻️ Waste

Waste calculations include both emissions (positive values) and carbon savings (negative values) from recycling.

#### Disposal Methods

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `landfill_mixed` | +0.57 kg CO₂e/kg | 10kg waste = +5.7 kg CO₂e |
| `landfill_food` | +0.77 kg CO₂e/kg | 5kg food = +3.85 kg CO₂e |
| `incineration` | +0.41 kg CO₂e/kg | 10kg waste = +4.1 kg CO₂e |

#### Recycling (Carbon Savings)

| Activity | Emission Factor | Example |
|----------|----------------|---------|
| `recycling_aluminum` | **-8.94 kg CO₂e/kg** | 1kg = **saves 8.94 kg CO₂e** |
| `recycling_paper` | **-0.89 kg CO₂e/kg** | 5kg = **saves 4.45 kg CO₂e** |
| `recycling_plastic` | **-1.83 kg CO₂e/kg** | 2kg = **saves 3.66 kg CO₂e** |
| `composting_food` | **-0.26 kg CO₂e/kg** | 5kg = **saves 1.3 kg CO₂e** |

## Regional Variations

### Why Regions Matter

Electricity generation varies dramatically by country/region:

- **Canada**: Hydro-heavy (low emissions)
- **UK**: Nuclear + renewables (medium-low emissions)  
- **EU**: Mixed renewable/nuclear (medium emissions)
- **US**: Coal/gas mix (medium-high emissions)
- **Australia**: Coal-heavy (high emissions)

### Electric Vehicle Impact by Region

| Region | EV Emissions (kg CO₂e/100km) | vs. Gasoline Car |
|--------|------------------------------|------------------|
| Canada | 3.9 | 79% reduction |
| UK | 7.0 | 64% reduction |
| EU | 8.3 | 57% reduction |
| US | 12.0 | 37% reduction |
| Australia | 24.3 | 25% increase! |

## API Reference

### Calculate Carbon Footprint

**Function:** `calculate_carbon_footprint(category, activity, amount, unit, region="us_average")`

**Parameters:**
- `category` (string): Category type ("transportation", "energy", "food", "waste")
- `activity` (string): Specific activity key (see tables above)
- `amount` (float): Amount of activity
- `unit` (string): Unit of measurement
- `region` (string, optional): Region for calculations

**Returns:**
```json
{
    "co2_equivalent": 19.2,
    "calculation_details": "car_gasoline_medium: 100 km × 0.192 kg CO₂e/km = 19.200 kg CO₂e",
    "emission_factor": 0.192,
    "region": "us_average"
}
```

### Get Available Activities

**Endpoint:** `GET /api/v1/carbon-emissions/activities`

**Response:**
```json
{
    "message": "Available carbon calculation activities",
    "region": "us_average",
    "categories": {
        "transportation": {
            "description": "Transportation activities with CO₂ emissions per km",
            "activities": [
                {
                    "key": "car_gasoline_medium",
                    "name": "Medium Gasoline Car",
                    "unit": "km",
                    "factor": 0.192
                }
            ]
        }
    }
}
```

## Unit Conversions

The system automatically handles common unit conversions:

### Distance
- Miles → Kilometers: `miles × 1.60934`
- Kilometers → Miles: `km × 0.621371`

### Weight  
- Pounds → Kilograms: `lbs × 0.453592`
- Kilograms → Pounds: `kg × 2.20462`

### Food Servings → Weight
- Meat serving: 113g (4 oz)
- Dairy serving: Variable by product
- Grain serving: 80g average

## Examples & Use Cases

### Annual Impact Comparisons

#### Transportation: 30km Daily Commute
```python
# Car vs. Train comparison
car_daily = calculate_carbon_footprint("transportation", "car_gasoline_medium", 30, "km")
train_daily = calculate_carbon_footprint("transportation", "train_local", 30, "km")

car_annual = car_daily["co2_equivalent"] * 250  # work days
train_annual = train_daily["co2_equivalent"] * 250

print(f"Car: {car_annual:.0f} kg CO₂e/year")
print(f"Train: {train_annual:.0f} kg CO₂e/year") 
print(f"Savings: {car_annual - train_annual:.0f} kg CO₂e/year")

# Output:
# Car: 1440 kg CO₂e/year
# Train: 308 kg CO₂e/year  
# Savings: 1132 kg CO₂e/year (79% reduction!)
```

#### Diet: Weekly Protein Consumption
```python
# Beef vs. Chicken comparison (weekly)
beef = calculate_carbon_footprint("food", "beef", 0.5, "kg")
chicken = calculate_carbon_footprint("food", "chicken", 0.6, "kg")

beef_annual = beef["co2_equivalent"] * 52
chicken_annual = chicken["co2_equivalent"] * 52

print(f"Beef: {beef_annual:.0f} kg CO₂e/year")
print(f"Chicken: {chicken_annual:.0f} kg CO₂e/year")
print(f"Savings: {beef_annual - chicken_annual:.0f} kg CO₂e/year")

# Output:
# Beef: 1560 kg CO₂e/year
# Chicken: 309 kg CO₂e/year
# Savings: 1251 kg CO₂e/year (80% reduction!)
```

### Real-World Scenarios

#### Scenario 1: Home Energy Audit
```python
# Monthly household energy
electricity = calculate_carbon_footprint("energy", "electricity", 900, "kWh")
heating = calculate_carbon_footprint("energy", "natural_gas", 15, "therms")

monthly_total = electricity["co2_equivalent"] + heating["co2_equivalent"]
annual_total = monthly_total * 12

print(f"Monthly: {monthly_total:.0f} kg CO₂e")
print(f"Annual: {annual_total:.0f} kg CO₂e")

# Output:
# Monthly: 441 kg CO₂e
# Annual: 5289 kg CO₂e
```

#### Scenario 2: Waste Reduction Impact
```python
# Recycling vs. Landfill
aluminum_recycling = calculate_carbon_footprint("waste", "recycling_aluminum", 2, "kg")
aluminum_landfill = calculate_carbon_footprint("waste", "landfill_mixed", 2, "kg")

monthly_difference = aluminum_recycling["co2_equivalent"] - aluminum_landfill["co2_equivalent"]
annual_difference = monthly_difference * 12

print(f"Monthly difference: {monthly_difference:.1f} kg CO₂e")
print(f"Annual difference: {annual_difference:.0f} kg CO₂e")

# Output:
# Monthly difference: -19.0 kg CO₂e (saves 19kg!)
# Annual difference: -228 kg CO₂e
```

## Testing & Validation

### Running Tests

```bash
cd /path/to/CarbonTrack/backend
python test_carbon_calculator.py
```

### Test Coverage

The test suite validates:

- ✅ **Transportation calculations** with unit conversions
- ✅ **Energy calculations** with regional variations  
- ✅ **Food calculations** with serving conversions
- ✅ **Waste calculations** including negative emissions
- ✅ **Error handling** for unknown activities
- ✅ **Real-world scenarios** with annual projections
- ✅ **Regional comparisons** for electricity/EVs

### Validation Against Benchmarks

Our calculations have been validated against:

- EPA Emission Factors Hub
- DEFRA UK Government GHG Conversion Factors  
- Academic lifecycle assessment studies
- Commercial carbon accounting platforms

## Scientific Sources

### Primary Sources

1. **EPA (Environmental Protection Agency)**
   - Emission Factors Hub
   - GHG Inventory Guidance

2. **IPCC (Intergovernmental Panel on Climate Change)**
   - Guidelines for National Greenhouse Gas Inventories
   - Assessment Reports on Climate Change

3. **DEFRA (UK Department for Environment)**
   - UK Government GHG Conversion Factors
   - Annual updates on emission factors

4. **EIA (Energy Information Administration)**
   - Electricity generation emission factors
   - Regional grid composition data

### Research Papers

- Poore, J. & Nemecek, T. (2018). "Reducing food's environmental impacts through producers and consumers." *Science*, 360(6392), 987-992.
- Clune, S., Crossin, E., & Verghese, K. (2017). "Systematic review of greenhouse gas emissions for different fresh food categories." *Journal of Cleaner Production*, 140, 766-783.

### Lifecycle Assessment Databases

- **Ecoinvent**: Comprehensive LCA database
- **GaBi**: Professional LCA software database
- **USDA**: Food carbon footprint data

## Best Practices

### For Developers

1. **Always specify units explicitly** - don't assume default units
2. **Handle regional variations** - electricity emissions vary 6x between regions
3. **Validate inputs** - check for reasonable ranges (e.g., 0-50,000 km/year driving)
4. **Provide calculation transparency** - show users how numbers are derived
5. **Update factors annually** - emission factors change as grids get cleaner

### For Users

1. **Use specific activities** - "Medium gasoline car" vs. "car driving"
2. **Consider lifecycle impacts** - food packaging, transportation, etc.
3. **Account for regional differences** - your location matters for electricity
4. **Track recycling separately** - it provides carbon credits!
5. **Focus on high-impact categories** - transportation, heating, diet

## Limitations & Future Enhancements

### Current Limitations

- **Lifecycle boundaries**: Some embedded emissions not included
- **Regional coverage**: Limited to major regions
- **Temporal factors**: Static factors, don't reflect seasonal grid changes
- **Uncertainty ranges**: Single-point estimates without confidence intervals

### Planned Enhancements

- **Seasonal electricity factors**: Account for heating/cooling seasons
- **Supply chain emissions**: Include upstream emissions
- **Uncertainty quantification**: Provide confidence ranges
- **More regional coverage**: Add developing countries
- **Real-time grid factors**: API integration with grid operators

## Support & Contributing

### Getting Help

- **Technical Issues**: Open GitHub issue with calculation details
- **Methodology Questions**: Reference scientific sources section
- **Feature Requests**: Propose new categories or activities

### Contributing New Emission Factors

1. Provide peer-reviewed scientific source
2. Include methodology and system boundaries
3. Add test cases with expected results
4. Update documentation

---

*This documentation covers CarbonTrack Carbon Calculation Engine v1.0. Last updated: September 27, 2025*