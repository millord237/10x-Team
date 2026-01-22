# Sales Funnel - FlowMetrics Launch Campaign

## Funnel Visualization

```mermaid
graph TD
    subgraph AWARENESS["AWARENESS STAGE"]
        A1[LinkedIn Ads] --> AWARE
        A2[Twitter Content] --> AWARE
        A3[Google Ads] --> AWARE
        A4[Blog/SEO] --> AWARE
        AWARE((10,000 Impressions))
    end

    subgraph INTEREST["INTEREST STAGE"]
        AWARE --> L1[Landing Page Visit]
        L1 --> L2{Engaged?}
        L2 -->|Yes| INTEREST_POOL((2,000 Visitors))
        L2 -->|No| BOUNCE[Bounce]
    end

    subgraph CONSIDERATION["CONSIDERATION STAGE"]
        INTEREST_POOL --> C1[Email Signup]
        INTEREST_POOL --> C2[Demo Request]
        INTEREST_POOL --> C3[Free Trial]
        C1 --> CONSIDER((500 Leads))
        C2 --> CONSIDER
        C3 --> CONSIDER
    end

    subgraph DECISION["DECISION STAGE"]
        CONSIDER --> D1[Trial Activation]
        D1 --> D2{Value Realized?}
        D2 -->|Yes| DECIDE((100 Qualified))
        D2 -->|No| NURTURE[Nurture Sequence]
        NURTURE --> CONSIDER
    end

    subgraph PURCHASE["PURCHASE STAGE"]
        DECIDE --> P1[Sales Call]
        P1 --> P2{Convert?}
        P2 -->|Yes| CUSTOMER((50 Customers))
        P2 -->|No| LOST[Lost Deal]
    end

    style AWARENESS fill:#E0E7FF
    style INTEREST fill:#C7D2FE
    style CONSIDERATION fill:#A5B4FC
    style DECISION fill:#818CF8
    style PURCHASE fill:#6366F1
    style CUSTOMER fill:#10B981
```

## Funnel Metrics

| Stage | Metric | Target | Conversion Rate |
|-------|--------|--------|----------------|
| Awareness | Impressions | 10,000 | - |
| Interest | Website Visitors | 2,000 | 20% |
| Consideration | Leads | 500 | 25% |
| Decision | Qualified Leads | 100 | 20% |
| Purchase | Customers | 50 | 50% |

## Channel Mix by Stage

**Awareness:** LinkedIn Ads, Twitter Content, Google Ads, Blog/SEO

**Interest:** Landing Page, Product Demo Video, Case Studies

**Consideration:** Email Nurture, Free Trial, Demo Calls

**Decision:** Sales Calls, Custom Demos, Proposal

**Purchase:** Contract, Onboarding, Success Check-in

