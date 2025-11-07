import logging
import requests
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class RouteCalculationError(Exception):
    pass


def calculate_route_segments(stops: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    if not stops or len(stops) < 2:
        logger.warning("calculate_route_segments called with less than 2 stops")
        return None

    api_key = settings.GOOGLE_MAP_API_KEY
    if not api_key:
        logger.error("Google Maps API key not configured in settings")
        raise RouteCalculationError("Google Maps API key not configured")

    logger.info(f"Calculating route segments for {len(stops)} stops")
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
            logger.debug(f"Requesting route from {origin_coords} to {destination_coords}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK':
                error_msg = f"Directions API error: {data.get('status')}"
                if data.get('error_message'):
                    error_msg += f" - {data.get('error_message')}"
                logger.error(error_msg)
                raise RouteCalculationError(error_msg)

            if not data.get('routes'):
                logger.error("No routes returned from Directions API")
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
            logger.debug(f"Successfully calculated segment {i+1} of {len(stops)-1}")

        except requests.RequestException as e:
            error_msg = f"Failed to fetch directions: {str(e)}"
            logger.error(error_msg)
            raise RouteCalculationError(error_msg)

    logger.info(f"Successfully calculated {len(segments)} route segments")
    return segments
