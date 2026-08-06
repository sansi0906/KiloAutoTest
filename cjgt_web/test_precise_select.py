"""
测试精确选择input元素的方法
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

        # 登录
        await page.goto(LOGIN_URL, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.fill('input[placeholder="账号"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button:has-text("登 录")')
        await page.wait_for_timeout(2000)

        # 进入服务项目配置
        await page.goto(f"{BASE_URL}/smart-service/project-config", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.click('button:has-text("新增服务项目")')
        await page.wait_for_timeout(1500)

        print("测试精确选择input元素...")
        
        # 使用更精确的选择器: input#id
        try:
            # 选择input元素而不是div
            input_el = page.locator('input#ServiceProjectForm_itemName')
            if await input_el.count() > 0:
                print(f"找到input元素: count={await input_el.count()}")
                
                # 尝试fill
                await input_el.first.click()
                await input_el.first.fill("")
                await input_el.first.fill("测试精确选择")
                await page.wait_for_timeout(500)
                
                value = await input_el.first.input_value()
                print(f"  fill后值: {value}")
                
                await page.screenshot(path="test_precise_select.png")
        except Exception as e:
            print(f"  精确选择失败: {e}")
        
        # 使用代码字段属性选择
        try:
            input_el = page.locator('input[codefield="itemName"]')
            if await input_el.count() > 0:
                print(f"找到codefield元素: count={await input_el.count()}")
                
                await input_el.first.click()
                await input_el.first.fill("")
                await input_el.first.fill("测试codefield选择")
                await page.wait_for_timeout(500)
                
                value = await input_el.first.input_value()
                print(f"  codefield选择后值: {value}")
                
                await page.screenshot(path="test_codefield_select.png")
        except Exception as e:
            print(f"  codefield选择失败: {e}")
        
        # 检查当前状态
        status = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('.ant-modal input[codefield]');
                const results = [];
                for (const inp of inputs) {
                    results.push({
                        codefield: inp.getAttribute('codefield'),
                        value: inp.value,
                        visible: inp.offsetParent !== null,
                    });
                }
                return results;
            }
        """)
        print(f"\n当前codefield元素状态:")
        for s in status:
            print(f"  {s}")
        
        # 检查验证错误
        errors = await page.evaluate("""
            () => Array.from(document.querySelectorAll('.ant-form-item-explain-error')).map(e => e.textContent.trim())
        """)
        print(f"\n当前验证错误: {errors}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
