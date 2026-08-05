# -*- coding: utf-8 -*-
"""
页面基类 —— 通用点击、输入、弹窗、等待、下拉、级联、富文本等封装
所有 Page 对象继承此类
"""
import os
from typing import Optional

from playwright.sync_api import Page, Locator, expect

from utils.logger import logger
from utils.file_helper import screenshot_path


class BasePage:
    """所有页面对象的基类"""

    def __init__(self, page: Page):
        self.page: Page = page

    # ──────────── 导航 ────────────

    def navigate(self, path: str) -> None:
        """导航到指定路径（相对路径）"""
        from config.env_config import BASE_URL
        full_url = f"{BASE_URL}{path}"
        self.page.goto(full_url, wait_until="networkidle")
        self.page.wait_for_timeout(2000)
        logger.info(f"导航到: {path} -> {self.page.url}")
        try:
            self.page.wait_for_selector(".ant-layout-content, .ant-layout", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

    # ──────────── 等待 ────────────

    def wait_modal(self, timeout: int = 5000) -> bool:
        """等待弹窗出现"""
        try:
            self.page.wait_for_selector(".ant-modal", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_loading(self, timeout: int = 10000) -> None:
        """等待 loading 消失"""
        try:
            self.page.wait_for_selector(".ant-spin", state="detached", timeout=timeout)
        except Exception:
            pass

    # ──────────── 点击 / 输入 ────────────

    def click_button(self, text: str, force: bool = True) -> None:
        """点击包含指定文本的按钮"""
        btn = self.page.locator(f'button:has-text("{text}")')
        btn.first.click(force=force)
        logger.info(f"点击按钮: {text}")

    def fill_input(self, selector: str, value: str) -> None:
        """填充 input"""
        el = self.page.locator(selector)
        el.fill(value)
        logger.info(f"填充 {selector}: {value}")

    def fill_input_by_id(self, field_id: str, value: str) -> bool:
        """通过 input id 填充"""
        try:
            self.page.locator(f"input#{field_id}").fill(value)
            return True
        except Exception as e:
            logger.warning(f"填充 input#{field_id} 失败: {e}")
            return False

    def fill_textarea_by_id(self, field_id: str, value: str) -> bool:
        """通过 textarea id 填充"""
        try:
            self.page.locator(f"textarea#{field_id}").fill(value)
            return True
        except Exception as e:
            logger.warning(f"填充 textarea#{field_id} 失败: {e}")
            return False

    # ──────────── 弹窗操作 ────────────

    def submit_modal(self) -> None:
        """点击弹窗内的确认按钮"""
        self.page.click('.ant-modal button:has-text("确 认")')
        self.page.wait_for_timeout(3000)

    def close_modal_safe(self) -> None:
        """安全关闭弹窗"""
        try:
            close_btn = self.page.locator(".ant-modal-close")
            if close_btn.count() > 0:
                close_btn.first.click()
                self.page.wait_for_timeout(500)
            else:
                self.page.keyboard.press("Escape")
        except Exception:
            self.page.keyboard.press("Escape")

    # ──────────── Toast / 错误 ────────────

    def get_toasts(self) -> list:
        """获取 Toast 消息列表"""
        return self.page.evaluate("""
            () => {
                const toasts = document.querySelectorAll('.ant-message-notice-content');
                return Array.from(toasts).map(t => t.textContent.trim());
            }
        """)

    def get_form_errors(self) -> list:
        """获取表单验证错误"""
        return self.page.evaluate("""
            () => {
                const errors = document.querySelectorAll(
                    '.ant-form-item-explain-error'
                );
                return Array.from(errors)
                    .filter(e => e.offsetParent !== null)
                    .map(e => e.textContent.trim());
            }
        """)

    # ──────────── 列表验证 ────────────

    def is_data_in_table(self, keyword: str) -> bool:
        """刷新列表后检查数据是否在表格中"""
        self.page.reload(wait_until="networkidle")
        self.page.wait_for_timeout(2000)
        text = self.page.evaluate(
            "() => document.querySelector('.ant-table-tbody')?.textContent || ''"
        )
        return keyword in text

    # ──────────── 截图 ────────────

    def screenshot(self, name: str) -> str:
        """截图并返回路径"""
        path = screenshot_path(name)
        self.page.screenshot(path=path)
        logger.info(f"截图: {name} -> {path}")
        return path

    # ──────────── 下拉选择 ────────────

    def select_dropdown(self, label_text: str, option_index: int = 0) -> bool:
        """
        选择下拉框选项 —— 自动判断普通 Select / 级联 Cascader

        Args:
            label_text: 表单项标签文本（如"资讯类型"、"适用区域"）
            option_index: 选项索引
        Returns:
            是否选择成功
        """
        try:
            # 清理已存在的 popup
            self.page.evaluate("""
                () => {
                    document.querySelectorAll(
                        '.ant-select-dropdown, .ant-cascader-menus'
                    ).forEach(p => p.remove());
                }
            """)
            self.page.wait_for_timeout(200)

            form_item = self.page.locator(
                ".ant-modal .ant-form-item"
            ).filter(has_text=label_text)
            if form_item.count() == 0:
                logger.warning(f"未找到标签 '{label_text}' 的表单项")
                return False

            is_cascader = form_item.evaluate("""
                el => {
                    const select = el.querySelector('.ant-select');
                    return select ? select.classList.contains('ant-cascader') : false;
                }
            """)

            if is_cascader:
                return self._select_cascader(form_item, label_text, option_index)
            else:
                return self._select_normal_dropdown(form_item, label_text, option_index)

        except Exception as e:
            logger.error(f"select_dropdown 错误: {e}")
            return False

    def _select_normal_dropdown(
        self, form_item: Locator, label_text: str, option_index: int = 0
    ) -> bool:
        """普通下拉选择器"""
        try:
            select = form_item.locator(".ant-select-selector").first
            select.click(force=True)
            self.page.wait_for_timeout(500)

            self.page.wait_for_selector(
                ".ant-select-dropdown:not(.ant-select-dropdown-hidden)",
                timeout=3000,
            )
            self.page.wait_for_timeout(500)

            options = self.page.locator(
                ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                ".ant-select-item-option"
            )
            count = options.count()
            if count == 0:
                logger.warning(f"下拉框 '{label_text}' 无选项")
                self.page.keyboard.press("Escape")
                return False

            logger.info(f"下拉框 '{label_text}' 选项数: {count}")

            # 选择第一个非禁用项
            for i in range(count):
                opt = options.nth(i)
                opt_text = opt.text_content() or ""
                if "禁用" not in opt_text:
                    opt.click(force=True)
                    self.page.wait_for_timeout(300)
                    return True

            options.nth(0).click(force=True)
            return True
        except Exception as e:
            logger.error(f"普通下拉选择失败: {e}")
            return False

    def _select_cascader(
        self, form_item: Locator, label_text: str, option_index: int = 0
    ) -> bool:
        """
        级联选择器 —— 使用 typeahead 搜索方式（支持多选）
        """
        try:
            logger.info(f"检测到级联选择器 '{label_text}'")

            # 清理 popup
            self.page.evaluate("""
                () => {
                    document.querySelectorAll(
                        '.ant-cascader-menus, .ant-select-dropdown'
                    ).forEach(m => m.remove());
                }
            """)
            self.page.wait_for_timeout(300)

            # 使用搜索框输入方式
            input_el = form_item.locator(".ant-cascader input").first
            if input_el.count() > 0:
                input_el.click()
                self.page.wait_for_timeout(300)

                # 输入搜索文本
                search_text = "北京市"
                input_el.fill(search_text)
                self.page.wait_for_timeout(1500)

                menus = self.page.locator(
                    ".ant-cascader-menus:not(.ant-cascader-hidden)"
                )
                if menus.count() > 0:
                    items = menus.first.locator(".ant-cascader-menu-item")
                    if items.count() > 0:
                        items.first.click(force=True)
                        self.page.wait_for_timeout(1000)

                        # 检查子菜单
                        sub_menus = self.page.locator(
                            ".ant-cascader-menus:not(.ant-cascader-hidden)"
                        ).nth(1)
                        if sub_menus.count() > 0:
                            sub_items = sub_menus.locator(
                                ".ant-cascader-menu-item"
                            )
                            if sub_items.count() > 0:
                                sub_items.first.click(force=True)
                                self.page.wait_for_timeout(1000)

                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(500)
                        return True

            # 回退：点击方式
            logger.info("搜索方式失败，尝试点击方式")
            selector = form_item.locator(
                ".ant-cascader .ant-select-selector"
            ).first
            selector.click(force=True)
            self.page.wait_for_timeout(1500)

            menus = self.page.locator(
                ".ant-cascader-menus:not(.ant-cascader-hidden)"
            )
            if menus.count() == 0:
                return False

            for level in range(3):
                menu = menus.nth(level)
                items = menu.locator(".ant-cascader-menu-item")
                count = items.count()
                if count == 0:
                    break

                for i in range(count):
                    item = items.nth(i)
                    classes = item.get_attribute("class") or ""
                    if "disabled" in classes:
                        continue
                    item_text = item.text_content() or ""
                    if "加载中" in item_text:
                        continue
                    logger.info(f"点击第{level+1}级: {item_text.strip()}")
                    item.click(force=True)
                    self.page.wait_for_timeout(1000)
                    break

                if menus.nth(level + 1).count() == 0:
                    break

            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            logger.error(f"级联选择失败: {e}")
            return False

    # ──────────── 富文本编辑器 ────────────

    def fill_tinymce_editor(self, content: str) -> bool:
        """
        填写 TinyMCE 富文本编辑器内容
        通过 tinymce API 设置内容并触发 save 同步到表单
        """
        try:
            # 方式1: TinyMCE API
            result = self.page.evaluate(
                """(content) => {
                    if (window.tinymce) {
                        const editors = window.tinymce.get();
                        if (editors.length > 0) {
                            for (const ed of editors) {
                                try {
                                    ed.setContent('<p>' + content + '</p>');
                                    ed.save();
                                    // 触发 textarea 事件
                                    const ta = document.querySelector(
                                        '.ant-modal textarea'
                                    );
                                    if (ta) {
                                        ta.dispatchEvent(new Event('input', {bubbles: true}));
                                        ta.dispatchEvent(new Event('change', {bubbles: true}));
                                    }
                                    return {success: true, method: 'tinymce_api'};
                                } catch(e) {}
                            }
                        }
                    }
                    return {success: false};
                }""",
                content,
            )
            if result.get("success"):
                logger.info(f"TinyMCE 内容填写成功 ({result.get('method')})")
                self.page.wait_for_timeout(1000)
                return True
            return False
        except Exception as e:
            logger.error(f"TinyMCE 填写失败: {e}")
            return False

    def fill_hidden_textarea(self, textarea_id: str, content: str) -> bool:
        """
        填写隐藏的 textarea（通过 JS 设置 value 并触发事件）
        适用于自定义富文本编辑器底层的隐藏 textarea
        """
        try:
            self.page.evaluate(
                """({id, content}) => {
                    const ta = document.getElementById(id);
                    if (ta) {
                        ta.value = content;
                        ta.dispatchEvent(new Event('input', {bubbles: true}));
                        ta.dispatchEvent(new Event('change', {bubbles: true}));
                        return true;
                    }
                    return false;
                }""",
                {"id": textarea_id, "content": content},
            )
            logger.info(f"隐藏 textarea 填写: {textarea_id}")
            return True
        except Exception as e:
            logger.error(f"隐藏 textarea 填写失败: {e}")
            return False

    # ──────────── Radio ────────────

    def select_first_radio_if_unchecked(self) -> dict:
        """选择弹窗内第一个未选中的 radio，返回 radio 组信息"""
        radio_info = self.page.evaluate("""
            () => {
                const radios = document.querySelectorAll('.ant-modal .ant-radio');
                const groups = {};
                radios.forEach((r, idx) => {
                    const formItem = r.closest('.ant-form-item');
                    const label = formItem
                        ? formItem.querySelector('.ant-form-item-label')?.textContent.trim()
                        : 'unknown';
                    if (!groups[label]) groups[label] = [];
                    groups[label].push({
                        index: idx,
                        checked: r.classList.contains('ant-radio-checked')
                    });
                });
                return groups;
            }
        """)
        for label, options in radio_info.items():
            if options and not any(o["checked"] for o in options):
                try:
                    radios = self.page.locator(".ant-modal .ant-radio")
                    radios.nth(options[0]["index"]).click()
                    logger.info(f"选择 Radio: {label}")
                except Exception as e:
                    logger.warning(f"选择 radio 失败: {e}")
        return radio_info

    # ──────────── UI 验证方法 ────────────

    def get_table_headers(self) -> list:
        """获取表格表头列表"""
        return self.page.evaluate("""
            () => {
                const thead = document.querySelector('.ant-table-thead');
                if (!thead) return [];
                return Array.from(thead.querySelectorAll('th'))
                    .map(th => th.textContent.trim())
                    .filter(t => t);
            }
        """)

    def get_table_row_count(self) -> int:
        """获取表格数据行数"""
        return self.page.locator(".ant-table-tbody tr.ant-table-row").count()

    def get_pagination_info(self) -> dict:
        """获取分页信息"""
        return self.page.evaluate("""
            () => {
                const p = document.querySelector('.ant-pagination');
                if (!p) return {exists: false};
                const total = p.querySelector('.ant-pagination-total-text');
                const active = p.querySelector('.ant-pagination-item-active');
                return {
                    exists: true,
                    total: total ? total.textContent.trim() : '',
                    current: active ? active.textContent.trim() : '1'
                };
            }
        """)

    def has_search_box(self, input_id: str = None) -> bool:
        """检查是否存在搜索框"""
        if input_id:
            return self.page.locator(f"#{input_id}").count() > 0
        return self.page.locator(
            ".ant-table-filter-trigger-container input, .jeecg-table-search input"
        ).count() > 0

    def search(self, keyword: str, input_id: str = None) -> None:
        """搜索并回车"""
        if input_id:
            el = self.page.locator(f"#{input_id}")
        else:
            el = self.page.locator(
                ".ant-table-filter-trigger-container input, .jeecg-table-search input"
            ).first
        el.fill(keyword)
        self.page.wait_for_timeout(500)
        el.press("Enter")
        self.page.wait_for_timeout(2000)
        logger.info(f"搜索: {keyword}")

    def clear_search(self, input_id: str = None) -> None:
        """清空搜索"""
        if input_id:
            el = self.page.locator(f"#{input_id}")
        else:
            el = self.page.locator(
                ".ant-table-filter-trigger-container input, .jeecg-table-search input"
            ).first
        el.fill("")
        el.press("Enter")
        self.page.wait_for_timeout(2000)
        logger.info("清空搜索")

    def get_modal_required_fields(self) -> list:
        """获取弹窗内必填字段标签"""
        return self.page.evaluate("""
            () => {
                const modal = document.querySelector('.ant-modal');
                if (!modal) return [];
                const required = modal.querySelectorAll('.ant-form-item-required');
                return Array.from(required).map(r => {
                    const item = r.closest('.ant-form-item');
                    return item?.querySelector('.ant-form-item-label')?.textContent.trim() || '';
                }).filter(t => t);
            }
        """)

    def submit_empty_form_and_get_errors(self) -> list:
        """提交空表单，返回验证错误信息"""
        self.page.locator('.ant-modal button:has-text("确 认")').first.click()
        self.page.wait_for_timeout(1000)
        errors = self.get_form_errors()
        logger.info(f"空表单验证错误: {errors}")
        return errors

    def close_modal_by_cancel(self) -> None:
        """点击取消按钮关闭弹窗"""
        cancel = self.page.locator('.ant-modal button:has-text("取 消")')
        if cancel.count() > 0:
            cancel.first.click()
            self.page.wait_for_timeout(500)
            logger.info("点击取消关闭弹窗")

    def close_modal_by_esc(self) -> None:
        """ESC 关闭弹窗"""
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)
        logger.info("ESC 关闭弹窗")

    def is_modal_open(self) -> bool:
        """弹窗是否打开"""
        return self.page.locator(".ant-modal").count() > 0

    # ──────────── 表单探索 ────────────

    def get_modal_form_fields(self) -> dict:
        """获取弹窗内所有可见 input / textarea 信息"""
        return self.page.evaluate("""
            () => {
                const inputs = Array.from(
                    document.querySelectorAll('.ant-modal input[codefield]')
                ).filter(i => i.offsetParent !== null);
                const textareas = Array.from(
                    document.querySelectorAll('.ant-modal textarea')
                );
                return {
                    inputs: inputs.map(i => ({
                        id: i.id,
                        placeholder: i.placeholder,
                        codefield: i.getAttribute('codefield')
                    })),
                    textareas: textareas.map(t => ({
                        id: t.id,
                        placeholder: t.placeholder,
                        visible: t.offsetParent !== null
                    }))
                };
            }
        """)
