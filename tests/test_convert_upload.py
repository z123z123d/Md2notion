#!/usr/bin/env python3
"""
Comprehensive test script for all content types
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from md2notion_cli import MarkdownToNotionConverter

def print_block_details(block, index):
    """Print detailed information about a single block"""
    print(f"\n📦 块 #{index + 1}:")
    print(f"   类型: {block.get('type', 'unknown')}")
    
    # Get the content based on block type
    content = block.get(block.get('type', ''), {})
    
    if isinstance(content, dict):
        # Handle rich text content
        rich_text = content.get('rich_text', [])
        if rich_text:
            print(f"   内容: {len(rich_text)} 个文本片段")
            for i, text_item in enumerate(rich_text):
                text_content = text_item.get('text', {}).get('content', '')
                annotations = text_item.get('annotations', {})
                print(f"     片段 {i+1}: '{text_content[:50]}{'...' if len(text_content) > 50 else ''}'")
                if annotations:
                    print(f"       样式: {annotations}")
        
        # Handle other content types
        if 'url' in content:
            print(f"   URL: {content['url']}")
        if 'external' in content:
            print(f"   外部链接: {content['external'].get('url', '')}")
        if 'file' in content:
            print(f"   文件: {content['file'].get('url', '')}")
        if 'caption' in content:
            caption = content['caption']
            if caption and len(caption) > 0:
                print(f"   标题: {caption[0].get('text', {}).get('content', '')}")
        
        # Handle list items
        if 'children' in content:
            print(f"   子块数量: {len(content['children'])}")
        
        # Handle table
        if 'table_width' in content:
            print(f"   表格宽度: {content['table_width']}")
            if 'children' in content:
                print(f"   表格行数: {len(content['children'])}")
    
    # Print full block structure for debugging
    print(f"   完整结构: {json.dumps(block, indent=2, ensure_ascii=False)}")

async def test_convert_upload(test_files: list[str] = []):
    """Test all content types with markdown files"""
    
    print("🎯 全面测试所有内容类型")
    print("=" * 60)
    
    # Get token from environment
    token = os.getenv('NOTION_TOKEN')
    if not token:
        print("❌ 请设置 NOTION_TOKEN 环境变量")
        return
    
    # Test page ID
    test_page_id = "24997b0feb94803b94bac77c5eb751ea"  # Replace with your actual page ID
    
    # Create converter
    converter = MarkdownToNotionConverter(token)
    
    print(f"\n1️⃣ 读取测试文件")
    print("-" * 30)
    
    # Read all test files
    test_contents = {}
    for file_path in test_files:
        file_path = Path(file_path)
        filename = file_path.name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            test_contents[filename] = content
            print(f"✅ 读取文件: {filename}")
        else:
            print(f"❌ 文件不存在: {filename}")
    
    if not test_contents:
        print("❌ 没有找到任何测试文件")
        return
    
    print(f"\n2️⃣ 测试转换功能")
    print("-" * 30)
    
    # Test conversion for each file
    for filename, content in test_contents.items():
        print(f"\n测试文件: {filename}")
        print(f"内容长度: {len(content)} 字符")
        
        try:
            # Test conversion
            blocks = converter.convert_markdown_to_blocks(content)
            print(f"✅ 转换成功，生成了 {len(blocks)} 个块")
            
            # Analyze block types
            block_types = [block.get('type', 'unknown') for block in blocks]
            type_counts = {}
            for block_type in block_types:
                type_counts[block_type] = type_counts.get(block_type, 0) + 1
            
            print(f"块类型统计:")
            for block_type, count in sorted(type_counts.items()):
                print(f"  - {block_type}: {count}")
            
            # Print detailed information for each block
            print(f"\n📋 详细块信息:")
            print("-" * 40)
            for i, block in enumerate(blocks):
                print_block_details(block, i)
            
        except Exception as e:
            print(f"❌ 转换失败: {str(e)}")
            continue
    
    print(f"\n3️⃣ 测试上传功能")
    print("-" * 30)
    
    # Test upload for each file
    for filename, content in test_contents.items():
        print(f"\n上传文件: {filename}")
        
        try:
            # Test upload
            result = await converter.append_markdown_to_notion(content, test_page_id)
            print(f"✅ 上传成功: {result}")
            
        except Exception as e:
            print(f"❌ 上传失败: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            continue
    
    print(f"\n4️⃣ 测试文件上传功能")
    print("-" * 30)
    
    # Test file upload for each file
    for filename in test_contents.keys():
        file_path = Path(__file__).parent / "test_files" / filename
        print(f"\n上传文件: {filename}")
        
        try:
            # Test file upload
            result = await converter.upload_file_to_notion(str(file_path), test_page_id, f"Test-{filename}")
            print(f"✅ 文件上传成功: {result}")
            
        except Exception as e:
            print(f"❌ 文件上传失败: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            continue
    
    print(f"\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("📋 测试总结:")
    print("✅ 转换功能测试")
    print("✅ 上传功能测试")
    print("✅ 文件上传功能测试")
    print("✅ 各种内容类型测试")