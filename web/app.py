#!/usr/bin/env python3
"""
md2notion Web Application

A simple web interface for converting Markdown files to Notion pages.
"""

import os
import tempfile
import asyncio
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
        page_id_input = request.form.get('page_id', '').strip()
        title = request.form.get('title', '').strip()
        markdown_text = request.form.get('markdown_text', '').strip()
        
        # Validate required fields
        if not notion_token:
            return jsonify({'error': 'Notion token is required'}), 400
        if not page_id_input:
            return jsonify({'error': 'Page ID is required'}), 400
        
        # Extract page ID from URL if needed
        try:
            from md2notion_cli import extract_page_id_from_url
            page_id = extract_page_id_from_url(page_id_input)
            if page_id != page_id_input:
                print(f"Extracted page ID: {page_id} from URL")
        except ValueError as e:
            return jsonify({'error': f'Invalid page ID or URL: {str(e)}'}), 400
        
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
                
                # Upload to Notion (async)
                print(f"🔍 DEBUG: Starting Notion upload process")
                print(f"🔍 DEBUG: File path: {temp_path}")
                print(f"🔍 DEBUG: Page ID: {page_id}")
                print(f"🔍 DEBUG: Page title: {page_title}")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    print(f"🔍 DEBUG: Creating async event loop")
                    page_url = loop.run_until_complete(
                        converter.upload_file_to_notion(temp_path, page_id, page_title)
                    )
                    print(f"🔍 DEBUG: Successfully got page URL: {page_url}")
                except Exception as async_error:
                    print(f"❌ DEBUG: Async operation failed: {str(async_error)}")
                    print(f"❌ DEBUG: Error type: {type(async_error).__name__}")
                    import traceback
                    print(f"❌ DEBUG: Full traceback:")
                    traceback.print_exc()
                    raise async_error
                finally:
                    print(f"🔍 DEBUG: Closing event loop")
                    loop.close()
                
                # Clean up temporary file
                os.remove(temp_path)
                
                return jsonify({
                    'success': True,
                    'message': 'File successfully uploaded to Notion!',
                    'page_url': page_url,
                    'title': page_title
                })
                
            except Exception as e:
                print(f"❌ DEBUG: File upload error: {str(e)}")
                print(f"❌ DEBUG: Error type: {type(e).__name__}")
                import traceback
                print(f"❌ DEBUG: Full traceback for file upload:")
                traceback.print_exc()
                
                # Clean up temporary file on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    print(f"🔍 DEBUG: Cleaned up temporary file: {temp_path}")
                
                return jsonify({'error': f'Error uploading to Notion: {str(e)}'}), 500
                
        elif markdown_text:
            # Text input mode - append to existing page
            try:
                # Convert and append to Notion
                converter = MarkdownToNotionConverter(notion_token)
                
                # Append content to existing page (async)
                print(f"🔍 DEBUG: Starting Notion append process")
                print(f"🔍 DEBUG: Page ID: {page_id}")
                print(f"🔍 DEBUG: Content length: {len(markdown_text)} characters")
                print(f"🔍 DEBUG: Content preview: {markdown_text[:200]}...")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    print(f"🔍 DEBUG: Creating async event loop for append")
                    page_url = loop.run_until_complete(
                        converter.append_markdown_to_notion(markdown_text, page_id)
                    )
                    print(f"🔍 DEBUG: Successfully appended content, page URL: {page_url}")
                except Exception as async_error:
                    print(f"❌ DEBUG: Async append operation failed: {str(async_error)}")
                    print(f"❌ DEBUG: Error type: {type(async_error).__name__}")
                    import traceback
                    print(f"❌ DEBUG: Full traceback for append:")
                    traceback.print_exc()
                    raise async_error
                finally:
                    print(f"🔍 DEBUG: Closing event loop for append")
                    loop.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Markdown text successfully appended to Notion page!',
                    'page_url': page_url,
                    'title': 'Content appended'
                })
                
            except Exception as e:
                print(f"❌ DEBUG: Text append error: {str(e)}")
                print(f"❌ DEBUG: Error type: {type(e).__name__}")
                import traceback
                print(f"❌ DEBUG: Full traceback for text append:")
                traceback.print_exc()
                return jsonify({'error': f'Error appending to Notion: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Please provide either a file or markdown text'}), 400
            
    except Exception as e:
        print(f"❌ DEBUG: Unexpected error in upload_file: {str(e)}")
        print(f"❌ DEBUG: Error type: {type(e).__name__}")
        import traceback
        print(f"❌ DEBUG: Full traceback for unexpected error:")
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run in debug mode if FLASK_ENV is set to development
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting md2notion web server on port {port}")
    print("Open your browser and go to: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 