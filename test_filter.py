#!/usr/bin/env python3
"""
Test the localized_name filter directly
"""

# Sample data structure from Stardust API
sample_data = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "code": "10",
        "name": [
            {"code": "th", "name": "กรุงเทพมหานคร"},
            {"code": "en", "name": "Bangkok"}
        ],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002", 
        "code": "11",
        "name": [
            {"code": "th", "name": "สมุทรปราการ"},
            {"code": "en", "name": "Samut Prakan"}
        ],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
]

def localized_name_filter(name_array, language):
    """
    Test implementation of the localized_name filter
    """
    if not isinstance(name_array, list):
        return str(name_array) if name_array else ""
    
    # Try to find name in requested language
    for name_item in name_array:
        if isinstance(name_item, dict) and name_item.get("code") == language:
            return name_item.get("name", "")
    
    # Fallback to English if requested language not found
    if language != "en":
        for name_item in name_array:
            if isinstance(name_item, dict) and name_item.get("code") == "en":
                return name_item.get("name", "")
    
    # Last fallback to first available name
    if name_array and isinstance(name_array[0], dict):
        return name_array[0].get("name", "")
    
    return ""

def test_filter():
    """Test the filter with sample data"""
    print("🧪 Testing localized_name filter...")
    
    for record in sample_data:
        print(f"\nRecord: {record['code']}")
        print(f"Raw name data: {record['name']}")
        
        # Test with Thai
        th_name = localized_name_filter(record['name'], 'th')
        print(f"Thai name: {th_name}")
        
        # Test with English
        en_name = localized_name_filter(record['name'], 'en')
        print(f"English name: {en_name}")
        
        # Test with unknown language
        unknown_name = localized_name_filter(record['name'], 'fr')
        print(f"French (fallback to EN): {unknown_name}")

def test_template_logic():
    """Test the template display logic"""
    print("\n🎨 Testing template display logic...")
    
    language = 'th'
    
    for record in sample_data:
        print(f"\nRecord: {record['code']}")
        
        # Primary name
        primary_name = localized_name_filter(record['name'], language)
        print(f"Primary ({language}): {primary_name}")
        
        # Alternative name
        alt_language = 'en' if language == 'th' else 'th'
        alt_name = localized_name_filter(record['name'], alt_language)
        
        if alt_name and alt_name != primary_name:
            print(f"Alternative ({alt_language}): {alt_name}")
        else:
            print("No alternative name to show")

if __name__ == "__main__":
    test_filter()
    test_template_logic()
