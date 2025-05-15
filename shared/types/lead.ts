/**
 * Shared type definitions for leads
 */

export interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  predicted_email?: string;
  email_confidence?: number;
  title?: string;
  company: string;
  company_domain?: string;
  company_size?: string;
  industry?: string;
  location?: string;
  phone?: string;
  linkedin_url?: string;
  twitter_url?: string;
  website_url?: string;
  source?: string;
  notes?: string;
  status: string;
  score: number;
  enrichment_data?: any;
  created_at: string;
  updated_at?: string;
  project_id: number;
  owner_id: number;
}

export interface LeadSearchParams {
  industry?: string;
  title?: string;
  location?: string;
  company_size?: string;
  keywords?: string;
  project_id?: number;
  min_score?: number;
  status?: string;
  limit?: number;
  offset?: number;
}

export interface LeadCreate {
  first_name: string;
  last_name: string;
  email?: string;
  title?: string;
  company: string;
  company_domain?: string;
  company_size?: string;
  industry?: string;
  location?: string;
  linkedin_url?: string;
  source?: string;
  notes?: string;
  project_id: number;
}

export interface LeadUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  title?: string;
  company?: string;
  company_domain?: string;
  company_size?: string;
  industry?: string;
  location?: string;
  phone?: string;
  linkedin_url?: string;
  twitter_url?: string;
  website_url?: string;
  source?: string;
  notes?: string;
  status?: string;
  score?: number;
  enrichment_data?: any;
}

export interface LeadEnrichRequest {
  lead_id: number;
}

export interface LeadBatchEnrichRequest {
  lead_ids: number[];
  project_id?: number;
}

export interface LeadScoreExplanation {
  score: number;
  reasons: string[];
  factors: {
    [key: string]: {
      value: any;
      importance: number;
    }
  };
}

export interface LeadWithScore extends Lead {
  score_explanation?: LeadScoreExplanation;
}
