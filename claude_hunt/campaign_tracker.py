#!/usr/bin/env python3
"""
CAMPAIGN MANAGEMENT TRACKER
===========================

Track:
1. Outreach emails sent (company, contact, date, status)
2. LinkedIn content posted
3. Responses received
4. Follow-ups sent
5. Overall metrics

This is your job hunt CRM.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

class CampaignTracker:
    def __init__(self):
        self.outreach_file = 'outreach_log.csv'
        self.linkedin_file = 'linkedin_log.csv'
        self.responses_file = 'responses.csv'
        
        self._init_files()
    
    def _init_files(self):
        """Initialize CSV files if they don't exist"""
        
        # Outreach tracking
        if not Path(self.outreach_file).exists():
            with open(self.outreach_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'date', 'company', 'contact_email', 'contact_name',
                    'subject_line', 'template_used', 'personalization_level',
                    'status', 'followup_date', 'response_date', 'notes'
                ])
                writer.writeheader()
        
        # LinkedIn tracking
        if not Path(self.linkedin_file).exists():
            with open(self.linkedin_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'date', 'post_type', 'topic', 'post_content_preview',
                    'impressions', 'engagement', 'saves', 'comments', 'reposts',
                    'notes'
                ])
                writer.writeheader()
        
        # Response tracking
        if not Path(self.responses_file).exists():
            with open(self.responses_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'date', 'company', 'contact_name', 'message_preview',
                    'response_type', 'next_action', 'status', 'notes'
                ])
                writer.writeheader()
    
    def log_outreach(self, company, contact_email, contact_name, 
                    subject_line, template_used, personalization_level='HIGH'):
        """Log an outreach email sent"""
        with open(self.outreach_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'company', 'contact_email', 'contact_name',
                'subject_line', 'template_used', 'personalization_level',
                'status', 'followup_date', 'response_date', 'notes'
            ])
            writer.writerow({
                'date': datetime.now().isoformat(),
                'company': company,
                'contact_email': contact_email,
                'contact_name': contact_name,
                'subject_line': subject_line,
                'template_used': template_used,
                'personalization_level': personalization_level,
                'status': 'SENT',
                'followup_date': (datetime.now() + timedelta(days=5)).isoformat(),
                'response_date': '',
                'notes': ''
            })
    
    def log_linkedin_post(self, post_type, topic, content_preview):
        """Log LinkedIn post sent"""
        with open(self.linkedin_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'post_type', 'topic', 'post_content_preview',
                'impressions', 'engagement', 'saves', 'comments', 'reposts', 'notes'
            ])
            writer.writerow({
                'date': datetime.now().isoformat(),
                'post_type': post_type,
                'topic': topic,
                'post_content_preview': content_preview[:100],
                'impressions': '',
                'engagement': '',
                'saves': '',
                'comments': '',
                'reposts': '',
                'notes': 'Posted'
            })
    
    def log_response(self, company, contact_name, message_preview, response_type, next_action):
        """Log response received"""
        with open(self.responses_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'company', 'contact_name', 'message_preview',
                'response_type', 'next_action', 'status', 'notes'
            ])
            writer.writerow({
                'date': datetime.now().isoformat(),
                'company': company,
                'contact_name': contact_name,
                'message_preview': message_preview[:100],
                'response_type': response_type,
                'next_action': next_action,
                'status': 'NEW',
                'notes': ''
            })
    
    def get_summary(self):
        """Get campaign summary stats"""
        try:
            with open(self.outreach_file, 'r') as f:
                outreach_count = len(f.readlines()) - 1  # Exclude header
            
            with open(self.responses_file, 'r') as f:
                response_count = len(f.readlines()) - 1
            
            response_rate = (response_count / outreach_count * 100) if outreach_count > 0 else 0
            
            return {
                'emails_sent': outreach_count,
                'responses_received': response_count,
                'response_rate': f"{response_rate:.1f}%",
                'pending_followups': outreach_count - response_count
            }
        except:
            return {'emails_sent': 0, 'responses_received': 0, 'response_rate': '0%'}


