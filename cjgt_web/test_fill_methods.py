"""
测试用Playwright fill方法操作codefield元素
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

        print("测试服务项目名称的填写方式...")
        
        # 方法1: 使用Playwright的fill方法
        try:
            input_by_id = page.locator('#ServiceProjectForm_itemName')
            if await input_by_id.count() > 0:
                await input_by_id.click()
                await input_by_id.fill("测试填充值1")
                await page.wait_for_timeout(1000)
                value = await input_by_id.input_value()
                print(f"  方法1(fill): input_value={value}")
                await page.screenshot(path="test_fill_method1.png")
        except Exception as e:
            print(f"  方法1失败: {e}")
        
        # 方法2: 使用type方法
        try:
            input_by_id = page.locator('#ServiceProjectForm_itemName')
            if await input_by_id.count() > 0:
                await input_by_id.click()
                await input_by_id.fill("")  # 清空
                await page.wait_for_timeout(300)
                await input_by_id.type("测试填充值2", delay=50)
                await page.wait_for_timeout(1000)
                value = await input_by_id.input_value()
                print(f"  方法2(type): input_value={value}")
                await page.screenshot(path="test_fill_method2.png")
        except Exception as e:
            print(f"  方法2失败: {e}")
        
        # 方法3: 使用press键逐个输入
        try:
            input_by_id = page.locator('#ServiceProjectForm_itemName')
            if await input_by_id.count() > 0:
                await input_by_id.click()
                await page.wait_for_timeout(300)
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Delete")
                await page.keyboard.type("测试填充值3", delay=100)
                await page.wait_for_timeout(1000)
                value = await input_by_id.input_value()
                print(f"  方法3(keyboard): input_value={value}")
                await page.screenshot(path="test_fill_method3.png")
        except Exception as e:
            print(f"  方法3失败: {e}")
        
        # 方法4: 使用React内部状态设置
        try:
            result = await page.evaluate("""
                () => {
                    const inp = document.getElementById('ServiceProjectForm_itemName');
                    if (!inp) return 'not_found';
                    
                    // 模拟React的输入行为
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 
                        'value'
                    ).set;
                    
                    nativeInputValueSetter.call(inp, '测试填充值4');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    return {
                        value: inp.value,
                        formValues: inp.getAttribute('formvalues'),
                    };
                }
            """)
            print(f"  方法4(React setter): {result}")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="test_fill_method4.png")
        except Exception as e:
            print(f"  方法4失败: {e}")

        # 方法5: focus后直接设置值
        try:
            result = await page.evaluate("""
                () => {
                    const inp = document.getElementById('ServiceProjectForm_itemName');
                    if (!inp) return 'not_found';
                    
                    inp.focus();
                    // 等待focus完成
                    return new Promise(resolve => {
                        setTimeout(() => {
                            inp.value = '测试填充值5';
                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                            inp.dispatchEvent(new Event('change', { bubbles: true }));
                            resolve({
                                value: inp.value,
                                formValues: inp.getAttribute('formvalues'),
                            });
                        }, 100);
                    });
                }
            """)
            print(f"  方法5(setTimeout): {result}")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="test_fill_method5.png")
        except Exception as e:
            print(f"  方法5失败: {e}")

        # 方法6: 查看formvalues属性的变化
        print("\n检查formvalues属性变化...")
        formvalues_info = await page.evaluate("""
            () => {
                const inp = document.getElementById('ServiceProjectForm_itemName');
                if (!inp) return null;
                return {
                    value: inp.value,
                    formvalues: inp.getAttribute('formvalues'),
                    type: typeof inp.getAttribute('formvalues'),
                };
            }
        """)
        print(f"  最终状态: {formvalues_info}")
        
        # 检查是否有验证错误
        errors = await page.evaluate("""
            () => Array.from(document.querySelectorAll('.ant-form-item-explain-error')).map(e => e.textContent.trim())
        """)
        print(f"  当前验证错误: {errors}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
