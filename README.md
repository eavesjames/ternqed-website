# TernQED Research Engine

**Human-AI Collaboration System for Latency Value Research**

A code-first, multi-agent research and publishing platform that produces a continuously updated knowledge base explaining how reductions in latency create value in electronic markets (equities + crypto).

---

## Philosophy

**You write. AI helps.**

This system optimizes for **human expertise + AI efficiency**:
- AI handles grunt work (research aggregation, formatting, verification)
- You handle high-leverage work (insight, narrative, claims)
- AI assists you in the moment (drafting help, citation finding, claim verification)

**Cost:** ~$20-25/month (vs $80-100 for full automation)
**Quality:** Higher (your domain expertise is irreplaceable)
**Time savings:** 10+ hours/week on research and formatting

---

## Weekly Workflow

### Monday: AI Prep Work (Automated)
```bash
python3 run.py research --topic "tail latency in crypto arbitrage"
```
**What happens:**
- AI analyzes 7 days of intake briefs
- Extracts relevant sources (20-30 articles)
- Generates claim table with citations
- Creates research summary JSON + HTML preview

**Cost:** ~$0.50
**Your time:** 0 minutes (runs overnight)

---

### Tuesday-Thursday: You Write (AI-Assisted)
```bash
# Terminal 1: Hugo live preview
hugo server -D

# Terminal 2: AI assistant
python3 run.py assist --research data/research/2026-02-24-tail-latency.json
```

**AI assistant commands:**
```
> find source: latency impact on bid-ask spreads

> draft: why tail latency matters more than mean for arbitrage

> verify: 1ms improvement reduces spreads by 0.8bp

> suggest links

> exit
```

**Cost per session:** ~$0.30-0.50
**Your time:** 3-4 hours writing (producing high-quality content)

---

### Friday: AI Finishing Work (Mostly Automated)
```bash
python3 run.py finalize --draft content/posts/tail-latency-arbitrage.md
```

**What AI does:**
1. Extracts claims from your draft
2. Runs evidence gate (verifies every claim has source)
3. Checks for risky content
4. Generates/updates frontmatter
5. Suggests internal links to evergreen hubs
6. Creates social media drafts
7. Saves claim table JSON

**If evidence gate fails:**
- AI flags specific problematic claims
- You fix them and re-run
- Much faster than full rewrite

**Cost:** ~$0.30
**Your time:** 15-30 min to fix any flagged issues

---

### Weekend: Review + Publish
- Review draft + artifacts
- Commit and push to GitHub
- Create PR
- Merge → Cloudflare Pages auto-deploys

**Cost:** $0
**Your time:** 15 min

---

## Installation

### 1. Install Dependencies

```bash
# Install Hugo
brew install hugo

# Install Python dependencies
pip3 install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env
```

### 3. Test Installation

```bash
# Make run.py executable
chmod +x run.py

# Test CLI
python3 run.py --help
```

---

## Commands Reference

### Research Prep
```bash
# Monday: Prepare research for writing
python3 run.py research --topic "impact of jitter on arbitrage" --days 7
```

**Options:**
- `--topic`: Research angle/topic to focus on (required)
- `--days`: How many days of intake to analyze (default: 7)
- `--min-sources`: Minimum relevant sources needed (default: 10)

**Output:**
- `data/research/YYYY-MM-DD-topic-slug.json` - Research summary
- `data/research/YYYY-MM-DD-topic-slug.html` - HTML preview

---

### Interactive Assistant
```bash
# Tuesday-Thursday: Get help while writing
python3 run.py assist --research data/research/2026-02-24-jitter.json
```

**Commands in assistant:**
- `find source: <query>` - Find source from research corpus
- `draft: <section description>` - Draft a section
- `verify: <claim>` - Verify claim against sources
- `suggest links` - Suggest evergreen hub links
- `help` - Show commands
- `exit` - Exit assistant

---

### Finalize Draft
```bash
# Friday: Finalize and prepare for PR
python3 run.py finalize --draft content/posts/my-post.md
```

**Options:**
- `--draft`: Path to draft Markdown file (required)
- `--skip-gate`: Skip evidence gate (not recommended)
- `--no-pr`: Don't create PR automatically

**Output:**
- Updated draft with frontmatter
- `data/claims/my-post.json` - Claim table
- `data/social/my-post.json` - Social media drafts

