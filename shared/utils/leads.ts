/**
 * Utility functions for lead data
 */
import { Lead, LeadWithScore } from '../types/lead';

/**
 * Format a lead's name
 */
export function formatLeadName(lead: Lead): string {
  if (!lead) return '';
  
  if (lead.first_name && lead.last_name) {
    return `${lead.first_name} ${lead.last_name}`;
  } else if (lead.first_name) {
    return lead.first_name;
  } else if (lead.last_name) {
    return lead.last_name;
  }
  
  return 'Unknown';
}

/**
 * Get the lead score color class based on the score value
 */
export function getLeadScoreColorClass(score: number): string {
  if (score >= 90) return 'bg-green-100 text-green-800';
  if (score >= 80) return 'bg-blue-100 text-blue-800';
  if (score >= 70) return 'bg-yellow-100 text-yellow-800';
  if (score >= 60) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
}

/**
 * Format a lead score into a descriptive label
 */
export function formatLeadScoreLabel(score: number): string {
  if (score >= 90) return 'Excellent';
  if (score >= 80) return 'Very Good';
  if (score >= 70) return 'Good';
  if (score >= 60) return 'Fair';
  return 'Poor';
}

/**
 * Check if a lead has a valid email
 */
export function hasValidEmail(lead: Lead): boolean {
  if (!lead) return false;
  
  // Check if lead has a direct email
  if (lead.email && isValidEmail(lead.email)) {
    return true;
  }
  
  // Check if lead has a predicted email with high confidence
  if (lead.predicted_email && 
      isValidEmail(lead.predicted_email) && 
      lead.email_confidence && 
      lead.email_confidence >= 0.7) {
    return true;
  }
  
  return false;
}

/**
 * Basic email validation
 */
export function isValidEmail(email: string): boolean {
  if (!email) return false;
  
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

/**
 * Sort leads by score
 */
export function sortLeadsByScore(leads: Lead[]): Lead[] {
  if (!leads || !Array.isArray(leads)) return [];
  
  return [...leads].sort((a, b) => b.score - a.score);
}

/**
 * Filter leads by minimum score
 */
export function filterLeadsByMinScore(leads: Lead[], minScore: number): Lead[] {
  if (!leads || !Array.isArray(leads)) return [];
  if (minScore === undefined || minScore === null) return leads;
  
  return leads.filter(lead => lead.score >= minScore);
}

/**
 * Group leads by company
 */
export function groupLeadsByCompany(leads: Lead[]): Record<string, Lead[]> {
  if (!leads || !Array.isArray(leads)) return {};
  
  return leads.reduce((groups, lead) => {
    const company = lead.company || 'Unknown';
    if (!groups[company]) {
      groups[company] = [];
    }
    groups[company].push(lead);
    return groups;
  }, {} as Record<string, Lead[]>);
}

/**
 * Get best email for a lead (actual or predicted)
 */
export function getBestEmail(lead: Lead): string {
  if (!lead) return '';
  
  if (lead.email && isValidEmail(lead.email)) {
    return lead.email;
  }
  
  if (lead.predicted_email && isValidEmail(lead.predicted_email)) {
    return lead.predicted_email;
  }
  
  return '';
}

/**
 * Format lead company size
 */
export function formatCompanySize(size: string): string {
  if (!size) return 'Unknown';
  
  const sizeMap: Record<string, string> = {
    '1-10': 'Micro (1-10)',
    '11-50': 'Small (11-50)',
    '51-200': 'Medium (51-200)',
    '201-500': 'Large (201-500)',
    '501-1000': 'Large (501-1000)',
    '1001+': 'Enterprise (1000+)'
  };
  
  return sizeMap[size] || size;
}
