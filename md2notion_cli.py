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
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from notion_client import AsyncClient
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
        self.notion = AsyncClient(auth=token)
    
    def _create_rich_text(self, content: str, annotations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        """Parse inline equations and text styling with better mixed content handling"""
        rich_text = []
        
        # First, check if there are styled blocks that contain equations
        # Pattern to match styled content that might contain equations
        styled_pattern = re.compile(r'(\*\*[^*]*?\$[^*]*?\$[^*]*?\*\*|__[^_]*?\$[^_]*?\$[^_]*?__|\*[^*]*?\$[^*]*?\$[^*]*?\*|_[^_]*?\$[^_]*?\$[^_]*?_)')
        
        # Find all styled content with equations
        styled_matches = list(styled_pattern.finditer(text))
        
        if styled_matches:
            # Process styled content with equations
            last_idx = 0
            for match in styled_matches:
                # Add text before styled content
                if match.start() > last_idx:
                    before_text = text[last_idx:match.start()]
                    if before_text:
                        rich_text.extend(self._parse_mixed_content(before_text))
                
                # Process styled content with equations
                styled_content = match.group(0)
                rich_text.extend(self._parse_styled_with_equations(styled_content))
                
                last_idx = match.end()
            
            # Add remaining text
            if last_idx < len(text):
                remaining_text = text[last_idx:]
                if remaining_text:
                    rich_text.extend(self._parse_mixed_content(remaining_text))
        else:
            # No styled content with equations, use regular parsing
            rich_text = self._parse_mixed_content(text)
        
        return rich_text
    
    def _parse_styled_with_equations(self, styled_content: str) -> List[Dict[str, Any]]:
        """Parse styled content that contains equations"""
        rich_text = []
        
        # Determine the style type
        if styled_content.startswith('**') and styled_content.endswith('**'):
            style = {"bold": True, "italic": False, "code": False, "underline": False, "strikethrough": False, "color": "default"}
            content = styled_content[2:-2]
        elif styled_content.startswith('__') and styled_content.endswith('__'):
            style = {"bold": True, "italic": False, "code": False, "underline": False, "strikethrough": False, "color": "default"}
            content = styled_content[2:-2]
        elif styled_content.startswith('*') and styled_content.endswith('*'):
            style = {"bold": False, "italic": True, "code": False, "underline": False, "strikethrough": False, "color": "default"}
            content = styled_content[1:-1]
        elif styled_content.startswith('_') and styled_content.endswith('_'):
            style = {"bold": False, "italic": True, "code": False, "underline": False, "strikethrough": False, "color": "default"}
            content = styled_content[1:-1]
        else:
            # Fallback to regular text
            return [self._create_rich_text(styled_content)]
        
        # Parse equations within the styled content
        equation_pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)|\\\((.+?)\\\)', re.DOTALL)
        last_idx = 0
        
        for match in equation_pattern.finditer(content):
            # Text before equation
            if match.start() > last_idx:
                before_text = content[last_idx:match.start()]
                if before_text:
                    rich_text.append(self._create_rich_text(before_text, style))
            
            # Equation content
            if match.group(1):  # $...$ format
                equation = match.group(1).strip('\n ').replace('\n', ' ')
            else:  # \(...\) format
                equation = match.group(2).strip('\n ').replace('\n', ' ')
            
            if equation:
                rich_text.append({
                    "type": "equation",
                    "equation": {"expression": equation}
                })
            
            last_idx = match.end()
        
        # Text after last equation
        if last_idx < len(content):
            remaining_text = content[last_idx:]
            if remaining_text:
                rich_text.append(self._create_rich_text(remaining_text, style))
        
        return rich_text
    
    def _parse_mixed_content(self, text: str) -> List[Dict[str, Any]]:
        """Parse regular text that may contain equations and styling"""
        rich_text = []
        # Extract inline equations first (support both $...$ and \(...\) formats)
        pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)|\\\((.+?)\\\)', re.DOTALL)
        last_idx = 0
        
        for match in pattern.finditer(text):
            # Text before equation
            if match.start() > last_idx:
                before_text = text[last_idx:match.start()]
                if before_text:
                    rich_text.extend(self.parse_style(before_text))
            
            # Equation content (handle both formats)
            if match.group(1):  # $...$ format
                equation = match.group(1).strip('\n ').replace('\n', ' ')
            else:  # \(...\) format
                equation = match.group(2).strip('\n ').replace('\n', ' ')
            
            if equation:
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

    
    def _parse_table(self, lines: List[str], start_index: int) -> tuple[List[Dict[str, Any]], int]:
        """Parse markdown table and convert to Notion table blocks"""
        table_blocks = []
        i = start_index
        
        # Parse header
        if i >= len(lines):
            return table_blocks, i
        
        header_line = lines[i].strip()
        if not header_line.startswith('|') or not header_line.endswith('|'):
            return table_blocks, i
        
        # Parse header cells
        header_cells = [cell.strip() for cell in header_line.split('|')[1:-1]]
        
        # Skip separator line (| --- | --- |)
        i += 1
        if i < len(lines) and lines[i].strip().startswith('|'):
            i += 1
        
        # Parse data rows
        data_rows = []
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith('|') or not line.endswith('|'):
                break
            
            row_cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(row_cells) == len(header_cells):
                data_rows.append(row_cells)
            i += 1
        
        # Create table block
        if header_cells and data_rows:
            # Per Notion validation, table rows must live under table.children
            table_block = {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": len(header_cells),
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": []
                }
            }
            
            # Add header row
            header_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [[self._create_rich_text(cell)] for cell in header_cells]
                }
            }
            table_block["table"]["children"].append(header_row)
            
            # Add data rows
            for row in data_rows:
                data_row = {
                    "object": "block",
                    "type": "table_row",
                    "table_row": {
                        "cells": [[self._create_rich_text(cell)] for cell in row]
                    }
                }
                table_block["table"]["children"].append(data_row)
            
            table_blocks.append(table_block)
        
        return table_blocks, i
    
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
        
        # Split by block equations first (support both $$...$$ and \[...\] formats)
        equation_pattern = re.compile(r'(\$\$\s*\n.*?\n\s*\$\$|\$\$.*?\$\$|\\\[.*?\\\])', re.DOTALL)
        parts = equation_pattern.split(markdown_content)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if part.startswith('$$'):
                # Block equation ($$...$$ format)
                latex = part[2:-2].strip().replace('\n', '\\')
                blocks.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": latex}
                })
            elif part.startswith('\\[') and part.endswith('\\]'):
                # Block equation (\[...\] format)
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
                    
                    # Check for table
                    if line_strip.startswith('|') and line_strip.endswith('|'):
                        if paragraph_lines:
                            self._append_paragraph_block(blocks, '\n'.join(paragraph_lines))
                            paragraph_lines = []
                        table_blocks, i = self._parse_table(lines, i)
                        blocks.extend(table_blocks)
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
    
    async def _upload_blocks(self, blocks: list, target_id: str, is_page: bool = False):
        """Upload blocks to Notion in batches"""
        if not blocks:
            return
        
        logger.info(f"Uploading {len(blocks)} blocks to Notion")
        
        # Notion API limit: 100 blocks per request
        batch_size = 100
        
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            try:
                await self.notion.blocks.children.append(block_id=target_id, children=batch)
                logger.info(f"Uploaded batch {batch_num} ({len(batch)} blocks)")
            except Exception as e:
                logger.error(f"Failed to upload batch {batch_num}: {str(e)}")
                raise e
    
    async def append_markdown_to_notion(self, markdown_content: str, page_id: str) -> str:
        """Append Markdown content to existing Notion page"""
        logger.info(f"Processing markdown content (length: {len(markdown_content)})")
        
        # Get page URL
        page_info = await self.notion.pages.retrieve(page_id=page_id)
        page_url = page_info['url']
        
        # Convert markdown to blocks
        blocks = self.convert_markdown_to_blocks(markdown_content)
        logger.info(f"Converted {len(blocks)} blocks")
        
        # Upload blocks
        await self._upload_blocks(blocks, page_id)
        logger.info(f"Added {len(blocks)} blocks to existing page")
        
        return page_url
    
    async def upload_markdown_to_notion(self, markdown_content: str, page_id: str, title: str = "Untitled") -> str:
        """Upload Markdown content as new Notion page"""
        logger.info(f"Processing markdown content (length: {len(markdown_content)})")
        
        blocks = self.convert_markdown_to_blocks(markdown_content)
        logger.info(f"Converted {len(blocks)} blocks")
        
        # Create new page
        new_page = await self.notion.pages.create(
            parent={"page_id": page_id},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        )
        
        logger.info(f"Created new page: {new_page['url']}")
        
        # Upload blocks
        await self._upload_blocks(blocks, new_page["id"])
        logger.info(f"Added {len(blocks)} blocks to new page")
        
        return new_page['url']
    
    async def upload_file_to_notion(self, markdown_file: str, page_id: str, title: Optional[str] = None) -> str:
        """Upload Markdown file to Notion"""
        with open(markdown_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        logger.info(f"Reading markdown file: {markdown_file}")
        
        if not title:
            title = Path(markdown_file).stem
        
        return await self.upload_markdown_to_notion(content, page_id, title)


def extract_page_id_from_url(url: str) -> str:
    """Extract page ID from Notion URL"""
    import re
    
    # Pattern for Notion page URLs
    # Examples:
    # https://www.notion.so/z123z123d/Survey-latent-reasoning-22f97b0feb94808fbfa4c07162457633?source=copy_link
    # https://www.notion.so/My-Page-22f97b0feb94808fbfa4c07162457633
    # https://www.notion.so/22f97b0feb94808fbfa4c07162457633
    
    patterns = [
        # Pattern for URLs with workspace and page name
        r'https://www\.notion\.so/[^/]+/[^-]*?([a-f0-9]{32})',
        # Pattern for direct page ID URLs
        r'https://www\.notion\.so/([a-f0-9]{32})',
        # Pattern for URLs with just page ID
        r'([a-f0-9]{32})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's already a page ID
    if re.match(r'^[a-f0-9]{32}$', url):
        return url
    
    raise ValueError(f"Could not extract page ID from URL: {url}")


def get_token_from_env() -> str:
    """Get Notion token from environment variable"""
    token = os.getenv('NOTION_TOKEN')
    if not token:
        raise ValueError("NOTION_TOKEN environment variable not set")
    return token


async def main_async():
    """Main command-line interface (async version)"""
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
        
        # Extract page ID from URL if needed
        try:
            page_id = extract_page_id_from_url(args.page_id)
            if page_id != args.page_id:
                logger.info(f"Extracted page ID: {page_id} from URL")
        except ValueError as e:
            logger.error(f"Invalid page ID or URL: {str(e)}")
            sys.exit(1)
        
        # Validate file
        if not os.path.exists(args.markdown_file):
            logger.error(f"Markdown file not found: {args.markdown_file}")
            sys.exit(1)
        
        # Convert and upload
        converter = MarkdownToNotionConverter(token)
        url = await converter.upload_file_to_notion(args.markdown_file, page_id, args.title)
        
        print(f"\n✅ Successfully uploaded to Notion!")
        print(f"📄 Page URL: {url}")
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


def main():
    """Main command-line interface"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main() 