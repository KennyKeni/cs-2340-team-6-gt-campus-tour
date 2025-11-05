"""
Script to add sample Georgia Tech campus locations to the database.
Run with: python manage.py shell < add_locations.py
"""
from campus.models import Location

# Sample Georgia Tech locations
locations_data = [
    {
        'name': 'Tech Tower',
        'description': 'The iconic centerpiece of Georgia Tech campus, housing administrative offices.',
        'historical_info': 'Built in 1888, Tech Tower is the oldest building on campus and a beloved landmark.',
        'latitude': 33.7756,
        'longitude': -84.3985,
        'address': '225 North Ave NW, Atlanta, GA 30332',
        'category': 'Historic Building',
    },
    {
        'name': 'Bobby Dodd Stadium',
        'description': 'Home of Georgia Tech Yellow Jackets football team.',
        'historical_info': 'Opened in 1913, one of the oldest stadiums in college football.',
        'latitude': 33.7726,
        'longitude': -84.3920,
        'address': '150 Bobby Dodd Way NW, Atlanta, GA 30332',
        'category': 'Athletics',
    },
    {
        'name': 'Klaus Advanced Computing Building',
        'description': 'State-of-the-art facility for computer science and computational research.',
        'historical_info': 'Opened in 2006, named after Chris Klaus, founder of Internet Security Systems.',
        'latitude': 33.7771,
        'longitude': -84.3960,
        'address': '266 Ferst Dr NW, Atlanta, GA 30332',
        'category': 'Academic',
    },
    {
        'name': 'Student Center',
        'description': 'Hub of student life with dining, bookstore, and meeting spaces.',
        'historical_info': 'Renovated in 2010 to provide modern amenities for student activities.',
        'latitude': 33.7744,
        'longitude': -84.3987,
        'address': '350 Ferst Dr NW, Atlanta, GA 30332',
        'category': 'Student Services',
    },
    {
        'name': 'Georgia Tech Library',
        'description': 'The main library with extensive study spaces and resources.',
        'historical_info': 'Price Gilbert Memorial Library has served students since 1953.',
        'latitude': 33.7747,
        'longitude': -84.3963,
        'address': '704 Cherry St NW, Atlanta, GA 30332',
        'category': 'Academic',
    },
    {
        'name': 'Clough Undergraduate Learning Commons',
        'description': 'Modern collaborative learning space with innovative technology.',
        'historical_info': 'Opened in 2011 as a cutting-edge facility for undergraduate education.',
        'latitude': 33.7753,
        'longitude': -84.3966,
        'address': '266 4th St NW, Atlanta, GA 30332',
        'category': 'Academic',
    },
    {
        'name': 'McCamish Pavilion',
        'description': 'Home arena for Georgia Tech basketball and volleyball teams.',
        'historical_info': 'Renovated and reopened in 2012, replacing Alexander Memorial Coliseum.',
        'latitude': 33.7804,
        'longitude': -84.3926,
        'address': '965 Fowler St NW, Atlanta, GA 30332',
        'category': 'Athletics',
    },
    {
        'name': 'Campus Recreation Center',
        'description': 'Comprehensive fitness and recreation facility for students and staff.',
        'historical_info': 'The CRC opened in 1996 and has been a cornerstone of campus wellness.',
        'latitude': 33.7758,
        'longitude': -84.4032,
        'address': '750 Ferst Dr NW, Atlanta, GA 30332',
        'category': 'Recreation',
    },
]

# Add locations to database
created_count = 0
updated_count = 0

for loc_data in locations_data:
    location, created = Location.objects.get_or_create(
        name=loc_data['name'],
        defaults=loc_data
    )
    if created:
        created_count += 1
        print(f"✓ Created: {location.name}")
    else:
        updated_count += 1
        print(f"• Already exists: {location.name}")

print(f"\n✅ Done! Created {created_count} new locations, {updated_count} already existed.")
print(f"Total locations in database: {Location.objects.count()}")
