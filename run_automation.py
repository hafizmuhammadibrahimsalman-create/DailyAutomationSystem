#!/usr/bin/env python3
"""
DailyNewsBot - Master Automation Controller
============================================
Production-ready script with comprehensive error handling,
logging, and system monitoring.

Author: Muhammad Ibrahim Salman
Last Enhanced: January 19, 2026
"""

import sys
import os
import time
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Force UTF-8 for Windows with safe encoding
try:
    from console_utils import setup_console, sanitize_text
    setup_console()
except ImportError:
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    sanitize_text = lambda x: x

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# CONFIGURATION
# =============================================================================

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"automation_{datetime.now().strftime('%Y%m%d')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutomationMaster")

# =============================================================================
# SYSTEM CHECKS
# =============================================================================

def check_python_version() -> bool:
    """Ensure Python 3.8+"""
    if sys.version_info < (3, 8):
        logger.error(f"Python 3.8+ required. Found: {sys.version}")
        return False
    logger.info(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_dependencies() -> Dict[str, bool]:
    """Check all required packages are installed."""
    required = [
        'dotenv', 'requests', 'feedparser', 'google.generativeai',
        'pywhatkit', 'PIL', 'keyring'
    ]
    
    status = {}
    for pkg in required:
        try:
            __import__(pkg.replace('.', '_') if '.' in pkg else pkg)
            status[pkg] = True
        except ImportError:
            # Try alternate import names
            try:
                if pkg == 'dotenv':
                    import dotenv
                    status[pkg] = True
                elif pkg == 'PIL':
                    from PIL import Image
                    status[pkg] = True
                elif pkg == 'google.generativeai':
                    import google.generativeai
                    status[pkg] = True
                else:
                    status[pkg] = False
                    logger.warning(f"[WARN] Missing package: {pkg}")
            except ImportError:
                status[pkg] = False
                logger.warning(f"[WARN] Missing package: {pkg}")
    
    return status

def check_env_config() -> Dict[str, bool]:
    """Verify environment configuration."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['WHATSAPP_NUMBER', 'GEMINI_API_KEY']
    optional_vars = ['NEWS_API_KEY', 'GNEWS_API_KEY']
    
    status = {}
    
    for var in required_vars:
        value = os.getenv(var, '')
        is_valid = bool(value) and 'YOUR_' not in value
        status[var] = is_valid
        if is_valid:
            logger.info(f"[OK] {var} configured")
        else:
            logger.error(f"[ERR] {var} missing or placeholder")
    
    for var in optional_vars:
        value = os.getenv(var, '')
        is_valid = bool(value) and 'YOUR_' not in value
        status[var] = is_valid
        if is_valid:
            logger.info(f"[OK] {var} configured")
        else:
            logger.info(f"[INFO] {var} not configured (optional)")
    
    return status

def check_network() -> bool:
    """Check internet connectivity."""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        logger.info("[OK] Network connected")
        return True
    except OSError:
        logger.error("[ERR] No internet connection")
        return False

# =============================================================================
# MAIN OPERATIONS
# =============================================================================

def run_health_check() -> Dict[str, Any]:
    """Run comprehensive system health check."""
    logger.info("=" * 60)
    logger.info("[>>] SYSTEM HEALTH CHECK")
    logger.info("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'python': check_python_version(),
        'network': check_network(),
        'dependencies': check_dependencies(),
        'config': check_env_config()
    }
    
    # Calculate overall health
    dep_ok = all(results['dependencies'].values())
    cfg_ok = results['config'].get('WHATSAPP_NUMBER', False) and results['config'].get('GEMINI_API_KEY', False)
    
    results['overall'] = all([
        results['python'],
        results['network'],
        dep_ok,
        cfg_ok
    ])
    
    if results['overall']:
        logger.info("=" * 60)
        logger.info("[OK] SYSTEM HEALTHY - Ready to run")
        logger.info("=" * 60)
    else:
        logger.warning("=" * 60)
        logger.warning("[WARN] SYSTEM HAS ISSUES - Review above errors")
        logger.warning("=" * 60)
    
    return results

def run_news_fetch(dry_run: bool = False) -> Dict[str, Any]:
    """Fetch news from all sources."""
    logger.info("[>>] Fetching news...")
    
    try:
        from news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        all_news = fetcher.fetch_all_news()
        
        total = sum(len(articles) for articles in all_news.values())
        logger.info(f"[OK] Fetched {total} articles from {len(all_news)} topics")
        
        return {'success': True, 'count': total, 'topics': len(all_news)}
    except Exception as e:
        logger.error(f"[ERR] News fetch failed: {e}")
        return {'success': False, 'error': str(e)}

def run_summarize(news_data: Dict) -> Optional[str]:
    """Summarize news using AI."""
    logger.info("[>>] Generating AI summary...")
    
    try:
        from ai_summarizer import GeminiSummarizer
        summarizer = GeminiSummarizer()
        
        # Filter and summarize
        filtered = {k: summarizer.filter_relevant_news(v, k) for k, v in news_data.items() if v}
        report = summarizer.create_intelligence_report(filtered)
        
        logger.info(f"[OK] Report generated ({len(report)} chars)")
        return report
    except Exception as e:
        logger.error(f"[ERR] Summarization failed: {e}")
        return None

def run_send_message(message: str, dry_run: bool = False) -> bool:
    """Send message via WhatsApp."""
    if dry_run:
        logger.info("[DRY] DRY RUN - Message not sent")
        logger.info(f"Preview ({len(message)} chars):\n{message[:500]}...")
        return True
    
    logger.info("[>>] Sending via WhatsApp...")
    
    try:
        from whatsapp_sender import WhatsAppSender
        sender = WhatsAppSender()
        success = sender.send_message(message)
        
        if success:
            logger.info("[OK] Message sent successfully")
        else:
            logger.warning("[WARN] Send command issued but verify delivery")
        
        return success
    except Exception as e:
        logger.error(f"[ERR] Send failed: {e}")
        return False

def run_full_cycle(dry_run: bool = False, json_output: bool = False) -> Dict[str, Any]:
    """Run complete automation cycle."""
    start_time = time.time()
    
    logger.info("=" * 60)
    logger.info("[>>] STARTING FULL AUTOMATION CYCLE")
    logger.info(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 60)
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'live',
        'steps': {}
    }
    
    # Step 1: Health Check
    health = run_health_check()
    result['steps']['health'] = health['overall']
    
    if not health['overall']:
        result['success'] = False
        result['error'] = 'Health check failed'
        return result
    
    # Step 2: Fetch News
    from news_fetcher import NewsFetcher
    from news_clustering import NewsClusterer
    
    fetcher = NewsFetcher()
    all_news = fetcher.fetch_all_news()
    
    # Clustering (Smart De-duplication)
    try:
        clusterer = NewsClusterer(similarity_threshold=0.65)
        all_news = clusterer.cluster_news(all_news)
    except Exception as e:
        logger.warning(f"[WARN] Clustering failed (skipping): {e}")
    
    result['steps']['fetch'] = {'articles': sum(len(v) for v in all_news.values())}
    
    # Step 3: Summarize
    report = run_summarize(all_news)
    result['steps']['summarize'] = bool(report)
    
    if not report:
        result['success'] = False
        result['error'] = 'Summarization failed'
        return result
    
    result['report'] = report
    
    # Step 4: Send
    send_success = run_send_message(report, dry_run=dry_run)
    result['steps']['send'] = send_success
    
    # Final
    elapsed = time.time() - start_time
    result['elapsed_seconds'] = round(elapsed, 2)
    result['success'] = True
    
    logger.info("=" * 60)
    logger.info(f"[OK] CYCLE COMPLETE in {elapsed:.1f}s")
    logger.info("=" * 60)
    
    # 5. Generate Dashboard
    try:
        from dashboard_generator import DashboardGenerator
        dash = DashboardGenerator()
        dash_path = dash.generate()
        logger.info(f"[OK] Dashboard updated: {dash_path}")
        result['dashboard'] = str(dash_path)
    except Exception as e:
        logger.error(f"[WARN] Dashboard generation failed: {e}")

    # 6. Video Generation (Optional/On-Request)
    if json_output:
        try:
            from video_generator import generate_video
            # We need the filtered news for the video, but here we have the full report or raw news.
            # Ideally we pass the structured data. For now, let's pass 'all_news' (raw) 
            # or refactor return values. 
            # Simpler: Just log availability.
            # Actual implementation:
            vid_path = generate_video(all_news)
            result['video'] = vid_path
        except Exception as e:
            logger.error(f"[WARN] Video generation failed: {e}")

    if json_output:
        print(json.dumps(result, indent=2))
    
    return result

# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='DailyNewsBot - Master Automation Controller',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_automation.py --health      # Check system health
  python run_automation.py --dry-run     # Test without sending
  python run_automation.py --run         # Full live cycle
  python run_automation.py --fetch-only  # Just fetch news
  python run_automation.py --dashboard   # Regenerate dashboard
        """
    )
    
    parser.add_argument('--health', action='store_true', help='Run health check only')
    parser.add_argument('--dry-run', action='store_true', help='Test cycle without sending')
    parser.add_argument('--run', action='store_true', help='Run full live cycle')
    parser.add_argument('--fetch-only', action='store_true', help='Fetch news only')
    parser.add_argument('--dashboard', action='store_true', help='Regenerate dashboard')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Default to health check if no args
    if not any([args.health, args.dry_run, args.run, args.fetch_only, args.dashboard]):
        args.health = True
    
    try:
        if args.dashboard:
            from dashboard_generator import DashboardGenerator
            DashboardGenerator().generate()
            return 0

        if args.health:
            result = run_health_check()
            return 0 if result['overall'] else 1
        
        if args.fetch_only:
            result = run_news_fetch()
            return 0 if result['success'] else 1
        
        if args.dry_run:
            result = run_full_cycle(dry_run=True, json_output=args.json)
            return 0 if result['success'] else 1
        
        if args.run:
            result = run_full_cycle(dry_run=False, json_output=args.json)
            return 0 if result['success'] else 1
        
    except KeyboardInterrupt:
        logger.info("\n[STOP] Interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"[FATAL] Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
