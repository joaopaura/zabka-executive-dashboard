# Żabka Group | Executive Dashboard | Synthetic Dataset

> Hypothetical data for executive dashboard demonstration purposes only. Not affiliated with Żabka Group.

- **Period:** Actuals Jan 2023 to Aug 2026 | Budget Jan 2023 to Dec 2026
- **Currency:** PLN | **Network:** sample of 1,000 stores (972 active at Aug 2026)
- **Encoding:** UTF-8 | **Delimiter:** comma | **Decimal:** dot (in Power Query, set Locale = English (United States))

## Relationships (star schema)

| From (many) | To (one) | Key |
|---|---|---|
| FactDailySales | DimDate | Date |
| FactDailySales | DimStore | StoreID |
| FactCategorySales | DimDate | MonthStart → Date |
| FactCategorySales | DimStore | StoreID |
| FactCategorySales | DimCategory | CategoryID |
| FactStoreOpex | DimDate | MonthStart → Date |
| FactStoreOpex | DimStore | StoreID |
| FactBudget | DimDate | MonthStart → Date |
| FactBudget | DimRegion | RegionID |
| FactBudget | DimCategory | CategoryID |
| FactAppMetrics | DimDate | MonthStart → Date |
| FactAppMetrics | DimRegion | RegionID |
| DimStore | DimRegion | RegionID (snowflake, filters stores by region) |
| DimStore | DimFranchisee | FranchiseeID |

Monthly facts join on the first day of the month, so analyse them at Month level or above.

## Fact tables

### FactDailySales | grain: Store × Day | ~1.17M rows
| Column | Description |
|---|---|
| Date | Transaction date |
| StoreID | Store key |
| NetSales | Net sales excl. VAT (PLN) |
| COGS | Cost of goods sold (PLN) |
| GrossProfit | NetSales − COGS |
| Transactions | Number of receipts |
| ItemsSold | Number of items scanned |
| AppTransactions | Receipts linked to the Żappka app |
| AppSales | Net sales from app-linked receipts |
| PromoSales | Net sales sold under promotion |

### FactCategorySales | grain: Store × Month × Category | ~463k rows
| Column | Description |
|---|---|
| MonthStart | First day of the month |
| StoreID / CategoryID | Keys |
| NetSales / GrossProfit | Reconciles with FactDailySales at store-month level |
| UnitsSold | Units sold |
| WasteValue | Value of written-off products (PLN) |
| PrivateLabelSales | Sales of own-brand products |

### FactBudget | grain: Region × Month × Category | 2,880 rows
| Column | Description |
|---|---|
| BudgetNetSales / BudgetGrossProfit | Approved budget (PLN), full year 2026 included |

### FactStoreOpex | grain: Store × Month | ~38k rows
| Column | Description |
|---|---|
| OpenDays | Days the store traded in the month |
| RentCost, EnergyCost, FranchiseeCommission, MarketingCost, TechnologyCost, OtherOpex | Store operating costs (PLN). Store EBITDA = GrossProfit − sum of these |

### FactAppMetrics | grain: Region × Month | 220 rows
| Column | Description |
|---|---|
| RegisteredUsers | Cumulative registered app users (end of month) |
| MonthlyActiveUsers | Users with at least one app transaction in the month |
| NewRegistrations | Gross new sign-ups in the month |
| CouponsRedeemed | App coupons redeemed |
| AppRating | Average app store rating |

## Dimension tables

| Table | Rows | Main columns |
|---|---|---|
| DimDate | 1,461 | Date, Year, Quarter, MonthName, YearMonth, ISOWeek, DayName, IsWeekend, IsHoliday, HolidayName, IsTradingSunday, IsNonTradingSunday, Season, IsActualPeriod |
| DimStore | 1,000 | StoreID, StoreName, FranchiseeID, Format (Standard / Nano / Travel), OperatingModel, LocationType, City, Voivodeship, Region, Latitude, Longitude, SalesAreaSqm, OpeningDate, ClosingDate, Status, StoreCohort, IsSeasideCity |
| DimFranchisee | 822 | FranchiseeID, JoinDate, CohortYear, TenureBand, Tier (Gold / Silver / Bronze / Company), NumberOfStores, IsMultiStore |
| DimCategory | 12 | CategoryID, Category, CategoryGroup, TargetGrossMargin, IsFresh, IsStrategicGrowth, SortOrder |
| DimRegion | 5 | RegionID, Region (Central, South, West, North, East), RegionalDirector, RegionalHQ |

## Built-in business stories (what the dashboard should reveal)

1. **Sunday trading ban advantage:** non-trading Sundays outperform weekdays, while trading Sundays fall about 20%.
2. **Inflation 2023:** basket size rises and gross margin is squeezed in H1 2023, then recovers.
3. **Food-to-go shift:** Ready Meals and Coffee gain share, Tobacco declines structurally, and the mix lifts gross margin.
4. **Żappka growth:** app share of transactions grows from ~32% to ~48%, and app baskets are ~20% higher.
5. **Nano format:** highest sales per sqm in the network.
6. **Store maturity:** new stores ramp up over 12 to 18 months.
7. **East region misses budget** by ~7% from 2025 onward.
8. **North seaside summer peak:** above budget in Jun to Aug.
9. **Waste reduction:** fresh waste falls about 25% from 2023 to 2026 (forecasting initiative).
10. **Private label** share grows from ~20% to ~28%.
11. **Franchisee tier effect:** Gold franchisees sell more and waste less than Bronze.
