export interface Project {
  id: number; name: string; address?: string; city?: string; state?: string;
  zip_code?: string; lot_number?: string; total_budget: number;
  start_date?: string; target_end_date?: string; actual_end_date?: string;
  status: string; notes?: string; created_at: string; updated_at: string;
}

export interface BudgetCategory {
  id: number; project_id: number; name: string; code: string;
  budgeted_amount: number; sort_order: number;
}

export interface BudgetItem {
  id: number; project_id: number; category_id: number; item_code: string;
  description: string; original_budget: number; current_budget: number;
  committed_cost: number; actual_cost: number; forecast_cost: number;
  percent_complete: number; notes?: string;
  bids: Bid[];
}

export interface Bid {
  id: number;
  budget_item_id: number;
  project_id: number;
  contractor_name: string;
  amount: number;
  is_selected: boolean;
  notes?: string;
  proposal_path?: string;
  created_at: string;
}

export interface CostSuggestion {
  label: string;
  amount: number;
  type: 'low' | 'average' | 'high';
  description_options: string[];
  rationale: string;
}

export interface KnowledgeEntry {
  id: string;
  title: string;
  short_description: string;
  full_description: string;
  pros: string[];
  cons: string[];
  risks: string[];
  related_terms: string[];
}

export interface Activity {
  id: number; project_id: number; activity_code: string; name: string;
  duration_days: number; early_start: number; early_finish: number;
  late_start: number; late_finish: number; total_float: number;
  is_critical: boolean; status: string; percent_complete: number;
  planned_start?: string; planned_finish?: string; actual_start?: string;
  actual_finish?: string; assigned_to?: string; predecessor_ids: number[];
}

export interface Milestone {
  id: number; project_id: number; name: string; target_date?: string;
  actual_date?: string; status: string;
}

export interface Permit {
  id: number; project_id: number; permit_type: string; permit_number?: string;
  jurisdiction?: string; status: string; application_date?: string;
  issued_date?: string; expiry_date?: string; description?: string;
}

export interface Inspection {
  id: number; permit_id: number; inspection_type: string;
  scheduled_date?: string; completed_date?: string; result?: string; notes?: string;
}

export interface PunchItem {
  id: number; project_id: number; punch_list_id: number; description: string;
  location: string; trade: string; priority: string; status: string;
  assigned_to?: string; due_date?: string; photo_before_path?: string;
  photo_after_path?: string; back_charge: boolean; back_charge_amount: number;
}

export interface DailyLog {
  id: number; project_id: number; log_date: string; weather_temp?: number;
  weather_condition?: string; weather_impact?: string; work_summary?: string; issues?: string;
  safety_incidents: number; crew_entries: CrewEntry[]; work_items: WorkItem[];
}

export interface CrewEntry {
  id: number; trade: string; company_name?: string; headcount: number; hours_worked: number;
}

export interface WorkItem {
  id: number; trade?: string; description: string; status: string;
}

export interface DocRecord {
  id: number; project_id: number; name: string; file_path: string;
  file_type?: string; file_size?: number; category_id?: number;
  description?: string; created_at: string;
}

export interface Subcontractor {
  id: number; project_id: number; company_name: string; contact_name?: string;
  email?: string; phone?: string; trade: string; license_number?: string;
  insurance_expiry?: string; contract_amount: number; retention_percent: number;
  status: string; total_paid: number; total_retention: number; balance_remaining: number;
}

export interface Payment {
  id: number; subcontractor_id: number; invoice_number?: string;
  gross_amount: number; retention_held: number; net_amount: number;
  status: string; paid_date?: string;
}

export interface DashboardSummary {
  project_name: string; project_status: string;
  budget: { total_budget: number; total_spent: number; total_committed: number; variance: number; variance_percent: number; status: string };
  schedule: { total_activities: number; completed_activities: number; percent_complete: number; critical_count: number; days_remaining: number; status: string };
  alerts: { module: string; severity: string; message: string }[];
  deadlines: { module: string; description: string; due_date: string; days_until: number }[];
  recent_activity: { module: string; action: string; description: string; created_at: string }[];
  weather?: { temp?: number; condition?: string; humidity?: number; wind_speed?: number };
}
