"""Synthetic data generator for the Zabka Executive Dashboard.
Creates 10 CSV files (star schema) with realistic retail patterns.
Requirements: python 3.10+, numpy, pandas. Run: python generate_dataset.py
"""
import numpy as np, pandas as pd, os
from datetime import date, timedelta
rng = np.random.default_rng(42)
OUT = "Zabka_Dataset"  # output folder (relative)
os.makedirs(OUT, exist_ok=True)
def save(df, name): df.to_csv(f"{OUT}/{name}.csv", index=False, encoding="utf-8-sig")

# ---------------- DATES ----------------
START, END_ACT, END_BUD = pd.Timestamp("2023-01-01"), pd.Timestamp("2026-08-31"), pd.Timestamp("2026-12-31")
dates = pd.date_range(START, END_BUD, freq="D"); ND = len(dates)
n_act = int((END_ACT - START).days) + 1
easter = {2023:"2023-04-09",2024:"2024-03-31",2025:"2025-04-20",2026:"2026-04-05"}
hol = {}
for y,e in easter.items():
    e = pd.Timestamp(e)
    hol.update({pd.Timestamp(f"{y}-01-01"):"New Year's Day", pd.Timestamp(f"{y}-01-06"):"Epiphany",
        e:"Easter Sunday", e+timedelta(1):"Easter Monday", pd.Timestamp(f"{y}-05-01"):"Labour Day",
        pd.Timestamp(f"{y}-05-03"):"Constitution Day", e+timedelta(49):"Pentecost Sunday",
        e+timedelta(60):"Corpus Christi", pd.Timestamp(f"{y}-08-15"):"Assumption Day",
        pd.Timestamp(f"{y}-11-01"):"All Saints' Day", pd.Timestamp(f"{y}-11-11"):"Independence Day",
        pd.Timestamp(f"{y}-12-25"):"Christmas Day", pd.Timestamp(f"{y}-12-26"):"Second Day of Christmas"})
    if y >= 2025: hol[pd.Timestamp(f"{y}-12-24")] = "Christmas Eve"
# trading Sundays (simplified rule set)
trading = set()
for y,e in easter.items():
    e = pd.Timestamp(e)
    for m in (1,4,6,8):
        last = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0)
        trading.add(last - timedelta((last.weekday()+1) % 7))
    trading.add(e - timedelta(7))
    xmas = pd.Timestamp(f"{y}-12-24"); s = xmas - timedelta((xmas.weekday()+1) % 7)
    if s == xmas: s -= timedelta(7)
    for k in range(3 if y >= 2025 else 2): trading.add(s - timedelta(7*k))
dim_date = pd.DataFrame({"Date": dates})
d = dim_date["Date"]
iso = d.dt.isocalendar()
dim_date = dim_date.assign(
    DateKey=d.dt.strftime("%Y%m%d").astype(int), Year=d.dt.year, Quarter=d.dt.quarter,
    QuarterLabel="Q"+d.dt.quarter.astype(str), YearQuarter=d.dt.year.astype(str)+"-Q"+d.dt.quarter.astype(str),
    MonthNumber=d.dt.month, MonthName=d.dt.strftime("%B"), MonthShort=d.dt.strftime("%b"),
    YearMonth=d.dt.strftime("%Y-%m"), YearMonthNumber=d.dt.year*100+d.dt.month,
    MonthStart=d.dt.to_period("M").dt.start_time.dt.date,
    ISOWeek=iso.week.astype(int), ISOYear=iso.year.astype(int), DayOfMonth=d.dt.day,
    DayOfWeekNumber=d.dt.weekday+1, DayName=d.dt.strftime("%A"), DayShort=d.dt.strftime("%a"),
    IsWeekend=(d.dt.weekday>=5).astype(int),
    IsHoliday=d.isin(list(hol)).astype(int), HolidayName=d.map(hol).fillna(""),
    IsSunday=(d.dt.weekday==6).astype(int))
