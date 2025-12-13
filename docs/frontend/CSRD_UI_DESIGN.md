# CSRD Module - Frontend UI Design

## Overview
Professional CSRD compliance reporting interface for CarbonTrack users on Professional, Business, and Enterprise tiers.

**Design Principles:**
- Clean, data-dense interface for professionals
- Step-by-step wizard for complex data entry
- Real-time completeness feedback
- Clear deadline awareness
- Enterprise-grade data visualization

---

## Page Structure

###  1. CSRD Dashboard (Main Page)
**Route:** `/app/#/csrd` or `/app/#/compliance/csrd`

**Access Control:**
- Show "Upgrade to Professional" modal if user is FREE or BASIC tier
- Only accessible to PROFESSIONAL+ users

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ 🏢 CSRD Compliance Dashboard                      [?] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│ │ Reports  │  │ Completed│  │ In Review│  │Next     ││
│ │ Created  │  │ Reports  │  │ Reports  │  │Deadline ││
│ │    5     │  │    2     │  │    1     │  │ Apr 2026││
│ └──────────┘  └──────────┘  └──────────┘  └─────────┘│
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │  📋 Your CSRD Reports                 [+ New Report]││
│ ├─────────────────────────────────────────────────────┤│
│ │                                                      ││
│ │ Filters: [2024 ▼] [All Status ▼] [Search...      ]││
│ │                                                      ││
│ │ ┌────────────────────────────────────────────────┐ ││
│ │ │ Company Name    │ Year │ Status │ Score │ ⚙  │ ││
│ │ ├────────────────────────────────────────────────┤ ││
│ │ │ Test Corp GmbH  │ 2024 │●SUBMITTED│ 85%  │ ⋮  │ ││
│ │ │ Test Corp GmbH  │ 2023 │●COMPLETED│ 92%  │ ⋮  │ ││
│ │ │ Test Corp GmbH  │ 2024 │●IN_REVIEW│ 65%  │ ⋮  │ ││
│ │ └────────────────────────────────────────────────┘ ││
│ │                                                      ││
│ │           [← Previous]  Page 1 of 3  [Next →]       ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ 📚 ESRS Standards Reference                         ││
│ │                                                      ││
│ │ E1: Climate Change | E2: Pollution | E3: Water     ││
│ │ S1: Own Workforce | S2: Value Chain Workers        ││
│ │ G1: Business Conduct                                ││
│ │                                           [View All]││
│ └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Stats Cards**: Quick overview of report counts and deadlines
- **Report Table**: Sortable, filterable list of all reports
- **Status Indicators**: Color-coded status badges
  - 🔴 NOT_STARTED (red)
  - 🟡 IN_PROGRESS (yellow)
  - 🔵 IN_REVIEW (blue)
  - 🟢 COMPLETED (green)
  - ✅ SUBMITTED (green check)
- **Actions Menu (⋮)**: Edit, Duplicate, Export PDF, Delete
- **ESRS Quick Reference**: Links to standard descriptions

---

### 2. Create/Edit CSRD Report Page
**Route:** `/app/#/csrd/reports/new` or `/app/#/csrd/reports/:id/edit`

