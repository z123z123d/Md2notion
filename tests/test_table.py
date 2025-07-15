#!/usr/bin/env python3
"""
Test script for table functionality
"""

import asyncio
from md2notion_cli import MarkdownToNotionConverter

async def test_table_conversion():
    """Test table conversion functionality"""
    
    # Test markdown content with tables
    test_content = """
# 测试表格功能

## 简单表格

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |

## 复杂表格

| 姓名 | 年龄 | 职业 | 薪资 |
|------|------|------|------|
| 张三 | 25 | 工程师 | $5000 |
| 李四 | 30 | 设计师 | $6000 |
| 王五 | 28 | 产品经理 | $7000 |

## 普通文本

这是表格后的普通文本内容。
"""
    
    # Create converter (without actual token for testing)
    converter = MarkdownToNotionConverter("dummy_token")
    
    # Convert markdown to blocks
    blocks = converter.convert_markdown_to_blocks(test_content)
    
    print("✅ 转换完成！")
    print(f"📊 生成了 {len(blocks)} 个块")
    
    # Print block types
    block_types = [block.get('type', 'unknown') for block in blocks]
    print(f"📋 块类型: {block_types}")
    
    # Check for table blocks
    table_blocks = [block for block in blocks if block.get('type') == 'table']
    print(f"📊 表格块数量: {len(table_blocks)}")
    
    for i, table_block in enumerate(table_blocks):
        print(f"\n📊 表格 {i+1}:")
        table_data = table_block.get('table', {})
        print(f"   - 列数: {table_data.get('table_width', 'unknown')}")
        print(f"   - 有列标题: {table_data.get('has_column_header', False)}")
        print(f"   - 行数: {len(table_data.get('children', []))}")
        
        # Print table content
        for j, row in enumerate(table_data.get('children', [])):
            cells = row.get('table_row', {}).get('cells', [])
            cell_texts = []
            for cell in cells:
                if cell and len(cell) > 0:
                    cell_texts.append(cell[0].get('text', {}).get('content', ''))
                else:
                    cell_texts.append('')
            print(f"   行 {j+1}: {' | '.join(cell_texts)}")

if __name__ == "__main__":
    asyncio.run(test_table_conversion()) 