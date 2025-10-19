# Backend - Amazon PPC Simulator

Backend API server for the Amazon PPC Simulator.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp ../../.env.example ../../.env
# Edit .env with your database credentials
```

3. Generate Prisma client:
```bash
npm run prisma:generate
```

4. Run database migrations:
```bash
npm run migrate:dev
```

5. Seed the database (optional):
```bash
npm run seed
```

## Development

Start the development server:
```bash
npm run dev
```

The API will be available at `http://localhost:3001/api`

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm test` - Run tests
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix linting issues
- `npm run prisma:generate` - Generate Prisma client
- `npm run migrate:dev` - Run database migrations
- `npm run seed` - Seed database with test data

## API Endpoints

### Campaigns
- `POST /api/campaigns` - Create a new campaign
- `GET /api/campaigns` - Get all campaigns
- `GET /api/campaigns/:id` - Get a single campaign
- `PUT /api/campaigns/:id` - Update a campaign
- `DELETE /api/campaigns/:id` - Delete a campaign
- `GET /api/campaigns/:id/stats` - Get campaign statistics

## Tech Stack

- Node.js 18+
- Express.js
- TypeScript
- Prisma ORM
- PostgreSQL
- Winston (logging)
