#!/usr/bin/env python3
"""
md2notion Web Server Starter

A simple script to start the md2notion web application.
"""

import os
import sys
import webbrowser
import time
from web.app import app

def main():
    """Start the web server and open browser"""
    print("🚀 Starting md2notion Web Server...")
    print("=" * 50)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Check if port is available
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} is already in use!")
            print(f"   Please stop the existing service or use a different port:")
            print(f"   export PORT=5001 && python start_web.py")
            sys.exit(1)
    except:
        pass
    
    print(f"📡 Server will start on: http://localhost:{port}")
    print("🌐 Opening browser automatically...")
    print("=" * 50)
    
    # Start server in background thread
    import threading
    
    def start_server():
        app.run(host='0.0.0.0', port=port, debug=False)
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open browser
    try:
        webbrowser.open(f'http://localhost:{port}')
        print("✅ Browser opened successfully!")
    except:
        print("⚠️  Could not open browser automatically.")
        print(f"   Please manually open: http://localhost:{port}")
    
    print("\n🎉 md2notion Web Server is running!")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down md2notion Web Server...")
        sys.exit(0)

if __name__ == "__main__":
    main() 