**Multi-Step Wizard Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ Create CSRD Report                           [Save Draft]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Progress: ████████░░░░░░░░░░░ 45% Complete            │
│                                                         │
│ Steps: [1.Info✓] [2.Environmental] [3.Social] [4.Gov] │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Step 2: Environmental Metrics (ESRS E1-E5)         ││
│ ├─────────────────────────────────────────────────────┤│
│ │                                                      ││
│ │ E1: Climate Change & GHG Emissions                  ││
│ │ ═════════════════════════════════════════════       ││
│ │                                                      ││
│ │ Scope 1 Emissions (Direct)                          ││
│ │ ┌───────────────────────────────┐                   ││
│ │ │ 150.5                         │ tonnes CO2e      ││
│ │ └───────────────────────────────┘                   ││
│ │ ℹ Direct emissions from owned sources              ││
│ │                                                      ││
│ │ Scope 2 Emissions (Energy)                          ││
│ │ ┌───────────────────────────────┐                   ││
│ │ │ 75.3                          │ tonnes CO2e      ││
│ │ └───────────────────────────────┘                   ││
│ │                                                      ││
│ │ Scope 3 Emissions (Value Chain)                     ││
│ │ ┌───────────────────────────────┐                   ││
│ │ │ 200.0                         │ tonnes CO2e      ││
│ │ └───────────────────────────────┘                   ││
│ │                                                      ││
│ │ Total GHG Emissions: 425.8 tonnes CO2e             ││
│ │ ┌──────────────────────────────────────────────┐   ││
│ │ │ [Scope 1: 35%][Scope 2: 18%][Scope 3: 47%]  │   ││
│ │ └──────────────────────────────────────────────┘   ││
│ │                                                      ││
│ │ Renewable Energy Usage                               ││
│ │ ┌───────────────────────────────┐                   ││
│ │ │ 35.5                          │ %                ││
│ │ └───────────────────────────────┘                   ││
│ │                                                      ││
│ │ Total Energy Consumption                            ││
│ │ ┌───────────────────────────────┐                   ││
│ │ │ 1,250                         │ MWh              ││
│ │ └───────────────────────────────┘                   ││
│ │                                                      ││
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ││
│ │                                                      ││
│ │ E2: Pollution to Air, Water, and Soil              ││
│ │                                                      ││
│ │ [+ Add Pollutant Emissions Data]                    ││
│ │                                                      ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│     [← Previous Step]  [Save & Continue →]             │
└─────────────────────────────────────────────────────────┘
```

**Step Breakdown:**

**Step 1: Company Information**
- Company Name (auto-filled)
- Registration Number
- Country
- Sector (dropdown: Technology, Manufacturing, Finance, etc.)
- Employee Count
- Annual Revenue (EUR)
- Reporting Year (2024, 2025, etc.)
- Reporting Period (Q1, Q2, Q3, Q4, Annual)

**Step 2: Environmental Metrics (E1-E5)**
- E1 Climate: Emissions (Scope 1/2/3), Energy, Renewables
- E2 Pollution: Air pollutants, Water discharge, Soil contamination
- E3 Water: Consumption, Discharge, Recycling rate
- E4 Biodiversity: Land use, Protected areas impact
- E5 Circular Economy: Waste generated, Recycled percentage, Material reuse

**Step 3: Social Metrics (S1-S4)**
- S1 Own Workforce: Employee count, Training hours, Safety incidents
- S2 Value Chain Workers: Supplier workforce conditions
- S3 Affected Communities: Community engagement metrics
- S4 Consumers: Product safety, Customer satisfaction

**Step 4: Governance (G1)**
- Board composition
- Ethics policies
- Anti-corruption measures
- Business conduct code

**Features:**
- **Real-time Validation**: Show errors immediately
- **Auto-save**: Save draft every 30 seconds
- **Completeness Score**: Live percentage in top bar
- **Field Help**: Hover/click ℹ for ESRS guidance
- **Calculation Fields**: Auto-calculate totals (e.g., Scope 1+2+3)
- **Visual Feedback**: Progress bar, color coding

---

### 3. Report Detail View
**Route:** `/app/#/csrd/reports/:id`

```
┌─────────────────────────────────────────────────────────┐
│ CSRD Report: Test Corporation GmbH - 2024              │
│ [← Back]                    [Edit] [Export PDF] [⋮]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌──────────────┐  ┌──────────────┐  ┌────────────────┐│
│ │ Status       │  │ Completeness │  │ Deadline       ││
│ │ ●SUBMITTED   │  │ 85%          │  │ Apr 30, 2026   ││
│ │ June 15,2025 │  │ ████████▒▒   │  │ 341 days left  ││
│ └──────────────┘  └──────────────┘  └────────────────┘│
│                                                         │
│ 📊 GHG Emissions Overview                              │
│ ┌─────────────────────────────────────────────────────┐│
│ │                                                      ││
│ │  Total: 425.8 tonnes CO2e                           ││
│ │                                                      ││
│ │  ┌────────────────────────────────────────────────┐ ││
│ │  │                                                 │ ││
│ │  │   📊 [Emissions Breakdown Chart]                │ ││
│ │  │       Scope 1: 150.5t (35%)                     │ ││
│ │  │       Scope 2: 75.3t  (18%)                     │ ││
│ │  │       Scope 3: 200.0t (47%)                     │ ││
│ │  │                                                 │ ││
│ │  └────────────────────────────────────────────────┘ ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ 🌱 Environmental Metrics                               │
│ ┌─────────────────────────────────────────────────────┐│
│ │ E1 Climate Change                                   ││
│ │ • Renewable Energy: 35.5%                           ││
│ │ • Total Energy: 1,250 MWh                           ││
│ │                                                      ││
│ │ E2 Pollution                                        ││
│ │ • Air Pollutants: [View Details]                    ││
│ │                                                      ││
│ │ E3 Water & Marine                                   ││
│ │ • Water Consumption: 5,000 m³                       ││
│ │ • Recycling Rate: 45%                               ││
│ │                                                      ││
│ │ [+ View All Environmental Metrics]                  ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ 📋 Audit Trail                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Jun 15, 2025 10:30 AM - SUBMITTED by user@test.de  ││
│ │ Jun 14, 2025 3:45 PM  - UPDATED (status: review)   ││
│ │ Jun 10, 2025 9:15 AM  - UPDATED (metrics added)    ││
│ │ Jun 5, 2025 11:00 AM  - CREATED by user@test.de    ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ 🔐 Verification                                        │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Not yet verified                                    ││
│ │ [+ Add Third-Party Verification]                    ││
│ └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

**Features:**
- **Status Header**: Prominent display of report status and deadline
- **Completeness Progress**: Visual bar showing completion percentage
- **Emissions Visualization**: Chart.js donut/bar chart for Scope 1/2/3
- **Collapsible Sections**: Expand/collapse for each ESRS standard
- **Audit Timeline**: Chronological list of all changes
- **Verification Section**: Add third-party auditor details
- **Export Options**: PDF download with one click
- **Edit Button**: Quick jump to edit mode

---

### 4. ESRS Standards Reference Page
**Route:** `/app/#/csrd/standards`