dim_date["IsTradingSunday"] = ((dim_date.IsSunday==1) & d.isin(list(trading))).astype(int)
dim_date["IsNonTradingSunday"] = ((dim_date.IsSunday==1) & (dim_date.IsTradingSunday==0)).astype(int)
dim_date["Season"] = d.dt.month.map({12:"Winter",1:"Winter",2:"Winter",3:"Spring",4:"Spring",5:"Spring",6:"Summer",7:"Summer",8:"Summer",9:"Autumn",10:"Autumn",11:"Autumn"})
dim_date["IsActualPeriod"] = (d <= END_ACT).astype(int)
dim_date["Date"] = d.dt.date
save(dim_date, "DimDate")

# ---------------- REGIONS / GEO ----------------
regions = pd.DataFrame({"RegionID":["R1","R2","R3","R4","R5"],
    "Region":["Central","South","West","North","East"],
    "RegionalDirector":["Director Central","Director South","Director West","Director North","Director East"],
    "RegionalHQ":["Warszawa","Kraków","Poznań","Gdańsk","Lublin"]})
save(regions, "DimRegion")
geo = [ # voivodeship, region, [(city, lat, lon, weight)]
 ("Mazowieckie","R1",[("Warszawa",52.2297,21.0122,10),("Radom",51.4027,21.1471,1.2),("Płock",52.5463,19.7065,1)]),
 ("Łódzkie","R1",[("Łódź",51.7592,19.4560,4),("Piotrków Trybunalski",51.4052,19.7030,0.8)]),
 ("Małopolskie","R2",[("Kraków",50.0647,19.9450,6),("Tarnów",50.0121,20.9858,1),("Nowy Sącz",49.6175,20.7153,0.8)]),
 ("Śląskie","R2",[("Katowice",50.2649,19.0238,4),("Gliwice",50.2945,18.6714,1.5),("Częstochowa",50.8118,19.1203,1.3),("Bielsko-Biała",49.8224,19.0584,1.2)]),
 ("Świętokrzyskie","R2",[("Kielce",50.8661,20.6286,1.5)]),
 ("Podkarpackie","R2",[("Rzeszów",50.0412,21.9991,2),("Przemyśl",49.7838,22.7678,0.6)]),
 ("Wielkopolskie","R3",[("Poznań",52.4064,16.9252,5),("Kalisz",51.7611,18.0910,1),("Konin",52.2230,18.2511,0.7)]),
 ("Dolnośląskie","R3",[("Wrocław",51.1079,17.0385,6),("Wałbrzych",50.7714,16.2843,1),("Legnica",51.2070,16.1553,0.9)]),
 ("Lubuskie","R3",[("Zielona Góra",51.9356,15.5062,1.2),("Gorzów Wielkopolski",52.7368,15.2288,1)]),
 ("Opolskie","R3",[("Opole",50.6751,17.9213,1.3)]),
 ("Pomorskie","R4",[("Gdańsk",54.3520,18.6466,4),("Gdynia",54.5189,18.5305,2),("Sopot",54.4418,18.5601,0.8),("Słupsk",54.4641,17.0285,0.7)]),
 ("Zachodniopomorskie","R4",[("Szczecin",53.4285,14.5528,3),("Koszalin",54.1943,16.1715,0.9),("Kołobrzeg",54.1760,15.5830,0.6)]),
 ("Kujawsko-Pomorskie","R4",[("Bydgoszcz",53.1235,18.0084,2.5),("Toruń",53.0138,18.5984,2)]),
 ("Warmińsko-Mazurskie","R4",[("Olsztyn",53.7784,20.4801,1.8),("Elbląg",54.1522,19.4088,0.8)]),
 ("Lubelskie","R5",[("Lublin",51.2465,22.5684,3),("Zamość",50.7231,23.2520,0.7),("Chełm",51.1431,23.4716,0.6)]),
 ("Podlaskie","R5",[("Białystok",53.1325,23.1688,2.2),("Suwałki",54.1118,22.9309,0.6)]),
]
cities = [(v,r,c,la,lo,w) for v,r,cl in geo for (c,la,lo,w) in cl]
cw = np.array([x[5] for x in cities]); cw = cw/cw.sum()
SEASIDE = {"Gdańsk","Gdynia","Sopot","Kołobrzeg","Słupsk","Koszalin"}

