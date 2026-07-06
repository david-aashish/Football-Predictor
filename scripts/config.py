# ==========================================================
# World Cup Qualification Windows
# ==========================================================

WORLD_CUPS = {
    2006: {
        "start": "2003-09-06",
        "end": "2005-11-16"
    },
    2010: {
        "start": "2007-08-25",
        "end": "2009-11-18"
    },
    2014: {
        "start": "2011-06-15",
        "end": "2013-11-20"
    },
    2018: {
        "start": "2015-03-12",
        "end": "2017-11-15"
    },
    2022: {
        "start": "2019-06-06",
        "end": "2022-06-14"
    }
}

# ==========================================================
# World Cup Hosts
# ==========================================================

HOSTS = {
    2006: ["Germany"],
    2010: ["South Africa"],
    2014: ["Brazil"],
    2018: ["Russia"],
    2022: ["Qatar"]
}

# ==========================================================
# Confederations
# ==========================================================

CONFEDERATIONS = {

    # UEFA
    "Germany": "UEFA",
    "England": "UEFA",
    "France": "UEFA",
    "Spain": "UEFA",
    "Portugal": "UEFA",
    "Italy": "UEFA",
    "Netherlands": "UEFA",
    "Belgium": "UEFA",
    "Croatia": "UEFA",
    "Switzerland": "UEFA",
    "Denmark": "UEFA",
    "Sweden": "UEFA",
    "Norway": "UEFA",
    "Poland": "UEFA",
    "Serbia": "UEFA",
    "Czechia": "UEFA",
    "Slovakia": "UEFA",
    "Austria": "UEFA",
    "Slovenia": "UEFA",
    "Ukraine": "UEFA",
    "Russia": "UEFA",
    "Wales": "UEFA",
    "Bosnia and Herzegovina": "UEFA",
    "Greece": "UEFA",
    "Iceland": "UEFA",
    "Serbia and Montenegro": "UEFA",
    "Scotland": "UEFA",
    "Turkey": "UEFA",


    # CONMEBOL
    "Brazil": "CONMEBOL",
    "Argentina": "CONMEBOL",
    "Uruguay": "CONMEBOL",
    "Chile": "CONMEBOL",
    "Paraguay": "CONMEBOL",
    "Colombia": "CONMEBOL",
    "Ecuador": "CONMEBOL",
    "Peru": "CONMEBOL",

    # CONCACAF
    "Mexico": "CONCACAF",
    "United States": "CONCACAF",
    "Canada": "CONCACAF",
    "Costa Rica": "CONCACAF",
    "Honduras": "CONCACAF",
    "Panama": "CONCACAF",
    "Trinidad and Tobago": "CONCACAF",
    "CuraÃ§ao": "CONCACAF",
    "Haiti": "CONCACAF",

    # AFC
    "Japan": "AFC",
    "South Korea": "AFC",
    "Australia": "AFC",
    "Iran": "AFC",
    "Saudi Arabia": "AFC",
    "North Korea": "AFC",
    "Qatar": "AFC",
    "Iraq": "AFC",
    "Jordan": "AFC",
    "Uzbekistan": "AFC",

    # CAF
    "South Africa": "CAF",
    "Nigeria": "CAF",
    "Ghana": "CAF",
    "Cameroon": "CAF",
    "Ivory Coast": "CAF",
    "Algeria": "CAF",
    "Tunisia": "CAF",
    "Morocco": "CAF",
    "Senegal": "CAF",
    "Angola": "CAF",
    "Egypt": "CAF",
    "Togo": "CAF",
    "Cape Verde": "CAF",
    "DR Congo": "CAF",

    # OFC
    "New Zealand": "OFC"

}

# ==========================================================
# Ranking Schedule Ids
# ==========================================================

FIFA_RANKING_IDS = {
    2006: "id145",
    2010: "id9276",
    2014: "id10747",
    2018: "id12210",
    2022: "id13792"
}

# ==========================================================
# Fifa Team Name Mapping
# ==========================================================

# For FIFA Ranking
FIFA_TEAM_MAPPING = {

    # Europe
    "Czechia": "Czech Republic",

    # Asia
    "Iran": "IR Iran",
    "South Korea": "Korea Republic",
    "North Korea": "Korea DPR",

    # North America
    "United States": "USA",

    # Africa
    "Ivory Coast": "Côte d'Ivoire"

}

# For FIFA 2026 Ranking
FIFA_TEAM_MAPPING_2026 = {

    # Europe
    "Turkey": "Türkiye",

    # Africa
    "DR Congo": "Congo DR",
    "Cape Verde": "Cabo Verde",
    "Ivory Coast": "Côte d'Ivoire",

    # Asia
    "Iran": "IR Iran",
    "South Korea": "Korea Republic",

    # North America
    "United States": "USA",
    "CuraÃ§ao": "Curaçao"

}

# For Qualification Stats
TEAM_NAME_MAPPING = {

    # Czech Republic -> Czechia
    "Czech Republic": "Czechia",

    # Historical name used in old datasets
    "Czechoslovakia": "Czechia",

    # Curacao spelling
    "Curaçao": "CuraÃ§ao",

}

# ==========================================================
# World Cup Winners
# ==========================================================

WORLD_CUP_WINNERS = {
    2002: "Brazil",
    2006: "Italy",
    2010: "Spain",
    2014: "Germany",
    2018: "France",
    2022: "Argentina",
}

# ==========================================================
# Previous World Cup Mapping
# ==========================================================

PREVIOUS_WORLD_CUP = {
    2006: 2002,
    2010: 2006,
    2014: 2010,
    2018: 2014,
    2022: 2018,
}