# theba.sh — 2026-04-07

The AI industry is colliding with geopolitics in real time, and the cracks are showing everywhere — from executive suites to data centers in the Gulf. Meanwhile, the models keep shipping and the "is coding dead" discourse refuses to die.

---

## Headlines

### Iran Strikes Target U.S. AI Infrastructure — AWS Goes Dark in the Gulf
Iran followed through on threats against Stargate-linked data centers, and the collateral damage hit AWS infrastructure across the Gulf region. This is no longer a hypothetical risk for teams with regional deployments.
- AWS Gulf regions experienced outages tied to the strikes
- Iran explicitly named U.S.-linked AI data centers as targets
- Stargate's centralized infrastructure model is now a geopolitical liability
**🔧 Dev Take:** "Your multi-region DR plan just became a geopolitical requirement, not a nice-to-have."

---

### OpenAI's Executive Bench Collapses Ahead of IPO
Multiple senior departures hit OpenAI right as it's trying to stick the landing on what would be one of the biggest tech IPOs in years. The timing is brutal.
- Leadership instability at exactly the wrong moment for investor confidence
- Pattern continues a long string of high-profile exits from the company
- IPO timeline and valuation expectations now under serious scrutiny
**🔧 Dev Take:** "Building on a platform whose leadership is in freefall is a dependency risk, full stop."

---

### Gemma 4 Drops — Google's Best Small Multimodal Model Yet
Google shipped Gemma 4 and it's a meaningful jump over Gemma 3 across the board — multimodal capability, performance, and efficiency. Small open models are getting genuinely competitive.
- Dramatically better than Gemma 3 on multimodal benchmarks
- Runs at a size range that's practical for self-hosted and edge deployments
- Puts real pressure on the "just use the API" default for common workloads
**🔧 Dev Take:** "If you haven't re-evaluated open weights in the last 90 days, Gemma 4 is your reason to do it now."

---

### An AI Agent Hacked FreeBSD in Four Hours
An autonomous AI agent compromised a FreeBSD system in under four hours — no human in the loop. This is the kind of benchmark that matters more than any leaderboard score.
- Demonstrates agentic capability has crossed into meaningful offensive security territory
- Raises the floor on what "autonomous agent risk" actually looks like in practice
- Red teams and security orgs need to be running drills against AI-assisted attacks now
**🔧 Dev Take:** "If an agent can root FreeBSD in four hours, your threat model from 2024 is already obsolete."

---

### Anthropic Hits $30B in Revenue
Anthropic crossed $30 billion in revenue, a number that reframes the entire "when does this become a real business" conversation. The enterprise Claude adoption story is accelerating hard.
- $30B revenue puts Anthropic firmly in tier-one infrastructure territory
- Comes alongside an acquisition (details still emerging) that signals aggressive expansion
- DeepSeek V4 on Huawei chips in the same week — the competitive pressure isn't letting up
**🔧 Dev Take:** "At $30B, Anthropic isn't a research lab with a product anymore — architect your integrations accordingly."

---

### Lobste.rs: LLMs and the Enshittification Thesis
A Lobste.rs thread is making the rounds arguing that LLMs represent the pinnacle of enshittification — the idea that the product degrades the more it scales and monetizes. The comments are worth reading.
- Core argument: optimization for engagement and revenue corrupts model utility over time
- Counter-arguments focus on open weights as a structural escape valve
- Underlying tension between "AI as tool" and "AI as platform" is real and worth sitting with
**🔧 Dev Take:** "The enshittification risk is real — it's why your stack should have an exit path from any single model provider."

---

## Quick Hits

- **"The era of human coding is over"** trending on r/singularity again — the discourse is recursive at this point, but the agentic coding benchmarks backing it are less easy to dismiss
- **DeepSeek V4** confirmed running on Huawei chips — the hardware decoupling story for non-U.S. AI is moving faster than most expected
- **Haystack** (deepset-ai) trending on GitHub at 24.7k stars — solid pick if you're building production RAG or agent pipelines and want explicit control over your architecture
- **MLflow** at 25.1k stars and still the default for teams who need agent + LLM observability without vendor lock-in — worth a look if you're not already tracking evals
- **MIT Tech Review** flags gig workers training humanoid robots — the data labeling economy is quietly pivoting to physical-world AI training
- **Better AI benchmarks** piece from MIT is worth a skim — current evals are garbage and smarter people are finally trying to fix it
- **dev.to take on AI as collaborator** is soft, but the underlying point about using models for brainstorming rather than just codegen is one practitioners actually report working

---

*theba.sh — built for builders*