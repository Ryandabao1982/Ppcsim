/**
 * This file contains the core logic for generating AI-powered feedback
 * on a user's PPC campaign setup. It uses a rule-based approach to analyze
 * different aspects of the campaign.
 */

// --- Helper Data & Constants ---

// We can use the product data to give more specific bid feedback.
// In a real app, this would be managed more dynamically.
const productData = {
    "SKU-001": { name: "Wireless Earbuds", defaultBidRange: [0.5, 1.5] },
    "SKU-002": { name: "Yoga Mat", defaultBidRange: [0.8, 2.0] },
    "SKU-003": { name: "Coffee Grinder", defaultBidRange: [1.0, 2.5] },
};

const MIN_BUDGET = 10;
const MIN_KEYWORDS = 3;
const MAX_KEYWORDS = 20;

/**
 * Generates feedback for a given campaign configuration.
 * @param {object} campaign - The complete campaign configuration object.
 * @returns {object} A feedback object with score, strengths, weaknesses, and pro-tips.
 */
export const generateFeedback = (campaign) => {
    let score = 100;
    const strengths = [];
    const weaknesses = [];
    const proTips = [];

    // --- Rule-based checks ---

    // 1. Budget Analysis
    if (campaign.dailyBudget >= MIN_BUDGET) {
        strengths.push(`A daily budget of $${campaign.dailyBudget} is a solid start for gathering performance data.`);
    } else {
        weaknesses.push(`A budget of $${campaign.dailyBudget} is quite low. It may not be enough to get consistent traffic.`);
        score -= 15;
        proTips.push("Consider increasing your daily budget to at least $10-$20 to ensure your ads are shown more frequently.");
    }

    // Assume one ad group for now, as per our UI flow
    const adGroup = campaign.adGroups[0];

    // 2. Naming Convention Analysis
    if (campaign.campaignName && (campaign.campaignName.toLowerCase().includes('test') || campaign.campaignName.length < 5)) {
        weaknesses.push("Your campaign name is generic. Descriptive names help with organization.");
        score -= 5;
    } else {
        strengths.push("Your campaign name is descriptive and easy to identify. Great for organization!");
    }

    if (adGroup.adGroupName && (adGroup.adGroupName.toLowerCase().includes('test') || adGroup.adGroupName.length < 5)) {
        weaknesses.push("Your ad group name is generic. Specific names help you know what's inside at a glance.");
        score -= 5;
    }

    // 3. Targeting Analysis (Manual vs. Auto)
    if (campaign.campaignType === 'manual') {
        const keywords = adGroup.targeting.manualKeywords || [];

        if (keywords.length < MIN_KEYWORDS) {
            weaknesses.push(`You only have ${keywords.length} keyword(s). This severely limits your reach.`);
            score -= 20;
            proTips.push(`Aim for at least ${MIN_KEYWORDS}-${MAX_KEYWORDS} relevant keywords in an ad group to start.`);
        } else if (keywords.length > MAX_KEYWORDS) {
            weaknesses.push(`You have ${keywords.length} keywords. This might be too broad for a single ad group.`);
            score -= 10;
            proTips.push("If you have many keywords, consider splitting them into more tightly-themed ad groups.");
        } else {
            strengths.push(`A set of ${keywords.length} keywords is a good starting point for a targeted ad group.`);
        }

        const matchTypes = new Set(keywords.map(kw => kw.matchType));
        if (matchTypes.size === 1 && keywords.length > 1) {
            weaknesses.push(`You're only using one match type ('${[...matchTypes][0]}'). This can be inflexible.`);
            score -= 10;
            proTips.push("Try using a mix of 'phrase' and 'exact' match keywords to balance reach and precision.");
        } else if (matchTypes.size > 1) {
            strengths.push("Great job using multiple match types! This gives you a good mix of control and reach.");
        }

    } else { // Auto campaign
        const autoTargets = adGroup.targeting.autoTargeting || {};
        const enabledTargets = Object.values(autoTargets).filter(Boolean).length;
        if (enabledTargets <= 1) {
            weaknesses.push("You've only enabled one automatic targeting option. This can limit Amazon's ability to explore.");
            score -= 10;
        } else {
            strengths.push("Using multiple automatic targeting options allows Amazon to effectively explore different traffic sources.");
        }
        proTips.push("Auto campaigns are great for harvesting new, high-performing keywords. Check your search term report regularly!");
    }

    // 4. Bidding Analysis
    const bid = adGroup.defaultBid;
    if (bid < 0.5) {
        weaknesses.push(`Your default bid of $${bid} is very low and might not win many auctions.`);
        score -= 10;
    } else if (bid > 5) {
        weaknesses.push(`Your default bid of $${bid} is quite high. Be sure to monitor your costs closely.`);
        score -= 5; // Less severe, as high bids can be a strategy
    } else {
        strengths.push(`Your default bid of $${bid} is a reasonable starting point.`);
    }

    // Make sure score is not negative
    score = Math.max(0, score);

    // Add a final encouraging message
    proTips.push("Remember, PPC is all about testing and iterating. This is a great first step!");

    // Add emojis back for display
    return {
        score,
        strengths: strengths.map(s => `✅ ${s}`),
        weaknesses: weaknesses.map(w => `⚠️ ${w}`),
        proTips: proTips.map(p => `🚀 ${p}`)
    };
};
