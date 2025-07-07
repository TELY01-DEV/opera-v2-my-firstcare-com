#!/usr/bin/env python3
"""
Simple test to verify the active/inactive filter logic
"""

def test_is_active_conversion():
    """Test the is_active parameter conversion logic from master_data.py"""
    
    def convert_is_active_filter(is_active):
        """Simulate the conversion logic from the route"""
        is_active_bool = None
        
        if is_active and is_active.strip():
            if is_active.lower() in ['true', '1', 'active']:
                is_active_bool = True
            elif is_active.lower() in ['false', '0', 'inactive']:
                is_active_bool = False
        
        return is_active_bool
    
    # Test cases
    test_cases = [
        ("true", True),
        ("True", True), 
        ("TRUE", True),
        ("1", True),
        ("active", True),
        ("ACTIVE", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("inactive", False),
        ("INACTIVE", False),
        ("", None),
        (None, None),
        ("   ", None),
        ("invalid", None),
        ("maybe", None)
    ]
    
    print("🧪 Testing is_active filter conversion logic...")
    print("=" * 60)
    
    all_passed = True
    for input_val, expected in test_cases:
        result = convert_is_active_filter(input_val)
        status = "✅" if result == expected else "❌"
        
        if result != expected:
            all_passed = False
            
        print(f"{status} Input: '{input_val}' -> Expected: {expected}, Got: {result}")
    
    print("=" * 60)
    if all_passed:
        print("🎉 All test cases passed!")
    else:
        print("❌ Some test cases failed!")
    
    return all_passed

def test_filter_parameters():
    """Test URL parameter construction"""
    print("\n🔗 Testing URL parameter construction...")
    print("=" * 60)
    
    # Simulate different filter scenarios
    scenarios = [
        {
            "description": "Active only filter",
            "params": {"is_active": "true"},
            "expected_query": "is_active=true"
        },
        {
            "description": "Inactive only filter", 
            "params": {"is_active": "false"},
            "expected_query": "is_active=false"
        },
        {
            "description": "No status filter",
            "params": {},
            "expected_query": ""
        },
        {
            "description": "Combined filters",
            "params": {"search": "hospital", "is_active": "true", "province_code": "10"},
            "expected_query": "search=hospital&is_active=true&province_code=10"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['description']}:")
        
        # Build query string
        query_parts = []
        for key, value in scenario['params'].items():
            if value:
                query_parts.append(f"{key}={value}")
        
        actual_query = "&".join(query_parts)
        print(f"   Expected: {scenario['expected_query']}")
        print(f"   Actual:   {actual_query}")
        
        if actual_query == scenario['expected_query']:
            print("   ✅ Match!")
        else:
            print("   ❌ Mismatch!")

def simulate_api_response():
    """Simulate API response filtering"""
    print("\n📊 Simulating API response filtering...")
    print("=" * 60)
    
    # Sample hospital data
    sample_hospitals = [
        {
            "id": "1",
            "name": {"en": "Bangkok Hospital", "th": "โรงพยาบาลกรุงเทพ"},
            "active": True,
            "updated_at": "2025-01-15T10:30:00Z"
        },
        {
            "id": "2", 
            "name": {"en": "Inactive Clinic", "th": "คลินิกปิด"},
            "active": False,
            "updated_at": "2025-01-10T08:00:00Z"
        },
        {
            "id": "3",
            "name": {"en": "Community Hospital", "th": "โรงพยาบาลชุมชน"},
            "active": True,
            "updated_at": "2025-01-20T14:15:00Z"
        },
        {
            "id": "4",
            "name": {"en": "Old Hospital", "th": "โรงพยาบาลเก่า"},
            "active": False,
            "updated_at": "2024-12-01T09:00:00Z"
        }
    ]
    
    def filter_by_status(records, is_active_filter):
        """Simulate server-side filtering"""
        if is_active_filter is None:
            return records
        
        return [r for r in records if r["active"] == is_active_filter]
    
    # Test different filters
    print("📋 Original data: 4 hospitals (2 active, 2 inactive)")
    
    # Filter for active only
    active_results = filter_by_status(sample_hospitals, True)
    print(f"🟢 Active filter: {len(active_results)} results")
    for hospital in active_results:
        name = hospital["name"]["en"]
        print(f"   - {name} (active: {hospital['active']})")
    
    # Filter for inactive only
    inactive_results = filter_by_status(sample_hospitals, False)
    print(f"🔴 Inactive filter: {len(inactive_results)} results")
    for hospital in inactive_results:
        name = hospital["name"]["en"]
        print(f"   - {name} (active: {hospital['active']})")
    
    # No filter
    all_results = filter_by_status(sample_hospitals, None)
    print(f"⚪ No filter: {len(all_results)} results")
    for hospital in all_results:
        name = hospital["name"]["en"]
        print(f"   - {name} (active: {hospital['active']})")

if __name__ == "__main__":
    print("🔍 Testing Opera Panel Status Filtering Logic")
    print("=" * 80)
    
    # Run all tests
    test_is_active_conversion()
    test_filter_parameters()
    simulate_api_response()
    
    print("\n" + "=" * 80)
    print("✅ Filter testing completed!")
