#!/usr/bin/env python3
"""
Test runner for md2notion
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_all_tests():
    """Run all test scripts"""
    
    test_files = [
        "tests/test_url_extraction.py",
        "tests/test_table.py", 
        "tests/test_math_formats.py",
        "tests/test_all_features.py",
        "tests/test_complete_features.py"
    ]
    
    print("🧪 Running all md2notion tests")
    print("=" * 50)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 Running {test_file}...")
            try:
                # Import and run the test module
                module_name = test_file.replace('/', '.').replace('.py', '')
                module = __import__(module_name, fromlist=[''])
                
                # Find the main test function
                if hasattr(module, 'test_url_extraction'):
                    await module.test_url_extraction()
                elif hasattr(module, 'test_table_conversion'):
                    await module.test_table_conversion()
                elif hasattr(module, 'test_math_formats'):
                    await module.test_math_formats()
                elif hasattr(module, 'test_all_features'):
                    await module.test_all_features()
                elif hasattr(module, 'test_complete_features'):
                    await module.test_complete_features()
                else:
                    print(f"   ⚠️  No test function found in {test_file}")
                    
            except Exception as e:
                print(f"   ❌ Error running {test_file}: {str(e)}")
        else:
            print(f"   ⚠️  Test file not found: {test_file}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 