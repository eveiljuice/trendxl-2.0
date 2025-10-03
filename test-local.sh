#!/bin/bash
# TrendXL 2.0 - Local Testing Script

set -e

echo "🧪 TrendXL 2.0 - Local Docker Testing"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="trendxl-fullstack"
CONTAINER_NAME="trendxl-test"
TEST_PORT=3000

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   - Image: ${IMAGE_NAME}"
echo "   - Container: ${CONTAINER_NAME}"
echo "   - Port: ${TEST_PORT}"
echo ""

# Stop and remove existing container
echo -e "${YELLOW}🧹 Cleaning up existing container...${NC}"
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

# Build image
echo -e "${YELLOW}🏗 Building Docker image...${NC}"
docker build -t ${IMAGE_NAME} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Run container
echo -e "${YELLOW}🚀 Starting container...${NC}"
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${TEST_PORT}:80 \
    -e PORT=80 \
    ${IMAGE_NAME}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container started successfully!${NC}"
else
    echo -e "${RED}❌ Failed to start container!${NC}"
    exit 1
fi

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Test health check
echo -e "${YELLOW}🔍 Testing health check...${NC}"
if curl -s -f http://localhost:${TEST_PORT}/health > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed!${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Test frontend
echo -e "${YELLOW}🌐 Testing frontend...${NC}"
if curl -s -f http://localhost:${TEST_PORT}/ > /dev/null; then
    echo -e "${GREEN}✅ Frontend accessible!${NC}"
else
    echo -e "${RED}❌ Frontend not accessible!${NC}"
fi

# Test API backend (if health endpoint exists)
echo -e "${YELLOW}🔧 Testing API backend...${NC}"
API_RESPONSE=$(curl -s -w "%{http_code}" http://localhost:${TEST_PORT}/api/ -o /dev/null)
if [ "${API_RESPONSE}" -eq 200 ] || [ "${API_RESPONSE}" -eq 404 ]; then
    echo -e "${GREEN}✅ API backend responding! (HTTP ${API_RESPONSE})${NC}"
else
    echo -e "${YELLOW}⚠️ API backend may need configuration (HTTP ${API_RESPONSE})${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Testing completed!${NC}"
echo ""
echo -e "${BLUE}📊 Access URLs:${NC}"
echo "   - Frontend: http://localhost:${TEST_PORT}/"
echo "   - Health:   http://localhost:${TEST_PORT}/health"
echo "   - API:      http://localhost:${TEST_PORT}/api/"
echo ""
echo -e "${BLUE}🛠 Useful commands:${NC}"
echo "   - View logs:        docker logs ${CONTAINER_NAME}"
echo "   - Follow logs:      docker logs -f ${CONTAINER_NAME}"
echo "   - Enter container:  docker exec -it ${CONTAINER_NAME} sh"
echo "   - Stop container:   docker stop ${CONTAINER_NAME}"
echo "   - Remove container: docker rm ${CONTAINER_NAME}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the container and exit${NC}"

# Keep script running and show logs
trap 'echo -e "\n${YELLOW}🛑 Stopping container...${NC}"; docker stop ${CONTAINER_NAME}; docker rm ${CONTAINER_NAME}; exit 0' INT

# Follow logs
docker logs -f ${CONTAINER_NAME}
