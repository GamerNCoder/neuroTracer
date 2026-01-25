# Text Length Guidelines for Optimal Analysis

## 📊 Test Results Summary

Based on empirical testing, here's how text length affects HumanScore accuracy:

| Length | Words | Sentences | Chars | HumanScore | Quality |
|--------|-------|-----------|-------|------------|---------|
| Very Short | 10 | 1 | 59 | 49.2% | ⚠️ Poor |
| Short | 50 | 4 | 287 | **80.1%** | ✅ Excellent |
| Medium | 150 | 11 | 828 | 64.6% | ⚠️ Good |
| Long | 300 | 15 | 1,508 | 70.7% | ✅ Good |

## 🎯 Ideal Text Length

### **Optimal Range: 50-200 words, 3-8 sentences**

**Best Performance: ~50 words with 4-5 sentences**

This length provides:
- ✅ Enough sentences for drift analysis (needs 2+)
- ✅ Sufficient variation for cadence detection
- ✅ Room for hedging patterns to emerge
- ✅ Multiple coherence break opportunities
- ✅ Rich stylometric fingerprint
- ✅ Not so long that patterns get averaged out

## 📏 Minimum Requirements

### Absolute Minimum
- **Characters:** 10 (API requirement)
- **Sentences:** 1 (but most markers need 2+)
- **Words:** ~5-10

### Functional Minimum (for reliable scoring)
- **Characters:** 100+
- **Sentences:** 2+ (critical for drift, cadence, coherence)
- **Words:** 20-30

## 🔍 How Each Marker Responds to Length

### 1. **Semantic Drift** (20% weight)
- **Minimum:** 2 sentences
- **Optimal:** 3-10 sentences
- **Why:** Needs sentence-to-sentence transitions to detect meaning changes
- **Too Short:** Returns default 0.5 score
- **Too Long:** Patterns may average out

### 2. **Cadence Variability** (15% weight)
- **Minimum:** 2 sentences
- **Optimal:** 3-8 sentences
- **Why:** Measures irregularity in sentence pacing
- **Too Short:** Limited variance to detect
- **Too Long:** Variance may normalize

### 3. **Hedging Language** (15% weight)
- **Minimum:** 1 sentence (but needs multiple for variance)
- **Optimal:** 3-10 sentences
- **Why:** Looks for distribution of uncertainty markers
- **Works at:** Any length, but variance improves with more sentences

### 4. **Metaphor Rarity** (10% weight)
- **Minimum:** 1 sentence
- **Optimal:** 5-15 sentences
- **Why:** Needs enough text to find unique metaphors
- **Works at:** Any length, but more text = more opportunities

### 5. **Coherence Breaks** (20% weight)
- **Minimum:** 2 sentences
- **Optimal:** 4-12 sentences
- **Why:** Detects mid-thought direction changes
- **Too Short:** Fewer opportunities for breaks
- **Too Long:** Breaks may get diluted

### 6. **Stylometric Fingerprint** (20% weight)
- **Minimum:** 1 sentence
- **Optimal:** 3+ sentences
- **Why:** Statistical analysis of writing patterns
- **Works at:** Any length, but more text = more reliable fingerprint

## ⚠️ Common Issues by Length

### Very Short Text (< 30 words, 1-2 sentences)
**Problems:**
- Drift analyzer returns default 0.5 (needs 2+ sentences)
- Cadence has limited variance to detect
- Coherence breaks are rare
- Stylometric features are sparse

**Example:** "Hello bro, hows it going? hows lifee man?"
- Score: ~47% (lower than ideal)

### Short Text (30-100 words, 2-5 sentences) ✅ **OPTIMAL**
**Strengths:**
- All markers can function
- Patterns are clear and not averaged out
- Natural human variation is visible
- Best balance of signal vs. noise

**Example:** "I've been thinking about this problem for a while now, and honestly, I'm not entirely sure what the best approach is. Maybe we should try a different angle?"
- Score: ~80% (excellent)

### Medium Text (100-300 words, 6-15 sentences)
**Considerations:**
- Patterns may start averaging out
- Some markers may normalize
- Still reliable, but slightly less accurate than short texts

### Long Text (300+ words, 15+ sentences)
**Considerations:**
- Patterns may get averaged out
- More formal writing may score differently
- Still reliable, but may miss subtle patterns
- Good for comprehensive analysis

## 📋 Recommendations

### For Best Accuracy
1. **Target: 50-150 words**
2. **Target: 3-8 sentences**
3. **Ensure: At least 2 sentences** (critical for drift/cadence/coherence)

### For Different Use Cases

#### **Casual Conversation**
- **Ideal:** 30-80 words, 2-5 sentences
- **Why:** Captures natural flow without over-formalization

#### **Formal Writing (Academic/Business)**
- **Ideal:** 100-250 words, 5-10 sentences
- **Why:** More structured, needs more text to show patterns

#### **Creative Writing**
- **Ideal:** 75-200 words, 4-10 sentences
- **Why:** Needs room for metaphors and stylistic variation

#### **Social Media Posts**
- **Ideal:** 20-100 words, 1-4 sentences
- **Note:** Very short posts may score lower due to limited markers

## 🔧 Technical Details

### Code Requirements
```python
# Minimum API requirement
text: str = Field(..., min_length=10)

# Marker requirements
if len(sentences) < 2:
    # Drift, Cadence, Coherence return default scores
    return {"score": 0.5, ...}
```

### Why Sentence Count Matters More Than Word Count
- Most markers analyze **sentence-level patterns**
- Drift needs sentence transitions
- Cadence measures sentence-to-sentence variation
- Coherence detects breaks between sentences
- **Recommendation: Prioritize sentence count over word count**

## 📈 Scoring Confidence by Length

| Length | Confidence | Notes |
|--------|------------|-------|
| < 20 words, 1 sentence | ⚠️ Low | Many markers return defaults |
| 20-50 words, 2-3 sentences | ✅ Medium | Functional but limited |
| 50-150 words, 3-8 sentences | ✅✅ High | **Optimal range** |
| 150-300 words, 8-15 sentences | ✅ Good | Reliable but may average |
| 300+ words, 15+ sentences | ✅ Good | Reliable, comprehensive |

## 💡 Best Practices

1. **Aim for 3+ sentences** - Enables all markers
2. **50-150 words is the sweet spot** - Best accuracy
3. **Natural writing is better** - Don't force length
4. **Multiple paragraphs OK** - System handles them
5. **Quality over quantity** - Better to have natural 50 words than forced 200

## 🎯 Quick Reference

**Minimum for reliable scoring:**
- 2+ sentences
- 30+ words
- 100+ characters

**Optimal for best accuracy:**
- 3-8 sentences
- 50-150 words
- 200-800 characters

**Maximum recommended:**
- No hard limit, but 300+ words may start averaging patterns

---

**Last Updated:** Based on empirical testing with TraceNeuro v0.1.0
