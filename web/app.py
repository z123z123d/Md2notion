#!/usr/bin/env python3
"""
md2notion Web Application

A simple web interface for converting Markdown files to Notion pages.
"""

import os
import tempfile
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from md2notion_cli import MarkdownToNotionConverter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'md', 'markdown', 'txt'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and conversion"""
    try:
        # Get form data
        notion_token = request.form.get('notion_token', '').strip()
        page_id = request.form.get('page_id', '').strip()
        title = request.form.get('title', '').strip()
        markdown_text = request.form.get('markdown_text', '').strip()
        
        # Validate required fields
        if not notion_token:
            return jsonify({'error': 'Notion token is required'}), 400
        if not page_id:
            return jsonify({'error': 'Page ID is required'}), 400
        
        # Check if file was uploaded or text was provided
        if 'file' in request.files and request.files['file'].filename != '':
            # File upload mode
            file = request.files['file']
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Please upload .md, .markdown, or .txt files'}), 400
            
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(temp_path)
            
            try:
                # Convert and upload to Notion
                converter = MarkdownToNotionConverter(notion_token)
                
                # Use custom title if provided, otherwise use filename
                page_title = title if title else os.path.splitext(filename)[0]
                
                # Upload to Notion
                page_url = converter.upload_to_notion(temp_path, page_id, page_title)
                
                # Clean up temporary file
                os.remove(temp_path)
                
                return jsonify({
                    'success': True,
                    'message': 'File successfully uploaded to Notion!',
                    'page_url': page_url,
                    'title': page_title
                })
                
            except Exception as e:
                # Clean up temporary file on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({'error': f'Error uploading to Notion: {str(e)}'}), 500
                
        elif markdown_text:
            # Text input mode - save to temporary file first (like file upload)
            try:
                # Save text to temporary file (same as file upload)
                filename = "text_input.md"
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                
                # Write text to file with UTF-8 encoding
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_text)
                
                try:
                    # Convert and upload to Notion (use same path as file upload)
                    converter = MarkdownToNotionConverter(notion_token)
                    
                    # Use custom title if provided, otherwise use default
                    page_title = title if title else "Untitled"
                    
                    # Upload to Notion using the same method as file upload
                    page_url = converter.upload_to_notion(temp_path, page_id, page_title)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Markdown text successfully uploaded to Notion!',
                        'page_url': page_url,
                        'title': page_title
                    })
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
            except Exception as e:
                return jsonify({'error': f'Error uploading to Notion: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Please provide either a file or markdown text'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'md2notion-web'})

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run in debug mode if FLASK_ENV is set to development
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting md2notion web server on port {port}")
    print("Open your browser and go to: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 