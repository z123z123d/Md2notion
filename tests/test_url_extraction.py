#!/usr/bin/env python3
"""
Test script for URL extraction functionality
"""

import asyncio
from md2notion_cli import extract_page_id_from_url

async def test_url_extraction():
    """Test URL extraction functionality"""
    
    # Test cases
    test_cases = [
        {
            "url": "https://www.notion.so/z123z123d/Survey-latent-reasoning-22f97b0feb94808fbfa4c07162457633?source=copy_link",
            "expected": "22f97b0feb94808fbfa4c07162457633",
            "description": "Full Notion URL with workspace and query params"
        },
        {
            "url": "https://www.notion.so/My-Page-22f97b0feb94808fbfa4c07162457633",
            "expected": "22f97b0feb94808fbfa4c07162457633",
            "description": "Notion URL with page name"
        },
        {
            "url": "https://www.notion.so/22f97b0feb94808fbfa4c07162457633",
            "expected": "22f97b0feb94808fbfa4c07162457633",
            "description": "Direct page ID URL"
        },
        {
            "url": "22f97b0feb94808fbfa4c07162457633",
            "expected": "22f97b0feb94808fbfa4c07162457633",
            "description": "Raw page ID"
        },
        {
            "url": "https://www.notion.so/workspace/Page-Title-1234567890abcdef1234567890abcdef",
            "expected": "1234567890abcdef1234567890abcdef",
            "description": "URL with different workspace and page title"
        }
    ]
    
    print("🧪 测试 URL 提取功能")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}: {test_case['description']}")
        print(f"   输入: {test_case['url']}")
        print(f"   期望: {test_case['expected']}")
        
        try:
            result = extract_page_id_from_url(test_case['url'])
            print(f"   结果: {result}")
            
            if result == test_case['expected']:
                print("   ✅ 通过")
                success_count += 1
            else:
                print("   ❌ 失败")
                
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败")
    
    # Test invalid URLs
    print("\n🧪 测试无效 URL")
    print("=" * 30)
    
    invalid_urls = [
        "https://www.notion.so/invalid",
        "https://example.com/page",
        "not-a-url",
        "https://www.notion.so/",
        ""
    ]
    
    for url in invalid_urls:
        print(f"\n📋 测试无效 URL: {url}")
        try:
            result = extract_page_id_from_url(url)
            print(f"   结果: {result}")
        except ValueError as e:
            print(f"   ✅ 正确抛出错误: {str(e)}")
        except Exception as e:
            print(f"   ❌ 意外错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_url_extraction()) 