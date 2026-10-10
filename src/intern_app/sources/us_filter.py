"""Whether a location is in the US or remote. Everything else is dropped.

The repo sources are worldwide, and a listing in Singapore is noise for a US
search, so this runs before anything is stored.

Two rules shape the implementation, both learned the hard way:

Markers are matched on **word boundaries**, never as substrings. Matching "uk"
anywhere dropped Milwaukee, Waukegan and Tukwila; "india" dropped Indianapolis;
"mexico" dropped every New Mexico role.

Where the two error directions conflict, this errs toward **keeping** a
listing. A German role slipping onto the board costs one glance; silently
dropping every Indianapolis job costs real opportunities. So a foreign city
whose name also belongs to a US town — Dublin, Paris, Athens, Vienna, Moscow
and two dozen more — is **not** a marker at all: those rely on the
country name instead, which these lists almost always include ("Dublin,
Ireland", "London, United Kingdom"). The known residual risk is "City, DE"
strings, where a foreign country's two-letter code is also a state
abbreviation (DE, IN, CA, IL, OR, MA).
"""

from __future__ import annotations

import re

# fmt: off
STATE_CODES = frozenset((
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC", "PR",
))

# Multi-word names matter: without them "New York" and "North Carolina" were
# dropped unless the string happened to carry a state code too.
STATE_NAMES = (
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois",
    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
    "massachusetts", "michigan", "minnesota", "mississippi", "missouri",
    "montana", "nebraska", "nevada", "ohio", "oklahoma", "oregon",
    "pennsylvania", "tennessee", "texas", "utah", "vermont", "virginia",
    "washington", "wisconsin", "wyoming",
    "new york", "new jersey", "new hampshire", "new mexico", "north carolina",
    "south carolina", "north dakota", "south dakota", "west virginia",
    "rhode island", "puerto rico",
)

# Cities that routinely appear with no state at all in these lists.
US_CITIES = (
    "new york city", "nyc", "san francisco", "sf bay area", "bay area",
    "seattle", "boston", "chicago", "austin", "atlanta", "denver", "dallas",
    "houston", "philadelphia", "phoenix", "san diego", "san jose", "los angeles",
    "mountain view", "palo alto", "sunnyvale", "santa clara", "redmond",
    "bellevue", "cupertino", "menlo park", "cambridge", "pittsburgh",
    "minneapolis", "detroit", "miami", "orlando", "tampa", "charlotte",
    "raleigh", "durham", "nashville", "columbus", "cleveland", "cincinnati",
    "kansas city", "st louis", "salt lake city", "portland", "sacramento",
    "irvine", "el segundo", "brooklyn", "manhattan", "arlington", "reston",
    "mclean", "bethesda", "baltimore", "newark", "jersey city", "hoboken",
    "stamford", "greenwich", "princeton", "ann arbor", "madison", "boulder",
)
# fmt: on

COUNTRY_WORDS = ("united states", "usa", "u s a", "us", "us only", "nationwide", "stateside")
REMOTE_WORDS = ("remote", "anywhere", "distributed", "work from home", "wfh", "virtual")

# Full country and region names. Two-letter codes are deliberately absent: half
# of them collide with US state abbreviations.
FOREIGN_MARKERS = (
    "united kingdom",
    "england",
    "scotland",
    "wales",
    "canada",
    "ontario",
    "quebec",
    "british columbia",
    "india",
    "singapore",
    "germany",
    "france",
    "ireland",
    "australia",
    "japan",
    "china",
    "netherlands",
    "israel",
    "brazil",
    "mexico city",
    "spain",
    "italy",
    "poland",
    "sweden",
    "switzerland",
    "belarus",
    "ukraine",
    "korea",
    "taiwan",
    "hong kong",
    "philippines",
    "vietnam",
    "indonesia",
    "malaysia",
    "thailand",
    "turkey",
    "egypt",
    "nigeria",
    "kenya",
    "south africa",
    "argentina",
    "chile",
    "colombia",
    "peru",
    "portugal",
    "austria",
    "denmark",
    "norway",
    "finland",
    "iceland",
    "greece",
    "romania",
    "hungary",
    "czechia",
    "czech republic",
    "slovakia",
    "bulgaria",
    "serbia",
    "croatia",
    "slovenia",
    "estonia",
    "latvia",
    "lithuania",
    "uae",
    "dubai",
    "abu dhabi",
    "saudi arabia",
    "qatar",
    "pakistan",
    "bangladesh",
    "sri lanka",
    "nepal",
    "new zealand",
    "emea",
    "apac",
    "latam",
    "uk",
    "eu",
    "international",
    "london",
    "toronto",
    "vancouver",
    "montreal",
    "bangalore",
    "bengaluru",
    "hyderabad",
    "mumbai",
    "delhi",
    "pune",
    "chennai",
    "gurgaon",
    "noida",
    "tokyo",
    "osaka",
    "seoul",
    "shanghai",
    "beijing",
    "shenzhen",
    "taipei",
    "sydney",
    "melbourne",
    "brisbane",
    "auckland",
    "munich",
    # Berlin NH exists but is tiny; a bare "Berlin" means Germany in practice.
    "berlin",
    "frankfurt",
    "amsterdam",
    "rotterdam",
    "zurich",
    "krakow",
    "istanbul",
    "tel aviv",
    "lagos",
    "nairobi",
    "johannesburg",
    "cape town",
    "sao paulo",
    "mexico city",
    "buenos aires",
    "santiago",
    "bogota",
    "manila",
    "jakarta",
    "bangkok",
    "kuala lumpur",
    "ho chi minh",
    "hanoi",
    "karachi",
    "lahore",
    "dhaka",
    "colombo",
    "guadalajara",
    "monterrey",
    "ottawa",
    "calgary",
    "waterloo, on",
    "tbilisi",
)


def _has_word(text: str, phrase: str) -> bool:
    """Whether `phrase` appears in `text` as whole words.

    This is the fix for the substring bug: "uk" must not match Milwaukee.
    """
    return re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", text) is not None


def is_us_or_remote(location: str) -> bool:
    """True when a location reads as US-based or remote."""
    if not location:
        # No location at all is kept: these lists often omit it for remote
        # roles, and dropping them loses real listings.
        return True

    text = " ".join(location.lower().replace(".", " ").split())

    # A named foreign country or city wins over everything, so "Remote - India"
    # and "London, Ontario" are both out.
    if any(_has_word(text, marker) for marker in FOREIGN_MARKERS):
        return False

    if any(_has_word(text, word) for word in COUNTRY_WORDS):
        return True
    if any(_has_word(text, word) for word in REMOTE_WORDS):
        return True
    if any(_has_word(text, name) for name in STATE_NAMES):
        return True
    if any(_has_word(text, city) for city in US_CITIES):
        return True

    # A state abbreviation, which must be uppercase in the original string:
    # lowercase "in" and "or" are ordinary English words.
    codes = set(re.findall(r"(?<![A-Za-z])([A-Z]{2})(?![A-Za-z])", location))
    return bool(codes & STATE_CODES)
