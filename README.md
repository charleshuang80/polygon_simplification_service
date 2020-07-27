# Polygon Simplification Service

## Getting Started

### Requirements
  - Docker

### Running the Service
Build the container and run the service

    docker-compose up -d --build

The service will be available at [http://localhost:8002](http://localhost:8002)

Stopping the container and service

    docker-compose stop
#### Logs
To view the logs, first find the container ID

    docker ps -a

Then follow the logs

    docker logs --follow <container_id>

### Additional information
The current (MVP) implementation uses Geopandas (built on Pandas, Shapely, Fiona, and others) to do the simplification and only accepts shapefiles as a zip. It uses Fiona to determine the number of features and points, and will re-run the simplification with an increased tolerance to get under 5000 points (the CMR limit).
Ability to work with geojson and kml has not been added but should be easy to implement.

#### Other commands
Sample endpoint call (with a file path from the current directory)

    curl -o output.zip -F file=@path/to/file/sample.zip 'http://localhost:8002/simplify_polygon/shapefile/geopandas'

API documentation (from OpenAPI formerly Swagger) (documentation needs some improvement)
    localhost:8002/docs

Tests are not fully functional at the moment, but to run the tests when the container is running:

    docker-compose exec web pytest .
