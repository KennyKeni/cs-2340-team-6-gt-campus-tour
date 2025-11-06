import requests
from typing import List, Dict, Any, Optional
from django.conf import settings


class RouteCalculationError(Exception):
    pass


def calculate_route_segments(stops: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    if not stops or len(stops) < 2:
        return None

    api_key = settings.GOOGLE_MAP_API_KEY
    if not api_key:
        raise RouteCalculationError("Google Maps API key not configured")

    segments = []

    for i in range(len(stops) - 1):
        origin = stops[i]
        destination = stops[i + 1]

        origin_coords = f"{origin['latitude']},{origin['longitude']}"
        destination_coords = f"{destination['latitude']},{destination['longitude']}"

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': origin_coords,
            'destination': destination_coords,
            'mode': 'walking',
            'key': api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK':
                raise RouteCalculationError(f"Directions API error: {data.get('status')}")

            if not data.get('routes'):
                raise RouteCalculationError("No routes returned from Directions API")

            route = data['routes'][0]
            leg = route['legs'][0]

            segment = {
                'segment_index': i,
                'origin': {
                    'location_id': origin['id'],
                    'name': origin['name'],
                    'lat': origin['latitude'],
                    'lng': origin['longitude']
                },
                'destination': {
                    'location_id': destination['id'],
                    'name': destination['name'],
                    'lat': destination['latitude'],
                    'lng': destination['longitude']
                },
                'distance': leg.get('distance', {}).get('text', ''),
                'duration': leg.get('duration', {}).get('text', ''),
                'polyline': route.get('overview_polyline', {}).get('points', ''),
                'steps': [
                    {
                        'distance': step.get('distance', {}).get('text', ''),
                        'duration': step.get('duration', {}).get('text', ''),
                        'instruction': step.get('html_instructions', ''),
                        'polyline': step.get('polyline', {}).get('points', '')
                    }
                    for step in leg.get('steps', [])
                ]
            }

            segments.append(segment)

        except requests.RequestException as e:
            raise RouteCalculationError(f"Failed to fetch directions: {str(e)}")

    return segments
