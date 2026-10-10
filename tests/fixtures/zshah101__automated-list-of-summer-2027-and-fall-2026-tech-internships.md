<div align="center">

# 🎓 Summer 2027 Tech Internships

**A self-updating engine that tracks tech internships so you don't have to.**

[![CI](https://img.shields.io/github/actions/workflow/status/zshah101/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/ci.yml?branch=main&label=tests&style=flat-square&color=3fb950)](https://github.com/zshah101/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/actions/workflows/ci.yml)&nbsp;[![Open roles](https://img.shields.io/badge/dynamic/json?label=open%20roles&query=open_total&url=https%3A%2F%2Fzshah101.github.io%2FAutomated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships%2Fapi%2Fstats.json&color=2f81f7&style=flat-square)](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/)&nbsp;![Updates](https://img.shields.io/badge/updates-every%2030%20min-3fb950?style=flat-square)&nbsp;[![RSS](https://img.shields.io/badge/RSS-subscribe-e67e22?style=flat-square)](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/feed.xml)

### 1181 open roles (647 listed below) · 145 new this week

4,739 employers tracked · data as of Oct 10, 2026 at 18:07 UTC

_797 have a cycle the employer stated · 384 are recent postings whose cycle isn't stated (listed separately, never mixed in)._

**[🖥️ Live dashboard](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/)** · **[📡 RSS](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/feed.xml)** · **[⚙️ JSON API](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/api/jobs.json)** · **[✉️ Email alerts](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/#subscribe)**

</div>

> [!TIP]
> **⭐ Star this repo** to save it and get updates when new roles are added.

Instead of refreshing a dozen career pages by hand, it reads company hiring feeds directly and keeps one live list — newest roles on top, refreshed automatically throughout the day.

**🔔 New roles in your inbox:** [subscribe by email](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/#subscribe) - one email a day, only when new internships actually appeared, unsubscribe from any email in two clicks. (Prefer RSS-to-email? [Feedrabbit works too](https://feedrabbit.com/subscriptions/new?url=https%3A%2F%2Fraw.githubusercontent.com%2Fzshah101%2FAutomated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships%2Fmain%2Fdocs%2Ffeed.xml).)

---

## What this is

This is an engine, not a hand-kept list. It polls company career feeds every 30 minutes, finds the internships, removes duplicates, and rebuilds this page on its own.

Every link comes straight from the source — so it's real and current, not a stale list someone forgot to update. Speed matters.

## What makes this different

| | |
|---|---|
| 📅 **[Drop Radar](#drop-radar)** | A forecast of **what's coming**. Each marquee company's typical opening window, replaced by the real drop date the moment the engine catches it live. Windows are estimates and labelled as such; only dates the engine saw itself are marked verified. |
| 🛂 **Visa intel, computed** | 🇺🇸 / 🛂 flags detected automatically from every job description, plus ✓ for employers with a real H-1B track record (USCIS data, FY2022-23 — a history, not a promise). The big lists crowdsource this by hand; here it's code. Most postings say nothing either way, and those show as unknown rather than guessed. |
| 📆 **A real date on nearly every role** | Taken from the job portal itself wherever the portal states one, so newest-first actually means newest. The exact coverage figure is printed at the bottom of this page every run. |
| 🧰 **Skill tags + pay, extracted** | Every posting's text is scanned for the stack it wants (Python, C++, PyTorch, …) and the pay it states — searchable on the [dashboard](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/), and included in the CSV and API. |
| 🔔 **Alerts your way** | [Email digests](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/#subscribe) or [RSS](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/feed.xml) — point any reader, or a Slack/Discord RSS integration, at it. Plus a [live dashboard](https://zshah101.github.io/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/) with search, filters, and a saved-roles list that never leaves your browser. |
| ⚙️ **An engine, not a spreadsheet** | 5,021 job-board endpoints (4,739 distinct employers; some run more than one board) polled every 30 minutes across 12 ATS platforms. Full source and tests in this repo. |

## Scope

| | |
|---|---|
| **Roles** | Software Engineering, Data Science & Machine Learning (and closely related technical internships) |
| **Region** | United States |
| **Cycles** | Summer 2027 and Fall 2026 |

## About

I'm an international student studying in the United States, so I built this for the search I'm doing myself. The list is US roles only for now — that's where I'm searching.

Use it to spot roles early and apply before they fill up. Being first genuinely helps.

## Where this is going

I'm building this in the open and adding to it as it grows.

**Recently shipped:** email alerts · the Drop Radar · auto-detected sponsorship flags · the live dashboard

**Next up:** personalized alerts (pick your categories) · per-company hiring pages · a ghost-posting detector

If it helps you, a star means a lot and tells me to keep going.

## How to use

<details>
<summary><b>Reading the table — flags, dates, and the cycle split</b> (click to expand)</summary>

- Roles are grouped by cycle below - **newest posting on top, oldest at the bottom.**
- A cycle section holds only roles whose **employer stated that cycle** - in the title, or in the posting's own text. Postings that name no cycle anywhere are in *Recently posted — cycle not stated* further down, with **no cycle guessed for them**. Same quality bar, different amount of evidence.
- **Apply** is the third column, right after the role, so the link is on screen even when the table is wider than your window.
- The **Posted** column is the date the company published the role.
- **_(3 openings)_ after a role title** = the employer has that many separate live requisitions for the same job, in the same place, for the same cycle. They're all real and each takes its own application, so they're linked individually (**Apply**, then **#2**, **#3**) instead of repeating the row. Counts still count requisitions, and the CSV export is never grouped.
- **🆁 after a company name** = **this role is remote** — the posting's own location or title says so. It marks the role on that row, not the whole company.
- **Flags after a role title:** 🇺🇸 = requires U.S. citizenship or a security clearance · 🛂 = the posting says it won't sponsor a work visa · 🆕 = spotted in the last 48 hours. Sponsorship flags are detected automatically from each job description - treat them as a strong hint and confirm on the posting.
- **✓ after a company name** = a real H-1B track record: USCIS approved 10+ petitions for that employer in FY2022–2023 (matched automatically against the official [H-1B Employer Data Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub)). No ✓ doesn't mean they won't sponsor - it means we can't prove they have.
- Track your applications with [`data/internships.csv`](data/internships.csv) (opens in Excel / Google Sheets).
- Missing a company? Adding one takes a single line, see [CONTRIBUTING.md](CONTRIBUTING.md).

</details>

---

## Summer 2027  (300 employer-stated)

| Company | Role | Apply | Location | Skills | Posted |
|---|---|---|---|---|---|
| Workday ✓ | Cybersecur​ity Engineer Intern 🛂 🆕 | [Apply](https://workday.wd5.myworkdayjobs.com/Workday_Early_Career/job/USA-CA-Pleasanton/Cybersecurity-Engineer-Intern_JR-0110809) | USA, CA, Pleasanton | Python, Java, TypeScript, JavaScript | Oct 09, 2026 |
| Workday ✓ | Software Development Engineer Intern 🛂 🆕 | [Apply](https://workday.wd5.myworkdayjobs.com/Workday_Early_Career/job/USA-CA-Pleasanton/Software-Development-Engineer-Intern_JR-0110810) | USA, CA, Pleasanton | Python, Java, C++, JavaScript | Oct 09, 2026 |
| Workday ✓ | Machine Learning Engineer Intern 🛂 🆕 | [Apply](https://workday.wd5.myworkdayjobs.com/Workday_Early_Career/job/USA-CA-Pleasanton/Machine-Learning-Engineer-Intern_JR-0110812) | USA, CA, Pleasanton | Python, Pandas, LLMs, AWS | Oct 09, 2026 |
| Itron ✓ | Intern - HR AI Data Science (Summer 2027) 🆕 | [Apply](https://itron.wd5.myworkdayjobs.com/Itron/job/United-States-of-America-Texas-Austin/Intern---HR-AI-Data-Science--Summer-2027-_JR103034-1) | United States of America, Texas, Austin | Python, Tableau | Oct 09, 2026 |
| Alcon | Clinical Data Science Intern 🛂 🆕 | [Apply](https://alcon.wd5.myworkdayjobs.com/careers_alcon/job/Fort-Worth-Texas/Clinical-Data-Science-Intern_R-2026-50204) | Fort Worth, Texas | Python | Oct 09, 2026 |
| American Family Insurance Group | Summer 2027 Intern - Data Analyst 🆕 | [Apply](https://amfam.wd1.myworkdayjobs.com/AmFamGroupInternCareers/job/WI-Madison/Summer-2027-Intern---Data-Analyst_R39404) | WI Madison | SQL | Oct 09, 2026 |
| General Motors ✓ | 2027 Summer Intern,  Data Scaling, Embodied AI 🆕 | [Apply](https://generalmotors.wd5.myworkdayjobs.com/Careers_GM/job/Sunnyvale-California-United-States-of-America/XMLNAME-2027-Summer-Intern---Data-Scaling--Embodied-AI_JR-202622132) | Sunnyvale +2 more | Python, C++, SQL, PyTorch | Oct 09, 2026 |
| General Motors ✓ | 2027 Summer Intern, AI Research, Embodied AI 🆕 | [Apply](https://generalmotors.wd5.myworkdayjobs.com/Careers_GM/job/Sunnyvale-California-United-States-of-America/XMLNAME-2027-Summer-Intern--AI-Research--Embodied-AI_JR-202622146) | Sunnyvale +2 more | Python, C++, PyTorch, TensorFlow | Oct 09, 2026 |
| General Motors ✓ | 2027 Summer Intern, Onboard Autonomy, Embodied AI 🆕 | [Apply](https://generalmotors.wd5.myworkdayjobs.com/Careers_GM/job/Sunnyvale-California-United-States-of-America/XMLNAME-2027-Summer-Intern--Onboard-Autonomy--Embodied-AI_JR-202622135) | Sunnyvale +2 more | Python, C++, PyTorch, TensorFlow | Oct 09, 2026 |
| GCM Grosvenor | 2027 Software Engineering Summer Intern 🆕 | [Apply](https://job-boards.greenhouse.io/gcmgrosvenor/jobs/8015792003) | Chicago, Illinois, United States | Python, Java, C++, C# | Oct 09, 2026 |
| Schonfeld | 2027 Quantitative Developer Intern 🆕 | [Apply](https://job-boards.greenhouse.io/schonfeld/jobs/8267092) | Austin, Texas, United States | Python, Java, C++, SQL | Oct 09, 2026 |
| Schonfeld | 2027 Quantitative Research Intern 🆕 | [Apply](https://job-boards.greenhouse.io/schonfeld/jobs/8267120) | Austin, Texas, United States | Python, Java, C++, SQL | Oct 09, 2026 |
| DoorDash ✓ | Software Engineer, Intern - Labs (Summer 2027) | [Apply](https://job-boards.greenhouse.io/doordashusa/jobs/8263774) | San Francisco, CA; Sunnyvale, CA | Python, Java, SQL, Kotlin | Oct 08, 2026 |
| IMC Trading ✓ | Machine Learning Engineer Intern - Summer 2027 🆕 | [Apply](https://job-boards.eu.greenhouse.io/imc/jobs/4962456101) | New York, United States | Python, C++ | Oct 08, 2026 |
| Viget | Software Developer Intern (2027) 🛂 🆕 | [Apply](https://jobs.lever.co/viget/b18cc87d-fca2-485a-a0f2-ad6197db63f2) | Boulder, CO | Python, JavaScript, Ruby, React | Oct 08, 2026 |
| Jones Lang LaSalle (JLL) | AI Intern Summer 2027 Internship - Los Angeles, CA 🛂 🆕 | [Apply](https://jll.wd1.myworkdayjobs.com/jllcareers/job/Los-Angeles-CA/AI-Intern-Summer-2027-Internship---Los-Angeles--CA_REQ539393) | Los Angeles, CA | Python, SQL, Pandas, LLMs | Oct 08, 2026 |
| Modernizing Medicine | Software Engineering Intern 🆕 | [Apply](https://modmed.wd501.myworkdayjobs.com/ModMed12/job/Boca-Raton-FL/Software-Engineering-Intern_R5148) | Boca Raton, FL | Python, Java, C#, Go | Oct 08, 2026 |
| Moog | Intern, Computer Science 🆕 | [Apply](https://moog.wd5.myworkdayjobs.com/moog_external_career_site/job/Torrance-CA/Intern--Computer-Science_R-26-19819) | Torrance, CA | No skills listed | Oct 08, 2026 |
| Northrop Grumman | 2027 Software Engineer Intern – McClellan CA 🇺🇸 🆕 | [Apply](https://ngc.wd1.myworkdayjobs.com/Northrop_Grumman_External_Site/job/United-States-California-McClellan/XMLNAME-2027-Software-Engineer-Intern---McClellan-CA_R10255207) | United States-California-McClellan | Python, C++ | Oct 08, 2026 |
| Rugged Robotics | Robotic Software Intern/Co-op (Spring or Summer 2027) | [Apply](https://job-boards.greenhouse.io/ruggedrobotics/jobs/4730908005) | Houston, TX | Python, C++ | Oct 08, 2026 |
| Stantec | Civil/Transporta​tion Engineering Intern - Infrastruc​ture (Summer 2027) | [Apply](https://hdhl.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/1008210) | Charleston +5 more | No skills listed | Oct 08, 2026 |
| Amazon ✓ | Software Development Engineer (Embedded Systems) Intern, Amazon Leo - Summer 2027 (USA) 🇺🇸 | [Apply](https://www.amazon.jobs/en/jobs/10571374/software-development-engineer-embedded-systems-intern-amazon-leo-summer-2027-usa) | Redmond, Washington, USA | Python, Java, C++, C# | Oct 07, 2026 |
| Apple Bank | 2027 Summer Intern- Information Security 🛂 🆕 | [Apply](https://applebank.wd5.myworkdayjobs.com/applebankcareers/job/New-York-NY/XMLNAME-2027-Summer-Intern--Information-Security_2026-1416) | New York, NY | No skills listed | Oct 07, 2026 |
| Motorola | Software Engineer - Summer 2027 Internship | [Apply](https://motorolasolutions.wd5.myworkdayjobs.com/Careers/job/Westminster-CO/Software-Engineer---Summer-2027-Internship_R68997) | Westminster, CO | C#, SQL, Angular | Oct 07, 2026 |
| Nissan | Digital Products & AI Strategy Intern - Summer 2027 - Franklin, TN 🛂 | [Apply](https://alliance.wd3.myworkdayjobs.com/nissanjobs/job/Franklin-Tennessee---United-States-of-America/Digital-Products---AI-Strategy-Intern---Summer-2027---Franklin--TN_R00214215) | Franklin +1 more | No skills listed | Oct 07, 2026 |
| Motorola | GenAI & Machine Learning - 2027 Summer Internship (Chicago Hybrid) 🛂 | [Apply](https://motorolasolutions.wd5.myworkdayjobs.com/Careers/job/Chicago-IL/GenAI---Machine-Learning---2027-Summer-Internship--Chicago-Hybrid-_R68929) | Chicago, IL | LLMs, Python, scikit-learn, Pandas | Oct 07, 2026 |
| RTX | Software Engineering Co-op (Spring/Summer 2027) | [Apply](https://globalhr.wd5.myworkdayjobs.com/rec_rtx_ext_gateway/job/US-IA-CEDAR-RAPIDS-130--5350-C-Ave-NE--BLDG-130/Software-Engineering-Co-op--Spring-Summer-2027-_01879726) | US-IA-CEDAR RAPIDS-130 ~ 5350 C Ave NE… | C++, Linux | Oct 07, 2026 |
| RTX | Software Engineering Co-op (Summer/Fall 2027) | [Apply](https://globalhr.wd5.myworkdayjobs.com/rec_rtx_ext_gateway/job/US-IA-CEDAR-RAPIDS-130--5350-C-Ave-NE--BLDG-130/Software-Engineering-Co-op--Summer-Fall-2027-_01879738) | US-IA-CEDAR RAPIDS-130 ~ 5350 C Ave NE… | C++, Linux | Oct 07, 2026 |
| Mastercard | Security Infrastruc​ture Engineering & Architecture Intern, Summer 2027 – Arlington, VA, US | [Apply](https://mastercard.wd1.myworkdayjobs.com/Campus/job/Arlington-Virginia/Security-Infrastructure-Engineering---Architecture-Intern--Summer-2027---Arlington--VA--US_R-284924) | Arlington, Virginia | Python, Java | Oct 07, 2026 |
| Amazon ✓ | Software Development Engineer Intern - Mobile(iOS/Android) - Summer 2027 (USA) | [Apply](https://www.amazon.jobs/en/jobs/10571004/software-development-engineer-intern-mobile-ios-android-summer-2027-usa) | Seattle, Washington, USA | Python, Java, C++, C# | Oct 06, 2026 |
| Sigma Computing ✓ | Software Engineering Intern (Summer 2027) 🛂 | [Apply](https://job-boards.greenhouse.io/sigmacomputing/jobs/8001295003) | New York, NY | Python, Java, JavaScript, SQL | Oct 06, 2026 |
| Highmark Health ✓ | Summer 2027 Artificial Intelligence (Operations) Undergradu​ate Intern 🛂 | [Apply](https://highmarkhealth.wd1.myworkdayjobs.com/highmark/job/Pittsburgh-PA-15222-FAP-5th-Avenue-Place/Summer-2027-Artificial-Intelligence--Operations--Undergraduate-Intern_J287476) | Pittsburgh PA +3 more | No skills listed | Oct 06, 2026 |
| Rivet Industries | Intern, Software Engineering (Summer 2027) | [Apply](https://jobs.ashbyhq.com/rivet/03fcb078-7371-4cfd-89a9-368e5b60d914) | San Jose, CA | C++, C#, Computer Vision | Oct 06, 2026 |
| Waymo ✓ | 2027 Summer Intern, BS, Waymo ML Ops & Automation | [Apply](https://careers.withwaymo.com/jobs?gh_jid=8257237) | Mountain View, CA, USA | C++, SQL | Oct 06, 2026 |
| Waymo ✓ | 2027 Summer Intern, BS, Software Engineer, Model Eval | [Apply](https://careers.withwaymo.com/jobs?gh_jid=8257660) | Mountain View, CA, USA | Python, C++, LLMs | Oct 06, 2026 |
| ABB ✓ | AI Engineering, Business Systems Intern- Summer 2027 🛂 | [Apply](https://abb.wd3.myworkdayjobs.com/external_career_page/job/USA-NC-Cary/AI-Engineering--Business-Systems-Intern--Summer-2027_JR00048714) | USA, NC, Cary | Python, SQL, LLMs, Git | Oct 06, 2026 |
| ABB ✓ | AI Engineering, ERP Intern- Summer 2027 🛂 | [Apply](https://abb.wd3.myworkdayjobs.com/external_career_page/job/USA-NC-Cary/AI-Engineering--ERP-Intern--Summer-2027_JR00048711) | USA, NC, Cary | Python, SQL, LLMs, Git | Oct 06, 2026 |
| Dmainc | Cybersecur​ity Intern - Summer 2027 | [Apply](https://dmainc.wd5.myworkdayjobs.com/dma/job/Fort-Wayne-IN/Cybersecurity-Intern---Summer-2027_REQ742) | Fort Wayne, IN | No skills listed | Oct 06, 2026 |
| Jabil ✓ | AI Transforma​tion Intern | [Apply](https://jabil.wd5.myworkdayjobs.com/Jabil_Careers/job/Austin-TX/AI-Transformation-Intern_J2466044) | Austin, TX | LLMs | Oct 06, 2026 |
| Leidos ✓ | Data Science Intern 🇺🇸 | [Apply](https://leidos.wd5.myworkdayjobs.com/External/job/Arlington-VA/Data-Science-Intern_R-00193937) | Arlington, VA | Python, Java, C++, PyTorch | Oct 06, 2026 |
| Leidos ✓ | Software Engineer Intern 🇺🇸 | [Apply](https://leidos.wd5.myworkdayjobs.com/External/job/Arlington-VA/Software-Engineer-Intern_R-00193933) | Arlington, VA | Python, Java, C++, Rust | Oct 06, 2026 |
| Niantic Spatial | Software Engineering Intern (Summer 2027) | [Apply](https://jobs.ashbyhq.com/niantic-spatial/898b2da7-03cd-486e-96e3-3430a148c8fd) | San Francisco, CA | Python, C++, TypeScript, SQL | Oct 06, 2026 |
| Courier Health | Software Engineering Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/courierhealth/jobs/5258913007) | New York, New York, United States | TypeScript, React, GraphQL, AWS | Oct 06, 2026 |
| MEMX | Information Security Intern, Summer 2027 (Hybrid, NYC) | [Apply](https://job-boards.greenhouse.io/memx/jobs/5445236008) | United States | AWS, Azure | Oct 06, 2026 |
| Pure Storage ✓ | Software Engineer Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/purestorage/jobs/8249749) | Santa Clara, California | C++ | Oct 06, 2026 |
| CACI | Cyber Analyst Intern - Summer 2027 | [Apply](https://caci.wd1.myworkdayjobs.com/external/job/Ashburn-VA-US/Cyber-Analyst-Intern---Summer-2027_333161) | Ashburn, VA, US | Linux | Oct 06, 2026 |
| Marvell | Machine Learning Engineer Intern, BS/MS - Summer 2027 | [Apply](https://marvell.wd1.myworkdayjobs.com/MarvellCareers/job/Santa-Clara-CA/Machine-Learning-Engineer-Intern--BS-MS---Summer-2027_2604989-1) | Santa Clara, CA | Python, CUDA, AWS, GCP | Oct 06, 2026 |
| Hudson River Trading ✓ | Data Scientist Intern - 2027 | [Apply](https://www.hudsonrivertrading.com/careers/job/?gh_jid=8257369) | London +4 more | Python, Pandas | Oct 05, 2026 |
| Midland States Bank | Intern - IT Infrastruc​ture | [Apply](https://midlandsb.wd1.myworkdayjobs.com/msbcareers/job/Effingham-IL/Intern---IT-Infrastructure_JR1471) | Effingham, IL | Python | Oct 05, 2026 |
| Stantec | Civil Engineering Internship - Infrastruc​ture (Summer 2027) | [Apply](https://hdhl.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/1008180) | Okemos, MI, United States | No skills listed | Oct 05, 2026 |
| Jain Global | Data Engineer Intern | [Apply](https://jainglobal.wd5.myworkdayjobs.com/ExternalSite/job/New-York-New-York/Data-Engineer-Intern_JR100605-1) | New York, New York | Python, SQL, React | Oct 05, 2026 |
| LexisNexis Risk Solutions ✓ | Data Science Intern | [Apply](https://relx.wd3.myworkdayjobs.com/RiskSolutions/job/Alpharetta-GA-Alderman/Data-Science-Intern_R118955) | Alpharetta, GA (Alderman) | Python, SQL, LLMs, Computer Vision | Oct 05, 2026 |
| CACI | Software Development Intern - Summer 2027 🇺🇸 | [Apply](https://caci.wd1.myworkdayjobs.com/external/job/Oklahoma-City-OK-US/Software-Development-Intern---Summer-2027_333085) | Oklahoma City, OK, US | Java, C++, C#, JavaScript | Oct 05, 2026 |
| Jain Global | Quant Research Intern, Systematic Trading | [Apply](https://jainglobal.wd5.myworkdayjobs.com/ExternalSite/job/New-York-New-York/Quant-Research-Intern--Systematic-Trading_JR100603-1) | New York, New York | Python | Oct 05, 2026 |
| Primient | AI Analyst Intern - Summer 2027 | [Apply](https://primient.wd1.myworkdayjobs.com/External_Careers/job/Schaumburg-IL/AI-Analyst-Intern---Summer-2027_JREQ7056) | Schaumburg, IL | Python, SQL | Oct 04, 2026 |
| Amazon ✓ | Software Development Engineer Intern (Embedded Systems) - Summer 2027 (USA) | [Apply](https://www.amazon.jobs/en/jobs/10567914/software-development-engineer-intern-embedded-systems-summer-2027-usa) | Seattle, Washington, USA | Python, Java, C++, C# | Oct 02, 2026 |
| Affirm ✓ | Software Engineer (Machine Learning) Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/affirm/jobs/8008645003) | San Francisco, California, United States | Python, Java, C++, JavaScript | Oct 02, 2026 |
| Affirm ✓ | Software Engineer Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/affirm/jobs/8011590003) | San Francisco, California, United States | Python, Java, C++, JavaScript | Oct 02, 2026 |
| Harvey | Software Engineering Intern (Summer 2027) | [Apply](https://jobs.ashbyhq.com/harvey/06d64648-b84b-48ae-94a2-d9c06dfdcb5d) | New York | Python, Java, TypeScript, JavaScript | Oct 02, 2026 |
| HNTB ✓ | Intern - AI Business Process Developer (Summer 2027) 🛂 | [Apply](https://hntb.wd5.myworkdayjobs.com/hntb_careers/job/Austin-TX/Intern---AI-Business-Process-Developer--Summer-2027-_R-31865-1) | Austin, TX | Python, C#, SQL | Oct 02, 2026 |
| Arc | Software Engineering Intern | [Apply](https://job-boards.greenhouse.io/arcboatcompany/jobs/5442881008) | Torrance, CA | Python, TypeScript, AWS, Git | Oct 02, 2026 |
| xAI | Summer 2027 Software Engineering Internship/Co-op | [Apply](https://job-boards.greenhouse.io/xai/jobs/5255111007) | Palo Alto, CA | Python, Java, C++, C# | Oct 02, 2026 |
| CACI | Software Engineer Intern - Summer 2027 | [Apply](https://caci.wd1.myworkdayjobs.com/external/job/Austin-TX-US/Software-Engineer-Intern---Summer-2027_333037) | Austin, TX, US | Java, C++, JavaScript, Linux | Oct 02, 2026 |
| Nelnet | Intern - IT Software Engineer .NET (Summer 2027) | [Apply](https://nelnet.wd1.myworkdayjobs.com/MyNelnet/job/Lincoln-NE/Intern---IT-Software-Engineer-NET--Summer-2027-_R23198) | Lincoln, NE | Angular | Oct 02, 2026 |
| Major League Baseball | Intern, Data Science | [Apply](https://sterlingmets.wd5.myworkdayjobs.com/Mets/job/Citi-Field--Queens-New-York/Intern--Data-Science_R1508) | Citi Field – Queens, New York | Python | Oct 02, 2026 |
| Bedrock Robotics | 2027 Internship Behavior ML Engineer, Learned Manipulation Policies | [Apply](https://jobs.ashbyhq.com/bedrock-robotics/96a6423e-7439-4cb4-9109-117b14e47f7c) | San Francisco, CA | Python, PyTorch | Oct 02, 2026 |
| Vanguard | College to Corporate IT Internship-Risk & Security Engineer (PA) | [Apply](https://vanguard.wd5.myworkdayjobs.com/vanguard_external/job/Malvern-PA/College-to-Corporate-IT-Internship-Risk---Security-Engineer--PA-_182784) | Malvern, PA | No skills listed | Oct 02, 2026 |
| Pinterest ✓ 🆁 | Software Engineer Intern 2027 (USA) | [Apply](https://www.pinterestcareers.com/jobs/?gh_jid=7838577) | San Francisco, CA, US; Remote, US | Python, Java, C++, TypeScript | Oct 01, 2026 |
| Pinterest ✓ | Master's Machine Learning Internship 2027 (USA) | [Apply](https://www.pinterestcareers.com/jobs/?gh_jid=8138090) | San Francisco +11 more | Python, Java, C++, PyTorch | Oct 01, 2026 |
| Pinterest ✓ | Master's Data Science Internship 2027 (USA) | [Apply](https://www.pinterestcareers.com/jobs/?gh_jid=8138097) | San Francisco +11 more | Python, SQL | Oct 01, 2026 |
| Walleye Capital | Special Projects Developer Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/walleyecapital-external-students/jobs/4716166006) | New York, New York | Python, SQL, LLMs | Oct 01, 2026 |
| Datacor 🆁 | Summer 2027 AI Engineer Intern | [Apply](https://job-boards.greenhouse.io/datacor/jobs/5242412007) | Remote, US | Python, Java, C++, LLMs | Oct 01, 2026 |
| Stantec | Transporta​tion Engineering Intern - Infrastruc​ture (Summer 2027) | [Apply](https://hdhl.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/1008089) | Atlanta, GA, United States | No skills listed | Oct 01, 2026 |
| ATC | Intern - Cyber Security Summer 2027 | [Apply](https://atcllc.wd5.myworkdayjobs.com/atcllc/job/Pewaukee-WI/Intern---Cyber-Security-Summer-2027_R0003307) | Pewaukee, WI | No skills listed | Oct 01, 2026 |
| CoStar Group | Embedded Software Engineering Intern 🛂 | [Apply](https://costar.wd1.myworkdayjobs.com/Costar_Campus/job/Sunnyvale-US/Embedded-Software-Engineering-Intern_R39950) | Sunnyvale (US) | Python, C++, MATLAB, PyTorch | Oct 01, 2026 |
| RTX | Flight Control Software Engineering Intern (Summer 2027) (Open) 🇺🇸 | [Apply](https://globalhr.wd5.myworkdayjobs.com/rec_rtx_ext_gateway/job/US-IA-CEDAR-RAPIDS-193--1120-Collins-Rd-NE--BLDG193/Flight-Control-Software-Engineering-Intern--Summer-2027---Open-_01870974) | US-IA-CEDAR RAPIDS-193 ~ 1120 Collins R… | C++, MATLAB | Oct 01, 2026 |
| The Federal Reserve System | Summer 2027 Intern-Cloud Engineering 🛂 | [Apply](https://rb.wd5.myworkdayjobs.com/FRS/job/Chicago-IL/Summer-2027-Intern-Cloud-Engineering_R-0000033614) | Chicago, IL | No skills listed | Oct 01, 2026 |
| The Federal Reserve System | Summer 2027 Intern-Computer Science and Software Engineering 🛂 | [Apply](https://rb.wd5.myworkdayjobs.com/FRS/job/Chicago-IL/Summer-2027-Intern-Computer-Science-and-Software-Engineering_R-0000033637) | Chicago, IL | No skills listed | Oct 01, 2026 |
| The Federal Reserve System | Summer 2027 Intern-Cybersecur​ity and Information Security 🛂 | [Apply](https://rb.wd5.myworkdayjobs.com/FRS/job/Chicago-IL/Summer-2027-Intern-Cybersecurity-and-Information-Security_R-0000033612-1) | Chicago, IL | No skills listed | Oct 01, 2026 |
| Old Mission Capital | Quantitative Trader - 2027 Micro-Internship Program (January Start) | [Apply](https://www.oldmissioncapital.com/careers/?gh_jid=8002345003) | Chicago, IL, United States | Python | Oct 01, 2026 |
| Varda Space | Cybersecur​ity Internship - Summer 2027 🇺🇸 | [Apply](https://job-boards.greenhouse.io/vardaspace/jobs/8005821003) | El Segundo, California, United States | Python, Bash | Oct 01, 2026 |
| Varda Space | Flight Software Internship - Summer 2027 🇺🇸 | [Apply](https://job-boards.greenhouse.io/vardaspace/jobs/8010159003) | El Segundo, California, United States | C++, Linux | Oct 01, 2026 |
| Allen Control Systems | Android Developer Intern, 2027 | [Apply](https://jobs.ashbyhq.com/allen-control-systems/1cd2b432-9a01-4ae0-8eb2-6ebd9c278b94) | Austin, TX | Kotlin, Computer Vision | Sep 30, 2026 |
| Muon Space | Flight Software Engineering Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/muonspace/jobs/5247725007) | San Jose, CA | Python, C++ | Sep 30, 2026 |
| Dandy | Summer 2027 Internship - Software Engineering Intern | [Apply](https://jobs.ashbyhq.com/dandy/d43558e9-8e51-4980-b00d-39275063f099) | USA - New York NY | TypeScript, React, GraphQL | Sep 30, 2026 |
| Waymo ✓ | 2027 Summer Intern, BS, Software Engineering, Labeling | [Apply](https://careers.withwaymo.com/jobs?gh_jid=8238525) | Mountain View, CA, USA | C++, TypeScript | Sep 30, 2026 |
| Robinhood | Data Science Intern (Summer 2027) | [Apply](https://boards.greenhouse.io/robinhood/jobs/8241738?t=gh_src=&gh_jid=8241738) | Menlo Park, CA | Python, SQL | Sep 29, 2026 |
| AMCA | Software Engineering Internship (Summer 2027) | [Apply](https://job-boards.greenhouse.io/amca/jobs/4425120009) | El Segundo, CA | Python, TypeScript, SQL, React | Sep 29, 2026 |
| Muon Space | GNC Software Engineering Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/muonspace/jobs/5252680007) | Mountain View, CA | Python, C++ | Sep 29, 2026 |
| Itron ✓ | Intern - Data Science, Distributed Intelligence | [Apply](https://itron.wd5.myworkdayjobs.com/Early_Careers/job/United-States-of-America-Washington-Liberty-Lake/Intern---Data-Science--Distributed-Intelligence_JR102942-2) | United States of America +2 more | Python, SQL, AWS, Azure | Sep 29, 2026 |
| ICF ✓ | 2027 Summer Intern, AI Engineer (Reston, VA) 🇺🇸 | [Apply](https://icf.wd5.myworkdayjobs.com/ICFExternal_Career_Site/job/Reston-VA/XMLNAME-2027-Summer-Intern--AI-Engineer--Reston--VA-_R2603312-1) | Reston, VA | Python, Java, C++, JavaScript | Sep 29, 2026 |
| Perchwell | Software Engineering Intern | [Apply](https://jobs.ashbyhq.com/perchwell/194eec78-26db-4d8e-850f-a99ea2733e9f) | New York Office | TypeScript, SQL, Ruby, React | Sep 29, 2026 |
| Enova | Software Engineer Internship Summer 2027 (Hybrid) 🛂 | [Apply](https://job-boards.greenhouse.io/enova/jobs/8239619) | Chicago, IL | Go, Ruby | Sep 29, 2026 |
| National Life | Digital & AI Experience Intern – Summer 2027 🛂 | [Apply](https://job-boards.greenhouse.io/nationallifeinsurancecompany/jobs/4403876009) | Addison, TX; Montpelier, VT | LLMs | Sep 29, 2026 |
| Marvell | AI-Native Development Platform Engineer Intern, MS - Summer 2027 | [Apply](https://marvell.wd1.myworkdayjobs.com/MarvellCareers/job/Santa-Clara-CA/AI-Native-Development-Platform-Engineer-Intern--MS---Summer-2027_2603848-1) | Santa Clara, CA | Python, Java, C#, TypeScript | Sep 29, 2026 |
| Q2 | 2027 Summer Internship - Data Science 🛂 | [Apply](https://q2ebanking.wd5.myworkdayjobs.com/Q2/job/Cary-North-Carolina/XMLNAME-2027-Summer-Internship---Data-Science_REQ-12799) | Cary, North Carolina | Python, SQL, Git | Sep 29, 2026 |
| Q2 | 2027 Summer Internship - Machine Learning Engineer 🛂 | [Apply](https://q2ebanking.wd5.myworkdayjobs.com/Q2/job/Cary-North-Carolina/XMLNAME-2027-Summer-Internship---Machine-Learning-Engineer_REQ-12800) | Cary, North Carolina | Python, Java, PyTorch, TensorFlow | Sep 29, 2026 |
| Q2 | 2027 Summer Internship - Software Engineer 🛂 | [Apply](https://q2ebanking.wd5.myworkdayjobs.com/Q2/job/Cary-North-Carolina/XMLNAME-2027-Summer-Internship---Software-Engineer_REQ-12798) | Cary, North Carolina | Python, C#, JavaScript, SQL | Sep 29, 2026 |
| Upbound Group | ServiceNow Developer Intern | [Apply](https://upbound.wd501.myworkdayjobs.com/Upbound/job/Plano-TX/User-Experience-Intern_R-100778) | Plano, TX | JavaScript | Sep 29, 2026 |
| Hermeus | Flight Software Engineering Intern (Simulation/Hardware-In-The-Loop) - Spring & Summer 2027 🇺🇸 | [Apply](https://jobs.lever.co/hermeus/78008094-ca81-4a0c-9a18-93b30f932acd) | Los Angeles, CA | Python, C++, MATLAB, Linux | Sep 29, 2026 |
| Verizon Communicat​ions | Irving V Teamer for a Day: Verizon Data Science Summer 2027 Internship | [Apply](https://verizon.wd12.myworkdayjobs.com/verizon-careers/job/Irving-Texas/Irving-V-Teamer-for-a-Day--Verizon-Data-Science-Summer-2027-Internship_R-1101386) | Irving, Texas | LLMs | Sep 29, 2026 |
| Verizon Communicat​ions | Verizon Network and Technology: Data Science Summer 2027 Internship | [Apply](https://verizon.wd12.myworkdayjobs.com/verizon-careers/job/Irving-Texas/Verizon-Network-and-Technology--Data-Science-Summer-2027-Internship_R-1101384) | Irving, Texas | LLMs | Sep 29, 2026 |
| The Aerospace Corporation | 2027 Software Tools and Assurance Engineering Grad Intern 🇺🇸 | [Apply](https://aero.wd5.myworkdayjobs.com/external/job/El-Segundo-CA/XMLNAME-2027-Software-Tools-and-Assurance-Engineering-Grad-Intern_R016753) | El Segundo, CA | Python, Java, C++ | Sep 28, 2026 |
| Cencora | AI Intern 🛂 | [Apply](https://myhrabc.wd5.myworkdayjobs.com/Global/job/Conshohocken-PA/AI-Intern_R2613670) | Conshohock​en, PA | No skills listed | Sep 28, 2026 |
| Formlabsin​ternships | Desktop Software Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/formlabsinternships/jobs/8223362) | Somerville, MA | C++ | Sep 28, 2026 |
| Blue Cross Blue Shield of Michigan ✓ | Summer 2027 Intern - Data Science / Biostatist​ician | [Apply](https://ejko.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_3/job/14837) | Detroit, MI, United States | Python, SQL, Spark | Sep 28, 2026 |
| GM financial | Intern - Cybersecur​ity 🛂 | [Apply](https://fa-exvu-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/260805) | Irving, TX, United States | No skills listed | Sep 28, 2026 |
| GM financial | Intern - Cybersecur​ity | [Apply](https://fa-exvu-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/260836) | Arlington, TX, United States | No skills listed | Sep 28, 2026 |
| Lawrence Livermore National Laboratory (LLNL) | Data Science Institute Graduate Student Intern - Summer 2027 | [Apply](https://jobs.smartrecruiters.com/LLNL/3743990015737586) | Livermore, CA, United States (Hybrid) | No skills listed | Sep 28, 2026 |
| Cencora | IT Software Development Intern 🛂 | [Apply](https://myhrabc.wd5.myworkdayjobs.com/Global/job/Conshohocken-PA/IT-Software-Development-Intern_R2614039) | Conshohock​en, PA | Java, C++, JavaScript, React | Sep 28, 2026 |
| Cencora | IT Software Intern 🛂 | [Apply](https://myhrabc.wd5.myworkdayjobs.com/Global/job/Conshohocken-PA/IT-Software-Intern_R2614031) | Conshohock​en, PA | Java, C++, JavaScript, React | Sep 28, 2026 |
| Upbound Group | Cybersecur​ity Intern | [Apply](https://upbound.wd501.myworkdayjobs.com/Upbound/job/Plano-TX/Cybersecurity-Intern_R-100776) | Plano, TX | Python, SQL, Pandas, LLMs | Sep 28, 2026 |
| Veterans United 🆁 | Intern - Software Engineer - Summer 2027 | [Apply](https://veteransunited.wd1.myworkdayjobs.com/VUHL/job/Remote-MO/Intern---Software-Engineer---Summer-2027_R6249) | Remote MO | No skills listed | Sep 28, 2026 |
| Philips | Intern – Embedded Systems Test Automation Engineer – Bothell, WA – Summer 2027 | [Apply](https://philips.wd3.myworkdayjobs.com/jobs-and-careers/job/Bothell-Washington-United-States/Intern---Embedded-Systems-Test-Automation-Engineer---Bothell--WA---Summer-2027_592074) | Bothell, Washington, United States | Python, C++ | Sep 28, 2026 |
| General Dynamics Information Technology ✓ | GDIT Summer Internship Program – Summer 2027 AI/ML Data Science and Engineering Internship 🇺🇸 | [Apply](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Data-Science-and-Engineering-Internship_RQ228936) | USA LA Bossier City | Python, SQL, LLMs | Sep 26, 2026 |
| General Dynamics Information Technology ✓ | GDIT Summer Internship Program – Summer 2027 AI/ML Software Development and Engineering Internship 🇺🇸 _(6 openings)_ | [Apply](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Software-Development-and-Engineering-Internship_RQ228939) [#2](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Software-Development-and-Engineering-Internship_RQ228940) [#3](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Software-Development-and-Engineering-Internship_RQ228941) [#4](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Software-Development-and-Engineering-Internship_RQ229141) [#5](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Software-Development-and-Engineering-Internship_RQ229142) [#6](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-ML-Software-Development-and-Engineering-Internship_RQ229143) | USA LA Bossier City | Python, SQL, PyTorch, TensorFlow | Sep 26, 2026 |
| Mach Industries | Summer 2027 Engineering Internship, Software/GNC 🛂 | [Apply](https://job-boards.greenhouse.io/machindustries/jobs/4420626009) | Huntington Beach +5 more | No skills listed | Sep 25, 2026 |
| Zurn Elkay Water Solutions | Embedded Firmware Intern (Summer 2027) | [Apply](https://elkay.wd1.myworkdayjobs.com/Elkay_External/job/Milwaukee-WI/Embedded-Firmware-Intern--Summer-2027-_REQ-020150-1) | Milwaukee, WI | C++ | Sep 25, 2026 |
| Zurn Elkay Water Solutions | Embedded Hardware Intern (Summer 2027) | [Apply](https://elkay.wd1.myworkdayjobs.com/Elkay_External/job/Milwaukee-WI/Embedded-Hardware-Intern--Summer-2027-_REQ-020151) | Milwaukee, WI | No skills listed | Sep 25, 2026 |
| Zurn Elkay Water Solutions | IT Infrastruc​ture & AI Enablement Intern (Summer 2027) _(2 openings)_ | [Apply](https://elkay.wd1.myworkdayjobs.com/Elkay_External/job/Milwaukee-WI/IT-Infrastructure-Intern--Summer-2027-_REQ-020160) [#2](https://elkay.wd1.myworkdayjobs.com/Elkay_External/job/Milwaukee-WI/IT-Infrastructure-Intern--Summer-2027-_REQ-020162) | Milwaukee, WI | No skills listed | Sep 25, 2026 |
| AbbVie ✓ | 2027 Business Technology Solutions Intern - Cybersecur​ity (Undergrad​uate) | [Apply](https://jobs.smartrecruiters.com/AbbVie/3743990015679246) | North Chicago +2 more | Python, Java, C#, JavaScript | Sep 25, 2026 |
| AbbVie ✓ | 2027 Business Technology Solutions Intern - Cloud Engineering (Undergrad​uate) | [Apply](https://jobs.smartrecruiters.com/AbbVie/3743990015679346) | North Chicago +2 more | HTML/CSS, AWS, GCP, Azure | Sep 25, 2026 |
| AbbVie ✓ | 2027 Business Technology Solutions Intern - Data & Software Engineering (Undergrad​uate) | [Apply](https://jobs.smartrecruiters.com/AbbVie/3743990015679386) | North Chicago +2 more | Python, Java, TypeScript, JavaScript | Sep 25, 2026 |
| Motorola | Software Engineering Intern - Summer 2027 🇺🇸 | [Apply](https://motorolasolutions.wd5.myworkdayjobs.com/Careers/job/Plantation-FL/Software-Engineering-Intern---Summer-2027_R69136) | Plantation, FL | Java, C++, C#, SQL | Sep 24, 2026 |
| Voloridge | Quantitative Trading Intern 2027 | [Apply](https://job-boards.greenhouse.io/voloridgeinvestmentmanagement/jobs/4405530009) | Jupiter, FL | Python, SQL | Sep 24, 2026 |
| ABB ✓ | IS Common Infrastruc​ture Intern- Summer 2027 🛂 | [Apply](https://abb.wd3.myworkdayjobs.com/external_career_page/job/USA-NC-Cary/IS-Common-Infrastructure-Intern--Summer-2027_JR00047125) | USA, NC, Cary | No skills listed | Sep 24, 2026 |
| Figma ✓ | Data Engineer Intern (2027) | [Apply](https://boards.greenhouse.io/figma/jobs/6178851004?gh_jid=6178851004) | San Francisco, CA • New York, NY | Python, SQL | Sep 23, 2026 |
| DoorDash ✓ | Machine Learning Intern (Masters) - Summer 2027 | [Apply](https://job-boards.greenhouse.io/doordashusa/jobs/8204111) | San Francisco +7 more | Python, Java, C++, Go | Sep 23, 2026 |
| Klaviyo ✓ | AI Engineer Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/klaviyocampus/jobs/8003260003) | Boston, MA | No skills listed | Sep 23, 2026 |
| Klaviyo ✓ | Machine Learning Engineer Internship-Summer 2027 | [Apply](https://job-boards.greenhouse.io/klaviyocampus/jobs/7999274003) | Palo Alto, CA | Python, PyTorch, LLMs | Sep 23, 2026 |
| General Dynamics Information Technology ✓ | GDIT Summer Internship Program – Summer 2027 AI Network Engineering Internship 🇺🇸 | [Apply](https://gdit.wd5.myworkdayjobs.com/gdit_earlytalent/job/USA-LA-Bossier-City/GDIT-Summer-Internship-Program---Summer-2027-AI-Network-Engineering-Internship_RQ228934-2) | USA LA Bossier City | Python, LLMs | Sep 23, 2026 |
| Insulet Corporation ✓ | Intern, DevOps Engineer: June-August 2027 (Onsite) | [Apply](https://insulet.wd5.myworkdayjobs.com/insuletcareers/job/San-Diego-California/Intern--DevOps-Engineer--June-August-2027--Onsite-_REQ-2026-18202) | San Diego, California | Python, Bash, AWS, Linux | Sep 23, 2026 |
| Grow Therapy | Software Engineering Intern (Summer 2027) | [Apply](https://jobs.ashbyhq.com/grow-therapy/92bfe88a-4c23-48c8-8f7b-4959ab6cd8d8) | New York City | Python, TypeScript, React | Sep 22, 2026 |
| Astranis | Software Engineer Backend Intern (Summer 2027) 🇺🇸 | [Apply](https://job-boards.greenhouse.io/astranis/jobs/4705214006) | San Francisco, CA | Python, Kubernetes, PostgreSQL | Sep 22, 2026 |
| Astranis | Software Engineer - Enterprise Systems Intern (Summer 2027) 🇺🇸 | [Apply](https://job-boards.greenhouse.io/astranis/jobs/4705610006) | San Francisco, CA | Python, Kubernetes, PostgreSQL | Sep 22, 2026 |
| American Express ✓ | Campus Undergradu​ate Summer Internship Program - 2027 Software Engineer, Enterprise Technology Services- Salt Lake City, UT | [Apply](https://egug.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/26014224) | Salt Lake City, UT, United States | Python, Java, C#, Go | Sep 22, 2026 |
| Rentvision | Software Engineering Intern | [Apply](https://apply.workable.com/rentvision/j/0F1C7992BF/) | Lincoln, Nebraska, United States | Java, TypeScript, JavaScript, React | Sep 21, 2026 |
| Formlabsin​ternships | Embedded Software Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/formlabsinternships/jobs/8222268) | Somerville, MA | Python, C++, Linux | Sep 21, 2026 |
| Cowboy Space | Intern, Software Engineering, 2027 🇺🇸 | [Apply](https://jobs.ashbyhq.com/cowboyspace/56d1d7e4-fa7e-4c25-aa8b-6828447fc64a) | San Carlos, California | Python, C++, Verilog | Sep 21, 2026 |
| Bracco | Quality Analyst Intern (Software) | [Apply](https://bracco.wd103.myworkdayjobs.com/braccocareers/job/USA-Eden-Prairie-Minnesota-55344/Quality-Analyst-Intern--Software-_JR100314) | USA, Eden Prairie, Minnesota, 55344 | No skills listed | Sep 21, 2026 |
| Commerce Bank | Intern - Data Analyst (Summer 2027) 🛂 | [Apply](https://commercebank.wd1.myworkdayjobs.com/CommerceJobs/job/MO---Kansas-City-DowntownPlaza---Kansas-City---KC-Downtown-Trust-Building-922-Walnut-64106/Intern-EABI---Data-Analyst-Summer-2027_38484) | MO - Kansas City Downtown/Plaza - Kansa… | Python, SQL, Tableau | Sep 21, 2026 |
| Commerce Bank | Intern - Data Science (Summer 2027) 🛂 | [Apply](https://commercebank.wd1.myworkdayjobs.com/CommerceJobs/job/MO---Kansas-City-DowntownPlaza---Kansas-City---KC-Downtown-Trust-Building-922-Walnut-64106/Intern-EABI---Data-Science-Summer-2027_38483) | MO - Kansas City Downtown/Plaza - Kansa… | Python | Sep 21, 2026 |
| AutoZone ✓ | AutoZone 2027 Summer Internship – Data Science | [Apply](https://egud.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/155461) | Memphis, TN, United States | Python, Java, SQL, Tableau | Sep 21, 2026 |
| Thrivent 🆁 | Associate Software Engineer - Junior Intern Summer 2027 🛂 | [Apply](https://thrivent.wd5.myworkdayjobs.com/external/job/Remote-Minnesota/Associate-Software-Engineer---Junior-Intern-Summer-2027_REQ-48334) | Remote-Minnesota | JavaScript, HTML/CSS | Sep 18, 2026 |
| Thrivent 🆁 | Associate Software Engineer - Sophomore Intern Summer 2027 🛂 | [Apply](https://thrivent.wd5.myworkdayjobs.com/external/job/Remote-Minnesota/Associate-Software-Engineer---Sophomore-Intern-Summer-2027_REQ-48457) | Remote-Minnesota | JavaScript, HTML/CSS | Sep 18, 2026 |
| Lawrence Livermore National Laboratory (LLNL) | Computing Undergradu​ate Student Intern: DevOps Internship Program - Summer 2027 | [Apply](https://jobs.smartrecruiters.com/LLNL/3743990015408206) | Livermore, CA, United States | LLMs, Kubernetes, Git | Sep 18, 2026 |
| Veolia | SAP & ServiceNow AI Automation Intern 🛂 | [Apply](https://jobs.smartrecruiters.com/VeoliaEnvironnementSA/744000150460339) | Trevose, PA, United States (Hybrid) | No skills listed | Sep 18, 2026 |
| Centene 🆁 | Cybersecur​ity Summer 2027 Intern (Undergrad​uate) | [Apply](https://centene.wd5.myworkdayjobs.com/Centene_External/job/Remote-MO/Cybersecurity-Summer-2027-Intern--Undergraduate-_1660514) | Remote-MO | No skills listed | Sep 18, 2026 |
| Zekelman Industries | AI Intern | [Apply](https://zekelman.wd12.myworkdayjobs.com/Careers/job/Wheatland-PA---Council-Ave/AI-Intern_JR002752) | Wheatland, PA - Council Ave | No skills listed | Sep 17, 2026 |
| Church & Dwight | AI Developer Co-op - Graduate Program (9 Months) 🇺🇸 | [Apply](https://churchdwight.wd1.myworkdayjobs.com/chdcareers/job/USA-Ewing-NJ/AI-Developer-Co-op---Graduate-Program--9-Months-_R2026-15686) | USA, Ewing, NJ | Python, SQL, LLMs, AWS | Sep 17, 2026 |
| Honeywell | Data Science Co-Op - Spring/Summer 2027 🇺🇸 | [Apply](https://ibqbjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/157903) | Pittsford, NY, United States | Python, LLMs, AWS, Azure | Sep 17, 2026 |
| Honeywell | Software Engineer Co-Op - Spring/Summer 2027 🇺🇸 | [Apply](https://ibqbjb.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/158088) | Pittsford, NY, United States | No skills listed | Sep 17, 2026 |
| LabCorp | Intern – Network Infrastruc​ture & Automation Engineering 🛂 | [Apply](https://labcorp.wd1.myworkdayjobs.com/external/job/Durham-NC/Intern---Network-Infrastructure---Automation-Engineering_2632795) | Durham NC | Python, Linux, Git | Sep 17, 2026 |
| Marvell | SRAM Software Engineer Intern, BS - Summer 2027 | [Apply](https://marvell.wd1.myworkdayjobs.com/MarvellCareers/job/Burlington-VT/SRAM-Software-Engineer-Intern--BS---Summer-2027_2603760-1) | Burlington, VT | Python, Java, Bash, Linux | Sep 17, 2026 |
| GM financial | Intern - Software Development Engineer _(2 openings)_ | [Apply](https://fa-exvu-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/260795) [#2](https://fa-exvu-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/260943) | Arlington, TX, United States | LLMs | Sep 17, 2026 |
| Clarios ✓ | Data Science Intern (Summer 2027) 🛂 | [Apply](https://clarios.wd5.myworkdayjobs.com/clarioscareers/job/United-States-Wisconsin-Milwaukee/Data-Science-Intern--Summer-2027-_WD50211) | United States, Wisconsin, Milwaukee | Python, SQL, LLMs, Azure | Sep 17, 2026 |
| Smith+Nephew ✓ | Intern AI Center of Excellence Data Science | [Apply](https://smithnephew.wd5.myworkdayjobs.com/External/job/US---Pittsburgh-PA/Intern-AI-Center-of-Excellence-Data-Science_R92480-1) | US - Pittsburgh, PA | Python, MATLAB, PyTorch, TensorFlow | Sep 17, 2026 |
| Smith+Nephew ✓ | Intern Robotics Software Engineering | [Apply](https://smithnephew.wd5.myworkdayjobs.com/External/job/US---Pittsburgh-PA/Intern-Robotics-Software-Engineering_R92482) | US - Pittsburgh, PA | C++ | Sep 17, 2026 |
| Avav | Summer 2027 Software Engineering Intern | [Apply](https://avav.wd1.myworkdayjobs.com/avav/job/Melbourne-FL/Summer-2027-Software-Engineering-Intern_8550) | Melbourne, FL | Python, Java, C++, Bash | Sep 16, 2026 |
| CoVar | Machine Learning Internship Summer 2027 | [Apply](https://job-boards.greenhouse.io/covar/jobs/5240360007) | Durham, NC | Python, PyTorch, Pandas, Computer Vision | Sep 16, 2026 |
| Nanopath | Software Development Co-op (Jan '27 Start) | [Apply](https://job-boards.greenhouse.io/nanopathinc/jobs/4732881005) | Cambridge, MA | No skills listed | Sep 16, 2026 |
| Bass Pro Shops | Cybersecur​ity Intern Summer 2027 | [Apply](https://basspro.wd1.myworkdayjobs.com/careers/job/Springfield-MO-Bass-Pro-Shops-Base-Camp/Cybersecurity-Intern-Summer-2027_R267444) | Springfield +1 more | No skills listed | Sep 16, 2026 |
| Bass Pro Shops | IT Developer Intern Summer 2027 | [Apply](https://basspro.wd1.myworkdayjobs.com/careers/job/Springfield-MO-Bass-Pro-Shops-Base-Camp/IT-Developer-Intern-Summer-2027_R267441-1) | Springfield +1 more | No skills listed | Sep 16, 2026 |
| Rendezvous Robotics | Software Engineering Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/rendezvousrobotics/jobs/4408590009) | Golden, CO | Python, C++, Linux | Sep 16, 2026 |
| AspenTech | Software Development Intern - Digital Grid Management - Summer 2027 | [Apply](https://aspentech.wd5.myworkdayjobs.com/aspentech/job/Medina-Minnesota/Software-Development-Intern---Digital-Grid-Management---Summer-2027_R9456) | Medina, Minnesota | Python, Java, C++, JavaScript | Sep 16, 2026 |
| Bedrock Robotics | 2027 Internship Software Engineer, Fleet Platform | [Apply](https://jobs.ashbyhq.com/bedrock-robotics/8927dd7e-a48d-49a2-92eb-09ec059432f4) | New York, NY | Python, C++, Rust, TypeScript | Sep 16, 2026 |
| Gecko Robotics | Full Stack Software Engineering Intern | [Apply](https://jobs.ashbyhq.com/gecko-robotics/01138338-ff3c-4982-8ba3-5401386bf082) | New York City | Python, TypeScript, JavaScript, LLMs | Sep 16, 2026 |
| Gecko Robotics | AI/Machine Learning Engineering Intern | [Apply](https://jobs.ashbyhq.com/gecko-robotics/c097505b-0a28-4a33-a917-268f463641e8) | New York City | Python, SQL, PyTorch, Pandas | Sep 16, 2026 |
| Cartesian | IAP Software Engineering Intern 2027 | [Apply](https://job-boards.greenhouse.io/cartesiansystems/jobs/4408204009) | Cambridge, MA | Python, TypeScript, Kotlin, PyTorch | Sep 16, 2026 |
| Relay | Software Engineering Intern (AI/ML) - Summer 2027 | [Apply](https://job-boards.greenhouse.io/relaypro/jobs/8176774) | Raleigh, NC | Python, Rust, JavaScript, PyTorch | Sep 16, 2026 |
| Relay | Software Engineering Intern (Device Team) - Summer 2027 | [Apply](https://job-boards.greenhouse.io/relaypro/jobs/8180836) | Raleigh, NC | Python, Java, C++, Rust | Sep 16, 2026 |
| Lawrence Livermore National Laboratory (LLNL) | Data Science Institute Undergradu​ate Student Intern - Summer 2027 | [Apply](https://jobs.smartrecruiters.com/LLNL/3743990015289136) | Livermore, CA, United States (Hybrid) | No skills listed | Sep 16, 2026 |
| Anduril | 2027 Flight Software Engineer Intern | [Apply](https://boards.greenhouse.io/andurilindustries/jobs/5239083007?gh_jid=5239083007) | Costa Mesa, California, United States | Python, MATLAB, Computer Vision | Sep 15, 2026 |
| RAVE Aerospace | Intern - Software Engineering (Summer 2027) | [Apply](https://apply.workable.com/raveaerospace/j/739753C003/) | Laramie, Wyoming, United States | Python, Java, C++ | Sep 15, 2026 |
| SingleStore ✓ | Software Engineer Intern- Helios- 2027 | [Apply](https://job-boards.greenhouse.io/singlestore/jobs/8205514) | United States | Go, TypeScript, JavaScript, SQL | Sep 15, 2026 |
| Johnson & Johnson | Software Engineering Intern - Robotics R&D 🛂 | [Apply](https://jj.wd5.myworkdayjobs.com/JJ/job/Santa-Clara-California-United-States-of-America/Software-Engineering-Intern---Robotics-R-D_R-099919) | Santa Clara +2 more | Python, C++, Computer Vision, Git | Sep 15, 2026 |
| Philips | Intern- AI Business Operations-Nashville, TN-Summer 2027 | [Apply](https://philips.wd3.myworkdayjobs.com/jobs-and-careers/job/Nashville-Tennessee-United-States/Intern--AI-Business-Operations-Nashville--TN-Summer-2027_590986) | Nashville, Tennessee, United States | Python | Sep 15, 2026 |
| NOV | Software Engineering Intern | [Apply](https://egay.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_4001/job/44449) | Houston, TX, United States | Python, Java, C++, C# | Sep 15, 2026 |
| AspenTech | Data Science Intern - Summer 2027 - Bedford, MA | [Apply](https://aspentech.wd5.myworkdayjobs.com/aspentech/job/Bedford-Massachusetts/Data-Science-Intern---Summer-2027---Bedford--MA_R9459) | Bedford, Massachuse​tts | Python, C++, C#, LLMs | Sep 15, 2026 |
| CAI | Cybersecur​ity Analyst Intern | [Apply](https://cai.wd5.myworkdayjobs.com/computer_aid/job/California/Cybersecurity-Analyst-Intern_R8488) | California | Python, AWS, Azure, Linux | Sep 15, 2026 |
| Robinhood | Software Engineering Intern, Backend (Summer 2027) | [Apply](https://boards.greenhouse.io/robinhood/jobs/8123225?t=gh_src=&gh_jid=8123225) | Bellevue +5 more | Python, Django, AWS, Kubernetes | Sep 14, 2026 |
| Robinhood | Software Engineering Intern, iOS (Summer 2027) | [Apply](https://boards.greenhouse.io/robinhood/jobs/8142959?t=gh_src=&gh_jid=8142959) | Menlo Park, CA; New York, NY | Swift | Sep 14, 2026 |
| Figma ✓ | Software Engineer Intern (Summer 2027) | [Apply](https://boards.greenhouse.io/figma/jobs/6143238004?gh_jid=6143238004) | San Francisco, CA • New York, NY | Python, Java, C++, JavaScript | Sep 14, 2026 |
| Figma ✓ | Data Science Intern (2027) | [Apply](https://boards.greenhouse.io/figma/jobs/6178857004?gh_jid=6178857004) | San Francisco, CA • New York, NY | Python, SQL | Sep 14, 2026 |
| DoorDash ✓ | Software Engineer, Intern (Summer 2027) - US | [Apply](https://job-boards.greenhouse.io/doordashusa/jobs/8171041) | New York +9 more | Python, Java, SQL, Kotlin | Sep 14, 2026 |
| Workshop | Software Engineer Intern (Summer 2027) | [Apply](https://job-boards.greenhouse.io/workshop/jobs/5237900007) | Omaha, Nebraska, United States | No skills listed | Sep 14, 2026 |
| Amgen ✓ 🆁 | Grad Intern – Digital Product – Technology, AI & Data (Summer 2027) | [Apply](https://amgen.wd1.myworkdayjobs.com/careers/job/United-States---Remote/Grad-Intern---Digital-Product---Amgen-s-Technology---Medical-Organizations--Summer-2027-_R-255744) | United States - Remote | Python, Java, SQL, Scala | Sep 14, 2026 |
| Amgen ✓ 🆁 | Undergrad Intern – Digital Product – Technology, AI & Data (Summer 2027) | [Apply](https://amgen.wd1.myworkdayjobs.com/careers/job/United-States---Remote/Undergrad-Intern---Digital-Product---Amgen-s-Technology---Medical-Organizations--Summer-2027-_R-255711) | United States - Remote | Python, Java, SQL, Scala | Sep 14, 2026 |
| LabCorp | Intern - Software Developer 🛂 | [Apply](https://labcorp.wd1.myworkdayjobs.com/external/job/Durham-NC/Intern---Software-Developer_2632330) | Durham NC | No skills listed | Sep 14, 2026 |
| SingleStore ✓ | Software Engineer Intern- Engine-2027 | [Apply](https://job-boards.greenhouse.io/singlestore/jobs/8154399) | United States | Go, TypeScript, JavaScript, SQL | Sep 14, 2026 |
| Brevan Howard | 2027 Summer Internship Program – AI & Quantitative Analyst, New York | [Apply](https://wd3.myworkdaysite.com/recruiting/brevanhoward/BH_ExternalCareers/job/New-York/XMLNAME-2027-Summer-Internship-Program---AI---Quantitative-Analyst--New-York_JR101602) | New York | Python, LLMs | Sep 14, 2026 |
| Clarios ✓ | People Analytics & AI Intern (Summer 2027) 🛂 | [Apply](https://clarios.wd5.myworkdayjobs.com/clarioscareers/job/United-States-Wisconsin-Milwaukee/People-Analytics---AI-Intern--Summer-2027-_WD50216) | United States, Wisconsin, Milwaukee | Python, SQL, Snowflake | Sep 14, 2026 |
| Oshkosh | Robotic Programming/Welding Intern (Summer 2027) | [Apply](https://oshkoshcorporation.wd5.myworkdayjobs.com/Oshkosh/job/McConnellsburg-Pennsylvania-United-States/Robotic-Programming-Welding-Intern--Summer-2027-_R49598) | Mc​Connellsburg +2 more | No skills listed | Sep 14, 2026 |
| AtkinsRéalis | Data Scientist Intern - Summer 2027 | [Apply](https://slihrms.wd3.myworkdayjobs.com/careers/job/USAZTempe/Data-Scientist-Intern---Summer-2027_R-161183-1) | US.AZ.Tempe | Python, SQL | Sep 14, 2026 |
| AtkinsRéalis | Water Infrastruc​ture Engineering Intern - Summer 2027 | [Apply](https://slihrms.wd3.myworkdayjobs.com/careers/job/USNVHenderson/Water-Infrastructure-Engineering-Intern---Summer-2027_R-160500-2) | US.NV.Hend​erson | No skills listed | Sep 14, 2026 |
| AI Intern to the CEO | Software Engineering Intern - SWE/ML (Summer 2027) | [Apply](https://jobs.ashbyhq.com/cyvl/8bfc4116-b0bb-47f8-bca1-7069a37db328) | Boston, Massachuse​tts | Python, SQL, PyTorch, Computer Vision | Sep 14, 2026 |
| CoStar Group | Security Engineer Intern - Richmond, VA 🛂 | [Apply](https://costar.wd1.myworkdayjobs.com/Costar_Campus/job/US-VA-Richmond/Security-Engineer-Intern---Richmond--VA_R39726) | US-VA Richmond | Python, Bash, Linux | Sep 14, 2026 |
| Oshkosh | Software Engineer Intern - Summer 2027 | [Apply](https://oshkoshcorporation.wd5.myworkdayjobs.com/Oshkosh/job/Huntersville-North-Carolina-United-States/Software-Engineer-Intern---Summer-2027_R50321) | Huntersville +2 more | Python, C++, C#, JavaScript | Sep 14, 2026 |
| Philips | Intern – Medical Imaging Software Engineering, IVUS – Plymouth, MN – Summer 2027 | [Apply](https://philips.wd3.myworkdayjobs.com/jobs-and-careers/job/Plymouth-Minnesota-United-States/Intern---Software-Engineering---Plymouth--MN---Summer-2027_590403) | Plymouth, Minnesota, United States | Python, Java, C++, C# | Sep 14, 2026 |
| TD Bank | 2027 Summer Internship Program - Global Technology & Solutions - Data Analyst | [Apply](https://td.wd3.myworkdayjobs.com/TD_Bank_Careers/job/Mount-Laurel-New-Jersey/XMLNAME-2027-Summer-Internship-Program---Global-Technology---Solutions---Data-Analyst_R_1510800) | Mount Laurel, New Jersey | No skills listed | Sep 13, 2026 |
| TD Bank | 2027 Summer Internship Program - Global Technology & Solutions - Cloud/DevOps | [Apply](https://td.wd3.myworkdayjobs.com/TD_Bank_Careers/job/Mount-Laurel-New-Jersey/XMLNAME-2027-Summer-Internship-Program---Global-Technology---Solutions---Cloud-DevOps_R_1510799) | Mount Laurel, New Jersey | Terraform | Sep 13, 2026 |
| TD Bank | 2027 Summer Internship Program - Global Technology & Solutions - Cyber Security | [Apply](https://td.wd3.myworkdayjobs.com/TD_Bank_Careers/job/Mount-Laurel-New-Jersey/XMLNAME-2027-Summer-Internship-Program---Global-Technology---Solutions---Cyber-Security_R_1510795) | Mount Laurel, New Jersey | No skills listed | Sep 13, 2026 |
| AnaVation | Computer Science Internship Summer 2027 🇺🇸 | [Apply](https://jobs.lever.co/anavationllc/4a82ae00-30f0-410c-bf3c-f1cdd18739e7) | Chantilly, VA | Python, Java, Node.js, AWS | Sep 12, 2026 |
| Lyft ✓ | Data Analyst Intern (Summer 2027) | [Apply](https://app.careerpuck.com/job-board/lyft/job/8802198002?gh_jid=8802198002) | New York, NY | SQL | Sep 11, 2026 |
| Lyft ✓ | Software Engineer Intern, Backend (Summer 2027 - SF) | [Apply](https://app.careerpuck.com/job-board/lyft/job/8767726002?gh_jid=8767726002) | San Francisco, CA | No skills listed | Sep 11, 2026 |
| Lyft ✓ | Data Science Intern, Algorithms (Summer 2027 - SF/NYC) | [Apply](https://app.careerpuck.com/job-board/lyft/job/8796124002?gh_jid=8796124002) | New York, NY | Python, SQL, PyTorch, TensorFlow | Sep 11, 2026 |
| Megazone​Cloud | Software Engineer Co-op 2027 🛂 | [Apply](https://jobs.ashbyhq.com/megazone/e2889469-cf20-4227-bf24-2a6e885f8dca) | Rochester, NY | Python, Java, JavaScript, LLMs | Sep 11, 2026 |
| Megazone​Cloud | Data Engineer Co-op 2027 🛂 | [Apply](https://jobs.ashbyhq.com/megazone/fde09888-986f-4207-88fe-3ff5b921a1fa) | Rochester, NY | Python, SQL, LLMs, AWS | Sep 11, 2026 |
| Klaviyo ✓ | Software Engineer Intern (Summer 2027) 🛂 | [Apply](https://job-boards.greenhouse.io/klaviyocampus/jobs/7989364003) | Boston, MA | Python, TypeScript, React, Django | Sep 11, 2026 |
| Xcimer Energy | Summer 2027 Internship - Computatio​nal and Software Engineering 🇺🇸 | [Apply](https://jobs.lever.co/xcimer/fee9965c-8040-4614-8fd1-10bddfe3b911) | Denver, CO | No skills listed | Sep 11, 2026 |
| Booz Allen | University - Summer 2027, Software Engineer Intern 🇺🇸 | [Apply](https://bah.wd1.myworkdayjobs.com/bah_jobs/job/Fayetteville-NC/University---Summer-2027--Software-Engineer-Intern_R0249225) | Fayettevil​le, NC | Java, C++, Git | Sep 11, 2026 |
| Amgen ✓ 🆁 | Grad Intern – Data Engineer – Amgen’s Technology & Medical Organizati​ons (Summer 2027) | [Apply](https://amgen.wd1.myworkdayjobs.com/careers/job/United-States---Remote/Grad-Intern---Data-Engineer---Amgen-s-Technology---Medical-Organizations--Summer-2027-_R-255725) | United States - Remote | Python, Java, SQL, Scala | Sep 11, 2026 |
| Leidos ✓ | AI/ML Intern 🇺🇸 | [Apply](http
