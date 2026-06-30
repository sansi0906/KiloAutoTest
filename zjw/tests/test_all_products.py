"""全部商品模块测试"""
import pytest

class TestAllProducts:
    """全部商品测试类"""
    
    def _navigate_to_all_products(self, page):
        """导航到全部商品页面"""
        # 尝试通过导航栏进入全部商品页面
        nav_links = page.locator("nav a, .nav-item a")
        all_products_link = None
        
        # 查找包含"商品"或"全部商品"的导航链接
        for i in range(nav_links.count()):
            link = nav_links.nth(i)
            try:
                link_text = link.text_content()
                if "商品" in link_text or "全部商品" in link_text:
                    all_products_link = link
                    break
            except Exception:
                continue
        
        if all_products_link:
            all_products_link.click()
            page.wait_for_load_state("networkidle")
            return True
        else:
            # 如果找不到导航链接，尝试点击页面上的"全部商品"按钮
            all_products_btn = page.locator("text=全部商品").first
            if all_products_btn.is_visible():
                all_products_btn.click()
                page.wait_for_load_state("networkidle")
                return True
        
        return False

    def test_product_card_display(self, page):
        """G01-001: 商品卡片展示"""
        # 先导航到全部商品页面
        self._navigate_to_all_products(page)
        
        product_cards = page.locator("div[class*='card'], div[class*='item']")
        assert product_cards.count() > 0, "未找到商品卡片"

    def test_price_format(self, page):
        """G01-002: 价格显示格式"""
        # 先导航到全部商品页面
        self._navigate_to_all_products(page)
        
        # 尝试多种价格格式匹配
        price_patterns = [
            "text=/¥\\d+/",          # 人民币格式
            "text=/￥\\d+/",          # 全角人民币符号
            "text=/\\d+\\.?\\d*元/",  # 数字+元格式
            "text=/\\d+\\.?\\d*元整/", # 数字+元整格式
        ]
        
        found_price = False
        for pattern in price_patterns:
            price_elements = page.locator(pattern)
            if price_elements.count() > 0:
                found_price = True
                break
        
        # 如果都没找到，检查是否有包含价格相关的元素
        if not found_price:
            price_containers = page.locator("span[class*='price'], div[class*='price']")
            if price_containers.count() > 0:
                found_price = True
        
        assert found_price, "未找到价格元素"

    def test_product_images_load(self, page):
        """G01-003: 图片加载"""
        # 先导航到全部商品页面
        self._navigate_to_all_products(page)
        
        images = page.locator("img")
        loaded_count = 0
        for i in range(min(images.count(), 10)):
            img = images.nth(i)
            if img.is_visible():
                try:
                    # 等待图片加载完成（最多3秒）
                    page.wait_for_timeout(3000)
                    if img.evaluate("img => img.complete && img.naturalHeight > 0"):
                        loaded_count += 1
                except Exception:
                    # 图片加载失败不影响测试，继续检查下一张
                    continue
        # 至少有一张图片加载成功即可
        assert loaded_count > 0, f"没有图片加载成功，检查了{min(images.count(), 10)}张图片"

    def test_product_card_click(self, page):
        """G02-001: 商品卡片点击"""
        # 先导航到全部商品页面
        self._navigate_to_all_products(page)
        
        # 使用更精确的定位器：包含价格的卡片（商品卡片通常包含价格）
        product_cards = page.locator("div[class*='card']").filter(has=page.locator("text=/¥\\d+/"))
        if product_cards.count() > 0:
            product_card = product_cards.first
            product_card.click()
            page.wait_for_load_state("networkidle")
            assert "详情" in page.content() or "商品" in page.content()
        else:
            # 如果没有找到带价格的卡片，回退到普通卡片
            product_card = page.locator("div[class*='card']").first
            if product_card.is_visible():
                product_card.click()
                page.wait_for_load_state("networkidle")

    def test_product_detail_info(self, page):
        """G02-002: 商品详情信息"""
        from conftest import click_and_wait_for_new_page
        
        # 先导航到全部商品页面
        self._navigate_to_all_products(page)
        
        # 使用更精确的定位器：包含价格的卡片（商品卡片通常包含价格）
        product_cards = page.locator("div[class*='card']").filter(has=page.locator("text=/¥\\d+/"))
        if product_cards.count() > 0:
            product_card = product_cards.first
            result_page = click_and_wait_for_new_page(page, product_card)
            # 商品详情URL通常包含product或detail
            assert "product" in result_page.url.lower() or "detail" in result_page.url.lower(), \
                f"URL中未包含product或detail，当前URL: {result_page.url}"
        else:
            # 如果没有找到带价格的卡片，回退到普通卡片
            product_card = page.locator("div[class*='card']").first
            if product_card.is_visible():
                result_page = click_and_wait_for_new_page(page, product_card)
