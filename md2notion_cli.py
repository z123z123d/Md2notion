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
    
    def parse_inline_equation_and_style(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse inline equations and text styling
        Supports: $...$ equations, *text* italic, `text` code, **text** bold
        """
        rich_text = []
        last_idx = 0
        
        # Handle $...$ inline equations
        for m in re.finditer(r'\$(.+?)\$', text):
            if m.start() > last_idx:
                t = text[last_idx:m.start()]
                rich_text.extend(self.parse_style(t))
            eq = m.group(1)
            rich_text.append({
                "type": "equation",
                "equation": {"expression": eq}
            })
            last_idx = m.end()
        
        if last_idx < len(text):
            t = text[last_idx:]
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
    
    def convert_markdown_to_blocks(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Convert Markdown content to Notion blocks
        Supports: headings, equations, lists, paragraphs, dividers
        """
        blocks = []
        lines = markdown_content.split('\n')
        paragraph_lines = []
        
        def flush_paragraph():
            if paragraph_lines:
                paragraph = ' '.join(paragraph_lines).strip()
                if paragraph:
                    # Split long paragraphs to fit within Notion's rich_text length limit
                    text_chunks = self.split_text_for_rich_text(paragraph)
                    for chunk in text_chunks:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": self.parse_inline_equation_and_style(chunk)
                            }
                        })
                paragraph_lines.clear()
        
        i = 0
        n = len(lines)
        
        while i < n:
            line = lines[i].rstrip()
            
            # Divider ---
            if re.match(r'^\s*-{3,}\s*$', line):
                flush_paragraph()
                blocks.append({"object": "block", "type": "divider", "divider": {}})
                i += 1
                continue
            
            # Numbered list 1. 2. ...
            if re.match(r'^\s*\d+\. ', line):
                flush_paragraph()
                item_text = re.sub(r'^\s*\d+\. ', '', line).strip()
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": self.parse_inline_equation_and_style(item_text)
                    }
                })
                i += 1
                continue
            
            # Bullet list *
            if line.strip().startswith('* '):
                flush_paragraph()
                item_text = line.strip()[2:].strip()
                # Split long list items to fit within Notion's rich_text length limit
                text_chunks = self.split_text_for_rich_text(item_text)
                for chunk in text_chunks:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": self.parse_inline_equation_and_style(chunk)
                        }
                    })
                i += 1
                continue
            
            # Block equation $$...$$ single line
            if line.strip().startswith('$$') and line.strip().endswith('$$') and len(line.strip()) > 4:
                flush_paragraph()
                latex = line.strip()[2:-2].strip()
                blocks.append({
                    "object": "block",
                    "type": "equation",
                    "equation": {"expression": latex}
                })
                i += 1
                continue
            
            # Multi-line block equation
            if line.strip().startswith('$$'):
                flush_paragraph()
                equation_lines = [line.strip()[2:]]
                i += 1
                while i < n and not lines[i].strip().endswith('$$'):
                    equation_lines.append(lines[i])
                    i += 1
                if i < n:
                    equation_lines.append(lines[i].strip()[:-2])
                    latex = '\n'.join(equation_lines)
                    blocks.append({
                        "object": "block",
                        "type": "equation",
                        "equation": {"expression": latex}
                    })
                i += 1
                continue
            
            # Headings
            if line.startswith('#'):
                flush_paragraph()
                level = len(line) - len(line.lstrip('#'))
                title = self.clean_title(line.lstrip('#').strip())
                
                # Split long headings to fit within Notion's rich_text length limit
                text_chunks = self.split_text_for_rich_text(title)
                for chunk in text_chunks:
                    if level == 1:
                        blocks.append({
                            "object": "block",
                            "type": "heading_1",
                            "heading_1": {
                                "rich_text": self.parse_inline_equation_and_style(chunk)
                            }
                        })
                    elif level == 2:
                        blocks.append({
                            "object": "block",
                            "type": "heading_2",
                            "heading_2": {
                                "rich_text": self.parse_inline_equation_and_style(chunk)
                            }
                        })
                    elif level == 3:
                        blocks.append({
                            "object": "block",
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": self.parse_inline_equation_and_style(chunk)
                            }
                        })
                i += 1
                continue
            
            # Empty line - flush paragraph
            if not line.strip():
                flush_paragraph()
                i += 1
                continue
            
            # Regular paragraph line
            paragraph_lines.append(line)
            i += 1
        
        # Flush remaining paragraph
        flush_paragraph()
        return blocks
    
    def upload_to_notion(self, markdown_file: str, page_id: str, title: str | None = None) -> str:
        """
        Upload Markdown content to Notion page
        
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
            
            # Convert to Notion blocks
            blocks = self.convert_markdown_to_blocks(content)
            logger.info(f"Converted {len(blocks)} blocks")
            
            # Use filename as title if not provided
            if not title:
                title = Path(markdown_file).stem
            
            # Create new page
            new_page = self.notion.pages.create(
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
            
            logger.info(f"Created new page: {new_page['url']}")
            
            # Add content blocks
            if blocks:
                # Notion API 限制每次最多 100 blocks
                for i in range(0, len(blocks), 100):
                    batch = blocks[i:i+100]
                    self.notion.blocks.children.append(
                        block_id=new_page["id"],
                        children=batch
                    )
                logger.info(f"Added {len(blocks)} content blocks")
            
            return new_page['url']
            
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