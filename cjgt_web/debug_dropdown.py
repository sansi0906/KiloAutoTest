"""
调查下拉菜单的渲染位置
"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://172.16.1.165:9100"
LOGIN_URL = f"{BASE_URL}/adminLogin"
USERNAME = "17695729351"
PASSWORD = "123456"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        await page.goto(LOGIN_URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.fill('input[placeholder="账号"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button:has-text("登 录")')
        await page.wait_for_timeout(2000)

        await page.goto(f"{BASE_URL}/smart-service/contract-service", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        
        await page.click('button:has-text("新增合同服务")')
        await page.wait_for_timeout(2000)
        
        # 点击"所属服务项目"下拉
        await page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.includes('所属服务项目')) {
                        const select = item.querySelector('.ant-select-selector');
                        if (select) { select.click(); }
                    }
                }
            }
        """)
        await page.wait_for_timeout(1500)
        
        print("="*60)
        print("查找下拉选项")
        print("="*60)
        
        # 用Playwright的选择器查找
        select_triggers = page.locator('.ant-select')
        count = await select_triggers.count()
        print(f"ant-select数量: {count}")
        
        # 检查每个select的状态
        for i in range(count):
            sel = select_triggers.nth(i)
            try:
                # 获取关联的label
                form_item = sel.locator('xpath=ancestor::div[contains(@class,"ant-form-item")]')
                label_el = form_item.locator('.ant-form-item-label label')
                label_text = await label_el.text_content() if await label_el.count() > 0 else '未知'
                
                # 检查是否有值
                placeholder = sel.locator('.ant-select-selection-placeholder')
                has_placeholder = await placeholder.count() > 0
                
                selector_view = sel.locator('.ant-select-selector')
                is_focused = await selector_view.evaluate("el => document.activeElement === el")
                
                print(f"\nSelect {i}: label='{label_text}', hasPlaceholder={has_placeholder}, isFocused={is_focused}")
            except Exception as e:
                print(f"\nSelect {i}: error={e}")
        
        # 查找下拉选项 - 可能在body的顶层
        print("\n查找所有可能的下拉选项...")
        
        # 方法1: 直接查找
        options = page.locator(".ant-select-item-option")
        opt_count = await options.count()
        print(f"方法1 (ant-select-item-option): {opt_count}")
        
        # 方法2: 查找所有listbox选项
        listbox_options = page.locator("[role='option']")
        lb_count = await listbox_options.count()
        print(f"方法2 (role=option): {lb_count}")
        
        # 方法3: 查找所有可见的弹出层
        popups = page.locator(".ant-select-dropdown, .ant-select-popup")
        popup_count = await popups.count()
        print(f"方法3 (dropdown/popup): {popup_count}")
        
        # 方法4: 查找所有绝对定位的元素
        popup_elements = page.locator("div[style*='position: absolute']")
        pe_count = await popup_elements.count()
        print(f"方法4 (absolute定位): {pe_count}")
        
        # 如果找到了选项，尝试点击第一个
        if opt_count > 0:
            visible_opts = []
            for i in range(opt_count):
                try:
                    is_visible = await options.nth(i).is_visible()
                    text = await options.nth(i).text_content()
                    if is_visible:
                        visible_opts.append((i, text))
                except:
                    pass
            
            print(f"\n可见选项: {visible_opts}")
            
            if visible_opts:
                idx, text = visible_opts[0]
                print(f"点击第一个可见选项: {text}")
                await options.nth(idx).click()
                print("已点击")
        
        await page.screenshot(path="dropdown_debug.png")
        print("\n截图: dropdown_debug.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
