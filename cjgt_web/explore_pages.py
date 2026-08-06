"""
超级个体后台管理系统 - 页面结构探索脚本
探索智能服务配置、内容管理模块的页面结构
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def explore_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 1. 登录
        print("=" * 60)
        print("步骤1: 登录系统")
        print("=" * 60)
        await page.goto(LOGIN_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 填写账号密码
        inputs = await page.query_selector_all("input")
        print(f"找到 {len(inputs)} 个输入框")
        for i, inp in enumerate(inputs):
            placeholder = await inp.get_attribute("placeholder")
            input_type = await inp.get_attribute("type")
            print(f"  输入框[{i}]: type={input_type}, placeholder={placeholder}")

        # 输入账号
        account_input = page.locator('input[placeholder*="账号"], input[placeholder*="手机"], input[placeholder*="用户"]').first
        await account_input.fill(USERNAME)
        print(f"已输入账号: {USERNAME}")

        # 输入密码
        pwd_input = page.locator('input[type="password"], input[placeholder*="密码"]').first
        await pwd_input.fill(PASSWORD)
        print(f"已输入密码: {PASSWORD}")

        # 点击登录按钮
        login_btn = page.locator('button:has-text("登录"), button:has-text("登 录")').first
        await login_btn.click()
        print("已点击登录按钮")

        await page.wait_for_timeout(3000)
        print(f"登录后URL: {page.url}")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_after_login.png"))

        # 2. 探索左侧菜单结构
        print("\n" + "=" * 60)
        print("步骤2: 探索左侧菜单结构")
        print("=" * 60)

        # 获取所有菜单项
        menu_items = await page.query_selector_all('.jeecg-menu, .ant-menu-item, .ant-menu-submenu-title, [class*="menu"]')
        print(f"找到 {len(menu_items)} 个菜单相关元素")

        # 尝试获取菜单文本
        menu_texts = []
        for item in menu_items:
            text = await item.inner_text()
            if text and text.strip():
                menu_texts.append(text.strip())
        print(f"菜单文本: {menu_texts}")

        # 3. 探索智能服务配置模块
        print("\n" + "=" * 60)
        print("步骤3: 探索智能服务配置模块")
        print("=" * 60)

        # 尝试点击智能服务配置菜单
        smart_service_menu = page.locator('text=智能服务配置').first
        if await smart_service_menu.count() > 0:
            print("找到'智能服务配置'菜单项")
            # 先尝试点击
            await smart_service_menu.click()
            await page.wait_for_timeout(2000)
            print(f"点击后URL: {page.url}")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_smart_service_config.png"))

            # 检查是否有子菜单展开
            submenus = await page.query_selector_all('.ant-menu-submenu-open .ant-menu-item, .jeecg-simple-menu__child .jeecg-simple-menu-item')
            print(f"子菜单项数量: {len(submenus)}")
            submenu_texts = []
            for sm in submenus:
                text = await sm.inner_text()
                if text and text.strip():
                    submenu_texts.append(text.strip())
            print(f"子菜单: {submenu_texts}")

            # 如果没有展开，尝试找展开箭头
            if not submenu_texts:
                print("尝试通过父元素展开子菜单...")
                parent = smart_service_menu.locator('..')
                await parent.click()
                await page.wait_for_timeout(2000)
                submenus = await page.query_selector_all('.ant-menu-submenu-open .ant-menu-item, .jeecg-simple-menu__child .jeecg-simple-menu-item')
                submenu_texts = []
                for sm in submenus:
                    text = await sm.inner_text()
                    if text and text.strip():
                        submenu_texts.append(text.strip())
                print(f"再次尝试后子菜单: {submenu_texts}")

            # 逐一点击子菜单并记录页面结构
            for i, sm_text in enumerate(submenu_texts):
                print(f"\n--- 探索子菜单: {sm_text} ---")
                try:
                    sm_locator = page.locator(f'text={sm_text}').first
                    await sm_locator.click()
                    await page.wait_for_timeout(2000)
                    current_url = page.url
                    print(f"  URL: {current_url}")

                    # 截图
                    safe_name = sm_text.replace("/", "_").replace("\\", "_")
                    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"03_smart_{i}_{safe_name}.png"))

                    # 获取页面标题
                    titles = await page.query_selector_all('h1, h2, h3, .ant-page-header-heading-title, .title')
                    for t in titles:
                        title_text = await t.inner_text()
                        if title_text and title_text.strip():
                            print(f"  页面标题: {title_text.strip()}")
                            break

                    # 获取表格列头
                    ths = await page.query_selector_all('th, .ant-table-thead th')
                    th_texts = []
                    for th in ths:
                        text = await th.inner_text()
                        if text and text.strip():
                            th_texts.append(text.strip())
                    if th_texts:
                        print(f"  表格列: {th_texts}")

                    # 获取按钮
                    buttons = await page.query_selector_all('button, .ant-btn')
                    btn_texts = []
                    for btn in buttons:
                        text = await btn.inner_text()
                        if text and text.strip() and len(text.strip()) < 20:
                            btn_texts.append(text.strip())
                    if btn_texts:
                        print(f"  按钮: {btn_texts}")

                    # 获取表单字段
                    form_items = await page.query_selector_all('.ant-form-item-label label, .ant-form-item label')
                    form_texts = []
                    for fi in form_items:
                        text = await fi.inner_text()
                        if text and text.strip():
                            form_texts.append(text.strip())
                    if form_texts:
                        print(f"  表单字段: {form_texts}")

                    # 获取搜索区域
                    search_inputs = await page.query_selector_all('.ant-table-filter-dropdown input, .ant-input-search input, input[placeholder]')
                    search_placeholders = []
                    for si in search_inputs:
                        ph = await si.get_attribute("placeholder")
                        if ph:
                            search_placeholders.append(ph)
                    if search_placeholders:
                        print(f"  搜索/输入框: {search_placeholders}")

                except Exception as e:
                    print(f"  探索出错: {e}")
        else:
            print("未找到'智能服务配置'菜单项")

        # 4. 探索内容管理模块
        print("\n" + "=" * 60)
        print("步骤4: 探索内容管理模块")
        print("=" * 60)

        content_menu = page.locator('text=内容管理').first
        if await content_menu.count() > 0:
            print("找到'内容管理'菜单项")
            await content_menu.click()
            await page.wait_for_timeout(2000)
            print(f"点击后URL: {page.url}")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_content_management.png"))

            # 检查子菜单
            submenus = await page.query_selector_all('.ant-menu-submenu-open .ant-menu-item, .jeecg-simple-menu__child .jeecg-simple-menu-item')
            print(f"子菜单项数量: {len(submenus)}")
            submenu_texts = []
            for sm in submenus:
                text = await sm.inner_text()
                if text and text.strip():
                    submenu_texts.append(text.strip())
            print(f"子菜单: {submenu_texts}")

            # 逐一点击子菜单
            for i, sm_text in enumerate(submenu_texts):
                print(f"\n--- 探索子菜单: {sm_text} ---")
                try:
                    sm_locator = page.locator(f'text={sm_text}').first
                    await sm_locator.click()
                    await page.wait_for_timeout(2000)
                    current_url = page.url
                    print(f"  URL: {current_url}")

                    safe_name = sm_text.replace("/", "_").replace("\\", "_")
                    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"05_content_{i}_{safe_name}.png"))

                    # 获取页面标题
                    titles = await page.query_selector_all('h1, h2, h3, .ant-page-header-heading-title, .title')
                    for t in titles:
                        title_text = await t.inner_text()
                        if title_text and title_text.strip():
                            print(f"  页面标题: {title_text.strip()}")
                            break

                    # 获取表格列头
                    ths = await page.query_selector_all('th, .ant-table-thead th')
                    th_texts = []
                    for th in ths:
                        text = await th.inner_text()
                        if text and text.strip():
                            th_texts.append(text.strip())
                    if th_texts:
                        print(f"  表格列: {th_texts}")

                    # 获取按钮
                    buttons = await page.query_selector_all('button, .ant-btn')
                    btn_texts = []
                    for btn in buttons:
                        text = await btn.inner_text()
                        if text and text.strip() and len(text.strip()) < 20:
                            btn_texts.append(text.strip())
                    if btn_texts:
                        print(f"  按钮: {btn_texts}")

                    # 获取表单字段
                    form_items = await page.query_selector_all('.ant-form-item-label label, .ant-form-item label')
                    form_texts = []
                    for fi in form_items:
                        text = await fi.inner_text()
                        if text and text.strip():
                            form_texts.append(text.strip())
                    if form_texts:
                        print(f"  表单字段: {form_texts}")

                    # 获取搜索区域
                    search_inputs = await page.query_selector_all('input[placeholder]')
                    search_placeholders = []
                    for si in search_inputs:
                        ph = await si.get_attribute("placeholder")
                        if ph:
                            search_placeholders.append(ph)
                    if search_placeholders:
                        print(f"  搜索/输入框: {search_placeholders}")

                except Exception as e:
                    print(f"  探索出错: {e}")
        else:
            print("未找到'内容管理'菜单项")

        # 5. 获取完整的页面HTML结构（用于分析）
        print("\n" + "=" * 60)
        print("步骤5: 保存页面HTML结构")
        print("=" * 60)

        # 回到首页
        await page.goto(f"{BASE_URL}/dashboard/analysis", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 保存左侧菜单HTML
        menu_html = await page.query_selector('.ant-pro-sider-menu, .ant-layout-sider, [class*="sider"], [class*="menu-container"]')
        if menu_html:
            html_content = await menu_html.inner_html()
            with open(os.path.join(SCREENSHOT_DIR, "menu_structure.html"), "w", encoding="utf-8") as f:
                f.write(html_content)
            print("菜单HTML已保存")

        # 保存完整页面HTML
        full_html = await page.content()
        with open(os.path.join(SCREENSHOT_DIR, "full_page.html"), "w", encoding="utf-8") as f:
            f.write(full_html)
        print("完整页面HTML已保存")

        await browser.close()
        print("\n探索完成!")


if __name__ == "__main__":
    asyncio.run(explore_pages())
