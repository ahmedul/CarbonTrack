# 🌍 CarbonTrack

CarbonTrack is a **SaaS MVP** for tracking and reducing individual and organizational carbon footprints.  
It is designed to showcase **cloud-native architecture on AWS** and has the potential to grow into a full SaaS startup.  

---

## � Carbon Calculation Engine

CarbonTrack uses scientifically-backed emission factors from leading environmental agencies to provide accurate carbon footprint calculations across multiple categories:

### Categories Covered
- **🚗 Transportation**: Cars, flights, public transport, trains
- **⚡ Energy**: Electricity, natural gas, heating oil  
- **🍽️ Food**: Beef, pork, chicken, fish, dairy products
- **🗑️ Waste**: Landfill waste, recycling, composting

### Key Features
- **80+ Activity Types** with specific emission factors
- **Regional Variations** for electricity grids (US, EU, UK, Canada, Australia)
- **Multiple Units Support** with automatic conversions
- **Scientific Accuracy** based on peer-reviewed research

---

## 📚 Scientific Sources & Documentation

Our carbon calculation methodology is based on authoritative sources from leading environmental and governmental agencies:

### Primary Sources

**🇺🇸 United States Environmental Protection Agency (EPA)**
- [Emission Factors for Greenhouse Gas Inventories](https://www.epa.gov/climateleadership/ghg-emission-factors-hub)
- [Energy and Environment Guide to Action](https://www.epa.gov/statelocalenergy)
- EPA eGRID Database for regional electricity factors

**🌍 Intergovernmental Panel on Climate Change (IPCC)**
- [2019 Refinement to the 2006 IPCC Guidelines](https://www.ipcc-nggip.iges.or.jp/public/2019rf/)
- IPCC Working Group III Assessment Report 6
- Transportation and energy sector emission factors

**🇬🇧 UK Department for Environment, Food & Rural Affairs (DEFRA)**
- [UK Government GHG Conversion Factors](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2023)
- UK Energy Statistics
- Food and waste emission factors

**📊 International Energy Agency (IEA)**
- [World Energy Outlook](https://www.iea.org/reports/world-energy-outlook-2023)
- Global electricity emission factors by country
- Energy efficiency metrics

**🥩 Food and Agriculture Organization (FAO)**
- [Livestock's Long Shadow Report](http://www.fao.org/3/a0701e/a0701e00.htm)
- Global food production emission factors
- Agricultural greenhouse gas emissions

### Academic and Research Sources

**🎓 Peer-Reviewed Research**
- Journal of Cleaner Production studies on LCA methodologies
- Environmental Science & Technology carbon footprint assessments
- Nature Climate Change transportation emission analyses

**🏢 Industry Standards**
- ISO 14064 for greenhouse gas quantification
- GHG Protocol Corporate Standard
- Carbon Trust methodologies

### Data Quality and Updates

- **Verification**: All emission factors cross-referenced with multiple sources
- **Regional Accuracy**: Location-specific factors for major economies
- **Regular Updates**: Annual review of emission factors following EPA/DEFRA updates
- **Transparency**: Complete calculation methodology documented in `/docs/CARBON_CALCULATION_DOCS.md`

### Calculation Methodology

For detailed information about our calculation methods, emission factors, and scientific rationale, see our comprehensive documentation:
- 📖 **[Carbon Calculation Documentation](./CARBON_CALCULATION_DOCS.md)** - 65-page technical guide
- 🔬 **Scientific Validation** - Benchmarked against EPA and DEFRA calculators
- 📊 **API Reference** - Complete endpoint documentation with examples

---

## �🚀 Features (MVP Scope)

- 🔐 **User Authentication** with AWS Cognito  
- 📝 **Data Input** for energy usage & travel records  
- 📊 **CO₂ Calculation Engine** (Python backend)  
- 📈 **Dashboard** with charts to visualize emissions over time  
- 💾 **Serverless Storage** using DynamoDB + S3  
- ⚡ **CI/CD Pipeline** with AWS CodePipeline  

---

## 🛠️ Tech Stack

- **Frontend:** Vue.js (S3 + CloudFront hosting)  
- **Backend:** Python (FastAPI, AWS Lambda, API Gateway)  
- **Database:** DynamoDB (NoSQL)  
- **Storage:** S3 (static files, reports)  
- **Auth:** Cognito (user management)  
- **CI/CD:** GitHub Actions → CodePipeline  
- **Infra:** AWS SAM / CDK (optional)  

---

## 📂 Project Roadmap

### ✅ Phase 1 (Backend Basics)
- [✅] Set up AWS Cognito authentication  
- [✅] Create user registration + login API (Python, Lambda, API Gateway)  
- [✅] Define DynamoDB schema for users + carbon data  

### ✅ Phase 2 (Frontend + Integration)
- [✅] Deploy Vue.js frontend on S3 + CloudFront  
- [✅] Connect frontend with backend APIs  

### ✅ Phase 3 (Carbon Calculation Engine)
- [✅] **Build comprehensive carbon footprint calculation logic**
  - ✅ Scientific emission factors from EPA, IPCC, DEFRA
  - ✅ 80+ activities across transportation, energy, food, waste
  - ✅ Regional variations for electricity grids
  - ✅ Multiple unit support with automatic conversions
- [✅] **Create comprehensive documentation (65 pages)**
  - ✅ Complete calculation methodology
  - ✅ API reference with examples
  - ✅ Scientific sources and validation
- [✅] **Enhanced dashboard with charts** (CO₂ trend visualization)

### 🔮 Phase 4 (Production & CI/CD)
- [ ] Set up CI/CD pipeline with CodePipeline  
- [ ] Production deployment optimization
- [ ] Performance monitoring and analytics  

---

## 📌 Definition of Done (DoD)

Each feature is considered **done** when:  
1. Code is implemented & tested locally  
2. Successfully deployed to AWS  
3. Documented in `README.md` or project wiki  
4. Linked issue is closed in GitHub Project board  

---

## 🏗️ Architecture (MVP)

```mermaid
flowchart TD
  A["User Browser"] -->|Login/Register| B["AWS Cognito"]
  A -->|API Calls| C["API Gateway"]
  C --> D["Lambda (Python Backend)"]
  D --> E["DynamoDB (Carbon Data)"]
  D --> F["S3 (Reports & Static Assets)"]
  A -->|Dashboard| G["Vue.js Frontend (S3 + CloudFront)"]


