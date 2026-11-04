import os, sys, glob
from playwright.sync_api import sync_playwright

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
files = sys.argv[1:] or sorted(glob.glob(os.path.join(D, "*.svg")))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(device_scale_factor=1)
    for f in files:
        pg.goto("file://" + os.path.abspath(f))
        pg.query_selector("svg").screenshot(path=f[:-4] + ".png")
    b.close()
print("rendered", len(files))
