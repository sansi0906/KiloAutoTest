"""
超级个体后台管理系统 - 页面探索脚本V2
使用Playwright直接操控DOM展开菜单并导航
"""
import asyncio
import os
import json
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 菜单结构
MENU_STRUCTURE = {
    "智能服务配置": ["服务项目配置", "服务定价配置", "合同服务配置", "经营范围配置"],
    "内容管理": ["知识库"],
}


async def login(page):
    """登录系统"""
    print("=" * 60)
    print("登录系统")
    print("=" * 60)
    await page.goto(LOGIN_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # 输入账号密码
    await page.fill('input[placeholder="账号"]', USERNAME)
    await page.fill('input[type="password"]', PASSWORD)

    # 选择账号登录方式（默认已选）
    # 点击登录 - 尝试多种选择器
    login_clicked = False
    for selector in [
        'button:has-text("登录")',
        'button:has-text("登 录")',
        'button[type="submit"]',
        '.login-button',
        'button.ant-btn-primary',
        'button:has-text("Login")',
    ]:
        try:
            btn = page.locator(selector).first
            if await btn.count() > 0:
                await btn.click(timeout=5000)
                login_clicked = True
                print(f"登录按钮选择器: {selector}")
                break
        except:
            continue

    if not login_clicked:
        # 最后用JavaScript点击
        await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.textContent.includes('登录') || btn.textContent.includes('登 录')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        """)

    await page.wait_for_timeout(3000)
    print(f"登录后URL: {page.url}")
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_after_login.png"))


async def expand_menu_and_navigate(page, parent_menu, child_menu):
    """展开父菜单并点击子菜单"""
    print(f"\n--- 导航到: {parent_menu} > {child_menu} ---")

    # 方法1: 通过JavaScript修改子菜单display并点击
    result = await page.evaluate("""
        (args) => {
            const [parentName, childName] = args;
            const menus = document.querySelectorAll('.jeecg-menu-submenu-title, .jeecg-simple-menu__parent');
            let parentFound = false;
            for (const menu of menus) {
                if (menu.textContent.includes(parentName)) {
                    // 找到父菜单，尝试点击
                    menu.click();
                    parentFound = true;
                    break;
                }
            }
            return {parentFound, method: 'click_parent'};
        }
    """, [parent_menu, child_menu])
    await page.wait_for_timeout(1000)

    # 方法2: 直接找到子菜单项并点击
    result2 = await page.evaluate("""
        (args) => {
            const [parentName, childName] = args;
            // 找到所有子菜单项
            const items = document.querySelectorAll('.jeecg-menu-item, .jeecg-simple-menu__children');
            let childFound = false;
            let childClicked = false;
            for (const item of items) {
                if (item.textContent.includes(childName) && !item.textContent.includes(parentName)) {
                    childFound = true;
                    // 确保元素可见
                    item.style.display = '';
                    item.style.visibility = 'visible';
                    item.style.opacity = '1';
                    // 点击
                    item.click();
                    childClicked = true;
                    break;
                }
            }
            return {childFound, childClicked};
        }
    """, [parent_menu, child_menu])
    await page.wait_for_timeout(2000)

    print(f"  URL: {page.url}")
    return page.url


async def capture_page_info(page, module_name, page_name, index):
    """捕获页面信息"""
    safe_name = page_name.replace("/", "_").replace("\\", "_")
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{module_name}_{index}_{safe_name}.png")
    await page.screenshot(path=screenshot_path)

    info = {
        "module": module_name,
        "page_name": page_name,
        "url": page.url,
        "screenshot": screenshot_path,
    }

    # 获取页面标题
    title = await page.evaluate("""
        () => {
            const titles = document.querySelectorAll('h1, h2, h3, .ant-page-header-heading-title, .title, .jeecg-page-header');
            for (const t of titles) {
                if (t.textContent && t.textContent.trim()) {
                    return t.textContent.trim();
                }
            }
            return null;
        }
    """)
    info["title"] = title

    # 获取表格列头
    th_texts = await page.evaluate("""
        () => {
            const ths = document.querySelectorAll('th, .ant-table-thead th');
            const texts = [];
            for (const th of ths) {
                const text = th.textContent.trim();
                if (text) texts.push(text);
            }
            return texts;
        }
    """)
    info["table_columns"] = th_texts

    # 获取按钮
    btn_texts = await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button, .ant-btn');
            const texts = [];
            for (const btn of buttons) {
                const text = btn.textContent.trim();
                if (text && text.length < 30) texts.push(text);
            }
            return [...new Set(texts)];
        }
    """)
    info["buttons"] = btn_texts

    # 获取搜索区域
    search_info = await page.evaluate("""
        () => {
            const inputs = document.querySelectorAll('input[placeholder]');
            const placeholders = [];
            for (const inp of inputs) {
                const ph = inp.getAttribute('placeholder');
                if (ph) placeholders.push(ph);
            }
            return placeholders;
        }
    """)
    info["search_inputs"] = search_info

    # 获取表单字段
    form_labels = await page.evaluate("""
        () => {
            const labels = document.querySelectorAll('.ant-form-item-label label, .ant-form-item label');
            const texts = [];
            for (const l of labels) {
                const text = l.textContent.trim();
                if (text) texts.push(text);
            }
            return texts;
        }
    """)
    info["form_fields"] = form_labels

    # 获取表格数据行数
    row_count = await page.evaluate("""
        () => {
            const rows = document.querySelectorAll('.ant-table-tbody tr');
            return rows.length;
        }
    """)
    info["table_row_count"] = row_count

    # 打印信息
    print(f"  标题: {info['title']}")
    print(f"  URL: {info['url']}")
    print(f"  表格列: {info['table_columns']}")
    print(f"  按钮: {info['buttons']}")
    print(f"  搜索框: {info['search_inputs']}")
    print(f"  表单字段: {info['form_fields']}")
    print(f"  数据行数: {info['table_row_count']}")

    return info


async def main():
    all_page_info = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 登录
        await login(page)

        # 探索每个模块
        for module_name, sub_menus in MENU_STRUCTURE.items():
            print(f"\n{'=' * 60}")
            print(f"探索模块: {module_name}")
            print(f"{'=' * 60}")

            for i, sub_menu in enumerate(sub_menus):
                try:
                    url = await expand_menu_and_navigate(page, module_name, sub_menu)
                    info = await capture_page_info(page, module_name, sub_menu, i)
                    all_page_info.append(info)
                except Exception as e:
                    print(f"  探索出错: {e}")
                    import traceback
                    traceback.print_exc()

        # 保存所有页面信息
        with open(os.path.join(os.path.dirname(__file__), "page_structure.json"), "w", encoding="utf-8") as f:
            json.dump(all_page_info, f, ensure_ascii=False, indent=2)
        print(f"\n页面结构信息已保存到 page_structure.json")

        await browser.close()
        print("探索完成!")


if __name__ == "__main__":
    asyncio.run(main())
