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
    
    def _create_rich_text(self, content: str, annotations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a rich text object"""
        return {
            "type": "text",
            "text": {"content": content},
            "annotations": annotations or {
                "italic": False, "bold": False, "code": False,
                "underline": False, "strikethrough": False, "color": "default"
            }
        }
    
    def parse_style(self, text: str) -> List[Dict[str, Any]]:
        """Parse text styling: **bold**, *italic*, `code`"""
        rich_text = []
        
        # More robust pattern that handles nested content better
        # This pattern matches bold, italic, code, and regular text
        pattern = r'(`[^`]*`|\*\*[^*]*\*\*|__[^_]*__|\*[^*]*\*|_[^_]*_|[^*_`]+)'
        
        for match in re.finditer(pattern, text):
            content = match.group(0)
            
            if content.startswith('`') and content.endswith('`'):
                rich_text.append(self._create_rich_text(content[1:-1], {"code": True, "italic": False, "bold": False, "underline": False, "strikethrough": False, "color": "default"}))
            elif content.startswith('**') and content.endswith('**') or content.startswith('__') and content.endswith('__'):
                rich_text.append(self._create_rich_text(content[2:-2], {"bold": True, "italic": False, "code": False, "underline": False, "strikethrough": False, "color": "default"}))
            elif content.startswith('*') and content.endswith('*') or content.startswith('_') and content.endswith('_'):
                rich_text.append(self._create_rich_text(content[1:-1], {"italic": True, "bold": False, "code": False, "underline": False, "strikethrough": False, "color": "default"}))
            else:
                rich_text.append(self._create_rich_text(content))
        
        return rich_text
    
    def parse_equations_and_style(self, text: str) -> List[Dict[str, Any]]:
        """Parse inline equations and text styling"""
        rich_text = []
        # Extract inline equations first
        pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', re.DOTALL)
        last_idx = 0
        
        for match in pattern.finditer(text):
            # Text before equation
            if match.start() > last_idx:
                before_text = text[last_idx:match.start()]
                if before_text:
                    rich_text.extend(self.parse_style(before_text))
            
            # Equation content
            equation = match.group(1).strip('\n ').replace('\n', ' ')
            rich_text.append({
                "type": "equation",
                "equation": {"expression": equation}
            })
            last_idx = match.end()
        
        # Text after last equation
        if last_idx < len(text):
            remaining_text = text[last_idx:]
            if remaining_text:
                rich_text.extend(self.parse_style(remaining_text))
        
        return rich_text
    
    def _is_list_item(self, line: str) -> tuple[bool, str, str, int]:
        """Check if line is a list item. Returns: (is_list, type, content, indent_level)"""
        line_strip = line.strip()
        if not line_strip:
            return False, "", "", 0
        
        indent_level = len(line) - len(line.lstrip())
        
        # Check numbered list
        numbered_match = re.match(r'^\d+\.\s+(.+)$', line_strip)
        if numbered_match:
            return True, "numbered", numbered_match.group(1), indent_level
        
        # Check bulleted list
        bullet_match = re.match(r'^[\*\-+]\s+(.+)$', line_strip)
        if bullet_match:
            return True, "bulleted", bullet_match.group(1), indent_level
        
        return False, "", "", 0
    
    def _process_list_group(self, lines: list, start_index: int, blocks: list) -> int:
        """Process a group of list items with nesting"""
        i = start_index
        stack = []  # Stack to manage nesting levels: (indent_level, block)
        
        while i < len(lines):
            line = lines[i]
            is_list, list_type, content, indent_level = self._is_list_item(line)
            
            if not is_list:
                break
            
            # Create current list item
            current_block = {
                "object": "block",
                "type": f"{list_type}_list_item",
                f"{list_type}_list_item": {
                    "rich_text": self.parse_equations_and_style(content)
                },
                "_line_index": i
            }
            
            # Handle nesting
            while stack and stack[-1][0] >= indent_level:
                stack.pop()
            
            if stack:
                # Add to parent's children
                parent_indent, parent_block = stack[-1]
                parent_type = parent_block["type"]
                if "children" not in parent_block[parent_type]:
                    parent_block[parent_type]["children"] = []
                parent_block[parent_type]["children"].append(current_block)
            else:
                # Add to main blocks
                blocks.append(current_block)
            
            stack.append((indent_level, current_block))
            i += 1
        
        return i
    
    def _clean_blocks_recursively(self, blocks):
        """Remove temporary fields from blocks recursively"""
        if not isinstance(blocks, list):
            return blocks
        
        cleaned_blocks = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            
            # Copy block without temporary fields
            cleaned_block = {k: v for k, v in block.items() if k != '_line_index'}
            
            # Clean children recursively
            block_type = cleaned_block.get("type")
            if block_type in ["bulleted_list_item", "numbered_list_item"]:
                list_content = cleaned_block.get(block_type, {})
                if "children" in list_content:
                    list_content["children"] = self._clean_blocks_recursively(list_content["children"])
                    if not list_content["children"]:
                        del list_content["children"]
            
            cleaned_blocks.append(cleaned_block)
        
        return cleaned_blocks
    
    def _append_paragraph_block(self, blocks: list, text: str):
        """Add paragraph block(s) to blocks list"""
        text = text.strip()
        if not text:
            return
        
        # Split long paragraphs for Notion API limits
        max_length = 2000  # Conservative limit
        if len(text) <= max_length:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": self.parse_equations_and_style(text)
                }
            })
        else:
            # Split by sentences or at word boundaries
            chunks = []
            current_chunk = ""
            sentences = re.split(r'([.!?]+\s+)', text)
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= max_length:
                    current_chunk += sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            for chunk in chunks:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": self.parse_equations_and_style(chunk)
                    }
                })
    
    def convert_markdown_to_blocks(self, markdown_content: str) -> list:
        """Convert Markdown content to Notion blocks"""
        blocks = []
        
        # Split by block equations first
        equation_pattern = re.compile(r'(\$\$\s*\n.*?\n\s*\$\$|\$\$.*?\$\$)', re.DOTALL)
        parts = equation_pattern.split(markdown_content)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if part.startswith('$$'):
                # Block equation
                latex = part[2:-2].strip().replace('\n', '\\')
                blocks.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": latex}
                })
            else:
                # Process text content
                # Handle headings first
                def heading_replacer(match):
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    blocks.append({
                        "object": "block",
                        "type": f"heading_{level}",
                        f"heading_{level}": {
                            "rich_text": self.parse_equations_and_style(title)
                        }
                    })
                    return ''
                
                part = re.sub(r'^(#{1,3})\s+(.+)$', heading_replacer, part, flags=re.MULTILINE)
                
                # Process remaining content line by line
                lines = part.split('\n')
                paragraph_lines = []
                i = 0
                
                while i < len(lines):
                    line = lines[i]
                    line_strip = line.strip()
                    
                    # Check for divider
                    if re.match(r'^\s*-{3,}\s*$', line_strip):
                        if paragraph_lines:
                            self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
                            paragraph_lines = []
                        blocks.append({"object": "block", "type": "divider", "divider": {}})
                        i += 1
                        continue
                    
                    # Check for list items
                    is_list, _, _, _ = self._is_list_item(line)
                    if is_list:
                        if paragraph_lines:
                            self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
                            paragraph_lines = []
                        i = self._process_list_group(lines, i, blocks)
                    else:
                        paragraph_lines.append(line)
                        i += 1
                
                # Add remaining paragraphs
                if paragraph_lines:
                    self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
        
        return self._clean_blocks_recursively(blocks)
    
    def _upload_blocks(self, blocks: list, target_id: str, is_page: bool = False):
        """Upload blocks to Notion in batches"""
        if not blocks:
            return
        
        # Notion API limit: 100 blocks per request
        for i in range(0, len(blocks), 100):
            batch = blocks[i:i+100]
            if is_page:
                self.notion.blocks.children.append(block_id=target_id, children=batch)
            else:
                self.notion.blocks.children.append(block_id=target_id, children=batch)
    
    def append_markdown_to_notion(self, markdown_content: str, page_id: str) -> str:
        """Append Markdown content to existing Notion page"""
        logger.info(f"Processing markdown content (length: {len(markdown_content)})")
        
        blocks = self.convert_markdown_to_blocks(markdown_content)
        logger.info(f"Converted {len(blocks)} blocks")
        
        # Get page URL
        page_info = self.notion.pages.retrieve(page_id=page_id)
        page_url = page_info['url']
        
        # Upload blocks
        self._upload_blocks(blocks, page_id)
        logger.info(f"Added {len(blocks)} blocks to existing page")
        
        return page_url
    
    def upload_markdown_to_notion(self, markdown_content: str, page_id: str, title: str = "Untitled") -> str:
        """Upload Markdown content as new Notion page"""
        logger.info(f"Processing markdown content (length: {len(markdown_content)})")
        
        blocks = self.convert_markdown_to_blocks(markdown_content)
        logger.info(f"Converted {len(blocks)} blocks")
        
        # Create new page
        new_page = self.notion.pages.create(
            parent={"page_id": page_id},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        )
        
        logger.info(f"Created new page: {new_page['url']}")
        
        # Upload blocks
        self._upload_blocks(blocks, new_page["id"])
        logger.info(f"Added {len(blocks)} blocks to new page")
        
        return new_page['url']
    
    def upload_file_to_notion(self, markdown_file: str, page_id: str, title: str = None) -> str:
        """Upload Markdown file to Notion"""
        with open(markdown_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        logger.info(f"Reading markdown file: {markdown_file}")
        
        if not title:
            title = Path(markdown_file).stem
        
        return self.upload_markdown_to_notion(content, page_id, title)


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
  export NOTION_TOKEN="your_token_here"
  python md2notion_cli.py document.md --page_id your_page_id
  python md2notion_cli.py document.md --page_id your_page_id --title "My Document"
        """
    )
    
    parser.add_argument('markdown_file', help='Path to the markdown file')
    parser.add_argument('--page_id', required=True, help='Notion page ID')
    parser.add_argument('--token', help='Notion API token (or set NOTION_TOKEN env var)')
    parser.add_argument('--title', help='Title for the new page (defaults to filename)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Get token
        token = args.token or get_token_from_env()
        
        # Validate file
        if not os.path.exists(args.markdown_file):
            logger.error(f"Markdown file not found: {args.markdown_file}")
            sys.exit(1)
        
        # Convert and upload
        converter = MarkdownToNotionConverter(token)
        url = converter.upload_file_to_notion(args.markdown_file, args.page_id, args.title)
        
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