# 测试说明

## 测试文件结构

```
tests/
├── README.md                    # 本说明文件
├── run_tests.py                 # 测试运行脚本
├── test_all_content.py          # 全面测试脚本
├── test_specific_issue.py       # 特定问题测试脚本
├── simple_text.md              # 简单文本测试
├── math_formulas.md            # 数学公式测试
├── tables.md                   # 表格测试
├── nested_lists.md             # 嵌套列表测试
├── complex_content.md          # 复杂内容综合测试
└── problematic_content.md      # 问题内容测试
```

## 测试内容

### 1. 简单文本测试 (`simple_text.md`)
- 基本标题和段落
- 简单列表
- 中文内容

### 2. 数学公式测试 (`math_formulas.md`)
- 行内公式：`$E = mc^2$`
- 块级公式：`$$...$$`
- 复杂数学表达式

### 3. 表格测试 (`tables.md`)
- 简单表格
- 包含数学公式的复杂表格
- 中文表格内容

### 4. 嵌套列表测试 (`nested_lists.md`)
- 有序列表嵌套
- 无序列表嵌套
- 混合列表结构

### 5. 复杂内容综合测试 (`complex_content.md`)
- 所有功能的综合测试
- 文本格式（粗体、斜体、代码）
- 分隔线
- 多种数学公式格式

### 6. 问题内容测试 (`problematic_content.md`)
- 之前遇到问题的具体内容
- 复杂的嵌套结构和数学公式

## 运行测试

### 设置环境变量
```bash
export NOTION_TOKEN="your_notion_token_here"
```

### 运行所有测试
```bash
cd tests
python run_tests.py
```

### 运行特定测试
```bash
# 运行全面测试
python test_all_content.py

# 运行特定问题测试
python test_specific_issue.py
```

## 添加新的测试样例

1. 在 `tests/` 目录下创建新的 `.md` 文件
2. 在 `test_all_content.py` 的 `test_files` 列表中添加新文件名
3. 运行测试验证新样例

## 测试功能

每个测试脚本都会验证：

1. **转换功能** - Markdown 到 Notion 块的转换
2. **上传功能** - 直接内容上传到 Notion
3. **文件上传功能** - 从文件上传到 Notion
4. **块类型分析** - 统计生成的块类型
5. **错误处理** - 详细的错误信息

## 注意事项

- 确保设置了正确的 `NOTION_TOKEN` 环境变量
- 确保测试页面 ID 存在且有写入权限
- 测试文件使用 UTF-8 编码
- 数学公式使用 LaTeX 语法
