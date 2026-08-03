import uiautomator2 as u2
import time, re

d = u2.connect()
xml = d.dump_hierarchy()
texts = re.findall(r'text="([^"]*)"', xml)
for t in texts:
    if t.strip():
        print(repr(t))
