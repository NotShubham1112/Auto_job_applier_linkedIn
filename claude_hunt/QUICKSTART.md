🚀 QUICK START GUIDE
====================

Everything you need is in this folder. Here's where to start:

STEP 1: Read the strategy (30 min)
FILE: STRATEGY.md
→ Understand the full system
→ Read mindset shifts
→ See why this works better than spray applying

STEP 2: Set up contact discovery (15 min)
FILE: contact_discovery.py
→ Run: python3 contact_discovery.py
→ Output: recruiting_contacts.csv (emails you found)
→ This bypasses ATS entirely

STEP 3: Prep LinkedIn content (30 min)
FILE: linkedin_posts_ready.txt
→ Copy first post (Post #1 - RAG optimization)
→ Post to LinkedIn today
→ Don't overthink, just post

STEP 4: Send first email (15 min)
FILE: outreach_templates.json + target_companies.json
→ Pick Modal or Together (good response rates)
→ Use the template for that company
→ Personalize one sentence about their product
→ Send to recruiting@company.com

STEP 5: Start logging (5 min)
FILE: campaign_tracker.py
→ Run: python3 campaign_tracker.py
→ Log your first email
→ This creates your tracking CSVs

Total time to execute: 90 minutes

═══════════════════════════════════════════════════════════════════════════════

FILE STRUCTURE & PURPOSE
========================

📁 /home/claude/ai_job_hunt/

STRATEGY & PLANNING
────────────────────
STRATEGY.md
  → Master strategic document
  → Read this first (30 min)
  → Reference throughout

linkedin_strategy.py
  → LinkedIn content strategy
  → Content pillars, posting schedule
  → Engagement rules

linkedin_posts_ready.txt
  → 10 ready-to-post LinkedIn posts
  → Week 1-4 content
  → Copy-paste ready

EXECUTION TOOLS
────────────────
contact_discovery.py
  → Finds recruiting emails from company websites
  → Web scraper + email extraction
  → Usage: python3 contact_discovery.py
  → Output: recruiting_contacts.csv

outreach_templates.py
  → 12 company-specific email templates
  → Personalization guides
  → Follow-up variations

campaign_tracker.py
  → Logging system for all activities
  → Tracks emails sent, responses, LinkedIn posts
  → Usage: python3 campaign_tracker.py
  → Output: outreach_log.csv, responses.csv, linkedin_log.csv

DATA & REFERENCE
────────────────
target_companies.json
  → 38 curated remote AI/ML companies
  → Organized by stage (Series A-D)
  → Tech stack + hiring signals

outreach_templates.json
  → All email templates in JSON format
  → Easy for importing into tools
  → Follow-up variations

recruiting_contacts.csv
  → Output from contact_discovery.py
  → Company, website, email, confidence
  → Your target list

EXECUTION LOGS (Created after first use)
────────────────────
outreach_log.csv
  → Every email you send
  → Company, contact, subject, date, response status
  → Update manually or via campaign_tracker.py

responses.csv
  → Every response received
  → Company, contact, message, response type, next action
  → Track conversation progress

linkedin_log.csv
  → Every LinkedIn post
  → Date, post type, impressions, engagement
  → Measure what works

═══════════════════════════════════════════════════════════════════════════════

DAILY ROUTINE (30-45 min total)
===============================

MORNING (15 min):
□ Check for email responses
□ Log any new responses in campaign_tracker.py
□ Reply to any meaningful messages (within 1 hour)

MIDDAY (20 min):
□ Post LinkedIn content (if it's a posting day)
  Mon: Technical or Learning post
  Wed: Build in Public or Systems Thinking
  Fri: Systems Thinking or Founder Perspective
□ Engage with 2-3 relevant posts in your feed (5 min)
□ Reply to comments on your posts (5 min)

EVENING (20 min):
□ Send 5-10 outreach emails (batch is faster)
□ Log sent emails in campaign_tracker.py
□ Update tracker with status

WEEKLY REVIEW (30 min):
□ Check metrics: Response rate, engagement
□ Which templates are working?
□ Which LinkedIn posts got traction?
□ Adjust messaging if needed
□ Plan next week's posts

═══════════════════════════════════════════════════════════════════════════════

USAGE INSTRUCTIONS
==================

RUNNING CONTACT DISCOVERY
═════════════════════════
python3 contact_discovery.py

What it does:
- Visits career pages of target companies
- Extracts publicly visible recruiting emails
- Rates confidence (HIGH/MEDIUM/LOW)
- Outputs CSV of contacts

Output file: recruiting_contacts.csv
Columns: company, website, email, contact_type, confidence, source_page

Takes: ~2-5 min (configurable for full or subset)
Result: Ready-to-contact email addresses


SENDING OUTREACH EMAILS
═══════════════════════
1. Open outreach_templates.json
2. Find template for your target company
3. Customize 1-2 sentences for their specific product
4. Copy subject line (optional: customize)
5. Paste body into email
6. Replace {hiring_contact} with real name if you have it
7. Send from your email
8. Log in campaign_tracker.py

Example personalization:
TEMPLATE: "I'm building orchestration systems for multi-model LLM workflows"
PERSONALIZED: "I'm building orchestration systems for multi-model LLM workflows—
your OpenRouter integration is interesting for this approach"

Time per email: 3-5 min (template saves time)


POSTING TO LINKEDIN
═══════════════════
1. Open linkedin_posts_ready.txt
2. Copy entire post (preserves formatting)
3. Paste into LinkedIn post editor
4. Click Post
5. Log post in campaign_tracker.py

Best practice:
- Post same time each day (9am or 2pm IST)
- Don't edit much (authenticity > perfection)
- Engage with comments in first 2 hours

Time per post: 2 min


TRACKING METRICS
════════════════
python3 campaign_tracker.py

What it tracks:
- Emails sent (date, company, template, response status)
- LinkedIn posts (date, type, impressions, engagement)
- Responses received (date, company, message, next action)

Output files:
- outreach_log.csv (emails)
- linkedin_log.csv (posts)
- responses.csv (conversations)

Manual entry for simplicity. Can automate later if needed.

═══════════════════════════════════════════════════════════════════════════════

COMMON QUESTIONS
================

Q: Should I customize every email?
A: 70% template, 30% custom. Change 1-2 sentences to reference their product.

Q: How many emails should I send per day?
A: 5-10/day. More is burnout, less is slow. Spread across time zones.

Q: When should I follow up?
A: 5 days after initial send. Max 2 follow-ups per person.

Q: What if I get no responses?
A: Check your personalization first. Generic emails get ignored. Then adjust template.

Q: Should I DM people on LinkedIn?
A: Only after they engage with your content. Then reference the post they liked.

Q: How long until I see results?
A: First response: 3-5 days. Meaningful conversations: 2-3 weeks. Interviews: 4-8 weeks.

Q: What's a good response rate?
A: 5-10% = good personalization. 2-3% = need better template. <1% = generic email.

Q: Can I apply to jobs AND do outreach?
A: Yes, but use this system instead. Better ROI than ATS.

Q: Should I mention I'm actively looking?
A: No. Say "evaluating opportunities" or "open to conversations."

Q: What if a company says they're not hiring?
A: Build relationship anyway. Ask when they expect to hire. Stay connected.

═══════════════════════════════════════════════════════════════════════════════

WEEK 1 CHECKLIST
================

□ Read STRATEGY.md (understand the system)
□ Run contact_discovery.py (get recruiting emails)
□ Customize profile for LinkedIn (add link to GitHub)
□ Post first LinkedIn post (use linkedin_posts_ready.txt #1)
□ Send first batch of outreach emails (5-10 total)
□ Log all activities in campaign_tracker.py
□ Set up calendar for rest of week:
  □ Wednesday: Post LinkedIn #2
  □ Friday: Post LinkedIn #3
  □ Send emails daily (5-10 each day)

═══════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING
===============

PROBLEM: Getting 0% response rate
→ Are you personalizing? Each email should reference their product specifically.
→ Are you targeting right companies? Smaller companies (TIER 2-3) respond better.
→ Is email going to spam? Use company domain for reply (not Gmail).

PROBLEM: Contact discovery script failing
→ Some sites block scraping. That's OK, move to next company.
→ Check recruiting_contacts.json for manual fallback (try LinkedIn searches).
→ Try different company in same tier.

PROBLEM: LinkedIn posts getting 0 engagement
→ Are you posting at good times? 9am or 2pm IST.
→ Are posts too generic? Add specific numbers/learnings.
→ Are you engaging in comments? Engagement helps algorithmic distribution.

PROBLEM: Not finding time to execute
→ This is 45 min/day max. Is that really impossible?
→ Consider batch work: 2 hours on Sunday for entire week of emails.
→ Or do 15 min chunks (LinkedIn morning, emails evening).

═══════════════════════════════════════════════════════════════════════════════

SUCCESS STORY TEMPLATE
======================

When you get an interview, come back and update this:

Date: ___________
Company: ___________
Contact: ___________

How I found them: □ Contact discovery  □ LinkedIn  □ Referral
Template used: ___________
Response time: _____ days
Number of follow-ups: _____

What worked:
- ___________
- ___________
- ___________

What I'd change:
- ___________

Outcome:
□ Phone screen scheduled
□ Interview scheduled
□ Offer received
□ Became friend/connection

Key insight:
___________

(Share this with other builders. The system only gets better when people iterate.)

═══════════════════════════════════════════════════════════════════════════════

NEXT STEPS
==========

You're 90 minutes away from execution.

Do this now:
1. Read STRATEGY.md (30 min)
2. Run contact_discovery.py (15 min)
3. Post first LinkedIn post (5 min)
4. Send first email (10 min)
5. Log it (5 min)

That's it. You've started.

Everything else is just repetition.

System > Luck
Consistency > Talent
Action > Planning

Start now.

═══════════════════════════════════════════════════════════════════════════════
