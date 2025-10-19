import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('Starting database seeding...');

  // Create a test user
  const hashedPassword = await bcrypt.hash('Demo123!', 10);
  
  const user = await prisma.user.upsert({
    where: { email: 'demo@ppcsimulator.com' },
    update: {},
    create: {
      email: 'demo@ppcsimulator.com',
      passwordHash: hashedPassword,
      firstName: 'Demo',
      lastName: 'User',
      role: 'STUDENT',
      emailVerified: true,
      emailVerifiedAt: new Date(),
      status: 'ACTIVE',
    },
  });

  console.log('Created user:', user.email);

  // Create sample campaigns
  const campaign1 = await prisma.campaign.create({
    data: {
      userId: user.id,
      name: 'Summer Sale 2024',
      campaignType: 'SPONSORED_PRODUCTS',
      targetingType: 'MANUAL',
      dailyBudget: 50.00,
      status: 'ACTIVE',
      biddingStrategy: 'MANUAL',
      startDate: new Date('2024-06-01'),
      totalImpressions: BigInt(15000),
      totalClicks: 450,
      totalConversions: 23,
      totalSpend: 234.50,
      totalSales: 1250.75,
    },
  });

  const campaign2 = await prisma.campaign.create({
    data: {
      userId: user.id,
      name: 'Fall Collection Launch',
      campaignType: 'SPONSORED_PRODUCTS',
      targetingType: 'AUTOMATIC',
      dailyBudget: 75.00,
      status: 'ACTIVE',
      biddingStrategy: 'DYNAMIC_UP_DOWN',
      startDate: new Date('2024-09-01'),
      totalImpressions: BigInt(28500),
      totalClicks: 890,
      totalConversions: 67,
      totalSpend: 567.80,
      totalSales: 3250.25,
    },
  });

  const campaign3 = await prisma.campaign.create({
    data: {
      userId: user.id,
      name: 'Holiday Special',
      campaignType: 'SPONSORED_PRODUCTS',
      targetingType: 'MANUAL',
      dailyBudget: 100.00,
      status: 'PAUSED',
      biddingStrategy: 'MANUAL',
      startDate: new Date('2024-11-01'),
      endDate: new Date('2024-12-31'),
      totalBudget: 3000.00,
      totalImpressions: BigInt(5200),
      totalClicks: 125,
      totalConversions: 8,
      totalSpend: 98.45,
      totalSales: 425.00,
    },
  });

  console.log('Created campaigns:', [campaign1.name, campaign2.name, campaign3.name]);

  // Create ad groups for campaign1
  const adGroup1 = await prisma.adGroup.create({
    data: {
      campaignId: campaign1.id,
      name: 'Electronics Ad Group',
      defaultBid: 1.5,
      status: 'ACTIVE',
    },
  });

  const adGroup2 = await prisma.adGroup.create({
    data: {
      campaignId: campaign2.id,
      name: 'Fashion Ad Group',
      defaultBid: 2.0,
      status: 'ACTIVE',
    },
  });

  console.log('Created ad groups:', [adGroup1.name, adGroup2.name]);

  // Create keywords for ad groups
  const createdKeywords = await Promise.all([
    prisma.keyword.create({
      data: {
        campaignId: campaign1.id,
        adGroupId: adGroup1.id,
        keywordText: 'wireless headphones',
        matchType: 'PHRASE',
        bid: 1.75,
        status: 'ACTIVE',
        impressions: BigInt(5000),
        clicks: 150,
        conversions: 8,
        spend: 262.50,
        sales: 480.00,
      },
    }),
    prisma.keyword.create({
      data: {
        campaignId: campaign1.id,
        adGroupId: adGroup1.id,
        keywordText: 'bluetooth earbuds',
        matchType: 'EXACT',
        bid: 2.0,
        status: 'ACTIVE',
        impressions: BigInt(3500),
        clicks: 120,
        conversions: 10,
        spend: 240.00,
        sales: 550.00,
      },
    }),
    prisma.keyword.create({
      data: {
        campaignId: campaign2.id,
        adGroupId: adGroup2.id,
        keywordText: 'summer dress',
        matchType: 'BROAD',
        bid: 1.5,
        status: 'ACTIVE',
        impressions: BigInt(8000),
        clicks: 250,
        conversions: 20,
        spend: 375.00,
        sales: 1200.00,
      },
    }),
    // Negative keywords
    prisma.keyword.create({
      data: {
        campaignId: campaign1.id,
        keywordText: 'cheap',
        matchType: 'EXACT',
        bid: 0,
        status: 'ACTIVE',
        isNegative: true,
      },
    }),
    prisma.keyword.create({
      data: {
        campaignId: campaign1.id,
        keywordText: 'free',
        matchType: 'EXACT',
        bid: 0,
        status: 'ACTIVE',
        isNegative: true,
      },
    }),
  ]);

  console.log(`Created ${createdKeywords.length} keywords (including 2 negative keywords)`);

  console.log('Database seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
