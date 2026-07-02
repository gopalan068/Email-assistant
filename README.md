# AI-Powered Email Organizer & Newsletter Digest

## Problem Statement
Modern inboxes are overwhelmed with a mix of urgent messages, low-priority updates, promotional content, and newsletters — making it hard to quickly identify what actually needs attention. Manually sorting through this every day is time-consuming and leads to missed important emails or wasted time on irrelevant ones.

## Objective
Build a system that automatically:
1. Classifies incoming emails by **importance** (Urgent / Important / Low Priority)
2. Filters out **spam/promotional** content using a trained ML classifier
3. Detects **newsletters** and generates a concise, readable **2-minute summary digest** of each

## Approach

### 1. Spam Detection — Classical Machine Learning
- Dataset: Public spam datasets (e.g., SMS Spam Collection / Enron Spam Dataset from Hugging Face)
- Method: TF-IDF vectorization + Naive Bayes / Logistic Regression classifier
- Rationale: Spam is a stable, well-defined pattern-matching problem — a lightweight trained model is fast, cheap, and accurate, without needing an LLM call per email

### 2. Importance Classification — LLM-based
- A pre-filter using heuristics (known senders, reply history, sender domain patterns) narrows down ambiguous cases
- An LLM classifies remaining emails into importance categories using a structured prompt, returning structured JSON output (e.g., `{"importance": "high", "reason": "..."}`)

### 3. Newsletter Summarization — LLM-based
- Newsletters are detected via heuristics (sender patterns, "unsubscribe" footers, mailing list headers)
- Content is summarized into a ~2-minute read (~400-500 words) using an extractive-then-abstractive approach: key sentences are pulled first, then summarized, to reduce the risk of the AI inventing details not in the source

## Tech Stack
- **Language:** Python
- **ML:** scikit-learn (TF-IDF, Naive Bayes/Logistic Regression)
- **Gen AI:** LLM API (Claude/GPT) for classification and summarization
- **Data source:** Gmail API
- **Analysis/Storage:** pandas, simple JSON/local storage for tracking results

## System Architecture

```
Gmail Inbox
     |
     v
[Spam Filter: trained ML model]
     |
     v (not spam)
[Heuristic Pre-filter: newsletter or not?]
     |                          |
     v                          v
[LLM: Importance Classifier]  [LLM: Newsletter Summarizer]
     |                          |
     v                          v
     Sorted Inbox View     2-min Digest
```

## Planned Timeline

| Phase | Task |
|-------|------|
| 1 | Gmail API setup, fetch sample emails |
| 2 | Build & train spam classifier on public dataset |
| 3 | Build & test LLM importance classifier with structured output |
| 4 | Build & test newsletter summarizer |
| 5 | Integrate full pipeline, generate combined output |
| 6 | Test on real inbox, refine based on results |
| 7 | Prepare final report/demo |

## Expected Deliverables
- Working prototype pipeline (Python scripts/notebook)
- Sample sorted inbox output + newsletter digest
- Report analyzing classifier accuracy and summarization quality
- Discussion of design tradeoffs (why classical ML for spam, LLM for importance/summarization)

## Status
🔧 In development — this repository will be updated with code, results, and findings as the project progresses.