```
┌─────────────────────────────────────────────────────────┐
│ ESRS Standards Reference Guide                [Search]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Environmental (E1-E5)                                   │
│ ┌─────────────────────────────────────────────────────┐│
│ │ E1 - Climate Change                                 ││
│ │ Requirements: GHG emissions (Scope 1/2/3), energy   ││
│ │ consumption, renewable energy usage, climate risks  ││
│ │                                       [View Details]││
│ ├─────────────────────────────────────────────────────┤│
│ │ E2 - Pollution                                      ││
│ │ Requirements: Air, water, soil pollutants           ││
│ │                                       [View Details]││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ Social (S1-S4)                                          │
│ ┌─────────────────────────────────────────────────────┐│
│ │ S1 - Own Workforce                                  ││
│ │ S2 - Workers in Value Chain                         ││
│ │ S3 - Affected Communities                           ││
│ │ S4 - Consumers and End-Users                        ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ Governance (G1)                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ G1 - Business Conduct                               ││
│ └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

**Features:**
- **Searchable**: Quick search for specific requirements
- **Expandable Cards**: Click to see detailed requirements
- **Compliance Tips**: Hover tooltips with best practices
- **External Links**: Link to official EFRAG documentation

---

## Component Structure

### Vue Components

```
src/components/csrd/
├── CsrdDashboard.vue          # Main dashboard page
├── CsrdReportForm.vue         # Multi-step form wizard
├── CsrdReportDetail.vue       # Single report view
├── CsrdStandardsReference.vue # ESRS standards list
├── components/
│   ├── CsrdStatsCard.vue      # Stat cards (reports count, etc.)
│   ├── CsrdReportTable.vue    # Sortable report table
│   ├── CsrdProgressBar.vue    # Completeness progress bar
│   ├── CsrdStatusBadge.vue    # Color-coded status badge
│   ├── CsrdEmissionsChart.vue # Chart.js emissions visualization
│   ├── CsrdAuditTimeline.vue  # Audit trail timeline
│   ├── CsrdFieldInput.vue     # Reusable form input with help text
│   ├── CsrdStepNavigation.vue # Multi-step wizard nav
│   ├── CsrdFilterBar.vue      # Report filters (year, status)
│   └── CsrdUpgradeModal.vue   # Premium tier upsell modal
```

### API Integration

```javascript
// src/services/csrdService.js

