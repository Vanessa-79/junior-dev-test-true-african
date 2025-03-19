# junior-dev-test-true-african

# 🚖 Ride-Sharing Service Backend

## 📌 Overview
A Django-based ride-sharing backend service that demonstrates:
- **Code Versioning** → Git with GitHub Actions CI/CD pipeline
- **Algorithm Design** → Haversine-based driver matching with Uganda-specific optimizations
- **API Integration** → OpenStreetMap integration for real-time geolocation
- **Code Deployment** → Docker containerization for easy deployment
- **Caching System** → Redis integration for optimized performance

## 🚀 Features
✅ **Smart Ride-Matching** 
- Assigns nearest driver using Haversine formula
- Optimized for Uganda's geographical bounds
- Considers driver availability and location

✅ **Real-Time Geolocation** 
- OpenStreetMap integration via Nominatim
- Geocoding and reverse geocoding
- Distance calculation between locations
- Redis caching for location lookups (24-hour cache)

✅ **Performance Optimizations**
- Redis caching system for:
  - Geolocation results (24-hour cache)
  - Nearby drivers (5-minute cache)
  - Ride details (1-hour cache)
  - User profiles (1-hour cache)

✅ **REST API Endpoints**
- Request rides with location matching
- Real-time ride status tracking
- Driver availability management

✅ **Production Ready**
- Containerized with Docker
- CI/CD with GitHub Actions
- PostgreSQL database
- Redis caching

## 📂 Project Structure
```
📦 ride-sharing-backend
├── 📂 rides/          → Core ride management
│   ├── matching.py    → Driver matching algorithm
│   ├── models.py      → Ride data models
│   ├── views.py       → API endpoints
│   └── urls.py        → URL routing
├── 📂 drivers/        → Driver management
├── 📂 riders/         → Rider management
├── 📂 utils/          → Shared utilities
│   └── geolocation.py → Location services
├── 📂 tests/          → Test suite
├── 📄 Dockerfile      → Container configuration
└── 📄 docker-compose.yml → Local development
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (optional for local development)
- Redis (for caching)

### Local Development
1. Clone the repository:
```bash
https://github.com/Vanessa-79/junior-dev-test-true-african.git
cd ride-sharing-backend
```

2. Set up environment variables:


3. Run with Docker (includes Redis):
```bash
docker-compose up --build
```

4. Run locally (alternative):
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (if not using Docker)
docker-compose up redis -d

# Run migrations and start server
python manage.py migrate
python manage.py runserver
```

### Redis Commands
```bash
# Start Redis container
docker-compose up redis -d

# Check Redis status
docker-compose ps

# Redis CLI (if needed)
docker-compose exec redis redis-cli

# Stop Redis
docker-compose stop redis
```

### Testing Redis Connection
```python
# In Django shell (python manage.py shell)
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)  
cache.get('test_key')  # Should return 'test_value'
```

## 🔌 API Endpoints
### Drivers API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/drivers/` | Register a new driver |
| GET | `/api/drivers/` | List available drivers |

#### Register a Driver
```bash
curl -X POST "http://localhost:8000/api/drivers/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "driver1",
    "password": "secure_password",
    "email": "driver1@gmail.com",
    "phone_number": "+256700000000",
    "vehicle_model": "Toyota Camry",
    "vehicle_plate": "UAX 123K"
  }'
```

#### Register a Rider
```bash
curl -X POST "http://localhost:8000/api/riders/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ronia",
    "password": "secure_password",
    "email": "ronia@gmail.com",
    "phone_number": "+256700000000"
  }'
```

### Rides API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/request-ride/` | Request a new ride |
| GET | `/api/ride-status/{id}/` | Check ride status |


#### Request a Ride
```bash
curl -X POST "http://localhost:8000/api/request-ride/" \
  -H "Content-Type: application/json" \
  -d '{
    "rider_id": "123",
    "pickup_place": "Kampala",
    "destination_place": "Entebbe"
  }'
```

### Riders API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/riders/` | Register a new rider |
| GET | `/api/riders/` | Get riders details |

#### Get Ride Status
```bash
curl -X GET "http://localhost:8000/api/ride-status/3/" \
  -H "Content-Type: application/json"
```


## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

## 🌍 Deployment
### Deploy with Docker

#### Docker Image
The application is available as a Docker image:
```
vanessa79/ride-sharing:latest    
```

#### 1. Pull Docker Image
```bash
# Pull the latest image
docker pull vanessa79/ride-sharing:latest
```

#### 2. Build Image Locally (Alternative)
```bash
# Build the main application
docker build -t vanessa79/ride-sharing:latest .
```

#### 3. Run the Application
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or run manually
docker run -d -p 8000:8000 vanessa79/ride-sharing:latest
```

#### 4. Check Running Containers
```bash
docker ps
```

#### 5. View Logs
```bash
# View container logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

#### 6. Stop and Clean Up
```bash
# Using docker-compose
docker-compose down

# Or manually
docker stop <container_id>
docker rm <container_id>
```

#### Available Tags
- `latest` - Most recent version
- `6575126f7e210a511...` - Specific commit version

## 💡 Future Improvements
- [ ] WebSocket integration for real-time updates
- [x] Redis caching for location lookups
- [ ] Payment gateway integration
- [ ] OAuth2 authentication
- [ ] Rate limiting for API endpoints

## 📜 License
MIT License © 2025 True African 

## 💡 Future Improvements
- [ ] WebSocket integration for real-time updates
- [x] Redis caching for location lookups
- [ ] Payment gateway integration
- [ ] OAuth2 authentication
- [ ] Rate limiting for API endpoints

## 📜 License
MIT License © 2025 True African 