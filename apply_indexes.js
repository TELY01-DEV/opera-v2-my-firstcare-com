// Opera Panel Database Optimization Script
// Generated automatically based on performance analysis
// Created: 2025-07-07T13:56:30.138898

print('🚀 Starting database optimization...');

// Full-text search index for name and address fields
print('📇 Creating index: Full-text search index for name and address fields...');
db.organizations.createIndex({"name.th": "text", "name.en": "text", "formatted_address": "text"});
print('✅ Index created successfully');

// Compound index for status + province filtering
print('📇 Creating index: Filter active hospitals by province...');
db.organizations.createIndex({is_active: 1, province_code: 1});
print('✅ Index created successfully');

// Compound index for status + district filtering
print('📇 Creating index: Filter active hospitals by district...');
db.organizations.createIndex({is_active: 1, district_code: 1});
print('✅ Index created successfully');

// Geospatial index with status for location-based queries
print('📇 Creating index: Find active hospitals near location...');
db.organizations.createIndex({location: "2dsphere", is_active: 1});
print('✅ Index created successfully');

print('🎉 Database optimization completed!');