# Inbound Lead Report: Test Contact A - E.ON SE
_Generated automatically by the Inbound Lead Desk agent (Claude Code, one subagent per stage) on 2026-11-05 20:03 in 973s (6 subagent calls, 44 sources). Every research fact links to its source._

> **E.ON's Head of Asset Inspection (Grid Operations) wants docked drones for routine thermal and visual inspection of ~40 HV substations in Bavaria, ideally BVLOS. Vendors are being evaluated this quarter and procurement wants a pilot proposal by January. ICP 74, priority 67 (P2), no warm intro, no existing FlytBase relationship. Run it as an AE-led co-sell with Droniq.**

## Assignment requirements check
_Each requirement in the assignment PDF, checked in Python against the stage output._

| Stage | Requirement | Met |
|---|---|---|
| 1 Qualification | Framework stated and explained | yes |
| 1 Qualification | Known information extracted from the email (Identify Pain) | yes |
| 1 Qualification | Missing information required for full qualification (Metrics, Economic Buyer, Decision Criteria, Decision Process, Paper Process, Champion, Competition) | yes |
| 1 Qualification | Fit assessment (every ICP factor rated with a reason) | yes |
| 1 Qualification | Priority score with reasoning (67/100, P2 - Warm: respond within 24h, BDR-led discovery) | yes |
| 2 Deep account research | Organizational structure and reporting lines (INFERENCE (not sourced): the contact signs as 'Head of Asset Inspection, Grid Operations' at E.ON SE, but ~40 HV substations in Bavaria fall in the Bayernwerk Netz GmbH grid area (S28). The role probably sits in Bayernwerk Netz's high-voltage organisation (the 'Leiter der Hochspannung' area, S28) or in an asset management/technical function under it. That function reports up to the Bayernwerk AG management board (CEO Westphal, CFO Groher, S33), which in turn reports into E.ON's Energy Networks division. Procurement, which the email names, is probably a Bayernwerk or E.ON procurement function separate from the contact's line. The economic buyer is likely the head of the high-voltage area or a Bayernwerk board member, not the contact.) | yes |
| 2 Deep account research | Budget signals from public filings (capex, opex, technology) | yes |
| 2 Deep account research | Recent news, press releases, strategic announcements | yes |
| 2 Deep account research | Stakeholder or investor letters revealing priorities | yes |
| 2 Deep account research | Synthesized FlytBase positioning recommendation | yes |
| 2 Deep account research | All research real: every kept claim cites a stored source and passed the fact-check (46 claims checked, 6 removed) | yes |
| 3 Response generation | Reflects Stage 2 research (each email cites kept research) (email 1: S28, S36, S7, S31; email 2: S7, S36, S26, S17, S31; email 3: S32, S13, S14, S7; email 4: S11) | yes |
| 3 Response generation | Aims to discover the Stage 1 unknowns (email 1: Decision Criteria, Decision Process; email 2: Metrics, Paper Process; email 3: Competition, Champion; email 4: Economic Buyer) | yes |
| 3 Response generation | Tone adapted to seniority, industry and stated context | yes |
| 3 Response generation | Clear progression logic (why this email, then this email) (4 emails, 5 reply branches) | yes |
| 4 Case study matching | Autonomously searched FlytBase's public website for case studies (24 case studies scanned) | yes |
| 4 Case study matching | Referral connection identified (no hard-coding) (found=False ) | yes |
| 4 Case study matching | Matched on industry, use case and operational context | yes |
| 4 Case study matching | Explains why the case study is the strongest fit (EnBW Case Study: Autonomous Drones for Gigawatt Solar Portfolio | FlytBase) | yes |
| 4 Case study matching | Primary match is a page the crawler actually read | yes |
| 5 Partner identification | Direct AE or partner-led motion for the region decided (AE-led with partner (co-sell)) | yes |
| 5 Partner identification | Justified by region, deal complexity and partner availability | yes |
| 5 Partner identification | If partner-led: specific partner type and rationale (Droniq (Reseller), Solectric (Reseller), Drone Architect (other)) | yes |
| 5 Partner identification | Every named partner appears in a stored source | yes |
| 6 AE handoff | Buyer context: who he is, what he cares about, who else is involved | yes |
| 6 AE handoff | Qualification status: framework score, knowns, unknowns | yes |
| 6 AE handoff | Top 3 research highlights, each citing kept research | yes |
| 6 AE handoff | Recommended case study and why | yes |
| 6 AE handoff | Suggested next step with rationale (BDR sends the same-day reply (Email 1) and books a 30-minute discovery call, offering Tue 10 Nov 10:00 CET or Wed 11 Nov 15:00 CET, with the call in German if preferred. The AE joins and runs the call to close the highest-risk gaps: who the economic buyer is and which entity contracts (E.ON SE or Bayernwerk Netz), the tender or vendor-onboarding format, decision criteria, competing vendors, and how the 40 substations relate to the existing robot sites. Send the one-page pilot outline (1-2 docks, thermal and visual missions, a compliant start with the SORA 2.5 BVLOS application in parallel) before the call. After the call, the AE asks the FlytBase partner manager to bring Droniq in for the second meeting.) | yes |

## Stage 1 - Qualification (MEDDPICC)
**Why MEDDPICC:** MEDDPICC fits this lead because E.ON is a large enterprise utility buying an autonomous inspection program across ~40 high-voltage substations in Bavaria: a multi-site purchase where grid operations (the contact), procurement (already named in the email), safety, IT/OT security and likely aviation/BVLOS regulatory stakeholders all have a say, and where a regional integrator or reseller may shape the pilot. The email gives strong Pain and timeline signals but leaves the Economic Buyer, Decision Criteria, Paper Process details, Champion and Competition open, and MEDDPICC makes those gaps explicit so the first emails can target them. BANT would capture budget/authority/need/timing but is too shallow for a procurement-led, multi-stakeholder pilot; SPICED is designed for recurring SaaS expansion and impact framing rather than a formal enterprise vendor evaluation with a procurement deadline.

| ICP fit | MEDDPICC completeness | Priority score | Tier |
|---|---|---|---|
| 74/100 | 50% | **67/100** | P2 - Warm: respond within 24h, BDR-led discovery |

_Formula: priority = 0.7 x ICP fit + 0.3 x MEDDPICC completeness; tier set by ICP fit (>=75 P1, >=55 P2)_

| Element | Status | Known from email | Missing | Discovery question |
|---|---|---|---|---|
| Metrics | partial | We inspect ~40 high-voltage substations in Bavaria manually every month. | Quantified target outcome: inspection hours/cost per substation today, crew size, defect detection rate, outage/incident cost, desired inspection frequency with drones. | How many crew hours and how much cost does one monthly round of the 40 substations take today, and what would a successful pilot need to improve? |
| Economic Buyer | unknown | - | Who owns the budget for the inspection program and signs off the pilot and rollout. | Besides your team and procurement, who would own the budget and final approval for a pilot and a wider rollout? |
| Decision Criteria | partial | Docked drones for routine thermal and visual inspection, ideally BVLOS. | Full technical and commercial criteria: dock/drone hardware preferences, BVLOS approval support, data/security and on-prem requirements, integration with asset management, pricing model. | Beyond thermal, visual and BVLOS capability, what criteria will you use to compare vendors, for example hardware choice, data hosting, or integration with your asset management systems? |
| Decision Process | partial | Evaluating vendors this quarter; procurement wants a pilot proposal by January. | Steps after the pilot proposal, who evaluates, how many vendors are shortlisted, pilot success criteria and decision date for rollout. | What happens after the pilot proposal goes to procurement in January: who reviews it, and how will you decide whether to move from pilot to rollout? |
| Paper Process | partial | Procurement wants a pilot proposal by January. | Procurement format (RFP/tender), vendor onboarding, IT/OT security and legal review, contracting entity, whether a partner/reseller is required. | Does procurement run this as a formal tender, and are there security, legal or vendor-onboarding reviews we should prepare for in parallel? |
| Identify Pain | known | We inspect ~40 high-voltage substations in Bavaria manually every month. Looking at docked drones for routine thermal and visual inspection. | Consequence of the pain: safety exposure of crews in HV environments, missed defects, outages, staffing constraints. | What is the biggest cost of doing these inspections manually today: crew time, safety exposure in the substations, or defects caught too late? |
| Champion | partial | Contact is Head of Asset Inspection, Grid Operations, and reached out proactively via flytbase.com/contact. | Whether the contact will actively sponsor FlytBase internally and has influence with the economic buyer and procurement. | Would you be the one leading the pilot internally, and who else should we bring into the conversation early? |
| Competition | partial | Evaluating vendors this quarter. | Which other vendors are being evaluated, and whether in-house or status-quo manual inspection is a real alternative. | Which other drone-in-a-box or inspection vendors are you looking at, and what has stood out so far? |

**Fit assessment**

| Factor | Weight | Rating (0-5) | Reason |
|---|---|---|---|
| industry_fit | 20 | 5 | Energy utility grid operations: 'high-voltage substations' and 'line inspection' are core heavy-industry outdoor assets. |
| site_scale | 15 | 4 | '~40 high-voltage substations in Bavaria' is a large multi-site footprint, though limited to one region. |
| continuous_operations | 10 | 3 | Grid assets need recurring checks ('manually every month', 'routine thermal and visual inspection'), but 24/7 operations are not stated. |
| pain_severity | 15 | 4 | Monthly manual inspection of ~40 HV substations is a clear cost and safety burden that docked drones directly remove; consequences are not quantified. |
| buyer_authority | 15 | 4 | 'Head of Asset Inspection, Grid Operations' owns the operational problem; budget authority is not stated. |
| warm_introduction | 10 | 0 | No referral or existing relationship mentioned; inbound via flytbase.com/contact. |
| timing_and_budget | 15 | 4 | 'Evaluating vendors this quarter; procurement wants a pilot proposal by January' is a concrete timeline with procurement engaged; no budget figure. |

**Verdict:** Strong ICP fit: a German energy utility's Head of Asset Inspection wants docked drones for thermal/visual inspection of ~40 HV substations, with an active vendor evaluation and a January pilot proposal deadline. Pain, use case and timeline are clear; economic buyer, decision criteria detail, paper process, champion strength and competitors remain to be uncovered. No warm introduction, so priority rests on fit and urgency.

**Risks:** Economic buyer and budget are not identified; pilot could stall without budget owner sponsorship; Competitive vendor evaluation already underway this quarter; BVLOS approval in Germany (EU/LBA regulation) may slow or limit the pilot; Tight timeline: pilot proposal due by January; Procurement-led process may require tender format, security and IT/OT reviews, or a local partner; Large utility with many stakeholders can lengthen pilot-to-rollout cycle

## Stage 2 - Deep Account Research

**Organisational structure**

- In a November 2020 Bayernwerk press release Dr. Egon Leo Westphal was described as Bayernwerk's technical board member (Technikvorstand) and was quoted supporting drones to make overhead-line inspection more efficient. [[S24](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/digitalisierung-im-stromnetz-drohne-ersetzt-helikopter-3049586)]
  - _So what:_ Bayernwerk's current CEO has gone on record backing drone inspection, which helps when escalating the pilot.
- Bayernwerk Netz has dedicated high-voltage leadership roles: Günther Mertel was quoted as 'Leiter der Hochspannung' in November 2025, and Stephan Engelbrecht as 'Leiter Hochspannungsleitungen' and Peter Ketterl as 'Leiter Technik Ostbayern' in October 2025. [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111), [S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988)]
  - _So what:_ The high-voltage unit owns substations and lines, so it is the most likely home of the economic buyer or technical approver for an HV substation pilot.
