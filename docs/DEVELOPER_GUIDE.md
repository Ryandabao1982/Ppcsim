# Developer Quick Start Guide
## Amazon PPC Simulator

**Get up and running in 15 minutes!**

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Node.js 18.x or higher** - [Download](https://nodejs.org/)
- ✅ **PostgreSQL 15.x** - [Download](https://www.postgresql.org/download/)
- ✅ **Redis 7.x** - [Download](https://redis.io/download)
- ✅ **Git** - [Download](https://git-scm.com/downloads)
- ✅ **VS Code** (recommended) - [Download](https://code.visualstudio.com/)

**OR**

- ✅ **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop)

---

## Quick Start (Docker - Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/Ryandabao1982/Ppcsim.git
cd Ppcsim
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env
```

**Minimal .env configuration:**
```env
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ppcsim"

# Redis
REDIS_URL="redis://localhost:6379"

# JWT Secret (generate a random string)
JWT_SECRET="your-super-secret-jwt-key-change-this"

# Application
NODE_ENV="development"
PORT=3001
FRONTEND_URL="http://localhost:3000"
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Run Database Migrations

```bash
# Run migrations
docker-compose exec backend npm run migrate

# Seed database (optional)
docker-compose exec backend npm run seed
```

### 5. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:3001
- **API Documentation:** http://localhost:3001/api-docs

**Default login:**
```
Email: demo@ppcsimulator.com
Password: Demo123!
```

---

## Manual Setup (Without Docker)

### 1. Clone and Install Dependencies

```bash
# Clone repository
git clone https://github.com/Ryandabao1982/Ppcsim.git
cd Ppcsim

# Install root dependencies
npm install

# Install backend dependencies
cd src/backend
npm install

# Install frontend dependencies
cd ../frontend
npm install

# Return to root
cd ../..
```

### 2. Set Up PostgreSQL Database

```bash
# Create database
createdb ppcsim

# Or using psql
psql -U postgres
CREATE DATABASE ppcsim;
\q
```

### 3. Set Up Redis

```bash
# Start Redis server
redis-server

# Or on macOS with Homebrew
brew services start redis

# Or on Linux
sudo systemctl start redis
```

### 4. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit configuration
nano .env
```

### 5. Run Database Migrations

```bash
# Navigate to backend
cd src/backend

# Run Prisma migrations
npx prisma migrate dev

# Generate Prisma Client
npx prisma generate

# Seed database (optional)
npm run seed
```

### 6. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd src/backend
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend
npm run dev
```

**Terminal 3 - Simulation Worker (optional):**
```bash
cd src/backend
npm run worker
```

---

## Development Workflow

### Daily Development

```bash
# Pull latest changes
git pull origin main

# Install any new dependencies
npm install

# Run migrations if schema changed
npm run migrate

# Start development servers
npm run dev
```

### Creating a New Feature

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code, code, code ...

# Run linter
npm run lint

# Run tests
npm test

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

---

## Project Structure (When Implemented)

```
Ppcsim/
├── src/
│   ├── backend/              # Backend API
│   │   ├── controllers/      # Route controllers
│   │   ├── services/         # Business logic
│   │   ├── models/           # Data models
│   │   ├── middleware/       # Express middleware
│   │   ├── routes/           # API routes
│   │   ├── utils/            # Utilities
│   │   ├── config/           # Configuration
│   │   └── server.ts         # Entry point
│   │
│   ├── frontend/             # React frontend
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── store/            # Redux store
│   │   ├── services/         # API services
│   │   ├── hooks/            # Custom hooks
│   │   ├── utils/            # Utilities
│   │   └── App.tsx           # Entry point
│   │
│   └── database/             # Database files
│       ├── migrations/       # Prisma migrations
│       ├── seeds/            # Database seeds
│       └── schema.prisma     # Prisma schema
│
├── tests/                    # Test files
├── docs/                     # Documentation
├── .github/                  # GitHub config
└── docker-compose.yml        # Docker setup
```

---

## Common Commands

### Database

```bash
# Create migration
npm run migrate:create

# Run migrations
npm run migrate

# Reset database
npm run migrate:reset

# Open Prisma Studio (DB GUI)
npm run db:studio

# Seed database
npm run seed
```

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- path/to/test.spec.ts
```

### Linting & Formatting

```bash
# Run ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting
npm run format:check
```

### Build

```bash
# Build backend
cd src/backend
npm run build

# Build frontend
cd src/frontend
npm run build

# Build both
npm run build:all
```

---

## Debugging

### VS Code Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Backend",
      "skipFiles": ["<node_internals>/**"],
      "program": "${workspaceFolder}/src/backend/server.ts",
      "preLaunchTask": "tsc: build - tsconfig.json",
      "outFiles": ["${workspaceFolder}/src/backend/dist/**/*.js"]
    }
  ]
}
```

### Debugging Tips

**Backend:**
- Add breakpoints in VS Code
- Use `console.log()` for quick debugging
- Check logs in terminal
- Use Postman/Insomnia for API testing

**Frontend:**
- Use React Developer Tools browser extension
- Use Redux DevTools browser extension
- Chrome DevTools for debugging
- Check Network tab for API calls

**Database:**
- Use Prisma Studio: `npm run db:studio`
- Use pgAdmin for PostgreSQL
- Check query logs in terminal

---

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in .env file
```

**Database Connection Failed:**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
# Ensure database exists
psql -U postgres -l
```

**Redis Connection Failed:**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
redis-server
```

**Prisma Client Not Found:**
```bash
# Regenerate Prisma Client
npx prisma generate
```

**Module Not Found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**TypeScript Errors:**
```bash
# Rebuild TypeScript
npm run build

# Check tsconfig.json for issues
```

---

## Useful Resources

### Documentation
- [React Docs](https://react.dev)
- [Node.js Docs](https://nodejs.org/docs)
- [Express.js Docs](https://expressjs.com)
- [Prisma Docs](https://www.prisma.io/docs)
- [TypeScript Docs](https://www.typescriptlang.org/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs)

### Tools
- [Postman](https://www.postman.com) - API testing
- [pgAdmin](https://www.pgadmin.org) - PostgreSQL GUI
- [Redis Commander](http://joeferner.github.io/redis-commander/) - Redis GUI
- [Prisma Studio](https://www.prisma.io/studio) - Database GUI

---

## Getting Help

### In the Codebase
- Check `/docs` directory for detailed documentation
- Read code comments
- Look at test files for examples

### External Resources
- **GitHub Issues:** Report bugs or ask questions
- **Stack Overflow:** Search for similar issues
- **Discord/Slack:** Join community channels (coming soon)

### Contact
- **Email:** dev-support@ppcsimulator.com
- **GitHub:** https://github.com/Ryandabao1982/Ppcsim

---

## Next Steps

1. ✅ Complete the setup above
2. 📖 Read the [User Guide](docs/user-guide/USER_GUIDE.md)
3. 🏗️ Review the [Architecture](docs/technical/ARCHITECTURE.md)
4. 📝 Check the [PRD](docs/PRD.md) for features to implement
5. 🎯 Pick an issue from GitHub Issues
6. 💻 Start coding!

---

**Happy Coding! 🚀**

If you encounter any issues, please:
1. Check the troubleshooting section above
2. Search existing GitHub Issues
3. Create a new issue if needed

Welcome to the team! 🎉
