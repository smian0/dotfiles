# RSS Intelligence Platform Evolution Roadmap

**Generated**: 2025-11-14
**Status**: Planning complete, ready for Phase 1 implementation
**Planning Method**: Zen planner with deepseek-v3.1 + gemini-2.5-pro models

---

## EXECUTIVE SUMMARY

**Current State**: 35-40% of Palantir quality ("Tier 2 brain with Tier 4 data")
**Target State**: 60-72% of Palantir quality at 99% cost reduction
**Timeline**: 12 weeks, 4 sequential phases
**Risk Level**: Medium-High (30% chance Phase 1 requires pivot)

**Quality Progression**:
```
Current   Phase 1   Phase 2   Phase 3   Phase 4   Target
  35%  →   42%   →   65%   →   75%   →   80%   → 60-72%
```

**Critical Blocker**: Phase 1 analysis fails at 202,752 token limit with 204 articles (error: "prompt too long, limit is 202752 tokens")

**Market Opportunity**:
- Cost: $0 vs $30k-100k/year commercial platforms (99% cost reduction)
- Quality: 60-72% of Palantir (sufficient for small organizations)
- Sweet Spot: Organizations needing intelligence but unable to afford enterprise solutions

---

## PHASE 1: FIX CONTEXT LIMIT BLOCKER

**Duration**: 1-2 weeks
**Quality Impact**: +7-10% (35% → 42-45%)
**Dependencies**: None (critical path - blocks all other phases)

**Problem**: Single intelligence_agent.arun() call at line 1568 receives full formatted articles (204 articles × ~1000 tokens = 204k tokens) which exceeds glm-4.6:cloud's 202,752 token limit.

**Solution**: Map-reduce chunking pattern
1. Map phase: Split 204 articles into chunks of 40-50 articles (5 chunks)
2. Reduce phase: Synthesize chunk analyses into final intelligence brief

**Engineering Tasks**:

**Task 1.1**: Design chunking strategy (2-3 days)
- Implement article chunking logic (40-50 articles per chunk)
- Design overlap strategy for cross-chunk entity tracking
- Create chunk metadata for temporal ordering (newer articles in later chunks)
- Success criteria: Chunking logic tested with 500 article simulation

**Task 1.2**: Implement map-reduce intelligence analysis (3-4 days)
- Refactor `analyze_knowledge_graph()` into map-reduce workflow
- Create chunk analyzer agent (processes 40-50 articles)
- Create synthesis agent (combines 5 chunk analyses into final brief)
- Success criteria: Map-reduce completes with 204 articles, zero errors

**Task 1.3**: Validation and quality testing (2-3 days)
- Compare single-pass vs map-reduce output quality on 100 articles
- Test with progressively larger article counts (204 → 300 → 500)
- Measure execution time overhead (target: <10 min total)
- Success criteria: Intelligence quality maintains 35%+, execution time <10 min

**Testing Strategy**:
- Unit tests: Chunking logic edge cases (49, 50, 51 articles per chunk)
- Integration tests: Full map-reduce with 100, 250, 500 articles
- Quality tests: A/B comparison of single-pass vs map-reduce output (human evaluation)
- Performance tests: Execution time benchmarks (target: <10 min for 500 articles)
- Acceptance criteria: Zero context limit errors, quality maintained at 35%+

**Critical Risk**: Map-reduce breaks analytical coherence (30% probability)
- Impact: Quality drops below 30%, invalidates entire approach
- Detection: A/B testing Week 2, human evaluation
- Mitigation: Build proof-of-concept first (Days 1-3), explicit entity/theme tracking between chunks
- Contingency: Pivot to paid models (gemini-2.5-pro 1M context, +$50-100/month cost)

---

## PHASE 2: DATA INFRASTRUCTURE EXPANSION

**Duration**: 2-4 weeks
**Quality Impact**: +20% (45% → 65%)
**Dependencies**: Phase 1 must be complete and proven with 500+ articles

**Problem**: Single source (4 Guardian RSS feeds) creates information silo, limits cross-source validation, caps quality at ~45%.

**Solution**: Expand from 4 to 20+ RSS sources across news, financial, technical, and geopolitical domains with geographic and political diversity.

**Engineering Tasks**:

**Task 2.1**: RSS source discovery and validation (1 week)
- Research and catalog 30+ candidate RSS feeds across:
  - News: Reuters, AP, Bloomberg, NYT, BBC, Al Jazeera, SCMP
  - Financial: FT, WSJ, MarketWatch, Seeking Alpha
  - Technical: TechCrunch, Ars Technica, The Verge, Hacker News
  - Geopolitical: Foreign Affairs, Diplomat, Defense One
