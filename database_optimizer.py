#!/usr/bin/env python3
"""
Opera Panel Database Index Optimizer
Creates optimal database indexes for better performance
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List

class DatabaseIndexOptimizer:
    """Optimizes database indexes for Opera Panel performance"""
    
    def __init__(self):
        self.optimization_scripts = []
        self.performance_improvements = []
        
    def analyze_performance_report(self, report_file: str = "performance_report.json"):
        """Analyze performance report and generate optimization scripts"""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
                
            print(f"📊 Analyzing performance report...")
            print(f"   Current grade: {report['summary']['performance_grade']}")
            print(f"   Average response time: {report['summary']['avg_response_time']:.0f}ms")
            
            # Generate optimizations based on suggestions
            for suggestion in report.get('optimization_suggestions', []):
                self._generate_optimization_scripts(suggestion)
                
            return True
            
        except FileNotFoundError:
            print(f"❌ Performance report not found: {report_file}")
            return False
    
    def _generate_optimization_scripts(self, suggestion: dict):
        """Generate specific optimization scripts"""
        endpoint = suggestion['endpoint']
        response_time = suggestion['response_time']
        
        for sug in suggestion['suggestions']:
            if sug['type'] == 'database_index':
                self._add_database_index_script(endpoint, sug)
            elif sug['type'] == 'search_optimization':
                self._add_search_index_script(endpoint, sug)
            elif sug['type'] == 'pagination':
                self._add_pagination_optimization(endpoint, sug)
    
    def _add_database_index_script(self, endpoint: str, suggestion: dict):
        """Add database index optimization script"""
        if 'master-data' in endpoint and 'hospital' in endpoint:
            script = {
                "type": "mongodb_index",
                "collection": "organizations",  # Hospitals collection in Stardust
                "index": {"is_active": 1},
                "description": "Index on is_active field for faster status filtering",
                "estimated_improvement": "30-50% faster is_active queries",
                "mongodb_command": "db.organizations.createIndex({is_active: 1})",
                "priority": "high"
            }
            self.optimization_scripts.append(script)
            print(f"📇 Added index optimization: is_active field")
    
    def _add_search_index_script(self, endpoint: str, suggestion: dict):
        """Add search index optimization script"""
        if 'master-data' in endpoint:
            script = {
                "type": "mongodb_text_index",
                "collection": "organizations",
                "index": {
                    "name.th": "text",
                    "name.en": "text", 
                    "formatted_address": "text"
                },
                "description": "Full-text search index for name and address fields",
                "estimated_improvement": "50-70% faster text searches",
                "mongodb_command": "db.organizations.createIndex({\"name.th\": \"text\", \"name.en\": \"text\", \"formatted_address\": \"text\"})",
                "priority": "high"
            }
            self.optimization_scripts.append(script)
            print(f"🔍 Added search optimization: full-text index")
    
    def _add_pagination_optimization(self, endpoint: str, suggestion: dict):
        """Add pagination optimization"""
        script = {
            "type": "ui_optimization",
            "component": "pagination",
            "description": "Implement smarter pagination with default limits",
            "improvements": [
                "Set default page size to 25 items",
                "Add page size selector (10, 25, 50)",
                "Implement infinite scroll for better UX",
                "Add total count caching"
            ],
            "estimated_improvement": "20-30% faster page loads",
            "priority": "medium"
        }
        self.optimization_scripts.append(script)
        print(f"📄 Added pagination optimization")
    
    def generate_compound_indexes(self):
        """Generate compound indexes for complex queries"""
        compound_indexes = [
            {
                "type": "mongodb_compound_index",
                "collection": "organizations",
                "index": {"is_active": 1, "province_code": 1},
                "description": "Compound index for status + province filtering",
                "mongodb_command": "db.organizations.createIndex({is_active: 1, province_code: 1})",
                "use_case": "Filter active hospitals by province"
            },
            {
                "type": "mongodb_compound_index",
                "collection": "organizations",
                "index": {"is_active": 1, "district_code": 1},
                "description": "Compound index for status + district filtering",
                "mongodb_command": "db.organizations.createIndex({is_active: 1, district_code: 1})",
                "use_case": "Filter active hospitals by district"
            },
            {
                "type": "mongodb_compound_index",
                "collection": "organizations",
                "index": {"location": "2dsphere", "is_active": 1},
                "description": "Geospatial index with status for location-based queries",
                "mongodb_command": "db.organizations.createIndex({location: \"2dsphere\", is_active: 1})",
                "use_case": "Find active hospitals near location"
            }
        ]
        
        self.optimization_scripts.extend(compound_indexes)
        print(f"🗂️  Added {len(compound_indexes)} compound indexes")
    
    def create_optimization_implementation_plan(self):
        """Create step-by-step implementation plan"""
        plan = {
            "optimization_plan": {
                "created_at": datetime.utcnow().isoformat(),
                "total_optimizations": len(self.optimization_scripts),
                "estimated_total_improvement": "40-60% performance boost",
                "implementation_phases": []
            }
        }
        
        # Phase 1: High Priority Database Indexes
        high_priority = [s for s in self.optimization_scripts if s.get('priority') == 'high']
        if high_priority:
            plan["optimization_plan"]["implementation_phases"].append({
                "phase": 1,
                "name": "Critical Database Indexes",
                "description": "Implement high-impact database indexes",
                "optimizations": high_priority,
                "estimated_duration": "1-2 hours",
                "estimated_improvement": "30-50%"
            })
        
        # Phase 2: UI and Pagination Improvements
        ui_optimizations = [s for s in self.optimization_scripts if s.get('type') == 'ui_optimization']
        if ui_optimizations:
            plan["optimization_plan"]["implementation_phases"].append({
                "phase": 2,
                "name": "UI Performance Optimizations",
                "description": "Improve pagination and UI responsiveness",
                "optimizations": ui_optimizations,
                "estimated_duration": "2-4 hours",
                "estimated_improvement": "10-20%"
            })
        
        # Phase 3: Advanced Indexes
        compound_indexes = [s for s in self.optimization_scripts if 'compound' in s.get('type', '')]
        if compound_indexes:
            plan["optimization_plan"]["implementation_phases"].append({
                "phase": 3,
                "name": "Advanced Compound Indexes",
                "description": "Implement compound indexes for complex queries",
                "optimizations": compound_indexes,
                "estimated_duration": "1-2 hours",
                "estimated_improvement": "15-25%"
            })
        
        return plan
    
    def save_optimization_plan(self, filename: str = "database_optimization_plan.json"):
        """Save optimization plan to file"""
        plan = self.create_optimization_implementation_plan()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Optimization plan saved to: {filename}")
        return filename
    
    def print_optimization_summary(self):
        """Print optimization summary"""
        plan = self.create_optimization_implementation_plan()
        
        print(f"\n🎯 Database Optimization Plan")
        print(f"═══════════════════════════════")
        print(f"📊 Total Optimizations: {plan['optimization_plan']['total_optimizations']}")
        print(f"⚡ Estimated Improvement: {plan['optimization_plan']['estimated_total_improvement']}")
        
        for phase in plan["optimization_plan"]["implementation_phases"]:
            print(f"\n📋 Phase {phase['phase']}: {phase['name']}")
            print(f"   ⏱️  Duration: {phase['estimated_duration']}")
            print(f"   📈 Improvement: {phase['estimated_improvement']}")
            print(f"   🔧 Optimizations: {len(phase['optimizations'])}")
            
            for opt in phase['optimizations']:
                if opt['type'].startswith('mongodb'):
                    print(f"      🗃️  {opt['description']}")
                    print(f"         Command: {opt['mongodb_command']}")
                else:
                    print(f"      🎨 {opt['description']}")
    
    def generate_mongodb_script(self, filename: str = "apply_indexes.js"):
        """Generate MongoDB script to apply all indexes"""
        script_lines = [
            "// Opera Panel Database Optimization Script",
            "// Generated automatically based on performance analysis",
            f"// Created: {datetime.utcnow().isoformat()}",
            "",
            "print('🚀 Starting database optimization...');",
            ""
        ]
        
        for opt in self.optimization_scripts:
            if opt['type'].startswith('mongodb'):
                script_lines.extend([
                    f"// {opt['description']}",
                    f"print('📇 Creating index: {opt.get('use_case', opt['description'])}...');",
                    opt['mongodb_command'] + ";",
                    "print('✅ Index created successfully');",
                    ""
                ])
        
        script_lines.append("print('🎉 Database optimization completed!');")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(script_lines))
        
        print(f"📜 MongoDB script saved to: {filename}")
        return filename


async def main():
    """Main optimization function"""
    print("🗃️  Opera Panel Database Index Optimizer")
    print("=" * 45)
    
    optimizer = DatabaseIndexOptimizer()
    
    # Analyze performance report
    if optimizer.analyze_performance_report():
        print("✅ Performance report analyzed successfully")
        
        # Generate compound indexes
        optimizer.generate_compound_indexes()
        
        # Print summary
        optimizer.print_optimization_summary()
        
        # Save files
        optimizer.save_optimization_plan()
        optimizer.generate_mongodb_script()
        
        print(f"\n✅ Optimization plan completed!")
        print(f"📋 Next steps:")
        print(f"   1. Review the optimization plan")
        print(f"   2. Apply MongoDB indexes using apply_indexes.js")
        print(f"   3. Implement UI optimizations")
        print(f"   4. Re-run performance tests to measure improvement")
        
    else:
        print("❌ Could not analyze performance report")
        print("💡 Run the performance monitor first: python3 test_performance_monitor.py")


if __name__ == "__main__":
    asyncio.run(main())
