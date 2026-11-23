import pandas as pd

d = pd.read_csv("cereals_clean.csv")
d["period"] = d["year"].map(lambda y: "1998-2000" if 1998 <= y <= 2000 else "2020-2022" if y >= 2020 else None)
p = d.dropna(subset=["period"])


def avg(by):
    return p.groupby(by + ["period"])[["area_ha", "production_t"]].sum().div(3).unstack("period")


def show(title, t):
    print(f"\n{title}\n{t.round(2).to_string()}")


g = avg(["crop_group"]) / 1e6
g.loc["All cereals"] = g.sum()
show("Average area (million ha) and production (million t) per year", g)

m = g.loc["Millets"]
print("\nMillet area change:", f"{m.area_ha['2020-2022'] / m.area_ha['1998-2000'] - 1:.1%}")
print("Millet production change:", f"{m.production_t['2020-2022'] / m.production_t['1998-2000'] - 1:.1%}")
y = m.production_t / m.area_ha
print("Millet yield t/ha:", y.round(2).to_dict(), f"change {y['2020-2022'] / y['1998-2000'] - 1:.1%}")
print("Millet share of cereal area:", (g.loc["Millets", "area_ha"] / g.loc["All cereals", "area_ha"]).round(3).to_dict())

c = avg(["crop"]) / 1e6
c[("area_ha", "change")] = c.area_ha["2020-2022"] / c.area_ha["1998-2000"] - 1
c[("production_t", "change")] = c.production_t["2020-2022"] / c.production_t["1998-2000"] - 1
show("By crop", c)

s = (p[p.crop_group == "Millets"].groupby(["state", "period"]).area_ha.sum().div(3).unstack().fillna(0) / 1e3)
s["change"] = s["2020-2022"] - s["1998-2000"]
s["pct"] = s["change"] / s["1998-2000"]
s["share_now"] = s["2020-2022"] / s["2020-2022"].sum()
show("Millet area by state ('000 ha)", s.sort_values("change"))
lost = s.loc[s.change < 0, "change"].sum()
print("\nMaharashtra + Karnataka share of area lost:", f"{s.loc[['Maharashtra', 'Karnataka'], 'change'].sum() / lost:.1%}")

j = p[p.crop == "Jowar"].groupby(["state", "period"]).area_ha.sum().div(3).unstack().fillna(0) / 1e3
j["change"] = j["2020-2022"] - j["1998-2000"]
show("Jowar area by state ('000 ha), biggest falls", j.sort_values("change").head(5))

t = d[d.crop_group == "Millets"].groupby("year")[["area_ha", "production_t"]].sum() / 1e6
show("Millet area and production by year (million)", t.T)

dist = p[(p.crop_group == "Millets") & (p.period == "2020-2022")].groupby(["state", "district"]).area_ha.sum().div(3)
print("\nTop millet districts 2020-22 ('000 ha) and share of India:")
print(pd.concat([dist.nlargest(5) / 1e3, (dist.nlargest(5) / dist.sum()).round(3)], axis=1).to_string())
