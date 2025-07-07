#!/usr/bin/env python3
"""
Opera Panel Analytics Module
Tracks user interactions and filter usage patterns
"""
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional

class OperaPanelAnalytics:
    """Analytics tracker for Opera Panel user interactions"""
    
    def __init__(self, base_url: str = "http://localhost:5055"):
        self.base_url = base_url
        self.analytics_data = []
        
    async def track_filter_usage(self, session: aiohttp.ClientSession, 
                               filter_type: str, filter_value: Optional[str] = None):
        """Track filter usage patterns"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "filter_usage",
            "filter_type": filter_type,
            "filter_value": filter_value,
            "session_id": id(session)
        }
        self.analytics_data.append(event)
        print(f"📊 Tracked filter usage: {filter_type}={filter_value}")
        
    async def track_page_access(self, session: aiohttp.ClientSession, 
                              page_name: str, response_time: float):
        """Track page access and performance"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "page_access",
            "page_name": page_name,
            "response_time_ms": response_time,
            "session_id": id(session)
        }
        self.analytics_data.append(event)
        print(f"📈 Tracked page access: {page_name} ({response_time:.0f}ms)")
        
    def generate_analytics_report(self) -> Dict:
        """Generate analytics report from collected data"""
        filter_usage = {}
        page_performance = {}
        
        for event in self.analytics_data:
            if event["event_type"] == "filter_usage":
                filter_key = f"{event['filter_type']}={event['filter_value']}"
                filter_usage[filter_key] = filter_usage.get(filter_key, 0) + 1
                
            elif event["event_type"] == "page_access":
                page = event["page_name"]
                if page not in page_performance:
                    page_performance[page] = []
                page_performance[page].append(event["response_time_ms"])
        
        # Calculate averages
        page_avg_performance = {}
        for page, times in page_performance.items():
            page_avg_performance[page] = {
                "avg_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "total_requests": len(times)
            }
        
        return {
            "summary": {
                "total_events": len(self.analytics_data),
                "filter_events": len([e for e in self.analytics_data if e["event_type"] == "filter_usage"]),
                "page_events": len([e for e in self.analytics_data if e["event_type"] == "page_access"])
            },
            "filter_usage": filter_usage,
            "page_performance": page_avg_performance,
            "report_generated": datetime.utcnow().isoformat()
        }
        
    def save_report(self, filename: str = "analytics_report.json"):
        """Save analytics report to file"""
        report = self.generate_analytics_report()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"💾 Analytics report saved to {filename}")
        return filename


async def test_filter_usage_analytics():
    """Test filter usage with analytics tracking"""
    analytics = OperaPanelAnalytics()
    
    # Test credentials
    LOGIN_URL = f"{analytics.base_url}/auth/login"
    HOSPITALS_URL = f"{analytics.base_url}/admin/master-data/hospitals"
    
    connector = aiohttp.TCPConnector(ssl=False)
    session = aiohttp.ClientSession(connector=connector)
    
    try:
        # Login
        login_data = {"username": "operapanel", "password": "Sim!443355"}
        
        start_time = datetime.utcnow()
        async with session.post(LOGIN_URL, json=login_data) as response:
            login_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if response.status == 200:
                await analytics.track_page_access(session, "login", login_time)
                print("✅ Login successful")
                
                # Test different filter scenarios with analytics
                test_scenarios = [
                    ("is_active", "true", "Active hospitals filter"),
                    ("is_active", "false", "Inactive hospitals filter"),
                    ("is_active", None, "All hospitals (no filter)"),
                    ("search", "bangkok", "Search for Bangkok"),
                    ("province", "10", "Filter by province"),
                ]
                
                for filter_type, filter_value, description in test_scenarios:
                    print(f"\n🔍 Testing: {description}")
                    
                    params = {"limit": 10, "skip": 0}
                    if filter_value is not None:
                        params[filter_type] = filter_value
                    
                    start_time = datetime.utcnow()
                    async with session.get(HOSPITALS_URL, params=params) as resp:
                        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                        
                        if resp.status == 200:
                            await analytics.track_filter_usage(session, filter_type, filter_value)
                            await analytics.track_page_access(session, "hospitals_filtered", response_time)
                            print(f"✅ {description} - Response time: {response_time:.0f}ms")
                        else:
                            print(f"❌ {description} failed with status {resp.status}")
                
                # Generate and display analytics report
                print("\n📊 Generating Analytics Report...")
                report = analytics.generate_analytics_report()
                
                print(f"\n📈 Analytics Summary:")
                print(f"   Total Events: {report['summary']['total_events']}")
                print(f"   Filter Events: {report['summary']['filter_events']}")
                print(f"   Page Events: {report['summary']['page_events']}")
                
                print(f"\n🔍 Filter Usage Patterns:")
                for filter_combo, count in report['filter_usage'].items():
                    print(f"   {filter_combo}: {count} times")
                
                print(f"\n⚡ Page Performance:")
                for page, perf in report['page_performance'].items():
                    print(f"   {page}: {perf['avg_response_time']:.0f}ms avg ({perf['total_requests']} requests)")
                
                # Save report
                report_file = analytics.save_report()
                print(f"\n📄 Full report available in: {report_file}")
                
            else:
                print(f"❌ Login failed with status {response.status}")
                
    finally:
        await session.close()


async def main():
    """Main analytics test function"""
    print("📊 Opera Panel Filter Usage Analytics Test")
    print("=" * 50)
    
    await test_filter_usage_analytics()
    
    print("\n✅ Analytics test completed!")
    print("📈 This demonstrates how we can track filter usage patterns")
    print("🎯 Use this data to optimize the most-used filters")


if __name__ == "__main__":
    asyncio.run(main())
