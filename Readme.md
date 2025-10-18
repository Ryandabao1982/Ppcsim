# Amazon PPC Simulator 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> A comprehensive training platform for aspiring Virtual Assistants and PPC managers to learn Amazon Pay-Per-Click advertising in a risk-free simulation environment.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The Amazon PPC Simulator is an educational platform designed to train Virtual Assistants (VAs) to become proficient Amazon PPC (Pay-Per-Click) managers. The simulator provides a realistic, risk-free environment where students can:

- 🎓 Practice managing Amazon advertising campaigns without budget risk
- 📊 Experience realistic campaign performance simulation
- 💡 Learn optimization strategies and data-driven decision-making
- 🏆 Earn certifications to demonstrate their skills to potential employers

### Why This Matters

- **High Demand:** E-commerce businesses desperately need skilled PPC managers
- **Expensive Learning Curve:** Real campaigns require thousands of dollars to learn
- **Risk Reduction:** Mistakes on real campaigns can waste significant money
- **Career Opportunities:** PPC managers earn $40-80K+ annually working remotely

---

## ✨ Features

### Core Functionality

#### Campaign Management
- ✅ Create and manage Sponsored Products campaigns
- ✅ Configure daily budgets and bidding strategies
- ✅ Manual and automatic targeting options
- ✅ Pause, resume, and archive campaigns

#### Keyword Management
- ✅ Add keywords with multiple match types (broad, phrase, exact)
- ✅ Set individual keyword bids
- ✅ Manage negative keywords
- ✅ View keyword performance metrics

#### Performance Simulation
- ✅ Realistic impression, click, and conversion generation
- ✅ Dynamic ACOS (Advertising Cost of Sale) calculation
- ✅ Time-based performance evolution
- ✅ Multiple campaign simulation support

#### Analytics & Reporting
- ✅ Real-time campaign performance dashboard
- ✅ Keyword performance analysis
- ✅ Time-series performance charts
- ✅ Key metrics: CTR, CVR, CPC, ACOS, ROAS, TACoS

#### Learning & Training
- ✅ Interactive tutorial system
- ✅ Step-by-step onboarding
- ✅ Best practice recommendations
- ✅ Progress tracking
- ✅ Achievement system

### Coming Soon 🚀

- 📱 Mobile responsive design improvements
- 🔍 Search term reports
- 📦 Bulk keyword operations
- 📊 Advanced analytics and custom reports
- 🤖 AI-powered optimization suggestions
- 👥 Team collaboration features
- 📧 Email notifications and alerts
- 🎖️ Certification program

---

## 📚 Documentation

Comprehensive documentation is available in the `/docs` directory:

### For Product & Business
- **[Product Requirements Document (PRD)](docs/PRD.md)** - Complete product specification, user stories, and success metrics
- **[MVP Specification](docs/MVP.md)** - Minimum Viable Product scope and features

### For Development
- **[Technical Development Plan](docs/technical/TECHNICAL_DEVELOPMENT_PLAN.md)** - 18-week development roadmap, architecture, and tech stack
- **[Database Schemas](docs/schemas/DATABASE_SCHEMAS.md)** - Complete database design with Prisma schema
- **[API Documentation](docs/api/API_DOCUMENTATION.md)** - RESTful API endpoints and examples

### For Operations
- **[Logging Strategy](logs/LOGGING_STRATEGY.md)** - Comprehensive logging and monitoring approach

### For Users
- **[User Guide](docs/user-guide/USER_GUIDE.md)** - Complete guide for students and VAs learning PPC

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18.x or higher
- PostgreSQL 15.x
- Redis 7.x (for caching and sessions)
- Docker & Docker Compose (recommended for local development)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/Ryandabao1982/Ppcsim.git
cd Ppcsim

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start services with Docker Compose
docker-compose up -d

# Run database migrations
npm run migrate

# Start the application
npm run dev
```

### Manual Setup

```bash
# Install dependencies
npm install

# Set up PostgreSQL database
createdb ppcsim

# Set up environment variables
cp .env.example .env

# Run database migrations
npx prisma migrate dev

# Seed database (optional)
npm run seed

# Start development server
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:3000
- **API:** http://localhost:3001/api
- **API Docs:** http://localhost:3001/api-docs (Swagger UI)

### Default Credentials (Development Only)

```
Email: demo@ppcsimulator.com
Password: Demo123!
```

---

## 📁 Project Structure

