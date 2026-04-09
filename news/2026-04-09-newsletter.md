# theba.sh — 2026-04-09

The open-source model ecosystem is moving faster than any one lab can keep up with, while OpenAI is quietly showing cracks despite sitting on nearly a trillion dollars in paper valuation. It's a weird week to be in AI.

---

## Headlines

### EXAONE-4.5-33B Drops from LGAI
LG's AI research arm quietly released EXAONE-4.5-33B on HuggingFace, adding another serious 33B contender to an already crowded weight class. Worth benchmarking if you're running inference at scale and tired of paying Anthropic invoices.
- 33B parameter open model from LG AI Research
- Available on HuggingFace under LGAI-EXAONE
- Joins a increasingly competitive open-weight tier alongside Qwen, Mistral, and friends
**🔧 Dev Take:** "The 33B tier is where the real open-source value war is being fought right now — pull it and run evals before assuming you need something bigger."

---

### The Vibes Are Off at OpenAI
Despite closing a staggering $122B round at an $852B post-money valuation, The Verge is reporting that internal morale and external perception at OpenAI are increasingly shaky. Money is not the same thing as stability, and the cracks are starting to show in public.
- $122B raise at $852B valuation — numbers that require serious squinting
- Internal culture and leadership continuity remain persistent concerns
- Competitors are shipping fast while OpenAI manages investor narratives
**🔧 Dev Take:** "A $852B valuation is a number that needs a product roadmap to match it — and right now that roadmap is anyone's guess."

---

### Gemma 4 Is a Genuine Leap
Google's Gemma 4 landed and by most accounts it's a meaningful improvement over Gemma 3 across the board — multimodal capability, reasoning, and efficiency. For teams running local or on-prem inference, this is the most compelling open-weight multimodal option Google has shipped yet.
- Dramatically better than Gemma 3 on multimodal benchmarks
- Strong small-model performance makes it practical for edge and on-device use
- Google appears to be taking the open-weights race seriously again
**🔧 Dev Take:** "Gemma 4 is the first Google open model that doesn't feel like a consolation prize — actually test it before defaulting to Llama."

---

### Google Research Publishes "Social Learning" for LLMs
Google Research dropped a paper on collaborative learning between LLMs — essentially exploring how models can share knowledge without sharing weights or raw training data. It's early-stage research but points toward a genuinely different paradigm for distributed model improvement.
- Models learn from each other via generated examples, not shared gradients
- Privacy-preserving approach — no raw data exchanged between models
- Potential implications for federated AI systems and multi-agent architectures
**🔧 Dev Take:** "This is the kind of research that sounds academic until suddenly it's the reason your fine-tuning pipeline works differently in two years."

---

### Anthropic's Week: Dangerous Models, $30B Revenue, Managed Agents
Per The Neuron's digest, Anthropic built a model internally that it deemed too dangerous to release, disclosed $30B in annualized revenue, and shipped a Managed Agents product. That's a lot of news to process from a single company in three days.
- A model was built and deliberately not released on safety grounds — rare public acknowledgment
- $30B revenue signals Anthropic has crossed into genuine enterprise scale
- Managed Agents is a direct play for the agentic workflow market
**🔧 Dev Take:** "Anthropic saying 'we built it and won't ship it' is either the most responsible thing in AI right now or the best PR move — probably both."

---

### Haystack Hits 24K Stars — AI Orchestration Is Infrastructure Now
Deepset's Haystack framework continues its climb, sitting at nearly 25K GitHub stars, positioning itself alongside LangChain and LlamaIndex as a serious choice for production LLM pipeline work. The emphasis on "context-engineered" pipelines is a deliberate signal about where the framework is headed.
- 24,775 stars and actively maintained by deepset
- Focus on modular pipelines and explicit agent workflow control
- Production-readiness is a first-class concern, not an afterthought
**🔧 Dev Take:** "If you're choosing an orchestration framework in 2026 and you haven't looked at Haystack, you're making the decision with incomplete information."

---

## Quick Hits

- **MLflow (25K★)** continues to be the unglamorous backbone of serious ML ops teams — if you're not using it for eval tracking, you're probably doing it worse
- **Meta shipped Muse Spark** — another generative media tool entering an already saturated creative AI market
- **Z.ai's GLM-5.1** is open-source and reportedly worth a look if you're tracking non-Western lab output
- **prompts.chat (158K★)** remains the most-starred prompt resource on GitHub, which says something about where most people are in their AI journey
- **OpenBB (65K★)** is becoming the default financial data layer for quant/AI agent workflows — relevant if you're building anything in fintech
- **PyTorch Lightning (31K★)** — if you're fine-tuning at scale and writing raw training loops, you're wasting time

---

*theba.sh — built for builders*