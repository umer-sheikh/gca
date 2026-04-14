# Tool Suite Specification

This document translates Table 4 into concrete engineering decisions.

## Remote sensing and land surface

- `get_satellite_image(lat, lon, date)`
  - Returns artifact references for RGB preview, NDVI index, NDWI index, and a manifest.
- `calculate_ndvi(image)`
  - Accepts a manifest URI or direct index artifact and returns a rendered map plus statistics.
- `calculate_ndwi(image)`
  - Same pattern as NDVI.
- `desertification_analysis(image1, image2)`
  - Computes delta metrics, emits a change map, then synthesizes an analytical narrative.

## Biodiversity and species

- `detect_bird(audio_clip)`
  - TensorFlow plus MFCC pipeline.
- `detect_species(image)`
  - Shells out to `bioclip predict` and normalizes the returned candidates.

## Web retrieval and summarization

- `online_search(query)`
  - Tavily search with ranked snippets.
- `summarize(text)`
  - GPT-5 summarization using OpenAI Responses.

## Carbon and sustainability

- `carbon_footprint_calculation(country, industry, year, revenue)`
  - GCC sector estimator with proxy emission factors where direct sector factors are missing.

## Air quality and health indices

- `aqi_inquiry(lat, lon, date)`
- `aqi_prediction(lat, lon, horizon)`
- `aqi_analysis(lat, lon, start, end)`
- `pollen_forecast(lat, lon)`
- `uv_index_forecast(lat, lon)`

## Weather, rainfall, and hydrology

- `weather_inquiry(lat, lon, date)`
- `weather_forecast(lat, lon, days)`
- `weather_analysis(lat, lon, start, end)`
- `rain_inquiry(lat, lon, date)`
- `rain_prediction(lat, lon, horizon)`
- `rain_analysis(lat, lon, start, end)`
- `river_discharge_check(lat, lon, date)`
- `geocode_mapping(region)`

## Output normalization policy

Every output should contain:

- `meta.provider`
- `meta.generated_at`
- `meta.units`
- `meta.timestamps`
- `meta.location` where relevant
- optional warnings

That normalization policy is central to composability.
