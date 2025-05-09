# Algorithmic Design of New Transit Routes Using Open Data

This project was created as a part of the CS-497: Advanced Project course at Whitman College.
In this project, I developed an iterative, and score-based algorithm that proposes new bus stops in underserved areas.
The algorithm was developed for specific datasets of the City of Seattle. 

An example of running the algorithm step-by-step is in [TransitDesignAlgorithm.ipynb](https://github.com/gabrielf598/algorithmic-transit-design/blob/main/TransitDesignAlgorithm.ipynb). The example operates on the Seattle neighborhood Madison Park. The resulting data can be found in the [Results](https://github.com/gabrielf598/algorithmic-transit-design/tree/main/Results) folder.

### Data used:

* [Street Network Database (SND)](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::street-network-database-snd-1/about)
* [Neighborhood Map Atlas Neighborhoods](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::neighborhood-map-atlas-neighborhoods/about)
* [Single and Multi Family Residential](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::single-and-multi-family-residential/about)
* [Annual Population and Housing Estimates for 2020 Census Blocks in Seattle](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::annual-population-and-housing-estimates-for-2020-census-blocks-in-seattle/about)
* [Public and Private Parcels with No Development Expected](https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::zoned-development-capacity-layers-2016/about?layer=6)
* [Puget Sound Consolidated GTFS Schedule File Set](https://www.soundtransit.org/help-contacts/business-information/open-transit-data-otd/otd-downloads)
