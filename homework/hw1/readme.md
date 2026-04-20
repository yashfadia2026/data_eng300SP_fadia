# Homework 1 — BTS Schedule B-43 Aircraft Inventory

## Repository structure
homework_1/
├── readme.md
├── homework_1.ipynb
└── homework_1.html

## Requirements
pip install pandas numpy scipy scikit-learn miceforest seaborn matplotlib

## Data
Download T_F41SCHEDULE_B43.csv from the BTS TranStats database and place it 
in the homework_1/ folder before running the notebook.

## How to run
1. Clone the repository
2. Install dependencies
3. Place T_F41SCHEDULE_B43.csv in the homework_1/ folder
4. Open homework_1.ipynb in VS Code or Jupyter
5. Run all cells from top to bottom in order

## Expected outputs
- Missing data summary across all columns
- Imputed dataset with 0 missing values across all in-scope columns
- Standardised MANUFACTURER column (183 → 86 unique values)
- Standardised MODEL column (1,340 → 1,121 unique values)
- Dataset after dropping remaining missing rows: 100,665 rows retained (76.1%)
- Box-Cox transformed columns: NUMBER_OF_SEATS_BOXCOX, CAPACITY_IN_POUNDS_BOXCOX
- SIZE feature column with categories: SMALL, MEDIUM, LARGE, XLARGE
- Four model RMSE results:

| Model             | Target             | Train RMSE | Test RMSE  |
|-------------------|--------------------|------------|------------|
| Linear Regression | NUMBER_OF_SEATS    | 57.4658    | 57.8696    |
| Linear Regression | CAPACITY_IN_POUNDS | 81,886.61  | 81,693.23  |
| Random Forest     | NUMBER_OF_SEATS    | 13.1275    | 16.1397    |
| Random Forest     | CAPACITY_IN_POUNDS | 9,800.38   | 13,354.36  |