- Validate RSS quality (well-formed XML, consistent updates, full content)
- Assess source credibility (editorial standards, fact-checking, corrections policy)
- Test rate limits and access restrictions
- Success criteria: 25+ validated sources with credibility scores

**Task 2.2**: Cross-source entity resolution (1-1.5 weeks)
- Implement entity deduplication across sources (same person/org different names)
- Design fuzzy matching for entity names ("Pres. Biden" = "President Biden" = "Joe Biden")
- Add entity disambiguation (distinguish multiple "John Smith" entities)
- Integrate with Graphiti for unified entity graph
- Success criteria: >90% entity resolution accuracy on test dataset

**Task 2.3**: Multi-source integration and testing (1-1.5 weeks)
- Integrate 20+ sources into existing RSS fetch workflow
- Implement source diversity tracking (geographic, political, domain)
- Add source attribution to all extracted entities/relationships
- Test with full 20-source load (expect 500-1000 articles per cycle)
- Validate Phase 1 map-reduce handles increased volume
- Success criteria: Zero context limit errors with 1000 articles, source diversity >0.7

**Testing Strategy**:
- Source validation tests: All 20 sources produce valid RSS (automated daily checks)
- Entity resolution tests: Test dataset with known entity duplicates (>90% accuracy)
- Diversity tests: Geographic, political, domain diversity metrics (>0.7 target)
- Load tests: 1000 articles per cycle without failures
- Acceptance criteria: Zero context limit errors with 1000 articles, quality reaches 65%

**Critical Risk**: Can't find 20 high-quality sources (25% probability)
- Impact: Quality caps at 55-60% instead of 65%
- Detection: Source validation testing Week 3-4
- Mitigation: Start source research during Phase 1 (parallel work), accept 12-15 sources if quality maintained
- Contingency: Adjust quality target to 55-60%, still competitive vs $30k platforms

**Medium Risk**: Entity resolution accuracy below 70% (35% probability)
- Impact: Knowledge graph has duplicate entities, intelligence analysis confused
- Detection: Automated testing Week 5
- Mitigation: Start with exact match only, defer fuzzy matching to Phase 3, use LLM for disambiguation
- Contingency: Simplify to exact match, document known limitation

---

## PHASE 3: PRODUCTION FEATURES - ANALYTICAL ENHANCEMENTS

**Duration**: 1-3 weeks
**Quality Impact**: +10% (65% → 75%)
**Dependencies**: Phase 2 multi-source data must be operational

**Problem**: System lacks production-grade features for trust and transparency: no confidence scoring, no contradiction detection, incomplete source attribution.

**Solution**: Add metadata layer for confidence, contradictions, and source attribution to transform from prototype to production-ready intelligence platform.

**Engineering Tasks**:

**Task 3.1**: Confidence scoring system (3-5 days)
- Design confidence scoring model based on:
  - Source credibility (Reuters 0.95, random blog 0.3)
  - Cross-source confirmation (3+ sources = high confidence)
  - Temporal freshness (breaking news lower confidence)
  - Entity resolution quality (fuzzy match = lower confidence)
- Implement scoring algorithm integrated with Graphiti facts
- Add confidence thresholds to intelligence analysis (exclude <0.4 confidence facts)
- Success criteria: Confidence scores assigned to 100% of facts, human validation >80% accuracy

**Task 3.2**: Contradiction detection (4-6 days)
- Design contradiction detection using:
  - Semantic similarity for related claims (same entities, same time window)
  - LLM-based contradiction assessment (glm-4.6:cloud)
  - Temporal logic (newer claim may supersede older)
- Implement contradiction detection workflow step
- Add contradiction flagging to intelligence briefs
- Success criteria: Detect contradictions in test dataset (10 known contradictions), <20% false positive rate

**Task 3.3**: Enhanced source attribution (2-3 days)
- Extend existing attribution to track:
  - Original article URL for every fact
  - Source credibility score
  - Publication timestamp
  - Cross-source confirmation count
- Add attribution display to newsletters (footnotes with sources)
- Success criteria: 100% facts traceable to source articles

**Task 3.4**: Integration testing and quality validation (2-3 days)
- Test full pipeline with Phases 1-3 features
- Validate intelligence quality reaches 70-75% target
- Human evaluation of confidence scores and contradiction detection
- Performance benchmarking (should still complete in <15 minutes)
- Success criteria: Quality 70-75%, zero regressions from Phase 2

