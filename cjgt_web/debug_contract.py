"""
调查合同服务下拉选择问题
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

        # 进入合同服务配置
        await page.goto(f"{BASE_URL}/smart-service/contract-service", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        
        # 查看当前列表
        list_text = await page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || '空'")
        print(f"当前合同服务列表: {list_text[:200]}")
        
        # 点击新增
        await page.click('button:has-text("新增合同服务")')
        await page.wait_for_timeout(2000)
        
        print("\n" + "="*60)
        print("合同服务新增表单分析")
        print("="*60)
        
        # 分析表单结构
        structure = await page.evaluate("""
            () => {
                const result = {
                    formItems: [],
                    selects: [],
                };
                
                // 所有表单项
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    const control = item.querySelector('.ant-form-item-control');
                    
                    // 检查类型
                    let type = 'unknown';
                    if (control) {
                        if (control.querySelector('.ant-select')) {
                            type = 'select';
                        } else if (control.querySelector('input[codefield]')) {
                            type = 'input';
                        } else if (control.querySelector('textarea')) {
                            type = 'textarea';
                        }
                    }
                    
                    result.formItems.push({
                        label: label ? label.textContent.trim() : '无标签',
                        type: type,
                    });
                }
                
                // 所有select元素
                const selects = document.querySelectorAll('.ant-modal .ant-select');
                for (const sel of selects) {
                    const label = sel.closest('.ant-form-item')?.querySelector('.ant-form-item-label label');
                    result.selects.push({
                        label: label ? label.textContent.trim() : '无标签',
                        hasValue: sel.classList.contains('ant-select-single'),
                        placeholder: sel.querySelector('.ant-select-selection-placeholder')?.textContent?.trim(),
                    });
                }
                
                return result;
            }
        """)
        
        print("\n【表单项】")
        for item in structure['formItems']:
            print(f"  - {item['label']}: {item['type']}")
        
        print("\n【Selects】")
        for sel in structure['selects']:
            print(f"  - {sel}")
        
        # 尝试点击"所属服务项目"下拉
        print("\n尝试点击所属服务项目下拉...")
        await page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.includes('所属服务项目')) {
                        const select = item.querySelector('.ant-select-selector');
                        if (select) { 
                            select.click(); 
                            console.log('clicked select');
                        } else {
                            console.log('select not found');
                        }
                    }
                }
            }
        """)
        await page.wait_for_timeout(1000)
        
        # 检查下拉选项
        options = await page.evaluate("""
            () => {
                const dropdowns = document.querySelectorAll('.ant-select-dropdown');
                const results = [];
                for (const dd of dropdowns) {
                    const items = dd.querySelectorAll('.ant-select-item-option');
                    const option_texts = [];
                    for (const item of items) {
                        if (!item.classList.contains('ant-select-item-option-disabled')) {
                            option_texts.push(item.textContent.trim());
                        }
                    }
                    results.push({
                        visible: dd.offsetParent !== null,
                        option_count: items.length,
                        options: option_texts,
                    });
                }
                return results;
            }
        """)
        
        print(f"\n下拉选项: {options}")
        
        # 尝试用Playwright选择
        select_els = page.locator('.ant-select-item-option:not(.ant-select-item-option-disabled)')
        count = await select_els.count()
        print(f"\nPlaywright找到的选项数: {count}")
        
        if count > 0:
            text = await select_els.first.text_content()
            print(f"第一个选项: {text}")
            await select_els.first.click()
            print("已选择第一个选项")
        
        await page.screenshot(path="contract_select_debug.png")
        print("\n截图: contract_select_debug.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
