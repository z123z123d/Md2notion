# md2notion 使用指南

## 快速开始

### 1. 安装

```bash
# 从源码安装
git clone https://github.com/yourusername/md2notion.git
cd md2notion
pip install -e .

# 或者直接安装
pip install git+https://github.com/yourusername/md2notion.git
```

### 2. 获取 Notion API 凭证

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 创建新的集成
3. 复制 "Internal Integration Token"

### 3. 获取页面 ID

1. 打开要添加内容的 Notion 页面
2. 从 URL 中提取 32 位字符的页面 ID
3. 将页面分享给你的集成

### 4. 使用工具

```bash
# 设置环境变量（推荐）
export NOTION_TOKEN="your_token_here"
md2notion document.md --page_id your_page_id

# 或使用命令行参数
md2notion document.md --page_id your_page_id --token your_token_here
```

## 支持的 Markdown 功能

### 标题
```markdown
# 一级标题
## 二级标题
### 三级标题
```

### 文本格式
```markdown
**粗体文本**
*斜体文本*
`代码文本`
```

### 列表
```markdown
* 项目符号列表
1. 数字列表
```

### 数学公式
```markdown
行内公式：$E = mc^2$

块级公式：
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

### 分隔线
```markdown
---
```

## 命令行选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `markdown_file` | Markdown 文件路径 | `document.md` |
| `--page_id` | Notion 页面 ID | `53c2af0bbbcd44b087277f829e7a635d` |
| `--token` | API 令牌 | `secret_abc123...` |
| `--title` | 页面标题 | `"我的文档"` |
| `--verbose` | 详细日志 | `--verbose` |

## 实际使用示例

### 示例 1：上传技术文档
```bash
# 设置令牌
export NOTION_TOKEN="secret_abc123..."

# 上传文档
md2notion technical_doc.md --page_id 53c2af0bbbcd44b087277f829e7a635d --title "技术文档"
```

### 示例 2：上传数学笔记
```bash
md2notion math_notes.md --page_id 53c2af0bbbcd44b087277f829e7a635d --title "数学笔记" --verbose
```

### 示例 3：批量上传
```bash
# 创建脚本
for file in *.md; do
    md2notion "$file" --page_id 53c2af0bbbcd44b087277f829e7a635d
done
```

## 故障排除

### 常见错误

1. **Token 错误**
   ```
   Error: NOTION_TOKEN environment variable not set
   ```
   解决：设置环境变量或使用 `--token` 参数

2. **页面访问权限错误**
   ```
   Error: The page could not be found
   ```
   解决：确保页面已分享给你的集成

3. **文件不存在**
   ```
   Error: Markdown file not found
   ```
   解决：检查文件路径是否正确

### 调试模式

使用 `--verbose` 参数获取详细日志：
```bash
md2notion document.md --page_id your_page_id --verbose
```

## 最佳实践

1. **使用环境变量**：将 API 令牌存储在环境变量中，避免在命令行中暴露
2. **测试小文件**：先用小文件测试，确保配置正确
3. **备份重要内容**：上传前备份重要的 Markdown 文件
4. **检查权限**：确保集成有足够的权限访问目标页面

## 高级用法

### 自定义标题
```bash
md2notion report.md --page_id your_page_id --title "月度报告 - 2024年1月"
```

### 批量处理
```bash
# 上传目录中的所有 Markdown 文件
find . -name "*.md" -exec md2notion {} --page_id your_page_id \;
```

### 集成到工作流
```bash
# 在 CI/CD 中使用
export NOTION_TOKEN="$NOTION_API_TOKEN"
md2notion generated_docs.md --page_id $NOTION_PAGE_ID --title "自动生成的文档"
``` 