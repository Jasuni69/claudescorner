---
title: "Most of your AI requests don't need a frontier model. Here's how I cut my spend."
source: "https://old.reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/"
author:
  - "[[stosssik]]"
published: 2026-04-14
created: 2026-04-15
description: "I've seen people spend $1000+ a month on AI agents, sending everything to Opus or GPT-5.4. I use agents daily for GTM (content, Reddit/Twitt"
tags:
  - "clippings"
---
I've seen people spend $1000+ a month on AI agents, sending everything to Opus or GPT-5.4. I use agents daily for GTM (content, Reddit/Twitter monitoring, morning signal aggregation) and for coding. At some point I looked at my usage and realized most of my requests were simple stuff that a 4B model could handle.

Three things fixed it for me easily.

**1\. Local models for the routine work.** Classification, summarization, embeddings, text extraction. A Qwen 3.5 or Gemma 4 running locally handles this fine. You don't need to hit the cloud for "is this message a question or just ok". If you're on Apple Silicon, Ollama gets you running in minutes. And if you happen to have an Nvidia RTX GPU lying around, even an older one, LM Studio works great too.

**2\. Route everything through tiers.** I built Manifest, an open-source router. You set up tiers by difficulty or by task (simple, standard, complex, reasoning, coding) and assign models to each. Simple task goes to a local model or a cheap one. Complex coding goes to a frontier. Each tier has fallbacks, so if a model is rate-limited or down, the next one picks it up automatically.

**3\. Plug in the subscriptions you're already paying for.** I have GitHub Copilot, MiniMax, and Z.ai. With Manifest I just connected them directly. The router picks the lightest model that can handle each request, so I consume less from each subscription and I hit rate limits way later, or never. And if I do hit a limit on one provider, the fallback routes to another. Nothing gets stuck. I stopped paying for API access on top of subscriptions I was already paying for.

**4\. My current config:**

- Simple: gemma3:4b (local) / fallback: GLM-4.5-Air (Z.ai)
- Standard: gemma3:27b (local) / fallback: MiniMax-M2.7 (MiniMax)
- Complex: gpt-5.2-codex (GitHub Copilot) / fallback: GLM-5 (Z.ai)
- Reasoning: GLM-5.1 (Z.ai) / fallback: MiniMax-M2.7-highspeed (MiniMax)
- Coding: gpt-5.3-codex (GitHub Copilot) / fallback: devstral-small-2:24b (local)

**5\. What it actually costs me per month:**

- Z ai subscription: ~$18/mo
- MiniMax subscription: ~$8/mo
- GitHub Copilot: ~$10/mo
- Local models on my Mac Mini ($600 one-time)
- Manifest.build: free, runs locally or on cloud

I'm building Manifest for the community, os if this resonates with you, give it a try and tell me what you think. I would be happy to hear yoru feedback.

---

## Comments

> **Melodic\_Ad865** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6ez4z/) · 2 points
> 
> Noiceeeeee
> 
> > **stosssik** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6gxvy/) · 1 point
> > 
> > 😊 Thank you. If you try it, give us feedback 🙏
> > 
> > > **Melodic\_Ad865** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6hgvf/) · 1 point
> > > 
> > > Have you tried gemma4 Models?
> > > 
> > > > **stosssik** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6ig2s/) · 2 points
> > > > 
> > > > this one: [https://www.reddit.com/r/LocalLLaMA/comments/1sb9f4g/gemma\_4\_is\_fine\_great\_even/?tl=fr](https://www.reddit.com/r/LocalLLaMA/comments/1sb9f4g/gemma_4_is_fine_great_even/?tl=fr)
> > > > 
> > > > > **Melodic\_Ad865** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6kwkt/) · 1 point
> > > > > 
> > > > > Thanks for the answer. Nice setup you got. How do you manage all the skills and tool usage?
> > > > > 
> > > > > > **stosssik** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6ozpd/) · 1 point
> > > > > > 
> > > > > > Manifest looks at what's in each request, the message, the tools attached, the context, and automatically picks the right tier. (coding, emailing, complex, simple, reasongin, etc...)
> > > 
> > > > **stosssik** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og6ieoy/) · 1 point
> > > > 
> > > > Not enough, I read an interesting discussion on it recently

> **Space-Trash-666** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og8bkdr/) · 2 points
> 
> Well thought out. Will try.
> 
> > **stosssik** · [2026-04-15](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/oga4jqh/) · 1 point
> > 
> > Thank you [u/Space-Trash-666](https://old.reddit.com/u/Space-Trash-666)   . I am also looking for feedback from beta users. If you try it and are interested to give your feedback during a chat session, it would help a lot :)

> **bumkinas** · [2026-04-14](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/og7zp9i/) · 2 points
> 
> I would love open source functionality for something like manifest. I try to do it manually and it's just clunky.
> 
> > **stosssik** · [2026-04-15](https://reddit.com/r/clawdbot/comments/1slf9uj/most_of_your_ai_requests_dont_need_a_frontier/oga7zy2/) · 1 point
> > 
> > Manifest is open source. - [https://github.com/mnfst/manifest](https://github.com/mnfst/manifest)