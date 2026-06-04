"""
OUTREACH TEMPLATES FOR SHUBHAM
==============================

Strategy: Position as builder > job applicant
- Reference their actual product
- Show you understand their technical challenges
- Propose specific value
- Call to conversation (not "let's talk about my resume")

Rule: NO generic application language
Rule: 3-4 sentences max
Rule: Technical + founder mindset
Rule: Make them curious about what you've built
"""

import json

templates = {
    
    # ===========================================
    # 1. MODAL / SERVERLESS INFRA PLATFORMS
    # ===========================================
    "Modal": {
        "subject": "Distributed LLM orchestration architecture question",
        "body": """Hey {hiring_contact},

I'm building orchestration layers for multi-model LLM workflows (Anthropic/OpenAI/Mistral) with hot-swap model selection and fallback chains. Modal's serverless compute model seems like the natural fit for this—especially the ability to dynamically route inference loads.

Shipped a production SaaS with similar architecture. Would be curious to explore how Modal approaches container orchestration for stateful AI workloads.

Open to conversation if you're building on this front.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 2. TOGETHER AI / LLM INFERENCE
    # ===========================================
    "Together AI": {
        "subject": "Latency optimization for multi-provider LLM routing",
        "body": """Hey {hiring_contact},

Been optimizing inference latency across OpenRouter's multi-model gateway—reduced p95 response time ~65% through connection pooling + request batching. Curious how Together approaches distributed inference scheduling for variable-latency model providers.

Currently shipping production AI workflows at scale. Would be interesting to discuss your infrastructure challenges if you're building on this.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 3. PINECONE / VECTOR DB PLATFORMS
    # ===========================================
    "Pinecone": {
        "subject": "Hybrid retrieval + semantic search optimization",
        "body": """Hey {hiring_contact},

I've been working on RAG pipelines with hybrid vector search (semantic + BM25 re-ranking). Built a financial intelligence platform that surfaces analyst-grade company research in <10 seconds over 10K+ document corpus using text-embedding-3-small + vector similarity.

The retrieval bottleneck is interesting—A/B tested pure embedding search vs. hybrid and saw significant relevance improvements. Would be curious about your approach to this problem.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 4. LANGCHAIN / AI FRAMEWORKS
    # ===========================================
    "Langchain": {
        "subject": "Production LLM orchestration patterns",
        "body": """Hey {hiring_contact},

Just shipped a multi-agent document processing pipeline using MCP-based orchestration. Built task routing across 4 LLM providers with reusable workflow abstractions and zero-downtime fallback chains.

Langchain's abstractions are solid for this—curious about how you're thinking about orchestration primitives for production systems at scale.

Open to chat.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 5. RETOOL / LOW-CODE PLATFORMS WITH AI
    # ===========================================
    "Retool": {
        "subject": "Shipping production AI features fast",
        "body": """Hey {hiring_contact},

I've been shipping full-stack AI applications to 500+ users on Next.js + FastAPI. What's been interesting is reducing the iteration cycle on backend workflows—went from 3-hour manual reviews to <15 minutes with AI-powered document processing.

Retool's direction on AI seems aligned with this need. Would be curious about your approach to no-code + AI.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 6. HUGGING FACE
    # ===========================================
    "Hugging Face": {
        "subject": "Production deployment of open-source models",
        "body": """Hey {hiring_contact},

Been integrating open-source models (Mistral, Llama variants) into production workflows alongside proprietary APIs. The challenge is managing model versioning, inference optimization, and fallback chains.

Hugging Face is obviously the backbone here. Interested in how you're thinking about production deployment infrastructure for model inference at scale.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 7. SUPABASE / OPEN SOURCE DATA PLATFORMS
    # ===========================================
    "Supabase": {
        "subject": "Scaling AI applications with vector search",
        "body": """Hey {hiring_contact},

Currently building AI SaaS on Next.js + Supabase + Vercel. The vector search layer is critical—implemented hybrid retrieval over a document corpus with real-time analytics pipelines.

Supabase's PostgreSQL foundation makes this possible. Would be interesting to discuss how you're approaching vector search + real-time capabilities for AI-driven applications.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 8. REPLIT / AI-POWERED CODING
    # ===========================================
    "Replit": {
        "subject": "Developer experience in AI workflows",
        "body": """Hey {hiring_contact},

I'm a full-stack AI engineer shipping products in Python, TypeScript, and SQL. Development velocity matters—automation tools, intelligent workflows, reduction of boilerplate. Replit's mission here is compelling.

Built orchestration systems + production SaaS. Would be curious to explore how you're building developer experience into AI.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 9. VERCEL / FRONTEND AI DEPLOYMENT
    # ===========================================
    "Vercel": {
        "subject": "AI-native frontend architecture",
        "body": """Hey {hiring_contact},

Shipped a production SaaS frontend on Next.js (obviously). The interesting part is integrating real-time AI features—streaming responses, live document processing, orchestrated workflows.

Vercel's direction on AI feels like the natural progression. Curious about your vision for AI-native frontend primitives.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 10. ANTHROPIC / FOUNDATIONAL MODELS
    # ===========================================
    "Anthropic": {
        "subject": "Multi-model orchestration with Claude + competitors",
        "body": """Hey {hiring_contact},

I've been building orchestration systems that route requests across Claude, GPT-4, and Mistral based on task requirements—comparing quality, latency, and cost tradeoffs.

Claude's reasoning capabilities are compelling for structured workflows. Curious about how you're thinking about model integration patterns for production systems.

Would love to chat.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 11. MISTRAL AI / OPEN SOURCE LLMS
    # ===========================================
    "Mistral AI": {
        "subject": "Open-source model deployment + optimization",
        "body": """Hey {hiring_contact},

Using Mistral models in production workflows. The appeal is clear—open-source reliability + latency benefits + cost structure. Been comparing model quality across Mistral vs Anthropic vs OpenAI on specific task benchmarks.

Curious about your approach to production deployment infrastructure for open models at scale.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # 12. FIREWORKS AI / INFERENCE OPTIMIZATION
    # ===========================================
    "Fireworks AI": {
        "subject": "Sub-300ms inference latency optimization",
        "body": """Hey {hiring_contact},

Optimizing for inference latency is critical in production systems. My current stack achieves sub-300ms p95 retrieval over 10K+ documents using optimized vector search + batching strategies.

Fireworks' approach to inference optimization is interesting. Would be curious about your technical approach here.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # GENERIC FALLBACK (For any other AI company)
    # ===========================================
    "Generic AI Platform": {
        "subject": "Building production AI systems",
        "body": """Hey {hiring_contact},

I've shipped full-stack AI applications with end-to-end architecture—Next.js frontend, FastAPI backend, vector search, real-time analytics. Current focus: intelligent document processing + multi-model orchestration.

Your product seems well-positioned for this type of system. Would be curious to chat about technical direction.

Shubham
github.com/NotShubham1112"""
    },
    
    # ===========================================
    # VARIATION: FOUNDING TEAM APPROACH
    # (For companies with public founder info)
    # ===========================================
    "Founding Team": {
        "subject": "{founder_name} — similar problems you're solving",
        "body": """Hey {founder_name},

Following {company}'s direction. Building similar systems—multi-model LLM orchestration, vector search optimization, production SaaS architecture.

Been shipping rapidly (Browork + Quantexera projects in parallel). Would be interesting to discuss technical approach on the infrastructure side.

Shubham
github.com/NotShubham1112"""
    },
}

# ===========================================
# EMAIL SUBJECT LINE VARIATIONS
# ===========================================
subject_variations = {
    "Technical Depth": "Quick technical question on {technology}",
    "Product Direction": "Curious about your approach to {challenge}",
    "Builder to Builder": "Shipping similar systems—technical discussion?",
    "Problem-Focused": "Optimizing for {metric}—your take?",
    "Architecture": "{architecture_type} at scale",
}

# ===========================================
# FOLLOW-UP TEMPLATES (if no response after 5 days)
# ===========================================
followups = {
    "Gentle Reminder": """Hi {hiring_contact},

Sent this a few days ago—no pressure, but curious if you saw it. My approach to multi-model orchestration might be relevant to what you're building.

If timing's not right, totally understand.

Shubham""",
    
    "Different Angle": """Hey {hiring_contact},

Different angle: been optimizing latency on distributed inference. Sub-300ms p95 on vector search + multi-model routing. Curious how this compares to your infrastructure challenges.

Would be a good conversation.

Shubham""",
    
    "One Last Time": """Hey {hiring_contact},

Last attempt—genuinely interested in what {company} is building on the infrastructure side. Happy to grab 15 min if timing works.

Shubham
github.com/NotShubham1112""",
}

# ===========================================
# PERSONALIZATION DATA
# ===========================================
company_context = {
    "Anthropic": {
        "focus": "constitutional AI, reasoning, safety",
        "your_angle": "Multi-model orchestration with Claude + competitors",
        "tech_stack": "Claude API, orchestration, fallback chains"
    },
    "Modal": {
        "focus": "serverless compute for AI/ML",
        "your_angle": "Stateful LLM orchestration",
        "tech_stack": "FastAPI, distributed inference, container orchestration"
    },
    "Together AI": {
        "focus": "distributed LLM inference",
        "your_angle": "Latency optimization across providers",
        "tech_stack": "OpenRouter, multi-provider routing, connection pooling"
    },
    "Pinecone": {
        "focus": "vector database as a service",
        "your_angle": "Hybrid RAG + semantic search optimization",
        "tech_stack": "text-embedding-3-small, BM25, hybrid retrieval"
    },
    "Hugging Face": {
        "focus": "open-source model ecosystem",
        "your_angle": "Production deployment of open models",
        "tech_stack": "Mistral, Llama, model versioning"
    },
}

if __name__ == "__main__":
    print("=" * 60)
    print("📧 OUTREACH TEMPLATE SYSTEM")
    print("=" * 60)
    print(f"\nAvailable templates: {len(templates)}")
    print(f"Available follow-ups: {len(followups)}")
    print(f"\nTemplates:")
    for company in templates.keys():
        print(f"  - {company}")
    
    # Export as JSON for easy access
    with open('outreach_templates.json', 'w') as f:
        json.dump({
            'templates': templates,
            'subject_variations': subject_variations,
            'followups': followups,
            'company_context': company_context
        }, f, indent=2)
    
    print(f"\n✅ Exported to outreach_templates.json")
