# EU Compliance Requirements — NCM (Network Configuration Management)

> Working compliance checklist for an NCM software platform intended for the EU market.
>
> **Important:** This document is a technical/compliance planning aid, not legal advice. Applicability depends on the product architecture, deployment model, customer sectors, data processing, and whether the software is placed on the EU market.

## 1. Executive summary

For a commercial NCM platform that manages routers, switches, firewalls, access points and similar network devices, the primary EU framework to assess is the **Cyber Resilience Act (CRA), Regulation (EU) 2024/2847**.

The European Commission specifically identifies **network management systems** among products important from a cybersecurity perspective. Depending on the exact product classification and the standards used, a conformity-assessment procedure involving a notified body may be required.

The CRA entered into force on **10 December 2024**. Its main obligations apply from **11 December 2027**. CRA reporting obligations apply from **11 September 2026**.

---

# 2. Core EU legislation

## 2.1 Cyber Resilience Act (CRA)

**Legal instrument:** Regulation (EU) 2024/2847

**Priority for NCM:** CRITICAL

### Why it matters

The CRA applies to hardware and software products with digital elements that are made available on the EU market and whose intended or reasonably foreseeable use includes a direct or indirect logical or physical data connection to a device or network.

An NCM platform normally has exactly this characteristic because it communicates with network infrastructure.

### Main obligations to design for

- Cybersecurity risk assessment
- Secure-by-design development
- Secure-by-default configuration
- Vulnerability management
- Security updates
- Security support period
- Security documentation
- SBOM / component inventory where applicable
- Secure authentication
- Access control
- Encryption
- Protection of sensitive configuration and credentials
- Logging and monitoring
- Incident handling
- Vulnerability disclosure process
- Security testing
- Technical documentation
- EU Declaration of Conformity
- CE marking where required
- Market-surveillance cooperation
- Reporting of actively exploited vulnerabilities
- Reporting of severe security incidents

### NCM-specific security requirements

The platform should provide:

- MFA
- RBAC
- Least privilege
- SSO where appropriate
- Secure secret storage
- Credential rotation
- SSH key management
- TLS for web/API communication
- Secure device communication
- Configuration encryption
- Audit logs
- Immutable/tamper-resistant security logs
- Configuration versioning
- Configuration diff
- Rollback
- Approval workflow
- Change tracking
- Vulnerability tracking
- Security update mechanism
- Secure backup and restore

### CRA reporting

From 11 September 2026, manufacturers must report actively exploited vulnerabilities and severe incidents affecting the security of products with digital elements.

The CRA reporting process includes:

- early warning within 24 hours of awareness;
- full notification within 72 hours;
- final report after the corrective measure is available, according to the applicable deadline.

### Conformity assessment

Network management systems are identified by the European Commission as an important product category from a cybersecurity perspective.

The exact conformity-assessment route depends on the final product classification and whether applicable harmonised standards/common specifications or a European cybersecurity certification scheme are used.

---

# 3. NIS2

**Legal instrument:** Directive (EU) 2022/2555

**Priority for NCM:** HIGH when serving regulated/critical customers; otherwise indirect

NIS2 does **not automatically regulate every NCM vendor** merely because it develops NCM software.

It primarily regulates entities in specified sectors and categories.

However, NCM can become an important security component for customers such as:

- telecom operators;
- digital infrastructure providers;
- cloud providers;
- data centres;
- managed service providers;
- managed security service providers;
- energy organisations;
- transport organisations;
- banking/financial infrastructure;
- healthcare;
- water;
- public administration;
- other entities covered by national implementation.

### NCM should therefore support NIS2-oriented controls

- Risk management
- Incident management
- Business continuity
- Disaster recovery
- Crisis management
- Supply-chain security
- Secure development
- Vulnerability management
- Access control
- Cryptography
- MFA
- Asset management
- Network monitoring
- Logging
- Incident evidence
- Backup
- Recovery testing

---

# 4. GDPR

**Legal instrument:** Regulation (EU) 2016/679

**Priority for NCM:** HIGH if personal data is processed

