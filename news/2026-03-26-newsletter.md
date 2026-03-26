# theba.sh — 2026-03-26

The AI industry is simultaneously hitting walls and tearing them down: safety researchers are sounding alarms about fundamental model failures while the market keeps consolidating, pivoting, and shipping anyway. Today's dispatch covers the cracks forming under the hood and what that means if you're building on top of any of this.

---

## Headlines

### ARC-AGI-3 Launches — Every Frontier Model Scores Under 1%
The newest benchmark from the ARC Prize team dropped today, and it's a humbling moment: every major frontier model scores below 1%, suggesting the gap between "impressive demos" and genuine general reasoning remains enormous. If you've been skeptical of AGI timelines, print this one out.
- Designed to resist pattern-matching and benchmark overfitting
- Results hold across GPT, Claude, and Gemini-class models
- ARC-AGI-2 was already considered hard — this is a different category of hard

**🔧 Dev Take:** "Your AI assistant that 'codes better than most humans' can't score 1% on a reasoning test — calibrate accordingly."

---

### Internal Safety Collapse in Frontier LLMs (arXiv:2603.23509)
Researchers have identified a failure mode they're calling Internal Safety Collapse (ISC), where frontier LLMs break down on safety constraints under specific task conditions — not through jailbreaks, but through something deeper in the model's internals. This is the kind of paper that should be required reading before you ship anything user-facing.
- ISC is distinct from prompt injection or adversarial attacks — it's an emergent failure, not an exploit
- Affects models from multiple frontier labs
- Has implications for anyone using LLMs in high-trust or compliance-sensitive pipelines

**🔧 Dev Take:** "If your threat model only covers prompt injection, you're already behind — go read this paper."

---

### OpenAI Kills ChatGPT's Erotic Mode (And Other Side Quests)
OpenAI has abandoned its brief experiment with adult content generation in ChatGPT, the latest in a string of rapid pivots and quiet shutdowns this week. Between this and the Sora discontinuation, it's starting to look like the company is doing some aggressive portfolio pruning.
- Sora reportedly shut down in a move that surprised Disney, a known partner
- Pattern suggests OpenAI is refocusing hard on core products and enterprise
- Each killed project represents real developer integrations that now need to be unwound

**🔧 Dev Take:** "Building on OpenAI's experimental features is a liability, not a feature — stick to the stable APIs."

---

### Apple to Open Siri to Third-Party AI Chatbots in iOS 27
Apple is extending its ChatGPT handoff model to allow other third-party AI chatbots to integrate directly with Siri in iOS 27, per Bloomberg. This is a significant architectural shift — Apple is effectively turning Siri into a routing layer rather than the destination.
- Current ChatGPT integration is the template; expect Claude, Gemini to follow
- Opens a real distribution channel for AI apps on iOS
- Apple retains control over the handoff UX, which means they control the trust layer

**🔧 Dev Take:** "Siri as an AI router is actually a more defensible position than Siri as an AI — smart move, good news for builders."

---

### Google Gemini Gets Memory Import — The AI Portability Wars Heat Up
Following Anthropic's recent memory export tool for Claude, Google has rolled out "Import Memory" and "Import Chat History" features for Gemini on desktop. The race to make AI switching costs lower (while hoping you stay anyway) is officially on.
- Users can now migrate context from other AI assistants into Gemini
- Anthropic moved first this month; Google is responding fast
- This is the beginning of an interoperability pressure campaign across the whole industry

**🔧 Dev Take:** "AI memory portability is table stakes within 12 months — design your product's memory layer accordingly."

---

### Harvey Hits $11B Valuation — Vertical AI Is Where the Money Is Going
Legal AI platform Harvey has reached an $11B valuation, a signal that purpose-built vertical AI applications are capturing serious capital even as generalist AI hype cools. While horizontal AI platforms fight on margins, vertical players are locking in professional workflows.
- Kleiner Perkins also raised $3.5B, partly earmarked for vertical AI bets
- Legal, medical, and financial verticals continue to attract the largest rounds
- Harvey's trajectory validates the "AI that knows one domain cold" thesis

**🔧 Dev Take:** "The generalist AI wrapper is dead; the specialized AI workflow tool is where durable businesses are being built."

---

## Quick Hits

- **r/singularity declares the era of human coding over** — the discourse has arrived, the evidence is still debated, the vibes are immaculate
- **Sanders and AOC propose a data center construction ban** — the first serious legislative pushback on AI infrastructure buildout hits Congress
- **dev.to: AI Beyond the Hype** — solid grounded take: even if VC dries up and progress plateaus, AI as a productivity layer isn't going away
- **deepset-ai/haystack hits 24.6K stars** — the context-engineering and RAG pipeline framework keeps climbing; worth a look if you're building production LLM apps
- **mlflow/mlflow at 24.9K stars** — still the go-to for LLM evaluation and experiment tracking if you're running anything at scale
- **EYG goes open source on Lobste.rs** — low-key drop worth watching; community discussion is active

---

*theba.sh — built for builders*