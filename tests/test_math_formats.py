#!/usr/bin/env python3
"""
Test script for different math equation formats
"""

import asyncio
from md2notion_cli import MarkdownToNotionConverter

async def test_math_formats():
    """Test different math equation formats"""
    
    # Test markdown content with various math formats
    test_content = """
# 数学公式格式测试

## 行内公式测试

### 美元符号格式
这是一个行内公式：$E = mc^2$ 在文本中。

### 反斜杠括号格式
这是另一个行内公式：\\(E = mc^2\\) 在文本中。

### 混合格式
这里有一个 $\\alpha$ 和另一个 \\(\\beta\\) 公式。

## 块级公式测试

### 美元符号格式
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

### 反斜杠括号格式
\\[
\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}
\\]

### 复杂公式
$$
\\frac{\\partial f}{\\partial x} = \\lim_{h \\to 0} \\frac{f(x + h) - f(x)}{h}
$$

## 普通文本

这是公式后的普通文本内容。
"""
    
    # Create converter (without actual token for testing)
    converter = MarkdownToNotionConverter("dummy_token")
    
    # Convert markdown to blocks
    blocks = converter.convert_markdown_to_blocks(test_content)
    
    print("✅ 数学公式格式测试完成！")
    print(f"📊 生成了 {len(blocks)} 个块")
    
    # Print block types
    block_types = [block.get('type', 'unknown') for block in blocks]
    print(f"📋 块类型: {block_types}")
    
    # Check for equation blocks
    equation_blocks = [block for block in blocks if block.get('type') == 'equation']
    print(f"🧮 公式块数量: {len(equation_blocks)}")
    
    for i, eq_block in enumerate(equation_blocks):
        print(f"\n🧮 公式 {i+1}:")
        expression = eq_block.get('equation', {}).get('expression', '')
        print(f"   表达式: {expression}")
    
    # Check for rich text with equations
    rich_text_equations = []
    for block in blocks:
        if 'rich_text' in str(block):
            # This is a simplified check - in practice you'd need to traverse the rich_text structure
            if 'equation' in str(block):
                rich_text_equations.append(block)
    
    print(f"\n📝 包含行内公式的文本块数量: {len(rich_text_equations)}")

if __name__ == "__main__":
    asyncio.run(test_math_formats()) 