from decimal import Decimal

from django.core.management.base import BaseCommand

from campus.models import Location


class Command(BaseCommand):
    help = 'Seeds the database with Georgia Tech campus locations'

    def handle(self, *args, **options):
        self.stdout.write('Seeding campus locations...')

        from decimal import Decimal

        landmarks = [
            {
                'name': 'Tech Tower',
                'slug': 'tech-tower',
                'description': (
                    'Built in 1888, Tech Tower is one of Georgia Tech\'s oldest buildings '
                    'and is home to the iconic TECH signs that overlook campus.'
                ),
                'historical_info': (
                    'Officially known as the Lettie Pate Whitehead Evans Administration Building, Tech Tower '
                    'was completed in 1888 as the Academic Building and is the second edifice completed on the '
                    'Georgia Tech campus. It is the oldest surviving building at Georgia Tech. Originally '
                    'erected with two towers, the second tower burned in 1892 and was never replaced. '
                    'The building stands 145 feet tall from ground floor to the top of the tower finial. '
                    '\n\n'
                    'The iconic "TECH" letters were first installed on all four sides of the tower in 1918 by '
                    'the class of 1922, intended "to light the spirit of Tech to the four points of the compass." '
                    'These original letters were made of wood and painted in the school\'s white and gold colors. '
                    'The letters were first lighted in the 1930s when light bulbs were added to their faces, '
                    'and they have been outlined in neon since the 1950s. Each letter stands approximately '
                    'four to five feet tall. '
                    '\n\n'
                    'The tradition of stealing the "T" began in April 1969 when a secret group of students '
                    'calling themselves the "Magnificent Seven" planned the theft to commemorate Institute '
                    'President Edwin D. Harrison\'s retirement. The students were inspired by a similar prank '
                    'at Harvard University in 1968. The stolen "T" was returned several days later via '
                    'helicopter at the behest of Atlanta mayor Ivan Allen. Over the decades, the "T" has been '
                    'successfully stolen several times, with the most recent successful theft occurring during '
                    'spring break on March 18, 2014. '
                    '\n\n'
                    'After a visitor was accidentally killed while climbing the Alexander Memorial Coliseum in '
                    '1999, President G. Wayne Clough banned the stealing of the "T" due to safety concerns and '
                    'potential liability. Security features including pressure-sensitive roof tiling, fiber '
                    'optic cabling running throughout the letters, cameras, and an audible alarm system have '
                    'been installed to prevent theft. The tradition technically refers only to stealing the "T" '
                    'from Tech Tower, not other signage around campus. The building is part of the Georgia '
                    'Institute of Technology Historic District and serves as the architectural anchor and '
                    'focal point of the central campus.'
                ),
                'latitude': Decimal('33.772356'),
                'longitude': Decimal('-84.394839'),
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
                'historical_info': (
                    'The G. Wayne Clough Undergraduate Learning Commons (commonly known as Clough Commons or CULC) '
                    'opened in August 2011 after more than 10 years of planning and development. The facility was '
                    'developed in response to the rapid growth of Georgia Tech\'s student body and became the '
                    'institute\'s highest capital priority during President G. Wayne Clough\'s tenure. '
                    '\n\n'
                    'The building is named in honor of President Emeritus G. Wayne Clough, who served as Georgia '
                    'Tech\'s president and championed undergraduate education during his tenure. The naming was '
                    'requested in June 2008 by Campaign Georgia Tech, the institute\'s fundraising arm, to honor '
                    'Clough\'s commitment to undergraduate education and ensure future students appreciate the '
                    'Clough legacy. '
                    '\n\n'
                    'Construction cost $93.7 million, with $60 million provided by the State of Georgia and the '
                    'remainder from private funding. The formal groundbreaking took place on April 5, 2010, with '
                    'G. Wayne Clough, Institute President G.P. "Bud" Peterson, and University System of Georgia '
                    'Chancellor Erroll B. Davis present. Construction was undertaken by Turner Construction and '
                    'completed in August 2011. The building opened to the Georgia Tech community on August 20, 2011. '
                    '\n\n'
                    'The five-story, 220,000 square-foot building was designed by Bohlin Cywinski Jackson, with '
                    'facility programming completed by Perry Dean Rogers Architects and Houser Walker Architecture. '
                    'The building is physically connected to the Georgia Tech Library on two levels and is managed '
                    'by the Library. It is located on a slope between Tech Green and the Library, providing views '
                    'of green space and the Kessler Campanile. The site was previously a parking lot. '
                    '\n\n'
                    'The Clough Commons houses 41 classrooms, two 300-seat auditoriums, presentation rehearsal '
                    'studios, and all first-year laboratories in biology, physics, chemistry, and environmental/'
                    'atmospheric science. It also contains tutoring services, undergraduate writing assistance, '
                    'academic advising, and the Office of Information Technology. The building features a Kaldi\'s '
                    'Coffee outlet on the second floor, art exhibit space, and an 18,000-square-foot rooftop garden '
                    'with native plants. '
                    '\n\n'
                    'Built with LEED certification in mind, the building contains extensive sustainability features '
                    'including a rooftop solar panel array with an 85-kilowatt capacity capable of producing 118 '
                    'megawatt-hours annually, a 1.4-million-gallon cistern for water harvesting, water-efficient '
                    'landscaping using native plants, and smart lighting techniques with daylight harvesting and '
                    'motion sensors. The solar panels were supplied by Suniva, a local manufacturing company started '
                    'by a Georgia Tech professor. In August 2012, the building was used as a major set piece for '
                    'the 2013 film "The Internship," staged as a building within the Googleplex.'
                ),
                'latitude': Decimal('33.774413'),
                'longitude': Decimal('-84.396575'),
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
                    'Bobby Dodd Stadium at Historic Grant Field is the oldest continuously used on-campus site '
                    'for college football in Division I FBS. Football has been played at the current site since '
                    '1905, with permanent grandstands first constructed in 1913, mostly by Georgia Tech students. '
                    'The stadium opened on September 27, 1913, with Georgia Tech defeating Fort McPherson 19-0. '
                    'The original facility, corresponding roughly to the lower level of the current west grandstands, '
                    'seated only 5,600. '
                    '\n\n'
                    'The stadium was originally named Grant Field in honor of Hugh Inman Grant, son of John W. Grant, '
                    'a well-known Atlanta merchant and original benefactor of the stadium. The facility was built at '
                    'an initial cost of $15,000. Within six years of opening, capacity grew from 7,000 to 25,000. '
                    'The first major additions came in 1924 and 1925 when stands on the east and south sides were '
                    'constructed, increasing capacity to 30,000. By the 1947 season, the original west stands were '
                    'rebuilt with a press box, pushing capacity to 40,000. '
                    '\n\n'
                    'The north stands were built in 1958, a second deck was constructed in 1962 on the east side, '
                    'and by 1967 the west side was built, boosting seating capacity to 58,121. In 1971, Georgia '
                    'Tech replaced the grass field with Astroturf. Throughout the 1980s, new scoreboards were '
                    'installed in 1982, and the south stands were demolished in 1985 to make room for the William C. '
                    'Wardlaw Center, a modern field house and athletic office facility, reducing capacity to 46,000. '
                    '\n\n'
                    'In 1988, the stadium was renamed Bobby Dodd Stadium in honor of legendary coach Bobby Dodd, '
                    'who has the most wins of any coach in Georgia Tech history. The playing surface retained the '
                    'name Grant Field and is now known as Hyundai Field following a 20-year, $55 million naming '
                    'rights deal announced in August 2023. '
                    '\n\n'
                    'Following the 2001 season, a major $75 million expansion and renovation project began, split '
                    'into two phases to allow the 2002 season to be played in the stadium. The first phase returned '
                    'seating to the south end in front of the Wardlaw Center and rebuilt the original north stands '
                    'and lower east bleachers. After the 2002 season, phase two was completed by adding a massive '
                    'free-standing upper deck in the north end zone, bringing capacity to 55,000. '
                    '\n\n'
                    'The stadium has hosted numerous memorable games, including the most lopsided game in American '
                    'football history on October 7, 1916, when Georgia Tech defeated Cumberland College 222-0 under '
                    'legendary coach John Heisman. On November 17, 1962, Georgia Tech upset #1 Alabama 7-6, ending '
                    'the Crimson Tide\'s 26-game unbeaten streak. On November 6, 1976, Georgia Tech defeated #11 '
                    'Notre Dame 23-14 without throwing a single forward pass. '
                    '\n\n'
                    'The stadium also served as a venue for the 1996 Summer Olympics and has hosted events beyond '
                    'football. Grant Field was used for an Atlanta Falcons game on October 5, 1969, and served as '
                    'home field for the Atlanta Apollos of the North American Soccer League in 1973. In August 1984, '
                    'it hosted the annual Drum Corps International World Championships. '
                    '\n\n'
                    'In summer 2020, the playing surface was replaced with Legion NXT synthetic turf by Shaw Sports, '
                    'and the stadium received a new sound system, LED lights, rebranded signage, and renovated '
                    'restrooms. In 2024, sections 217-219 were partially removed to accommodate the new Fanning Center, '
                    'a 100,000-square-foot facility in the northeast corner, reducing capacity from 55,000 to 51,913. '
                    'In October 2024, "Full Steam Ahead," a $500 million expansion and renovation project was announced, '
                    'approved by the Board of Regents in May 2025, with construction set to begin in Fall 2026 and '
                    'conclude in 2027. The stadium remains a cornerstone of college football and has been the site of '
                    'more home wins than any other FBS stadium.'
                ),
                'latitude': Decimal('33.772445'),
                'longitude': Decimal('-84.392805'),
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
                'historical_info': (
                    'Price Gilbert Memorial Library serves as Georgia Tech\'s main library and is a central '
                    'hub for academic research and student learning. The 217,652 square-foot facility houses '
                    'extensive collections, study spaces, and research support services that serve the entire '
                    'Georgia Tech community. '
                    '\n\n'
                    'The library is physically connected to the Clough Undergraduate Learning Commons on two '
                    'levels, creating an integrated learning environment. The Library manages both facilities '
                    'and provides comprehensive services including research assistance, tutoring, academic '
                    'advising, and access to extensive digital and physical collections. '
                    '\n\n'
                    'The building features multiple floors of study spaces designed to accommodate different '
                    'learning styles, from quiet individual study areas to collaborative group spaces. The '
                    'first floor includes a Blue Donkey Coffee location, providing a convenient meeting point '
                    'and refreshment option for students, faculty, and staff. '
                    '\n\n'
                    'The library\'s collections support research across all disciplines taught at Georgia Tech, '
                    'with particular strength in engineering, computing, sciences, and technology. Modern '
                    'technological infrastructure supports digital scholarship and provides access to vast '
                    'online databases and resources. '
                    '\n\n'
                    'Operating hours are extensive to accommodate student needs, with the facility open late '
                    'during the academic year. The library staff includes subject librarians who provide '
                    'specialized research support in various disciplines, helping students and faculty navigate '
                    'complex research projects and locate appropriate resources. '
                    '\n\n'
                    'Contact information: Tel: (404) 894-4500 or 1-888-225-7804. The library continues to '
                    'evolve to meet the changing needs of the Georgia Tech community, incorporating new '
                    'technologies and learning approaches while maintaining its core mission of supporting '
                    'academic excellence and research innovation.'
                ),
                'latitude': Decimal('33.7746'),
                'longitude': Decimal('-84.3961'),
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
                'historical_info': (
                    'The Kendeda Building for Innovative Sustainable Design represents a landmark achievement in '
                    'regenerative architecture and sustainable building design. In September 2015, Georgia Tech '
                    'received a $30 million grant from the Kendeda Fund for the purposes of building a green '
                    'building on campus - the single largest donation ever made by the Kendeda Fund and one of '
                    'the largest grants ever received by the institute. '
                    '\n\n'
                    'Construction began in 2017 on what was previously a parking lot, located on the northwest '
                    'corner of Ferst Drive and State Street. The building was designed by architectural firms '
                    'Lord Aeck Sargent and Miller Hull with 100% funding for design and construction from the '
                    'Kendeda Fund. The project was designed to meet the rigorous standards of the Living Building '
                    'Challenge, the world\'s most ambitious green building certification program. '
                    '\n\n'
                    'The building opened in late September 2019 and achieved Living Building Challenge certification '
                    'in March 2021, becoming the first certified Living Building in Georgia, the 28th in the world, '
                    'and the first Living Building Challenge-certified academic building in the Southeastern United '
                    'States. Unlike traditional green buildings that focus on reducing harm, the Kendeda Building '
                    'is regenerative, meaning it gives back more than it consumes. '
                    '\n\n'
                    'Even before completion, the building received significant recognition. In October 2018, the '
                    'Atlanta Better Buildings Challenge presented it with its annual Game Changer Award. In November '
                    '2019, it received a "Development of Excellence" award from the Atlanta Regional Commission. '
                    'In October 2020, the Metro Atlanta Chamber selected it for its annual E3 Award, recognizing '
                    'it as one of the region\'s most innovative projects at the intersection of sustainability and '
                    'commerce. In 2021, the building received the American Institute of Architects COTE Top Ten '
                    'Award, the architecture industry\'s best-known award program for sustainable design excellence. '
                    '\n\n'
                    'The building\'s design follows regenerative principles and mimics the hydrological flow of the '
                    'area while reintroducing vegetation and biology native to the Piedmont Forest ecosystem. The '
                    'site moderately slopes from south to north, and the building terraces down to follow this '
                    'natural topography. The approximately 5,000-square-foot rooftop garden features a honeybee '
                    'apiary, pollinator garden, blueberry orchard, and laboratory, satisfying the Urban Agriculture '
                    'Imperative requirement while offering curriculum and research opportunities through the Georgia '
                    'Tech Urban Honey Bee Project. '
                    '\n\n'
                    'The building demonstrates exceptional sustainable practices, including net positive waste '
                    'construction. Materials were salvaged from iconic Georgia Tech buildings and incorporated into '
                    'the Kendeda Building - slate roof tiles from the former Alumni House became bathroom tiles, '
                    'and wood from the 2017 renovations of Tech Tower (erected in 1888) became stair treads in the '
                    'common area, saving $60,000 compared to purchasing new materials. '
                    '\n\n'
                    'As a multi-disciplinary, non-departmental education building, the Kendeda Building welcomes '
                    'the broadest cross-section of students rather than focusing on one subject. The 176-seat '
                    'auditorium provides maximum flexibility for teaching intro-level classes in varied topics from '
                    'economics to chemistry to calculus. The building is open to the public and offers guided tours, '
                    'self-guided visits, and a virtual 3D tour, serving as a living laboratory for sustainability '
                    'and innovation. The Kendeda Building will be part of Georgia Tech\'s larger Eco-Commons, a '
                    'passive recreation and high-performance landscape that also replaces surface parking, '
                    'demonstrating the institute\'s commitment to campus-wide sustainability.'
                ),
                'latitude': Decimal('33.778616'),
                'longitude': Decimal('-84.399565'),
                'address': '422 Ferst Dr NW, Atlanta, GA 30332',
                'category': 'Sustainability',
            },
            {
                'name': 'John Lewis Student Center',
                'slug': 'john-lewis-student-center',
                'description': (
                    'Recently renovated student center featuring dining, event venues, and gathering '
                    'spaces for campus organizations.'
                ),
                'historical_info': (
                    'The John Lewis Student Center, formerly known as the Student Center, was renamed in honor '
                    'of distinguished civil rights advocate and Congressman John Lewis, who died in July 2020. '
                    'The renaming was unveiled by Georgia Tech to honor Lewis\'s legacy and his lifelong commitment '
                    'to civil rights, social justice, and service to the community. Lewis was a towering figure '
                    'in American history, known for his role in the Civil Rights Movement, his leadership of the '
                    'Student Nonviolent Coordinating Committee (SNCC), his participation in the Freedom Rides, '
                    'and his pivotal role in the 1965 Selma to Montgomery marches, particularly his injuries on '
                    '"Bloody Sunday" at the Edmund Pettus Bridge. He served as the U.S. Representative for '
                    'Georgia\'s 5th congressional district for over three decades. '
                    '\n\n'
                    'The student center underwent major renovation and expansion as part of Georgia Tech\'s '
                    'commitment to providing world-class facilities for student life. The renovated facility '
                    'stands as the central hub on Georgia Tech\'s campus, offering some of the most stunning '
                    'views of Midtown Atlanta. It has become a cherished gathering place for students to convene, '
                    'socialize, and participate in numerous activities. '
                    '\n\n'
                    'The John Lewis Student Center and adjacent Stamps Commons encompasses multiple facilities '
                    'and services spread across several floors. The building houses two theaters - the Walter G. '
                    'Ehmer Theater (Atlantic) and another performance space - along with eight meeting rooms '
                    'available for reservation by Georgia Tech student organizations, departments, and external '
                    'clients. In addition to indoor spaces, the Student Center Event Services team manages '
                    'reservations for outdoor spaces adjacent to the Student Center, including the Experiential '
                    'Pathway, Tech Green, and Koan Plaza. '
                    '\n\n'
                    'The second floor features an Information Desk that provides comprehensive services including '
                    'information about events, building services, directions around campus, lost and found services, '
                    'and day locker rentals. The Information Desk can be contacted at 404.385.4275. The second '
                    'floor also houses the DePoe Eye Center, which offers eye care services including eye exams '
                    'and eyewear to the Georgia Tech community during weekday hours. '
                    '\n\n'
                    'The third floor hosts the Student Center Administrative Office, which provides limited notary '
                    'services to Georgia Tech students, faculty, and staff (by appointment, Monday-Friday, 9am-4pm). '
                    'The Center for Student Engagement, which operates the John Lewis Student Leadership Pathways '
                    'program, is also located in Suite 3110 of the building. '
                    '\n\n'
                    'The first floor includes the Georgia Tech Post Office, serving all mailing needs for the '
                    'campus community. Students living on campus can access their virtual mailboxes and pick up '
                    'parcels at the package pick-up window. The Post Office operates cashless, accepting all major '
                    'credit cards. '
                    '\n\n'
                    'Tech Dining operates numerous food service options within the student center, bringing together '
                    'a diverse mix of both franchise and self-operated concepts to meet the varied tastes of Tech '
                    'students. Ten quick-service eateries and a coffee shop provide convenient dining options '
                    'throughout the day. Burdell\'s, operated by Barnes & Noble at Georgia Tech, serves as a one-stop '
                    'shop for Georgia Tech merchandise, school supplies, and snacks. '
                    '\n\n'
                    'The building features study nooks, meeting spots, and leisure areas designed to support '
                    'student success and community building. With its versatile and strategically placed location '
                    'on campus, the John Lewis Student Center embodies the values of community, leadership, and '
                    'service that John Lewis exemplified throughout his remarkable life. The building serves not '
                    'only as a functional space for student activities but also as a lasting tribute to Lewis\'s '
                    'enduring legacy and his connection to Atlanta and Georgia.'
                ),
                'latitude': Decimal('33.7740362'),
                'longitude': Decimal('-84.3990168'),
                'address': '351 Ferst Dr NW, Atlanta, GA 30332',
                'category': 'Student Life',
            },
            {
                'name': 'Ferst Center for the Arts',
                'slug': 'ferst-center-for-the-arts',
                'description': (
                    'A performing arts venue that hosts concerts, theater productions, and lectures.'
                ),
                'historical_info': (
                    'The Ferst Center for the Arts opened in April 1992, originally named the Georgia Tech '
                    'Theatre for the Arts. Located in the heart of the Georgia Tech campus at 349 Ferst Drive, '
                    'the facility was designed to serve as a showcase for the presentation of concerts, lectures, '
                    'dance, film, and theater, providing enriching opportunities for both Georgia Tech and the '
                    'greater Atlanta community. '
                    '\n\n'
                    'Shortly after its opening, the venue achieved national prominence when it hosted the vice '
                    'presidential debate between Al Gore, Dan Quayle, and James Stockdale on October 13, 1992, '
                    'during the 1992 presidential election campaign. This high-profile event brought significant '
                    'attention to the new facility and established it as a venue capable of hosting major national '
                    'events. '
                    '\n\n'
                    'The center was renamed the Ferst Center for the Arts in honor of Robert H. Ferst, a Georgia '
                    'Tech alumnus, following a $1 million donation by his widow, Jeanne Rolfe Ferst. This generous '
                    'contribution helped ensure the facility\'s continued operation and enhancement, cementing the '
                    'Ferst family\'s legacy within the Georgia Tech community. '
                    '\n\n'
                    'The main auditorium contains 950 seats and features a proscenium stage, orchestra pit, and '
                    'state-of-the-art theatrical lighting and sound systems. The theater auditorium includes stairs '
                    'to most seating rows, with accessible seating available in the Left Orchestra, Right Orchestra, '
                    'and an Accessible Seating Platform located in the Center Orchestra sections to accommodate '
                    'patrons with limited mobility. '
                    '\n\n'
                    'The Ferst Center is adjacent to DramaTech, Georgia Tech\'s student-run theater, which performs '
                    'in the James E. Dull Theatre within the Ferst Center complex. This proximity creates a vibrant '
                    'theatrical ecosystem that supports both professional productions and student performances. '
                    '\n\n'
                    'Today, the venue is filled with activity year-round. The Office of the Arts (Georgia Tech Arts) '
                    'operates the Ferst Center and presents the Arts@Tech Season of professional music, dance, and '
                    'theater performances from September through April. The Georgia Tech School of Music performs '
                    'several concerts at the Ferst Center throughout the year, and DramaTech stages multiple '
                    'productions annually. The Ferst Center is also available for rental, and performances by '
                    'student and community organizations are often open to the public. '
                    '\n\n'
                    'The Ferst Center Box Office manages ticket sales for all events and performances, including '
                    'those presented by Georgia Tech Arts, the School of Music, other Georgia Tech departments and '
                    'organizations, and off-campus organizations. The box office is generally open Monday through '
                    'Friday from 11:00 am to 5:00 pm, and opens one hour before showtime on performance days. '
                    'Tickets are available online anytime at tickets.arts.gatech.edu. Contact: 404.894.9600 or '
                    'tickets@arts.gatech.edu. '
                    '\n\n'
                    'The Georgia Tech Arts administrative office is located in the Charles Smithgall Student Services '
                    'Building at 353 Ferst Drive NW, Suite 141, with office hours Monday-Friday, 8am-5pm. The Ferst '
                    'Center is easily accessible via MARTA, with the Midtown station being the closest. Visitors can '
                    'take the complimentary Stinger Gold Route bus from Midtown station to campus, exiting at the '
                    'Clough Undergraduate Learning Commons stop and crossing Tech Green to reach the Ferst Center. '
                    '\n\n'
                    'Parking is available in several visitor areas on campus, with the most convenient being Visitors '
                    'Area 2 (Student Center Lot) directly in front of the Ferst Center and Visitors Area 3 (Student '
                    'Center Deck). The venue continues to serve as a cultural beacon for Georgia Tech and the Atlanta '
                    'community, presenting diverse programming that enriches campus life and connects the university '
                    'to the broader arts community. Over three decades after its opening, the Ferst Center remains '
                    'a vital hub for the performing arts, fostering creativity, cultural appreciation, and community '
                    'engagement.'
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
