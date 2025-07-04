# md2notion

A simple and powerful command-line tool to convert Markdown files to Notion pages.

## ✨ Features

- **Easy to use**: Simple command-line interface
- **Rich formatting**: Supports headings, lists, code blocks, equations, and inline styles
- **Secure**: Handles API tokens securely via environment variables
- **Flexible**: Custom page titles and verbose logging options
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

#### Option 1: Install from source
```bash
git clone https://github.com/yourusername/md2notion.git
cd md2notion
pip install -e .
```

#### Option 2: Install directly
```bash
pip install git+https://github.com/yourusername/md2notion.git
```

### Setup

1. **Get your Notion API Token:**
   - Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Create a new integration and copy the "Internal Integration Token"

2. **Get your Notion Page ID:**
   - Open the Notion page where you want to add content
   - The Page ID is the 32-character string at the end of the URL
   - Example: `https://www.notion.so/My-Page-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
   - Page ID: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
   - **Important:** Share the page with your integration for access

### Usage

#### Basic usage with environment variable (recommended)
```bash
export NOTION_TOKEN="your_notion_token_here"
md2notion document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

#### Using command-line token
```bash
md2notion document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --token your_token_here
```

#### With custom title
```bash
md2notion document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --title "My Custom Title"
```

#### Verbose logging
```bash
md2notion document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --verbose
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
usage: md2notion [-h] [--page_id PAGE_ID] [--token TOKEN] [--title TITLE] [--verbose] markdown_file

Convert Markdown files to Notion pages

positional arguments:
  markdown_file         Path to the markdown file to convert

optional arguments:
  -h, --help           show this help message and exit
  --page_id PAGE_ID    Notion page ID where to create the new page
  --token TOKEN        Notion API token (or set NOTION_TOKEN environment variable)
  --title TITLE        Title for the new Notion page (defaults to filename)
  --verbose, -v        Enable verbose logging
```

## 🔧 Examples

### Example 1: Basic document upload
```bash
# Set your token
export NOTION_TOKEN="secret_abc123..."

# Upload a document
md2notion my_document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Example 2: Upload with custom title
```bash
md2notion report.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --title "Monthly Report"
```

### Example 3: Debug mode
```bash
md2notion document.md --page_id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --verbose
```

## 📁 Project Structure

```
md2notion/
├── md2notion.py      # Main command-line tool
├── setup.py          # Package setup script
├── requirements.txt  # Python dependencies
├── README.md         # This file
├── LICENSE           # MIT License
├── .gitignore        # Git ignore rules
├── build.py          # Build script
├── USAGE.md          # Detailed usage guide
├── PROJECT_SUMMARY.md # Project overview
└── examples/         # Example markdown files
    └── sample.md
```

## 🛠️ Development

### Prerequisites
- Python 3.7+
- pip

### Setup development environment
```bash
git clone https://github.com/yourusername/md2notion.git
cd md2notion
pip install -e .
```

### Running tests
```bash
python -m pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Notion API](https://developers.notion.com/) for providing the integration platform
- [notion-client](https://github.com/ramnes/notion-sdk-py) for the Python SDK

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/md2notion/issues) page
2. Create a new issue with detailed information
3. Include your markdown file and error messages

---

Made with ❤️ for the Notion community
