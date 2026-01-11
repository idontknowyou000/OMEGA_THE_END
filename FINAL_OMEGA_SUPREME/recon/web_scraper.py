#!/usr/bin/env python3
"""
OMEGA_X WEB SCRAPER
====================

Advanced web scraping component that collects data from websites
and sends it as network packets through OMEGA_X network services.

FEATURES:
- Browser-based scraping with Selenium
- Data extraction and processing
- Packet generation from scraped content
- Integration with TCP/UDP network services
- Performance optimized for laptop hardware
- Multi-threaded scraping for efficiency

USAGE:
    python3 web_scraper.py --url https://example.com --target tcp --count 100
"""

import os
import sys
import time
import threading
import socket
import json
import random
import hashlib
from datetime import datetime
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# OMEGA_X imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omega_launcher import Colors

class WebScraper:
    """Web scraper that sends scraped data as network packets"""

    def __init__(self, target_host='127.0.0.1', target_port=4444, protocol='tcp'):
        self.target_host = target_host
        self.target_port = target_port
        self.protocol = protocol.lower()
        self.driver = None
        self.running = False
        self.stats = {
            'pages_scraped': 0,
            'data_sent': 0,
            'packets_sent': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

        # Scraping configuration
        self.config = {
            'max_pages': 100,
            'delay_between_requests': 1,
            'max_threads': 4,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ],
            'browser': 'chrome',  # chrome or firefox
            'headless': True,
            'timeout': 10
        }

        # Thread pool for concurrent scraping
        self.threads = []
        self.url_queue = []
        self.data_queue = []

    def log(self, message, level="info"):
        """Log messages with timestamps"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        colors = {
            'info': Colors.BLUE,
            'success': Colors.GREEN,
            'warning': Colors.YELLOW,
            'error': Colors.RED,
            'critical': Colors.RED + Colors.BOLD
        }

        color = colors.get(level, Colors.WHITE)
        print(f"{color}[{timestamp}] SCRAPER: {message}{Colors.ENDC}")

    def setup_browser(self):
        """Setup Selenium WebDriver"""
        self.log("🔧 Setting up web browser...")

        try:
            if self.config['browser'] == 'chrome':
                options = Options()
                if self.config['headless']:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument(f'--user-agent={random.choice(self.config["user_agents"])}')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-plugins')
                options.add_argument('--disable-images')  # Speed up loading

                self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

            elif self.config['browser'] == 'firefox':
                from selenium.webdriver.firefox.options import Options
                options = Options()
                if self.config['headless']:
                    options.add_argument('--headless')
                options.set_preference("general.useragent.override", random.choice(self.config["user_agents"]))

                self.driver = webdriver.Firefox(GeckoDriverManager().install(), options=options)

            self.driver.set_page_load_timeout(self.config['timeout'])
            self.log("✅ Browser setup complete")

        except Exception as e:
            self.log(f"❌ Failed to setup browser: {e}", "error")
            raise

    def scrape_url(self, url):
        """Scrape a single URL"""
        try:
            self.log(f"🌐 Scraping: {url}")

            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, self.config['timeout']).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Extract page content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract various data types
            data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'title': soup.title.string if soup.title else '',
                'text_content': soup.get_text(),
                'links': [link.get('href') for link in soup.find_all('a', href=True)],
                'images': [img.get('src') for img in soup.find_all('img', src=True)],
                'meta_tags': {meta.get('name', meta.get('property', '')): meta.get('content', '')
                             for meta in soup.find_all('meta') if meta.get('name') or meta.get('property')},
                'headers': dict(self.driver.execute_script("return navigator.userAgent;")),
                'page_hash': hashlib.md5(page_source.encode()).hexdigest()
            }

            self.stats['pages_scraped'] += 1
            self.log(f"✅ Scraped {len(data['text_content'])} characters from {url}")

            return data

        except TimeoutException:
            self.log(f"⏰ Timeout scraping {url}", "warning")
            self.stats['errors'] += 1
        except WebDriverException as e:
            self.log(f"🌐 WebDriver error scraping {url}: {e}", "error")
            self.stats['errors'] += 1
        except Exception as e:
            self.log(f"❌ Error scraping {url}: {e}", "error")
            self.stats['errors'] += 1

        return None

    def send_data_packet(self, data):
        """Send scraped data as network packet"""
        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            packet_size = len(json_data.encode('utf-8'))

            if self.protocol == 'tcp':
                self.send_tcp_packet(json_data)
            elif self.protocol == 'udp':
                self.send_udp_packet(json_data)
            else:
                self.log(f"❌ Unknown protocol: {self.protocol}", "error")
                return

            self.stats['data_sent'] += packet_size
            self.stats['packets_sent'] += 1

            self.log(f"📤 Sent {packet_size} bytes via {self.protocol.upper()}")

        except Exception as e:
            self.log(f"❌ Failed to send packet: {e}", "error")
            self.stats['errors'] += 1

    def send_tcp_packet(self, data):
        """Send data via TCP connection"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.target_host, self.target_port))
            sock.sendall(data.encode('utf-8'))
        finally:
            sock.close()

    def send_udp_packet(self, data):
        """Send data via UDP packet"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Split large data into smaller UDP packets (max ~65KB)
            chunk_size = 60000  # Leave room for headers
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                sock.sendto(chunk.encode('utf-8'), (self.target_host, self.target_port))
        finally:
            sock.close()

    def worker_thread(self):
        """Worker thread for scraping and sending"""
        while self.running:
            try:
                # Get URL from queue
                if not self.url_queue:
                    time.sleep(0.1)
                    continue

                url = self.url_queue.pop(0)

                # Scrape the URL
                data = self.scrape_url(url)
                if data:
                    # Send the data
                    self.send_data_packet(data)

                    # Add new URLs to queue (crawling)
                    if len(self.url_queue) < self.config['max_pages']:
                        for link in data['links'][:5]:  # Limit to 5 links per page
                            if link and link.startswith('http'):
                                if link not in [u for u in self.url_queue]:
                                    self.url_queue.append(link)

                # Delay between requests
                time.sleep(self.config['delay_between_requests'])

            except Exception as e:
                self.log(f"❌ Worker thread error: {e}", "error")
                time.sleep(1)

    def start_scraping(self, start_urls, max_pages=100):
        """Start the scraping process"""
        self.config['max_pages'] = max_pages
        self.url_queue = start_urls.copy()
        self.running = True

        self.log("🚀 Starting web scraper...")
        self.log(f"🎯 Target: {self.target_host}:{self.target_port} via {self.protocol.upper()}")
        self.log(f"📄 Max pages: {max_pages}")

        # Setup browser
        self.setup_browser()

        # Start worker threads
        for i in range(min(self.config['max_threads'], len(start_urls))):
            thread = threading.Thread(target=self.worker_thread, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.log(f"🧵 Started worker thread {i+1}")

        # Monitor progress
        self.monitor_progress()

    def monitor_progress(self):
        """Monitor scraping progress"""
        while self.running and (self.stats['pages_scraped'] < self.config['max_pages']):
            time.sleep(5)
            self.show_stats()

            # Check if we have URLs to process
            if not self.url_queue and self.stats['pages_scraped'] > 0:
                self.log("📭 No more URLs in queue, finishing...")
                break

    def show_stats(self):
        """Show scraping statistics"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.CYAN}║{Colors.ENDC}                   {Colors.RED}🌐 WEB SCRAPER STATS 🌐{Colors.ENDC}                     {Colors.CYAN}║{Colors.ENDC}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")

        print(f"{Colors.BLUE}📊 Statistics:{Colors.ENDC}")
        print(f"  Pages Scraped: {self.stats['pages_scraped']}")
        print(f"  Data Sent: {self.stats['data_sent']:,} bytes")
        print(f"  Packets Sent: {self.stats['packets_sent']}")
        print(f"  Errors: {self.stats['errors']}")
        print(f"  Uptime: {uptime:.0f} seconds")
        print(f"  URLs in Queue: {len(self.url_queue)}")
        print(f"  Active Threads: {len([t for t in self.threads if t.is_alive()])}")

    def stop_scraping(self):
        """Stop the scraping process"""
        self.log("🛑 Stopping web scraper...")
        self.running = False

        # Close browser
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)

        self.log("✅ Web scraper stopped")
        self.show_stats()

def main():
    """Main function for standalone usage"""
    import argparse

    parser = argparse.ArgumentParser(description="OMEGA_X Web Scraper")
    parser.add_argument('--url', required=True, help='Starting URL to scrape')
    parser.add_argument('--target-host', default='127.0.0.1', help='Target host for packets')
    parser.add_argument('--target-port', type=int, default=4444, help='Target port for packets')
    parser.add_argument('--protocol', choices=['tcp', 'udp'], default='tcp', help='Protocol to use')
    parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to scrape')
    parser.add_argument('--browser', choices=['chrome', 'firefox'], default='chrome', help='Browser to use')

    args = parser.parse_args()

    scraper = WebScraper(args.target_host, args.target_port, args.protocol)
    scraper.config['browser'] = args.browser

    try:
        scraper.start_scraping([args.url], args.max_pages)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Scraper interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Scraper error: {e}{Colors.ENDC}")
    finally:
        scraper.stop_scraping()

if __name__ == "__main__":
    main()