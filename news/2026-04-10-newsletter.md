# theba.sh — 2026-04-10

The AI industry is having a full identity crisis this week: OpenAI is bleeding executives ahead of its IPO while Anthropic is quietly eating its lunch, and somewhere in between, an AI agent pwned FreeBSD in four hours. If you're still writing code by hand, the discourse is coming for you.

---

## Headlines

### Anthropic Hits $30B ARR, Drops Claude Mythos — Too Dangerous to Ship
Anthropic is flexing hard ahead of OpenAI's IPO, announcing $30B ARR and previewing Claude Mythos — reportedly the first model since GPT-2 that the lab deemed too dangerous to release publicly. Project GlassWing details remain sparse, but the timing is surgical.
- $30B ARR puts Anthropic in serious revenue territory, not just valuation theater
- Claude Mythos joins GPT-2 in the "we built something and got scared" club — a very short list
- Project GlassWing appears to be a new internal safety/capability research initiative

**🔧 Dev Take:** "Anthropic is doing more damage to OpenAI's IPO roadshow than any competitor ever has with a product."

---

### OpenAI's Executive Bench Collapses Ahead of IPO
OpenAI's leadership is thinning out at the worst possible moment — right before it needs to convince public market investors it's a stable, governable company. The departures follow months of internal tension and restructuring drama.
- Multiple senior executives have exited in a compressed window pre-IPO
- Public market investors hate leadership instability more than almost anything else
- Florida AG is now probing OpenAI over alleged harms to minors and a possible link to the FSU shooting

**🔧 Dev Take:** "You can't IPO on vibes alone when your C-suite has a revolving door and a state AG is asking questions."

---

### AI Agent Hacks FreeBSD in Four Hours
An AI agent autonomously identified and exploited a vulnerability in FreeBSD in under four hours. This is no longer a theoretical threat surface — autonomous offensive security is here and it works.
- Four-hour full exploit cycle is well within operational attack windows
- No human in the loop for the discovery or exploitation chain
- Red teams and security engineers need to be modeling AI-assisted adversaries *now*

**🔧 Dev Take:** "If you're still threat-modeling for human attackers only, your security posture is already outdated."

---

### ChatGPT Gets a $100/Month Tier
OpenAI is launching a $100/month ChatGPT tier, targeting power users and professionals who've maxed out what the $20 plan offers. It's a revenue play, but also a signal about where the product ceiling is heading.
- Positions OpenAI between prosumer and enterprise pricing
- Likely bundles higher rate limits, priority access, and advanced model access
- Sets a new anchor price in the consumer AI market — expect competitors to respond

**🔧 Dev Take:** "Charging $100/month for a chat interface is bold when Claude and Gemini are one tab away."

---

### "The Era of Human Coding Is Over" — r/singularity Weighs In
The r/singularity thread is doing what it does, but the underlying conversation is worth tracking: developers are genuinely renegotiating what their jobs look like, not theoretically, but in day-to-day practice.
- Anecdotes range from "AI writes 90% of my PRs" to "I just review and redirect now"
- The role is shifting from implementation to specification and judgment
- Adjacent thread: "What my job feels like now" — the emotional reality is hitting people hard

**🔧 Dev Take:** "The era of *typing* code may be ending; the era of *understanding* code just got more important."

---

### Google Research: Collaborative Learning with LLMs
Google published work on "social learning" — LLMs learning from each other through collaborative interaction rather than purely from static datasets. Early research, but the architectural implications are real.
- Models sharing learned behaviors without direct weight transfer
- Could reduce fine-tuning costs for specialized domains
- Opens questions about emergent behavior in multi-agent learning environments

**🔧 Dev Take:** "Multi-agent training loops are the next frontier — watch this space closely, it'll matter for how you architect systems."

---

## Quick Hits

- **Iran strikes took down AWS in the Gulf** — regional cloud redundancy is a geopolitical problem now, not just an engineering one
- **DeepSeek V4 targeting Huawei chips** — the non-Nvidia inference stack is becoming a real, shipping reality
- **[GitHub] deepset-ai/haystack** (⭐24.8k) — context-engineered LLM pipelines with explicit control; worth a look if LangChain's abstractions are driving you nuts
- **[GitHub] mlflow/mlflow** (⭐25.3k) — agent and LLM observability is becoming table stakes; MLflow keeps expanding here
- **r/artificial: "When LLMs can do X, I'll be impressed"** — useful signal for calibrating where actual gaps still exist vs. hype
- **Anthropic acquired [undisclosed company]** — details truncated but the acquisition spree continues heading into H1 2026

---

*theba.sh — built for builders*