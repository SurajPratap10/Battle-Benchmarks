# 🌍 Geolocation Feature

## Overview
Added accurate geolocation tracking to all benchmark results and tables throughout the application. The system automatically detects the user's location using IP-based geolocation APIs.

---

## ✅ Implementation Details

### 1. **Geolocation Service**
   - **File**: `geolocation.py`
   - **Primary API**: ipapi.co (free, no API key required)
   - **Fallback API**: ip-api.com (backup service)
   - **Caching**: Results cached for session duration
   
### 2. **Data Captured**
   - Country (with flag emoji)
   - Country Code (for flag display)
   - City
   - Region/State
   - Latitude & Longitude
   - Timezone
   - IP Address

### 3. **Database Schema**
   - Added columns to `benchmark_results` table:
     - `location_country`
     - `location_city`
     - `location_region`
   - Automatic migration for existing databases (ALTER TABLE)

### 4. **BenchmarkResult Dataclass**
   - Added fields:
     - `location_country: str`
     - `location_city: str`
     - `location_region: str`

---

## 📊 Geolocation Display in All Tables

### 1. **Quick Test Results**
   - Shows: `🇺🇸 City, Country`
   - Displays location for each test result

### 2. **Blind Test Comparison**
   - Shows: `🇺🇸 City, Country`
   - Location displayed in results comparison table

### 3. **Batch Benchmark Summary**
   - Shows: `🇺🇸 City, Country`
   - Current testing location displayed

### 4. **Leaderboard**
   - Shows: `🇺🇸 City, Country`
   - Current location for all rankings

### 5. **Provider Statistics**
   - Shows: `🇺🇸 City, Country`
   - Location context for statistics

### 6. **User Voting Statistics**
   - Shows: `🇺🇸 City, Country`
   - Location where votes were cast

### 7. **Export Preview**
   - Shows: `🇺🇸 City, Country`
   - Location included in export data

---

## 🎯 Features

### Flag Emoji Display
```python
🇺🇸 = United States
🇬🇧 = United Kingdom
🇮🇳 = India
🇩🇪 = Germany
🇫🇷 = France
🌍 = Unknown/Global
```

### Location Format
- **Full**: `🇺🇸 San Francisco, United States`
- **City Only**: `🇺🇸 San Francisco, USA`
- **Country Only**: `🇺🇸 United States`
- **Unknown**: `🌍 Unknown`

### Helper Functions
```python
# Get location display with flag
get_location_display(result)  # Returns: "🇺🇸 City, Country"

# Get country flag
geo_service.get_country_flag('US')  # Returns: "🇺🇸"

# Get location string
geo_service.get_location_string()  # Returns: "City, Region, Country"

# Get full location data
location = geo_service.get_location()
# Returns: {country, city, region, latitude, longitude, ...}
```

---

## 🔧 Technical Implementation

### 1. **Automatic Capture**
   - Location captured automatically during each test
   - Happens in `benchmarking_engine.run_single_test()`
   - No user interaction required

### 2. **Performance**
   - Results cached after first API call
   - 3-second timeout for API requests
   - Fallback to multiple APIs for reliability
   - Graceful degradation if APIs fail

### 3. **Privacy**
   - Uses public IP for location detection
   - No personal data collected
   - Location stored with test results only
   - IP address not stored in database

### 4. **Accuracy**
   - City-level accuracy in most cases
   - Country-level minimum guarantee
   - Updates automatically per session

---

## 📋 API Services Used

### Primary: ipapi.co
- **Free Tier**: 1,000 requests/day
- **No API Key**: Required
- **Accuracy**: High (city-level)
- **Data**: Comprehensive location data

### Fallback: ip-api.com
- **Free Tier**: 45 requests/minute
- **No API Key**: Required
- **Accuracy**: Good (city-level)
- **Data**: Standard location data

---

## 🎨 UI Integration

### Table Columns
All tables now include a "Location" column showing:
- Flag emoji for visual identification
- City and country name
- Formatted for readability

### Example Display
```
| Provider | Model          | Location                | Latency | ... |
|----------|----------------|------------------------|---------|-----|
| Deepgram | Deepgram Aura  | 🇺🇸 San Francisco, USA | 234ms   | ... |
| Murf     | Murf AI TTS v1 | 🇺🇸 San Francisco, USA | 456ms   | ... |
```

---

## 📊 Database Storage

### Schema
```sql
CREATE TABLE benchmark_results (
    ...
    location_country TEXT,
    location_city TEXT,
    location_region TEXT,
    ...
);
```

### Query Example
```python
# Get results by location
SELECT * FROM benchmark_results 
WHERE location_country = 'United States' 
AND location_city = 'San Francisco';
```

---

## 🚀 Usage

### Automatic
- No configuration needed
- Works out of the box
- Location detected on first test
- Cached for session duration

### Manual (Advanced)
```python
from geolocation import geo_service

# Get current location
location = geo_service.get_location()
print(f"Testing from: {location['city']}, {location['country']}")

# Get formatted string
location_str = geo_service.get_location_string()
print(f"Location: {location_str}")

# Get flag
flag = geo_service.get_country_flag()
print(f"Flag: {flag}")
```

---

## ✅ Benefits

1. **Context**: Know where tests are run from
2. **Analysis**: Compare performance by region
3. **Debugging**: Identify location-specific issues
4. **Reporting**: Comprehensive location data in exports
5. **User Experience**: Visual flag emojis for quick identification
6. **Accuracy**: City-level precision in most cases

---

## 🔮 Future Enhancements

Potential additions:
1. **Regional Analysis**: Compare latency by geographic region
2. **Location Filtering**: Filter results by location
3. **Map Visualization**: Show test locations on world map
4. **ISP Detection**: Identify internet service provider
5. **Network Type**: Detect WiFi vs Mobile connection
6. **Time Zone Awareness**: Auto-adjust timestamps to local time

---

## 📝 Notes

- Location cached per session (browser refresh required for update)
- Fallback to "Unknown" if all APIs fail
- No impact on test performance (async API calls)
- Works globally without configuration
- Privacy-friendly (no personal data)

---

**Date Added**: October 1, 2025  
**Status**: ✅ Fully Integrated  
**Files Modified**: 4 (geolocation.py, app.py, benchmarking_engine.py, database.py)  
**Tables Updated**: 7 (All major tables)  
**API Endpoints**: 2 (ipapi.co, ip-api.com)

