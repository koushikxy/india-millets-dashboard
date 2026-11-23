import re, sys, time
from pathlib import Path
import requests, truststore
truststore.inject_into_ssl()

BASE = "https://data.desagri.gov.in"
PAGE = BASE + "/website/crops-apy-report-web"
CROPS = ["1", "2", "5", "3", "4", "6", "9", "7"]
out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
out.mkdir(parents=True, exist_ok=True)

s = requests.Session()
page = s.get(PAGE, timeout=60).text
token = re.search(r'name="_token" value="([^"]+)"', page).group(1)
states = re.findall(r'<option value="(\d+)"\s*>([^<]+)</option>', page.split('id="fltrstates"')[1].split("</select>")[0])

for code, name in states:
    f = out / f"{code}.html"
    if f.exists():
        continue
    r = s.post(BASE + "/report/crop/horizontal_crop_vertical_year", timeout=300, headers={"Referer": PAGE}, data={
        "reportformat": "horizontal_crop_vertical_year", "fltrstates[]": code, "fltrdistricts[]": "all",
        "fltrcrops[]": CROPS, "fltrstartyear": "1997", "fltrendyear": "2022", "fltrrptformat": "scrview", "_token": token})
    f.write_text(r.text, encoding="utf-8")
    print(code, name.strip(), r.status_code, len(r.text))
    time.sleep(2)
