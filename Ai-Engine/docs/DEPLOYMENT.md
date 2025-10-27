🚀 AI-Engine Deployment Guide
Môi trường yêu cầu
Hardware tối thiểu
CPU: 4 cores
RAM: 8 GB
Storage: 20 GB
GPU (optional): NVIDIA với CUDA 11.8+
Software yêu cầu
Python: 3.10+
Docker: 20.10+
Docker Compose: 2.0+
Redis: 7.0+ (hoặc Docker)
🐳 Deployment với Docker
1. Clone repository
bash
git clone https://github.com/yourusername/ai-engine.git
cd ai-engine
2. Cấu hình environment
bash
cp .env.example .env
nano .env  # Chỉnh sửa cấu hình
Các biến quan trọng:

bash
# Environment
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# WebSocket
WEBSOCKET_URL=ws://your-esp32-ip:8080/ws

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Security
SECRET_KEY=your-random-secret-key
3. Build Docker image
CPU version:

bash
docker build -f docker/Dockerfile -t ai-engine:latest .
GPU version:

bash
docker build -f docker/Dockerfile.gpu -t ai-engine:gpu .
4. Chạy với Docker Compose
Basic setup:

bash
cd docker
docker-compose up -d
With monitoring:

bash
docker-compose --profile monitoring up -d
5. Kiểm tra logs
bash
docker-compose logs -f ai-engine
6. Stop services
bash
docker-compose down
💻 Deployment trực tiếp (không Docker)
1. Cài đặt dependencies
System packages:

bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3.10 python3-pip \
    libgl1-mesa-glx libglib2.0-0 \
    libsndfile1 ffmpeg portaudio19-dev \
    redis-server

# macOS
brew install python@3.10 redis portaudio
Python packages:

bash
# Sử dụng Poetry (recommended)
pip install poetry
poetry install

# Hoặc pip
pip install -r requirements.txt
2. Start Redis
bash
redis-server
3. Setup environment
bash
cp .env.example .env
# Chỉnh sửa .env
4. Run application
bash
# Với Poetry
poetry run python main.py

# Hoặc trực tiếp
python main.py
☁️ Cloud Deployment
AWS EC2
1. Launch EC2 instance:

AMI: Ubuntu 22.04
Instance type: t3.large (hoặc p3.2xlarge cho GPU)
Storage: 30 GB
Security Group: Mở port 8000, 8080
2. SSH vào instance:

bash
ssh -i your-key.pem ubuntu@ec2-ip
3. Install Docker:

bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
4. Clone và deploy:

bash
git clone https://github.com/yourusername/ai-engine.git
cd ai-engine
cp .env.example .env
# Edit .env
cd docker
docker-compose up -d
Google Cloud Platform
1. Create VM:

bash
gcloud compute instances create ai-engine-vm \
    --machine-type=n1-standard-4 \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB
2. SSH và deploy:

bash
gcloud compute ssh ai-engine-vm
# Tiếp theo giống AWS
Azure
1. Create VM:

bash
az vm create \
    --resource-group ai-engine-rg \
    --name ai-engine-vm \
    --image Ubuntu2204 \
    --size Standard_D4s_v3
2. Deploy tương tự AWS

🎯 Kubernetes Deployment
1. Create Dockerfile (đã có)
2. Push image to registry
bash
docker tag ai-engine:latest your-registry/ai-engine:latest
docker push your-registry/ai-engine:latest
3. Create Kubernetes manifests
deployment.yaml:

yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-engine
  template:
    metadata:
      labels:
        app: ai-engine
    spec:
      containers:
      - name: ai-engine
        image: your-registry/ai-engine:latest
        ports:
        - containerPort: 8000
        - containerPort: 8080
        env:
        - name: ENV
          value: "production"
        - name: REDIS_HOST
          value: "redis-service"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
service.yaml:

yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-engine-service
spec:
  selector:
    app: ai-engine
  ports:
  - name: api
    port: 8000
    targetPort: 8000
  - name: websocket
    port: 8080
    targetPort: 8080
  type: LoadBalancer
4. Deploy
bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
🔧 Production Configuration
Nginx Reverse Proxy
nginx.conf:

nginx
upstream ai_engine {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://ai_engine;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
SSL với Let's Encrypt
bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
Systemd Service
ai-engine.service:

ini
[Unit]
Description=AI-Engine Service
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-engine
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Enable service:

bash
sudo systemctl enable ai-engine
sudo systemctl start ai-engine
sudo systemctl status ai-engine
📊 Monitoring
Prometheus + Grafana
Already included in docker-compose:

bash
docker-compose --profile monitoring up -d
Access:

Prometheus: http://localhost:9090
Grafana: http://localhost:3000 (admin/admin)
Health Check Script
health_check.sh:

bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ $response -eq 200 ]; then
    echo "✅ AI-Engine is healthy"
    exit 0
else
    echo "❌ AI-Engine is down"
    exit 1
fi
Uptime Monitoring
UptimeRobot
Pingdom
Datadog
🔒 Security Hardening
1. Firewall
bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
2. Fail2ban
bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
3. Auto-updates
bash
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
4. Secrets Management
Sử dụng environment variables
AWS Secrets Manager / GCP Secret Manager
HashiCorp Vault
🔄 CI/CD Pipeline
GitHub Actions
.github/workflows/deploy.yml:

yaml
name: Deploy AI-Engine

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t ai-engine:latest .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push your-registry/ai-engine:latest
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd ai-engine
          docker-compose pull
          docker-compose up -d
📝 Backup & Recovery
Backup Script
backup.sh:

bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup models
tar -czf $BACKUP_DIR/models_$DATE.tar.gz src/models/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Backup Redis
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

echo "✅ Backup completed: $DATE"
Restore
bash
# Restore models
tar -xzf models_20251019.tar.gz -C src/

# Restore Redis
cp redis_20251019.rdb /var/lib/redis/dump.rdb
sudo systemctl restart redis
🐛 Troubleshooting
Container không start
bash
# Check logs
docker logs ai-engine

# Check resources
docker stats

# Restart
docker-compose restart ai-engine
High memory usage
bash
# Monitor
htop
docker stats

# Adjust buffer sizes in .env
MAX_MEMORY_MB=1024
WebSocket connection failed
Kiểm tra firewall
Kiểm tra WEBSOCKET_URL trong .env
Kiểm tra ESP32 có đang chạy không
📞 Support
Issues: https://github.com/yourusername/ai-engine/issues
Discussions: https://github.com/yourusername/ai-engine/discussions
Email: support@your-domain.com