**Testing Strategy**:
- Confidence scoring tests: Human validation of confidence scores (>80% agreement)
- Contradiction detection tests: Known contradiction dataset (10+ examples, <20% false positives)
- Attribution tests: 100% facts traceable to source articles (automated verification)
- Regression tests: Phases 1-2 functionality unchanged
- Acceptance criteria: Quality reaches 75%, zero production-blocking bugs

**Critical Risk**: Contradiction detection false positives erode trust (15% probability)
- Impact: Users lose confidence in platform
- Detection: Automated testing Week 8
- Mitigation: Conservative thresholds, human review loop, performance profiling
- Contingency: Remove feature if >30% false positives, focus on source attribution only

---

## PHASE 4: PERFORMANCE OPTIMIZATION

**Duration**: 2-3 weeks
**Quality Impact**: +3-5% (75% → 78-80%)
**Dependencies**: Phases 1-3 must be stable and passing quality tests

**Problem**: Current 2-hour cycle time too slow for real-time intelligence and breaking news response. Need 5-10 minute cycles for production use.

**Solution**: Optimize through caching, concurrency, incremental updates, and workflow parallelization without sacrificing analytical quality.

**Engineering Tasks**:

**Task 4.1**: Caching strategy implementation (3-5 days)
- Implement multi-level caching:
  - RSS fetch cache (avoid re-fetching unchanged feeds)
  - Content extraction cache (reuse extracted content for 24 hours)
  - Entity extraction cache (reuse entities for unchanged articles)
  - Graphiti query cache (cache common search patterns)
- Add cache invalidation logic (time-based + content-hash based)
- Success criteria: 40-50% reduction in redundant processing

**Task 4.2**: Workflow concurrency optimization (4-6 days)
- Profile current workflow to identify sequential bottlenecks
- Parallelize independent workflow steps:
  - Entity/sentiment/topic extraction (already parallel via Agno)
  - Multiple RSS source fetching (parallel requests)
  - Map-reduce chunk processing (parallel chunk analysis)
- Add async/await patterns for I/O-bound operations
- Success criteria: 2-3x speedup in I/O-bound steps

**Task 4.3**: Incremental update architecture (5-7 days)
- Implement delta processing (only analyze new articles since last cycle)
- Design incremental knowledge graph updates (Graphiti append vs full rebuild)
- Add state management for tracking processed articles/entities
- Implement graceful degradation (full rebuild if delta fails)
- Success criteria: 10-minute cycles for incremental updates, 30-minute for full rebuild

**Task 4.4**: Performance monitoring and regression testing (2-3 days)
- Add performance instrumentation (timing each workflow step)
- Create performance regression test suite
- Set up alerting for performance degradation (>15 min cycles)
- Validate quality maintained at 75%+ with optimizations
- Success criteria: Consistent 5-10 minute cycles, zero quality regressions

**Testing Strategy**:
- Cache tests: Verify cache hit rates (>40% hit rate target)
- Concurrency tests: Race condition detection (stress testing with rapid cycles)
- Incremental update tests: Delta processing accuracy (compare vs full rebuild)
- Performance regression tests: Automated benchmarks for each commit
- Acceptance criteria: 5-10 minute cycles, quality maintained at 75%+

**Critical Risk**: Aggressive caching causes stale data (15% probability)
- Impact: Intelligence briefs contain outdated information
- Detection: Automated regression tests Week 11-12
- Mitigation: Conservative cache TTLs (6 hours for content, 1 hour for entities), thorough testing
- Contingency: Disable optimization if quality drops >3%, ship with 15-20 minute cycles

---

## ROLLOUT STRATEGY (PHASED DEPLOYMENT)

**Alpha Phase** (Week 6 - After Phase 2):
- Audience: Internal testing only (1-2 users)
- Features: Phases 1-2 (map-reduce + 20 sources)
- Cycles: Every 4 hours (conservative)
- Monitoring: Manual review of every intelligence brief
- Success criteria: 65% quality, zero critical bugs for 2 weeks

**Beta Phase** (Week 9 - After Phase 3):
- Audience: 5-10 early adopters (friendly users)
- Features: Phases 1-3 (add confidence scoring, contradictions)
- Cycles: Every 2 hours
- Monitoring: Automated metrics + weekly human review
- Success criteria: 75% quality, <5 minor bugs reported, positive user feedback

**Production Phase** (Week 12 - After Phase 4):
- Audience: Full deployment (unlimited users)
- Features: All phases (optimized performance)
- Cycles: Every 10 minutes (incremental), 30 minutes (full rebuild)
- Monitoring: Automated dashboard + alerting
- Success criteria: 78-80% quality, >99% uptime, <1% error rate

