# Żabka Group | Executive Performance Dashboard

**Power BI executive dashboard for a leading Polish convenience retailer, covering sales and profitability, store network expansion and digital (app) performance.**

> ⚠️ **Hypothetical data for executive dashboard demonstration purposes only.** Independent portfolio project, not affiliated with Żabka Group. All figures are synthetic.

![Cover](docs/images/01_cover.png)

---

## 🎯 Business context

Żabka operates a large franchise network of convenience stores in Poland, a fast-growing autonomous format (Żabka Nano) and a loyalty app (Żappka). This dashboard answers the questions a **C-level / Board audience** asks every month:

| Page | Key question |
|---|---|
| **01 Sales & Profitability** | Are we growing profitably and delivering the budget? |
| **02 Store Network & Franchise** | Is the network expanding in the right places and formats? |
| **03 Digital & Customer** | Is the Żappka app changing how customers shop? |

---

## 📊 Dashboard pages

### 01 | Sales & Profitability
![Sales & Profitability](docs/images/02_sales.png)

6 KPIs (Net Sales, LFL Growth, Gross Margin, Store EBITDA Margin, Avg Basket, Sales vs Budget) | Monthly trend CY vs PY with YoY % | Growth bridge by region (waterfall) | Budget delivery by region with 3-band traffic lights | Category performance table (mix, growth, margin, private label, waste)

### 02 | Store Network & Franchise
![Store Network](docs/images/03_network.png)

Store map (Azure Maps, 1,000 stores) | Quarterly openings vs closures with active store count | Regional scorecard | Sales per sqm by format | Franchisee tier performance (sales vs fresh waste)

### 03 | Digital & Customer
![Digital & Customer](docs/images/04_digital.png)

App adoption trend (MAU and app transaction share) | App vs non-app basket | Weekly shopping heatmap (weekday x month) | App share by region and format

---

## 💡 Key insights (2026 YTD)

- **Profitable growth:** Net sales +12.8% YoY, with gross margin +1.0 pp and store EBITDA margin +1.1 pp.
- **One region drives the budget miss:** East is -7.6% vs budget (network -1.3%), with the lowest growth, lowest sales per store and lowest app adoption.
- **Food-to-go is the growth engine:** Ready Meals (+25%) and Coffee (+23%) grow fastest and carry the highest margins, while Tobacco grows only +3.4%.
- **Nano is the most productive format:** 372 PLN per sqm per day (about 3x a standard store), yet only 3.1% of sales. A clear expansion opportunity.
- **Franchisee quality matters:** Gold franchisees sell about 14% more per store and waste about 30% less fresh product than Bronze.
- **The app lifts the basket:** 48% of transactions are app-linked (+3.1 pp), and app baskets are 20% larger than non-app baskets.
- **Sunday trading ban advantage:** convenience stores sell 5.6% more on non-trading Sundays than on regular weekdays.

---

## 🧱 Data model

Star schema with 5 fact tables at different grains and 5 conformed dimensions.

![Data model](docs/images/05_data_model.png)

| Table | Grain | Rows |
|---|---|---|
| FactDailySales | Store x Day | ~1.17M |
| FactCategorySales | Store x Month x Category | ~463K |
| FactStoreOpex | Store x Month | ~38K |
| FactBudget | Region x Month x Category | 2,880 |
| FactAppMetrics | Region x Month | 220 |
| DimDate, DimStore, DimRegion, DimFranchisee, DimCategory | | |

Full data dictionary: [docs/Data_Dictionary.md](docs/Data_Dictionary.md)

---

## 🧮 DAX highlights (137 measures)

All measures live in a dedicated `_Measures` table, organized in display folders (Base, Sales, Profitability, Time Intelligence, Budget, Category, Store Network, Digital, Formatting) and deployed through a **TMDL script** ([dax/Zabka_Measures.tmdl](dax/Zabka_Measures.tmdl)).

