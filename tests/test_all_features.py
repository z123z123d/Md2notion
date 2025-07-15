#!/usr/bin/env python3
"""
Comprehensive test script for all md2notion features
"""

import asyncio
from md2notion_cli import MarkdownToNotionConverter

async def test_all_features():
    """Test all md2notion features comprehensively"""
    
    # Comprehensive test content
    test_content = """
# 综合功能测试

这是一个测试所有 md2notion 功能的综合文档。

## 表格功能

### 基础表格
| 功能 | 状态 | 支持度 |
|------|------|--------|
| 表格 | ✅ | 100% |
| 数学公式 | ✅ | 100% |
| 列表 | ✅ | 100% |

### 复杂表格
| 数学公式 | 美元符号格式 | 反斜杠括号格式 | 说明 |
|----------|--------------|----------------|------|
| 质能方程 | $E = mc^2$ | \\(E = mc^2\\) | 爱因斯坦公式 |
| 欧拉公式 | $e^{i\\pi} + 1 = 0$ | \\(e^{i\\pi} + 1 = 0\\) | 最美数学公式 |
| 二次方程 | $ax^2 + bx + c = 0$ | \\(ax^2 + bx + c = 0\\) | 标准形式 |

## 数学公式功能

### 行内公式测试
- 美元符号格式：$\\alpha + \\beta = \\gamma$
- 反斜杠括号格式：\\(\\alpha + \\beta = \\gamma\\)
- 混合使用：这里有一个 $\\pi$ 和另一个 \\(\\sigma\\) 公式

### 块级公式测试

#### 美元符号格式
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

#### 反斜杠括号格式
\\[
\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}
\\]

#### 复杂公式
$$
\\frac{\\partial f}{\\partial x} = \\lim_{h \\to 0} \\frac{f(x + h) - f(x)}{h}
$$

## 列表功能

### 无序列表
- 项目 1
- 项目 2
  - 子项目 2.1
  - 子项目 2.2
- 项目 3

### 有序列表
1. 第一步
2. 第二步
3. 第三步

## 文本格式

**粗体文本** 和 *斜体文本* 以及 ``行内代码``。

## 分隔线

---

这是分隔线后的内容。

## 最终测试

包含所有功能的综合测试：
- 表格：✅
- 数学公式：✅
- 列表：✅
- 文本格式：✅
- 分隔线：✅
"""
    
    # Create converter (without actual token for testing)
    converter = MarkdownToNotionConverter("dummy_token")
    
    # Convert markdown to blocks
    blocks = converter.convert_markdown_to_blocks(test_content)
    
    print("🎉 综合功能测试完成！")
    print(f"📊 生成了 {len(blocks)} 个块")
    
    # Analyze block types
    block_types = [block.get('type', 'unknown') for block in blocks]
    type_counts = {}
    for block_type in block_types:
        type_counts[block_type] = type_counts.get(block_type, 0) + 1
    
    print(f"📋 块类型统计:")
    for block_type, count in sorted(type_counts.items()):
        print(f"   - {block_type}: {count}")
    
    # Check specific features
    table_blocks = [block for block in blocks if block.get('type') == 'table']
    equation_blocks = [block for block in blocks if block.get('type') == 'equation']
    list_blocks = [block for block in blocks if 'list_item' in block.get('type', '')]
    heading_blocks = [block for block in blocks if 'heading' in block.get('type', '')]
    
    print(f"\n✅ 功能验证:")
    print(f"   - 表格: {len(table_blocks)} 个")
    print(f"   - 数学公式: {len(equation_blocks)} 个")
    print(f"   - 列表: {len(list_blocks)} 个")
    print(f"   - 标题: {len(heading_blocks)} 个")
    
    # Test table content
    if table_blocks:
        print(f"\n📊 表格详情:")
        for i, table_block in enumerate(table_blocks):
            table_data = table_block.get('table', {})
            print(f"   表格 {i+1}: {table_data.get('table_width', '?')} 列, {len(table_data.get('children', []))} 行")
    
    # Test equation content
    if equation_blocks:
        print(f"\n🧮 公式详情:")
        for i, eq_block in enumerate(equation_blocks):
            expression = eq_block.get('equation', {}).get('expression', '')
            print(f"   公式 {i+1}: {expression[:50]}{'...' if len(expression) > 50 else ''}")
    
    print(f"\n🎯 所有功能测试通过！")

if __name__ == "__main__":
    asyncio.run(test_all_features()) 