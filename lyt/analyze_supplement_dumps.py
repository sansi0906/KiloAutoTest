"""分析营销补充测试XML dumps"""
import re, os

DUMP_DIR = "E:/KiloAutoTest/lyt/explore_supplement/ui_dumps"
files = [
    "营销_login_result_105148.xml",
    "营销_settings_01_home_105151.xml",
    "营销_settings_try_980_180_105153.xml",
    "营销_cust_detail_01_105200.xml",
    "营销_cart_mgmt_01_105220.xml",
    "营销_ord_action_01_105225.xml",
]

for fname in files:
    fpath = os.path.join(DUMP_DIR, fname)
    if not os.path.exists(fpath): continue
    with open(fpath, "r", encoding="utf-8") as f:
        xml = f.read()
    texts = re.findall(r'text="([^"]*)"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    non_empty = [(t, (int(x1)+int(x2))//2, (int(y1)+int(y2))//2)
                 for t, x1, y1, x2, y2 in texts if t.strip() and int(y1) > 104]
    # clickable elements
    clickable = re.findall(r'clickable="true"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml)
    click_centers = [((int(x1)+int(x2))//2, (int(y1)+int(y2))//2) for x1, y1, x2, y2 in clickable]
    print(f"\n{'='*60}")
    print(f"  {fname} ({len(non_empty)} texts, {len(click_centers)} clickable)")
    print(f"{'='*60}")
    for t, cx, cy in non_empty[:20]:
        print(f"  [{t}] @({cx},{cy})")
    if click_centers:
        print(f"  Clickable: {click_centers[:8]}")
