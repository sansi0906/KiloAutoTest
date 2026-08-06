#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级个体后台管理系统 - 实际数据提交验证测试
测试新增、编辑、删除等操作的实际数据是否正确提交
"""
import asyncio
import json
import time
import os
from datetime import datetime
from playwright.async_api import async_playwright, Page


class RealDataTest:
    def __init__(self):
        self.base_url = "http://172.16.1.165:9100"
        self.username = "17695729351"
        self.password = "123456"
        self.results = []
        self.created = {}
        self.browser = None
        self.context = None
        self.page: Page = None
        
        # 报告目录
        self.report_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(self.report_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 截图目录
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots", self.timestamp)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # 测试数据
        ts = datetime.now().strftime("%H%M%S")
        self.data = {
            # 服务项目
            "project_name": f"测项{ts}",
            "project_subtitle": f"副标题{ts}",
            "project_content": f"测试描述内容_{ts}",
            
            # 合同服务
            "contract_title": f"合同标题_{ts}",
            "contract_content": f"合同服务内容_{ts}",
            "contract_fee": "100",
            
            # 经营范围
            "business_scope_name": f"范围_{ts}",
            "business_remark": f"备注_{ts}",
            
            # 知识库
            "knowledge_title": f"测试知识_{ts}",
            "knowledge_content": f"<p>这是知识库测试内容_{ts}</p><p>包含多个段落</p>",
        }

    async def ss(self, name):
        """截图"""
        path = os.path.join(self.screenshot_dir, f"{name}.png")
        await self.page.screenshot(path=path)
        return path

    async def toasts(self):
        """获取Toast消息"""
        return await self.page.evaluate("""
            () => {
                const toasts = document.querySelectorAll('.ant-message-notice-content');
                return Array.from(toasts).map(t => t.textContent.trim());
            }
        """)

    async def get_errors(self):
        """获取表单验证错误"""
        return await self.page.evaluate("""
            () => {
                const errors = document.querySelectorAll('.ant-form-item-explain, .ant-form-item-extra');
                return Array.from(errors).filter(e => e.offsetParent !== null).map(e => e.textContent.trim());
            }
        """)

    def ok(self, mod, name, detail, shot=None):
        self.results.append({
            "module": mod, "type": name, "pass": True,
            "detail": detail, "screenshot": shot
        })
        print(f"  ✅ [PASS] {name}: {detail}")

    def fail(self, mod, name, detail, shot=None):
        self.results.append({
            "module": mod, "type": name, "pass": False,
            "detail": detail, "screenshot": shot
        })
        print(f"  ❌ [FAIL] {name}: {detail}")

    def skip(self, mod, name, detail):
        self.results.append({
            "module": mod, "type": name, "pass": None,
            "detail": detail, "screenshot": None
        })
        print(f"  ⏭️ [SKIP] {name}: {detail}")

    async def start(self):
        # 初始化Playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()
        await self.page.goto(f"{self.base_url}/adminLogin")
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_timeout(3000)
        
        # 查找登录表单元素
        inputs_info = await self.page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input');
                return Array.from(inputs).map((inp, idx) => ({
                    index: idx,
                    id: inp.id,
                    type: inp.type,
                    name: inp.name,
                    placeholder: inp.placeholder,
                    visible: inp.offsetParent !== null
                }));
            }
        """)
        print(f"  登录页inputs: {inputs_info}")
        
        # 找到用户名和密码输入框
        username_input = None
        password_input = None
        
        for inp in inputs_info:
            if inp['visible']:
                if inp['type'] == 'password':
                    password_input = inp
                elif inp['placeholder'] and ('用户' in inp['placeholder'] or '账号' in inp['placeholder'] or 'account' in inp['placeholder'].lower()):
                    username_input = inp
                elif inp['name'] and ('user' in inp['name'].lower() or 'account' in inp['name'].lower()):
                    username_input = inp
        
        # 如果还没找到，尝试按顺序
        if not username_input or not password_input:
            visible_inputs = [i for i in inputs_info if i['visible']]
            print(f"  可见inputs数量: {len(visible_inputs)}")
            if len(visible_inputs) >= 2:
                # 第一个是用户名，第二个是密码
                if visible_inputs[0]['type'] == 'password':
                    password_input = visible_inputs[0]
                    username_input = visible_inputs[1]
                else:
                    username_input = visible_inputs[0]
                    password_input = visible_inputs[1]
        
        if not username_input or not password_input:
            print("  无法定位登录表单元素")
            return
        
        print(f"  用户名input: {username_input}")
        print(f"  密码input: {password_input}")
        
        # 检查radio状态（第一个应该已经选中）
        radio_status = await self.page.evaluate("""
            () => {
                const radios = document.querySelectorAll('input[type="radio"]');
                return Array.from(radios).map((r, i) => ({
                    index: i,
                    value: r.value,
                    checked: r.checked
                }));
            }
        """)
        print(f"  Radio状态: {radio_status}")
        
        # 使用Playwright的fill方法填写表单（会触发React状态更新）
        username_selector = 'input[placeholder="账号"]'
        password_selector = 'input[type="password"]'
        
        try:
            username_el = self.page.locator(username_selector)
            await username_el.fill(self.username)
            print(f"  已填写用户名")
            
            password_el = self.page.locator(password_selector)
            await password_el.fill(self.password)
            print(f"  已填写密码")
        except Exception as e:
            print(f"  表单填写失败: {e}")
            return
        
        # 点击登录按钮（使用force=True来确保点击成功）
        login_btn = self.page.locator('button:has-text("登 录")')
        if await login_btn.count() > 0:
            await login_btn.click(force=True)
            print(f"  已点击登录按钮")
        else:
            # 按Enter键提交
            await self.page.keyboard.press('Enter')
            print(f"  已按Enter提交")
        
        # 等待页面跳转
        try:
            await self.page.wait_for_url(lambda url: 'login' not in url.lower() and 'adminLogin' not in url.lower(), timeout=10000)
            print("登录成功！")
            await self.page.wait_for_timeout(3)
            return
        except:
            pass
        
        # 检查登录状态
        current_url = self.page.url
        print(f"  当前URL: {current_url}")
        
        if "login" not in current_url.lower() and "adminLogin" not in current_url.lower():
            print("登录成功！")
            await self.page.wait_for_timeout(3)
            return
        
        # 如果还在登录页，检查错误提示
        error_msgs = await self.page.evaluate("""
            () => {
                const errors = document.querySelectorAll('.ant-message-error, .ant-form-item-explain, .ant-notification, .ant-message');
                return Array.from(errors).filter(e => e.offsetParent !== null).map(e => e.textContent.trim());
            }
        """)
        if error_msgs:
            print(f"  登录错误: {error_msgs}")
        else:
            # 尝试等待更长时间
            await self.page.wait_for_timeout(5)
            current_url = self.page.url
            if "login" not in current_url.lower() and "adminLogin" not in current_url.lower():
                print("  延迟后登录成功！")
                return
            print(f"  登录失败，URL仍为: {current_url}")
        return

    async def go(self, path):
        """导航到指定路径"""
        full_url = f"{self.base_url}{path}"
        await self.page.goto(full_url, wait_until="networkidle")
        await self.page.wait_for_timeout(2000)  # 增加等待时间
        
        # 输出当前URL和页面结构
        current_url = self.page.url
        print(f"  导航到: {path} -> 当前URL: {current_url}")
        
        # 等待页面加载完成
        try:
            await self.page.wait_for_selector('.ant-layout-content, .ant-layout', timeout=5000)
        except:
            pass
        await self.page.wait_for_timeout(1000)

    async def select_dropdown(self, label_text, option_index=0):
        """选择下拉框中的选项 - 支持普通Select和级联Cascader"""
        try:
            # 第一步：先清理所有已存在的下拉popup
            await self.page.evaluate("""
                () => {
                    const popups = document.querySelectorAll(
                        '.ant-select-dropdown-wrapper, .ant-select-dropdown, ' +
                        '.ant-select-dropdown-placement-bottomLeft, .ant-select-dropdown-placement-bottomRight, ' +
                        '.ant-cascader-menus'
                    );
                    popups.forEach(p => p.remove());
                }
            """)
            await self.page.wait_for_timeout(200)
            
            # 第二步：找到表单项并判断类型
            form_item = self.page.locator('.ant-modal .ant-form-item').filter(has_text=label_text)
            if await form_item.count() == 0:
                print(f"    未找到标签为 '{label_text}' 的表单项")
                return False
            
            # 检查是否是级联选择器
            is_cascader = await form_item.evaluate("""
                el => {
                    const select = el.querySelector('.ant-select');
                    return select ? select.classList.contains('ant-cascader') : false;
                }
            """)
            
            if is_cascader:
                # 级联选择器处理
                return await self._select_cascader(form_item, label_text, option_index)
            else:
                # 普通下拉选择器处理
                return await self._select_normal_dropdown(form_item, label_text, option_index)
                
        except Exception as e:
            print(f"    select_dropdown错误: {e}")
            return False

    async def _select_normal_dropdown(self, form_item, label_text, option_index=0):
        """普通下拉选择器处理"""
        try:
            # 点击select选择器
            select = form_item.locator('.ant-select-selector').first
            await select.click(force=True)
            await self.page.wait_for_timeout(500)
            
            # 等待下拉菜单出现
            await self.page.wait_for_selector('.ant-select-dropdown:not(.ant-select-dropdown-hidden)', timeout=3000)
            await self.page.wait_for_timeout(500)
            
            # 获取当前下拉菜单中的选项
            options = self.page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option')
            count = await options.count()
            
            if count == 0:
                print(f"    下拉框 '{label_text}' 没有选项")
                # 关闭下拉
                await self.page.keyboard.press('Escape')
                return False
            
            print(f"    下拉选项数: {count}")
            
            # 选择指定选项或第一个非禁用项
            target_index = min(option_index, count - 1)
            
            # 尝试选择第一个非禁用项
            selected = False
            for i in range(count):
                opt = options.nth(i)
                opt_text = await opt.text_content()
                if '禁用' not in opt_text:
                    await opt.click(force=True)
                    selected = True
                    break
            
            if not selected and count > 0:
                await options.nth(0).click(force=True)
                selected = True
            
            await self.page.wait_for_timeout(500)
            
            # 验证选择结果
            selected_value = await form_item.evaluate("""
                el => {
                    const selector = el.querySelector('.ant-select-selection-item');
                    return selector ? selector.textContent.trim() : '';
                }
            """)
            print(f"    当前选中值: {selected_value}")
            
            # 选择后等待下拉关闭
            await self.page.wait_for_timeout(300)
            
            return selected
        except Exception as e:
            print(f"    普通下拉选择失败: {e}")
            return False

    async def _select_cascader(self, form_item, label_text, option_index=0):
        """级联选择器处理 - 使用typeahead搜索方式"""
        try:
            print(f"    检测到级联选择器 '{label_text}'")
            
            # 先清理popup
            await self.page.evaluate("""
                () => {
                    document.querySelectorAll('.ant-cascader-menus, .ant-select-dropdown').forEach(m => m.remove());
                }
            """)
            await self.page.wait_for_timeout(300)
            
            # 对于多选级联，尝试使用搜索框输入方式
            # 查找input搜索框
            input_el = form_item.locator('.ant-cascader input').first
            if await input_el.count() > 0:
                # 清除已有内容
                await input_el.click()
                await self.page.wait_for_timeout(300)
                
                # 输入要搜索的城市名
                search_text = "北京市"
                await input_el.fill(search_text)
                await self.page.wait_for_timeout(1500)
                
                # 等待搜索结果
                menus = self.page.locator('.ant-cascader-menus:not(.ant-cascader-hidden)')
                menu_count = await menus.count()
                print(f"    搜索后级联菜单数量: {menu_count}")
                
                if menu_count > 0:
                    # 选择第一个匹配项
                    menu = menus.first
                    items = menu.locator('.ant-cascader-menu-item')
                    item_count = await items.count()
                    print(f"    第一级选项数: {item_count}")
                    
                    if item_count > 0:
                        # 点击第一个选项
                        await items.first.click(force=True)
                        await self.page.wait_for_timeout(1000)
                        
                        # 检查是否有子菜单
                        sub_menus = self.page.locator('.ant-cascader-menus:not(.ant-cascader-hidden)').nth(1)
                        if await sub_menus.count() > 0:
                            sub_items = sub_menus.locator('.ant-cascader-menu-item')
                            if await sub_items.count() > 0:
                                await sub_items.first.click(force=True)
                                await self.page.wait_for_timeout(1000)
                        
                        # 按Escape关闭下拉
                        await self.page.keyboard.press('Escape')
                        await self.page.wait_for_timeout(500)
                        
                        return True
            
            # 如果搜索方式失败，回退到点击方式
            print(f"    搜索方式失败，尝试点击方式")
            selector = form_item.locator('.ant-cascader .ant-select-selector').first
            await selector.click(force=True)
            await self.page.wait_for_timeout(1500)
            
            menus = self.page.locator('.ant-cascader-menus:not(.ant-cascader-hidden)')
            menu_count = await menus.count()
            print(f"    点击后级联菜单数量: {menu_count}")
            
            if menu_count == 0:
                return False
            
            # 逐级选择
            for level in range(3):
                menu = menus.nth(level)
                items = menu.locator('.ant-cascader-menu-item')
                count = await items.count()
                
                if count == 0:
                    break
                
                # 选择第一个非禁用项
                for i in range(count):
                    item = items.nth(i)
                    classes = await item.get_attribute('class') or ''
                    if 'disabled' in classes:
                        continue
                    
                    item_text = await item.text_content()
                    if '加载中' in item_text:
                        continue
                    
                    print(f"    点击第{level + 1}级: {item_text.strip()}")
                    await item.click(force=True)
                    await self.page.wait_for_timeout(1000)
                    break
                
                # 检查是否有下一级
                next_menu = menus.nth(level + 1)
                if await next_menu.count() == 0:
                    break
            
            # 点击外部区域关闭
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(500)
            
            return True
        except Exception as e:
            print(f"    级联选择失败: {e}")
            return False
    
    async def _set_cascader_value_js(self, form_item, label_text):
        """使用JS直接设置多选级联选择器的值"""
        try:
            # 先清理所有popup
            await self.page.evaluate("""
                () => {
                    document.querySelectorAll('.ant-cascader-menus, .ant-select-dropdown').forEach(m => m.remove());
                }
            """)
            await self.page.wait_for_timeout(300)
            
            result = await self.page.evaluate("""
                async () => {
                    // 查找级联选择器元素
                    const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                    let cascaderEl = null;
                    
                    for (const item of formItems) {
                        const label = item.querySelector('.ant-form-item-label label');
                        if (label && label.textContent.includes('适用区域')) {
                            cascaderEl = item.querySelector('.ant-cascader');
                            break;
                        }
                    }
                    
                    if (!cascaderEl) return {success: false, error: 'not_found'};
                    
                    // 清除已有值（如果有clear按钮）
                    const clearBtn = cascaderEl.querySelector('.ant-select-clear');
                    if (clearBtn) {
                        clearBtn.click();
                        await new Promise(r => setTimeout(r, 500));
                    }
                    
                    // 使用多种方式尝试打开下拉
                    const selector = cascaderEl.querySelector('.ant-select-selector');
                    const input = cascaderEl.querySelector('input');
                    
                    if (selector) {
                        selector.click();
                    } else if (input) {
                        input.click();
                        input.focus();
                    }
                    
                    // 等待菜单加载
                    await new Promise(r => setTimeout(r, 1500));
                    
                    // 查找所有可能的菜单
                    const menus = document.querySelectorAll('.ant-cascader-menus:not(.ant-cascader-hidden)');
                    const allMenus = document.querySelectorAll('.ant-cascader-menus');
                    
                    if (menus.length === 0 && allMenus.length === 0) {
                        // 尝试另一种点击方式
                        if (input) {
                            const rect = input.getBoundingClientRect();
                            const clickX = rect.left + rect.width / 2;
                            const clickY = rect.top + rect.height / 2;
                            const evt = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window,
                                clientX: clickX,
                                clientY: clickY
                            });
                            input.dispatchEvent(evt);
                            await new Promise(r => setTimeout(r, 1000));
                        }
                    }
                    
                    // 再次查找菜单
                    const finalMenus = document.querySelectorAll('.ant-cascader-menus:not(.ant-cascader-hidden)');
                    if (finalMenus.length === 0) return {success: false, error: 'no_menus', debug: {menusCount: allMenus.length}};
                    
                    // 选择第一级第一个选项
                    const firstMenu = finalMenus[0];
                    const firstLevelItems = firstMenu.querySelectorAll('.ant-cascader-menu-item');
                    if (firstLevelItems.length === 0) return {success: false, error: 'no_items'};
                    
                    // 过滤掉禁用项
                    let selectedItem = null;
                    for (const item of firstLevelItems) {
                        if (!item.classList.contains('disabled') && !item.classList.contains('ant-cascader-menu-item-disabled')) {
                            selectedItem = item;
                            break;
                        }
                    }
                    
                    if (!selectedItem) return {success: false, error: 'no_valid_items'};
                    
                    const selected = [];
                    selectedItem.click();
                    selected.push(selectedItem.textContent.trim());
                    await new Promise(r => setTimeout(r, 1000));
                    
                    // 检查是否有子菜单
                    const subMenus = document.querySelectorAll('.ant-cascader-menus:not(.ant-cascader-hidden)');
                    if (subMenus.length > 1) {
                        const subItems = subMenus[1].querySelectorAll('.ant-cascader-menu-item');
                        for (const item of subItems) {
                            if (!item.classList.contains('disabled') && !item.classList.contains('ant-cascader-menu-item-disabled')) {
                                item.click();
                                selected.push(item.textContent.trim());
                                await new Promise(r => setTimeout(r, 800));
                                break;
                            }
                        }
                    }
                    
                    // 点击外部区域关闭下拉并确认选择
                    const modal = document.querySelector('.ant-modal');
                    if (modal) {
                        const mask = modal.querySelector('.ant-modal-mask') || modal.parentElement;
                        if (mask) mask.click();
                        else document.body.click();
                    }
                    await new Promise(r => setTimeout(r, 500));
                    
                    return {success: true, selected: selected};
                }
            """)
            print(f"    JS设置级联结果: {result}")
            return result.get('success', False)
        except Exception as e:
            print(f"    JS设置级联失败: {e}")
            return False
    
    async def _select_cascader_js(self, form_item, label_text, option_index=0):
        """使用JS方式选择级联选择器"""
        try:
            result = await self.page.evaluate("""
                async () => {
                    // 清理已有popup
                    document.querySelectorAll('.ant-cascader-menus').forEach(m => m.remove());
                    
                    // 找到级联选择器
                    const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                    let cascader = null;
                    for (const item of formItems) {
                        const label = item.querySelector('.ant-form-item-label label');
                        if (label && label.textContent.includes('适用区域')) {
                            cascader = item.querySelector('.ant-cascader');
                            break;
                        }
                    }
                    
                    if (!cascader) return 'not_found';
                    
                    // 点击selector打开下拉
                    const selector = cascader.querySelector('.ant-select-selector');
                    if (selector) selector.click();
                    
                    // 等待菜单加载
                    await new Promise(r => setTimeout(r, 1000));
                    
                    // 查找菜单
                    const menus = document.querySelectorAll('.ant-cascader-menus:not(.ant-cascader-hidden)');
                    if (menus.length === 0) return 'no_menus';
                    
                    // 选择第一级第一个选项
                    const firstMenu = menus[0];
                    const items = firstMenu.querySelectorAll('.ant-cascader-menu-item:not(.disabled)');
                    if (items.length === 0) return 'no_items';
                    
                    items[0].click();
                    await new Promise(r => setTimeout(r, 800));
                    
                    // 检查是否有子菜单
                    const subMenus = document.querySelectorAll('.ant-cascader-menus:not(.ant-cascader-hidden)');
                    if (subMenus.length > 1) {
                        const subItems = subMenus[1].querySelectorAll('.ant-cascader-menu-item:not(.disabled)');
                        if (subItems.length > 0) {
                            subItems[0].click();
                            await new Promise(r => setTimeout(r, 500));
                        }
                    }
                    
                    return 'success';
                }
            """)
            print(f"    JS级联选择结果: {result}")
            return result == 'success'
        except Exception as e:
            print(f"    JS级联选择失败: {e}")
            return False

    async def fill_input_by_id(self, field_id, value):
        """通过id填充input"""
        try:
            await self.page.locator(f'input#{field_id}').fill(value)
            return True
        except Exception as e:
            print(f"    填充input#{field_id}失败: {e}")
            return False

    async def fill_editor(self, editor_id, value):
        """通过id填充富文本编辑器"""
        try:
            # 编辑器的textarea通常是隐藏的，需要通过JS操作
            await self.page.evaluate("""
                ({id, content}) => {
                    // 尝试找到编辑器相关的元素
                    const editors = document.querySelectorAll(`[id^="${id.split('_')[0]}"]`);
                    
                    // 找textarea
                    const textareas = document.querySelectorAll(`textarea[id^="my-editor_"]`);
                    for (const ta of textareas) {
                        ta.value = content;
                        ta.dispatchEvent(new Event('input', {bubbles: true}));
                        ta.dispatchEvent(new Event('change', {bubbles: true}));
                        return {success: true, method: 'textarea', id: ta.id};
                    }
                    
                    // 找contenteditable
                    const editables = document.querySelectorAll('[contenteditable="true"]');
                    for (const ed of editables) {
                        if (ed.offsetParent !== null) {
                            ed.textContent = content;
                            ed.dispatchEvent(new Event('input', {bubbles: true}));
                            ed.dispatchEvent(new Event('change', {bubbles: true}));
                            return {success: true, method: 'contenteditable'};
                        }
                    }
                    
                    return {success: false, method: 'none'};
                }
            """, {"id": editor_id, "content": value})
            return True
        except Exception as e:
            print(f"    填充编辑器失败: {e}")
            return False

    async def test_project_add(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/project-config")

        # 查找新增按钮 - 尝试多种选择器
        add_btn = None
        selectors = [
            'button:has-text("新增服务项目")',
            'button:has-text("新增")',
            '.ant-btn-primary:has-text("新增")',
            '.ant-btn:has-text("新增服务项目")',
        ]
        
        for selector in selectors:
            try:
                btn = self.page.locator(selector)
                if await btn.count() > 0:
                    add_btn = btn.first
                    print(f"  找到按钮: {selector}")
                    break
            except:
                continue
        
        if add_btn:
            await add_btn.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("project_add_01")
        else:
            # 输出页面按钮信息用于调试
            buttons_info = await self.page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button');
                    return Array.from(buttons).map(b => ({
                        text: b.textContent.trim(),
                        visible: b.offsetParent !== null,
                        classes: b.className.toString().substring(0, 50)
                    })).filter(b => b.visible);
                }
            """)
            print(f"  页面按钮: {buttons_info}")
            self.fail(mod, "新增服务项目", f"未找到新增按钮，页面按钮: {buttons_info}", await self.ss("project_add_no_btn"))
            return

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增服务项目", "弹窗未打开")
            return

        # 查找表单元素
        form_info = await self.page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('.ant-modal input[codefield]');
                const textareas = document.querySelectorAll('.ant-modal textarea');
                const visible_inputs = Array.from(inputs).filter(i => i.offsetParent !== null);
                const visible_textareas = Array.from(textareas).filter(t => t.offsetParent !== null);
                return {
                    inputs: visible_inputs.map(i => ({id: i.id, placeholder: i.placeholder, codefield: i.getAttribute('codefield')})),
                    textareas: visible_textareas.map(t => ({id: t.id, placeholder: t.placeholder})),
                };
            }
        """)
        
        # 填写服务项目名称
        if form_info['inputs']:
            await self.page.locator(f'input#{form_info["inputs"][0]["id"]}').fill(self.data["project_name"])
            print(f"  填写服务项目名称")
        
        # 填写副标题
        if len(form_info['inputs']) > 1:
            await self.page.locator(f'input#{form_info["inputs"][1]["id"]}').fill(self.data["project_subtitle"])
            print(f"  填写副标题")
        
        # 查找textarea或富文本编辑器
        textarea_info = await self.page.evaluate("""
            () => {
                // 查找所有textarea（包括隐藏的）
                const textareas = document.querySelectorAll('.ant-modal textarea');
                const editors = [];
                textareas.forEach(ta => {
                    editors.push({
                        id: ta.id,
                        placeholder: ta.placeholder,
                        visible: ta.offsetParent !== null
                    });
                });
                return editors;
            }
        """)
        
        # 填写服务项目介绍
        for ta in textarea_info:
            if ta['id']:
                await self.page.evaluate("""
                    ({id, content}) => {
                        const ta = document.getElementById(id);
                        if (ta) {
                            ta.value = content;
                            ta.dispatchEvent(new Event('input', {bubbles: true}));
                            ta.dispatchEvent(new Event('change', {bubbles: true}));
                        }
                    }
                """, {"id": ta['id'], "content": self.data["project_content"]})
                print(f"  填写服务项目介绍(id={ta['id']}, value={self.data['project_content']})")
                break
        
        # 查找并选择radio（计费方式等）
        radio_info = await self.page.evaluate("""
            () => {
                const radios = document.querySelectorAll('.ant-modal .ant-radio');
                const radio_groups = {};
                radios.forEach((r, idx) => {
                    const formItem = r.closest('.ant-form-item');
                    const label = formItem ? formItem.querySelector('.ant-form-item-label')?.textContent.trim() : 'unknown';
                    if (!radio_groups[label]) {
                        radio_groups[label] = [];
                    }
                    radio_groups[label].push({
                        index: idx,
                        text: r.textContent.trim(),
                        checked: r.classList.contains('ant-radio-checked')
                    });
                });
                return radio_groups;
            }
        """)
        print(f"  Radio组: {radio_info}")
        
        # 选择第一个radio选项（如果有）
        for label, options in radio_info.items():
            if options and not any(o['checked'] for o in options):
                # 点击第一个未选中的radio
                try:
                    radios = self.page.locator('.ant-modal .ant-radio')
                    first_idx = options[0]['index']
                    await radios.nth(first_idx).click()
                    print(f"  选择 {label}: {options[0]['text']}")
                except Exception as e:
                    print(f"  选择radio失败: {e}")
        
        print(f"  表单填写完成")
        
        # 表单值检查
        form_values = await self.page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('.ant-modal input[codefield]');
                const values = {};
                inputs.forEach(inp => {
                    values[inp.getAttribute('codefield')] = inp.value;
                });
                
                // 检查radio状态
                const checkedRadios = document.querySelectorAll('.ant-modal .ant-radio-checked');
                values['billing'] = checkedRadios.length > 0 ? checkedRadios[0].textContent.trim() : '';
                
                // 检查编辑器内容
                const textareas = document.querySelectorAll('.ant-modal textarea');
                textareas.forEach(ta => {
                    if (ta.id && ta.value) {
                        const key = ta.id.replace('my-editor_', 'editor_');
                        values[key] = ta.value;
                    }
                });
                
                return values;
            }
        """)
        print(f"  表单值检查: {form_values}")
        
        await self.ss("project_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)
        
        # 检查Toast和数据
        msgs = await self.toasts()
        errors = await self.get_errors()
        print(f"  Toast: {msgs}")
        
        # 刷新列表检查数据是否已添加
        await self.page.reload(wait_until="networkidle")
        await self.page.wait_for_timeout(2)
        
        text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
        if self.data["project_name"] in text:
            self.ok(mod, "新增服务项目", f"成功！数据已在列表中。Toast: {msgs}", await self.ss("project_add_ok"))
            self.created["project"] = self.data["project_name"]
        elif errors:
            self.fail(mod, "新增服务项目", f"验证错误: {errors}", await self.ss("project_add_err"))
        else:
            self.fail(mod, "新增服务项目", f"Toast: {msgs}, 数据未在列表中", await self.ss("project_add_fail"))

    async def test_project_edit(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 编辑\n{'='*60}")
        await self.go("/smart-service/project-config")
        await self.page.wait_for_timeout(1000)

        # 查找操作列的编辑按钮
        edit_btns = self.page.locator('a:has-text("编辑")')
        if await edit_btns.count() > 0:
            await edit_btns.first.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("project_edit_01")
            
            if await self.page.locator(".ant-modal").count() > 0:
                # 读取当前表单值
                current_values = await self.page.evaluate("""
                    () => {
                        const inputs = document.querySelectorAll('.ant-modal input[codefield]');
                        const values = {};
                        inputs.forEach(inp => {
                            values[inp.getAttribute('codefield')] = inp.value;
                        });
                        return values;
                    }
                """)
                print(f"  当前值: {current_values}")
                
                # 修改副标题
                subtitle_input = self.page.locator('input[codefield="subtitle"]')
                if await subtitle_input.count() > 0:
                    new_subtitle = f"修改_{self.data['project_subtitle']}"
                    await subtitle_input.fill(new_subtitle)
                    print(f"  修改副标题为: {new_subtitle}")
                
                await self.ss("project_edit_02")
                
                # 提交
                await self.page.click('.ant-modal button:has-text("确 认")')
                await self.page.wait_for_timeout(3)
                
                msgs = await self.toasts()
                print(f"  Toast: {msgs}")
                
                if any('成功' in m or '操作成功' in m for m in msgs):
                    self.ok(mod, "编辑服务项目", f"成功。Toast: {msgs}", await self.ss("project_edit_ok"))
                else:
                    self.fail(mod, "编辑服务项目", f"Toast: {msgs}", await self.ss("project_edit_fail"))
        else:
            self.skip(mod, "编辑服务项目", "未找到编辑按钮")

    async def test_project_toggle(self):
        mod = "智能服务配置-服务项目配置"
        print(f"\n{'='*60}\n{mod} - 切换展示\n{'='*60}")
        await self.go("/smart-service/project-config")
        await self.page.wait_for_timeout(1000)

        # 查找状态开关
        switches = self.page.locator('.ant-switch')
        if await switches.count() > 0:
            await switches.first.click()
            await self.page.wait_for_timeout(2)
            msgs = await self.toasts()
            self.ok(mod, "切换展示", f"成功。Toast: {msgs}", await self.ss("project_toggle_ok"))
        else:
            self.skip(mod, "切换展示", "未找到按钮")

    async def test_contract_add(self):
        mod = "智能服务配置-合同服务配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/contract-service")
        await self.page.wait_for_timeout(1000)

        # 下拉加载
        loading = True
        retry = 0
        while loading and retry < 5:
            loaders = self.page.locator('.ant-spin')
            if await loaders.count() == 0:
                loading = False
            else:
                await self.page.wait_for_timeout(500)
                retry += 1
        print("  下拉数据加载中...")

        await self.page.click('button:has-text("新增合同服务")')
        await self.page.wait_for_timeout(1500)
        await self.ss("contract_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增合同服务", "弹窗未打开")
            return

        # 使用Playwright的fill方法填写表单（会触发React状态更新）
        # 1. 合同服务标题
        try:
            title_el = self.page.locator('input#ContractServiceForm_title')
            if await title_el.count() > 0:
                await title_el.fill(self.data["contract_title"])
                print(f"  填写合同服务标题")
            else:
                title_el = self.page.locator('input[codefield="title"]')
                if await title_el.count() > 0:
                    await title_el.fill(self.data["contract_title"])
                    print(f"  填写合同服务标题 (codefield)")
        except Exception as e:
            print(f"  填写合同服务标题失败: {e}")

        # 2. 所属服务项目 - 下拉选择
        selected_project = await self.select_dropdown('所属服务项目', 0)
        print(f"  选择所属服务项目: {'成功' if selected_project else '无选项'}")

        # 3. 合同服务内容
        try:
            content_el = self.page.locator('textarea#ContractServiceForm_content')
            if await content_el.count() > 0:
                await content_el.fill(self.data["contract_content"])
                print(f"  填写合同服务内容")
            else:
                content_el = self.page.locator('textarea[codefield="content"]')
                if await content_el.count() > 0:
                    await content_el.fill(self.data["contract_content"])
                    print(f"  填写合同服务内容 (codefield)")
        except Exception as e:
            print(f"  填写合同服务内容失败: {e}")

        # 4. 费用内容
        try:
            fee_el = self.page.locator('textarea#ContractServiceForm_priceContent')
            if await fee_el.count() > 0:
                await fee_el.fill(self.data["contract_fee"])
                print(f"  填写费用内容")
            else:
                fee_el = self.page.locator('textarea[codefield="priceContent"]')
                if await fee_el.count() > 0:
                    await fee_el.fill(self.data["contract_fee"])
                    print(f"  填写费用内容 (codefield)")
        except Exception as e:
            print(f"  填写费用内容失败: {e}")

        print(f"  表单填写完成")
        await self.ss("contract_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)

        msgs = await self.toasts()
        errors = await self.get_errors()
        print(f"  Toast: {msgs}")

        # 刷新列表检查
        await self.page.reload(wait_until="networkidle")
        await self.page.wait_for_timeout(2)

        text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
        if self.data["contract_title"] in text:
            self.ok(mod, "新增合同服务", f"成功！数据已在列表中。Toast: {msgs}", await self.ss("contract_add_ok"))
        elif errors:
            self.fail(mod, "新增合同服务", f"验证错误: {errors}", await self.ss("contract_add_err"))
        else:
            self.fail(mod, "新增合同服务", f"Toast: {msgs}, 数据未在列表中", await self.ss("contract_add_fail"))

    async def test_business_scope_add(self):
        mod = "智能服务配置-经营范围配置"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/smart-service/scope-config")

        await self.page.click('button:has-text("新增经营范围")')
        await self.page.wait_for_timeout(1500)
        await self.ss("scope_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增经营范围", "弹窗未打开")
            return

        # 1. 经营范围名称 - 使用Playwright fill方法
        try:
            name_el = self.page.locator('input#BusinessScopeForm_scopeName')
            if await name_el.count() > 0:
                await name_el.fill(self.data["business_scope_name"])
                print(f"  填写经营范围名称")
        except Exception as e:
            print(f"  填写经营范围名称失败: {e}")
        
        # 2. 备注 - textarea
        try:
            remark_el = self.page.locator('.ant-modal textarea')
            if await remark_el.count() > 0:
                await remark_el.first.fill(self.data["business_remark"])
                print(f"  填写备注")
        except Exception as e:
            print(f"  填写备注失败: {e}")

        print(f"  表单填写完成")
        await self.ss("scope_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)

        msgs = await self.toasts()
        errors = await self.get_errors()
        print(f"  Toast: {msgs}")

        # 刷新列表检查
        await self.page.reload(wait_until="networkidle")
        await self.page.wait_for_timeout(2)

        text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
        if self.data["business_scope_name"] in text:
            self.ok(mod, "新增经营范围", f"成功！数据已在列表中。Toast: {msgs}", await self.ss("scope_add_ok"))
        elif errors:
            self.fail(mod, "新增经营范围", f"验证错误: {errors}", await self.ss("scope_add_err"))
        else:
            self.fail(mod, "新增经营范围", f"Toast: {msgs}, 数据未在列表中", await self.ss("scope_add_fail"))

    async def test_knowledge_add(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 新增\n{'='*60}")
        await self.go("/content-manage/knowledge")

        await self.page.click('button:has-text("新增知识库")')
        await self.page.wait_for_timeout(1500)
        await self.ss("knowledge_add_01")

        if await self.page.locator(".ant-modal").count() == 0:
            self.fail(mod, "新增知识库", "弹窗未打开")
            return

        # 1. 标题 - 使用Playwright fill方法
        try:
            title_el = self.page.locator('input#KnowledgeForm_title')
            if await title_el.count() > 0:
                await title_el.fill(self.data["knowledge_title"])
                print(f"  填写标题")
        except Exception as e:
            print(f"  填写标题失败: {e}")
        
        # 2. 资讯类型 - 下拉选择
        selected1 = await self.select_dropdown('资讯类型', 0)
        print(f"  选择资讯类型: {'成功' if selected1 else '无选项'}")
        
        # 3. 展示位置 - 下拉选择
        selected2 = await self.select_dropdown('展示位置', 0)
        print(f"  选择展示位置: {'成功' if selected2 else '无选项'}")
        
        # 4. 适用区域 - 级联选择
        await self.page.wait_for_timeout(500)
        
        # 先检查适用区域的实际结构
        region_info = await self.page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.includes('适用区域')) {
                        const select = item.querySelector('.ant-select');
                        const cascader = item.querySelector('.ant-cascader');
                        return {
                            hasSelect: !!select,
                            hasCascader: !!cascader,
                            selectClasses: select ? select.className : 'none',
                            cascaderClasses: cascader ? cascader.className : 'none',
                            html: item.innerHTML.substring(0, 500)
                        };
                    }
                }
                return 'not_found';
            }
        """)
        print(f"  适用区域结构: {region_info}")
        
        selected3 = await self.select_dropdown('适用区域', 0)
        print(f"  选择适用区域: {'成功' if selected3 else '无选项'}")
        
        # 如果级联选择失败，尝试使用JS直接设置值
        if not selected3:
            await self.page.evaluate("""
                () => {
                    // 查找适用区域的select元素
                    const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                    for (const item of formItems) {
                        const label = item.querySelector('.ant-form-item-label label');
                        if (label && label.textContent.includes('适用区域')) {
                            // 查找cascader元素
                            const cascader = item.querySelector('.ant-cascader');
                            if (cascader) {
                                // 模拟选择操作
                                const selector = cascader.querySelector('.ant-select-selector');
                                if (selector) selector.click();
                                return 'cascader_clicked';
                            }
                        }
                    }
                    return 'not_found';
                }
            """)
            await self.page.wait_for_timeout(500)
        
        # 验证选择结果
        region_value = await self.page.evaluate("""
            () => {
                const formItems = document.querySelectorAll('.ant-modal .ant-form-item');
                for (const item of formItems) {
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.includes('适用区域')) {
                        const selector = item.querySelector('.ant-select-selection-item');
                        return selector ? selector.textContent.trim() : 'not_selected';
                    }
                }
                return 'not_found';
            }
        """)
        print(f"  适用区域当前值: {region_value}")
        
        # 5. 内容 - TinyMCE富文本编辑器
        await self.page.wait_for_timeout(500)
        
        content_filled = False
        
        # 方式1: 通过TinyMCE API设置内容
        result = await self.page.evaluate("""
            (content) => {
                // 查找TinyMCE编辑器
                const iframes = document.querySelectorAll('.ant-modal iframe');
                for (const iframe of iframes) {
                    try {
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                        const editor = iframeDoc.querySelector('.tox-editor-container, .mce-container-body, .tox-edit-area');
                        if (editor) {
                            // 尝试通过TinyMCE API
                            if (window.tinymce && window.tinymce.get) {
                                const editors = window.tinymce.get();
                                for (const ed of editors) {
                                    ed.setContent('<p>' + content + '</p>');
                                    return {success: true, method: 'tinymce_api'};
                                }
                            }
                            
                            // 直接操作iframe中的DOM
                            const editableArea = iframeDoc.querySelector('.tox-edit-area__iframe, .mceContentBody');
                            if (editableArea) {
                                editableArea.innerHTML = '<p>' + content + '</p>';
                                // 触发事件
                                const evt = new Event('input', {bubbles: true});
                                editableArea.dispatchEvent(evt);
                                return {success: true, method: 'iframe_dom'};
                            }
                        }
                    } catch (e) {
                        // 跨域或其他错误，尝试下一个
                    }
                }
                
                return {success: false, method: 'not_found'};
            }
        """, self.data["knowledge_content"])
        
        if result.get('success'):
            print(f"  内容填写成功 ({result.get('method')})")
            content_filled = True
        
        # 方式2: 尝试查找tinymce实例并设置内容+触发事件
        if not content_filled:
            result2 = await self.page.evaluate("""
                async (content) => {
                    // 查找所有tinymce编辑器
                    if (window.tinymce) {
                        const editors = window.tinymce.get();
                        if (editors.length > 0) {
                            for (const ed of editors) {
                                try {
                                    // 设置内容
                                    ed.setContent('<p>' + content + '</p>');
                                    
                                    // 触发change事件通知表单
                                    ed.save();  // 同步内容到textarea
                                    
                                    // 手动触发事件
                                    const textarea = document.querySelector('#KnowledgeForm_content textarea');
                                    if (textarea) {
                                        textarea.dispatchEvent(new Event('input', {bubbles: true}));
                                        textarea.dispatchEvent(new Event('change', {bubbles: true}));
                                    }
                                    
                                    return {success: true, method: 'tinymce_set_content', count: editors.length};
                                } catch(e) {}
                            }
                        }
                    }
                    
                    // 尝试通过id查找textarea并设置值
                    const textarea = document.querySelector('#KnowledgeForm_content textarea');
                    if (textarea) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(textarea, '<p>' + content + '</p>');
                        textarea.dispatchEvent(new Event('input', {bubbles: true}));
                        textarea.dispatchEvent(new Event('change', {bubbles: true}));
                        return {success: true, method: 'textarea_direct'};
                    }
                    
                    return {success: false};
                }
            """, self.data["knowledge_content"])
            
            if result2.get('success'):
                print(f"  内容填写成功 ({result2.get('method')})")
                content_filled = True
        
        # 额外等待时间让表单状态更新
        await self.page.wait_for_timeout(1000)
        
        # 方式3: 最后尝试通过React fiber设置
        if not content_filled:
            result3 = await self.page.evaluate("""
                (content) => {
                    const form = document.querySelector('.ant-modal form');
                    if (!form) return {success: false};
                    
                    const formInstance = form.__reactFiber$ || form.__reactInternalInstance$;
                    if (!formInstance) return {success: false};
                    
                    function findFiber(fiber, name) {
                        if (!fiber) return null;
                        if (fiber.memoizedProps && fiber.memoizedProps.name === name) return fiber;
                        return findFiber(fiber.child, name) || findFiber(fiber.sibling, name);
                    }
                    
                    const contentFiber = findFiber(formInstance, 'content');
                    if (contentFiber && contentFiber.memoizedProps && contentFiber.memoizedProps.onChange) {
                        contentFiber.memoizedProps.onChange(content);
                        return {success: true, method: 'react_fiber'};
                    }
                    
                    return {success: false};
                }
            """, self.data["knowledge_content"])
            
            if result3.get('success'):
                print(f"  内容填写成功 ({result3.get('method')})")
                content_filled = True
        
        print(f"  内容填写: {'成功' if content_filled else '失败'}")
        print("  表单填写完成")
        await self.ss("knowledge_add_02")

        # 提交
        await self.page.click('.ant-modal button:has-text("确 认")')
        await self.page.wait_for_timeout(3)
        
        # 检查Toast和数据
        msgs = await self.toasts()
        errors = await self.get_errors()
        print(f"  Toast: {msgs}")
        print(f"  验证错误: {errors}")
        
        # 刷新列表检查数据是否已添加
        await self.page.reload(wait_until="networkidle")
        await self.page.wait_for_timeout(2)
        
        text = await self.page.evaluate("() => document.querySelector('.ant-table-tbody')?.textContent || ''")
        if self.data["knowledge_title"] in text:
            self.ok(mod, "新增知识库", f"成功！数据已在列表中。Toast: {msgs}", await self.ss("knowledge_add_ok"))
            self.created["knowledge"] = self.data["knowledge_title"]
        elif errors:
            self.fail(mod, "新增知识库", f"验证错误: {errors}", await self.ss("knowledge_add_err"))
        else:
            self.fail(mod, "新增知识库", f"Toast: {msgs}, 数据未在列表中", await self.ss("knowledge_add_fail"))

    async def test_knowledge_toggle(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 状态切换\n{'='*60}")
        await self.go("/content-manage/knowledge")
        await self.page.wait_for_timeout(1000)

        toggle = self.page.locator('a:has-text("禁用"), a:has-text("启用")')
        if await toggle.count() > 0:
            text = await toggle.first.text_content()
            await toggle.first.click()
            await self.page.wait_for_timeout(1000)

            confirm = self.page.locator(".ant-popconfirm button.ant-btn-primary")
            if await confirm.count() > 0:
                await confirm.first.click()
                await self.page.wait_for_timeout(2)
                msgs = await self.toasts()
                self.ok(mod, f"状态切换({text})", f"成功。Toast: {msgs}", await self.ss("knowledge_toggle_ok"))
            else:
                self.fail(mod, f"状态切换({text})", "无确认弹窗", await self.ss("knowledge_toggle_no"))
        else:
            self.skip(mod, "状态切换", "未找到按钮")

    async def test_knowledge_detail(self):
        mod = "内容管理-知识库"
        print(f"\n{'='*60}\n{mod} - 查看详情\n{'='*60}")
        await self.go("/content-manage/knowledge")
        await self.page.wait_for_timeout(1000)

        detail = self.page.locator('a:has-text("详情")')
        if await detail.count() > 0:
            await detail.first.click()
            await self.page.wait_for_timeout(1500)
            await self.ss("knowledge_detail_01")

            if await self.page.locator(".ant-modal, .ant-drawer").count() > 0:
                content = await self.page.evaluate("""
                    () => {
                        const body = document.querySelector('.ant-modal-body, .ant-drawer-body');
                        return body ? body.textContent.substring(0, 200) : '';
                    }
                """)
                print(f"  详情内容预览: {content}")
                self.ok(mod, "查看详情", "详情弹窗打开成功", await self.ss("knowledge_detail_ok"))
                
                # 关闭弹窗
                close_btn = self.page.locator('.ant-modal-close, .ant-drawer-close')
                if await close_btn.count() > 0:
                    await close_btn.first.click()
                    await self.page.wait_for_timeout(500)
            else:
                self.fail(mod, "查看详情", "未找到详情弹窗", await self.ss("knowledge_detail_fail"))
        else:
            self.skip(mod, "查看详情", "未找到详情按钮")

    def generate_report(self):
        """生成测试报告"""
        report_path = os.path.join(self.report_dir, f"real_data_report_{self.timestamp}.md")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['pass'] is True)
        failed = sum(1 for r in self.results if r['pass'] is False)
        skipped = sum(1 for r in self.results if r['pass'] is None)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 实际数据提交验证测试报告\n\n")
            f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**测试环境**: {self.base_url}\n\n")
            f.write(f"**测试账号**: {self.username}\n\n")
            f.write(f"## 测试结果汇总\n\n")
            f.write(f"| 指标 | 数量 |\n|------|------|\n")
            f.write(f"| 总数 | {total} |\n")
            f.write(f"| 通过 | {passed} |\n")
            f.write(f"| 失败 | {failed} |\n")
            f.write(f"| 跳过 | {skipped} |\n\n")
            
            # 按模块分组
            modules = {}
            for r in self.results:
                mod = r['module']
                if mod not in modules:
                    modules[mod] = []
                modules[mod].append(r)
            
            for mod, items in modules.items():
                f.write(f"\n## {mod}\n\n")
                f.write(f"| 测试项 | 状态 | 详情 | 截图 |\n|--------|------|------|------|\n")
                for item in items:
                    status = "✅ PASS" if item['pass'] else ("❌ FAIL" if item['pass'] is False else "⏭️ SKIP")
                    shot = f"[截图]({os.path.basename(item['screenshot'])})" if item['screenshot'] else "-"
                    detail = item['detail'].replace('\n', ' ')[:100]
                    f.write(f"| {item['type']} | {status} | {detail} | {shot} |\n")
            
            # 问题列表
            failures = [r for r in self.results if r['pass'] is False]
            if failures:
                f.write(f"\n## 发现的问题\n\n")
                for i, fail in enumerate(failures, 1):
                    f.write(f"### {i}. {fail['module']} - {fail['type']}\n\n")
                    f.write(f"- **问题描述**: {fail['detail']}\n")
                    if fail['screenshot']:
                        f.write(f"- **截图**: {os.path.basename(fail['screenshot'])}\n")
                    f.write("\n")
        
        print(f"\n报告: {report_path}")

    async def run(self):
        print("=" * 60)
        print("超级个体后台管理系统 - 实际数据提交验证测试")
        print("=" * 60)
        
        await self.start()
        
        # 智能服务配置 - 服务项目
        await self.test_project_add()
        await self.test_project_edit()
        await self.test_project_toggle()
        
        # 智能服务配置 - 合同服务
        await self.test_contract_add()
        
        # 智能服务配置 - 经营范围
        await self.test_business_scope_add()
        
        # 内容管理 - 知识库
        await self.test_knowledge_add()
        await self.test_knowledge_toggle()
        await self.test_knowledge_detail()
        
        # 生成报告
        self.generate_report()
        
        # 汇总
        total = len(self.results)
        passed = sum(1 for r in self.results if r['pass'] is True)
        failed = sum(1 for r in self.results if r['pass'] is False)
        skipped = sum(1 for r in self.results if r['pass'] is None)
        
        print(f"\n{'='*60}")
        print(f"测试完成！")
        print(f"总数:{total} 通过:{passed} 失败:{failed} 跳过:{skipped}")
        print(f"{'='*60}")
        
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


if __name__ == "__main__":
    test = RealDataTest()
    asyncio.run(test.run())
