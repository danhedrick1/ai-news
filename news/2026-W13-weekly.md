---

# theba.sh weekly - Mar 23 - Mar 29, 2026

*6 daily digests - one weekly signal pass*

---

## Week in One Screen

This was the week the gap between AI capability and AI deployment infrastructure became impossible to ignore. ARC-AGI-3 launched with sub-1% scores across every frontier model on the same day Reddit declared human coding dead. Sora got killed not because video AI failed but because OpenAI couldn't productize it fast enough. Cursor is self-improving Composer 2 every five hours. The throughline: the rate of model advancement has now outrun the surrounding systems — platform review, compute cost models, governance tooling, legal frameworks, and competitive roadmaps alike.

The second story is the convergence of agents, autonomy, and the security debt that comes with both. Claude outperforming Nicolas Carlini at smart contract exploitation ($3.7M in demonstrated exploits), AgentGuard launching as an open-source policy proxy, cryptographic RBAC discussions heating up, and "harness engineering" emerging as a named discipline — these aren't separate threads. They're the same thread. The industry gave agents real capabilities roughly 18 months before it built real governance for those capabilities, and the bill is arriving now.

---

## Biggest Shifts

### ARC-AGI-3 Sets a New Floor — And It's Very Low
Every frontier model scored under 1% on ARC-AGI-3 at launch. This isn't a benchmark controversy — it's a hard signal about the boundary between pattern-matching (which AI has largely won) and novel reasoning under distribution shift (which it still can't do reliably). Builders conflating the two will ship products that disappoint. The durable moats live in the gap between these two things.
- **Concrete takeaway:** Don't architect for "current best available model." Architect for a model that's better at task-specific reliability than at generalizing to novel problem shapes — because that's what you actually have.
- **Watch next:** Whether ARC-AGI-3 scores move materially in Q2, and which lab claims the first meaningful result above 5%.

**Source trail:** [Thu digest](https://thebash.dev/2026-03-26)

---

### Claude Mythos Leaks — The Capability Ladder Is Outrunning Public Releases
Anthropic shipped what Latent Space called its biggest launch ever, and a tier above Opus — codenamed Mythos — was already leaking by Friday. OpenAI killed Sora mid-cycle. Physical Intelligence is valued at $11B at age two. Frontier labs are running internal roadmaps 6-12 months ahead of public availability, and the gap is widening, not closing.
- **Concrete takeaway:** Any product strategy anchored to "the best publicly available model" is a strategy built for last quarter. Build with model routing and abstraction layers that let you swap backends without re-architecting.
- **Watch next:** Whether Anthropic officially announces Mythos before mid-Q2, and whether the capability jump is as large as the leaks suggest.

**Source trail:** [Fri digest](https://thebash.dev/2026-03-27), [Sat digest](https://thebash.dev/2026-03-28)

---

### Apple's Multi-AI Routing Layer Is the Biggest Distribution Story Nobody Is Covering
iOS 27 opens Siri to Claude, Gemini, and other backends — and the architecture appears to be genuine multi-model routing, not a preferred-partner swap. If Apple ships a real routing layer that invokes different models for different query types, it becomes the largest AI distribution channel on earth overnight, with no single lab controlling the relationship. Every lab optimizing to "be the default Siri backend" may have fundamentally misread Apple's strategy.
- **Concrete takeaway:** If your retention strategy depends on context lock-in inside any major platform, start rethinking it now. Memory portability is accelerating (Anthropic import tools, Google's Import Memory and Import Chat History, Apple's open routing) — stickiness from context accumulation is a depreciating asset.
- **Watch next:** iOS 27 beta API surface — specifically whether Apple exposes query routing logic to developers or keeps it opaque.

**Source trail:** [Thu digest](https://thebash.dev/2026-03-26), [Fri digest](https://thebash.dev/2026-03-27)

---

### The Agent Security Debt Is Now a Billing Item
Three separate signals landed this week: AgentGuard launching as an open-source policy engine and proxy, the "harness engineering" framing from NVIDIA's panel as a distinct discipline, and Nicolas Carlini publicly stating Claude outperformed him as a security researcher — with $3.7M in smart contract exploits as the receipt. The threat model has structurally changed. The adversary is now a senior security researcher with unlimited frontier model access and no ethical constraints.
- **Concrete takeaway:** Red-team your public-facing infrastructure against that specific adversary profile. Ask: what would a skilled attacker with unlimited Claude access find in 48 hours? If you don't know, you need to find out before someone else does.
- **Watch next:** YC S26 batch — expect a cluster of agent security and policy-enforcement startups. This is a real problem with enterprise budget attached, and the tooling gap is well-defined enough to build against.

**Source trail:** [Tue digest](https://thebash.dev/2026-03-24), [Sat digest](https://thebash.dev/2026-03-28), [Sun digest](https://thebash.dev/2026-03-29)

---

### Chinese Robotics Crossed a Manufacturing Threshold the West Isn't Tracking
Agibot hit 10,000 humanoid robots deployed — 5,000 units in the last 90 days. That's not a demo. That's a production ramp. The gap between "impressive robotics demo" and "manufacturing at scale" in Chinese robotics has closed in a way that hasn't registered in Western AI coverage. The question is no longer whether humanoid robots will be useful at scale. It's whether a Western supply chain for them exists before it's needed.
- **Concrete takeaway:** If you're building software for physical AI — warehouse automation, logistics, last-mile deployment tooling — the hardware availability timeline you're planning around is probably 12-18 months too conservative.
- **Watch next:** Whether any Western robotics manufacturer announces a comparable production milestone in Q2, and how US/EU industrial policy responds to the Agibot numbers.

**Source trail:** [Sat digest](https://thebash.dev/2026-03-28)

---

## Builder Board

- **AgentGuard** — Open-source policy engine and proxy for controlling what AI agents are permitted to do. If you're running agents with real access to APIs, secrets, or deploys, this is the most immediately actionable tool from the week. Evaluate it against your current agent permission model. [Reddit r/MachineLearning](https://www.reddit.com/r/MachineLearning/comments/1s2x252/p_agentguard_a_policy_engine_proxy_to_control/)

- **GigaChat open weights** — GigaChat-3.1-Ultra-702B and GigaChat-3.1-Lightning-10B-A1.8B are now available as open weights. The 10B-A1.8B MoE architecture is worth benchmarking for local inference use cases, especially if you're already evaluating Qwen or Mistral-class models. [Reddit r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1s2pkfw/new_open_weights_models_gigachat31ultra702b_and/)

- **OpenAI Teen Safety Tools** — Released open-source under their safety toolkit. If you're building any consumer-facing AI product, these tools are now a due-diligence item — both for genuine safety and for regulatory defensibility as platform liability rules tighten.

- **Gemini 3.1 Flash Live** — Lower latency, improved audio precision. If you're running real-time voice or multimodal pipelines, benchmark this against your current setup before your next architecture review. The latency delta on streaming audio tasks is reportedly meaningful.

- **Insilico/Lilly $2.75B deal structure** — Not a tool, but a template. The deal is structured around commercialization rights, not discovery milestones. That's a new model for AI-drug partnerships. If you're building in biotech or adjacent verticals, this is the contract structure your BD team needs to understand.

- **Cursor self-improving Composer 2** — Reported 5-hour self-improvement cycles on Composer 2. Treat this as a signal about where coding assistant capability ceilings are moving, not just a product feature. If your developer tooling roadmap assumes Cursor-class capability is stable for 6+ months, revisit that assumption.

- **ARC-AGI-3 benchmark** — Now the clearest public test of genuine reasoning vs. pattern-matching. Run your target model against it. The results will tell you more about where your product will fail in production than most capability benchmarks currently in use.

---

## What to Watch Next Week

Anthropic's Pentagon injunction win means federal AI procurement dynamics are live again — expect at least one major government AI contract announcement in the next 10 days as agencies recalibrate. The bigger watch, though, is iOS 27's developer preview and what Apple actually exposes in the multi-AI routing API surface. If builders get meaningful hooks into query routing, the competitive dynamics for every AI assistant product shift immediately; if Apple keeps the routing logic opaque, it becomes a toll road with no lane markings. Either outcome is important. Meanwhile, the Insilico/Lilly deal will either get replicated quickly — in which case AI drug platform valuations re-rate in Q2 — or it will sit as a one-off, which tells you something different about pharma's actual conviction on AI pipelines. Watch for the second deal. If it comes in the next 30 days, the re-rating is real.

---

*theba.sh weekly - built for builders*

---