  # Azure Data Factory Pokémon ETL Pipeline

This project demonstrates an end-to-end ETL pipeline using Azure Data Factory (ADF), Azure SQL Database, and Power BI to manage and visualize Pokémon data.

---

## 📌 Overview

- **Data Source**: Pokémon dataset (CSV format from Kaggle)
- **Goal**: Extract, Transform, Load (ETL) Pokémon data and update the database when new data is provided.
- **Tools Used**:
  - Azure Portal
  - Azure Blob Storage
  - Azure SQL Database
  - Azure Data Factory (ADF)
  - Power BI
  - VS Code + Azure DB
  - Data Flow Expressions & Data Preview
  - Event Triggering via Blob Storage + Event Grid

---

## ⚙️ Setup Steps

### 1. **Azure Environment Setup**
- Created Azure Account.
- Created a **Storage Account** with:
  - Containers: `raw/input`, `raw/output`
- Uploaded initial Pokémon CSV to `raw/input`.

### 2. **Azure SQL Database**
- Created a logical SQL server and Azure SQL Database.
- Connected using **Azure DB**.
- Created the initial table `Pokedex` with correct schema.

## 📊 Azure SQL Database Schema

This project uses an Azure SQL Database to store and analyze Pokémon data.

### Table: `pokemon`

| Column Name       | Data Type     | Description                                  |
|-------------------|---------------|----------------------------------------------|
| `sno`             | INT (PK, IDENTITY) | Unique auto-incrementing primary key        |
| `National_Number` | INT           | National Pokédex number                      |
| `English_Name`    | VARCHAR(50)   | Pokémon name                                 |
| `Primary_Type`    | VARCHAR(20)   | Primary type (e.g., fire, water)             |
| `Secondary_Type`  | VARCHAR(20)   | Secondary type (nullable)                    |
| `HP`              | INT           | Hit Points                                   |
| `Attack`          | INT           | Attack stat                                  |
| `Defense`         | INT           | Defense stat                                 |
| `Sp_Atk`          | INT           | Special Attack stat                          |
| `Sp_Def`          | INT           | Special Defense stat                         |
| `Speed`           | INT           | Speed stat                                   |
| `Generation`      | INT           | Generation number                            |
| `Legendary`       | BIT           | 1 if Legendary, 0 otherwise                  |
| `Mythical`        | BIT           | 1 if Mythical, 0 otherwise                   |
| `PseudoLegendary` | BIT           | 1 if Pseudo-Legendary, 0 otherwise           |
| `Can_Gigantimax`  | BIT           | 1 if can Gigantimax, 0 otherwise             |
| `Ability_1`       | VARCHAR(50)   | Primary ability                              |
| `Ability_2`       | VARCHAR(50)   | Secondary ability (nullable)                 |
| `Ability_3`       | VARCHAR(50)   | Hidden ability (nullable)                    |

---

**Note:** This schema supports advanced analytics in Power BI and data pipelines in Azure Data Factory.


### 3. **Azure Data Factory (ADF)**
- Created ADF instance.
- Linked services:
  - Azure Blob Storage (for CSVs)
  - Azure SQL Database (for table sink)
- Created Datasets:
  - `updatePokedex` for CSV input.
  - `AzureSqlTable1` for SQL destination.

---

## 🏗️ Data Flow: `updatePokedex`

### Logic:
1. **Source1**: Read from `updatePokedex` CSV (string columns).
2. **Source2**: Read from Azure SQL Table (typed columns).
3. **Derived Column**: Convert datatypes in source1 to match SQL table (e.g., string to int/bool).
4. **Select1**: Narrow down key columns from source2 for join.
5. **Join**: Left join on composite key:
   ```plaintext
   National_Number + Primary_Type + Secondary_Type
   ```
6. **Alter Row**: `updateIf` condition based on match:
   ```plaintext
   updateIf(National_Number == National_Number && Primary_Type == Primary_Type && Secondary_Type == Secondary_Type)
   ```
7. **Sink**: SQL Table with:
   - insertable: false
   - updateable: true
   - keys: [National_Number, Primary_Type, Secondary_Type]

  ## 🏗️ Data Flow: `insertPokedex`

This data flow is used to ingest and normalize raw Pokémon data from a CSV file and insert it into an Azure SQL table.

### Logic:
1. **Source**: Read from raw CSV (`inputFile`) with nested headers and all columns treated as strings.
2. **Select1**: Rename and map raw columns to a clean schema:
   - `{No.}` → `National_Number`
   - `Name` → `English_Name`
   - `Att`, `Def`, `S.Att`, `S.Def`, `Spd` → Stat columns
   - `PrimaryType`, `SecondaryType`, `mega_evolution`, etc.
3. **Aggregate1**: Group by Pokémon attributes and collect all `Ability` values into an array.
4. **DerivedColumn1**: Extract individual abilities and convert evolution flags:
   - `Ability1 = Ability[1]`
   - `Ability2 = Ability[2]`
   - `Ability3 = Ability[3]` (only if available)
   - `Mega_Evolution` → `toBoolean(Mega_Evolution)`
