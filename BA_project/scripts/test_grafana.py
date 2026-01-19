#!/usr/bin/env python3
"""
Test Grafana Cloud Connection
Verifies that credentials are correct and metrics can be pushed
"""
import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Try to load from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[i] Loaded environment from .env file")
except ImportError:
    print("[i] python-dotenv not installed, using system environment")

def print_status(emoji, message):
    """Print colored status message"""
    print(f"{emoji} {message}")

def test_configuration():
    """Test if Grafana Cloud is configured"""
    print("\n" + "="*60)
    print("Testing Grafana Cloud Configuration")
    print("="*60 + "\n")
    
    url = os.getenv('GRAFANA_CLOUD_URL', '')
    user = os.getenv('GRAFANA_CLOUD_USER', '')
    api_key = os.getenv('GRAFANA_CLOUD_API_KEY', '')
    
    if not url:
        print_status("❌", "GRAFANA_CLOUD_URL not set")
        print("   Set it to: https://prometheus-prod-xx-xxx.grafana.net/api/prom/push")
        return False
    else:
        print_status("✓", f"GRAFANA_CLOUD_URL: {url[:50]}...")
    
    if not user:
        print_status("❌", "GRAFANA_CLOUD_USER not set")
        print("   Set it to your Instance ID (e.g., 123456)")
        return False
    else:
        print_status("✓", f"GRAFANA_CLOUD_USER: {user}")
    
    if not api_key:
        print_status("❌", "GRAFANA_CLOUD_API_KEY not set")
        print("   Set it to your API key (starts with glc_)")
        return False
    else:
        print_status("✓", f"GRAFANA_CLOUD_API_KEY: {api_key[:10]}...{api_key[-5:]}")
    
    return True

def test_connection(url, user, api_key):
    """Test actual connection to Grafana Cloud"""
    print("\n" + "="*60)
    print("Testing Connection")
    print("="*60 + "\n")
    
    # Create sample metrics
    timestamp_ms = int(time.time() * 1000)
    test_metrics = f"""# HELP test_metric Test metric for connection
# TYPE test_metric gauge
test_metric{{source="ba_project_test"}} 1 {timestamp_ms}
"""
    
    try:
        print_status("🔄", "Sending test metrics to Grafana Cloud...")
        response = requests.post(
            url,
            data=test_metrics,
            auth=HTTPBasicAuth(user, api_key),
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print_status("✓", "Successfully pushed test metrics!")
            return True
        else:
            print_status("❌", f"Push failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Provide helpful error messages
            if response.status_code == 401:
                print("\n   💡 Tip: Check your GRAFANA_CLOUD_USER and GRAFANA_CLOUD_API_KEY")
            elif response.status_code == 404:
                print("\n   💡 Tip: Check your GRAFANA_CLOUD_URL (should end with /api/prom/push)")
            elif response.status_code == 429:
                print("\n   💡 Tip: Rate limit exceeded, wait a moment and try again")
            
            return False
            
    except requests.exceptions.Timeout:
        print_status("❌", "Connection timeout")
        print("   💡 Tip: Check your internet connection or firewall settings")
        return False
    except requests.exceptions.ConnectionError as e:
        print_status("❌", f"Connection error: {e}")
        print("   💡 Tip: Verify the URL is correct")
        return False
    except Exception as e:
        print_status("❌", f"Unexpected error: {e}")
        return False

def test_metrics_module():
    """Test if our metrics module works"""
    print("\n" + "="*60)
    print("Testing Metrics Module")
    print("="*60 + "\n")
    
    try:
        from utils.grafana_metrics import is_configured, format_prometheus_metrics
        from utils.metrics import calculate_metrics
        
        print_status("✓", "Successfully imported metrics modules")
        
        # Test configuration check
        if is_configured():
            print_status("✓", "Grafana Cloud is configured")
        else:
            print_status("❌", "Grafana Cloud not configured")
            return False
        
        # Test metrics calculation
        print_status("🔄", "Calculating A/B test metrics...")
        metrics = calculate_metrics()
        print_status("✓", f"Found metrics for {len(metrics)} variants")
        
        # Test formatting
        print_status("🔄", "Formatting metrics for Prometheus...")
        prometheus_data = format_prometheus_metrics(metrics)
        lines = prometheus_data.split('\n')
        print_status("✓", f"Formatted {len(lines)} lines of metrics")
        
        # Show sample
        print("\nSample metrics (first 10 lines):")
        print("-" * 60)
        for line in lines[:10]:
            print(f"  {line}")
        print("-" * 60)
        
        return True
        
    except ImportError as e:
        print_status("❌", f"Failed to import module: {e}")
        return False
    except Exception as e:
        print_status("❌", f"Error: {e}")
        return False

def test_full_push():
    """Test the actual push_metrics_to_grafana function"""
    print("\n" + "="*60)
    print("Testing Full Metrics Push")
    print("="*60 + "\n")
    
    try:
        from utils.grafana_metrics import push_metrics_to_grafana
        
        print_status("🔄", "Pushing real metrics to Grafana Cloud...")
        success = push_metrics_to_grafana()
        
        if success:
            print_status("✓", "Successfully pushed metrics!")
            print("\n   Next steps:")
            print("   1. Go to your Grafana Cloud dashboard")
            print("   2. Click Explore (compass icon)")
            print("   3. Select your Prometheus datasource")
            print("   4. Query: ba_ab_impressions_total")
            print("   5. You should see your metrics!")
            return True
        else:
            print_status("❌", "Push failed (check logs above)")
            return False
            
    except Exception as e:
        print_status("❌", f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Grafana Cloud Connection Test")
    print("  BA Project - Movie Recommender A/B Testing")
    print("="*60)
    
    results = []
    
    # Test 1: Configuration
    results.append(("Configuration", test_configuration()))
    
    if not results[-1][1]:
        print("\n" + "="*60)
        print("❌ Configuration Failed")
        print("="*60)
        print("\nPlease set the required environment variables:")
        print("  export GRAFANA_CLOUD_URL='...'")
        print("  export GRAFANA_CLOUD_USER='...'")
        print("  export GRAFANA_CLOUD_API_KEY='...'")
        print("\nOr create a .env file with these values.")
        print("\nSee docs/GRAFANA_SETUP.md for detailed instructions.")
        return 1
    
    # Test 2: Connection
    url = os.getenv('GRAFANA_CLOUD_URL')
    user = os.getenv('GRAFANA_CLOUD_USER')
    api_key = os.getenv('GRAFANA_CLOUD_API_KEY')
    results.append(("Connection", test_connection(url, user, api_key)))
    
    # Test 3: Metrics Module
    results.append(("Metrics Module", test_metrics_module()))
    
    # Test 4: Full Push
    results.append(("Full Metrics Push", test_full_push()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("="*60)
        print("\n🎉 Success! Your Grafana Cloud setup is working perfectly.")
        print("\nNext steps:")
        print("  1. Start your app: python app.py")
        print("  2. Import dashboard: grafana-dashboards/ab-test-dashboard.json")
        print("  3. Generate traffic and watch metrics flow!")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total} passed)")
        print("="*60)
        print("\nPlease fix the errors above.")
        print("See docs/GRAFANA_SETUP.md for help.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
