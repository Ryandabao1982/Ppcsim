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

### Keywords
- `POST /api/campaigns/:campaignId/keywords` - Create a new keyword
- `POST /api/campaigns/:campaignId/keywords/bulk` - Bulk create keywords
- `GET /api/campaigns/:campaignId/keywords` - Get all keywords for a campaign
- `GET /api/campaigns/:campaignId/keywords/negative` - Get negative keywords
- `GET /api/campaigns/:campaignId/keywords/:id` - Get a single keyword
- `PUT /api/campaigns/:campaignId/keywords/:id` - Update a keyword
- `DELETE /api/campaigns/:campaignId/keywords/:id` - Delete a keyword
- `GET /api/campaigns/:campaignId/keywords/:id/stats` - Get keyword statistics

### Ad Groups
- `POST /api/campaigns/:campaignId/adgroups` - Create a new ad group
- `GET /api/campaigns/:campaignId/adgroups` - Get all ad groups for a campaign
- `GET /api/campaigns/:campaignId/adgroups/:id` - Get a single ad group
- `PUT /api/campaigns/:campaignId/adgroups/:id` - Update an ad group
- `DELETE /api/campaigns/:campaignId/adgroups/:id` - Delete an ad group

## Tech Stack

- Node.js 18+
- Express.js
- TypeScript
- Prisma ORM
- PostgreSQL
- Winston (logging)