# ---------------- STORES ----------------
NS = 1000
n_open = {2023:70, 2024:72, 2025:62, 2026:36}; n_pre = NS - sum(n_open.values())
open_dates = list(pd.to_datetime(rng.integers(pd.Timestamp("2010-01-01").value//10**9, pd.Timestamp("2022-12-31").value//10**9, n_pre), unit="s").normalize())
for y,n in n_open.items():
    endy = pd.Timestamp("2026-08-31") if y==2026 else pd.Timestamp(f"{y}-12-31")
    days = (endy - pd.Timestamp(f"{y}-01-01")).days
    open_dates += [pd.Timestamp(f"{y}-01-01")+timedelta(int(x)) for x in rng.integers(0, days, n)]
open_dates = pd.to_datetime(open_dates)
is_new = np.array([od.year>=2023 for od in open_dates])
fmt = np.where(is_new, rng.choice(["Standard","Nano","Travel"], NS, p=[0.66,0.24,0.10]),
                        rng.choice(["Standard","Travel"], NS, p=[0.93,0.07]))
loc = np.empty(NS, dtype=object)
for i in range(NS):
    if fmt[i]=="Nano": loc[i] = rng.choice(["Urban","Transit"], p=[0.6,0.4])
    elif fmt[i]=="Travel": loc[i] = "Transit"
    else: loc[i] = rng.choice(["Urban","Suburban","Rural","Transit"], p=[0.50,0.28,0.17,0.05])
ci = rng.choice(len(cities), NS, p=cw)
sqm = np.where(fmt=="Nano", rng.uniform(14,24,NS), np.where(fmt=="Travel", rng.uniform(30,60,NS), rng.uniform(55,110,NS))).round(0)
# franchisees
fr_ids = []; fid = 0; i = 0
order = rng.permutation(NS)
store_fr = np.empty(NS, dtype=object)
while i < NS:
    k = rng.choice([1,2,3], p=[0.86,0.11,0.03]); fid += 1
    for j in order[i:i+k]: store_fr[j] = f"FR-{fid:04d}"
    i += k
NF = fid
tier_of = dict(zip([f"FR-{x:04d}" for x in range(1,NF+1)], rng.choice(["Gold","Silver","Bronze"], NF, p=[0.22,0.53,0.25])))
tier = np.array([tier_of[f] for f in store_fr])
# store economics
base_fmt = {"Standard":7300,"Nano":4300,"Travel":7600}
loc_mult = {"Urban":1.08,"Suburban":0.95,"Rural":0.78,"Transit":1.20}
tier_mult = {"Gold":1.09,"Silver":1.0,"Bronze":0.91}
city_mult = np.array([1.12 if cities[c][2] in ("Warszawa","Kraków","Wrocław","Gdańsk","Poznań") else 1.0 for c in ci])
store_eff = rng.lognormal(0, 0.17, NS)
base = np.array([base_fmt[f] for f in fmt]) * np.array([loc_mult[l] for l in loc]) * np.array([tier_mult[t] for t in tier]) * city_mult * store_eff
# closures: 28 weakest pre-2023 stores
pre_idx = np.where(~is_new)[0]
closing = pd.Series([pd.NaT]*NS)
weak = pre_idx[np.argsort(base[pre_idx])[:28]]
for j in weak: closing[j] = pd.Timestamp("2023-03-01") + timedelta(int(rng.integers(0, 1250)))
region_id = np.array([cities[c][1] for c in ci])
rmap = dict(zip(regions.RegionID, regions.Region))
dim_store = pd.DataFrame({
  "StoreID":[f"ZB{i+1:04d}" for i in range(NS)],
  "StoreName":[f"Żabka {cities[c][2]} #{i+1:04d}" for i,c in enumerate(ci)],
  "FranchiseeID":store_fr, "Format":fmt, "LocationType":loc,
  "City":[cities[c][2] for c in ci], "Voivodeship":[cities[c][0] for c in ci],
  "RegionID":region_id, "Region":[rmap[r] for r in region_id],
  "Latitude":[round(cities[c][3]+rng.normal(0,0.03),5) for c in ci],
  "Longitude":[round(cities[c][4]+rng.normal(0,0.045),5) for c in ci],
  "SalesAreaSqm":sqm.astype(int), "OpeningDate":open_dates.date,
  "OpeningYear":open_dates.year, "ClosingDate":[x.date() if pd.notna(x) else None for x in closing],
})
dim_store["Status"] = np.where(closing.notna() & (closing <= END_ACT), "Closed", "Active")
dim_store["StoreCohort"] = np.where(open_dates.year < 2023, "Pre-2023", open_dates.year.astype(str))
dim_store["IsSeasideCity"] = dim_store.City.isin(SEASIDE).astype(int)
# refurbishments (closed 7-14 days)
refurb = {}
for j in rng.choice(pre_idx, 60, replace=False):
    s = pd.Timestamp("2023-02-01")+timedelta(int(rng.integers(0,1200)))
    refurb[j] = (s, s+timedelta(int(rng.integers(7,15))))

# ---------------- TIME FACTORS ----------------
dd = pd.DatetimeIndex(dates); mon = dd.month.values; yr = dd.year.values; wd = dd.weekday.values
tfrac = (dd - START).days.values/365.25
# price index (inflation): monthly compounding
infl = {2023:0.105,2024:0.042,2025:0.038,2026:0.032}
price = np.cumprod(np.array([(1+infl[y])**(1/365.25) for y in yr])) * 1.0
vol = np.cumprod(np.array([(1+{2023:-0.012,2024:0.022,2025:0.031,2026:0.026}[y])**(1/365.25) for y in yr]))
season = {"Standard":[0.88,0.87,0.94,1.0,1.05,1.10,1.14,1.13,1.0,0.97,0.93,1.03],
          "Transit":[0.86,0.86,0.93,1.0,1.06,1.14,1.22,1.21,1.02,0.97,0.92,1.02]}
dow = {"Urban":[0.94,0.95,0.97,1.0,1.13,1.10,0.91],"Suburban":[0.92,0.93,0.95,0.99,1.12,1.14,0.95],
       "Rural":[0.93,0.93,0.95,0.99,1.12,1.16,0.92],"Transit":[1.08,1.08,1.09,1.10,1.12,0.84,0.69]}
is_sun = wd==6; tradS = dd.isin(list(trading)); holS = dd.isin(list(hol))
sunday_f = np.where(is_sun & ~tradS & ~holS, 1.24, np.where(is_sun & tradS, 0.92, 1.0))
hol_f = np.ones(ND)
for k,v in hol.items():
    idx = (dd==k)
    hol_f[idx] = 0.62 if v in ("Easter Sunday","Christmas Day","New Year's Day") else (0.85 if v=="Christmas Eve" else 1.14)
for y in easter:  # pre-holiday peaks
    for k in [pd.Timestamp(f"{y}-12-23"), pd.Timestamp(f"{y}-12-31"), pd.Timestamp(easter[y])-timedelta(1)]:
        hol_f[dd==k] *= 1.28
    if y < 2025: hol_f[dd==pd.Timestamp(f"{y}-12-24")] *= 1.20
# weather-ish daily shock shared by all stores (heat waves etc.)
wx = np.exp(np.convolve(rng.normal(0,0.035,ND), np.ones(5)/5, mode="same"))

# ---------------- STORE x DAY MATRIX ----------------
od = np.array([(o-START).days for o in open_dates])
cd = np.array([((c-START).days if pd.notna(c) else 10**6) for c in closing])
di = np.arange(ND)
open_mask = (di[None,:] >= od[:,None]) & (di[None,:] < cd[:,None])
for j,(s,e) in refurb.items():
    open_mask[j, (dd>=s)&(dd<e)] = False
months_open = np.clip((di[None,:] - od[:,None])/30.44, 0, None)
maturity = 0.52 + 0.48*(1-np.exp(-months_open/5.5))
# closing stores: decline in the last 6 months before closure
decl = np.clip((cd[:,None]-di[None,:])/180, 0.75, 1.0)
reg_f = np.ones((NS, ND))
east = region_id=="R5"
reg_f[east] *= np.where(yr>=2025, 0.935, 1.0)[None,:]   # East underperformance from 2025 (not in budget)
seaside = dim_store.IsSeasideCity.values==1
reg_f[seaside] *= np.where(np.isin(mon,[6,7,8]), 1.16, 1.0)[None,:]
seas = np.array([season["Transit" if l=="Transit" else "Standard"] for l in loc])[:, mon-1]
dowm = np.array([dow[l] for l in loc])[:, wd]
common = price*vol*sunday_f*hol_f
expected = base[:,None]*seas*dowm*common[None,:]*maturity*decl
# Nano ramps faster in 2025-26 (concept proven)
nano = fmt=="Nano"
expected[nano] *= np.where(yr>=2025, 1.08, 1.0)[None,:]
actual = expected*reg_f*wx[None,:]*rng.lognormal(0,0.085,(NS,ND))
# budget expectation: no East penalty, no noise, seaside effect known, stretch 1.5%
budget_daily = expected * np.where(seaside[:,None], np.where(np.isin(mon,[6,7,8]),1.12,1.0)[None,:], 1.0) * 1.015

# ---------------- CATEGORIES ----------------
cats = ["Beverages","Beer","Wine & Spirits","Tobacco","Snacks","Ready Meals","Coffee & Hot Drinks",
        "Fresh & Dairy","Bakery","Confectionery","Household & Personal Care","Services"]
cgrp = ["Beverages","Alcohol & Tobacco","Alcohol & Tobacco","Alcohol & Tobacco","Food","Food-to-Go","Food-to-Go",
        "Food","Food-to-Go","Food","Non-Food & Services","Non-Food & Services"]
share0 = np.array([16,14,3,18,9,8,5,7,6,7,4,3],float)/100
growth = np.array([0.03,0.00,0.01,-0.05,0.02,0.13,0.11,0.02,0.06,0.01,0.02,0.09])
margin0 = np.array([0.37,0.24,0.21,0.095,0.35,0.46,0.61,0.29,0.43,0.35,0.32,0.72])
unit_price = np.array([4.8,5.2,32.0,17.5,6.2,14.5,8.9,5.4,4.2,5.9,11.5,9.0])
pl0 = np.array([0.12,0.07,0.0,0.0,0.21,0.55,0.68,0.14,0.58,0.17,0.19,0.0])
waste0 = np.array([0.004,0.002,0.001,0.0,0.004,0.062,0.015,0.048,0.071,0.005,0.002,0.0])
cseason = np.ones((12,12))
cseason[0] = [0.85,0.85,0.92,1.0,1.08,1.2,1.3,1.28,1.02,0.9,0.85,0.9]   # beverages
cseason[1] = [0.75,0.75,0.88,1.0,1.15,1.3,1.42,1.38,1.0,0.88,0.8,0.98]  # beer
cseason[2] = [0.85,0.85,0.9,1.02,0.95,0.95,0.95,0.95,0.95,1.0,1.05,1.6]  # wine&spirits
cseason[6] = [1.18,1.15,1.05,0.95,0.88,0.82,0.78,0.8,0.98,1.1,1.17,1.2]  # coffee
cseason[9] = [0.9,1.05,1.05,1.2,0.92,0.88,0.88,0.88,0.95,1.02,1.05,1.3] # confectionery
cseason[7] = [1.0,1.0,1.0,1.08,1.0,0.98,0.95,0.95,1.0,1.0,1.0,1.1]
loc_adj = {"Urban":np.ones(12),
  "Suburban":np.array([1,1.05,1.05,1.02,1,0.9,0.85,1.08,1.0,1.02,1.1,1.0]),
  "Rural":np.array([0.98,1.2,1.25,1.15,0.95,0.65,0.6,1.12,1.0,1.0,1.2,0.9]),
  "Transit":np.array([1.12,0.8,0.6,0.9,1.1,1.45,1.6,0.85,1.25,1.05,0.7,1.1])}
nano_adj = np.array([1.2,0.75,0.4,0.25,1.2,1.7,1.7,0.9,1.3,1.1,0.8,0.5])

# monthly aggregation of actuals
act = np.where(open_mask, actual, 0.0)
mkeys = pd.PeriodIndex(dd, freq="M"); um = mkeys.unique(); NM_ALL = len(um)
m_idx = np.searchsorted(um.asi8 if hasattr(um,'asi8') else um.astype(int), mkeys.asi8)
msum = np.zeros((NS, NM_ALL)); np.add.at(msum.T, m_idx, act.T)
mbud = np.zeros((NS, NM_ALL)); np.add.at(mbud.T, m_idx, np.where(open_mask|(di[None,:]>=n_act), budget_daily*((di[None,:]>=od[:,None])&(di[None,:]<cd[:,None])), 0).T)
m_start = um.to_timestamp(); m_year = m_start.year.values; m_mon = m_start.month.values
m_t = ((m_start - START).days.values)/365.25
# category shares per store-month
sh = share0[None,None,:]*(1+growth[None,None,:])**m_t[None,:,None]*cseason[:,m_mon-1].T[None,:,:]
la = np.array([loc_adj[l] for l in loc]); la[nano] *= nano_adj
sh = sh*la[:,None,:]*rng.lognormal(0,0.05,(NS,1,12))
sh = sh/sh.sum(axis=2, keepdims=True)
# margins over time: 2023 inflation squeeze, 2025+ private label uplift
mp = np.select([ (m_year==2023)&(m_mon<=6), m_year==2023, m_year==2024, m_year==2025], [-0.016,-0.009,-0.002,0.003], 0.006)
cm = margin0[None,None,:] + mp[None,:,None] + rng.normal(0,0.004,(NS,1,12))
blend = (sh*cm).sum(axis=2)   # store x month

# ---------------- FactDailySales ----------------
basket_fmt = {"Standard":23.0,"Nano":17.5,"Travel":20.5}
bask0 = np.array([basket_fmt[f] for f in fmt])*np.array([{"Urban":1.0,"Suburban":1.06,"Rural":1.10,"Transit":0.92}[l] for l in loc])
app0 = np.where(nano, 0.62, 0.26) * np.array([{"R1":1.12,"R2":1.0,"R3":1.02,"R4":0.98,"R5":0.86}[r] for r in region_id])
rows = []
for j in range(NS):
    msk = open_mask[j,:n_act]
    if not msk.any(): continue
    ix = np.where(msk)[0]
    sales = act[j, ix]
    t = tfrac[ix]
    app_share = np.clip(app0[j] + (0.24 if not nano[j] else 0.2)*(1-np.exp(-t/1.8)) + rng.normal(0,0.02,len(ix)), 0.05, 0.95)
    basket = bask0[j]*price[ix]*(1+0.018*t)*rng.lognormal(0,0.03,len(ix))
    # app users spend 22% more per basket
    nonapp_b = basket/(app_share*1.22 + (1-app_share))
    trans = np.maximum(1, np.round(sales/basket)).astype(int)
    app_tr = np.round(trans*app_share).astype(int)
    app_sales = app_tr*nonapp_b*1.22
    app_sales = np.minimum(app_sales, sales*0.97)
    items = np.round(trans*(2.55+0.06*t+rng.normal(0,0.08,len(ix)))).astype(int)
    promo = sales*np.clip(0.17+0.03*np.isin(mon[ix],[6,7,8,12])+0.01*t+rng.normal(0,0.015,len(ix)),0.08,0.35)
    gm = blend[j, m_idx[ix]]*(1+rng.normal(0,0.01,len(ix)))
    gp = sales*gm
    rows.append(pd.DataFrame({"Date":dd[ix].date,"StoreID":f"ZB{j+1:04d}","NetSales":sales.round(2),
        "COGS":(sales-gp).round(2),"GrossProfit":gp.round(2),"Transactions":trans,"ItemsSold":items,
        "AppTransactions":app_tr,"AppSales":app_sales.round(2),"PromoSales":promo.round(2)}))
fds = pd.concat(rows, ignore_index=True)
save(fds, "FactDailySales")
print("daily rows", len(fds))

# exact monthly totals from the daily table (keeps facts reconciled)
fds["_m"] = pd.to_datetime(fds.Date).dt.to_period("M")
mtot = fds.groupby(["StoreID","_m"])[["NetSales","GrossProfit","AppTransactions"]].sum()

# ---------------- FactCategorySales ----------------
sid = np.array([int(s[2:])-1 for s in mtot.index.get_level_values(0)])
mi = np.searchsorted(um.asi8, pd.PeriodIndex(mtot.index.get_level_values(1)).asi8)
S = mtot.NetSales.values; G = mtot.GrossProfit.values
csales = S[:,None]*sh[sid, mi, :]
cgp = csales*cm[sid, mi, :]; cgp *= (G/cgp.sum(axis=1))[:,None]
ptime = price[np.searchsorted(dd, um[mi].to_timestamp())]
units = np.maximum(0, np.round(csales/(unit_price[None,:]*ptime[:,None]))).astype(int)
wimp = np.select([m_year[mi]==2023, m_year[mi]==2024, m_year[mi]==2025],[1.0,0.93,0.82],0.77)
tw = np.array([{"Gold":0.85,"Silver":1.0,"Bronze":1.22}[t] for t in tier])[sid]
waste = csales*waste0[None,:]*wimp[:,None]*tw[:,None]*rng.lognormal(0,0.12,csales.shape)
plg = np.clip(pl0[None,:]*(1+0.09*m_t[mi])[:,None]*rng.lognormal(0,0.05,csales.shape),0,0.9)
fcs = pd.DataFrame({
  "MonthStart":np.repeat(um[mi].to_timestamp().date,12),
  "StoreID":np.repeat(mtot.index.get_level_values(0),12),
  "CategoryID":np.tile([f"C{k+1:02d}" for k in range(12)], len(S)),
  "NetSales":csales.ravel().round(2),"GrossProfit":cgp.ravel().round(2),"UnitsSold":units.ravel(),
  "WasteValue":waste.ravel().round(2),"PrivateLabelSales":(csales*plg).ravel().round(2)})
save(fcs, "FactCategorySales"); print("cat rows", len(fcs))

dim_cat = pd.DataFrame({"CategoryID":[f"C{k+1:02d}" for k in range(12)],"Category":cats,"CategoryGroup":cgrp,
  "TargetGrossMargin":margin0.round(3),"IsFresh":[0,0,0,0,0,1,0,1,1,0,0,0],
  "IsStrategicGrowth":[0,0,0,0,0,1,1,0,1,0,0,1],"SortOrder":range(1,13)})
save(dim_cat, "DimCategory")

# ---------------- FactBudget (Region x Month x Category) ----------------
bsh = sh.mean(axis=0)*0+sh  # same mix
bud_rows = []
for r in regions.RegionID:
    rm = region_id==r
    bs = (mbud[rm][:,:,None]*sh[rm]).sum(axis=0)          # month x cat
    bg = (mbud[rm][:,:,None]*sh[rm]*(margin0[None,None,:]+np.where(m_year>=2025,0.006,0.0)[None,:,None])).sum(axis=0)
    bud_rows.append(pd.DataFrame({"MonthStart":np.repeat(um.to_timestamp().date,12),"RegionID":r,
        "CategoryID":np.tile(dim_cat.CategoryID.values, NM_ALL),"BudgetNetSales":bs.ravel().round(0),
        "BudgetGrossProfit":bg.ravel().round(0)}))
fb = pd.concat(bud_rows, ignore_index=True); save(fb, "FactBudget")

# ---------------- FactStoreOpex ----------------
fds_m = fds.groupby(["StoreID","_m"]).agg(NetSales=("NetSales","sum"),GrossProfit=("GrossProfit","sum"),OpenDays=("Date","count")).reset_index()
j = fds_m.StoreID.str[2:].astype(int).values-1
mm = fds_m._m.dt.month.values; yy = fds_m._m.dt.year.values
dim_in_m = fds_m._m.dt.days_in_month.values; frac = fds_m.OpenDays.values/dim_in_m
rent_sqm = np.array([{"Urban":125,"Suburban":82,"Rural":46,"Transit":185}[l] for l in loc])[j]
rent_idx = np.select([yy==2023,yy==2024,yy==2025],[1.0,1.06,1.10],1.135)
rent = sqm[j]*rent_sqm*rent_idx*frac
kwh = sqm[j]*np.where(fmt[j]=="Nano",70,46)*np.where(np.isin(mm,[6,7,8]),1.15,1.0)*frac
eprice = np.select([yy==2023,yy==2024,yy==2025],[1.12,0.96,0.86],0.81)
energy = kwh*eprice*rng.lognormal(0,0.05,len(j))
comm = (3200*frac + 0.30*fds_m.GrossProfit.values)*np.where(fmt[j]=="Nano",0.35,1.0)  # Nano: no franchisee, lower
mkt = fds_m.NetSales.values*0.012
tech = np.where(fmt[j]=="Nano", 5200*frac, 650*frac)
other = fds_m.NetSales.values*0.014*rng.lognormal(0,0.08,len(j))
fso = pd.DataFrame({"MonthStart":fds_m._m.dt.start_time.dt.date,"StoreID":fds_m.StoreID,"OpenDays":fds_m.OpenDays,
  "RentCost":rent.round(2),"EnergyCost":energy.round(2),"FranchiseeCommission":comm.round(2),
  "MarketingCost":mkt.round(2),"TechnologyCost":tech.round(2),"OtherOpex":other.round(2)})
save(fso, "FactStoreOpex")

# ---------------- FactAppMetrics (Region x Month) ----------------
fds["RegionID"] = region_id[fds.StoreID.str[2:].astype(int).values-1]
ra = fds.groupby(["RegionID","_m"]).AppTransactions.sum().reset_index()
out = []
for r, g in ra.groupby("RegionID"):
    g = g.sort_values("_m").reset_index(drop=True)
    t = ((g._m.dt.start_time - START).dt.days.values)/365.25
    freq = 6.2 + 0.45*t + np.where(g._m.dt.month.isin([6,7,8]),0.4,0)
    mau = g.AppTransactions.values/freq
    trend = pd.Series(mau).rolling(6, min_periods=1).mean().values
    act_rate = 0.41 + 0.028*t
    reg = np.maximum.accumulate(trend/act_rate)
    churn = reg*0.006
    new = np.diff(np.r_[reg[0]*0.985, reg]) + churn
    new = new*np.where(g._m.dt.month.isin([1,9]),1.15,1.0)
    coup = g.AppTransactions.values*(0.30+0.03*t)
    out.append(pd.DataFrame({"MonthStart":g._m.dt.start_time.dt.date,"RegionID":r,"RegisteredUsers":reg.round(0).astype(int),
        "MonthlyActiveUsers":mau.round(0).astype(int),"NewRegistrations":new.round(0).astype(int),
        "CouponsRedeemed":coup.round(0).astype(int),"AppRating":np.clip(4.45+0.05*t+rng.normal(0,0.03,len(g)),1,5).round(2)}))
fam = pd.concat(out, ignore_index=True); save(fam, "FactAppMetrics")

# ---------------- DimFranchisee ----------------
fr = dim_store.groupby("FranchiseeID").agg(FirstStoreOpening=("OpeningDate","min"),NumberOfStores=("StoreID","count"),
      HomeRegionID=("RegionID","first")).reset_index()
fr["JoinDate"] = [ (pd.Timestamp(x)-timedelta(int(rng.integers(20,120)))).date() for x in fr.FirstStoreOpening]
fr["CohortYear"] = pd.to_datetime(fr.JoinDate).dt.year
fr["Tier"] = fr.FranchiseeID.map(tier_of)
fr["TenureBand"] = pd.cut((END_ACT - pd.to_datetime(fr.JoinDate)).dt.days/365.25,[-1,1,3,5,10,99],labels=["<1 yr","1-3 yrs","3-5 yrs","5-10 yrs","10+ yrs"]).astype(str)
fr["IsMultiStore"] = (fr.NumberOfStores>1).astype(int)
fr = fr[["FranchiseeID","JoinDate","CohortYear","TenureBand","Tier","NumberOfStores","IsMultiStore","HomeRegionID"]]
# Nano stores are company operated
nano_ids = set(dim_store.loc[dim_store.Format=="Nano","FranchiseeID"])
dim_store.loc[dim_store.Format=="Nano","FranchiseeID"] = "COMPANY"
dim_store["OperatingModel"] = np.where(dim_store.Format=="Nano","Company-operated (autonomous)","Franchise")
fr = fr[~fr.FranchiseeID.isin(nano_ids - set(dim_store.FranchiseeID))]
fr = pd.concat([fr, pd.DataFrame([{"FranchiseeID":"COMPANY","JoinDate":None,"CohortYear":None,"TenureBand":"n/a",
     "Tier":"Company","NumberOfStores":int((dim_store.Format=="Nano").sum()),"IsMultiStore":1,"HomeRegionID":None}])])
fr["NumberOfStores"] = fr.FranchiseeID.map(dim_store.FranchiseeID.value_counts()).fillna(0).astype(int)
fr = fr[fr.NumberOfStores>0]; fr["IsMultiStore"]=(fr.NumberOfStores>1).astype(int)
save(fr, "DimFranchisee"); save(dim_store, "DimStore")
print("done")
