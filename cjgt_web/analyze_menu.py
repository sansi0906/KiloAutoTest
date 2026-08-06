"""分析菜单HTML结构，提取菜单项和URL映射"""
import re

with open(r'E:\KiloAutoTest\cjgt_web\screenshots\menu_structure.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all href links
hrefs = re.findall(r'href="([^"]*)"', content)
print("所有href链接:")
for h in hrefs:
    if h and h != '#':
        print(f"  {h}")

# Find all menu items with their text and onclick/data attributes
# Look for jeecg-simple-menu-item patterns
items = re.findall(r'class="[^"]*jeecg-simple-menu-item[^"]*"[^>]*>(.*?)</(?:li|div|a)', content, re.DOTALL)
print(f"\n菜单项数量: {len(items)}")
for i, item in enumerate(items):
    text = re.sub(r'<[^>]+>', '', item).strip()
    if text:
        print(f"  [{i}]: {text}")

# Find all data-key or data-path attributes
data_keys = re.findall(r'data-key="([^"]*)"', content)
print(f"\nData keys: {data_keys}")

# Find <a> tags with their text and href
a_tags = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', content, re.DOTALL)
print(f"\n<a>标签:")
for href, text in a_tags:
    clean_text = re.sub(r'<[^>]+>', '', text).strip()
    if clean_text:
        print(f"  href={href} text={clean_text}")

# Find spans with menu text
spans = re.findall(r'<span[^>]*>([^<]*(?:服务|配置|管理|知识|菜单|角色|员工|协议)[^<]*)</span>', content)
print(f"\n菜单span文本:")
for s in spans:
    print(f"  {s}")

# Look for onclick handlers
onclicks = re.findall(r'onclick="([^"]*)"', content)
print(f"\nOnclick handlers: {onclicks}")

# Find router links or data attributes
router_links = re.findall(r'to="([^"]*)"', content)
print(f"\nRouter links: {router_links}")

# Find all elements with path attribute
paths = re.findall(r'path="([^"]*)"', content)
print(f"\nPath attributes: {paths}")