NCM systems can process personal data even when their primary purpose is network management.

Potential personal data includes:

- usernames;
- names;
- email addresses;
- IP addresses;
- operator IDs;
- authentication logs;
- audit records;
- device ownership information;
- support tickets;
- activity history.

### NCM GDPR requirements

Implement:

- Privacy Policy
- Record of Processing Activities where applicable
- Data minimisation
- Purpose limitation
- Retention periods
- Data deletion
- Data export
- Access requests
- Rectification
- Encryption
- Access controls
- Processor/subprocessor management
- Data Processing Agreements where applicable
- Data breach procedure
- International transfer safeguards where applicable

### Recommended retention model

Do not retain audit and personal data indefinitely by default.

Define separate retention policies for:

- authentication logs;
- configuration-change logs;
- security logs;
- user account data;
- support data;
- deleted accounts.

---

# 5. ePrivacy / cookies

**Relevant framework:** Directive 2002/58/EC (ePrivacy Directive), as implemented by Member States.

**Priority:** MEDIUM/HIGH for web-based SaaS NCM

If the NCM web interface uses:

- analytics;
- tracking;
- advertising technologies;
- non-essential cookies;
- similar device storage/access technologies;

the platform needs an appropriate consent and information mechanism where required.

Recommended:

- Cookie Policy
- Cookie inventory
- Consent management
- Consent records
- Non-essential trackers disabled until valid consent where required

---

# 6. Cybersecurity Act

**Legal instrument:** Regulation (EU) 2019/881

**Priority:** MEDIUM / strategic

The EU Cybersecurity Act establishes the EU cybersecurity certification framework and strengthens ENISA.

For an NCM vendor, relevant areas include:

- cybersecurity certification schemes;
- European cybersecurity assurance;
- use of recognised certification where appropriate.

The Cybersecurity Act is not a blanket requirement that every NCM must obtain a certificate.

---

# 7. Cyber Resilience Act + standards

The CRA is supported by harmonised standards and technical specifications.

The European Commission has issued a standardisation request covering standards supporting CRA implementation.

An NCM manufacturer should monitor:

- CRA harmonised standards;
- product-specific standards;
- vulnerability-management standards;
- secure development standards;
- relevant European cybersecurity certification schemes.

Recommended engineering references include, depending on scope:

- ISO/IEC 27001
- ISO/IEC 27002
- ISO/IEC 27005
- ISO/IEC 29147
- ISO/IEC 30111
- IEC 62443 where industrial/OT environments are relevant
- relevant ETSI cybersecurity standards
- relevant ENISA guidance

These standards are not all automatically mandatory. Their applicability must be assessed against the product and legal route.

---

# 8. Data Act

**Legal instrument:** Regulation (EU) 2023/2854

**Priority for a conventional NCM:** LOW/MEDIUM

The Data Act mainly concerns access to and use of data generated by connected products and related services.

It should be assessed if the NCM product is integrated with connected devices/services in a way that falls within its scope.

Potential considerations:

- data access;
- data portability;
- contractual terms;
- interoperability;
- cloud switching;
- data sharing.

For a conventional NCM that simply manages third-party network equipment, the Data Act may not be the primary regulatory requirement.

---

# 9. Digital Services Act (DSA)

**Legal instrument:** Regulation (EU) 2022/2065

**Priority for a conventional enterprise NCM:** LOW

The DSA is primarily relevant to providers of intermediary services and online platforms.

A private enterprise NCM used to manage network infrastructure is generally not the typical DSA use case.

Reassess if the product evolves into a public online platform involving:

- user-generated content;
- public listings;
- public user interaction;
- content hosting;
- marketplace functionality.

---

# 10. AI Act

**Legal instrument:** Regulation (EU) 2024/1689

**Priority:** CONDITIONAL

The AI Act becomes relevant if NCM contains AI systems.

Potential NCM AI features:

- AI configuration generation;
- AI configuration validation;
- AI incident analysis;
- AI anomaly detection;
- AI-based device recommendations;
- AI-powered SOC/NOC assistant;
- automatic remediation;
- AI-based user profiling or decision-making.