- Bayernwerk Netz organises its network through regional customer centres. The Schwandorf customer centre alone serves about 267,000 people over a 10,337 km grid connected by 21 substations and switching stations. [[S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988)]
  - _So what:_ Substations are spread across regional units, so a dock rollout needs remote, central operation instead of local pilots at each site.
- In February 2021 E.ON named Thomas König as the board member responsible for networks when it announced an AI-based overhead-line inspection partnership with eSmart Systems. [[S14](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/)]
  - _So what:_ Group-level network leadership has publicly sponsored inspection digitalisation and start-up partnerships before. This source is from 2021, so his current role needs checking.
- E.ON's subsidiaries first piloted individual inspection robots, each with its own interface and data model, and then converged on a single shared robot platform ('one grid, one robot platform'). [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]
  - _So what:_ E.ON has shown it prefers one hardware-agnostic platform across subsidiaries. That matches a fleet and orchestration software pitch.

**Stakeholders found in public sources**

- **Günther Mertel**, Leiter der Hochspannung, Bayernwerk Netz GmbH - Head of the high-voltage area, which covers HV substations. Likely technical approver or budget holder for the contact's pilot. [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111)]
- **Stephan Engelbrecht**, Leiter Hochspannungsleitungen, Bayernwerk Netz GmbH - Owns HV lines, the natural phase-2 scope after substations (line inspection is in the lead's subject). [[S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988)]
- **Peter Ketterl**, Leiter Technik Ostbayern, Bayernwerk Netz GmbH - Regional technical head who speaks publicly on grid security, stability and resilience. [[S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988), [S30](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ambitionierter-netzausbau-fuer-heimatenergie-3447669)]
- **Michael Renghart**, Bayernwerk (title not stated in source) - Quoted as the Bayernwerk voice on the autonomous substation inspection robot pilot. Possible internal ally or knowledge holder on substation automation. [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)]
- **Thomas König**, E.ON Board of Management member responsible for networks (as of Feb 2021) - Group-level sponsor of earlier drone and AI inspection partnerships. His current role needs verifying. [[S14](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/)]

_Likely reporting line (inference):_ INFERENCE (not sourced): the contact signs as 'Head of Asset Inspection, Grid Operations' at E.ON SE, but ~40 HV substations in Bavaria fall in the Bayernwerk Netz GmbH grid area (S28). The role probably sits in Bayernwerk Netz's high-voltage organisation (the 'Leiter der Hochspannung' area, S28) or in an asset management/technical function under it. That function reports up to the Bayernwerk AG management board (CEO Westphal, CFO Groher, S33), which in turn reports into E.ON's Energy Networks division. Procurement, which the email names, is probably a Bayernwerk or E.ON procurement function separate from the contact's line. The economic buyer is likely the head of the high-voltage area or a Bayernwerk board member, not the contact.

**Budget signals (capex / opex / technology)**

- In February 2026 E.ON raised its investment plan to around EUR 48 billion for 2026-2030 (previously EUR 43 billion for 2024-2028), with about EUR 40 billion earmarked for Energy Networks, assuming an adequate regulatory framework. [[S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096), [S12](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-concludes-fiscal-year-with-strong-earnings-and-record-investments-in-the-energy-transition-2091497)]
  - _So what:_ Grid capex is growing for years to come. An inspection programme that protects or extends those assets fits the spending direction.
- E.ON's Energy Networks investments rose from about EUR 5.8 billion in 2024 to EUR 7.0 billion in 2025, a 20 percent increase, mainly for new grid connections and modernising network infrastructure. [[S12](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-concludes-fiscal-year-with-strong-earnings-and-record-investments-in-the-energy-transition-2091497), [S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)]
  - _So what:_ Modernisation is an explicit spending category, so autonomous inspection can be positioned as part of modernisation and digitalisation.
- In Q1 2026 E.ON's Energy Networks investments were EUR 1.1 billion, 9 percent below the prior year because very cold weather in January postponed network work. E.ON said it remains committed to its full-year investment plan. [[S17](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-off-to-a-good-start-to-the-year-in-a-challenging-environment-2326600)]
  - _So what:_ Weather limits crews. A docked drone that inspects when crews cannot travel supports the reliability case.
- Bayernwerk Netz budgeted EUR 280 million for grid work in the Oberpfalz alone in 2026, 27 percent more than the EUR 220 million of 2025. [[S30](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ambitionierter-netzausbau-fuer-heimatenergie-3447669)]
  - _So what:_ Regional budgets are rising fast. That supports a pilot in one region with a path to others.
- Bayernwerk Netz said it would spend more than EUR 100,000 in 2024 on helicopter safety inspection of its high-voltage lines, covering about 1,200 km in three weeks. [[S26](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988)]
  - _So what:_ This is a concrete, publicly stated spend on manned aerial inspection that drones could partly replace. Useful for a line-inspection ROI comparison.

**Recent news and announcements**