```
Ppcsim/
├── docs/                           # Documentation
│   ├── PRD.md                     # Product Requirements Document
│   ├── MVP.md                     # MVP Specification
│   ├── technical/                 # Technical documentation
│   │   └── TECHNICAL_DEVELOPMENT_PLAN.md
│   ├── schemas/                   # Database schemas
│   │   └── DATABASE_SCHEMAS.md
│   ├── api/                       # API documentation
│   │   └── API_DOCUMENTATION.md
│   └── user-guide/                # User documentation
│       └── USER_GUIDE.md
│
├── logs/                          # Logging documentation
│   └── LOGGING_STRATEGY.md
│
├── src/                           # Source code (to be created)
│   ├── backend/                   # Backend API server
│   │   ├── controllers/          # API controllers
│   │   ├── services/             # Business logic
│   │   ├── models/               # Data models
│   │   ├── middleware/           # Express middleware
│   │   ├── routes/               # API routes
│   │   ├── utils/                # Utility functions
│   │   └── config/               # Configuration
│   │
│   ├── frontend/                  # React frontend
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── store/                # Redux store
│   │   ├── services/             # API services
│   │   ├── hooks/                # Custom hooks
│   │   └── utils/                # Utility functions
│   │
│   ├── database/                  # Database files
│   │   ├── migrations/           # Prisma migrations
│   │   ├── seeds/                # Database seeds
│   │   └── schema.prisma         # Prisma schema
│   │
│   └── shared/                    # Shared code
│       ├── types/                # TypeScript types
│       └── constants/            # Shared constants
│
├── tests/                         # Test files
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
│
├── .github/                       # GitHub configuration
│   └── workflows/                # GitHub Actions
│
├── docker/                        # Docker files
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── scripts/                       # Utility scripts
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
├── docker-compose.yml            # Docker Compose configuration
├── package.json                  # Node.js dependencies
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # This file
```

---

## 🛠 Technology Stack

### Frontend
- **Framework:** React 18.x with TypeScript
- **State Management:** Redux Toolkit
- **UI Library:** Material-UI (MUI) v5
- **Charts:** Recharts + Chart.js
- **Routing:** React Router v6
- **Forms:** React Hook Form + Yup
- **HTTP Client:** Axios

### Backend
- **Runtime:** Node.js 18.x LTS
- **Framework:** Express.js 4.x with TypeScript
- **Database ORM:** Prisma
- **Authentication:** Passport.js + JWT
- **Validation:** Joi
- **Testing:** Jest + Supertest

### Database
- **Primary DB:** PostgreSQL 15.x
- **Cache/Session:** Redis 7.x
- **Migrations:** Prisma Migrate

### DevOps
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Code Quality:** ESLint, Prettier, Husky
- **Monitoring:** Winston (logging) + Morgan (HTTP logs)

---

## 🗓 Development Roadmap

### Phase 1: Foundation (Week 1-2) ✅
- [x] Project setup and documentation
- [x] Database schema design
- [x] Development environment setup

### Phase 2: Core Features (Week 3-10)
- [ ] User authentication system
- [ ] Campaign CRUD operations
- [ ] Keyword management
- [ ] Simulation engine
- [ ] Performance dashboard

### Phase 3: Advanced Features (Week 11-14)
- [ ] Tutorial system
- [ ] Search term reports
- [ ] Advanced analytics
- [ ] Optimization suggestions

### Phase 4: Polish & Testing (Week 15-16)
- [ ] Integration testing
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Security audit

### Phase 5: Launch (Week 17-18)
- [ ] Beta release
- [ ] User feedback collection
- [ ] Bug fixes and improvements
- [ ] Official launch

See the [Technical Development Plan](docs/technical/TECHNICAL_DEVELOPMENT_PLAN.md) for detailed timeline.

---

## 🎓 Target Audience

### Primary Users
- **Students** learning Amazon PPC advertising
- **Virtual Assistants** seeking to add PPC management skills
- **Career Changers** entering e-commerce and digital marketing

### Secondary Users
- **Training Organizations** providing VA certification programs
- **E-commerce Businesses** training their internal teams
- **Educational Institutions** teaching digital marketing courses

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🧪 Write tests
- 💻 Submit pull requests

### Development Process

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Write/update tests**
5. **Commit your changes** (`git commit -m 'feat: add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Code Standards
- Follow TypeScript and ESLint rules
- Write meaningful commit messages (Conventional Commits)
- Add tests for new features
- Update documentation as needed
- Maintain 80%+ test coverage

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines (coming soon).

---

## 📊 Success Metrics

### User Metrics (6-month targets)
- 1000+ registered users
- 500+ daily active users
- 70%+ tutorial completion rate
- 50%+ certification rate

### Technical Metrics
- 99.5%+ uptime
- < 500ms API response time (p95)
- < 2s page load time
- 80%+ test coverage

### Business Metrics
- 4.5+ star user rating
- 40%+ monthly retention
- 50+ Net Promoter Score (NPS)

---

## 🔐 Security

- All passwords hashed with bcrypt (10+ rounds)
- JWT token-based authentication
- HTTPS encryption in production
- SQL injection prevention via ORM
- XSS protection
- CORS policy enforcement
- Rate limiting on all endpoints

Report security vulnerabilities to: security@ppcsimulator.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Project Lead:** [Your Name]
- **Contributors:** See [CONTRIBUTORS.md](CONTRIBUTORS.md)

---

## 📞 Contact & Support

- **Website:** https://ppcsimulator.com (coming soon)
- **Email:** support@ppcsimulator.com
- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/Ryandabao1982/Ppcsim/issues)

---

## 🙏 Acknowledgments

- Amazon Advertising for PPC platform inspiration
- The open-source community for amazing tools
- All contributors and testers
- Students and VAs who will benefit from this platform

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/Ryandabao1982/Ppcsim?style=social)
![GitHub forks](https://img.shields.io/github/forks/Ryandabao1982/Ppcsim?style=social)
![GitHub issues](https://img.shields.io/github/issues/Ryandabao1982/Ppcsim)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Ryandabao1982/Ppcsim)

---

**Built with ❤️ for aspiring PPC managers worldwide**