The exact obligations depend on the AI system and its use case.

Recommended architecture:

    AI Inventory
        |
        +-- System ID
        +-- Provider
        +-- Model
        +-- Purpose
        +-- Data
        +-- Risk classification
        +-- Human oversight
        +-- Logging
        +-- Evaluation
        +-- Security controls

Do not classify every AI feature as high-risk automatically.

---

# 11. Consumer protection

**Priority:** CONDITIONAL

If NCM is sold only B2B to enterprises, many consumer-specific requirements may not apply in the same way as they would for a B2C product.

If the platform is offered to consumers, assess:

- Consumer Rights Directive
- Unfair Commercial Practices Directive
- applicable distance-selling requirements
- digital-content/service rules

For a purely enterprise NCM product, these are generally lower priority.

---

# 12. Product liability

**Relevant framework:** EU Product Liability Directive (EU) 2024/2853

**Priority:** HIGH for commercial software/product vendors

The updated EU product liability framework expands the rules to the modern digital environment, including software in relevant circumstances.

An NCM vendor should maintain:

- version history;
- release records;
- security testing evidence;
- vulnerability records;
- incident records;
- patch history;
- technical documentation;
- customer notices;
- configuration/change records;
- evidence of reasonable security measures.

---

# 13. Accessibility

**Relevant framework:** European Accessibility Act, Directive (EU) 2019/882

**Priority:** CONDITIONAL

Assess accessibility obligations if the NCM is offered as a covered service/product to consumers or falls within another covered category.

For an enterprise-only internal NCM, applicability may differ.

Recommended UI practices regardless:

- keyboard navigation;
- sufficient contrast;
- accessible forms;
- screen-reader support;
- semantic HTML;
- accessible error messages;
- non-colour-only status indicators.

---

# 14. NCM security baseline

The following should be treated as the minimum technical security baseline for an EU-oriented commercial NCM.

## Identity

- MFA
- RBAC
- SSO
- Session management
- Password policy
- API authentication
- Service-account controls
- Least privilege

## Secrets

- No plaintext credentials
- Vault-based secret storage
- Encryption at rest
- Encryption in transit
- Credential rotation
- SSH key management
- API key rotation
- Secret access auditing

## Network

- TLS
- SSH
- Certificate validation
- Secure management protocols
- Network segmentation
- Egress controls
- Firewalling
- Rate limiting

## Configuration

- Version control
- Configuration snapshots
- Diff
- Approval
- Rollback
- Change history
- Integrity verification

## Logging

Every privileged action should record:

- user/service identity;
- timestamp;
- source;
- target;
- action;
- result;
- affected object;
- request/change ID.

## Monitoring

- Authentication monitoring
- Privilege escalation monitoring
- Configuration change monitoring
- Failed deployment monitoring
- Suspicious API activity
- Security event correlation

---

# 15. Recommended NCM compliance architecture

    +------------------------------------------------------+
    |                    NCM PLATFORM                      |
    +------------------------------------------------------+
    |                                                      |
    |  IAM / RBAC / MFA                                    |
    |  Secrets Vault                                       |
    |  Audit Logging                                       |
    |  Configuration Versioning                            |
    |  Change Approval                                     |
    |  Vulnerability Management                            |
    |  Incident Management                                 |
    |                                                      |
    +-------------------------+----------------------------+
                              |
                    Secure Management Layer
                              |
              +---------------+---------------+
              |               |               |
             SSH           NETCONF         RESTCONF
              |               |               |
              +---------------+---------------+
                              |
                    Network Infrastructure

    Compliance Layer
    ├── CRA
    ├── NIS2 readiness
    ├── GDPR
    ├── ePrivacy
    ├── Cybersecurity Act
    ├── Product Liability
    ├── AI Act (if AI)
    └── Data Act (if applicable)

---

# 16. Required compliance documentation

Recommended documentation set:

