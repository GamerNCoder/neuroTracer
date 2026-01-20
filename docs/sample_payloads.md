# Sample API Payloads and Responses

## Score Text Endpoint

### Request

```bash
POST /api/v1/score
Content-Type: application/json
```

```json
{
  "text": "I've been thinking about this problem for a while now. Maybe there's a different approach we could take? It seems like the current solution isn't quite working, but perhaps I'm missing something. Let me reconsider...",
  "options": {
    "include_breakdown": true,
    "include_heatmap": false
  }
}
```

### Response (Success)

```json
{
  "humanscore": 0.7234,
  "breakdown": {
    "drift": 0.5000,
    "cadence": 0.6543,
    "hedging": 0.7500,
    "metaphor": 0.5000,
    "coherence": 0.5000,
    "stylometry": 0.5000
  },
  "metadata": {
    "sentence_count": 4,
    "token_count": 45,
    "char_count": 187
  }
}
```

### Response (Error)

```json
{
  "detail": "Scoring failed: Text too short (minimum 10 characters required)"
}
```

## Example: Human-Written Text

**Input:**
```
I'm not entirely sure about this, but I think we might want to reconsider our approach. 
The thing is, when I look at the data, something feels off. Maybe it's just me, but 
there's this nagging feeling that we're missing something important. Let me think 
through this again...
```

**Expected Output:**
- High `humanscore` (0.7-0.9)
- High `hedging` score (lots of uncertainty markers)
- Moderate `cadence` (varied sentence lengths)
- Some `drift` (thought process visible)

## Example: AI-Generated Text

**Input:**
```
The implementation of this solution requires careful consideration of multiple factors. 
First, we must analyze the core requirements. Second, we should evaluate potential 
approaches. Finally, we will select the most appropriate method based on our analysis.
```

**Expected Output:**
- Lower `humanscore` (0.2-0.4)
- Low `hedging` score (minimal uncertainty)
- Low `cadence` variance (uniform structure)
- Low `drift` (linear progression)

## Example: Hybrid Text

**Input:**
```
I've been working on this problem for weeks. The implementation requires careful 
consideration. Maybe I'm overthinking it, but I think we need to look at this 
differently. The solution should address all requirements systematically.
```

**Expected Output:**
- Moderate `humanscore` (0.4-0.6)
- Mixed signals across markers
- `hybrid_index` would indicate segments

