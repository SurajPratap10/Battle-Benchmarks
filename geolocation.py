"""
Geolocation utilities for tracking test locations
"""
import requests
from typing import Dict, Optional
import json

class GeolocationService:
    """Service to get geolocation information"""
    
    def __init__(self):
        self.cache = {}
    
    def get_location(self) -> Dict[str, str]:
        """
        Get current geolocation based on IP address
        Uses ipapi.co for geolocation (free, no API key needed)
        """
        
        # Check cache first
        if 'location' in self.cache:
            return self.cache['location']
        
        try:
            # Try ipapi.co first (free, accurate, no API key)
            response = requests.get('https://ipapi.co/json/', timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                
                location = {
                    'country': data.get('country_name', 'Unknown'),
                    'country_code': data.get('country_code', 'XX'),
                    'region': data.get('region', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': str(data.get('latitude', 0)),
                    'longitude': str(data.get('longitude', 0)),
                    'timezone': data.get('timezone', 'UTC'),
                    'ip': data.get('ip', 'Unknown')
                }
                
                # Cache the result
                self.cache['location'] = location
                return location
        
        except Exception as e:
            print(f"Primary geolocation service failed: {e}")
        
        # Fallback to ip-api.com (free, no API key)
        try:
            response = requests.get('http://ip-api.com/json/', timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                
                location = {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'XX'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': str(data.get('lat', 0)),
                    'longitude': str(data.get('lon', 0)),
                    'timezone': data.get('timezone', 'UTC'),
                    'ip': data.get('query', 'Unknown')
                }
                
                # Cache the result
                self.cache['location'] = location
                return location
        
        except Exception as e:
            print(f"Fallback geolocation service failed: {e}")
        
        # Return default if all services fail
        return {
            'country': 'Unknown',
            'country_code': 'XX',
            'region': 'Unknown',
            'city': 'Unknown',
            'latitude': '0',
            'longitude': '0',
            'timezone': 'UTC',
            'ip': 'Unknown'
        }
    
    def get_location_string(self) -> str:
        """Get location as a formatted string"""
        location = self.get_location()
        
        parts = []
        if location['city'] != 'Unknown':
            parts.append(location['city'])
        if location['region'] != 'Unknown' and location['region'] != location['city']:
            parts.append(location['region'])
        if location['country'] != 'Unknown':
            parts.append(location['country'])
        
        if parts:
            return ', '.join(parts)
        return 'Unknown'
    
    def get_country_flag(self, country_code: str = None) -> str:
        """Get country flag emoji from country code"""
        if country_code is None:
            location = self.get_location()
            country_code = location['country_code']
        
        if country_code == 'XX' or country_code == 'Unknown':
            return '🌍'
        
        # Convert country code to flag emoji
        # Each letter is converted to its regional indicator symbol
        try:
            flag = ''.join(chr(ord(c) + 127397) for c in country_code.upper())
            return flag
        except:
            return '🌍'

# Global instance
geo_service = GeolocationService()

