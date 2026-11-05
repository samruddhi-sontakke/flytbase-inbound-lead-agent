# Lead Desk test cases

How to use: send each case as its own email **from samruddhisontkke@gmail.com to sontakkesamruddhijain89@gmail.com**
(email subject = the "Email subject" line, email body = the block), or paste the block into the web app (New lead), or save the block
to a .txt file and run `py run.py --input that_file.txt`. The cron (`/process-inbox`, every 5 min) picks up new mail.
Contacts below are **fictional test people**. Companies are real so the research stage has public data to find.

---

## 1. Different region and industry: EMEA utility (tests routing, research, partner logic outside LATAM)
Email subject: Drone-in-a-box for substation and line inspection
```
Source: flytbase.com/contact
From: Test Contact A (ops.test@eon-example.com)
Title: Head of Asset Inspection, Grid Operations
Company: E.ON SE, Germany
Subject: Drone-in-a-box for substation and line inspection
Context: We inspect ~40 high-voltage substations in Bavaria manually every month. Looking at docked drones for routine thermal and visual inspection, ideally BVLOS. Evaluating vendors this quarter; procurement wants a pilot proposal by January.
```
Expected: lead; region EMEA; P1 or P2; case study about utilities or substations; partner search in Germany/EMEA; BVLOS regulation shows up as a risk.

## 2. Informal email, no form fields (tests that the agent judges content, not just markers)
Email subject: quick question about your docks
```
Hi FlytBase team,

I run security for a few container terminals at the Port of Rotterdam. Our night patrols are understaffed and we keep
getting perimeter alarms we can't verify fast enough. Do your docked drones work for 24/7 perimeter response, and roughly
what would a 2-site setup look like? Happy to jump on a call next week.

Best,
Test Contact B
Security Manager, Hutchison Ports ECT Rotterdam
```
Expected: lower marker score (hint possible_lead) but the agent opens the full mail and decides **lead**; security use case; EMEA.

## 3. Low fit (tests the P3 tier and an honest score)
Email subject: drone for my farm
```
Source: flytbase.com/contact
From: Test Contact C (testfarmer@gmail.com)
Title: Owner
Company: Family farm, Maharashtra, India
Subject: drone for my farm
Context: I have 15 acres of grapes and want a drone to spray and take photos. What is the price?
```
Expected: lead, but **P3 nurture** (small site, consumer email, no enterprise fit); the emails are a polite redirect, not an enterprise sequence.

## 4. Spanish-language lead, LATAM (tests language handling and the Spanish offer)
Email subject: Inspección autónoma de relaves
```
Source: flytbase.com/contact
From: Contacto de Prueba D (operaciones.test@codelco-example.cl)
Title: Gerente de Operaciones, División El Teniente
Company: Codelco, Chile
Subject: Inspección autónoma de relaves
Context: Buscamos inspección autónoma con drones para tranques de relaves y correas transportadoras, operación 24/7. Nos interesa un piloto en 2027 y queremos entender integración con nuestros sistemas de monitoreo.
```
Expected: lead; LATAM mining; research on Codelco / El Teniente; may surface the same Novandino link as the SQM run; emails offered in Spanish.

## 5. Not a lead: vendor pitch (tests the not-a-lead verdict)
Email subject: Partnership opportunity - boost your SEO 300%
```
Hi there,

We're a digital marketing agency helping drone companies rank #1 on Google. We noticed flytbase.com could get 300% more
traffic. Can we book 15 minutes to show you our packages? Prices start at $499/month.

Cheers,
Growth Team
```
Expected: **not a lead** (vendor pitch) with a reason; labelled `LeadDesk/Not a lead`; no lead created.

## 6. Not a lead: job application (tests a near-miss that mentions FlytBase)
Email subject: Application for BDR role at FlytBase
```
Dear Hiring Team,

I am writing to apply for the Business Development Representative role at FlytBase in Pune. I have 2 years of SaaS
sales experience and am passionate about drones. Please find my resume attached.

Regards,
Test Candidate E
```
Expected: **not a lead** (job application), even though it mentions FlytBase and drones.

## 7. Partner / reseller enquiry (tests a borderline call: a partnership enquiry from a potential channel)
Email subject: Becoming a FlytBase reseller in Peru
```
Source: flytbase.com/contact
From: Test Contact F (ventas.test@dronesperu-example.pe)
Title: Commercial Director
Company: Drone services integrator, Lima, Peru
Subject: Becoming a FlytBase reseller in Peru
Context: We deploy DJI docks for mining clients in southern Peru and want to resell FlytBase. Several clients are asking for remote operations software.
```
Expected: the agent decides lead or not and records why. A partner enquiry that brings end customers is reasonably a lead (partner track); the
Stage 5 motion should be partner-led.

## 8. Duplicate (tests deduplication)
Send case 1 again as a **reply in the same Gmail thread**, or re-paste the same text in the web app.
Expected: the same Gmail message never creates two leads (unique index on the message id). A web-app re-paste creates a new lead on purpose (re-run).

---

## What to check after each run
- **Inbox page** (web app): verdict, marker score and reason for every mail.
- **Gmail:** labels `LeadDesk/Seen` plus `Lead` / `Not a lead`; mail still unread; nothing sent or drafted.
- **Lead page:** live progress, each stage tab, the PDF checklist per stage (should be all green), sources tab, agent trace tab.
- **outputs/run_*/REPORT.html:** the full report with the requirements check.
