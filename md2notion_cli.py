#!/usr/bin/env python3
"""
Markdown to Notion Converter

A simple command-line tool to convert and upload Markdown files to Notion pages.
"""

import re
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

try:
    from notion_client import Client
except ImportError:
    print("Error: notion-client package not found. Please install it with: pip install notion-client")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarkdownToNotionConverter:
    """Convert Markdown content to Notion blocks"""
    
    def __init__(self, token: str):
        """Initialize the converter with Notion API token"""
        self.notion = Client(auth=token)
        # Use sync methods to avoid async issues
    
    def clean_title(self, text: str) -> str:
        """Remove markdown formatting from title"""
        return re.sub(r'\*+', '', text).strip()
    
    def split_text_for_rich_text(self, text: str, max_length: int = 100) -> List[str]:
        """
        Split text into chunks that fit within Notion's rich_text length limit.
        Preserves word boundaries when possible.
        
        Args:
            text: Text to split
            max_length: Maximum length per chunk (default 100 for Notion API)
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        words = text.split()
        
        for word in words:
            # If adding this word would exceed the limit
            if len(current_chunk) + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = word
                else:
                    # Single word is too long, split it
                    while len(word) > max_length:
                        chunks.append(word[:max_length])
                        word = word[max_length:]
                    current_chunk = word
            else:
                if current_chunk:
                    current_chunk += " " + word
                else:
                    current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def parse_equations_and_style(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse equations and text styling
        优先提取所有$...$公式块，剩余部分再做样式分割，保证公式内容不被样式正则分割。
        """
        import re
        rich_text = []
        # 先分割出所有$...$公式块（避免匹配$$...$$）
        pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', re.DOTALL)
        last_idx = 0
        for m in pattern.finditer(text):
            # 公式前的普通文本
            if m.start() > last_idx:
                t = text[last_idx:m.start()]
                if t:
                    rich_text.extend(self.parse_style(t))
            # 公式内容
            eq = m.group(1)
            eq = eq.strip('\n ').replace('\n', ' ')
            rich_text.append({
                "type": "equation",
                "equation": {"expression": eq}
            })
            last_idx = m.end()
        # 公式后的普通文本
        if last_idx < len(text):
            t = text[last_idx:]
            if t:
                rich_text.extend(self.parse_style(t))
        return rich_text
    
    def parse_style(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse text styling
        Supports: **text** bold, *text* italic, `text` code
        Priority: code > bold > italic > text
        """
        rich_text = []
        pattern = r'(`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_|[^*_`]+)'
        
        for m in re.finditer(pattern, text):
            s = m.group(0)
            if s.startswith('`') and s.endswith('`'):
                rich_text.append({
                    "type": "text",
                    "text": {"content": s[1:-1]},
                    "annotations": {"code": True, "italic": False, "bold": False, 
                                  "underline": False, "strikethrough": False, "color": "default"}
                })
            elif (s.startswith('**') and s.endswith('**')) or (s.startswith('__') and s.endswith('__')):
                rich_text.append({
                    "type": "text",
                    "text": {"content": s[2:-2]},
                    "annotations": {"bold": True, "italic": False, "code": False, 
                                  "underline": False, "strikethrough": False, "color": "default"}
                })
            elif (s.startswith('*') and s.endswith('*')) or (s.startswith('_') and s.endswith('_')):
                rich_text.append({
                    "type": "text",
                    "text": {"content": s[1:-1]},
                    "annotations": {"italic": True, "bold": False, "code": False, 
                                  "underline": False, "strikethrough": False, "color": "default"}
                })
            else:
                rich_text.append({
                    "type": "text",
                    "text": {"content": s},
                    "annotations": {"italic": False, "bold": False, "code": False, 
                                  "underline": False, "strikethrough": False, "color": "default"}
                })
        
        return rich_text
    
    def convert_markdown_to_blocks(self, markdown_content: str) -> list:
        """
        Convert Markdown content to Notion blocks
        支持标题、块级公式、列表、段落、分隔线、内联公式，保证顺序与原文一致
        """
        import re
        blocks = []

        # 清理特殊字符
        markdown_content = markdown_content.replace('\x0c', '\\frac')
        markdown_content = markdown_content.replace('\x07', '\\alpha')

        # 1. 分割为文本块和块级公式块
        # 支持多行和单行块级公式
        pattern = re.compile(r'(\$\$\s*\n.*?\n\s*\$\$|\$\$.*?\$\$)', re.DOTALL)
        parts = pattern.split(markdown_content)

        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.startswith('$$'):
                # 块级公式
                latex = part[2:-2].strip()  # 去除前后$$
                latex = latex.replace('\n', '\\')
                blocks.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": latex}
                })
            else:
                # 普通文本块，处理标题、列表、分隔线、段落、内联公式
                # 先处理标题
                def heading_sub(m):
                    level = len(m.group(1))
                    title = m.group(2).strip()
                    blocks.append({
                        "object": "block",
                        "type": f"heading_{level}",
                        f"heading_{level}": {
                            "rich_text": self.parse_equations_and_style(title)
                        }
                    })
                    return ''
                part = re.sub(r'^(#{1,3})\s+(.+)$', heading_sub, part, flags=re.MULTILINE)

                # 处理列表和分隔线
                lines = part.split('\n')
                paragraph_lines = []
                for line in lines:
                    line_strip = line.strip()
                    if re.match(r'^\d+\.\s+', line_strip):
                        # 先输出前面累计的段落
                        if paragraph_lines:
                            self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
                            paragraph_lines = []
                        item_text = re.sub(r'^\d+\.\s+', '', line_strip)
                        blocks.append({
                            "object": "block",
                            "type": "numbered_list_item",
                            "numbered_list_item": {
                                "rich_text": self.parse_equations_and_style(item_text)
                            }
                        })
                    elif line_strip.startswith('* '):
                        if paragraph_lines:
                            self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
                            paragraph_lines = []
                        item_text = line_strip[2:].strip()
                        blocks.append({
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": self.parse_equations_and_style(item_text)
                            }
                        })
                    elif re.match(r'^\s*-{3,}\s*$', line_strip):
                        if paragraph_lines:
                            self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
                            paragraph_lines = []
                        blocks.append({"object": "block", "type": "divider", "divider": {}})
                    else:
                        paragraph_lines.append(line)
                # 剩余段落
                if paragraph_lines:
                    self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
        return blocks

    def _append_paragraph_block(self, blocks, text):
        """辅助函数：将段落文本分割为 Notion 段落块，支持内联公式"""
        text = text.strip()
        if not text:
            return
        # 智能分段，包含公式的整体处理，否则分割
        dollar_count = text.count('$')
        if dollar_count >= 2:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": self.parse_equations_and_style(text)
                }
            })
        else:
            # 分割长段落
            for chunk in self.split_text_for_rich_text(text):
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": self.parse_equations_and_style(chunk)
                    }
                })

    def append_markdown_text_to_notion(self, markdown_content: str, page_id: str) -> str:
        """
        Append Markdown text content to existing Notion page
        
        Args:
            markdown_content: Markdown text content
            page_id: Notion page ID
        
        Returns:
            URL of the target page
        """
        try:
            logger.info(f"Processing markdown content (length: {len(markdown_content)})")
            
            # Convert to Notion blocks
            blocks = self.convert_markdown_to_blocks(markdown_content)
            logger.info(f"Converted {len(blocks)} blocks")
            
            # Get page info to return URL
            page_info = self.notion.pages.retrieve(page_id=page_id)  # type: ignore
            page_url = page_info['url']  # type: ignore
            
            # Add content blocks to existing page
            if blocks:
                # Notion API 限制每次最多 100 blocks
                for i in range(0, len(blocks), 100):
                    batch = blocks[i:i+100]
                    self.notion.blocks.children.append(  # type: ignore
                        block_id=page_id,
                        children=batch
                    )
                logger.info(f"Added {len(blocks)} content blocks to existing page")
            
            return page_url
            
        except Exception as e:
            logger.error(f"Error appending to Notion: {str(e)}")
            raise

    def upload_markdown_text_to_notion(self, markdown_content: str, page_id: str, title: str | None = None) -> str:
        """
        Upload Markdown text content to Notion page
        
        Args:
            markdown_content: Markdown text content
            page_id: Notion page ID
            title: Page title (optional, defaults to "Untitled")
        
        Returns:
            URL of the created page
        """
        try:
            logger.info(f"Processing markdown content (length: {len(markdown_content)})")
            
            # Convert to Notion blocks
            blocks = self.convert_markdown_to_blocks(markdown_content)
            logger.info(f"Converted {len(blocks)} blocks")
            
            # Use default title if not provided
            if not title:
                title = "Untitled"
            
            # Create new page
            new_page = self.notion.pages.create(  # type: ignore
                parent={"page_id": page_id},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                }
            )
            
            logger.info(f"Created new page: {new_page['url']}")  # type: ignore
            
            # Add content blocks
            if blocks:
                # Notion API 限制每次最多 100 blocks
                for i in range(0, len(blocks), 100):
                    batch = blocks[i:i+100]
                    self.notion.blocks.children.append(  # type: ignore
                        block_id=new_page["id"],  # type: ignore
                        children=batch
                    )
                logger.info(f"Added {len(blocks)} content blocks")
            
            return new_page['url']  # type: ignore
            
        except Exception as e:
            logger.error(f"Error uploading to Notion: {str(e)}")
            raise

    def upload_to_notion(self, markdown_file: str, page_id: str, title: str | None = None) -> str:
        """
        Upload Markdown file to Notion page
        
        Args:
            markdown_file: Path to markdown file
            page_id: Notion page ID
            title: Page title (optional, defaults to filename)
        
        Returns:
            URL of the created page
        """
        try:
            # Read markdown file
            with open(markdown_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"Reading markdown file: {markdown_file}")
            
            # Use filename as title if not provided
            if not title:
                title = Path(markdown_file).stem
            
            # Use the text upload method
            return self.upload_markdown_text_to_notion(content, page_id, title)
            
        except FileNotFoundError:
            logger.error(f"Markdown file not found: {markdown_file}")
            raise
        except Exception as e:
            logger.error(f"Error uploading to Notion: {str(e)}")
            raise


def get_token_from_env() -> str:
    """Get Notion token from environment variable"""
    token = os.getenv('NOTION_TOKEN')
    if not token:
        raise ValueError("NOTION_TOKEN environment variable not set")
    return token


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to Notion pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variable for token
  export NOTION_TOKEN="your_token_here"
  python md2notion.py document.md --page_id your_page_id

  # Using command line argument for token
  python md2notion.py document.md --page_id your_page_id --token your_token_here

  # With custom title
  python md2notion.py document.md --page_id your_page_id --title "My Document"
        """
    )
    
    parser.add_argument(
        'markdown_file',
        help='Path to the markdown file to convert'
    )
    
    parser.add_argument(
        '--page_id',
        required=True,
        help='Notion page ID where to create the new page'
    )
    
    parser.add_argument(
        '--token',
        help='Notion API token (or set NOTION_TOKEN environment variable)'
    )
    
    parser.add_argument(
        '--title',
        help='Title for the new Notion page (defaults to filename)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Get token
        if args.token:
            token = args.token
        else:
            token = get_token_from_env()
        
        # Validate markdown file
        if not os.path.exists(args.markdown_file):
            logger.error(f"Markdown file not found: {args.markdown_file}")
            sys.exit(1)
        
        # Convert and upload
        converter = MarkdownToNotionConverter(token)
        url = converter.upload_to_notion(args.markdown_file, args.page_id, args.title)
        
        print(f"\n✅ Successfully uploaded to Notion!")
        print(f"📄 Page URL: {url}")
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 