HomeGuard Platform - Deployment Guide
Môi trường phát triển
Prerequisites
Node.js >= 18.0.0
PNPM >= 8.0.0
Docker & Docker Compose
Git
Quick Start
bash
# Clone repository
git clone https://github.com/your-username/homeguard-platform.git
cd homeguard-platform

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start development
pnpm dev
Truy cập:

Frontend: http://localhost:3000
API: http://localhost:4000
API Health: http://localhost:4000/health
Development Commands
bash
# Install dependencies
pnpm install

# Build all packages
pnpm build

# Run linter
pnpm lint

# Type check
pnpm type-check

# Start dev servers
pnpm dev

# Start specific app
pnpm --filter @homeguard/web dev
pnpm --filter @homeguard/api dev
Docker Compose Deployment
Development
bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
Production
bash
# Copy environment file
cp .env.example .env.production

# Edit production variables
nano .env.production

# Build and start
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
Kubernetes Deployment
Prerequisites
Kubernetes cluster (GKE, EKS, AKS, hoặc local Minikube)
kubectl configured
Docker Hub account (hoặc container registry khác)
Step 1: Build và Push Images
bash
# Login to Docker Hub
docker login

# Build images
docker compose -f docker-compose.prod.yml build

# Tag images
docker tag homeguard-api:latest your-username/homeguard-api:latest
docker tag homeguard-web:latest your-username/homeguard-web:latest

# Push images
docker push your-username/homeguard-api:latest
docker push your-username/homeguard-web:latest
Step 2: Create Secrets
bash
# Create namespace
kubectl create namespace homeguard

# Create secrets
kubectl create secret generic homeguard-secrets \
  --from-literal=database-url='postgresql://user:pass@postgres:5432/homeguard' \
  --from-literal=redis-url='redis://redis:6379' \
  --from-literal=jwt-secret='your-super-secret-key' \
  -n homeguard
Step 3: Deploy PostgreSQL & Redis
bash
# Deploy PostgreSQL
kubectl apply -f infrastructure/kubernetes/postgres-deployment.yaml -n homeguard

# Deploy Redis
kubectl apply -f infrastructure/kubernetes/redis-deployment.yaml -n homeguard

# Wait for ready
kubectl wait --for=condition=ready pod -l app=postgres -n homeguard
kubectl wait --for=condition=ready pod -l app=redis -n homeguard
Step 4: Deploy API & Web
bash
# Update image names in deployment files
sed -i 's/your-docker-username/YOUR_USERNAME/g' infrastructure/kubernetes/*.yaml

# Deploy API
kubectl apply -f infrastructure/kubernetes/api-deployment.yaml -n homeguard

# Deploy Web
kubectl apply -f infrastructure/kubernetes/web-deployment.yaml -n homeguard

# Deploy Ingress
kubectl apply -f infrastructure/kubernetes/ingress.yaml -n homeguard
Step 5: Verify Deployment
bash
# Check pods
kubectl get pods -n homeguard

# Check services
kubectl get svc -n homeguard

# Check ingress
kubectl get ingress -n homeguard

# View logs
kubectl logs -f deployment/homeguard-api -n homeguard
kubectl logs -f deployment/homeguard-web -n homeguard
CI/CD với GitHub Actions
Setup
Add secrets trong GitHub repository settings:
DOCKER_USERNAME
DOCKER_PASSWORD
KUBECONFIG (nếu auto deploy)
Push code lên GitHub:
bash
git add .
git commit -m "Initial commit"
git push origin main
GitHub Actions sẽ tự động:
Run lint và tests
Build Docker images
Push lên Docker Hub
Deploy lên Kubernetes (nếu cấu hình)
Production Checklist
Security
 Đổi JWT_SECRET thành giá trị random mạnh
 Cập nhật database credentials
 Enable HTTPS/TLS
 Configure CORS properly
 Set up rate limiting
 Enable firewall rules
Performance
 Enable Redis caching
 Configure database connection pooling
 Set up CDN cho static assets
 Enable gzip compression
 Configure proper resource limits
Monitoring
 Set up logging aggregation
 Configure health checks
 Set up alerts
 Enable metrics collection
 Configure backup strategy
Database
 Run migrations
 Create indexes
 Set up automated backups
 Configure replication (nếu cần)
Troubleshooting
API không start
bash
# Check logs
docker compose logs api

# Common issues:
# - Database connection failed: Check DATABASE_URL
# - Redis connection failed: Check REDIS_URL
# - Port already in use: Change API_PORT
WebSocket không kết nối
bash
# Check CORS settings
# Check firewall rules
# Verify WS URL in frontend
Database migration failed
bash
# Reset database
docker compose down -v
docker compose up -d postgres
cd apps/api
pnpm db:push
pnpm db:seed
Maintenance
Database Backup
bash
# Backup
docker exec homeguard-postgres pg_dump -U homeguard homeguard_db > backup.sql

# Restore
docker exec -i homeguard-postgres psql -U homeguard homeguard_db < backup.sql
Update Deployment
bash
# Build new images
docker compose -f docker-compose.prod.yml build

# Push images
docker push your-username/homeguard-api:latest
docker push your-username/homeguard-web:latest

# Rolling update
kubectl rollout restart deployment/homeguard-api -n homeguard
kubectl rollout restart deployment/homeguard-web -n homeguard

# Check status
kubectl rollout status deployment/homeguard-api -n homeguard
Support
Nếu gặp vấn đề, vui lòng:

Check logs
Review documentation
Create GitHub issue
Contact support team
