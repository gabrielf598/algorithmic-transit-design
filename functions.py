import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union
import pandas as pd

def filter_blocks(blocks, rect, development, neighborhoods):
    rect_geom = rect.geometry.iloc[0]
    filtered_blocks = blocks[blocks.geometry.intersects(rect_geom)]

    development = development[development.geometry.intersects(rect_geom)]
    development = development[development["LAND_USE_DESC_10"] == "Parks/Open Space/Cemeteries"]
    filtered_blocks["geometry"] = filtered_blocks.geometry.difference(development.unary_union)
    filtered_blocks = filtered_blocks[~filtered_blocks.is_empty]
    neighborhoods = neighborhoods.union_all()

    blocks_with_water = filtered_blocks[filtered_blocks["WATER"] == 1].copy()
    blocks_with_water["geometry"] = blocks_with_water.geometry.intersection(neighborhoods)
    blocks_with_water = blocks_with_water[~blocks_with_water.is_empty]

    non_water_blocks = filtered_blocks[filtered_blocks["WATER"] == 0].copy()

    filtered_blocks = gpd.GeoDataFrame(pd.concat([blocks_with_water, non_water_blocks], ignore_index=True))

    return filtered_blocks
    

def score_blocks(blocks, stop_coverage, zoning, stops):

    block_center = blocks.copy()
    block_center["geometry"] = block_center.geometry.centroid
    nearest_stops = gpd.sjoin_nearest(block_center, stops, how="left", distance_col="distance_to_stop")
    blocks = blocks.reset_index(drop=True)
    nearest_stops = nearest_stops.reset_index(drop=True)
    blocks["distance_to_stop"] = nearest_stops["distance_to_stop"]

    stop_coverage_geom = stop_coverage.unary_union

    single_family = zoning[zoning["ZONELUT"].str.startswith("SF")].geometry
    single_family = single_family.unary_union

    multi_family = zoning[zoning["ZONELUT"].str.startswith("LR")].geometry
    multi_family = multi_family.unary_union

    commercial = zoning[zoning["ZONELUT"].str.startswith("NC") | zoning["ZONELUT"].str.startswith("C")].geometry
    commercial = commercial.unary_union

    scored_blocks = {}
    for row in blocks.iterrows():
        block_id = row[1]["OBJECTID"]
        block_geom = row[1].geometry
        block_nearest_stop = row[1]["distance_to_stop"]

        stop = block_geom.intersection(stop_coverage_geom).area / block_geom.area

        if stop >= 0.7:
            scored_blocks[block_id] = 0
            continue

        stop_distance_score = (block_nearest_stop - 1) // 400
        sf = block_geom.intersection(single_family).area / block_geom.area
        mf = block_geom.intersection(multi_family).area / block_geom.area
        comm = block_geom.intersection(commercial).area / block_geom.area

        zone_score = 3 * mf + 2 * comm + sf

        score = (1 - stop) * (stop_distance_score + zone_score)
        
        
        scored_blocks[block_id] = score

    return scored_blocks

def get_streets(block, streets, stop_coverage):
    minx, miny, maxx, maxy = block.bounds

    up    = box(minx, maxy, maxx, maxy + 5)
    down  = box(minx, miny - 5, maxx, miny)
    left  = box(minx - 5, miny, minx, maxy)
    right = box(maxx, miny, maxx + 5, maxy)

    stop_coverage_union = stop_coverage.unary_union
    extended_block = unary_union([block, up, down, left, right])
    extended_block = extended_block.difference(stop_coverage_union)
    block_streets = streets[streets.intersects(extended_block)]

    return block_streets.union_all()

def propose_stops(blocks, stop_coverage, streets, zoning, stops):
    scored_blocks = blocks.copy()
    new_stop_coverage = stop_coverage.copy()
    new_stops = stops.copy()

    score_dict = score_blocks(scored_blocks, new_stop_coverage, zoning, new_stops)
    scored_blocks["score"] = scored_blocks["OBJECTID"].map(score_dict)

    while (scored_blocks["score"].max() > 0.7):
        max_block = scored_blocks.loc[scored_blocks["score"].idxmax()]
        block_geom = max_block.geometry
        surrounding_streets = get_streets(block_geom, streets, new_stop_coverage)

        if not surrounding_streets:
            scored_blocks = scored_blocks.drop(max_block.name)
            continue

        stop_location = surrounding_streets.interpolate(surrounding_streets.project(block_geom.centroid))
        stop_buffer = stop_location.buffer(400)
       
        new_stops = pd.concat([new_stops, gpd.GeoDataFrame(geometry=[stop_location], crs=new_stops.crs)])
        new_stop_coverage = pd.concat([new_stop_coverage, gpd.GeoDataFrame(geometry=[stop_buffer], crs=new_stop_coverage.crs)])

        score_dict = score_blocks(scored_blocks, new_stop_coverage, zoning, new_stops)
        scored_blocks["score"] = scored_blocks["OBJECTID"].map(score_dict)

    new_stop_coverage.drop_duplicates()
    new_stop_coverage = new_stop_coverage.to_crs(epsg=4326)
    new_stop_coverage.to_file("Results/new_stop_coverage.geojson", driver="GeoJSON")

    new_stops = new_stops[new_stops["stop_name"].isna()]
    new_stops.drop_duplicates()
    new_stops = new_stops.to_crs(epsg=4326)
    new_stops.to_file("Results/proposed_stops.geojson", driver="GeoJSON")

    return new_stops






        