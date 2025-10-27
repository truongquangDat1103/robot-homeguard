🏠 HomeGuard Platform
Hệ thống giám sát & điều khiển robot HomeGuard với tích hợp IoT (ESP32) và AI Engine.

🏗️ Kiến trúc
Monorepo: Turborepo + PNPM Workspaces
Frontend: Next.js 14 (App Router)
Backend: Node.js/Bun + WebSocket
Database: PostgreSQL + Redis
IoT: ESP32 + AI Engine Adapter
📦 Cấu trúc dự án
homeguard-platform/
├── apps/
│   ├── web/          # Next.js Frontend
│   └── api/          # Backend WebSocket Server
├── packages/
│   ├── types/        # Shared TypeScript types
│   ├── utils/        # Shared utilities
│   ├── ui/           # Shared UI components
│   └── config/       # Shared configs
├── services/
│   └── ai-engine-adapter/
└── infrastructure/
    ├── docker/
    └── kubernetes/
🚀 Bắt đầu
Prerequisites
Node.js >= 18.0.0
PNPM >= 8.0.0
Docker & Docker Compose
Cài đặt
bash
# Clone repository
git clone <your-repo-url>
cd homeguard-platform

# Cài đặt dependencies
pnpm install

# Copy environment variables
cp .env.example .env

# Khởi động database
docker compose up -d postgres redis
Development
bash
# Build tất cả packages
pnpm build

# Chạy lint
pnpm lint

# Format code
pnpm format

# Type check
pnpm type-check

# Development mode (khi đã có apps)
pnpm dev
Docker
bash
# Chỉ chạy database
docker compose up -d

# Chạy full stack (khi đã hoàn thiện)
docker compose --profile full up
📋 Lộ trình phát triển
✅ Phase 1 (Tuần 1-2): Core Foundation
⏳ Phase 2 (Tuần 2-3): Backend Core
⏳ Phase 3 (Tuần 3-4): Device & AI Integration
⏳ Phase 4 (Tuần 4-5): Frontend MVP
⏳ Phase 5 (Tuần 6-10): Advanced Features & Deployment
📚 Tài liệu
Architecture
API Documentation
WebSocket Protocol
Deployment Guide
🤝 Contributing
Xem CONTRIBUTING.md để biết thêm chi tiết.

📝 License
MIT License - xem LICENSE để biết thêm chi tiết.

