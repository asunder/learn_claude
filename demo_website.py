#!/usr/bin/env python3
"""
Demo script to showcase the Hypervisor Agent MVP website
"""

import webbrowser
import time
import threading
from simple_app import app

def open_browser():
    """Open the browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def main():
    """Run the demo website"""
    print("=" * 60)
    print("🚀 HYPERVISOR AGENT MVP WEBSITE DEMO")
    print("=" * 60)
    print()
    print("Starting the Hypervisor Agent learning platform...")
    print("📍 Website will be available at: http://localhost:5000")
    print()
    print("Features included:")
    print("✅ Interactive agent query interface")
    print("✅ Terraform code generation")
    print("✅ SDK examples for AWS, Azure, GCP")
    print("✅ Cloud provider specific pages")
    print("✅ Best practices guidance")
    print("✅ Hypervisor management info")
    print("✅ Responsive design with Bootstrap")
    print()
    print("Use Cases Covered:")
    print("• Web Applications")
    print("• API Backends") 
    print("• Data Processing")
    print("• Machine Learning")
    print("• Container Workloads")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thanks for trying the Hypervisor Agent!")

if __name__ == '__main__':
    main()