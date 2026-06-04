#!/usr/bin/env python3
"""
Recruiting Contact Discovery System
=====================================
Find publicly available recruiting emails from AI/ML company websites.

RULES:
- Only public information
- Only emails displayed on websites
- No guessing patterns
- Prefer official recruiting channels

WORKFLOW:
1. Visit careers/jobs pages
2. Extract emails (regex + visible text)
3. Identify hiring manager contacts
4. Validate + deduplicate
5. Export structured CSV
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import csv
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import time

class RecrutingContactFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = []
        self.visited_urls = set()
        
    def extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses using regex"""
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        return set(re.findall(email_pattern, text))
    
    def score_email_priority(self, email: str) -> str:
        """Score email priority based on local part"""
        local_part = email.split('@')[0].lower()
        
        # HIGH priority recruiting emails
        high_priority = ['careers', 'recruiting', 'recruitment', 'talent', 'talentacquisition', 
                        'hiring', 'hr', 'people', 'jobs', 'apply']
        
        # MEDIUM priority
        medium_priority = ['contact', 'info', 'hello', 'team']
        
        # LOW priority - avoid
        low_priority = ['support', 'billing', 'legal', 'privacy', 'abuse', 'security', 
                       'press', 'media', 'marketing', 'sales']
        
        if any(keyword in local_part for keyword in high_priority):
            return 'HIGH'
        elif any(keyword in local_part for keyword in medium_priority):
            return 'MEDIUM'
        elif any(keyword in local_part for keyword in low_priority):
            return 'SKIP'
        else:
            return 'UNKNOWN'
    
    def fetch_page(self, url: str) -> tuple:
        """Fetch page content safely"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text, response.status_code
        except Exception as e:
            print(f"  ❌ Failed to fetch {url}: {str(e)}")
            return None, None
    
    def discover_company(self, company_data: Dict) -> Dict:
        """Discover recruiting contacts for a single company"""
        company_name = company_data['company']
        domain = company_data['domain']
        
        print(f"\n🔍 Scanning {company_name} ({domain})...")
        
        all_emails = set()
        contact_forms = []
        source_pages = []
        
        # Build base URL
        if not domain.startswith('http'):
            base_url = f"https://{domain}"
        else:
            base_url = domain
        
        # Common career page paths
        career_paths = [
            '/careers',
            '/jobs',
            '/join-us',
            '/work-with-us',
            '/hiring',
            '/contact',
            '/about',
            '/team',
            '/careers/',
            '/jobs/',
        ]
        
        urls_to_check = [base_url + path for path in career_paths]
        urls_to_check.insert(0, base_url)  # Always check homepage first
        
        for url in urls_to_check:
            if url in self.visited_urls:
                continue
            
            print(f"  → {url}")
            content, status = self.fetch_page(url)
            
            if content is None:
                continue
            
            self.visited_urls.add(url)
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract visible text emails
            page_text = soup.get_text()
            page_emails = self.extract_emails(page_text)
            
            # Extract emails from href attributes
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    page_emails.add(email)
            
            # Look for contact forms
            forms = soup.find_all('form')
            if forms and 'contact' in url.lower():
                contact_forms.append(url)
            
            # Filter emails by domain
            valid_emails = {
                email for email in page_emails 
                if domain.replace('www.', '') in email
            }
            
            if valid_emails:
                print(f"    ✅ Found {len(valid_emails)} email(s)")
                all_emails.update(valid_emails)
                source_pages.append(url)
            
            time.sleep(0.5)  # Be respectful
        
        # Filter and rank emails
        prioritized_emails = []
        for email in all_emails:
            priority = self.score_email_priority(email)
            if priority != 'SKIP':
                prioritized_emails.append({
                    'email': email,
                    'priority': priority
                })
        
        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'UNKNOWN': 2}
        prioritized_emails.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        # Determine confidence
        if any(e['priority'] == 'HIGH' for e in prioritized_emails):
            confidence = 'HIGH'
        elif prioritized_emails:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        result = {
            'company': company_name,
            'website': base_url,
            'recruiting_emails': [e['email'] for e in prioritized_emails[:3]],  # Top 3
            'all_emails': all_emails,
            'contact_forms': contact_forms,
            'source_pages': source_pages,
            'confidence': confidence,
            'email_details': prioritized_emails
        }
        
        return result
    
    def run(self, companies: List[Dict]):
        """Process all companies"""
        print("=" * 60)
        print("🚀 RECRUITING CONTACT DISCOVERY SYSTEM")
        print("=" * 60)
        print(f"\n📋 Scanning {len(companies)} companies...\n")
        
        for i, company in enumerate(companies, 1):
            print(f"[{i}/{len(companies)}]", end="")
            result = self.discover_company(company)
            self.results.append(result)
        
        return self.results
    
    def export_csv(self, filename: str):
        """Export results to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['company', 'website', 'email', 'contact_type', 
                           'confidence', 'source_page']
            )
            writer.writeheader()
            
            for result in self.results:
                for email in result['recruiting_emails']:
                    writer.writerow({
                        'company': result['company'],
                        'website': result['website'],
                        'email': email,
                        'contact_type': 'Recruiting',
                        'confidence': result['confidence'],
                        'source_page': result['source_pages'][0] if result['source_pages'] else 'N/A'
                    })
        
        print(f"\n✅ Exported to {filename}")
    
    def export_json(self, filename: str):
        """Export detailed results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"✅ Exported to {filename}")
    
    def print_summary(self):
        """Print summary"""
        print("\n" + "=" * 60)
        print("📊 DISCOVERY SUMMARY")
        print("=" * 60)
        
        total_emails = sum(len(r['recruiting_emails']) for r in self.results)
        high_confidence = sum(1 for r in self.results if r['confidence'] == 'HIGH')
        
        print(f"\n✅ Total Companies Scanned: {len(self.results)}")
        print(f"📧 Recruiting Emails Found: {total_emails}")
        print(f"🎯 HIGH Confidence: {high_confidence}")
        
        print("\n🔥 Top Contacts (HIGH confidence):\n")
        for result in self.results:
            if result['confidence'] == 'HIGH' and result['recruiting_emails']:
                print(f"  {result['company']}")
                for email in result['recruiting_emails'][:2]:
                    print(f"    → {email}")


if __name__ == "__main__":
    # Load target companies
    with open('target_companies.json', 'r') as f:
        companies = json.load(f)
    
    # Run discovery (subset for demo)
    finder = RecrutingContactFinder()
    
    # Start with top 10 for speed
    print("\n⚠️  NOTE: Running on top 10 companies (demo mode)")
    print("    Uncomment line 200 to run full scan\n")
    
    results = finder.run(companies[:10])  # Demo: top 10
    # results = finder.run(companies)  # Full scan
    
    # Export results
    finder.export_csv('recruiting_contacts.csv')
    finder.export_json('recruiting_contacts.json')
    finder.print_summary()