---

### Evidence Gate (Standalone)
```bash
# Run evidence gate on any draft
python3 run.py gate --draft content/posts/my-post.md
```

**What it checks:**
- Every claim has a credible source
- Claims aren't overstated vs evidence
- No venue-specific exploitation guidance
- No undefined technical terms (TODO: cross-reference glossary)

**Gate fails if:**
- Key claims lack credible sources
- Claim is overstated relative to evidence
- Risky content detected

---

### Daily Intake (Automated)
```bash
# Fetch and process sources (runs via GitHub Actions)
python3 run.py intake
```

**Status:** Placeholder (not yet implemented)
**TODO:**
- Add RSS feed parser
- Add web scraping for key sources
- Add LLM-based brief generation
- Add deduplication

---

## Directory Structure

```
ternqed/
├── content/              # Hugo content
│   ├── posts/           # Flagship essays
│   ├── digests/         # Weekly roundups
│   ├── evergreen/       # Updated-over-time hubs
│   ├── glossary/        # Term definitions
│   └── logs/            # Working notes
├── data/                # Agent-generated data
│   ├── intake/          # Daily intake briefs
│   ├── briefs/          # Processed briefs
│   ├── research/        # Research summaries
│   ├── claims/          # Claim tables
│   ├── hypotheses/      # Hypothesis registry
│   └── social/          # Social media drafts
├── agents/              # AI agent code
│   ├── prompts/         # Prompt templates
│   ├── configs/         # Agent configurations
│   ├── research_prep.py # Monday automation
│   ├── assistant.py     # Interactive helper
│   ├── finalize.py      # Friday automation
│   ├── evidence_gate.py # Hard blocker
│   └── intake.py        # Daily automation
├── layouts/             # Hugo templates (frozen)
├── static/              # Static assets
└── run.py               # Main CLI orchestrator
```

---

## Cost Breakdown

**Monthly costs with human-in-the-loop model:**

| Task | Frequency | Cost/Run | Monthly Total |
|------|-----------|----------|---------------|
| Research prep | 4x/month | $0.50 | $2 |
| Writing assistance | 12 sessions | $0.40 | $5 |
| Finalization | 4x/month | $0.30 | $1.20 |
| Daily intake | 30x/month | $0.20 | $6 |
| Digests | 4x/month | $0.50 | $2 |
| **Total** | | | **~$16-20/month** |

**Cost optimization tips:**
1. Use prompt caching for repeated research context (50-70% savings)
2. Batch process intake weekly instead of daily
3. Use Haiku for simple tasks (5x cheaper than Sonnet)

---

## Frontmatter Schema

Every post must include:

```yaml
title: "Your Title Here"
date: 2026-02-21
description: "SEO-optimized description (150-170 chars)"
markets: ["equities", "crypto", "both"]
mechanisms: [1, 2, 4]  # 1=adverse selection, 2=inventory risk, 3=coordination cost,
                        # 4=arbitrage, 5=info asymmetry, 6=queue priority
latency_budget: ["propagation", "processing", "queuing", "jitter"]
mean_vs_tail: "tail"
status: "reference"  # reference | working-notes | speculation
confidence: "high"   # high | medium | low
sources:
  - https://example.com/source1
  - https://example.com/source2
```

---

## Next Steps

### To Start Writing:

1. **Create seed content** (3-5 posts manually to establish style/structure)
2. **Run research prep** for your first topic
3. **Write with AI assistance**
4. **Finalize and publish**

### To Configure:

1. Edit `config/sources.json` (TODO: create this file)
2. Add RSS feeds, domains to monitor
3. Set up GitHub Actions for daily intake
4. Configure Cloudflare Pages deployment

### To Extend:

- [ ] Implement RSS feed parser for intake
- [ ] Add web scraping for specific sources
- [ ] Build glossary cross-reference in evidence gate
- [ ] Add PR auto-creation
- [ ] Integrate social media APIs for auto-posting
- [ ] Add analytics feedback loop

---

## Development

```bash
# Run Hugo dev server
hugo server -D

# Test agents
python3 -m pytest tests/

# Format code
black agents/
```

---

## License

[Specify license]

---

## Support

Questions? Issues? Open a GitHub issue or contact [your-email@example.com]
