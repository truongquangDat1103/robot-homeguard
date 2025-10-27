HomeGuard Platform Architecture
Tổng quan
HomeGuard là một hệ thống IoT full-stack để giám sát và điều khiển robot bảo vệ gia đình với tích hợp AI.

Kiến trúc hệ thống
┌─────────────────────────────────────────────────────────────┐
│                        Users / Admin                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Web Dashboard (Next.js)                   │
│  - Real-time monitoring   - Robot control                    │
│  - Camera feed           - Logs & notifications              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 API Server (Node.js + WebSocket)             │
│  - REST API              - WebSocket server                  │
│  - Authentication        - Message routing                   │
│  - Business logic        - Data persistence                  │
└───────┬─────────────────┬────────────────────┬──────────────┘
        │                 │                    │
        ▼                 ▼                    ▼
┌──────────────┐  ┌──────────────┐   ┌─────────────────┐
│  PostgreSQL  │  │    Redis     │   │  AI Engine      │
│  (Database)  │  │   (Cache)    │   │  Adapter        │
└──────────────┘  └──────────────┘   └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │   ESP32 Robot   │
                                     │   + Sensors     │
                                     └─────────────────┘
Các thành phần chính
1. Frontend (apps/web)
Framework: Next.js 14 với App Router
UI: Tailwind CSS + Shadcn/ui
State Management: Zustand
Real-time: Socket.io client
Features:
Dashboard với sensor cards và charts
Robot control interface
Camera live stream
Face recognition display
Logs và notifications
2. Backend API (apps/api)
Framework: Express.js
WebSocket: Socket.io
Database: Prisma ORM + PostgreSQL
Cache: Redis
Authentication: JWT
Features:
REST API endpoints
WebSocket message routing
Sensor data processing
Robot command handling
AI results processing
3. Shared Packages (packages/)
@homeguard/types: TypeScript type definitions
@homeguard/utils: Shared utilities (validators, formatters)
@homeguard/config: Shared configurations (ESLint, TypeScript)
4. AI Engine Adapter (services/ai-engine-adapter)
Kết nối WebSocket với backend
Gửi kết quả nhận diện khuôn mặt
Gửi kết quả phát hiện chuyển động
Mock mode cho testing
5. ESP32 Device
Gửi dữ liệu sensor qua WebSocket
Nhận lệnh điều khiển từ backend
Cập nhật trạng thái robot
Data Flow
Sensor Data Flow
ESP32 → WebSocket → API Server → Database
                          ↓
                    Web Dashboard
Robot Command Flow
Web Dashboard → WebSocket → API Server → ESP32
AI Detection Flow
AI Engine → WebSocket → API Server → Database
                             ↓
                       Web Dashboard
Technology Stack
Frontend
Next.js 14
React 18
TypeScript
Tailwind CSS
Socket.io Client
Zustand
Recharts
Backend
Node.js
Express.js
Socket.io
Prisma ORM
PostgreSQL
Redis
JWT
DevOps
Docker & Docker Compose
Kubernetes
GitHub Actions CI/CD
Nginx
Development Tools
Turborepo (Monorepo)
PNPM (Package Manager)
ESLint
Prettier
TypeScript
Security
JWT-based authentication
Password hashing với bcrypt
CORS configuration
Rate limiting
Helmet security headers
HTTPS/TLS encryption
WebSocket authentication
Scalability
Horizontal scaling với Kubernetes
Redis caching
Load balancing với Nginx
Database connection pooling
WebSocket room-based broadcasting
Monitoring & Logging
Pino logger
Health check endpoints
Real-time logs display
Error tracking
Performance metrics
