#!/usr/bin/env python3
"""
Opera Panel Performance Monitor
Monitors and optimizes query performance automatically
"""
import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class PerformanceMonitor:
    """Monitors and analyzes Opera Panel performance"""
    
    def __init__(self, base_url: str = "http://localhost:5055"):
        self.base_url = base_url
        self.performance_data = []
        self.slow_query_threshold = 1000  # 1 second
        self.optimization_suggestions = []
        
    async def monitor_endpoint(self, session: aiohttp.ClientSession, 
                             endpoint: str, params: dict = None, 
                             label: str = None) -> Tuple[int, float, dict]:
        """Monitor a specific endpoint's performance"""
        url = f"{self.base_url}{endpoint}"
        label = label or endpoint
        
        start_time = time.time()
        try:
            async with session.get(url, params=params) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # Check if response contains HTML (successful page load)
                content_type = response.headers.get('content-type', '')
                is_html = 'text/html' in content_type
                
                perf_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "endpoint": endpoint,
                    "params": params or {},
                    "status_code": response.status,
                    "response_time_ms": response_time,
                    "label": label,
                    "content_type": content_type,
                    "is_html": is_html
                }
                
                self.performance_data.append(perf_data)
                
                # Check for slow queries
                if response_time > self.slow_query_threshold:
                    await self._analyze_slow_query(perf_data)
                
                return response.status, response_time, perf_data
                
        except Exception as e:
            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": endpoint,
                "params": params or {},
                "error": str(e),
                "label": label
            }
            self.performance_data.append(error_data)
            return 0, float('inf'), error_data
    
    async def _analyze_slow_query(self, perf_data: dict):
        """Analyze slow queries and suggest optimizations"""
        endpoint = perf_data["endpoint"]
        params = perf_data["params"]
        response_time = perf_data["response_time_ms"]
        
        suggestions = []
        
        # Analyze specific patterns
        if "master-data" in endpoint:
            if "is_active" in params:
                suggestions.append({
                    "type": "database_index",
                    "suggestion": "Add database index on 'is_active' field for faster filtering",
                    "impact": "high",
                    "implementation": "db.hospitals.createIndex({is_active: 1})"
                })
            
            if "search" in params and params["search"]:
                suggestions.append({
                    "type": "search_optimization", 
                    "suggestion": "Implement full-text search index for better search performance",
                    "impact": "high",
                    "implementation": "db.hospitals.createIndex({name: 'text', address: 'text'})"
                })
            
            if not params.get("limit") or int(params.get("limit", 0)) > 50:
                suggestions.append({
                    "type": "pagination",
                    "suggestion": "Implement proper pagination with limit ≤ 50 for better performance",
                    "impact": "medium", 
                    "implementation": "Add pagination controls to UI"
                })
        
        if suggestions:
            optimization = {
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": endpoint,
                "response_time": response_time,
                "suggestions": suggestions
            }
            self.optimization_suggestions.append(optimization)
            
            print(f"🐌 Slow query detected: {endpoint} ({response_time:.0f}ms)")
            for suggestion in suggestions:
                print(f"   💡 {suggestion['type']}: {suggestion['suggestion']}")
    
    async def run_performance_test_suite(self):
        """Run comprehensive performance test suite"""
        print("🚀 Starting Performance Test Suite...")
        
        # Test credentials
        LOGIN_URL = "/auth/login"
        HOSPITALS_URL = "/admin/master-data/hospitals"
        
        connector = aiohttp.TCPConnector(ssl=False)
        session = aiohttp.ClientSession(connector=connector)
        
        try:
            # Login first
            login_data = {"username": "operapanel", "password": "Sim!443355"}
            async with session.post(f"{self.base_url}{LOGIN_URL}", json=login_data) as response:
                if response.status != 200:
                    print("❌ Login failed")
                    return
            
            print("✅ Login successful, starting performance tests...")
            
            # Test scenarios with different parameters
            test_scenarios = [
                # Basic scenarios
                ({}, "All hospitals (no filters)"),
                ({"is_active": "true"}, "Active hospitals only"),
                ({"is_active": "false"}, "Inactive hospitals only"),
                
                # Search scenarios
                ({"search": "bangkok"}, "Search: Bangkok"),
                ({"search": "hospital"}, "Search: Hospital"),
                ({"search": "โรงพยาบาล"}, "Search: Thai text"),
                
                # Pagination scenarios
                ({"limit": 10, "skip": 0}, "Page 1 (10 items)"),
                ({"limit": 50, "skip": 0}, "Page 1 (50 items)"),
                ({"limit": 100, "skip": 0}, "Large page (100 items)"),
                
                # Combined filters
                ({"is_active": "true", "search": "bangkok"}, "Active + Search"),
                ({"is_active": "true", "limit": 25, "skip": 0}, "Active + Pagination"),
                
                # Geographic filters
                ({"province": "10"}, "Province filter"),
                ({"district": "1001"}, "District filter"),
            ]
            
            print(f"\n📊 Testing {len(test_scenarios)} scenarios...")
            
            for i, (params, description) in enumerate(test_scenarios, 1):
                print(f"\n{i:2d}. Testing: {description}")
                status, response_time, data = await self.monitor_endpoint(
                    session, HOSPITALS_URL, params, description
                )
                
                if status == 200:
                    color = "🟢" if response_time < 500 else "🟡" if response_time < 1000 else "🔴"
                    print(f"    {color} {response_time:.0f}ms - Status: {status}")
                else:
                    print(f"    🔴 Failed - Status: {status}")
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            print(f"\n📈 Performance test completed!")
            
        finally:
            await session.close()
    
    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance report"""
        if not self.performance_data:
            return {"error": "No performance data available"}
        
        # Filter successful requests
        successful_requests = [
            d for d in self.performance_data 
            if isinstance(d.get("response_time_ms"), (int, float)) and d.get("status_code") == 200
        ]
        
        if not successful_requests:
            return {"error": "No successful requests to analyze"}
        
        response_times = [d["response_time_ms"] for d in successful_requests]
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Categorize performance
        fast_requests = len([t for t in response_times if t < 500])
        medium_requests = len([t for t in response_times if 500 <= t < 1000])
        slow_requests = len([t for t in response_times if t >= 1000])
        
        # Analyze by endpoint
        endpoint_performance = defaultdict(list)
        for req in successful_requests:
            endpoint_performance[req["label"]].append(req["response_time_ms"])
        
        endpoint_stats = {}
        for label, times in endpoint_performance.items():
            endpoint_stats[label] = {
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "request_count": len(times)
            }
        
        # Performance grades
        overall_grade = "A" if avg_response_time < 200 else \
                       "B" if avg_response_time < 500 else \
                       "C" if avg_response_time < 1000 else "D"
        
        return {
            "summary": {
                "total_requests": len(successful_requests),
                "avg_response_time": round(avg_response_time, 2),
                "min_response_time": round(min_response_time, 2),
                "max_response_time": round(max_response_time, 2),
                "performance_grade": overall_grade
            },
            "performance_distribution": {
                "fast_requests": fast_requests,      # < 500ms
                "medium_requests": medium_requests,   # 500-1000ms
                "slow_requests": slow_requests       # > 1000ms
            },
            "endpoint_performance": endpoint_stats,
            "optimization_suggestions": self.optimization_suggestions,
            "slow_query_threshold": self.slow_query_threshold,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def print_performance_summary(self):
        """Print a formatted performance summary"""
        report = self.generate_performance_report()
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        summary = report["summary"]
        distribution = report["performance_distribution"]
        
        print(f"\n📊 Performance Summary")
        print(f"═══════════════════════")
        print(f"🎯 Overall Grade: {summary['performance_grade']}")
        print(f"📈 Average Response Time: {summary['avg_response_time']:.0f}ms")
        print(f"⚡ Best Response Time: {summary['min_response_time']:.0f}ms")
        print(f"🐌 Worst Response Time: {summary['max_response_time']:.0f}ms")
        print(f"📊 Total Requests: {summary['total_requests']}")
        
        print(f"\n⏱️  Response Time Distribution")
        print(f"───────────────────────────")
        total = summary['total_requests']
        print(f"🟢 Fast (< 500ms):   {distribution['fast_requests']:3d} ({distribution['fast_requests']/total*100:.1f}%)")
        print(f"🟡 Medium (500-1000ms): {distribution['medium_requests']:3d} ({distribution['medium_requests']/total*100:.1f}%)")
        print(f"🔴 Slow (> 1000ms):   {distribution['slow_requests']:3d} ({distribution['slow_requests']/total*100:.1f}%)")
        
        if report["optimization_suggestions"]:
            print(f"\n💡 Optimization Suggestions")
            print(f"─────────────────────────────")
            for opt in report["optimization_suggestions"]:
                print(f"🎯 Endpoint: {opt['endpoint']} ({opt['response_time']:.0f}ms)")
                for suggestion in opt["suggestions"]:
                    impact_icon = "🔥" if suggestion["impact"] == "high" else "⚡" if suggestion["impact"] == "medium" else "💡"
                    print(f"   {impact_icon} {suggestion['suggestion']}")
        
        # Save detailed report
        with open("performance_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Detailed report saved to: performance_report.json")


async def main():
    """Main performance monitoring function"""
    print("⚡ Opera Panel Performance Monitor")
    print("=" * 40)
    
    monitor = PerformanceMonitor()
    
    # Run performance test suite
    await monitor.run_performance_test_suite()
    
    # Generate and display report
    monitor.print_performance_summary()
    
    print("\n✅ Performance monitoring completed!")
    print("🎯 Use the suggestions above to optimize slow queries")
    print("📊 Monitor trends over time to track improvements")


if __name__ == "__main__":
    asyncio.run(main())
