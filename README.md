# Where did India's millets go?

2023 was the International Year of Millets, and jowar, bajra and ragi were suddenly everywhere. I wanted to know what had actually happened to millet farming in India before that, so I built a Tableau dashboard from the Ministry of Agriculture's district-level crop statistics, covering 1997-98 to 2022-23 (743 districts, 8 cereal crops).

You can open the live dashboard on [Tableau Public](https://public.tableau.com/app/profile/koushik.maity/viz/india_millets/Overview).

![Overview](screenshots/overview.png)

## What I found

To compare periods I used 3-year averages, 1998-99 to 2000-01 against 2020-21 to 2022-23, so that one drought year doesn't decide the result.

Millet area (jowar, bajra, ragi and small millets) fell from 22.3 million hectares to 13.3 million, down 40%. Millets went from 22.5% of all cereal area to 12.2%. But production did not fall with it. Millet output went from 18.1 million tonnes to 18.7 million (+3%), because yield went up from 0.81 to 1.40 tonnes per hectare (+73%). Bajra did most of the work here, its production rose 81% on 19% less land.

Most of the lost area was jowar. Jowar area fell 58%, from 10.1 to 4.2 million hectares, and Maharashtra alone lost about 3 million hectares of it. Over the same years rice area grew 17%, wheat 31% and maize 58%.

When I looked at states, two of them explained most of the decline. Maharashtra and Karnataka together lost about 6 million hectares of millet area, which is 65% of all the area lost. Telangana kept only 13% of its millet area. Rajasthan went the other way: its millet area went up 4% (4.85 to 5.03 million hectares) and it now has 38% of India's millet area, 88% of that bajra. Barmer district alone has 7% of the country's millet area.

## Data and cleaning

The data comes from the [Area, Production & Yield report](https://data.desagri.gov.in/website/crops-apy-report-web) on the Directorate of Economics & Statistics (DES) data portal, Ministry of Agriculture & Farmers Welfare. It gives area, production and yield for every district, year, crop and season. The portal only shows the report on screen or as an Excel export per request, so `fetch_data.py` asks for one state at a time and saves the HTML into `data/raw`. The raw files are big, so they are not in this repo. Run the script once and it downloads them.

The raw report needed a lot of cleaning. It is a pivot table, with crop, season and measure in three header rows and state and district as merged cells. There are 676,686 cells in all and 365,413 of them are blank. State and district names have serial numbers in front (`1. Punjab`, `25. Faizabad`), 102 district names are in odd case like `West tripura`, and years are text like `1997 - 1998` and not in order. One crop can also have up to six seasons, so I added the seasons up to get one row per district, year and crop.

Some rows were plain errors. 628 season rows have an area but no production. After adding seasons up, 511 district-year-crop rows still had no production at all, and I dropped those (about 0.02% of all the area). Small millets in Maharashtra for 2010-11 show 4.53 million hectares, about 60 times the usual figure, so I dropped that too, along with 23 rows where the yield is above 15 tonnes per hectare, which isn't possible for these crops. Dadra and Nagar Haveli and Daman and Diu show up under three names because they were merged in 2020, so I used the merged name everywhere, and I counted Ladakh under Jammu and Kashmir for the same reason. Lakshadweep has no data at all.

After `prepare.py` the clean file, `cereals_clean.csv`, has 77,318 rows. `analysis.py` works out every number above from it, and the dashboard shows the same numbers.

## How I worked it out

The comparisons in Tableau use two periods, 1998-2000 and 2020-22, each averaged over three years with fields like `SUM(IF [Period] = '2020-22' THEN [Sel Area] END) / 3`. A `Select Crop` parameter lets the same views show all millets together or one millet at a time.

A state's share of India's millet area needs the all-India total in a view that is split by state, so I used a FIXED LOD with no dimension for that total, and `{FIXED [state] : ...}` for a district's share of its state. To see whether yield really made up for the lost land, I turned both area and yield into an index with the 1998-2000 average as 100 and put them on one synchronised axis. By 2022-23 area was at 57 and yield at 180. The share of cereal area line is smoothed with a 3-year moving average, `WINDOW_AVG(..., -2, 0)` along the crop year.

To check how concentrated the loss was, I made a set of the five states that lost the most area. For all millets that is Maharashtra, Karnataka, Gujarat, Madhya Pradesh and Telangana, and together they account for 85% of the area lost. I also grouped states into Maharashtra and Karnataka, Rajasthan, and the rest of India. Maharashtra and Karnataka went from 10.4 to 4.4 million hectares (-58%), the rest of India fell 45%, and Rajasthan went up 4%.

## Files

- `india_millets.twbx`: the workbook. The data is packaged inside, so it opens in Tableau Public directly.
- `cereals_clean.csv`: the cleaned data.
- `fetch_data.py`, `prepare.py`, `analysis.py`: download, clean and analyse the data, run in that order after `pip install -r requirements.txt`. `truststore` is in the requirements only because the DES site's certificate failed on my Windows machine without it.
- `screenshots/`: the two dashboards, the Overview with jowar selected, and the States dashboard with Maharashtra clicked.

## Limits

The numbers are summed from district data and don't exactly match the all-India estimates DES publishes separately, so I've compared changes and shares rather than treating the totals as official national figures.

Some states stop reporting some crops. Maharashtra has no small millets figures after 2015-16 and Jharkhand none after 1998-99, so part of the 70% fall in small millets is just missing data. The other millets are reported much more consistently.

1997-98 is incomplete (Kerala and Himachal Pradesh are missing, and Chhattisgarh has only 6 districts), which is why my comparison starts at 1998-99, though the year still shows on the trend charts. District boundaries also changed a lot (Telangana went from 9 to 30 districts in 2016-17 and Andhra Pradesh from 13 to 26 in 2022-23), so I compared states over time rather than districts.

Tools: Tableau Public, Python (Pandas)
