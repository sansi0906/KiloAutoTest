"""分析探索测试的XML dumps"""
import re
import os

DUMP_DIR = "E:/KiloAutoTest/lyt/explore_dual/ui_dumps"

files_to_check = [
    "营销_08_after_login_095105.xml",
    "营销_home_01_095108.xml",
    "营销_customer_01_095140.xml",
    "营销_cart_01_095149.xml",
    "营销_orders_01_095155.xml",
    "代理_07_code_entered_095241.xml",
    "代理_08_after_login_095249.xml",
]

for fname in files_to_check:
    fpath = os.path.join(DUMP_DIR, fname)
    if not os.path.exists(fpath):
        print(f"\n!!! NOT FOUND: {fname}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        xml = f.read()
    
    texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2) 
                 for t, x1, y1, x2, y2 in texts if t.strip() and int(y1) > 104]
    
    # also find clickable elements
    clickable = re.findall(r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    click_centers = [((int(x1)+int(x2))//2, (int(y1)+int(y2))//2) 
                     for x1, y1, x2, y2 in clickable]
    
    name = fname.replace(".xml", "")
    print(f"\n{'='*60}")
    print(f"  {name} ({len(non_empty)} texts, {len(click_centers)} clickable)")
    print(f"{'='*60}")
    for t, cx, cy in non_empty[:30]:
        print(f"  [{t}] @({cx},{cy})")
    if click_centers:
        print(f"  --- Clickable: {click_centers[:10]}")
