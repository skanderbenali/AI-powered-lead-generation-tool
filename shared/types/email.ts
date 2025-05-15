/**
 * Shared type definitions for email campaigns and templates
 */

export interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  is_ai_generated: boolean;
  created_at: string;
  updated_at?: string;
}

export interface EmailTemplateCreate {
  name: string;
  subject: string;
  body: string;
  is_ai_generated?: boolean;
}

export interface EmailCampaign {
  id: number;
  name: string;
  description?: string;
  status: string;
  from_email: string;
  reply_to?: string;
  template_id: number;
  sent_count: number;
  open_count: number;
  click_count: number;
  reply_count: number;
  scheduled_at?: string;
  project_id: number;
  creator_id: number;
  created_at: string;
  updated_at?: string;
}

export interface EmailCampaignCreate {
  name: string;
  description?: string;
  status?: string;
  from_email: string;
  reply_to?: string;
  template_id: number;
  project_id: number;
  lead_ids: number[];
  scheduled_at?: string;
}

export interface EmailCampaignUpdate {
  name?: string;
  description?: string;
  status?: string;
  from_email?: string;
  reply_to?: string;
  template_id?: number;
  lead_ids?: number[];
  scheduled_at?: string;
}

export interface EmailGenerationRequest {
  lead_ids: number[];
  project_id: number;
  tone?: 'professional' | 'friendly' | 'casual';
  length?: 'short' | 'medium' | 'long';
  focus?: 'benefits' | 'problems' | 'curiosity';
  custom_instructions?: string;
}

export interface EmailMetrics {
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  replied: number;
  bounced: number;
  open_rate: number;
  click_rate: number;
  reply_rate: number;
  bounce_rate: number;
}

export interface EmailPredictionRequest {
  first_name: string;
  last_name: string;
  company_domain: string;
}

export interface EmailPredictionResult {
  predictions: Array<{
    email: string;
    format: string;
    confidence: number;
  }>;
  first_name: string;
  last_name: string;
  company_domain: string;
  format_analysis?: {
    primary_format: string;
    formats: string[];
    confidence: number;
    sample_size: number;
  };
}
