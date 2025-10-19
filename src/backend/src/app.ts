import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { config } from './config';
import { logger, httpLogStream } from './utils/logger';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';

// Import routes
// import authRoutes from './routes/auth.routes';
import campaignRoutes from './routes/campaign.routes';
import keywordRoutes from './routes/keyword.routes';
import adGroupRoutes from './routes/adGroup.routes';

export const createApp = (): Express => {
  const app = express();

  // Security middleware
  app.use(helmet());
  
  // CORS
  app.use(cors({
    origin: config.cors.origin,
    credentials: true,
  }));

  // Body parsing
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // HTTP logging
  app.use(morgan('combined', { stream: httpLogStream }));

  // Health check
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  // API routes
  // app.use(`${config.apiPrefix}/auth`, authRoutes);
  app.use(`${config.apiPrefix}/campaigns`, campaignRoutes);
  
  // Nested routes for campaigns
  app.use(`${config.apiPrefix}/campaigns/:campaignId/keywords`, keywordRoutes);
  app.use(`${config.apiPrefix}/campaigns/:campaignId/adgroups`, adGroupRoutes);

  // Error handlers (must be last)
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
};
