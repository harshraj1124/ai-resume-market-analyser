# Market Research: India And Global Talent Demand

## Executive View

India remains one of the deepest technology talent markets in the world, but demand is uneven. Hiring teams face the sharpest shortages where new platform shifts require both applied engineering depth and domain fluency: GenAI, cloud security, data engineering, full-stack product engineering, MLOps, and cyber defense.

The system in this repository models both sides of the market:

- Supply: resume profiles, skills, locations, experience, industries, salary expectations.
- Demand: job postings, required skills, locations, experience bands, salary ranges.
- Gap: a comparable skill-level metric that identifies where hiring demand is not matched by available candidate supply.

## India Market Themes

### GenAI And Applied AI

Indian GCCs, SaaS companies, BFSI firms, and IT services organizations are hiring for LLM application builders, prompt engineers, AI product engineers, LangChain developers, RAG architects, and responsible AI roles. The practical shortage is strongest for engineers who can combine Python, vector databases, cloud deployment, evaluation, and business workflow design.

### Cloud And Platform Engineering

AWS, Azure, and GCP demand is broad across Bangalore, Hyderabad, Pune, Chennai, Mumbai, and Delhi NCR. Cloud demand is moving from migration work toward FinOps, platform engineering, Kubernetes, Terraform, observability, and secure multi-cloud operations.

### Cybersecurity

Security hiring is expanding across BFSI, healthcare, retail, SaaS, and government-adjacent vendors. India shows a growing need for cloud security, SOC analysts, IAM, AppSec, DevSecOps, and compliance-aware engineers.

### Data Engineering And Analytics

Demand is strong for SQL, Spark, Airflow, dbt, Snowflake, Databricks, Power BI, Tableau, and Python. Recruiters increasingly need candidates who can support both analytics and production-grade data products.

### Product Engineering

React, Node.js, Java, Python, mobile engineering, microservices, and DevOps remain high-volume categories. The market is more balanced than GenAI and cybersecurity, but senior engineers with architecture experience remain difficult to source.

## City-Level Signals

- Bangalore: AI, SaaS, product engineering, cloud, data platforms.
- Hyderabad: cloud, data engineering, enterprise SaaS, security, GCC hiring.
- Pune: automotive software, data, Java, cloud, DevOps.
- Delhi NCR: product, analytics, cyber, marketplace and fintech hiring.
- Chennai: enterprise engineering, cloud migration, data, testing automation.
- Mumbai: BFSI analytics, cybersecurity, product, data governance.
- Gurugram and Noida: analytics, consulting, fintech, marketing technology.
- Kochi, Coimbatore, Ahmedabad, Jaipur: growing second-tier supply pools.

## Global Compatibility

The taxonomy also supports globally relevant categories such as Rust, Go, Kubernetes, blockchain, quantum computing, sustainability AI, and privacy engineering. Location and salary fields are modeled cleanly so non-India sources can be added without changing the core pipeline.

## Recruiting Implications

Recruiting teams should:

- Prioritize shortage skills before opening generic campaigns.
- Use city-specific sourcing rather than one national campaign.
- Split GenAI roles into application engineering, platform, evaluation, and research profiles.
- Treat cybersecurity hiring as a community-led effort across LinkedIn, GitHub, X, security forums, and referrals.
- Use salary ranges and remote flexibility as levers for high-gap skills.

## System Assumptions

Synthetic data intentionally creates undersupply in GenAI, LLMs, LangChain, cybersecurity, cloud security, Kubernetes, and MLOps so the dashboard demonstrates shortage detection immediately.
