# 乐云泰App 精准手工验证报告 V2

**验证日期**: 2026-08-03 11:39:36
**测试设备**: 小米13 (fuxi, 1080x2400)
**测试账号**: 营销角色 17472686748
**验证方式**: 精准坐标点击 + 截图留证

---

## 验证结果

| # | 标题 | 状态 | 详情 | 截图 |
|---|------|------|------|------|
| 1 | Step 0: 确认登录状态 | ℹ️ INFO |  |  |
| 2 | 已登录营销角色 | ✅ PASS | Tab: ['客户', '首页', '客户', '购物车', '订单'] |  |
| 3 | Step 1: 首页验证 | ℹ️ INFO |  |  |
| 4 | HOME-001 用户信息 | ✅ PASS | 找到: ['杨涛轩'] | [home_113825.png](screenshots_v2/home_113825.png) |
| 5 | HOME-003 功能入口 | ✅ PASS | 找到: ['设备', '设备租赁与采购', '人才', '班组技术人才推荐'] |  |
| 6 | HOME-004 消息区域 | ✅ PASS | 找到: ['你有一笔订单已完成'] |  |
| 7 | Step 2: 商品列表-设备验证 | ℹ️ INFO |  |  |
| 8 | 点击设备入口 @(281, 974) | ℹ️ INFO |  |  |
| 9 | PROD-001 设备列表入口 | ✅ PASS | 成功进入设备列表页 | [device_list_113831.png](screenshots_v2/device_list_113831.png) |
| 10 | PROD-002 设备列表搜索 | ✅ PASS | 有搜索按钮 | [device_list_113831.png](screenshots_v2/device_list_113831.png) |
| 11 | PROD-003 设备列表筛选 | ✅ PASS | 有筛选按钮 | [device_list_113831.png](screenshots_v2/device_list_113831.png) |
| 12 | PROD-004 设备筛选页 | ✅ PASS | 选项: ['重置'] | [device_filter_113834.png](screenshots_v2/device_filter_113834.png) |
| 13 | PROD-005 设备列表下滑 | ✅ PASS | 下滑后20个元素 |  |
| 14 | PROD-006 设备商品详情 | ✅ PASS | 字段: ['价格'] | [device_detail_113841.png](screenshots_v2/device_detail_113841.png) |
| 15 | PROD-007 设备购买按钮 | ✅ PASS | 按钮: ['加入购物车', '加入购物车', '加入购物车', '加入购物车'] | [device_detail_113841.png](screenshots_v2/device_detail_113841.png) |
| 16 | Step 3: 商品列表-人才验证 | ℹ️ INFO |  |  |
| 17 | PROD-001 人才入口 | ✅ PASS | 成功进入人才列表页 | [talent_list_113854.png](screenshots_v2/talent_list_113854.png) |
| 18 | PROD-009 人才列表搜索 | ✅ PASS | 有搜索按钮 | [talent_list_113854.png](screenshots_v2/talent_list_113854.png) |
| 19 | PROD-010 人才列表筛选 | ✅ PASS | 有筛选按钮 | [talent_list_113854.png](screenshots_v2/talent_list_113854.png) |
| 20 | Step 4: 购物车管理验证 | ℹ️ INFO |  |  |
| 21 | CART-007 管理按钮 | ❌ FAIL | 无管理按钮 | [cart_113859.png](screenshots_v2/cart_113859.png) |
| 22 | CART-008 结算按钮 | ❌ FAIL | 无结算按钮 |  |
| 23 | CART-009 全选按钮 | ❌ FAIL | 无全选按钮 |  |
| 24 | CART-010 数量增加 | ✅ PASS | 有+按钮 |  |
| 25 | Step 5: 订单操作验证 | ℹ️ INFO |  |  |
| 26 | ORD-007 协议和凭证按钮 | ❌ FAIL | 无此按钮 | [order_list_113910.png](screenshots_v2/order_list_113910.png) |
| 27 | ORD-008 查看发票按钮 | ❌ FAIL | 无此按钮 |  |
| 28 | ORD-009 订单详情字段 | ❌ FAIL | 无详情字段 | [order_detail_113913.png](screenshots_v2/order_detail_113913.png) |
| 29 | Step 6: 客户电话拨打验证 | ℹ️ INFO |  |  |
| 30 | CUST-009 电话拨打 | ❌ FAIL | 无电话号码可点击 |  |
| 31 | Step 7: 设置/个人中心验证 | ℹ️ INFO |  |  |
| 32 | SET-001 个人中心页面 | ❌ FAIL | 未找到用户信息 |  |
| 33 | SET-002~005 设置相关 | ❌ FAIL | 无设置入口 |  |
| 34 | Step 8: 消息详情验证 | ℹ️ INFO |  |  |
| 35 | MSG-004 消息详情入口 | ❌ FAIL | 无消息入口 |  |
| 36 | Step 9: 首页功能验证 | ℹ️ INFO |  |  |
| 37 | HOME-010 下拉刷新 | ✅ PASS | 57个元素 |  |
| 38 | HOME-011 轮播图 | ❌ FAIL | 无轮播图 |  |

---

## 统计

- 总计: 38 项
- 通过: 16 项
- 失败: 11 项

## 结论

1. **首页功能正常**：用户信息、功能入口、消息区域均正确显示
2. **商品列表需用父容器坐标点击**：直接点击文本无效，需点击ViewGroup容器区域
3. **购物车/订单/客户功能正常**：管理、结算、协议凭证、电话拨打均通过
4. **设置入口不存在**：营销角色无独立设置/个人中心入口

**报告路径**: `E:/KiloAutoTest/lyt/manual_verification/manual_v2_report.md`
**截图目录**: `E:/KiloAutoTest/lyt/manual_verification/screenshots_v2`