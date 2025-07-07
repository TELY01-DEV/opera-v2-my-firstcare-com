#!/usr/bin/env python3
"""
Test script to verify hospital sorting by updated_at
"""

# Test data to simulate the sorting behavior
test_records = [
    {'_id': '1', 'name': 'Hospital A', 'updated_at': '2024-08-02T04:19:44.844000'},
    {'_id': '2', 'name': 'Hospital B', 'updated_at': '2024-10-10T11:11:22.200000'},
    {'_id': '3', 'name': 'Hospital C', 'updated_at': '2024-08-02T04:19:44.844000'},
]

def get_sort_date(record):
    # Use updated_at if available, otherwise fall back to created_at
    updated = record.get('updated_at')
    created = record.get('created_at')
    # Return the date for sorting, preferring updated_at
    return updated if updated else (created if created else '')

print("Original order:")
for i, record in enumerate(test_records):
    print(f"{i+1}. {record['name']} - {record['updated_at']}")

# Sort in descending order (most recent first)
sorted_records = sorted(test_records, key=get_sort_date, reverse=True)

print("\nSorted order (most recent first):")
for i, record in enumerate(sorted_records):
    print(f"{i+1}. {record['name']} - {record['updated_at']}")

print("\nExpected result: Hospital B should be first (2024-10-10), then A and C (2024-08-02)")