- In October 2026 E.ON confirmed it is working on a simpler steering model between headquarters and operating units under an efficiency programme called 'Polaris'. Manager Magazin reported a 20-25 percent cost-reduction target starting in spring 2027, which E.ON did not comment on. [[S19](https://www.zfk.de/unternehmen/nachrichten/eon-prueft-mit-polaris-den-umbau-seiner-organisation)]
  - _So what:_ Cost pressure and possible reorganisation are coming. Frame the pilot around measurable cost and hours saved, and expect stakeholders to change.
- In September 2026 a series of sabotage attacks on the German power grid, aimed at large-scale outages, led to federal-state talks on how critical infrastructure operators can protect themselves. Bavarian premier Söder proposed plant security guards (Werksicherheitswachten) that could defend against drones. [[S34](https://www.zfk.de/politik/deutschland/drohnen-abschuss-netzbetreiber-amprion-chef-kontra)] _(partially verified)_
  - _So what:_ Physical security of substations is now a political priority in Bavaria. Remote visual checks of fences and yards add a security benefit, but the company's own drones must be clearly distinguished from hostile ones.
- An IISS study published in July 2026 analysed 144 drone incidents in Europe between August 2024 and February 2026. Germany had the most reported sightings (58), and about 26 percent of sightings were linked to critical infrastructure. [[S44](https://www.zfk.de/politik/drohnen-kritis-deutschland-russland-studien)]
  - _So what:_ Grid operators are wary of drones near substations, so a pilot must address airspace coordination, identification and data security from day one.
- In November 2025 Bayernwerk Netz said a planned new substation near Rottenburg an der Laaber, linking TenneT's 380-kV network with Bayernwerk's 110-kV network, must be built on time by 2033. [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111)]
  - _So what:_ Bayernwerk keeps adding HV substations, so the inspection workload grows unless it is automated.
- In May 2026 Bayernwerk Netz said that, besides grid expansion and digitalisation, security, stability and resilience of the energy system are moving further into focus. [[S30](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ambitionierter-netzausbau-fuer-heimatenergie-3447669)]
  - _So what:_ Resilience is the operator's own word for its priority. Pitch docked drones as resilience infrastructure as well as a cost tool.

**Investor / stakeholder priorities**

- In the FY2025 results release, CEO Leonhard Birnbaum said E.ON is accelerating network expansion and consistently digitalising the energy system, and that investments must earn a fair return to be financed sustainably. [[S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)]
  - _So what:_ Digitalising grid operations is an investor-facing priority. The pilot should show return, not just novelty.
- E.ON's FY2025 release says security of supply and resilience are becoming more demanding, driven by system volatility and 'a heightened threat landscape for critical infrastructure'. [[S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)]
  - _So what:_ Resilience and critical-infrastructure protection are part of the group's investor message, which strengthens the case for continuous remote monitoring of substations.
- In February 2025 E.ON kept its 2024-2028 investment programme unchanged, citing a lack of visibility on Germany's regulatory framework, and Birnbaum said E.ON requires a return on network investments that is competitive internationally. [[S12](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-concludes-fiscal-year-with-strong-earnings-and-record-investments-in-the-energy-transition-2091497)]
  - _So what:_ Regulated returns limit capex appetite. Opex-saving tools that need little capital may get approved more easily than large capex items.
- CFO Nadia Jakobi said in February 2026 that growth through 2030 rests on operating performance, efficiency and consistent digitalisation, with strict discipline in all investment decisions. [[S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)]
  - _So what:_ Lead with efficiency metrics (crew hours, travel, inspection frequency per euro) to match the CFO's message.

**Operations context**

- Bayernwerk Netz inspects its high-voltage lines from the air every two years as routine, with a technician viewing every line from above at least every four years. Helicopter flights depend on the weather because inspectors need clear visibility. [[S26](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988)]
  - _So what:_ Today's inspection is periodic and weather-dependent. Docked drones offer higher frequency and flights on demand.
- A Bayernwerk representative said in November 2023 that Bayernwerk's substations were largely built between the 1950s and 1970s. [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461), [S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]
  - _So what:_ Ageing substations need closer condition monitoring, especially thermal checks for overheating, which suits routine thermal drone flights.
- E.ON's subsidiaries faced substation inspection requirements that increased as assets aged, while experienced technicians became harder to staff and retain, and drive time to sites consumed engineering hours. [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]
  - _So what:_ Labour shortage and travel time are pains E.ON has already named, and both are central to a drone-in-a-box ROI case.
- In Germany, BVLOS flights for grid inspection fall under the specific category of EU Regulation 2019/947 and require an operational authorisation from the Luftfahrt-Bundesamt. Since 1 January 2026 new applications must use SORA 2.5, with processing times of about two to four months. [[S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)]
  - _So what:_ An approval of two to four months collides with a pilot proposal due in January. FlytBase should propose starting with VLOS or remote-supervised operation while the BVLOS application runs in parallel.
- The Luftfahrt-Bundesamt has approved BVLOS operations for a Percepto client in Germany using drone-in-a-box technology, allowing fully automated flights without visual observers on site, around the clock. [[S32](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/)]
  - _So what:_ Docked BVLOS approval in Germany has been granted before, so the regulatory path exists. It also shows a competitor is already active in this market.

**Technology and drone adoption**

- Since January 2022 Bayernwerk has run an autonomous inspection robot at one of its substations using Energy Robotics software. The AI reads analogue gauges such as oil levels, detects overheating by thermography and spots holes in the fence. [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)]
  - _So what:_ Bayernwerk already accepts autonomous, AI-analysed substation inspection. Drones add aerial views and cover more sites, so they complement this robot rather than compete with it.
- E.DIS, Bayernwerk and Avacon converged on a single shared platform from Korial to run autonomous mobile robots in substations. [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]
  - _So what:_ There is a robotics platform incumbent. FlytBase must show it can integrate with existing robot and inspection data flows or work alongside them.
- In an October 2024 article, E.ON said that in Germany more than 270 pilots are trained to operate 100 drones, and that in Sweden switching from helicopters to drones let it detect ten times more faults. [[S13](https://news.eonenergy.com/news/how-drones-are-helping-secure-power-grids)]
  - _So what:_ E.ON already has drone skills in-house. The gap is automation and scale (docks, remote operations), not basic drone adoption.
- In November 2020 Bayernwerk announced its NEXT.LineInspect project to have drones increasingly take over overhead-line monitoring from helicopters, with AI comparing images to the target condition, and started staff drone training with start-up U-ROB. [[S24](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/digitalisierung-im-stromnetz-drohne-ersetzt-helikopter-3049586)]
  - _So what:_ Bayernwerk planned to move from helicopters to drones years ago. Docked drones are the next step toward autonomous operation.
- In 2021 E.ON deployed eSmart Systems' AI software to analyse drone images across E.DIS, MITNETZ STROM and Westnetz (about 45,000 km of lines), and in 2020 MITNETZ STROM flew a fully automated BVLOS line-inspection test with FlyNex. [[S14](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/), [S16](https://commercialuavnews.com/energy/flynex-performs-bvlos-flights-to-inspect-power-lines)]
  - _So what:_ E.ON's German DSOs have experience with BVLOS and AI image analysis, so FlytBase should integrate with existing analytics rather than replace them.
- In November 2025 CTU Prague, E.ON Group Innovation and EG.D tested HIVE technology for autonomous power-line inspection with cooperating drones, including BVLOS flights and automatic 3D LiDAR scanning. [[S15](https://cyber.felk.cvut.cz/news/collaboration-between-ctu-fee-e-on-and-eg-d-is-bringing-power-grid-inspection-into-the-era-of-autonomous-drones)]
  - _So what:_ E.ON Group Innovation is actively testing autonomous multi-drone BVLOS operations, which could make it an internal ally.

**Positioning recommendation:** Position FlytBase as the hardware-agnostic autonomy and remote-operations layer for docked drones at Bayernwerk's HV substations, the aerial counterpart to the 'one grid, one robot platform' model E.ON's subsidiaries already chose for ground robots. Lead with a tightly scoped pilot on a few of the ~40 Bavarian substations: routine thermal and visual missions flown remotely from a central location, with outputs fed into existing analytics and asset systems, and a parallel LBA SORA 2.5 application for BVLOS. Frame the value in E.ON's own language: efficiency and digitalisation (Polaris cost pressure, the CFO's investment discipline) plus resilience and critical-infrastructure protection (Bayernwerk's resilience project). Present the pilot as an affordable step within Bayernwerk's EUR 12 billion 2026-2030 programme.

- Platform consolidation: E.ON subsidiaries moved from scattered single-vendor robot pilots to one shared platform [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]. Offer the same for aerial inspection, with one orchestration layer across docks, sites and subsidiaries.
- Complement, don't compete, with ground robots: Bayernwerk's substation robot already does thermography and gauge reading [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)]. Docks add aerial thermal views of yards, busbars and lines, cover many sites at once, and do not need a robot at each substation.
- Ageing assets and scarce technicians: substations built 1950s-1970s and hard-to-staff inspection crews [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)][[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]. Remote-operated docks cut drive time and let fewer engineers cover more sites.
- Weather-proof cadence: Q1 2026 grid work slipped because of cold weather [[S17](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-off-to-a-good-start-to-the-year-in-a-challenging-environment-2326600)] and helicopter inspection depends on visibility [[S26](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988)]. Docked drones fly on schedule and on demand after storms.
- Resilience: Bayernwerk's resilience project and the 2026 sabotage and drone-incident debate [[S33](https://mnd-assets.mynewsdesk.com/raw/upload/fl_attachment/o6e69p4msd5o45qt8bn6pw)][[S34](https://www.zfk.de/politik/deutschland/drohnen-abschuss-netzbetreiber-amprion-chef-kontra)][[S44](https://www.zfk.de/politik/drohnen-kritis-deutschland-russland-studien)]. Offer remote perimeter and fence checks and rapid post-incident assessment, framed as the operator's authorised and identifiable fleet.
- Regulatory realism: BVLOS needs an LBA SORA 2.5 authorisation with a two to four month timeline [[S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)], and the LBA has approved docked BVLOS before [[S32](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/)]. Propose a January pilot plan that starts compliantly and moves to BVLOS when approved.
- German utility proof: reference FlytBase's EnBW autonomous drone-dock case study [[S1](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks)] as a peer German energy deployment.

_Likely objections:_ An incumbent robotics platform (Korial/Energy Robotics) is already at Bayernwerk and sister DSOs. Bayernwerk may see substation inspection as covered or ask for integration.; Polaris efficiency programme and possible reorganisation from spring 2027 could change stakeholders, freeze discretionary spend or centralise procurement.; Heightened drone security concerns at critical infrastructure may make security and IT/OT teams wary of permanent drones at substations. Expect requirements on data hosting, airspace and identification.; The LBA SORA 2.5 BVLOS approval (two to four months) may not fit a pilot that starts right after the January proposal.; E.ON already has 270+ trained drone pilots and established AI analytics partners (eSmart Systems). FlytBase must show value beyond what in-house manual drone teams provide.; A competitor with prior German docked BVLOS approval (Percepto) is active in this market.

_Searched for but not found:_ A total public count of Bayernwerk Netz high-voltage substations, and confirmation that the contact's ~40 substations are Bayernwerk's (only regional counts such as 21 in Schwandorf were found).; Any public page naming an 'Asset Inspection, Grid Operations' unit at E.ON SE or Bayernwerk, or the contact's reporting line.; The current E.ON SE board member responsible for Energy Networks from a 2025/2026 source (the E.ON board page could not be read; the latest stored source is from 2021).; E.ON 2025 annual report PDF and CEO letter text (not readable). Investor priorities rely on the official results releases instead.; LinkedIn profiles for Bayernwerk or E.ON operations, digital/innovation and procurement leaders (Chrome tools not available; job-ad pages were blocked).; Procurement leadership or tender process for inspection technology at Bayernwerk or E.ON.; Any existing drone-in-a-box deployment or LBA BVLOS authorisation held by Bayernwerk or E.ON in Germany.; Inspection-specific opex figures (crew cost per substation round) at Bayernwerk. The only spend figure found is the >EUR 100,000 helicopter line inspection in 2024.; Useful Reddit practitioner discussion on German substation drone inspection (searches timed out or returned unrelated posts).

_Fact-check: 6 claim(s) were removed because the cited source did not support them._

## Stage 3 - Adaptive Email Sequence
**Strategy:** Email 1 answers the inbound the same day. It plays back the exact ask (about 40 HV substations in Bavaria, monthly manual rounds, thermal and visual, ideally BVLOS, pilot proposal due to procurement by January) and gives one German energy peer proof point (EnBW). It asks only about decision criteria and what happens after the January proposal. Each later email goes after different MEDDPICC gaps (Metrics and Paper Process, then Competition and Champion, then Economic Buyer) and brings something new from the fact-checked research: drive time and technician scarcity, the LBA SORA 2.5 timeline and how to plan the pilot around it, prior German docked BVLOS approvals, and E.ON's preference for one shared platform. The emails get shorter each time, and the last one is a polite close-the-loop tied to the January deadline.

### Email 1 - Within 1 hour of the inbound (same day, Thu 5 Nov 2026)
**Goal:** Acknowledge the exact request, show we understand their substation and BVLOS context and the January deadline, give one German energy proof point, and book a 30-minute call.  
**Gaps targeted:** Decision Criteria, Decision Process  
**Why this email now:** This is an inbound request in an active vendor evaluation with a fixed January deadline, so speed and relevance matter most. Replying the same day with their own numbers, specifics from E.ON's own substation automation and a realistic BVLOS timeline shows we understood the request and can help them meet the deadline.  
**Success signal:** The contact accepts a slot or proposes another, or answers either question (shares vendor criteria or describes the post-January process).  
**Research used:** [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111), [S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461), [S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk), [S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)]

**Subject:** Docked drones for your ~40 Bavarian substations: input for the January pilot proposal

```text
Hello,

Thank you for reaching out through flytbase.com. As I understand it, your team inspects about 40 high-voltage substations in Bavaria by hand every month. You want docked drones to take over the routine thermal and visual rounds, ideally BVLOS, and procurement wants a pilot proposal by January. You came to us directly through our contact form rather than through a referral, so I have done some homework first.

Two things stood out. If your substations are in the Bayernwerk Netz area, Bayernwerk has run an autonomous ground robot at one of its substations since January 2022, reading gauges and finding hotspots by thermography. E.ON's grid subsidiaries have also moved from separate robot pilots to one shared platform. Docked drones fit alongside that model: they add the aerial view across many sites, run from one central location.

The closest proof point we have is EnBW, another large German energy company. They used DJI Dock 2 with FlytBase to move routine thermal inspection of their solar portfolio from annual to quarterly and cut out six-hour round trips to remote sites. It started as a two-dock proof of concept. Their assets are solar, not substations, but the operating model and the German conditions are the same.

On timing: BVLOS in Germany needs an LBA operating authorisation under SORA 2.5, which currently takes about two to four months. A January proposal can still work if the pilot starts in a compliant mode while the BVLOS application runs in parallel. I'm happy to sketch what that could look like.

Two questions to make the call useful:
1. Beyond thermal, visual and BVLOS, what will you compare vendors on, for example hardware choice, data hosting or integration with your asset systems?
2. Once the proposal reaches procurement in January, how will the decision from pilot to rollout be made?

Would a 30-minute call on Tuesday 10 November at 10:00 CET or Wednesday 11 November at 15:00 CET work? We can also hold the call and all later correspondence in German if you prefer.

Best regards,
Samruddhi Sontakke
Business Development, FlytBase
```

### Email 2 - Day 3 (Mon 9 Nov) if no reply to Email 1
**Goal:** Help them build the business case: quantify today's manual round and find out how procurement will run the pilot. Offer a one-page pilot outline as a resource.  
**Gaps targeted:** Metrics, Paper Process  
**Why this email now:** The contact has to put a pilot in front of procurement by January. A ready-made outline and a request for their baseline numbers help them do that, and they surface Metrics and the paper process early enough to plan security and onboarding reviews.  
**Success signal:** They ask for the outline, share baseline crew hours or cost, or describe the tender or onboarding steps.  
**Research used:** [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk), [S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461), [S26](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988), [S17](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-off-to-a-good-start-to-the-year-in-a-challenging-environment-2326600), [S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)]

**Subject:** A one-page pilot outline for the substation rounds

```text
Hello,

A short follow-up with something you can use for the January proposal.

E.ON's grid subsidiaries have described the same pressure your monthly rounds create: inspection needs rise as assets age, experienced technicians are harder to staff and keep, and drive time to sites eats engineering hours. Bayernwerk has said many of its substations were built between the 1950s and 1970s. Weather is the other limit. Bayernwerk's helicopter line inspections depend on clear visibility, and E.ON's Q1 2026 grid work slipped because of a very cold January. A dock on site flies on schedule and can fly again on demand after a storm, without anyone driving out.

I can send a one-page pilot outline covering 1-2 docks at representative substations, the thermal and visual missions, a compliant start while the SORA 2.5 BVLOS application runs (about two to four months), and the before-and-after numbers to measure. For BVLOS approval and on-site support in Germany we would bring in Droniq, our German partner that has done DJI Dock operating licences and airspace integration.

To make the numbers yours rather than generic:
1. Roughly how many crew hours does one monthly round of the 40 substations take today?
2. Will procurement run the pilot as a formal tender, and should we prepare for security or vendor-onboarding reviews in parallel?

Happy to switch to German at any point.

Best regards,
Samruddhi Sontakke
Business Development, FlytBase
```

### Email 3 - Day 7 (Fri 13 Nov) if still no reply
**Goal:** Show where FlytBase fits next to E.ON's existing drone teams, analytics and other docked BVLOS vendors, and find out who else is being evaluated and who should be involved.  
**Gaps targeted:** Competition, Champion  
**Why this email now:** The contact is evaluating vendors this quarter, and a competitor already holds a German docked BVLOS approval. Raising that openly, and setting FlytBase apart through integration with E.ON's existing investments, gives a reason to talk about competitors and stakeholders.  
**Success signal:** They name competitors or evaluation criteria, or name or copy in other stakeholders (security, the HV team, procurement).  
**Research used:** [[S32](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/), [S13](https://news.eonenergy.com/news/how-drones-are-helping-secure-power-grids), [S14](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/), [S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]

**Subject:** Docked BVLOS in Germany has been approved before

```text
Hello,

One more point that may help your vendor comparison. The LBA has already approved fully automated drone-in-a-box BVLOS flights in Germany for another operator, so the regulatory path exists. What usually separates vendors is what sits around the dock.

E.ON already has a lot in place: more than 270 trained drone pilots in Germany, AI image analysis from eSmart Systems on its lines, and one shared platform for its substation robots. FlytBase's role would be the hardware-agnostic layer that lets a central team run many docks and feeds results into the tools you already use, so nothing you have built gets replaced.

Two quick questions:
1. Which other vendors are you looking at, and what has stood out so far?
2. Besides you, who should be involved early, for example IT/OT security or the high-voltage team?

Best regards,
Samruddhi Sontakke
Business Development, FlytBase
```

### Email 4 - Day 12 (Wed 18 Nov) if no reply to Emails 1-3
**Goal:** Close the loop respectfully, keep the January proposal open, and find the budget owner.  
**Gaps targeted:** Economic Buyer  
**Why this email now:** Three useful messages without a reply means it's time to stop following up. A short, no-pressure close tied to their own deadline makes replying easy and asks for the one gap a non-responsive contact can still fill: who owns the budget.  
**Success signal:** A one-line reply naming the budget owner, a 'later', or a meeting request.  
**Research used:** [[S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)]

**Subject:** Close the loop on the substation pilot

```text
Hello,

I don't want to crowd your inbox during an evaluation, so this is my last note for now.

E.ON has said its growth rests on efficiency and consistent digitalisation, with strict discipline on investment. If it helps, we can build the January pilot proposal around measured crew hours and inspection frequency so it holds up in that review.

If someone else owns the budget or the final sign-off for the pilot, I'd be glad to be pointed to them. If the timing is simply wrong, reply "later" and I'll check back in early December, before the proposal is due.

Best regards,
Samruddhi Sontakke
Business Development, FlytBase
```

**Branches (adapt to his reply)**

- **If he replies:** Positive reply: agrees to a call or asks for the pilot outline  
  **Then:** Confirm the slot with a calendar invite in CET. Send the one-page pilot outline beforehand. Brief the AE on the Stage 6 handoff and alert the FlytBase partner manager so Droniq can join the second meeting once scope is outlined.

  ```text
  Hello,
  
  Thank you, [day/time] CET is confirmed and I'll send an invite shortly. Before then I'll share a one-page pilot outline (1-2 docks at representative substations, thermal and visual missions, a compliant start with the SORA 2.5 BVLOS application in parallel), so we can spend the call on your substations rather than on slides. Our Account Executive will join to cover scope and the January proposal. If there's anyone else you'd like included, for example from the high-voltage team or IT/OT security, feel free to forward the invite.
  
  We can hold the call in German if you prefer.
  
  Best regards,
  Samruddhi Sontakke
  Business Development, FlytBase
  ```
- **If he replies:** "Not now / budget not until later": the budget or approval comes after the January proposal, or the evaluation is on hold  
  **Then:** Accept the timing. Offer the pilot outline and the BVLOS approval timeline as material they can use when the budget opens, since the LBA authorisation takes two to four months and can start early. Set a check-in for the date they name and mark the lead nurture.

  ```text
  Hello,
  
  Understood, thank you for telling me. One thing that may still be worth doing now: the LBA BVLOS authorisation under SORA 2.5 currently takes about two to four months, so groundwork done before the budget is released can shorten the pilot start later. I'll send the one-page pilot outline so it's on file for when the proposal goes ahead, and I'll check back on [date you suggest]. If anything changes sooner, just reply here.
  
  Best regards,
  Samruddhi Sontakke
  Business Development, FlytBase
  ```
- **If he replies:** Referral to someone else: for example "please talk to our procurement / high-voltage lead / innovation team"  
  **Then:** Thank the contact and ask for a short intro, keeping them copied as champion. Write a short, context-rich note to the new person that mentions the original request. Record the new stakeholder against Economic Buyer or Decision Process in the CRM.

  ```text
  Hello,
  
  Thank you, that's very helpful. Would you be willing to introduce us by email, or should I contact [name] directly and mention your request? I'll keep you copied so nothing on the January pilot proposal gets lost.
  
  For [name], a short summary: your team is looking at docked drones for routine thermal and visual inspection of about 40 HV substations in Bavaria, ideally BVLOS, with a pilot proposal due by January. We would bring a German energy reference (EnBW, a two-dock proof of concept), a pilot outline and German BVLOS approval support through our partner Droniq.
  
  Best regards,
  Samruddhi Sontakke
  Business Development, FlytBase
  ```
- **If he replies:** No reply after Email 4  
  **Then:** Stop the active sequence. Set a nurture task for early December (before the January deadline) with one new relevant item, for example a utility or BVLOS update. Try one other channel (a LinkedIn connection note from the BDR) without repeating the emails. Mark the lead 'no response' in the Lead Desk.

  ```text
  Hello,
  
  A brief check-in as your January pilot proposal gets closer. If docked inspection of the Bavarian substations is still on the table, I can send the one-page pilot outline and the current SORA 2.5 BVLOS timeline. If the project has moved on, a one-word reply is fine and I'll close my file.
  
  Best regards,
  Samruddhi Sontakke
  Business Development, FlytBase
  ```
- **If he replies:** Objection: "we already have substation robots / a robot platform"  
  **Then:** Position docks as a complement to the ground robots. Ask how the robot sites relate to the 40 substations in scope and whether results need to land in the same platform.

  ```text
  Hello,
  
  That makes sense, and it's a good starting point. Ground robots cover close-range checks inside a substation. Docked drones add the overhead thermal and visual view and can cover many sites from one central team without a robot at each location. How do the robot sites relate to the 40 substations you're considering, and would drone results need to feed into the same platform? That tells us how to scope a pilot that adds coverage without duplicating what you already have.
  
  Best regards,
  Samruddhi Sontakke
  Business Development, FlytBase
  ```

## Stage 4 - Case Study Match
_Scanned 24 case studies on flytbase.com._

**Best match:** [EnBW Case Study: Autonomous Drones for Gigawatt Solar Portfolio | FlytBase](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks)

EnBW is one of Germany's largest energy companies, so it is the closest peer to E.ON among FlytBase's published customers. The site has no substation or line case study, but EnBW shows the same operating model E.ON is asking for: docked drones (DJI Dock 2 on FlytBase) running routine thermal inspection across dispersed remote energy assets in place of people travelling to site. It deals with the Germany-specific obstacles E.ON's Bavarian team will meet, namely unpredictable weather that makes thermal flight windows hard to schedule, grid curtailment, and terrain with line-of-sight problems. It also started as a two-dock proof of concept, which matches the pilot proposal E.ON's procurement wants by January.

- Solar portfolio grew 'from 150 MW to 1 GW in just four years'
- Increased inspection frequency 'from annual to quarterly monitoring'
- 'Eliminated six-hour round trips to remote sites'
- 'The proof-of-concept deployment with two operational docks is paving the way for autonomous operations across EnBW's entire gigawatt-scale solar portfolio'
- Stack: 'DJI Dock 2 hardware with FlytBase's automation platform and Sitemark's AI analytics'
- Before docks, 'pilots traveling two to six hours to remote sites often arrived to find conditions unsuitable for flying'

**How to use it:** Use it as the German peer proof point in the first reply: 'another large German energy company moved routine thermal inspection to docked drones and went from annual to quarterly inspections without adding headcount'. Present the two-dock PoC as the template for E.ON's January pilot proposal (for example 1-2 docks at representative Bavarian substations). Say plainly that the EnBW assets are solar PV, not substations, so the claim stays honest, and use it to open a discussion of substation-specific missions, BVLOS approval in Germany and data integration.

**Runner-up:** [Hydropower Monitoring with Autonomous Drones | FlytBase](https://flytbase.com/case-studies/axpo-hydropower-plant-monitoring-autonomous-drones) - A DACH utility (Axpo, Switzerland's largest sustainable energy producer) using DJI Dock 2 for routine inspection of remote energy infrastructure in harsh Alpine weather. The page covers health and safety, permits and aviation-safety (FLARM) integration and says Axpo plans to expand to grid infrastructure. Use it for the regulatory and operational-readiness discussion around BVLOS. TNB (S2) can be added as the only page that mentions substations, though only as a planned deployment.

**Referral connection (None):** Stage 1 found no referrer in the email (referral_source is null; the inbound came through flytbase.com/contact), so there is no referrer to connect to a case study. 

**Existing relationship with E.ON:** None of the 24 case studies in the flytbase.com sitemap mention E.ON, and 'site:flytbase.com E.ON' returned no FlytBase pages. FlytBase's public site shows no existing E.ON operation, partner or result. 

| Case study | Fit | Industry | Use case | Context |
|---|---|---|---|---|
| [EnBW Case Study: Autonomous Drones for Gigawatt Solar Portfolio | FlytBase](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks) | 82 | Strong: EnBW is 'one of Germany's largest energy companies', a direct peer of E.ON in German energy. | Partial-strong: routine thermal inspection with autonomous drone docks (DJI Dock 2 + FlytBase), but of solar PV assets, not substations or lines. | Strong: Germany (Baden-Württemberg, next to Bavaria); covers German weather, grid curtailment, remote dispersed sites, a two-dock proof of concept, and a cadence change from annual to quarterly. |
| [Hydropower Monitoring with Autonomous Drones | FlytBase](https://flytbase.com/case-studies/axpo-hydropower-plant-monitoring-autonomous-drones) | 64 | Strong: Axpo Group is Switzerland's largest sustainable energy producer (utility). | Partial: routine visual inspection of remote energy infrastructure with DJI Dock 2; the page says Axpo plans to expand to nuclear and grid infrastructure. | Good: DACH region, Alpine winter conditions, and integration into health and safety, permits and aviation safety (FLARM), which bears on E.ON's BVLOS ambition. |
| [How TNB Reduced Warehouse Inventory Verification Time by 90x with Autonomous Drones In Malaysia | FlytBase](https://flytbase.com/case-studies/tnb-warehouse-asset-monitoring-autonomous-drones-malaysia) | 58 | Strong: TNB is Malaysia's primary energy supplier, running transmission and distribution lines. | Weak-partial: warehouse asset monitoring today; the page says TNB 'is planning deployment at substations for regular inspections'. | Weak: Malaysia, one 43-hectare site, delivered through partner Aerodyne. |
| [How Sensorem Deployed 20+ Autonomous Drones Across Remote Australian Industrial Sites | FlytBase](https://flytbase.com/case-studies/sensorem-autonomous-docked-drones-deployment-australia) | 50 | Weak: an industrial-site monitoring integrator, not a utility. | Partial: asset inspection with a 20-dock network, more than 11,000 BVLOS missions and a central remote operations center. | Moderate: shows multi-site scale, 24/7 operation and BVLOS one-to-many management, which matters for ~40 dispersed substations; geography (Western Australia) does not match. |
| [How SQM Turned a 678 km² Mine into an Autonomous Inspection Zone | FlytBase | FlytBase](https://flytbase.com/case-studies/sqm-678-km2-mine-autonomous-inspection-adentu-and-flytbase) | 40 | Weak: mining. | Partial: routine daily RGB and thermal dock inspections with ranked findings, more than 95 percent mission reliability. | Weak: Chile, a single large open site; useful mainly as a pilot-to-routine story. |
| [How Aerial Fences is Automating Ranch Security and Oversight using Autonomous Drones | FlytBase | FlytBase](https://flytbase.com/case-studies/aerial-fences-automating-ranch-security-oversight-drones-flytbase) | 20 | None: agriculture / ranch security. | Weak: fence-line patrols with thermal. | None: a single US ranch under Part 107. |

## Stage 5 - Partner & Go-to-Market Motion
**Recommended motion:** AE-led with partner (co-sell)

- **Region:** Germany (Bavaria), EMEA. A German-language, EASA/LBA-regulated market where BVLOS approval in the 'specific' category and airspace integration are prerequisites. FlytBase's partner directory lists German partners (Droniq, Solectric), and Droniq specifically handles DJI Dock BVLOS operating licences and airspace integration in Germany (S21). Local partners cover German-speaking on-site deployment and support for docks at remote substations.
- **Deal Complexity:** High. E.ON SE is a large enterprise utility; ~40 high-voltage substations, procurement already engaged and wanting a pilot proposal by January, and likely stakeholders across grid operations, procurement, IT/OT security, HSE and aviation compliance. A strategic logo with enterprise procurement and a competitive evaluation this quarter calls for a FlytBase AE to own the account and commercial relationship directly, not hand it to a Bronze-tier reseller.
- **Partner Availability:** FlytBase's partner page (S18) lists two Germany-based partners, both Bronze Reseller / Solution Provider: Droniq and Solectric. Droniq has a public partnership with FlytBase to provide FlytBase software for DJI Dock operations and offers BVLOS licensing plus UTM airspace integration (S25, S21). Solectric is a DJI Enterprise dealer in Germany that presents DJI Dock 2 for energy (solar) sites (S27). No Germany-based System Integrator or BVLOS Advisory partner is listed; the nearest BVLOS Advisory partner is Drone Architect (Belgium) (S18).
- **Existing Account Relationship:** None found. Stage 4 found no FlytBase case study, partner or page mentioning E.ON (24 case studies scanned, site:flytbase.com E.ON returned nothing). No partner has delivered a FlytBase project for this account, so the partner is chosen on in-country capability, not prior delivery.

| Partner | Type | Country | Evidence | Role in deal | Verified in sources |
|---|---|---|---|---|---|
| Droniq | Reseller | Germany | 'Droniq is entering a partnership with the US-based drone autonomy software platform FlytBase... The software is particularly suitable for operating the DJI Dock... Possible application scenarios include... inspecting critical infrastructure.' Also S21: Droniq 'obtained the first operating licence for the DJI Dock drone-in-a-box system in Europe' and 'will take care of integrating the system into airspace... in addition to obtaining the operating licence to conduct flights beyond the pilot's visual line of sight.' Listed on S18 as 'Droniq Bronze Reseller Solution Provider Germany'. | Primary co-sell partner. E.ON wants BVLOS docked operations in Bavaria; Droniq (a DFS / Deutsche Telekom joint venture per public reporting) brings German BVLOS operating-licence experience, UTM airspace integration and DJI Dock supply, which are the biggest pilot risks. Role: secure the specific-category / BVLOS approval for the pilot substations, supply and commission docks, and provide German-language on-site support while the FlytBase AE owns the E.ON commercial relationship and platform scope. | yes |
| Solectric | Reseller | Germany | DJI Enterprise webinar on DJI Dock 2 for solar parks: 'Unser Händler Solectric wird über die vielfältigen Einsatzmöglichkeiten der Dock 2 berichten', with a Solectric key account manager responsible for DJI Enterprise since 2021. Listed on S18 as 'Solectric Bronze Reseller Solution Provider Germany'. | Backup / hardware supply partner. A German DJI Enterprise dealer with DJI Dock 2 experience in energy (solar) sites; can supply and service dock hardware across the ~40 substations if E.ON procurement prefers an existing hardware vendor or if Droniq capacity is limited. Does not show BVLOS licensing capability in the stored sources, so it would pair with Droniq or a BVLOS advisor for approvals. | yes |
| Drone Architect | other | Belgium | Listed on the FlytBase partner page as 'Drone Architect BVLOS Advisory Belgium'. | Optional BVLOS advisory support (EU/EASA) if the Bavarian BVLOS approval needs extra regulatory help beyond what Droniq provides. No Germany-based BVLOS Advisory partner is listed, so this is the nearest EASA-region option. | yes |

**Partner profile needed:** A Germany-based, German-speaking drone operations partner that can (1) obtain EASA specific-category / BVLOS operating approvals from the LBA for docked operations near high-voltage substations, (2) supply, install and maintain DJI Dock hardware at remote Bavarian sites, and (3) provide local first-line support. Ideally with utility or critical-infrastructure references and the ability to work under a large utility's procurement and vendor-onboarding requirements. Droniq is the closest match in FlytBase's directory.

- **flytbase_ae:** Owns the E.ON account and procurement relationship: runs discovery (economic buyer, decision criteria, tender format), scopes the January pilot proposal (for example 1-2 docks at representative substations, modelled on the EnBW two-dock PoC), leads commercial terms, security / on-prem hosting review and the pilot-to-rollout plan.
- **partner:** Droniq (primary): BVLOS / specific-category approvals, airspace (UTM) integration, dock supply, installation and German-language on-site support for the pilot substations. Solectric as hardware backup. Joins the second meeting once the pilot scope is outlined.
- **bdr:** Responds within 24h, qualifies the open MEDDPICC gaps (economic buyer, competitors, tender process, whether E.ON requires a local partner or has an existing DJI hardware vendor), books the AE discovery call, and alerts the FlytBase partner manager to loop in Droniq before the pilot proposal is drafted.

## Stage 6 - AE Handoff Summary
**Buyer:** Test Contact A, Head of Asset Inspection, Grid Operations at E.ON SE, Germany (Head/Director seniority). Came in on their own through flytbase.com/contact, with no referral. They own the operational problem: ~40 high-voltage substations in Bavaria inspected by hand every month. Budget authority is not stated. Research suggests (as an inference, not a sourced fact) that the substations sit in the Bayernwerk Netz GmbH grid area, Bayernwerk being Bavaria's largest regional DSO and an E.ON subsidiary [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111)][[S26](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988)]. The role may therefore sit in Bayernwerk's high-voltage organisation and not at E.ON SE group level.

**What he cares about:**
- Replacing monthly manual rounds of ~40 HV substations with docked drones flying routine thermal and visual missions (from the email)
- BVLOS operation, so a central team can run many sites without crews driving out (from the email)
- Getting a credible pilot proposal to procurement by January while vendors are evaluated this quarter (from the email)
- Pains E.ON's own subsidiaries have described: ageing assets, technicians who are hard to hire and keep, and drive time eating engineering hours [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]. Bayernwerk substations were largely built between the 1950s and 1970s [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)]
- Fit with what is already in place: an autonomous ground robot at a Bayernwerk substation since 2022 and the shared 'one grid, one robot platform' model on Korial [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)][[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)]

**Others likely involved:**
- Günther Mertel, Leiter der Hochspannung, Bayernwerk Netz GmbH [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111)] - Heads the high-voltage area that covers HV substations. Most likely technical approver or budget holder for the pilot (unconfirmed).
- Stephan Engelbrecht, Leiter Hochspannungsleitungen, Bayernwerk Netz GmbH [[S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988)] - Owns HV lines. Line inspection is in the lead's subject line, so he is the natural phase-2 owner.
- Peter Ketterl, Leiter Technik Ostbayern, Bayernwerk Netz GmbH [[S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988)][[S30](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ambitionierter-netzausbau-fuer-heimatenergie-3447669)] - Regional technical head who speaks publicly on grid security, stability and resilience. A likely voice for the resilience angle.
- Michael Renghart, Bayernwerk (title not in source) [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)] - Was Bayernwerk's public voice on the autonomous substation robot pilot. Could be an ally or the person who knows how substation automation was decided. Verification was partial: his name is confirmed, his title is not.
- Thomas König, E.ON board member responsible for networks (as of Feb 2021) [[S14](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/)] - Publicly backed earlier AI and drone inspection partnerships at group level. The source is from 2021, so check his current role before using it.
- Procurement (role named in the email, person unknown) - Wants the pilot proposal by January and probably runs the tender format, vendor onboarding and contracting.
- IT/OT security and aviation compliance (roles, not named) - Critical-infrastructure drone concerns are high in Germany [[S34](https://www.zfk.de/politik/deutschland/drohnen-abschuss-netzbetreiber-amprion-chef-kontra)][[S44](https://www.zfk.de/politik/drohnen-kritis-deutschland-russland-studien)], and BVLOS needs an LBA authorisation [[S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)]. Expect reviews of data hosting, airspace and drone identification.
- Droniq (FlytBase partner, Germany) [[S25](https://www.unmannedairspace.info/latest-news-and-information/droniq-teams-up-with-flytbase-on-dji-drone-operations-management/)][[S21](https://www.unmannedairspace.info/latest-news-and-information/droniq-obtains-first-european-operating-licence-for-dji-drone-in-a-box-system/)] - Recommended co-sell partner for BVLOS operating licences, UTM airspace integration, DJI Dock supply and German on-site support.

**Qualification:** MEDDPICC - ICP 74/100, completeness 50%, priority 67/100, P2 - Warm: respond within 24h, BDR-led discovery  
**Knowns:** Identify Pain (known): ~40 HV substations in Bavaria inspected by hand every month; Use case: docked drones for routine thermal and visual inspection of substations and lines, ideally BVLOS; Timeline: vendors evaluated this quarter, pilot proposal due to procurement by January; Paper Process (partial): procurement is already engaged; Champion (partial): a senior operational owner reached out on their own; Competition (partial): an active multi-vendor evaluation is under way; No referral and no existing FlytBase relationship: none of the 24 case studies mention E.ON, and no flytbase.com page mentions E.ON [[S1](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks)]  
**Unknowns:** Economic Buyer: who owns the budget and signs off the pilot and the rollout; Metrics: crew hours and cost per monthly round, and what the pilot must improve; Decision Criteria: hardware preference, data hosting / on-prem, integration with asset systems and the robot platform, pricing model; Decision Process: what happens after the January proposal, how many vendors are shortlisted, and the criteria for moving from pilot to rollout; Paper Process: formal tender or not, security, legal and vendor-onboarding reviews, contracting entity (E.ON SE or Bayernwerk), whether a local partner is required; Champion strength: will the contact sponsor the deal internally, and do they have influence with procurement and the budget owner; Competition: which vendors are named, given Percepto already holds a German docked BVLOS approval [[S32](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/)]; Whether the ~40 substations belong to Bayernwerk Netz, and whether E.ON already has a DJI hardware vendor

**Top 3 research highlights**
1. Bayernwerk has run an autonomous inspection robot (Energy Robotics software) at one of its substations since January 2022. It reads gauges, finds overheating by thermography and spots fence holes. E.ON's subsidiaries E.DIS, Bayernwerk and Avacon then moved from separate robot pilots to one shared robot platform on Korial ('one grid, one robot platform'). [[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461), [S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)] - _There is an incumbent for substation inspection, and E.ON has shown it prefers one platform across subsidiaries. Position FlytBase as the hardware-agnostic aerial layer that complements the ground robots and feeds the same data flows. Expect the objection 'we already have robots' and prepare for it._
1. BVLOS for grid inspection in Germany is in the specific category of EU 2019/947 and needs an LBA operating authorisation. Since 1 Jan 2026 applications must use SORA 2.5, and processing takes about two to four months. The LBA has already approved docked BVLOS, without on-site observers and around the clock, for a Percepto client in Germany. [[S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html), [S32](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/)] - _The approval timeline collides with a January pilot. Propose a compliant start (VLOS or remote-supervised) with the BVLOS application run in parallel through Droniq. The Percepto approval proves the regulatory path exists, and it also means a competitor with German docked BVLOS experience is probably in the evaluation._
1. Bayernwerk Netz is the largest regional DSO in Bavaria (156,000 km grid, about 7 million people supplied, wholly owned by Bayernwerk AG). It has dedicated high-voltage leaders: Günther Mertel (Leiter der Hochspannung), Stephan Engelbrecht (Leiter Hochspannungsleitungen) and Peter Ketterl (Leiter Technik Ostbayern). E.ON put EUR 7.0bn of its EUR 8.5bn 2025 investment into Energy Networks. [[S28](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111), [S26](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988), [S29](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988), [S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)] - _The contact's substations are probably Bayernwerk's, so the economic buyer and contracting entity may sit at Bayernwerk Netz, not E.ON SE. Confirm this on the first call and map the HV leadership. Grid is where E.ON spends its money, but tie the pilot to efficiency and digitalisation, which the CFO stresses [[S11](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096)]._

**Case study:** [EnBW Case Study: Autonomous Drones for Gigawatt Solar Portfolio | FlytBase](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks) - EnBW, one of Germany's largest energy companies, is E.ON's closest peer among FlytBase's published customers [[S1](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks)]. It shows the operating model E.ON wants: DJI Dock 2 with FlytBase running routine thermal inspection across dispersed remote energy sites, under German weather conditions. Inspection went from annual to quarterly, six-hour round trips to remote sites were eliminated, and the project started as a two-dock proof of concept [[S1](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks)]. That PoC is the template for the January pilot (1-2 docks at representative substations). Be upfront that EnBW's assets are solar PV, not substations: no FlytBase case study covers substation or line inspection. Use Axpo (DACH utility, permits and aviation safety) as a secondary reference for the BVLOS and regulatory discussion.

**GTM motion:** AE-led with partner (co-sell). The FlytBase AE owns the E.ON/Bayernwerk account, procurement, commercial terms, security review and pilot scope. Droniq (Germany, Bronze Reseller and FlytBase partner [[S25](https://www.unmannedairspace.info/latest-news-and-information/droniq-teams-up-with-flytbase-on-dji-drone-operations-management/)][[S18](https://flytbase.com/partner)]) handles BVLOS/specific-category approval, UTM airspace integration, DJI Dock supply and German on-site support [[S21](https://www.unmannedairspace.info/latest-news-and-information/droniq-obtains-first-european-operating-licence-for-dji-drone-in-a-box-system/)]. Solectric is the hardware backup [[S27](https://enterprise-insights.dji.com/de/automatisierte-perimeterschutz-in-solarparks-djidock2)] and Drone Architect (Belgium) is optional BVLOS advisory [[S18](https://flytbase.com/partner)]. Confirm the Bronze partners' capacity with the FlytBase partner team before naming them in the proposal.

**Next step:** BDR sends the same-day reply (Email 1) and books a 30-minute discovery call, offering Tue 10 Nov 10:00 CET or Wed 11 Nov 15:00 CET, with the call in German if preferred. The AE joins and runs the call to close the highest-risk gaps: who the economic buyer is and which entity contracts (E.ON SE or Bayernwerk Netz), the tender or vendor-onboarding format, decision criteria, competing vendors, and how the 40 substations relate to the existing robot sites. Send the one-page pilot outline (1-2 docks, thermal and visual missions, a compliant start with the SORA 2.5 BVLOS application in parallel) before the call. After the call, the AE asks the FlytBase partner manager to bring Droniq in for the second meeting. (owner: BDR (reply and booking, within 24h), then AE (discovery call, pilot scoping, partner loop-in), by: Reply today (Thu 5 Nov 2026). Discovery call by Wed 11 Nov 2026. Droniq looped in and the pilot proposal outline agreed before early December, ahead of procurement's January deadline.)  
_Why:_ This is an inbound lead in a live competitive evaluation with a fixed January deadline, so speed matters most. Pain and timeline are clear, but the economic buyer is unknown and five other MEDDPICC elements are only partial, which caps completeness at 50%. A discovery call is the fastest way to raise it. The 2-4 month LBA approval [[S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)] means the BVLOS plan, and the partner who delivers it, must be agreed before the proposal is written, not after.

**Watch-outs:** An incumbent robotics platform (Korial / Energy Robotics) is already at Bayernwerk and sister DSOs [[S7](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk)][[S36](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461)]. Position FlytBase as a complement and plan for integration, not replacement.; Competitor Percepto already holds a German docked BVLOS approval [[S32](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/)], and E.ON has 270+ trained drone pilots plus eSmart Systems AI analytics [[S13](https://news.eonenergy.com/news/how-drones-are-helping-secure-power-grids)][[S14](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/)]. FlytBase must show value beyond in-house manual drone teams.; E.ON's 'Polaris' efficiency programme. E.ON confirmed a simpler steering model; Manager Magazin reported a 20-25% cost-cut target from spring 2027, which E.ON did not comment on [[S19](https://www.zfk.de/unternehmen/nachrichten/eon-prueft-mit-polaris-den-umbau-seiner-organisation)]. Stakeholders may change and procurement may centralise, so build the pilot case on measured hours and cost.; BVLOS approval takes 2-4 months under SORA 2.5 [[S31](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html)] and will not be ready for a pilot right after January. Do not promise BVLOS from day one.; Drone security worries at German critical infrastructure are high [[S34](https://www.zfk.de/politik/deutschland/drohnen-abschuss-netzbetreiber-amprion-chef-kontra)][[S44](https://www.zfk.de/politik/drohnen-kritis-deutschland-russland-studien)]. Expect security and IT/OT reviews of data hosting, airspace and identification of the operator's own drones.; Both German partners are Bronze tier, and no German system integrator is listed. Check capacity and integration ownership, and agree deal registration if both Droniq and Solectric are involved.; Do not cite the Bayernwerk EUR 12bn 2026-2030 programme, the Bayernwerk resilience project or the current Bayernwerk board names. Those claims were removed by the fact-check because their source (S33) was unreadable.; The EnBW reference is solar PV, not substations [[S1](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks)]. Say so plainly to keep the claim honest.


## Sources
- **S1** [EnBW Case Study: Autonomous Drones for Gigawatt Solar Portfolio | FlytBase](https://flytbase.com/case-studies/enbw-scaled-solar-pv-inspections-150-mw-to-1-gw-autonomous-drone-docks) _(case_study)_
- **S2** [How TNB Reduced Warehouse Inventory Verification Time by 90x with Autonomous Drones In Malaysia | FlytBase](https://flytbase.com/case-studies/tnb-warehouse-asset-monitoring-autonomous-drones-malaysia) _(case_study)_
- **S3** [Hydropower Monitoring with Autonomous Drones | FlytBase](https://flytbase.com/case-studies/axpo-hydropower-plant-monitoring-autonomous-drones) _(case_study)_
- **S4** [How SQM Turned a 678 km² Mine into an Autonomous Inspection Zone | FlytBase | FlytBase](https://flytbase.com/case-studies/sqm-678-km2-mine-autonomous-inspection-adentu-and-flytbase) _(case_study)_
- **S5** [How Sensorem Deployed 20+ Autonomous Drones Across Remote Australian Industrial Sites | FlytBase](https://flytbase.com/case-studies/sensorem-autonomous-docked-drones-deployment-australia) _(case_study)_
- **S6** [How Aerial Fences is Automating Ranch Security and Oversight using Autonomous Drones | FlytBase | FlytBase](https://flytbase.com/case-studies/aerial-fences-automating-ranch-security-oversight-drones-flytbase) _(case_study)_
- **S7** [A Shared Robot Platform for E.ON | Korial](https://www.energy-robotics.com/post/automated-inspection-of-substations-at-bayernwerk) _(technology_adoption)_
- **S8** [KI & Multisensorik sichern Stromnetz aus der Luft](https://www.siemens-energy.com/de/de/home/press-releases/multisensorsystem-und-kuenstliche-intelligenz-stellen-stromversorgung-aus-der-vogelperspektive-sicher.html) _(technology_adoption)_
- **S9** [EQS-News: E.ON continues growth path in 2025 and delivers on energy transition | Company Announcement | Investegate](https://www.investegate.co.uk/announcement/eqs/e-on-ag--0mpp/eqs-news-e-on-continues-growth-path-in-2025-/9445200) _(budget_signals)_
- **S10** [EQS-News: E.ON concludes fiscal year with strong earnings and record investments in the energy transition | Company Announcement | Investegate](https://www.investegate.co.uk/announcement/eqs/e-on-ag--0mpp/eqs-news-e-on-concludes-fiscal-year-with-str-/8752407) _(budget_signals)_
- **S11** [boersengefluester.de · The Ultimate Swiss Knife · © boersengefluester.de · 2026](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-continues-growth-path-in-2025-and-delivers-on-energy-transition-2281096) _(budget_signals)_
- **S12** [boersengefluester.de · The Ultimate Swiss Knife · © boersengefluester.de · 2026](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-concludes-fiscal-year-with-strong-earnings-and-record-investments-in-the-energy-transition-2091497) _(budget_signals)_
- **S13** [Innovation in flight: how drones are helping to secure power grids | E.ON News](https://news.eonenergy.com/news/how-drones-are-helping-secure-power-grids) _(technology_adoption)_
- **S14** [E ON : partners up with eSmart Systems to digitalize the inspection of overhead lines | MarketScreener](https://www.marketscreener.com/quote/stock/E-ON-SE-3818998/news/E-ON-partners-up-with-eSmart-Systems-to-digitalize-the-inspection-of-overhead-lines-32393529/) _(technology_adoption)_
- **S15** [Collaboration between CTU FEE, E.ON, and EG.D is bringing power grid inspection into the era of autonomous drones ← Department of Cybernetics](https://cyber.felk.cvut.cz/news/collaboration-between-ctu-fee-e-on-and-eg-d-is-bringing-power-grid-inspection-into-the-era-of-autonomous-drones) _(technology_adoption)_
- **S16** [Flynex Performs BVLOS Flights to Inspect Power Lines for MITNETZ STROM | Commercial UAV News](https://commercialuavnews.com/energy/flynex-performs-bvlos-flights-to-inspect-power-lines) _(technology_adoption)_
- **S17** [boersengefluester.de · The Ultimate Swiss Knife · © boersengefluester.de · 2026](https://app.boersengefluester.de/en/newswire/DE000ENAG999/eon-se/eon-off-to-a-good-start-to-the-year-in-a-challenging-environment-2326600) _(budget_signals)_
- **S18** [Partner network | FlytBase](https://flytbase.com/partner) _(partner_directory)_
- **S19** [Eon prüft mit "Polaris" den Umbau seiner Organisation](https://www.zfk.de/unternehmen/nachrichten/eon-prueft-mit-polaris-den-umbau-seiner-organisation) _(recent_news)_
- **S20** [A Shared Robot Platform for E.ON | Korial](https://www.korial.com/customer-stories/e-on) _(technology_adoption)_
- **S21** [Droniq obtains first European operating licence for DJI drone-in-a-box system - Unmanned airspace](https://www.unmannedairspace.info/latest-news-and-information/droniq-obtains-first-european-operating-licence-for-dji-drone-in-a-box-system/) _(web)_
- **S22** [https://mnd-assets.mynewsdesk.com/raw/upload/fl_attachment/0x1b0tkliqezyycxwpoxom](https://mnd-assets.mynewsdesk.com/raw/upload/fl_attachment/0x1b0tkliqezyycxwpoxom) _(technology_adoption)_
- **S23** [Bot Verification](https://ceenergynews.com/whos-in-charge/attila-kiss-takes-over-as-senior-vice-president-energy-networks-europe-at-e-on-se-in-january/) _(org_structure)_
- **S24** [Digitalisierung im Stromnetz: Drohne ersetzt Helikopter | Bayernwerk AG](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/digitalisierung-im-stromnetz-drohne-ersetzt-helikopter-3049586) _(technology_adoption)_
- **S25** [Droniq teams up with Flytbase on DJI drone operations management - Unmanned airspace](https://www.unmannedairspace.info/latest-news-and-information/droniq-teams-up-with-flytbase-on-dji-drone-operations-management/) _(web)_
- **S26** [Bayernwerk kontrolliert Hochspannungsleitungen aus dem Hubschrauber | Bayernwerk AG](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-kontrolliert-hochspannungsleitungen-aus-dem-hubschrauber-3317988) _(operations_context)_
- **S27** [Automatisierter Perimeterschutz für Solarparks mit DJI DOCK2: Gegen Diebstahl und Vandalismus](https://enterprise-insights.dji.com/de/automatisierte-perimeterschutz-in-solarparks-djidock2) _(web)_
- **S28** [Bayernwerk betont Notwendigkeit für neues Umspannwerk im Raum Rottenburg an der Laaber | Bayernwerk AG](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/bayernwerk-betont-notwendigkeit-fuer-neues-umspannwerk-im-raum-rottenburg-an-der-laaber-3419111) _(operations_context)_
- **S29** [Rekordbudgets für das Stromnetz der Zukunft | Bayernwerk AG](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/rekordbudgets-fuer-das-stromnetz-der-zukunft-3412988) _(budget_signals)_
- **S30** [Ambitionierter Netzausbau für Heimatenergie | Bayernwerk AG](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ambitionierter-netzausbau-fuer-heimatenergie-3447669) _(budget_signals)_
- **S31** [KI-Drohneninspektion von Stromnetzen mit BVLOS | innobu](https://www.innobu.com/de/artikel/ki-drohneninspektion-stromnetze-2026.html) _(operations_context)_
- **S32** [Percepto achieves BVLOS approval for drone operations in Germany - Unmanned airspace](https://www.unmannedairspace.info/uncategorized/percepto-achieves-bvlos-approval-for-drone-operations-in-germany/) _(operations_context)_
- **S33** [https://mnd-assets.mynewsdesk.com/raw/upload/fl_attachment/o6e69p4msd5o45qt8bn6pw](https://mnd-assets.mynewsdesk.com/raw/upload/fl_attachment/o6e69p4msd5o45qt8bn6pw) _(investor_priorities)_
- **S34** [Drohnen-Abschuss durch Netzbetreiber: Amprion-Chef gibt Kontra](https://www.zfk.de/politik/deutschland/drohnen-abschuss-netzbetreiber-amprion-chef-kontra) _(recent_news)_
- **S35** [EQS-News: E.ON Annual General Meeting again approves higher dividend | Company Announcement | Investegate](https://www.investegate.co.uk/announcement/eqs/e-on-ag--0mpp/eqs-news-e-on-annual-general-meeting-again-a-/9535639) _(investor_priorities)_
- **S36** [KI-Schnüffelnase inspiziert das Umspannwerk | Bayernwerk AG](https://www.mynewsdesk.com/de/bayernwerk/pressreleases/ki-schnueffelnase-inspiziert-das-umspannwerk-3284461) _(technology_adoption)_
- **S37** [Reddit r/drones: Need advice: new battery not charging; tips or tricks?](https://www.reddit.com/r/drones/comments/1xdrcwz/need_advice_new_battery_not_charging_tips_or/) _(reddit)_
- **S38** [Reddit r/drones: Future potential drone use cases and emergence of docks](https://www.reddit.com/r/drones/comments/1x3yjfv/future_potential_drone_use_cases_and_emergence_of/) _(reddit)_
- **S39** [Reddit r/drones: FQ777 FQ21 (FQ21HDV) GPS drone: LED blinking blue and green, props won't spin. Anyone have the manual?](https://www.reddit.com/r/drones/comments/1x1yjk2/fq777_fq21_fq21hdv_gps_drone_led_blinking_blue/) _(reddit)_
- **S40** [Reddit r/drones: I solved the 5 global UAV deadlocks (LiDAR failure, Eagle attacks, Battery drain) using Eco-Naturalistic Mimicry. Thoughts?](https://www.reddit.com/r/drones/comments/1x1fw8s/i_solved_the_5_global_uav_deadlocks_lidar_failure/) _(reddit)_
- **S41** [Reddit r/drones: AI was supposed to change everything. Why does the drone industry still feel the same?](https://www.reddit.com/r/drones/comments/1wrbgyl/ai_was_supposed_to_change_everything_why_does_the/) _(reddit)_
- **S42** [Reddit r/drones: Mavic 4 Pro suddenly nose-dived into a lake—has anyone experienced this or successfully filed a DJI/Best Buy claim?](https://www.reddit.com/r/drones/comments/1vtyfom/mavic_4_pro_suddenly_nosedived_into_a_lakehas/) _(reddit)_
- **S43** [Edis testet Inspektionsroboter in Umspannwerk.](https://www.zfk.de/digitalisierung/smart-city-energy/edis-testet-hochsensible-inspektionsroboter) _(technology_adoption)_
- **S44** [Drohnen über Kritis-Anlagen: Studie zeigt Verwundbarkeit Europas](https://www.zfk.de/politik/drohnen-kritis-deutschland-russland-studien) _(recent_news)_