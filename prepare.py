import io, sys
from pathlib import Path
import pandas as pd

raw = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
MILLETS = ["Jowar", "Bajra", "Ragi", "Small millets"]

parts = []
for f in sorted(raw.glob("*.html")):
    t = pd.read_html(io.StringIO(f.read_text(encoding="utf-8")), flavor="lxml", thousands=None)[0]
    if t.iloc[0, 0] == "No Data Found":
        print("no data:", f.name)
        continue
    t.columns = [c[0] if c[0] in ("State", "District", "Year") else "|".join(c) for c in t.columns]
    long = t.melt(id_vars=["State", "District", "Year"], var_name="col", value_name="v")
    long[["crop", "season", "measure"]] = long["col"].str.split("|", expand=True)
    parts.append(long.drop(columns="col"))

d = pd.concat(parts, ignore_index=True)
print("raw cells:", len(d))
d["v"] = pd.to_numeric(d["v"].astype(str).str.replace(",", ""), errors="coerce")
print("blank cells (crop not grown or not reported):", d["v"].isna().sum())
d["measure"] = d["measure"].map({"Area (Hectare)": "area_ha", "Production (Tonnes)": "production_t", "Yield (Tonne/Hectare)": "yield_raw"})
d = d.pivot_table(index=["State", "District", "Year", "crop", "season"], columns="measure", values="v", aggfunc="first").reset_index()
print("rows after unpivot:", len(d))

for c in ["State", "District"]:
    d[c] = d[c].str.replace(r"^\d+\.\s*", "", regex=True).str.strip()
print("district names not in title case:", (d["District"] != d["District"].str.title()).groupby(d["District"]).any().sum())
d["District"] = d["District"].str.title()
d["State"] = d["State"].replace({"The Dadra & Nagar Haveli and Daman and Diu": "Dadra and Nagar Haveli and Daman and Diu",
                                 "Dadra and Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
                                 "Daman and Diu": "Dadra and Nagar Haveli and Daman and Diu", "Ladakh": "Jammu and Kashmir"})
d["year"] = d["Year"].str[:4].astype(int)
d["year_label"] = d["year"].astype(str) + "-" + (d["year"] + 1).astype(str).str[-2:]

print("area given but production blank:", (d.area_ha.notna() & d.production_t.isna()).sum())
print("zero or blank area:", (~(d.area_ha > 0)).sum())
d = d[d.area_ha > 0]

chk = d[d.production_t.notna() & d.yield_raw.notna()]
diff = (chk.production_t / chk.area_ha - chk.yield_raw).abs()
print("rows where source yield differs from production/area by > 0.05 t/ha:", (diff > 0.05).sum())

d = d.groupby(["State", "District", "year", "year_label", "crop"], as_index=False)[["area_ha", "production_t"]].sum(min_count=1)
d = d.rename(columns={"State": "state", "District": "district"})
d = d[d.production_t.notna()]
print("rows left after dropping blank production:", len(d))
bad = (d.state == "Maharashtra") & (d.crop == "Small millets") & (d.year == 2010)
print("Maharashtra small millets 2010 area (ha), about 60x its usual level:", d.loc[bad, "area_ha"].sum())
d = d[~bad]
odd = d.production_t / d.area_ha > 15
print("rows with yield above 15 t/ha dropped:", odd.sum())
d = d[~odd]
d["crop_group"] = d["crop"].where(d["crop"].isin(["Rice", "Wheat"]), "Maize and barley")
d.loc[d.crop.isin(MILLETS), "crop_group"] = "Millets"
d = d[["state", "district", "year", "year_label", "crop", "crop_group", "area_ha", "production_t"]].sort_values(["state", "district", "year", "crop"])
print("final rows:", len(d), "| states:", d.state.nunique(), "| districts:", d[["state", "district"]].drop_duplicates().shape[0])
d.to_csv("cereals_clean.csv", index=False)
