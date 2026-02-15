from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CostSuggestion:
    label: str
    amount: float
    type: str
    description_options: List[str]
    rationale: str

# Regional multipliers (normalized to 1.0 as national average)
REGIONAL_FACTORS = {
    "CA": 1.25, "NY": 1.30, "TX": 0.95, "FL": 1.00,
    "IL": 1.10, "WA": 1.15, "MA": 1.20, "GA": 0.90,
    "NC": 0.85, "CO": 1.05, "default": 1.0
}

# Base costs and descriptive metadata
CATEGORY_METADATA = {
    "01-SITE": {
        "avg": 15000, "range": (5000, 40000),
        "descriptions": ["General site clearing & grading", "Excavation and backfill", "Soil testing & compaction"],
        "logic": "Based on typical residential lot sizes. High end accounts for significant slope or rocky terrain."
    },
    "02-FOUND": {
        "avg": 25000, "range": (15000, 50000),
        "descriptions": ["Slab on grade foundation", "Stem wall with crawlspace", "Full basement concrete pour"],
        "logic": "Calculated per square foot. Regional factors account for frost line depth and local concrete prices."
    },
    "03-FRAME": {
        "avg": 45000, "range": (30000, 100000),
        "descriptions": ["Lumber package and labor", "Trusses and sheathing", "Steel beam reinforcement"],
        "logic": "Lumber market volatility is indexed. Premium includes complex roof lines or high ceilings."
    },
    "04-ROOF": {
        "avg": 12000, "range": (8000, 25000),
        "descriptions": ["30-year architectural shingles", "Standing seam metal roofing", "Concrete tile installation"],
        "logic": "Standard assumes asphalt shingles. Premium assumes metal or tile with high durability."
    },
    "05-PLUMB": {
        "avg": 18000, "range": (1000, 35000),
        "descriptions": ["Rough-in plumbing and stack", "Waste and vent lines", "Gas line installation"],
        "logic": "Calculated by fixture count. Regional costs vary significantly with labor union rates."
    },
    "06-ELEC": {
        "avg": 15000, "range": (8000, 30000),
        "descriptions": ["Electrical rough-in & wiring", "200A Service panel upgrade", "Smart home low-voltage wiring"],
        "logic": "Based on standard residential load requirements and local master electrician rates."
    },
    "07-HVAC": {
        "avg": 14000, "range": (7000, 22000),
        "descriptions": ["Central AC and furnace", "Heat pump system", "Ductwork installation"],
        "logic": "Climate-adjusted. Southern states index higher for AC; Northern for heating efficiency."
    },
    "08-INSUL": {
        "avg": 5000, "range": (3000, 10000),
        "descriptions": ["Batt and poly insulation", "Blown-in attic cellulose", "Closed-cell spray foam"],
        "logic": "Standard assumes fiberglass. Premium assumes high-efficiency spray foam (R-value 21+)."
    },
    "09-DRYWL": {
        "avg": 12000, "range": (7000, 20000),
        "descriptions": ["Hanging, taping & finishing", "Level 5 smooth finish", "Moisture-resistant board installation"],
        "logic": "Includes labor and material. High end accounts for high ceilings or radius walls."
    },
    "10-FLOOR": {
        "avg": 15000, "range": (5000, 40000),
        "descriptions": ["Engineered hardwood flooring", "Luxury Vinyl Plank (LVP)", "Premium wool carpeting"],
        "logic": "Based on coverage area. Material quality is the primary driver for variance here."
    },
}

class CostService:
    @staticmethod
    def get_suggestions(category_code: str, state: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        factor = REGIONAL_FACTORS.get(state, REGIONAL_FACTORS["default"]) if state else 1.0
        
        if city and city.lower() in ["san francisco", "new york", "seattle"]:
            factor *= 1.2
            
        meta = CATEGORY_METADATA.get(category_code)
        if not meta:
            return []
            
        avg = meta["avg"] * factor
        low = meta["range"][0] * factor
        high = meta["range"][1] * factor
        
        # Determine rationale prefix
        loc_str = f" in {city or state}" if city or state else ""
        
        return [
            {
                "label": "Budget", 
                "amount": round(low, -2), 
                "type": "low",
                "description_options": meta["descriptions"],
                "rationale": f"Minimum viable cost{loc_str}. {meta['logic']}"
            },
            {
                "label": "Standard", 
                "amount": round(avg, -2), 
                "type": "average",
                "description_options": meta["descriptions"],
                "rationale": f"Median market rate{loc_str}. {meta['logic']}"
            },
            {
                "label": "Premium", 
                "amount": round(high, -2), 
                "type": "high",
                "description_options": meta["descriptions"],
                "rationale": f"High-end specifications{loc_str}. {meta['logic']}"
            },
        ]
