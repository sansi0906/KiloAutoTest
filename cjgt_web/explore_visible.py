"""
快速探索每个表单的可见输入框
"""
import asyncio
import os
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

        # 探索函数
        async def explore(page_name, path, button_text):
            print(f"\n{'='*60}\n探索: {page_name}\n{'='*60}")
            
            await page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
            await page.wait_for_timeout(1500)
            
            # 点击新增
            await page.click(f'button:has-text("{button_text}")')
            await page.wait_for_timeout(1500)
            
            # 获取所有可见的输入元素
            visible_inputs = await page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('.ant-modal input.ant-input');
                    const result = [];
                    for (let i = 0; i < inputs.length; i++) {
                        const inp = inputs[i];
                        const visible = inp.offsetParent !== null;
                        const codefield = inp.hasAttribute('codefield');
                        const rect = inp.getBoundingClientRect();
                        result.push({
                            index: i,
                            visible: visible,
                            codefield: codefield,
                            placeholder: inp.placeholder,
                            rect: { top: Math.round(rect.top), left: Math.round(rect.left), width: Math.round(rect.width) }
                        });
                    }
                    return result;
                }
            """)
            
            print(f"\n  所有input.ant-input元素:")
            for inp in visible_inputs:
                status = "✅可见" if inp['visible'] else "❌隐藏"
                cf = "[codefield]" if inp['codefield'] else ""
                print(f"    [{inp['index']}] {status} {cf} placeholder='{inp['placeholder']}' rect={inp['rect']}")
            
            # 获取可见的form-item和它们的label
            form_items = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll('.ant-modal .ant-form-item');
                    const result = [];
                    for (let i = 0; i < items.length; i++) {
                        const item = items[i];
                        const label = item.querySelector('.ant-form-item-label label');
                        const labelText = label ? label.textContent.trim() : '';
                        const visible = item.offsetParent !== null;
                        
                        // 获取该form-item内的可见input
                        const inputs = item.querySelectorAll('input.ant-input');
                        const visible_inputs = [];
                        for (const inp of inputs) {
                            if (inp.offsetParent !== null && !inp.hasAttribute('codefield')) {
                                visible_inputs.push({
                                    placeholder: inp.placeholder,
                                    type: inp.type
                                });
                            }
                        }
                        
                        if (visible || visible_inputs.length > 0) {
                            result.push({
                                index: i,
                                label: labelText,
                                visible: visible,
                                visible_inputs: visible_inputs
                            });
                        }
                    }
                    return result;
                }
            """)
            
            print(f"\n  可见form-items:")
            for item in form_items:
                if item['visible'] or item['visible_inputs']:
                    print(f"    [{item['index']}] label='{item['label']}' visible_inputs={item['visible_inputs']}")
            
            # 关闭弹窗
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)

        # 探索各个表单
        await explore("服务项目配置", "/smart-service/project-config", "新增服务项目")
        await explore("合同服务配置", "/smart-service/contract-service", "新增合同服务")
        await explore("经营范围配置", "/smart-service/scope-config", "新增经营范围")
        await explore("知识库", "/content-manage/knowledge", "新增知识库")

        await browser.close()
        print("\n探索完成!")


if __name__ == "__main__":
    asyncio.run(main())
