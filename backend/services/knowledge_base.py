from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class KnowledgeEntry:
    id: str
    title: str
    short_description: str
    full_description: str
    pros: List[str]
    cons: List[str]
    risks: List[str]
    related_terms: List[str]

KNOWLEDGE_DATA = {
    "01-SITE": KnowledgeEntry(
        id="01-SITE",
        title="Site Work",
        short_description="Preparing the land for construction.",
        full_description="Site work involves clearing the land, excavation, grading, and utility preparation. It is the critical first step to ensure a stable foundation and proper drainage.",
        pros=["Ensures proper drainage", "Provides stable base for foundation", "Connects essential utilities"],
        cons=["Can be delayed by weather", "Unforeseen soil conditions can increase costs"],
        risks=["Soil instability", "Hitting underground utilities", "Erosion"],
        related_terms=["Excavation", "Grading", "Soil Testing"]
    ),
    "02-FOUND": KnowledgeEntry(
        id="02-FOUND",
        title="Foundation",
        short_description="The structural base of the building.",
        full_description="The foundation transfers the load of the building to the ground. Common types include slab-on-grade, crawlspace, and full basement.",
        pros=["Supports the structure", "Insulates from ground moisture"],
        cons=["Costly to repair", "Requires precise engineering"],
        risks=["Cracking due to settling", "Water infiltration", "Radon gas"],
        related_terms=["Slab", "Crawlspace", "Basement", "Footing"]
    ),
    "03-FRAME": KnowledgeEntry(
        id="03-FRAME",
        title="Framing",
        short_description="The skeleton of the house.",
        full_description="Framing provides the shape and structural support for the entire house. It involves constructing walls, floors, and the roof structure.",
        pros=["Defines the layout", "Provides support for finishes"],
        cons=["Vulnerable to weather until enclosed", "Wood prices can be volatile"],
        risks=["Structural failure if not up to code", "Mold if wood gets wet", "Termite damage"],
        related_terms=["Stud", "Joist", "Truss", "Sheathing"]
    ),
    "crawlspace": KnowledgeEntry(
        id="crawlspace",
        title="Crawl Space",
        short_description="A shallow unfinished space beneath the first floor.",
        full_description="A crawl space elevates the home off the ground (typically 18-48 inches). It provides access to plumbing and wiring while keeping the house away from ground moisture.",
        pros=["Easy access to utilities", "Elevates home from floods/pests", "Warmer floors than slab"],
        cons=["Can harbor moisture/mold if unsealed", "Pest entry point", "More expensive than slab"],
        risks=["High humidity", "Standing water", "Insulation sagging"],
        related_terms=["Vapor Barrier", "Encapsulation", "Sump Pump"]
    ),
    "slab": KnowledgeEntry(
        id="slab",
        title="Slab on Grade",
        short_description="A concrete foundation poured directly on the ground.",
        full_description="A slab foundation is a single layer of concrete several inches thick. The edges are thicker to form an integral footing.",
        pros=["Lower cost", "Durable", "No space for pests underneath"],
        cons=["Plumbing is buried in concrete (hard to repair)", "Harder underfoot", "Potential cracking"],
        risks=["Cracking due to soil shifting", "Cold floors"],
        related_terms=["Rebar", "Control Joint", "Grading"]
    ),
    "basement": KnowledgeEntry(
        id="basement",
        title="Full Basement",
        short_description="A fully accessible floor below the main level.",
        full_description="A basement is a foundation that includes a habitable space below ground level. It can be finished for extra living space or used for storage.",
        pros=["Additional living space", "Safe area during storms", "Easy utility access"],
        cons=["Most expensive foundation", "Prone to flooding/leaks", "Requires sump pump"],
        risks=["Water intrusion", "Mold", "Radon"],
        related_terms=["Waterproofing", "Sump Pump", "Egress Window"]
    ),
     "permits": KnowledgeEntry(
        id="permits",
        title="Permits & Inspections",
        short_description="Legal authorization and verification of construction.",
        full_description="Building permits are official approvals issued by the local government agency that allow you to proceed with a construction or remodeling project. Inspections verify compliance with building codes.",
        pros=["Ensures safety compliance", "Increases resale value", "Prevents legal issues"],
        cons=["Adds time and cost", "Strict requirements"],
        risks=["Stop-work orders", "Fines", "Having to redo work"],
        related_terms=["Building Code", "Inspector", "Certificate of Occupancy"]
    ),
    "punchlist": KnowledgeEntry(
        id="punchlist",
        title="Punch List",
        short_description="A list of tasks to be completed before final project handover.",
        full_description="A punch list is a document prepared near the end of a construction project listing work not conforming to contract specifications that the contractor must complete prior to final payment.",
        pros=["Ensures quality", "Clear expectations for completion"],
        cons=["Can delay final payment", "Tedious to track"],
        risks=["Disputes over what is 'finished'", "Contractor fatigue"],
        related_terms=["Walkthrough", "Substantial Completion", "Retainage"]
    )
}

class KnowledgeService:
    @staticmethod
    def get_entry(key: str) -> Optional[Dict]:
        # Normalize key
        key = key.lower()
        
        # Try direct match
        if key in KNOWLEDGE_DATA:
            entry = KNOWLEDGE_DATA[key]
            return entry.__dict__
            
        # Try searching titles (simple)
        for k, v in KNOWLEDGE_DATA.items():
            if k.lower() == key or v.title.lower() == key:
                return v.__dict__
        
        return None

    @staticmethod
    def search(query: str) -> List[Dict]:
        query = query.lower()
        results = []
        for v in KNOWLEDGE_DATA.values():
            if query in v.title.lower() or query in v.short_description.lower():
                results.append(v.__dict__)
        return results
