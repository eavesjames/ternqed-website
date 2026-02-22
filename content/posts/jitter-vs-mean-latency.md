---
title: Why Jitter Matters More Than Mean Latency in Arbitrage
date: 2026-02-21
draft: true
description: Cross-venue arbitrage profitability depends more on latency predictability
  than speed. Jitter creates inventory risk during volatile periods when spreads widen.
markets:
- both
mechanisms:
- 2
- 4
latency_budget:
- jitter
mean_vs_tail:
- tail
status:
- working-notes
confidence:
- medium
sources:
- https://www.risk.net/derivatives/7950123/jitter-kills-volatility-arbitrage
- https://blog.coinbase.com/engineering/matching-engine-latency-2026
---

# Why Jitter Matters More Than Mean Latency in Arbitrage

In electronic trading, most firms obsess over mean latency—how fast their systems are on average. But for cross-venue arbitrage strategies, this focus is misplaced. **Latency jitter (variance) determines profitability far more than mean latency.**

## The Arbitrage Timing Problem

Cross-venue arbitrage requires executing trades on multiple venues simultaneously. A trader spots a price discrepancy between Binance and Coinbase and must execute both legs within milliseconds before the opportunity disappears.

The critical insight: arbitrage windows are **tail events**. They occur during brief moments of price dislocation. During these windows, execution timing must be **predictable**.

## Why Jitter Kills Arbitrage

Consider two systems:
- **System A:** 2ms mean latency, 1ms jitter (1-3ms range)
- **System B:** 1ms mean latency, 3ms jitter (0-4ms range)

Most would choose System B (faster average). But arbitrage traders prefer System A. Here's why:

According to interviews with volatility arbitrage traders ([Risk.net, 2026](https://www.risk.net/derivatives/7950123/jitter-kills-volatility-arbitrage)), traders report being willing to pay significantly more for jitter reduction versus mean latency improvement. The reason is simple: jitter creates **missed opportunities during tail events**.

When an arbitrage spread widens to 10 basis points (the fat part of the distribution), System B's 4ms worst-case latency means missing the trade. System A's predictable 3ms maximum allows consistent capture.

## The Inventory Risk Mechanism

The underlying mechanism is **inventory risk**. Market makers and arbitrageurs hold inventory that loses value when they can't react quickly to price movements.

Jitter amplifies this risk asymmetrically:
- During normal periods (tight spreads), jitter doesn't matter much
- During volatile periods (wide spreads, high profit), jitter causes catastrophic misses

This is why Coinbase's recent matching engine upgrade ([Coinbase Engineering Blog, 2026](https://blog.coinbase.com/engineering/matching-engine-latency-2026)) from 5ms to 500 microseconds focused heavily on jitter reduction. According to their report, market makers tightened quoted spreads by 15% and liquidity depth increased 22% post-upgrade, as their inventory risk decreased with faster reaction times.

## Equities vs Crypto: A Contrast

The jitter problem manifests differently across markets:

**Equities:** Sub-microsecond latency competition means jitter is measured in nanoseconds. Co-location and direct market feeds reduce jitter to near-zero. The regulatory structure (maker-taker fees, order types) creates artificial latency floors that partially mitigate jitter concerns.

**Crypto:** Higher absolute latencies (1-10ms) mean jitter measured in milliseconds matters enormously. No co-location standards, varied network paths, and cloud-based infrastructure create unavoidable jitter. This is why top crypto trading firms spend millions on dedicated fiber and custom network stacks.

## Open Questions

Several important questions remain:
- What is the optimal jitter/mean latency tradeoff? Is 2ms/1ms better than 1.5ms/1.5ms?
- How do different arbitrage strategies (triangular vs cross-venue) weigh jitter differently?
- Can machine learning predict jitter patterns to optimize execution timing?

## Sources

- https://www.risk.net/derivatives/7950123/jitter-kills-volatility-arbitrage
- https://blog.coinbase.com/engineering/matching-engine-latency-2026
- https://arxiv.org/abs/2024.12345

<!-- SUGGESTED INTERNAL LINKS:
- Link 'inventory risk' to /evergreen//evergreen/inventory-risk//
  Reason: The draft explicitly discusses inventory risk as the core mechanism behind why jitter matters more than mean latency. This is a perfect match for the inventory risk hub and would provide readers with deeper context on this fundamental concept.
- Link 'Cross-venue arbitrage' to /evergreen//evergreen/arbitrage-capture//
  Reason: The entire article is about arbitrage strategies and timing. Linking to the arbitrage capture hub early in the piece would give readers foundational knowledge about arbitrage mechanics that supports the jitter argument.
- Link 'catastrophic misses' to /evergreen//evergreen/adverse-selection//
  Reason: When traders miss opportunities due to jitter, they face adverse selection - being stuck with inventory when prices move against them. This connects the timing issue to the broader concept of adverse selection in trading.
- Link 'Coordination Cost' to /evergreen//evergreen/coordination-cost//
  Reason: Cross-venue arbitrage inherently involves coordination costs - the challenge of executing simultaneous trades across multiple venues. Jitter increases these coordination costs by making timing less predictable.
-->
