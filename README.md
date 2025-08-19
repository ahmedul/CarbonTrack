# 🌍 CarbonTrack

CarbonTrack is a **SaaS MVP** for tracking and reducing individual and organizational carbon footprints.  
It is designed to showcase **cloud-native architecture on AWS** and has the potential to grow into a full SaaS startup.  

---

## 🚀 Features (MVP Scope)

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
- [ ] Set up AWS Cognito authentication  
- [ ] Create user registration + login API (Python, Lambda, API Gateway)  
- [ ] Define DynamoDB schema for users + carbon data  

### 🚧 Phase 2 (Frontend + Integration)
- [ ] Deploy Vue.js frontend on S3 + CloudFront  
- [ ] Connect frontend with backend APIs  

### 🔮 Phase 3 (User Experience & CI/CD)
- [ ] Build carbon footprint calculation logic  
- [ ] Create dashboard with charts (CO₂ trend)  
- [ ] Set up CI/CD pipeline with CodePipeline  

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


