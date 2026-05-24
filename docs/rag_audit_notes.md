# RAG Corpus & Chunk Audit - Sprint 5

## Overview
A review was conducted on the current RAG document corpus, chunking pipeline, and retrieval behaviour to identify any major issues affecting retrieval quality, grounding, or response stability.

The audit focused on:
- Chunk quality
- Retrieval consistency
- Structured PDF handling
- Overlap behaviour
- Repetitive retrieval
- Navigation and routing separation
- Potential hallucination risks caused by noisy chunks

---

## Chunking Pipeline Review

Current chunking implementation:
- Sentence-based chunking using NLTK sentence tokenization
- Fallback line-based splitting for structured PDF documents
- Chunk size: 80 words
- Overlap: 20 words

### Findings
- Chunk boundaries were generally coherent and readable
- Context continuity was maintained effectively through overlap
- Structured campus documents (directories, FAQs, service lists) were handled reasonably well
- No major chunk corruption or severe sentence fragmentation was observed

---

## Retrieval Behaviour Review

Representative queries were tested across:
- Student services
- Accommodation
- Accessibility support
- Wellbeing services
- Library information
- International student support
- Campus facilities
- Navigation-related queries

### Findings
- Retrieval remained relevant across most tested queries
- Responses were generally grounded in retrieved document content
- Navigation queries continued to route correctly to the dedicated navigation system
- No major retrieval pollution or irrelevant chunk injection was identified
- Confidence threshold adjustments improved the separation between low, medium, and high confidence retrieval results

---

## Minor Observations

### Overlap Repetition
Some responses contained small amounts of repeated or highly similar information due to overlap-based chunking. The repetition was minor and did not significantly affect response quality.

Example:
- Smoking zone responses occasionally repeated nearby grid-related location information across chunks.

### Structured PDF Metadata
Certain highly structured PDF documents occasionally produced small metadata fragments in responses due to table-style PDF extraction and line-based chunk fallback behaviour.

Examples:
- The Chisholm College response surfaced table-style accommodation metadata such as:
  - "Male, Female, No No No"

These fragments appeared to originate from structured accommodation tables within the source PDFs rather than meaningful natural-language content.

The occurrences were infrequent and did not significantly affect the overall usability or grounding quality of the system.

### Grid References
Location-related documents may still surface grid references in relevant answers. Current prompt refinements reduced unnecessary grid-heavy responses while preserving useful navigation context.

Examples:
- Accommodation-related answers included concise grid references such as:
  - "Chisholm College (Grid I10)"
  - "Glenn College (Grid K8, J8)"
- Smoking zone queries appropriately returned designated campus grid references for navigation relevance.

### Partial Information Responses
Some queries retrieved only partial contextual information from the corpus. In these situations, the system avoided hallucinating unsupported details and instead responded conservatively.

Example:
- The Digital Innovation Hub query correctly identified the location and classification of the space, while clearly stating that additional service details were not available in the retrieved context.

---

## Navigation Routing Validation

Additional testing confirmed that navigation-related queries continued to bypass the RAG pipeline correctly and were routed to the dedicated structured campus navigation system.

Example:
- Query:
  - "How do I get to HS?"
- Result:
  - The system correctly used the navigation database flow and returned step-by-step directional instructions without interfering with the RAG retrieval process.

This confirmed that Sprint 5 RAG refinements and threshold adjustments did not negatively affect the navigation subsystem.

---

## Conclusion

No critical corpus, chunking, or retrieval issues were identified during the Sprint 5 audit.

The current RAG pipeline was determined to be stable and appropriate for the project’s campus-assistant use case. No ingestion, embedding, or chunking changes were required at this stage.

The audit confirmed:
- Stable retrieval behaviour
- Coherent chunk generation
- Appropriate navigation separation
- Controlled hallucination behaviour
- Improved confidence calibration
- Reliable document-grounded responses across representative campus queries