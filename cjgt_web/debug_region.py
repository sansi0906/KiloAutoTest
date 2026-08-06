#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试适用区域下拉结构"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 登录
        await page.goto("http://172.16.1.165:9100/adminLogin")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)
        
        # 填写登录表单
        await page.fill('input[placeholder="账号"]', '17695729351')
        await page.fill('input[type="password"]', '123456')
        await page.wait_for_timeout(500)
        await page.click('button:has-text("登 录")')
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 导航到知识库页面
        await page.goto("http://172.16.1.165:9100/content-manage/knowledge")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)
        
        # 点击新增知识库
        await page.click('button:has-text("新增知识库")')
        await page.wait_for_timeout(1500)
        
        print("\n=== 知识库新增表单结构 ===")
        
        # 检查所有表单项
        form_items = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.ant-modal .ant-form-item');
                const results = [];
                items.forEach(item => {
                    const label = item.querySelector('label, .ant-form-item-label');
                    const labelText = label ? label.textContent.trim() : '无标签';
                    
                    // 检查是否有select
                    const select = item.querySelector('.ant-select');
                    const selectInfo = select ? {
                        hasSelect: true,
                        selectId: select.id || '无ID',
                        selectClasses: select.className,
                        placeholder: select.querySelector('.ant-select-selection-placeholder')?.textContent?.trim() || '无'
                    } : null;
                    
                    results.push({
                        label: labelText,
                        hasSelect: !!select,
                        selectInfo: selectInfo
                    });
                });
                return results;
            }
        """)
        
        for item in form_items:
            print(f"  标签: {item['label']}")
            if item['hasSelect']:
                print(f"    有Select组件")
                if item['selectInfo']:
                    print(f"    占位符: {item['selectInfo']['placeholder']}")
                    print(f"    类名: {item['selectInfo']['selectClasses'][:100]}")
            print()
        
        # 尝试点击适用区域的下拉
        print("\n=== 尝试点击适用区域下拉 ===")
        
        # 先清理所有已有下拉
        await page.evaluate("""
            () => {
                const popups = document.querySelectorAll('.ant-select-dropdown-wrapper, .ant-select-dropdown');
                popups.forEach(p => p.remove());
            }
        """)
        
        await page.wait_for_timeout(200)
        
        # 点击适用区域的下拉
        region_select = page.locator('.ant-modal .ant-form-item').filter(has_text='适用区域').locator('.ant-select-selector')
        if await region_select.count() > 0:
            print("找到适用区域的select选择器")
            await region_select.click(force=True)
            await page.wait_for_timeout(2000)
            
            # 检查下拉是否打开
            dropdown_info = await page.evaluate("""
                () => {
                    // 检查级联选择器的结构
                    const cascaderPanels = document.querySelectorAll('.ant-cascader-menu');
                    const selectDropdowns = document.querySelectorAll('.ant-select-dropdown');
                    
                    const cascaderInfo = {
                        cascaderCount: cascaderPanels.length,
                        cascaderMenus: []
                    };
                    
                    cascaderPanels.forEach((menu, i) => {
                        const items = menu.querySelectorAll('.ant-cascader-menu-item');
                        cascaderInfo.cascaderMenus.push({
                            index: i,
                            itemsCount: items.length,
                            items: Array.from(items).map(item => ({
                                text: item.textContent.trim(),
                                hasChildren: item.classList.contains('ant-cascader-menu-item-expand')
                            }))
                        });
                    });
                    
                    const selectInfo = {
                        selectCount: selectDropdowns.length,
                        options: []
                    };
                    
                    selectDropdowns.forEach((d, i) => {
                        const options = d.querySelectorAll('.ant-select-item-option');
                        selectInfo.options.push({
                            index: i,
                            optionsCount: options.length,
                            visible: d.style.display !== 'none'
                        });
                    });
                    
                    return {
                        cascaderInfo: cascaderInfo,
                        selectInfo: selectInfo
                    };
                }
            """)
            
            print(f"\n级联菜单数: {dropdown_info['cascaderInfo']['cascaderCount']}")
            for menu in dropdown_info['cascaderInfo']['cascaderMenus']:
                print(f"  菜单{menu['index']}: 选项数={menu['itemsCount']}")
                for item in menu['items']:
                    print(f"    - {item['text']} {'(有子项)' if item['hasChildren'] else ''}")
            
            print(f"\n普通下拉数: {dropdown_info['selectInfo']['selectCount']}")
            for opt in dropdown_info['selectInfo']['options']:
                print(f"  下拉{opt['index']}: 选项数={opt['optionsCount']}, 可见={opt['visible']}")
        else:
            print("未找到适用区域的select选择器")
        
        await page.wait_for_timeout(1000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