# ===========================================
# EXECUTION CHECKLIST
# ===========================================
execution_checklist = """
🚀 SHUBHAM'S JOB HUNT EXECUTION PLAN
=====================================

WEEK 1: SETUP
□ Run contact discovery on top 15 companies
□ Extract recruiting emails (HIGH priority only)
□ Set up LinkedIn strategy (customize profile)
□ Prepare first 5 LinkedIn posts
□ Create outreach email templates (personalized)

WEEK 2: LINKEDIN LAUNCH
□ Post Technical Breakdown #1 (RAG optimization)
□ Engage in comments daily (2-3 relevant posts)
□ Post Build in Public #1 (Browork overview)
□ Start building community (follow ~50 relevant people)
□ Prep Systems Thinking post

WEEK 3: OUTREACH BEGINS
□ Send first batch of outreach (15 emails)
  - 5 to high-priority targets (Anthropic, Modal, Together)
  - 10 to secondary targets
□ Post Systems Thinking post
□ Continue daily engagement
□ Log all emails in tracker
□ Prepare follow-up templates

WEEK 4: MOMENTUM
□ Send second batch of outreach (20 emails)
□ Post Learning & Insights post
□ Analyze LinkedIn metrics (what's working?)
□ Follow up with non-responders (first batch)
□ Build draft email response templates

WEEK 5-8: OPTIMIZATION LOOP
□ Continue 3x/week LinkedIn posting
□ Send 15-20 outreach emails weekly
□ Follow up with 50%+ of batch 1
□ Track metrics: response rate, engagement
□ Refine messaging based on feedback
□ Document conversations that lead to interviews

---

TARGET METRICS (By Week 8)
• Outreach emails sent: 100+
• Response rate: 5-10% (assuming good personalization)
• LinkedIn followers: 500-1000
• Interview conversations: 3-5+
• Actual interviews: 1-2+

KEY SUCCESS FACTORS
1. **Consistency** - 3x LinkedIn posts/week (no exceptions)
2. **Personalization** - Each email references their product
3. **Tracking** - Know your metrics (use CampaignTracker)
4. **Patience** - Most responses come weeks later
5. **Authenticity** - People can smell desperation; you're evaluating them too

FAILURE MODES TO AVOID
❌ Sending generic emails (instant delete)
❌ Ghosting LinkedIn strategy (kills credibility)
❌ Not tracking responses (lose opportunities)
❌ Giving up after week 1 (patience is competitive advantage)
❌ Copying other people's content (authentic beats viral)

---

DAILY ROUTINE
• Morning (30 min): Check responses, log in tracker
• Midday (20 min): Post LinkedIn content (3x/week), engage (daily)
• Evening (30 min): Outreach emails (batch 5-10/day)
• Weekly review (30 min): Metrics, adjust messaging, plan week ahead
"""

# ===========================================
# RESPONSE HANDLING GUIDE
# ===========================================
response_guide = """
📧 RESPONSE HANDLING GUIDE
==========================

When you get responses, they'll typically be one of:

1. "INTERESTED" - They want to talk
   Action: Reply quickly (within 1 hour)
   Message: "Thanks for getting back—excited to discuss [specific topic they mentioned]"
   Propose: 15 min call, no sales pitch, just conversation
   
2. "NOT NOW" - They like you but timing sucks
   Action: Ask when's better
   Message: "Totally understand timing. When's a good window to reconnect?"
   Save: Add to follow-up list (3 months later)
   
3. "NOT HIRING" - They're not hiring but respect your work
   Action: Build relationship anyway
   Message: "No problem. Happy to stay connected—excited about what you're building"
   Next: Engage with their content, check in 6 months
   
4. "PASS" - They're not interested
   Action: Move on (don't argue)
   Message: None necessary unless they give reason
   
5. NO RESPONSE (most common)
   Action: One follow-up after 5 days
   Then: Move on (don't spam)

---

CALL PREPARATION (If you get one)
• Research the person + company
• Have 3 specific questions about their tech stack
• Be ready to discuss your architecture decisions
• Ask what problems they're solving
• End with "What should I know about working with your team?"

GOAL: Position as peer/builder, not job applicant
• You're evaluating the opportunity too
• You have other options (LinkedIn + your products prove this)
• You're interested in their technical vision
• You want partnership, not just employment
"""

# ===========================================
# METRICS DASHBOARD
# ===========================================
dashboard_template = """
📊 CAMPAIGN METRICS DASHBOARD
=============================

Update weekly in your tracker.

OUTREACH METRICS:
Emails Sent This Week: ___
Response Rate: ___%
Total Conversations: ___
Interview Scheduled: ___

LINKEDIN METRICS:
New Followers: ___
Post Impressions (avg): ___
Comment Engagement: ___
Recruiter DMs: ___

INSIGHT:
What worked this week?
What needs adjustment?
Top performing content type?
"""

if __name__ == "__main__":
    print("=" * 60)
    print("📋 CAMPAIGN TRACKER & EXECUTION PLAN")
    print("=" * 60)
    
    tracker = CampaignTracker()
    print(f"\n✅ Initialized tracking files:")
    print(f"  - {tracker.outreach_file}")
    print(f"  - {tracker.linkedin_file}")
    print(f"  - {tracker.responses_file}")
    
    print("\n" + execution_checklist)
    print("\n" + response_guide)
    print("\n" + dashboard_template)
    
    # Save as text files
    with open('EXECUTION_PLAN.txt', 'w') as f:
        f.write(execution_checklist)
    
    with open('RESPONSE_GUIDE.txt', 'w') as f:
        f.write(response_guide)
    
    print(f"\n✅ Saved execution plan files")