5. **Aggregate2**: Compute `Base_Total` using:
   ```plaintext
   Base_Total = HP + Attack + Defense + Sp_Attack + Sp_Defense + Speed

6. **Lookup1**: Perform a lookup join between DerivedColumn1 and Aggregate2 using National_Number as the key.
   - Joins base stats with computed Base_Total
   - Ensures merged schema for final output

7.**Select2**: Map final column structure with correct data types:
   - Converts values to integer, string, or boolean as required by SQL schema
   - Includes columns like Ability, Ability_2, Ability_3, Base_Total, etc.

8. **Sink**: Write to Azure SQL Table with the following options:
    - insertable: true
    - updateable: false
    - truncate: true (clears old data before insertion)
    - booleanFormat: ['1', '0'] (true/false stored as 1/0)
---

## 🧪 Testing

### Data Preview
- Validated transformations and join behavior.
- Used `toLower(trim(...))` expressions to normalize join keys.

### Debug Runs
- Used `Debug` mode to test flows.
- Previewed records to validate update logic.

---

## 🔁 Automation

### Triggering Pipeline on File Upload:
1. Enabled **Event Grid** on Storage Account.
2. Created **Event Trigger** in ADF:
   - Event Type: `Blob Created`
   - Path: `raw/input/*.csv`
   - Linked to pipeline

Now, any new file uploaded to `raw/input` automatically triggers the ETL pipeline.

---

## 📊 Power BI Visualization
- Connected Power BI to Azure SQL DB.
- Imported `Pokedex` table.
- Created charts, slicers, and summaries.

---

## 🧠 Tips

- 🧼 Normalize data using `trim()` and `toLower()` in ADF expressions to avoid join mismatches.
- 📌 Use `Data Preview` in every step to trace transformation results.
- 🧪 Create a manual trigger to test your pipeline before automating.
- 🧼 Ensure you convert all string values to proper types before writing to SQL.

---

## 🔧 Commands Used

### Azure SQL via AzureDB
```sql
CREATE TABLE Pokedex (
    sno INT PRIMARY KEY,
    National_Number INT,
    English_Name VARCHAR(50),
    Primary_Type VARCHAR(30),
    Secondary_Type VARCHAR(30),
    ...
);
```

### ADF Expressions
```text
toInteger(column), toBoolean(column), toLower(trim(column))
```
## 📊 Power BI Dashboard: Pokémon Analytics

This dashboard visualizes insights from the cleaned Pokémon dataset stored in Azure SQL Database.

### ✅ Features Implemented:

1. **Interactive Data Table**
   - Displays key columns: `National_Number`, `English_Name`, `Gen`, `Types`, `Base_Total`, Stats, and Abilities.
   - Selecting a row filters all other visuals.

2. **Slicer Filters**
   - **Primary Type** and **Secondary Type** slicers allow users to filter Pokémon based on elemental types.
   - **Abilities** slicer dynamically filters Pokémon having that ability across `Ability`, `Ability_2`, or `Ability_3`.

3. **Stat-Based Bar Charts**
   - **Average Base_Total by Primary_Type** and **Secondary_Type**.
   - Enables comparison of strength distribution across Pokémon types.

4. **Pseudo Legendary Table**
   - Lists known pseudo-legendary Pokémon with their generation and names.

5. **Strong Legendary Table**
   - Highlights legendary Pokémon by `Base_Total` over 600 (e.g., Arceus, Eternatus, Lugia, etc.).

### 📐 Data Model & Relationships

- `pokemon`: Main table pulled from Azure SQL.
- `Ability`: unpivoted table for ability-specific visuals.
- `PokemonAbilities`: connection table between Abilities and pokemon via sno
- Slicers and tables interact through relationships:
  - `pokemon[sno]` → `PokemonAbilities[sno]`→ `Ability[Abilities]`
  - Flattened/unioned ability column used for many-to-many filtering.

### 📌 Notes:
- Dashboard is fully interactive.
- Clicking on a Pokémon filters visuals across abilities, and types.
- Useful for identifying trends like:
  - Which types tend to be stronger
  - Ability distribution
  - Power comparison between legendary and regular Pokémon
 
### Demo Image

<img width="1408" height="794" alt="image" src="https://github.com/user-attachments/assets/26377f21-54f0-416a-8cd2-5464ee23fbcd" />


---

## ✅ Final Outcome
- End-to-end pipeline works automatically on file upload.
- SQL table updates existing records based on composite key.
- No duplicate insertions.
- Fully connected to Power BI for reporting.

---

## 📁 Folder Structure

```
project-root/
│
├── data/
│   └── update.csv
│
├── ADF/
│   └── updatePokedex Data Flow
│
├── PowerBI/
│   └── dashboard.pbix
│
└── README.md
```

---

Happy Data Engineering! 🚀
