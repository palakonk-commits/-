"""
Network Impairment Tool - Main Application
Windows network lag/drop/throttle/tamper tool with web UI and system tray
รอบรับการควบคุมผ่านเว็บเบราว์เซอร์และมี system tray icon
"""

import os
import sys
import json
import logging
import threading
import subprocess
import tempfile
import time
import ctypes
from pathlib import Path
from functools import wraps

# Import Flask สำหรับ HTTP server
from flask import Flask, render_template, request, jsonify
import webview

# Import pystray สำหรับ system tray
try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    logging.warning("pystray/PIL not installed - tray feature disabled")

# Import network module
from network import engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Flask Application
# ============================================================================

app = Flask(__name__, template_folder='templates', static_folder='static')

# CORS-like support สำหรับ local requests
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/')
def index():
    """Main UI page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """ได้ config ปัจจุบัน"""
    try:
        config = engine.get_config()
        return jsonify(config), 200
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def set_config():
    """อัพเดต config"""
    try:
        data = request.get_json()
        engine.update_config(data)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Error setting config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/start', methods=['POST'])
def start():
    """เริ่ม network impairment"""
    try:
        config_data = request.get_json() or {}
        if config_data:
            engine.update_config(config_data)
        
        success = engine.start()
        if success:
            return jsonify({'status': 'running'}), 200
        else:
            return jsonify({'error': 'Failed to start engine'}), 500
    except Exception as e:
        logger.error(f"Error starting: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop():
    """หยุด network impairment"""
    try:
        engine.stop()
        return jsonify({'status': 'stopped'}), 200
    except Exception as e:
        logger.error(f"Error stopping: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """ได้ statistics"""
    try:
        stats = engine.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset-stats', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    try:
        engine.packet_queue.reset_stats()
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Error resetting stats: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Admin Check (Elevated Privileges)
# ============================================================================

def is_admin():
    """ตรวจสอบว่า run เป็น Administrator"""
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except:
        return False


def warn_not_admin():
    """เตือนผู้ใช้ว่าต้อง run as admin"""
    logger.warning("!" * 50)
    logger.warning("WARNING: This application requires Administrator privileges!")
    logger.warning("WinDivert requires admin rights to capture packets.")
    logger.warning("Please run as Administrator for proper functionality.")
    logger.warning("!" * 50)


# ============================================================================
# System Tray Icon
# ============================================================================

class TrayIconManager:
    """จัดการ system tray icon"""
    
    def __init__(self, app_window):
        self.app_window = app_window
        self.icon = None
    
    def create_image(self):
        """สร้าง icon image (simple colored square)"""
        try:
            # Create a simple icon: colored square with "NI" text
            size = 64
            image = Image.new('RGB', (size, size), color=(40, 40, 40))
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle(
                [(2, 2), (size-2, size-2)],
                outline=(100, 150, 200),
                width=2
            )
            
            # Draw text "NI" (Network Impairment)
            text = "NI"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2
            draw.text((text_x, text_y), text, fill=(100, 150, 200))
            
            return image
        except Exception as e:
            logger.error(f"Error creating icon: {e}")
            return None
    
    def create_menu(self):
        """สร้าง context menu"""
        menu = Menu(
            MenuItem('Show Control Window', self.show_window),
            MenuItem('Exit & Delete', self.exit_app),
        )
        return menu
    
    def show_window(self, icon=None, item=None):
        """แสดง window"""
        if self.app_window:
            self.app_window.show()
    
    def exit_app(self, icon=None, item=None):
        """ออกจากแอปพลิเคชัน"""
        logger.info("Exit & Delete requested from tray menu")
        self.perform_self_destruct()
    
    def perform_self_destruct(self):
        """Self-destruct logic"""
        logger.info("Performing self-destruct...")
        
        # Stop engine
        engine.stop()
        
        # Close window
        if self.app_window:
            try:
                self.app_window.destroy()
            except:
                pass
        
        # Create delete batch file
        try:
            self._create_delete_batch()
        except Exception as e:
            logger.error(f"Error creating delete batch: {e}")
    
    def _create_delete_batch(self):
        """สร้าง batch file ที่ลบตัวเอง"""
        try:
            # ได้ path ของ script/exe ปัจจุบัน
            if getattr(sys, 'frozen', False):
                # PyInstaller exe
                target_path = sys.executable
            else:
                # Script file
                target_path = os.path.abspath(__file__)
            
            # สร้าง batch file ใน TEMP
            temp_dir = tempfile.gettempdir()
            batch_file = os.path.join(temp_dir, f'delete_{int(time.time())}.bat')
            
            # Write batch script
            with open(batch_file, 'w') as f:
                f.write('@echo off\n')
                f.write('REM Self-delete batch file\n')
                f.write('timeout /t 2 /nobreak\n')
                f.write(f'del /f /q "{target_path}"\n')
                f.write(f'del /f /q "{batch_file}"\n')
            
            # Execute batch in detached process
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(
                batch_file,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            logger.info(f"Delete batch created: {batch_file}")
            
            # Exit app
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Self-destruct error: {e}")


# ============================================================================
# Main Application Class
# ============================================================================

class NetworkImpairmentApp:
    """Main application class"""
    
    def __init__(self):
        self.api = None
        self.webview = None
        self.tray_manager = None
        self.flask_thread = None
        self.flask_port = 5000
    
    def start_flask(self):
        """Start Flask server ใน background thread"""
        logger.info(f"Starting Flask on port {self.flask_port}")
        
        def run_flask():
            try:
                app.run(
                    host='127.0.0.1',
                    port=self.flask_port,
                    debug=False,
                    use_reloader=False,
                    threaded=True,
                )
            except Exception as e:
                logger.error(f"Flask error: {e}")
        
        self.flask_thread = threading.Thread(
            target=run_flask,
            daemon=True,
            name="FlaskServer"
        )
        self.flask_thread.start()
        
        # Wait for Flask to start
        time.sleep(1)
    
    def setup_webview(self):
        """Setup pywebview"""
        logger.info("Setting up webview")
        
        url = f'http://127.0.0.1:{self.flask_port}/'
        
        try:
            self.api = webview.api.WebView()
            self.webview = webview.create_window(
                'Network Impairment Tool',
                url,
                background_color='#282c34',
                min_size=(1000, 700),
            )
            
            return self.webview
        except Exception as e:
            logger.error(f"Webview setup error: {e}")
            return None
    
    def setup_tray(self):
        """Setup system tray icon"""
        if not HAS_TRAY:
            logger.warning("Tray support not available")
            return
        
        logger.info("Setting up system tray")
        
        try:
            self.tray_manager = TrayIconManager(self.webview)
            icon_image = self.tray_manager.create_image()
            
            if icon_image:
                self.tray_manager.icon = Icon(
                    "NetworkImpairment",
                    icon_image,
                    menu=self.tray_manager.create_menu(),
                )
                logger.info("Tray icon created")
        except Exception as e:
            logger.error(f"Tray setup error: {e}")
    
    def run(self):
        """Main entry point"""
        logger.info("=" * 60)
        logger.info("Network Impairment Tool v1.0")
        logger.info("=" * 60)
        
        # Check admin
        if not is_admin():
            warn_not_admin()
        
        try:
            # Start Flask
            self.start_flask()
            
            # Setup webview
            webview_window = self.setup_webview()
            if not webview_window:
                logger.error("Failed to create webview")
                return
            
            # Setup tray
            self.setup_tray()
            
            # Run webview (blocking)
            logger.info("Starting webview...")
            webview.start()
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            # Cleanup
            logger.info("Cleaning up...")
            engine.stop()
            
            if self.tray_manager and self.tray_manager.icon:
                try:
                    self.tray_manager.icon.stop()
                except:
                    pass


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    app_instance = NetworkImpairmentApp()
    app_instance.run()
