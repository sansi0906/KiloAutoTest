"""
尝试用Playwright方式操作下拉
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
        
        print("="*60)
        print("尝试用Playwright方式操作下拉")
        print("="*60)
        
        # 方法1: 用标签文本定位select
        select_label = page.get_by_text("所属服务项目").first
        print(f"找到标签: {await select_label.count() > 0}")
        
        # 方法2: 定位表单中的select
        form_item = page.locator('.ant-modal .ant-form-item').filter(has_text="所属服务项目")
        print(f"找到表单项: {await form_item.count() > 0}")
        
        if await form_item.count() > 0:
            select_selector = form_item.locator('.ant-select-selector')
            print(f"找到select: {await select_selector.count() > 0}")
            
            # 点击select
            await select_selector.click()
            print("已点击select")
            await page.wait_for_timeout(1000)
            
            # 检查选项
            options = page.locator(".ant-select-item-option")
            print(f"选项数量: {await options.count()}")
            
            if await options.count() > 0:
                for i in range(min(await options.count(), 5)):
                    try:
                        text = await options.nth(i).text_content()
                        visible = await options.nth(i).is_visible()
                        print(f"  选项{i}: text='{text}', visible={visible}")
                    except Exception as e:
                        print(f"  选项{i}: error={e}")
            else:
                # 尝试用键盘操作
                print("\n尝试用键盘操作...")
                await page.keyboard.press("ArrowDown")
                await page.wait_for_timeout(500)
                
                # 再次检查选项
                options2 = page.locator(".ant-select-item-option")
                print(f"键盘操作后选项数量: {await options2.count()}")
                
                # 检查是否有其他形式的选项
                any_options = page.locator("div[role='option'], li[role='option']")
                print(f"任何role=option的元素: {await any_options.count()}")
                
                # 检查下拉容器
                dropdown = page.locator(".ant-select-dropdown")
                print(f"ant-select-dropdown: {await dropdown.count()}")
                
                popup = page.locator(".ant-select-popup")  
                print(f"ant-select-popup: {await popup.count()}")
                
                # 尝试查看body下的所有popup
                all_absolute = page.locator("body > div[style*='position: absolute']")
                print(f"body下absolute定位的div: {await all_absolute.count()}")
        
        # 也可能下拉需要先输入搜索
        print("\n尝试输入搜索关键字...")
        # 有些select是远程搜索的，需要先输入内容
        search_input = page.locator('.ant-select-selection-search-input')
        if await search_input.count() > 0:
            await search_input.fill("测项")
            await page.wait_for_timeout(1000)
            
            options3 = page.locator(".ant-select-item-option")
            print(f"搜索后选项数量: {await options3.count()}")
        
        await page.screenshot(path="dropdown_pw.png")
        print("\n截图: dropdown_pw.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