**Comparable prior-year logic** | PY only uses the same actual days and returns blank when the prior period is not fully covered by data:

```dax
Net Sales PY =
IF (
    EDATE ( MIN ( DimDate[Date] ), -12 ) < [First Actual Date],
    BLANK (),
    CALCULATE (
        [Net Sales],
        CALCULATETABLE ( DATEADD ( DimDate[Date], -1, YEAR ), DimDate[IsActualPeriod] = 1 )
    )
)
```

**Like-for-like growth** | only stores open 12+ months before the period and still trading:

```dax
LFL Growth % =
VAR _Start = MIN ( DimDate[Date] )
VAR _End = MIN ( MAX ( DimDate[Date] ), [Last Actual Date] )
VAR _Stores =
    FILTER (
        DimStore,
        DimStore[OpeningDate] <= EDATE ( _Start, -12 )
            && ( ISBLANK ( DimStore[ClosingDate] ) || DimStore[ClosingDate] > _End )
    )
VAR _Current = CALCULATE ( [Net Sales], _Stores )
VAR _Previous = CALCULATE ( [Net Sales PY], _Stores )
RETURN DIVIDE ( _Current - _Previous, _Previous )
```

**FY outlook** | YTD actuals plus budget for the remaining months:

```dax
FY Outlook =
VAR _Year = MAX ( DimDate[Year] )
VAR _Actual = CALCULATE ( [Category Sales], ALL ( DimDate ), DimDate[Year] = _Year )
VAR _Remaining = CALCULATE ( [Budget Net Sales], ALL ( DimDate ), DimDate[Year] = _Year, DimDate[IsActualPeriod] = 0 )
RETURN _Actual + _Remaining
```

Other techniques: semi-additive measures (registered users, MAU), grain-aware budget guard (blank when filtered below budget grain), dynamic colour and arrow-label measures for conditional formatting, and store network measures based on opening and closing dates.

---

## 🔄 Power Query

- Single text parameter **`ProjectPath`** drives every source, so the project is portable.
- `FactDailySales` combines all CSVs in a folder, so new periods load automatically.
- Explicit column types with `en-US` culture, independent of the machine locale.

M code for each query: [powerquery/](powerquery/)

---

## 🎨 Design system

- Custom **theme JSON** built on the brand green (`#01672C`) | [design/Zabka_Theme.json](design/Zabka_Theme.json)
- Page backgrounds designed at **1920 x 1080** | [design/backgrounds/](design/backgrounds/)
- Consistent colour semantics: current year green, prior year and budget grey, favourable / watch / unfavourable as green / amber / red
- Synced slicers across pages, page navigation buttons, edited visual interactions for long-term trend charts

---

## 📁 Repository structure

```
├── report/          Power BI Project (.pbip)
├── data/            Synthetic CSV dataset (zipped)
├── dax/             TMDL script with all 137 measures
├── powerquery/      M code for every query
├── design/          Theme JSON and page backgrounds
├── docs/            Data dictionary and screenshots
└── scripts/         Python generator for the synthetic dataset
```

---

## ▶️ How to open

1. Extract the files in `data/` so the folder looks like `...\Zabka\Data\*.csv` and `...\Zabka\DailySales\*.csv`.
2. Open `report/Zabka_Executive_Dashboard.pbip` in Power BI Desktop.
3. Go to **Transform data > Manage Parameters** and set **ProjectPath** to your `...\Zabka\` folder (with a trailing backslash).
4. Click **Refresh**.

To regenerate the dataset: `pip install numpy pandas` then `python scripts/generate_dataset.py`.

---

## 🛠️ Tech stack

Power BI Desktop | DAX | Power Query (M) | TMDL | Power BI Project (PBIP) | Azure Maps | Python (NumPy, pandas) for synthetic data

---

## 👤 Author

**João Paúra** | Senior Data Analyst | BI Specialist

[LinkedIn](https://www.linkedin.com/in/joaopaura/) | [Portfolio](jpanalysis.pages.dev)
