# Geo Map

A satellite image processing application with a Vue frontend to view Cloud Optimized GeoTIFF image layers from [Landsat Analysis Ready Data (GLAD ARD)](https://glad.umd.edu/ard/home).

## Architecture

**Docker Compose Services:**
- **frontend** - Vue 3 application with [OpenLayers](https://vue3openlayers.netlify.app/) for interactive mapping
- **api** - [FastAPI](https://fastapi.tiangolo.com/) server providing metadata and tile information to the frontend
- **worker** - Image processing service for satellite data ingestion and analysis (runs via GitHub Actions)
- **nginx** - Reverse proxy routing frontend and backend from a single origin
- **PostgreSQL** - Database for tracking run statistics and metadata

**External Services:**
- **S3** - Cloud storage for processed satellite imagery
- **OIDC Provider** - Any OpenID Connect provider (e.g., Pocket ID, Auth0, Okta) for authentication

The [GLAD](lib/glad.py) class contains the main processing and ingestion logic. See [example.ipynb](example.ipynb) to understand the implementation details.


## Treecover Analysis

The Jupyter notebook [treecover-analysis.ipynb](treecover-analysis.ipynb) shows how the Treecover layer is computed using NDVI.
- NDVI is computed as (NIR-Red)/(NIR+Red)
- Missing values are imputed with forward fill and back fill along the time axis and outliers are clipped to known NDVI values = (-1, 1).
Missing values are due to the qf mask provided by GLAD ARD. This is to remove any bad quality data/cloud data.
- NDVI values are smoothened to account for seasonal/temporal variance along the time axis (3 periods).
- If the differnce between NDVI for a single time point is greater than a known value (0.25) (max NDVI along time axis - current NDVI), then this usually indicates that trees have been cut down. This check is also clipped to a lower bound of known NDVI value for tree (0.7).
- If a pixel is marked as tree loss then it will be marked as tree loss for all future time points unless re-growth (tree) is detected for 3 periods.

The values for NDVI difference for tree and cut tree (0.25) & and the NDVI lower bound for trees (0.7) is a configurable value per Tile ID as this may vary based on the geographical location of the Tile.


## Screenshots

The treecover (green = trees, red = no trees) can be seen for different dates -
![](docs/2025%20treecover.png)
![](docs/2000%20treecover.png)

The TCI layer can also be seen for different dates - 
![](docs/2025%20tci.png)
![](docs/2000%20tci.png)
*The TCIs are also imputed via forward fill & back fill along time axis.*

The GLAD ARD Grid can also be overlayed to see the Tile IDs on click - 
![](docs/glad%20tile%20grid.png)

Demo Tiles -
- Paraguay
  - 059W_20S
  - 058W_20S
  - 060W_20S
  - 060W_19S
  - 059W_19S
  - 058W_19S
- Brazil
  - 055W_04S
  - 054W_04S
  - 056W_04S
  - 056W_03S
  - 055W_03S
  - 054W_03S 


## Local Development

### Prerequisites
- Docker and Docker Compose installed
- A `.devcontainer` configuration is available for development in a containerized environment
- `.env` file configured using `sample.env`

### Running the App

```bash
docker compose up --build
```

The application will be available at `http://localhost`. Access is routed through Nginx, which sits in front of both the frontend and backend components.

## Production Deployment

### Building the Production Image

The production deployment uses Docker to containerize the application with all dependencies:

```bash
# Build with OIDC credentials
docker build \
  --build-arg VITE_AUTH_URL=oidc-provider-url \
  --build-arg VITE_AUTH_CLIENT_ID=client-id \
  -t geomap:latest \
  .

# Run in production
docker run -d \
  -p 80:80 \
  -e POSTGRES_URL=postgresql://user:pass@postgres-host:5432/geomap \
  -e S3_URL=your-s3-url-with-bucket \
  -e S3_ACCESS_KEY=s3-access-key \
  -e S3_SECRET_KEY=s3-secret-key \
  -e PUBLIC_S3_URL=s3-public-endpoint \
  -e AUTH_URL=oidc-provider \
  -e AUTH_CLIENT_ID=oidc-client-id \
  geomap:latest
```

### External Dependencies

1. **PostgreSQL** - Database for metadata and run statistics
2. **S3-compatible storage** - For storing processed satellite tiles
3. **OIDC Provider** - For authentication
4. **Worker infrastructure** - For image processing tasks (GitHub Actions or similar CI/CD)

### Deploying to Dokploy

1. Add a service of type Application and point to the repository using the Git provider with build type Dockerfile.
2. Add **Build Arguments** in the Environment tab:
    - `VITE_AUTH_URL` - OIDC provider URL
    - `VITE_AUTH_CLIENT_ID` - OIDC client ID
3. Set **Environment Variables** in the Environment tab:
    - `POSTGRES_URL` - PostgreSQL connection string
    - `S3_URL` - S3 endpoint with bucket
    - `S3_ACCESS_KEY` - S3 access key
    - `S3_SECRET_KEY` - S3 secret key
    - `PUBLIC_S3_URL` - Public endpoint for S3 assets
    - `AUTH_URL` - OIDC provider base URL
    - `AUTH_CLIENT_ID` - OIDC client ID
4. Map a domain to port 4000.
5. Deploy

## Attributions

- Landsat Analysis Ready Data (GLAD ARD) -

  > Potapov, P., Hansen, M.C., Kommareddy, I., Kommareddy, A., Turubanova, S., Pickens, A., Adusei, B., Tyukavina A., and Ying, Q., 2020.
  > 
  > Landsat analysis ready data for global land cover and land cover change mapping.
  > 
  > Remote Sens. 2020, 12, 426; doi:10.3390/rs12030426.

- Lakshya Vaibhav Datta ([![Linkedin](https://i.sstatic.net/gVE0j.png) LinkedIn](https://www.linkedin.com/in/lakshyavdatta) [![GitHub](https://i.sstatic.net/tskMh.png) GitHub](https://github.com/Rockets2Desighee)) for providing insights into the world of geospatial sorcery & satellite imagery.
