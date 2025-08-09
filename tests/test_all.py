#!/usr/bin/env python3
"""
Test runner script
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from test_convert_upload import test_convert_upload

async def test_all_content():
    """Run all tests"""
    
    print("🚀 运行所有测试")
    print("=" * 60)

    ## List all md files in tests directory
    md_path = Path(__file__).parent / "test_files"
    test_files = [f for f in md_path.glob("*.md")]
    
    await test_convert_upload(test_files)

if __name__ == "__main__":
    asyncio.run(test_all_content())
