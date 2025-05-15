/**
 * Shared type definitions for projects
 */

import { Lead } from './lead';

export interface Project {
  id: number;
  name: string;
  description?: string;
  target_industry?: string;
  target_company_size?: string;
  target_locations?: string;
  target_titles?: string;
  search_keywords?: string;
  config?: Record<string, any>;
  lead_count: number;
  email_sent_count: number;
  created_at: string;
  updated_at?: string;
  owner_id: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  target_industry?: string;
  target_company_size?: string;
  target_locations?: string;
  target_titles?: string;
  search_keywords?: string;
  config?: Record<string, any>;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  target_industry?: string;
  target_company_size?: string;
  target_locations?: string;
  target_titles?: string;
  search_keywords?: string;
  config?: Record<string, any>;
}

export interface ProjectScrapingRequest {
  project_id: number;
  max_results?: number;
}

export interface ProjectStats {
  total_leads: number;
  high_quality_leads: number;
  leads_contacted: number;
  total_emails_sent: number;
  response_rate: number;
  latest_leads: Lead[];
}
