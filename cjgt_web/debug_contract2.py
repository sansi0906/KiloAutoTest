"""
专门调试合同服务下拉
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

        # 监听网络请求
        requests = []
        async def on_request(req):
            if 'serviceItem' in req.url or 'dropdown' in req.url or 'list' in req.url:
                requests.append({'url': req.url, 'method': req.method})
                print(f"  📡 {req.method} {req.url}")
        page.on("request", on_request)

        await page.goto(f"{BASE_URL}/smart-service/contract-service", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        
        # 点击新增
        await page.click('button:has-text("新增合同服务")')
        await page.wait_for_timeout(2000)
        
        print("\n" + "="*60)
        print("合同服务表单分析")
        print("="*60)
        
        # 分析select元素
        selects = page.locator('.ant-modal .ant-select')
        select_count = await selects.count()
        print(f"select数量: {select_count}")
        
        for i in range(select_count):
            sel = selects.nth(i)
            form_item = sel.locator('xpath=ancestor::div[contains(@class,"ant-form-item")]')
            label_el = form_item.locator('.ant-form-item-label label')
            label_text = await label_el.text_content() if await label_el.count() > 0 else '未知'
            
            is_open = await sel.evaluate("el => el.classList.contains('ant-select-open')")
            has_value = await sel.evaluate("el => el.classList.contains('ant-select-single')")
            
            print(f"\nSelect {i}: label='{label_text}', isOpen={is_open}, hasValue={has_value}")
            
            # 获取select内部结构
            inner_html = await sel.evaluate("el => el.innerHTML.substring(0, 300)")
            print(f"  内部HTML: {inner_html[:200]}")
        
        # 尝试用不同方式点击下拉
        print("\n尝试点击第一个select...")
        first_select = selects.first
        
        # 方式1: 点击selector
        selector = first_select.locator('.ant-select-selector')
        await selector.click()
        print("  点击了selector")
        await page.wait_for_timeout(1500)
        
        # 检查下拉是否打开
        is_open = await first_select.evaluate("el => el.classList.contains('ant-select-open')")
        print(f"  isOpen: {is_open}")
        
        # 检查选项
        options = page.locator(".ant-select-item-option")
        opt_count = await options.count()
        print(f"  选项数: {opt_count}")
        
        if opt_count > 0:
            for i in range(min(opt_count, 5)):
                try:
                    text = await options.nth(i).text_content()
                    visible = await options.nth(i).is_visible()
                    print(f"    选项{i}: text='{text}', visible={visible}")
                except Exception as e:
                    print(f"    选项{i}: error={e}")
        else:
            # 尝试等待更长时间
            print("  等待更长时间...")
            await page.wait_for_timeout(2000)
            
            options2 = page.locator(".ant-select-item-option")
            opt_count2 = await options2.count()
            print(f"  等待后选项数: {opt_count2}")
        
        print(f"\n总请求数: {len(requests)}")
        for req in requests:
            print(f"  {req}")
        
        await page.screenshot(path="contract_dropdown.png")
        print("\n截图: contract_dropdown.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
