# md2notion

A simple and powerful tool to convert Markdown files to Notion pages.

## ✨ Features

- **Command Line Tool**: Simple CLI for batch processing
- **Web Interface**: Beautiful web UI for easy file upload
- **Rich Formatting**: Supports headings, lists, code blocks, equations
- **Secure**: Handles API tokens securely
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

1. **Get Notion API Token:**
   - Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Create a new integration and copy the "Internal Integration Token"

2. **Get Notion Page ID:**
   - Open the Notion page where you want to add content
   - Copy the 32-character string at the end of the URL
   - Example: `https://www.notion.so/My-Page-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
   - Page ID: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
   - **Important:** Share the page with your integration

### Installation

```bash
git clone https://github.com/yourusername/md2notion.git
cd md2notion
pip install -r requirements.txt
```

### Option 1: Web Interface (Recommended)

```bash
python start_web.py
```

Then open http://localhost:5000 in your browser.

**Features:**
- Drag & drop file upload
- Real-time conversion feedback
- Secure file processing
- Responsive design

### Option 2: Command Line

```bash
# Set environment variable (recommended)
export NOTION_TOKEN="your_notion_token_here"

# Basic usage
python md2notion_cli.py document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# With custom title
python md2notion_cli.py document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --title "My Title"

# Verbose logging
python md2notion_cli.py document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --verbose
```

## 📝 Supported Markdown Features

| Feature | Markdown | Notion Result |
|---------|----------|---------------|
| Headings | `# H1`, `## H2`, `### H3` | Heading blocks |
| Bold text | `**bold**` or `__bold__` | Bold text |
| Italic text | `*italic*` or `_italic_` | Italic text |
| Code | `` `code` `` | Inline code |
| Bullet lists | `* item` | Bullet list items |
| Numbered lists | `1. item` | Numbered list items |
| Block equations | `$$equation$$` | Equation blocks |
| Inline equations | `$equation$` | Inline equations |
| Dividers | `---` | Divider blocks |
| Paragraphs | Regular text | Paragraph blocks |

## 📋 Command Line Options

```
usage: md2notion_cli.py [-h] [--page_id PAGE_ID] [--token TOKEN] [--title TITLE] [--verbose] markdown_file

positional arguments:
  markdown_file         Path to the markdown file to convert

optional arguments:
  -h, --help           show this help message and exit
  --page_id PAGE_ID    Notion page ID where to create the new page
  --token TOKEN        Notion API token (or set NOTION_TOKEN environment variable)
  --title TITLE        Title for the new Notion page (defaults to filename)
  --verbose, -v        Enable verbose logging
```

## 📁 Project Structure

```
md2notion/
├── md2notion_cli.py      # Main command-line tool
├── start_web.py          # Web server starter
├── web/                  # Web application files
│   ├── app.py           # Flask web app
│   └── templates/       # HTML templates
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
├── build.py             # Build script
└── README.md            # This file
```

## 🛠️ Development

### Setup
```bash
pip install -e .
```

### Build
```bash
python build.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

Made with ❤️ for the Notion community
