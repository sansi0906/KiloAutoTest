# 津筑网 App 自动化测试系统

## 项目简介

这是一个基于Python和ADB的津筑网App自动化测试系统，能够按照测试用例文档中的顺序执行测试，生成详细的HTML测试报告和测试截图。

## 功能特性

- ✅ 按用例顺序自动执行测试
- ✅ 生成带时间戳的HTML测试报告
- ✅ 自动保存测试截图（按时间戳分类存储）
- ✅ 支持中间结果保存（每10个用例）
- ✅ 详细的测试统计和失败分析
- ✅ 响应式测试报告界面
- ✅ 支持测试重试和错误恢复

## 项目结构

```
KiloAutoTest/
├── jzw/
│   ├── run_tests.py              # 主测试执行脚本
│   ├── test_case_executor.py     # 测试用例执行器
│   ├── test_report_generator.py  # 测试报告生成器
│   ├── screenshot_manager.py     # 截图管理器
│   ├── config.py                 # 配置文件
│   ├── testCase/
│   │   └── app_test_cases.md     # 测试用例文档
│   ├── reports/                  # 测试报告目录（自动创建）
│   └── screenshots/              # 截图目录（自动创建）
└── requirements.txt              # Python依赖
```

## 环境要求

- Python 3.7+
- ADB (Android Debug Bridge)
- Android设备或模拟器
- 津筑网App (com.tjxinyu.fz)

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置ADB环境

确保ADB已安装并配置到系统PATH中：

```bash
adb version
```

### 3. 连接Android设备

```bash
adb devices
```

确保设备已连接并授权USB调试。

### 4. 安装测试App

```bash
adb install jzw/apk/xy50-test-2026-05-26\ 09_11_36.apk
```

## 使用方法

### 基本使用

```bash
cd E:\KiloAutoTest\jzw
python run_tests.py
```

### 自定义配置

编辑 `config.py` 文件来自定义测试配置：

```python
# 修改测试用例文件路径
test_case_file = "jzw/testCase/app_test_cases.md"

# 修改设备坐标（根据实际设备调整）
coordinates = {
    "nav_home": [135, 2300],  # 底部导航首页按钮坐标
    # ... 其他坐标
}
```

## 测试报告

### 报告位置

- HTML报告: `reports/test_report_YYYYMMDD_HHMMSS.html`
- 文本摘要: `reports/test_summary_YYYYMMDD_HHMMSS.txt`
- 测试截图: `screenshots/screenshots_YYYYMMDD_HHMMSS/`

### 报告内容

- 📊 测试概览统计
- 📈 通过率进度条
- 📋 按模块分组的测试结果
- 🖼️ 每个用例的执行前后截图
- ❌ 失败用例的详细错误信息
- ⏱️ 执行时间统计

## 测试用例格式

测试用例使用Markdown表格格式，位于 `testCase/app_test_cases.md`：

```markdown
| 用例ID | 用例名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|----------|----------|----------|--------|
| LOG-001 | 隐私政策页面同意 | 1. 启动App<br>2. 点击"同意"按钮 | 进入登录页面 | P0 |
```

## 坐标映射

系统使用预定义的坐标映射来执行点击操作。如需适配不同设备，请修改 `config.py` 中的坐标配置：

```python
coordinates = {
    "nav_home": [135, 2300],      # [x, y] 坐标
    "login_button": [500, 1430],
    # ... 更多坐标
}
```

### 获取元素坐标

使用ADB命令获取元素坐标：

```bash
# 1. 获取当前页面UI结构
adb shell uiautomator dump

# 2. 拉取XML文件
adb pull /sdcard/window_dump.xml

# 3. 解析XML查找元素bounds属性
# bounds="[x1,y1][x2,y2]" -> 中心点坐标: ((x1+x2)/2, (y1+y2)/2)
```

## 故障排除

### ADB连接失败

```bash
# 重启ADB服务
adb kill-server
adb start-server

# 检查设备连接
adb devices -l
```

### 截图失败

```bash
# 检查存储权限
adb shell pm grant com.tjxinyu.fz android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant com.tjxinyu.fz android.permission.WRITE_EXTERNAL_STORAGE
```

### 测试执行超时

修改 `config.py` 中的超时配置：

```python
page_load_timeout = 5  # 增加页面加载超时时间
element_find_timeout = 10  # 增加元素查找超时时间
```

## 扩展功能

### 添加新的测试步骤

在 `test_case_executor.py` 中的 `_execute_step` 方法添加新的步骤处理逻辑：

```python
def _execute_step(self, step):
    if "滑动" in step:
        return self._handle_swipe(step)
    # ... 其他步骤处理
```

### 自定义报告样式

修改 `test_report_generator.py` 中的CSS样式来自定义报告外观。

### 集成CI/CD

可以将测试脚本集成到CI/CD流程中：

```yaml
# GitHub Actions 示例
- name: Run App Tests
  run: |
    cd jzw
    python run_tests.py
    
- name: Upload Test Reports
  uses: actions/upload-artifact@v2
  with:
    name: test-reports
    path: jzw/reports/
```

## 注意事项

1. **设备分辨率**: 坐标映射需要根据实际设备分辨率调整
2. **网络连接**: 某些测试需要网络连接，确保设备网络正常
3. **App状态**: 测试前确保App处于初始状态
4. **权限授予**: 确保App已获得必要的系统权限
5. **测试数据**: 使用测试账号进行测试，避免影响生产数据

## 维护建议

1. **定期更新**: 当App UI变化时，及时更新坐标映射
2. **清理文件**: 定期清理旧的测试报告和截图文件
3. **监控执行**: 关注测试执行日志，及时发现异常
4. **优化用例**: 根据测试结果优化测试用例

## 技术支持

如有问题，请检查：
1. ADB连接状态
2. 设备授权情况
3. App安装状态
4. 配置文件正确性
5. 测试用例格式

## 许可证

内部测试项目，仅供团队内部使用。

---

**最后更新**: 2026-06-16  
**版本**: v1.0  
**维护者**: 测试团队