#!/usr/bin/env python3
"""
Test script for OMEGA Evolution Monitor
"""

import subprocess
import time
import json
import os
import sys

def test_dependencies():
    """Test if required dependencies are installed"""
    print("🔍 Testing dependencies...")

    required_packages = ['psutil', 'colorama']

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            return False

    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing required dependencies...")

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'psutil', 'colorama'
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def test_monitor_import():
    """Test if the monitor can be imported"""
    print("🔍 Testing monitor import...")

    try:
        import omega_evolution_monitor
        print("✅ Monitor module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import monitor: {e}")
        return False

def test_monitor_instantiation():
    """Test if the monitor can be instantiated"""
    print("🔍 Testing monitor instantiation...")

    try:
        from omega_evolution_monitor import OmegaEvolutionMonitor

        monitor = OmegaEvolutionMonitor()
        print("✅ Monitor instantiated successfully")
        print(f"📊 Monitor system info: {monitor.system_info}")

        return True
    except Exception as e:
        print(f"❌ Failed to instantiate monitor: {e}")
        return False

def test_basic_functionality():
    """Test basic monitor functionality"""
    print("🔍 Testing basic functionality...")

    try:
        from omega_evolution_monitor import OmegaEvolutionMonitor

        monitor = OmegaEvolutionMonitor()

        # Test system info
        system_info = monitor._get_system_info()
        print(f"✅ System info: {system_info['platform']} {system_info['architecture']}")

        # Test evolution summary
        summary = monitor.get_evolution_summary()
        print(f"✅ Evolution summary created with {len(summary)} fields")

        # Test threat assessment
        threat_level = monitor._assess_threat_level(3, 8)
        danger_level = monitor._assess_danger_level(3, 8)
        print(f"✅ Threat assessment: {threat_level} / {danger_level}")

        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("🔍 Testing report generation...")

    try:
        from omega_evolution_monitor import OmegaEvolutionMonitor

        monitor = OmegaEvolutionMonitor()

        # Generate a test report
        report_file = 'test_evolution_report.json'
        success = monitor.save_evolution_report(report_file)

        if success and os.path.exists(report_file):
            with open(report_file, 'r') as f:
                report = json.load(f)
            print(f"✅ Report generated with {len(report)} fields")
            print(f"📊 Report includes: {', '.join(report.keys())}")
            return True
        else:
            print("❌ Report generation failed")
            return False
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🔥 OMEGA EVOLUTION MONITOR - TESTING 🔥")
    print("=" * 60)

    # Test dependencies
    if not test_dependencies():
        print("\n💀 Missing dependencies detected!")
        if install_dependencies():
            print("🔄 Dependencies installed, retrying tests...")
            if not test_dependencies():
                print("❌ Still missing dependencies after installation")
                return
        else:
            print("❌ Failed to install dependencies")
            return

    # Run tests
    tests = [
        ("Dependency Test", test_dependencies),
        ("Import Test", test_monitor_import),
        ("Instantiation Test", test_monitor_instantiation),
        ("Basic Functionality Test", test_basic_functionality),
        ("Report Generation Test", test_report_generation)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"🎯 Tests Passed: {passed}/{total}")

    if passed == total:
        print("🔥 ALL TESTS PASSED - MONITOR IS READY!")
        print("💀 You can now run: python omega_evolution_monitor.py")
    else:
        print("⚠️  Some tests failed - check the output above")

    print("=" * 60)

if __name__ == "__main__":
    main()
