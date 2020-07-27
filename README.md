# polygon_simplification_service

## Getting Started

### Requirements
  - Docker

### Running the Service
Build the container and run the service

    docker-compose up -d --build

The service will be available at [http://localhost:8002](http://localhost:8002)

To view the logs, first find the container ID

    docker ps -a

Then follow the logs

    docker logs --follow <container_id>

#### Additional notes
Sample endpoint call (with a file path from the current directory)

    curl -o output.zip -F file=@path/to/file/sample.zip 'http://localhost:8002/simplify_polygon/shapefile/geopandas'

API documentation (from OpenAPI formerly Swagger) (documentation needs some improvement)
    localhost:8002/docs

Tests are not fully functional at the moment, but to run the tests when the container is running:

    docker-compose exec web pytest .
