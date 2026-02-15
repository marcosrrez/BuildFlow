export const TRADES = [
  'General', 'Excavation', 'Concrete', 'Masonry', 'Structural Steel',
  'Framing', 'Roofing', 'Plumbing', 'Electrical', 'HVAC',
  'Insulation', 'Drywall', 'Painting', 'Flooring', 'Cabinets',
  'Tile', 'Landscaping', 'Siding',
]

export const PRIORITIES = ['Critical', 'High', 'Medium', 'Low']

export const PUNCH_STATUSES = ['Open', 'Assigned', 'In Progress', 'Completed', 'Verified', 'Rejected']

export const PERMIT_TYPES = ['building', 'electrical', 'plumbing', 'mechanical', 'fire', 'demolition']

export const BUDGET_CATEGORIES = [
  { code: '01-SITE', name: 'Site Work' },
  { code: '02-FOUND', name: 'Foundation' },
  { code: '03-FRAME', name: 'Framing' },
  { code: '04-ROOF', name: 'Roofing' },
  { code: '05-PLUMB', name: 'Plumbing' },
  { code: '06-ELEC', name: 'Electrical' },
  { code: '07-HVAC', name: 'HVAC' },
  { code: '08-INSUL', name: 'Insulation' },
  { code: '09-DRYWL', name: 'Drywall' },
  { code: '10-FLOOR', name: 'Flooring' },
  { code: '11-PAINT', name: 'Painting' },
  { code: '12-FIXT', name: 'Fixtures & Appliances' },
  { code: '13-LAND', name: 'Landscaping' },
  { code: '14-PERMIT', name: 'Permits & Fees' },
  { code: '15-CONTG', name: 'Contingency' },
]

export const STATUS_COLORS: Record<string, string> = {
  on_track: 'bg-green-100 text-green-800',
  at_risk: 'bg-yellow-100 text-yellow-800',
  critical: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
}

export function formatCurrency(n: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}

export function formatPercent(n: number): string {
  return `${n.toFixed(1)}%`
}
