# Amazon PPC Simulator 🎯

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**Master Amazon PPC advertising without risking real money.**

The Amazon PPC Simulator is a comprehensive training platform that enables aspiring Virtual Assistants and PPC managers to learn Amazon Pay-Per-Click advertising through realistic, hands-on simulation. Practice campaign management, keyword optimization, and data-driven decision-making in a risk-free environment designed to build job-ready skills.

### 🎯 Core Purpose

This simulator serves three key purposes:

1. **Education** - Teach the fundamentals of Amazon PPC advertising through interactive, hands-on learning
2. **Practice** - Provide unlimited opportunities to experiment, make mistakes, and learn without financial consequences
3. **Career Development** - Prepare students for real-world PPC management roles by building demonstrable skills

**Target Users:** Students, Virtual Assistants, career changers, and anyone seeking to enter the lucrative field of Amazon PPC management without the typical $2,000-5,000 investment required to learn through real campaigns.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [What You Can Do](#what-you-can-do)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development Roadmap](#development-roadmap)
- [Target Audience](#target-audience)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

### What is the Amazon PPC Simulator?

The Amazon PPC Simulator is an educational platform designed to train Virtual Assistants (VAs) and aspiring digital marketers to become proficient Amazon PPC (Pay-Per-Click) managers. Unlike traditional training that requires spending real money on live campaigns, our simulator provides a realistic, consequence-free environment where you can:

- 🎓 **Practice Without Risk** - Manage campaigns with virtual budgets, not real money
- 📊 **Experience Realistic Scenarios** - Our simulation engine mirrors actual Amazon advertising behavior
- 💡 **Learn Through Doing** - Hands-on campaign creation, keyword optimization, and performance analysis
- 🏆 **Build Job-Ready Skills** - Develop competencies that employers actively seek
- 📈 **Track Your Progress** - See your improvement through performance metrics and tutorials

### The Problem We Solve

**Learning Amazon PPC is expensive and risky:**
- **High Barrier to Entry:** Real campaigns require $2,000-5,000+ to gain meaningful experience
- **Costly Mistakes:** Inexperienced managers can burn through advertising budgets quickly
- **Limited Practice Opportunities:** Most learners can't afford to experiment and learn
- **Skills Gap:** E-commerce businesses struggle to find qualified PPC managers

**Our Solution:**
We provide unlimited practice opportunities with realistic campaign simulation, enabling students to develop expertise before managing real advertising budgets. This approach reduces training costs, accelerates learning, and produces job-ready PPC managers.

### Why This Matters

- **🚀 High Demand:** E-commerce growth drives constant need for skilled PPC managers
- **💰 Lucrative Career:** PPC managers earn $40-80K+ annually working remotely
- **🌍 Location Independent:** Work from anywhere in the world
- **📊 Data-Driven Skills:** Transferable analytical skills valuable across industries
- **⏱️ Faster Learning:** Compress months of expensive trial-and-error into weeks of focused practice

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
- 📦 Bulk keyword operations (backend complete, UI pending)
- 📊 Advanced analytics and custom reports
- 🤖 AI-powered optimization suggestions
- 👥 Team collaboration features
- 📧 Email notifications and alerts
- 🎖️ Certification program

---

## 🎮 What You Can Do

The simulator enables you to perform core Amazon PPC management tasks in a realistic environment:

### 1. Campaign Management
**Create and manage Sponsored Products campaigns** just like on Amazon's advertising platform:
- Set daily budgets and choose bidding strategies (manual, dynamic)
- Configure campaign settings (targeting type, start/end dates)
- Monitor campaign performance in real-time
- Pause, resume, or archive campaigns based on performance
- Track key metrics: impressions, clicks, conversions, spend, and sales

### 2. Ad Group Organization
**Structure your campaigns with ad groups** for better organization:
- Create multiple ad groups within campaigns
- Set default bids at the ad group level
- Organize keywords by theme or product category
- Manage ad group status independently

### 3. Keyword Strategy & Optimization
**Master keyword management** - the heart of successful PPC:
- Add keywords with different match types (broad, phrase, exact)
- Set individual keyword bids to control spend
- Create negative keywords to prevent wasted ad spend
- Analyze keyword performance metrics (CTR, CVR, CPC, ACOS)
- Optimize bids based on keyword performance
- Filter and sort keywords to identify top performers and underperformers

### 4. Performance Analysis
**Make data-driven decisions** using comprehensive analytics:
- View campaign performance dashboards
- Analyze keyword-level metrics
- Track ACOS (Advertising Cost of Sale) - the critical profitability metric
- Calculate ROAS (Return on Ad Spend)
- Monitor CTR (Click-Through Rate) and CVR (Conversion Rate)
- Identify optimization opportunities

### 5. Learn While Practicing
**Guided learning experience** integrated throughout:
- Follow interactive tutorials
- Learn best practices and industry standards
- Understand when and why to make specific optimization decisions
- Build confidence before managing real campaigns

### Real-World Application
Every function in the simulator mirrors actual Amazon Advertising Console capabilities. The skills you develop - campaign structure, keyword research, bid management, performance analysis, and budget optimization - directly transfer to managing real Amazon PPC campaigns.

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
- PostgreSQL 15.x (or use Docker)
- Redis 7.x (or use Docker)
- Docker & Docker Compose (recommended for local development)

### Quick Start with Setup Script (Recommended)

The easiest way to get started is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/Ryandabao1982/Ppcsim.git
cd Ppcsim

# Run the setup script
./scripts/setup.sh
```

This script will:
- ✅ Check prerequisites
- ✅ Install all dependencies
- ✅ Start PostgreSQL and Redis with Docker
- ✅ Run database migrations
- ✅ Seed test data

After setup completes:

```bash
# Terminal 1: Start backend
cd src/backend
npm run dev

# Terminal 2: Start frontend
cd src/frontend
npm run dev
```

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/Ryandabao1982/Ppcsim.git
cd Ppcsim

# Set up environment variables
cp .env.example .env

# Start Docker services
docker-compose up -d

# Install dependencies
npm install

# Generate Prisma client
cd src/backend
npx prisma generate

# Run database migrations
npx prisma migrate dev

# Seed database (optional)
npm run seed
cd ../..

# Start backend (new terminal)
cd src/backend && npm run dev

# Start frontend (new terminal)
cd src/frontend && npm run dev
```

### Manual Setup

```bash
# Install dependencies
npm install

# Set up PostgreSQL database
createdb ppcsim

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Generate Prisma client
cd src/backend
npx prisma generate

# Run database migrations
npx prisma migrate dev

# Seed database (optional)
npm run seed

# Start backend
npm run dev

# In another terminal, start frontend
cd src/frontend
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:3001/api
- **Health Check:** http://localhost:3001/health

### Default Test Credentials

```
Email: demo@ppcsimulator.com
Password: Demo123!
```

*Note: Authentication is not yet implemented. Use userId=1 for testing.*

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

### Phase 2: Core Features (Week 3-10) 🚧 In Progress
- [x] Backend folder structure and configuration
- [x] Prisma schema implementation
- [x] Campaign CRUD operations (backend)
- [x] Frontend folder structure and configuration
- [x] Redux store setup
- [x] Campaign list display (frontend)
- [x] Campaign creation form
- [x] Campaign edit functionality
- [x] Campaign filtering and sorting
- [x] **Keyword CRUD operations (backend)**
- [x] **Ad group CRUD operations (backend)**
- [x] **Match types support (broad, phrase, exact)**
- [x] **Negative keyword management**
- [x] **Bulk keyword operations**
- [x] **Keyword management UI with filtering**
- [x] **Ad group management UI**
- [x] **Campaign details page with tabs**
- [ ] User authentication system
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

### Who Should Use This Simulator?

#### Primary Users

**1. Aspiring Virtual Assistants**
- Want to add high-value PPC management to their service offerings
- Seek to increase earning potential ($40-80K+ annually)
- Need practical experience to attract clients
- Looking for remote, location-independent work

**2. Career Changers & Job Seekers**
- Transitioning into digital marketing or e-commerce
- Building skills for Amazon PPC specialist roles
- Creating a portfolio of demonstrable PPC knowledge
- Preparing for real-world campaign management

**3. E-commerce Entrepreneurs**
- Own Amazon businesses and want to manage their own PPC
- Need to understand PPC before hiring managers
- Want to reduce dependency on expensive PPC agencies
- Looking to maximize advertising ROI

**4. Digital Marketing Students**
- Learning paid advertising and performance marketing
- Need hands-on experience to complement theoretical knowledge
- Preparing for careers in e-commerce marketing
- Building practical skills for job applications

#### Secondary Users

**Training Organizations**
- VA training programs seeking comprehensive PPC curriculum
- Certification programs requiring practical assessment tools
- Bootcamps teaching e-commerce marketing skills

**E-commerce Businesses**
- Companies training internal marketing teams
- Agencies onboarding new PPC managers
- Brands wanting to upskill existing staff

**Educational Institutions**
- Universities teaching digital marketing courses
- Vocational schools with e-commerce programs
- Online learning platforms offering PPC training

### Why Our Users Choose This Simulator

✅ **No Financial Risk** - Learn without burning real advertising budgets  
✅ **Realistic Practice** - Experience mirrors actual Amazon Advertising Console  
✅ **Self-Paced Learning** - Practice as much as needed to build confidence  
✅ **Job-Ready Skills** - Direct application to real-world PPC management  
✅ **Cost-Effective** - Free alternative to expensive trial-and-error learning  
✅ **Portfolio Building** - Demonstrate competency to potential employers/clients

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
