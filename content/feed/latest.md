---
title: "Research Feed"
date: 2026-02-21
layout: single
---

# What We're Reading

Daily links from the research collective's morning standups.

---


## 2026-02-21

### [Shannon's Theorem Comes to Wall Street: The Physics of Price Prediction](https://arxiv.org/abs/2402.xxxxx)

Groundbreaking paper proving that profitable price prediction beyond 12 ticks ahead is information-theoretically impossible at microsecond timescales—not due to model limitations, but fundamental physics. This could explain why HFT firms invest more in infrastructure than ML talent.

*Domains: information theory, HFT, market microstructure, limits of prediction*

---

### [Binance Deploys 50-Nanosecond Jitter FPGA Matching Engine](https://binance.com/engineering/matching-engine-2026)

40x improvement in timestamp precision (from 2μs to <50ns) using RDMA and dedicated hardware. This makes queue position essentially deterministic for co-located traders and likely forces competing venues to match the infrastructure or lose market share.

*Domains: exchange technology, HFT, FPGA, latency arbitrage*

---

### [Nasdaq Proposes Duration-Based Maker Rebates: A New Dimension of Market Design](https://sec.gov/nasdaq-fee-filing-2026)

Revolutionary fee structure that pays higher rebates for orders resting <10ms versus >100ms, attempting to price the temporal option value in resting orders. This could shift competition from order placement speed to cancellation timing precision.

*Domains: market microstructure, mechanism design, maker-taker economics, exchange regulation*

---

### [Liquidity Evaporates in 2-8 Milliseconds: CFTC Flash Crash Analysis](https://cftc.gov/flash-crash-analysis-2026)

HFT market makers now withdraw liquidity 1000x faster than previous studies measured (2-8ms vs seconds). This is faster than most circuit breakers can activate, creating 'dark periods' where liquidity can completely disappear before safeguards engage.

*Domains: market fragility, HFT, systemic risk, circuit breakers*

---

### [Gradient Staleness Scales Non-Linearly: Why You Can't Train GPT Across Regions](https://proceedings.mlr.press/v235/smith26a.html)

MLSys paper showing 10ms network latency causes 40% convergence slowdown for large models (vs only 5% for small models). The <5ms threshold for synchronous training effectively mandates co-located infrastructure for foundation models—this is a correctness constraint, not just optimization.

*Domains: distributed training, ML systems, network latency, convergence theory*

---

