# BuildFlow: Owner-Builder OS 🏗️

BuildFlow is a comprehensive construction management platform specifically designed for homeowners acting as their own General Contractors. It transforms the complex process of building a home into a structured, educational, and data-driven journey.

## 🌟 Key Features

### 🧠 Smart Budgeting & Cost Suggestions
- **Regional Benchmarking:** Get localized cost suggestions for construction categories based on your project's city and state.
- **Smart Descriptions:** One-tap suggestions for budget line item descriptions to ensure professional-grade documentation.
- **Cost Rationales:** Interactive info icons explain *why* specific amounts are recommended, including regional labor and material factors.

### 🎓 Integrated Knowledge Base
- **App-Wide Education:** Technical terms are highlighted throughout the app. Click any term to learn what it is, why it's important, and what the pros/cons are.
- **Builder's Knowledge Drawer:** A slide-out educational panel that provides deep dives into construction systems like Foundations (Slab vs. Crawlspace vs. Basement), Site Work, and more.
- **Risk Mitigation:** Each topic includes a "What to Watch Out For" section to help first-time builders avoid common pitfalls.

### 📊 Professional Bid Leveling
- **Side-by-Side Comparison:** Compare multiple contractor quotes for the same budget item.
- **Variance Analysis:** Instantly see how bids compare to each other and to regional market averages.
- **Missing Scope Alerts:** Automatic warnings if a bid is suspiciously low, suggesting a potential missing scope of work.

### 🛠️ Core Management Tools
- **Schedule Tracking:** Manage project timelines and critical path activities.
- **Permit Management:** Track applications, approvals, and inspections.
- **Daily Logs:** Document site progress, weather impacts, and deliveries.
- **Subcontractor Directory:** Manage contacts, insurance, and payments.

## 🚀 Tech Stack

- **Backend:** Python (FastAPI), SQLAlchemy, Pydantic, SQLite
- **Frontend:** React (TypeScript), Tailwind CSS, Lucide Icons, TanStack Query (React Query)
- **Deployment:** Git/GitHub

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -e ..`
3. Initialize the database: `python ../scripts/init_db.py`
4. Seed sample data: `python ../scripts/seed_data.py`
5. Run the server: `uvicorn backend.main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. Open your browser to `http://localhost:5173`

---

Built with ❤️ for the next generation of owner-builders.