**Rollback Plan**:
- Each phase has tagged git release (v0.1-alpha, v0.2-beta, v1.0-prod)
- Can rollback to previous phase within 1 hour if critical issues
- Automated rollback triggers: Quality drop >10%, error rate >5%, uptime <95%

---

## IMMEDIATE NEXT STEPS (WEEK 1)

**Critical Action 1: Phase 1 Proof-of-Concept (Days 1-3)**
- Owner: Engineering lead
- Task: Create `rss_intelligence_workflow_mapreduce_poc.py`
- Scope: 
  - Implement basic 50-article chunking
  - Create map-reduce workflow with Agno
  - Test with synthetic 250-article dataset
- Decision Point: Day 3 - Proceed with full implementation or pivot to paid models?
- Files: Create new PoC file, don't modify production workflow yet

**Critical Action 2: RSS Source Research (Days 1-5, Parallel)**
- Owner: Engineering lead (or delegate to research assistant)
- Task: Create `docs/rss_sources_evaluation.csv`
- Scope:
  - Research 30+ candidate RSS feeds
  - Test each for quality, rate limits, content availability
  - Assign credibility scores
  - Document in spreadsheet
- Deliverable: Validated list of 25+ sources ready for Phase 2 integration

**Week 1 End Goal**:
By end of Week 1, should have:
1. Phase 1 PoC validated (proceed/pivot decision made)
2. 25+ RSS sources identified and validated
3. Complete plan documented in project memory
4. Week 2 tasks clearly defined based on PoC results

**Next Planning Checkpoint**: End of Week 2 (Phase 1 complete)
- Review: Did map-reduce maintain quality?
- Decide: Proceed to Phase 2 or adjust approach?
- Plan: Detailed Phase 2 source integration tasks

---

## SUCCESS METRICS DASHBOARD

**Intelligence Quality Score** (0-100%, target: 60-72%)
- Measured via human evaluation of intelligence briefs
- Comparative analysis vs Palantir/commercial platform outputs

**Cycle Execution Time** (target: 5-10 minutes)
- Incremental updates: 5-10 minutes
- Full rebuild: 30 minutes maximum

**Article Processing Volume** (target: 1000+ per cycle)
- Across 20+ diverse sources
- Zero context limit errors

**Source Diversity** (target: >0.7)
- Geographic diversity (US, Europe, Asia, Middle East)
- Political diversity (left, center, right)
- Domain diversity (news, financial, technical, geopolitical)

**System Uptime** (target: >99%)
- Continuous operation without critical failures

**Error Rate** (target: <1% of cycles)
- Zero critical bugs
- Minor bugs resolved within 1 week

---

## RESOURCE REQUIREMENTS

**Engineering Resources**:
- 1 senior engineer (full-time for 12 weeks)
- Skills: Agno workflows, RSS parsing, entity resolution, performance optimization

**Data Resources**:
- Curated list of 30+ high-quality RSS feeds
- Source credibility dataset (Reuters reliability > random blog)
- Test dataset with known contradictions for Phase 3 validation

**Infrastructure**:
- Ollama cloud models (free): glm-4.6:cloud, deepseek-v3.1:671b-cloud
- Optional paid fallback: gemini-2.5-pro ($50-100/month if Phase 1 pivot required)
- Graphiti knowledge graph (already integrated)

**Monitoring/Observability**:
- Automated performance instrumentation
- Quality metrics dashboard
- Alerting for performance degradation or quality drops

---

## RISK SUMMARY

**HIGH RISK**: Phase 1 Map-Reduce Breaks Analytical Coherence (30% probability)
- Mitigation: Build PoC first, explicit entity tracking
- Contingency: Pivot to paid models (+$50-100/month)

**MEDIUM RISK**: Can't Find 20 High-Quality RSS Sources (25% probability)
- Mitigation: Start research early, accept 12-15 sources
- Contingency: Adjust quality target to 55-60%

**MEDIUM RISK**: Entity Resolution Accuracy Below 70% (35% probability)
- Mitigation: Start with exact match, use LLM disambiguation
- Contingency: Simplify to exact match, document limitation

**LOW-MEDIUM RISK**: Performance Optimization Breaks Quality (15% probability)
- Mitigation: Conservative cache TTLs, thorough testing
- Contingency: Ship with 15-20 minute cycles

---

**Last Updated**: 2025-11-14
**Next Review**: End of Week 2 (Phase 1 checkpoint)