export const csrdService = {
  // Reports
  async getReports(filters) {
    // GET /api/v1/csrd/reports?year=2024&status=submitted
  },
  
  async getReport(reportId) {
    // GET /api/v1/csrd/reports/:id
  },
  
  async createReport(reportData) {
    // POST /api/v1/csrd/reports
  },
  
  async updateReport(reportId, updates) {
    // PUT /api/v1/csrd/reports/:id
  },
  
  async submitReport(reportId) {
    // POST /api/v1/csrd/reports/:id/submit
  },
  
  async deleteReport(reportId) {
    // DELETE /api/v1/csrd/reports/:id
  },
  
  // Standards
  async getStandards() {
    // GET /api/v1/csrd/standards
  },
  
  // Compliance
  async checkCompliance(reportId) {
    // GET /api/v1/csrd/compliance-check/:id
  },
  
  // Audit
  async getAuditTrail(reportId) {
    // GET /api/v1/csrd/reports/:id/audit-trail
  },
  
  // Export
  async exportPDF(reportId) {
    // GET /api/v1/csrd/reports/:id/export/pdf
  },
  
  // Verification
  async addVerification(reportId, verificationData) {
    // POST /api/v1/csrd/reports/:id/verify
  }
}
```

---

## Design Tokens

### Colors

**Status Colors:**
- `--status-not-started`: #EF4444 (red)
- `--status-in-progress`: #F59E0B (amber)
- `--status-review`: #3B82F6 (blue)
- `--status-completed`: #10B981 (green)
- `--status-submitted`: #059669 (emerald)

**ESRS Category Colors:**
- `--esrs-environmental`: #10B981 (green)
- `--esrs-social`: #3B82F6 (blue)
- `--esrs-governance`: #8B5CF6 (purple)

**UI Colors:**
- `--primary`: #059669 (brand green)
- `--secondary`: #0F766E (teal)
- `--accent`: #F59E0B (amber)
- `--background`: #F9FAFB (gray-50)
- `--surface`: #FFFFFF (white)
- `--error`: #EF4444 (red)
- `--warning`: #F59E0B (amber)
- `--success`: #10B981 (green)
- `--info`: #3B82F6 (blue)

### Typography

**Fonts:**
- Headings: Inter, -apple-system, sans-serif
- Body: Inter, -apple-system, sans-serif
- Mono: 'Fira Code', 'Courier New', monospace

**Sizes:**
- `--text-xs`: 0.75rem (12px)
- `--text-sm`: 0.875rem (14px)
- `--text-base`: 1rem (16px)
- `--text-lg`: 1.125rem (18px)
- `--text-xl`: 1.25rem (20px)
- `--text-2xl`: 1.5rem (24px)
- `--text-3xl`: 1.875rem (30px)

### Spacing

- `--space-xs`: 0.25rem (4px)
- `--space-sm`: 0.5rem (8px)
- `--space-md`: 1rem (16px)
- `--space-lg`: 1.5rem (24px)
- `--space-xl`: 2rem (32px)
- `--space-2xl`: 3rem (48px)

---

## Responsive Breakpoints

- **Mobile:** < 640px (single column, stacked forms)
- **Tablet:** 640px - 1024px (2-column layout)
- **Desktop:** > 1024px (full 3-column layout)

**Mobile Adaptations:**
- Hide sidebar on mobile, use hamburger menu
- Stack stat cards vertically
- Single-column form layout
- Simplified table (hide less important columns)
- Bottom-fixed action buttons

---

## Accessibility

**WCAG 2.1 AA Compliance:**
- All form inputs have associated labels
- Color is not the only indicator (use icons + text)
- Keyboard navigation support (tab order, focus styles)
- ARIA labels for screen readers
- Min contrast ratio 4.5:1 for normal text
- Focus indicators on all interactive elements

**Features:**
- Skip navigation links
- Semantic HTML5 elements
- Alt text for all images/icons
- Form validation error messages
- Loading states with aria-busy
- Screen reader announcements for status changes

---

## Implementation Priority

### Phase 1 (MVP - Days 1-2)
✅ CsrdDashboard.vue - Report list view
✅ CsrdReportTable.vue - Basic table
✅ CsrdStatusBadge.vue - Status indicators
✅ API integration for list/get

### Phase 2 (Core Features - Days 3-4)
✅ CsrdReportForm.vue - Step 1 (Company Info)
✅ CsrdReportForm.vue - Step 2 (Environmental)
✅ CsrdFieldInput.vue - Reusable input component
✅ CsrdProgressBar.vue - Completeness indicator
✅ Auto-save functionality

### Phase 3 (Advanced - Days 5-6)
✅ CsrdReportDetail.vue - Full detail view
✅ CsrdEmissionsChart.vue - Chart.js visualization
✅ CsrdAuditTimeline.vue - Audit trail
✅ CsrdStandardsReference.vue - Standards page
✅ PDF export integration

### Phase 4 (Polish - Day 7)
✅ Mobile responsive design
✅ Loading states
✅ Error handling
✅ Premium upgrade modal
✅ Accessibility audit
✅ Integration testing

---

## Technical Notes

### State Management
Use Vue 3 Composition API with Pinia for state:
- `csrdReportsStore` - Report list, filters, pagination
- `csrdFormStore` - Form data, auto-save, validation
- `userStore` - Check premium tier access

### Form Validation
- **Client-side**: Vuelidate or VeeValidate
- **Server-side**: Pydantic validation in API
- **Real-time**: Show errors on blur
- **Submit validation**: Block submit if incomplete

### Performance
- **Lazy Loading**: Load ESRS sections on-demand
- **Pagination**: 50 reports per page (backend)
- **Debounce**: Auto-save with 500ms debounce
- **Caching**: Cache standards list in localStorage

### Browser Support
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

---

## Next Steps

1. **Review this design** with stakeholders
2. **Create mockups** in Figma (optional but helpful)
3. **Start implementation** with Phase 1 (Dashboard)
4. **Test with real data** using existing DynamoDB reports
5. **Iterate** based on user feedback

**Timeline:** 7 days total from design to deployed UI

**Launch Date:** January 15, 2026 🚀
