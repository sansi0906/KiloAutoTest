"""提取菜单DOM结构片段"""
import re

with open(r'E:\KiloAutoTest\cjgt_web\screenshots\full_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the context around "服务项目配置"
pos = content.find('服务项目配置')
if pos > 0:
    # Get surrounding 3000 chars
    start = max(0, pos - 1500)
    end = min(len(content), pos + 1500)
    snippet = content[start:end]
    with open(r'E:\KiloAutoTest\cjgt_web\screenshots\menu_snippet.txt', 'w', encoding='utf-8') as f:
        f.write(snippet)
    print("菜单片段已保存到 menu_snippet.txt")
    print(f"片段长度: {len(snippet)} 字符")

# Also find all URLs/routes in the page
urls = re.findall(r'["\'](/(?:smart|service|content|knowledge|contract|business)[^"\']*)["\']', content, re.IGNORECASE)
print(f"\n找到的路由URL: {urls}")

# Find all path-like strings
paths = re.findall(r'["\'](/[a-zA-Z][a-zA-Z0-9_/]*(?:config|manage|list|service|content|knowledge)[^"\']*)["\']', content, re.IGNORECASE)
print(f"\n路径模式: {paths}")