1. Product Security Policy
2. Cybersecurity Risk Assessment
3. Threat Model
4. Secure Development Lifecycle
5. Vulnerability Disclosure Policy
6. Vulnerability Management Procedure
7. Incident Response Plan
8. Security Update Policy
9. Security Support Policy
10. Software Component Inventory / SBOM
11. Technical Documentation
12. Configuration Management Policy
13. Access Control Policy
14. Cryptography Policy
15. Logging and Monitoring Policy
16. Backup and Recovery Policy
17. Business Continuity Plan
18. Disaster Recovery Plan
19. Privacy Policy
20. Data Retention Policy
21. Data Processing Agreements where applicable
22. Subprocessor Register where applicable
23. EU Declaration of Conformity where required
24. CE documentation where required
25. Customer Security Documentation
26. Security Architecture Document
27. Penetration Test Reports
28. Security Test Reports
29. Release Security Checklist
30. Vulnerability Disclosure / PSIRT procedure

---

# 17. Compliance priority matrix

| Framework | NCM applicability | Priority |
|---|---|---:|
| Cyber Resilience Act | Very likely / must assess | CRITICAL |
| GDPR | If personal data is processed | HIGH |
| NIS2 | Mainly dependent on vendor/customer scope | HIGH |
| Product Liability Directive | Commercial software/product | HIGH |
| Cybersecurity Act | Certification framework / strategic | MEDIUM |
| ePrivacy | Web/SaaS tracking | MEDIUM |
| AI Act | If AI is included | CONDITIONAL |
| Data Act | Certain connected-data scenarios | CONDITIONAL |
| DSA | Usually not relevant to enterprise NCM | LOW |
| Consumer protection | Mainly B2C | CONDITIONAL |
| Accessibility | Depends on product/service scope | CONDITIONAL |

---

# 18. CRA implementation timeline

| Date | Requirement |
|---|---|
| 10 Dec 2024 | CRA entered into force |
| 11 Jun 2026 | Certain provisions concerning conformity-assessment bodies apply |
| 11 Sep 2026 | CRA vulnerability/incident reporting obligations apply |
| 11 Dec 2027 | Main CRA obligations become applicable |

---

# 19. Important distinction

A platform being **"NIS2 compliant"** is not the same thing as the NCM product being compliant with the **CRA**.

For the NCM vendor:

    CRA
      ↓
    Product-level cybersecurity
      ↓
    Secure development
      ↓
    Vulnerability handling
      ↓
    Conformity assessment
      ↓
    CE / Declaration of Conformity where applicable

For a regulated NCM customer:

    NIS2
      ↓
    Organisation-level cybersecurity
      ↓
    Risk management
      ↓
    Incident response
      ↓
    Business continuity
      ↓
    Supplier / supply-chain security

The NCM product should therefore be **CRA-oriented** while also providing controls and evidence that help customers satisfy their own NIS2/security obligations.

---

# 20. Official EU sources

- European Commission — Cyber Resilience Act
- European Commission — CRA Summary
- European Commission — CRA Conformity Assessment
- European Commission — CRA Reporting
- European Commission — NIS2 Directive
- European Commission — GDPR
- European Commission — AI Act
- European Commission — Cybersecurity Act
- European Commission — Data Act
- European Commission — Digital Services Act
- European Commission — Product Liability

## Legal references

- Regulation (EU) 2024/2847 — Cyber Resilience Act
- Directive (EU) 2022/2555 — NIS2
- Regulation (EU) 2016/679 — GDPR
- Directive 2002/58/EC — ePrivacy
- Regulation (EU) 2019/881 — Cybersecurity Act
- Regulation (EU) 2023/2854 — Data Act
- Regulation (EU) 2022/2065 — Digital Services Act
- Regulation (EU) 2024/1689 — AI Act
- Directive (EU) 2024/2853 — Product Liability

---

## Final recommendation

For a commercial NCM platform targeting the EU, implement the product around:

**CRA + secure-by-design + vulnerability management + strong IAM + secrets management + immutable auditability + configuration integrity + GDPR controls + NIS2-oriented security evidence.**

The exact legal classification should be confirmed against the final product architecture, distribution model, deployment model, customer sectors and applicable CRA product category before making a formal conformity claim.
