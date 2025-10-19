export type MatchType = 'BROAD' | 'PHRASE' | 'EXACT';

export interface Keyword {
  id: number;
  campaignId: number;
  adGroupId: number;
  keywordText: string;
  matchType: MatchType;
  bid: number;
  status: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  isNegative: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateKeywordData {
  campaignId: number;
  adGroupId: number;
  keywordText: string;
  matchType: MatchType;
  bid: number;
  isNegative?: boolean;
}

export interface UpdateKeywordData {
  keywordText?: string;
  matchType?: MatchType;
  bid?: number;
  status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  isNegative?: boolean;
}

export type BulkKeywordOperation =
  | {
      keywordIds: number[];
      operation: 'updateBids';
      newBid: number;
    }
  | {
      keywordIds: number[];
      operation: 'pause' | 'activate' | 'archive';
    };
