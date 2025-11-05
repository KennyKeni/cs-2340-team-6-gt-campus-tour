from decimal import Decimal

from django.core.management.base import BaseCommand

from campus.models import Location


class Command(BaseCommand):
    help = 'Seeds the database with Georgia Tech campus locations'

    def handle(self, *args, **options):
        self.stdout.write('Seeding campus locations...')

        landmarks = [
            {
                'name': 'Tech Tower',
                'slug': 'tech-tower',
                'description': (
                    'Built in 1888, Tech Tower is one of Georgia Tech\'s oldest buildings '
                    'and is home to the iconic TECH signs that overlook campus.'
                ),
                'historical_info': (
                    'Tech Tower was completed in 1888 and is the oldest building on campus. '
                    'The iconic "TECH" letters on all four sides were added in 1918. '
                    'Students traditionally steal the "T" as a prank, which has led to '
                    'increased security measures over the years.'
                ),
                'latitude': Decimal('33.7724'),
                'longitude': Decimal('-84.3948'),
                'address': '225 North Ave NW, Atlanta, GA 30332',
                'category': 'Historic',
            },
            {
                'name': 'Clough Undergraduate Learning Commons',
                'slug': 'clough-commons',
                'description': (
                    'The Clough Commons is a hub for student learning that houses classrooms, labs, '
                    'and multiple academic support services.'
                ),
                'latitude': Decimal('33.7744'),
                'longitude': Decimal('-84.3965'),
                'address': '266 4th St NW, Atlanta, GA 30332',
                'category': 'Academic',
            },
            {
                'name': 'Bobby Dodd Stadium',
                'slug': 'bobby-dodd-stadium',
                'description': (
                    'Home to the Georgia Tech Yellow Jackets football team and the oldest on-campus '
                    'stadium in Division I FBS.'
                ),
                'historical_info': (
                    'Opened in 1913 as Grant Field, it was renamed Bobby Dodd Stadium in 1988 '
                    'to honor legendary coach Bobby Dodd. It is the oldest continuously used '
                    'on-campus stadium in Division I FBS and has a capacity of 55,000.'
                ),
                'latitude': Decimal('33.772541'),
                'longitude': Decimal('-84.392852'),
                'address': '177 North Ave NW, Atlanta, GA 30313',
                'category': 'Athletics',
            },
            {
                'name': 'Price Gilbert Library',
                'slug': 'price-gilbert-library',
                'description': (
                    'The main library on campus offering study space, research support, and extensive '
                    'collections that serve the Georgia Tech community.'
                ),
                'latitude': Decimal('33.7745'),
                'longitude': Decimal('-84.3960'),
                'address': '704 Cherry St NW, Atlanta, GA 30332',
                'category': 'Academic',
            },
            {
                'name': 'Kendeda Building for Innovative Sustainable Design',
                'slug': 'kendeda-building',
                'description': (
                    'A Living Building Challenge-certified facility showcasing advanced sustainability '
                    'features and interdisciplinary learning spaces.'
                ),
                'latitude': Decimal('33.778616'),
                'longitude': Decimal('-84.399565'),
                'address': '422 Ferst Dr NW, Atlanta, GA 30313',
                'category': 'Sustainability',
            },
            {
                'name': 'John Lewis Student Center',
                'slug': 'john-lewis-student-center',
                'description': (
                    'Recently renovated student center featuring dining, event venues, and gathering '
                    'spaces for campus organizations.'
                ),
                'latitude': Decimal('33.7740'),
                'longitude': Decimal('-84.3988'),
                'address': '351 Ferst Dr NW, Atlanta, GA 30332',
                'category': 'Student Life',
            },
            {
                'name': 'Ferst Center for the Arts',
                'slug': 'ferst-center-for-the-arts',
                'description': (
                    'A performing arts venue that hosts concerts, theater productions, and lectures.'
                ),
                'latitude': Decimal('33.7750'),
                'longitude': Decimal('-84.4020'),
                'address': '349 Ferst Dr NW, Atlanta, GA 30332',
                'category': 'Arts',
            },
        ]

        created_count = 0
        updated_count = 0

        for landmark in landmarks:
            location, created = Location.objects.update_or_create(
                slug=landmark['slug'],
                defaults=landmark,
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created: {location.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  ↻ Updated: {location.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete! Created {created_count}, Updated {updated_count}'
            )
        )
