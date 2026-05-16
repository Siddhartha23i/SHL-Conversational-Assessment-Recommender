# Approach Document - SHL Conversational Assessment Recommender

**Candidate:** Ambaigari Siddhartha Reddy  
**Role:** AI Intern, SHL Labs  
**Submission:** Refined version

## Design Choices

The main problem is intent ambiguity. Hiring managers often describe a role in plain language instead of using catalog vocabulary, so a pure keyword or faceted search experience is not enough. I treated the task as a stateless conversational retrieval problem with a strict response contract:

1. clarify only when a critical gap remains,
2. retrieve grounded candidates from the SHL catalog,
3. let the LLM choose the next action from a constrained set,
4. return a strict shortlist object that the evaluator can score.

The system uses three layers:

- `Sentence-BERT` (`all-MiniLM-L6-v2`) to embed the catalog and user intent
- `FAISS IndexFlatIP` for fast cosine-style retrieval over the local catalog
- `Groq llama-3.3-70b-versatile` for conversational reasoning, refinement, comparison, and refusal decisions

This separation matters. Retrieval keeps the system grounded in real SHL catalog entries, while the LLM handles conversational judgment. The model never gets to invent recommendations outside the retrieved candidate set.

## Retrieval Setup

The raw catalog is first filtered to keep only in-scope individual SHL solutions and exclude packaged Job Solutions. Each remaining assessment is converted into a rich document string containing name, description, test types, job levels, duration, and delivery metadata. That fuller representation improves matching for vague prompts like "graduate analyst" or "plant safety hiring" that may not overlap directly with the assessment title.

At runtime, the query is built from the accumulated user turns rather than only the most recent sentence. The retriever returns the top 24 candidates, which gives the LLM enough grounded options without making the prompt unnecessarily large.

## Prompt Design

The LLM does not generate free-form recommendation objects. It receives:

- the full stateless conversation history,
- a compact summary of facts already established,
- the upcoming assistant turn number,
- the retrieved candidate list as structured JSON.

It must respond with JSON only:

`{action, reply, selected_names}`

The allowed actions are `clarify`, `recommend`, `refine`, `compare`, `confirm`, and `refuse`. Returned names are validated against the real catalog before the API response is created.

Two evaluator-facing prompt constraints are especially important:

- do not clarify once the assistant is near the turn cap,
- prefer a full top-10 shortlist whenever recommending.

## Agent Behavior

The agent supports the required behaviors from the PDF:

- `Clarify`: asks one focused question if the request is still too underspecified
- `Recommend`: returns a grounded top-10 shortlist
- `Refine`: updates the shortlist after new constraints
- `Compare`: answers from catalog data only and suppresses the shortlist for that turn
- `Refuse`: stays in scope and declines off-topic or prompt-injection requests

The assignment's biggest implementation detail is the turn limit. The evaluator counts total messages across both user and assistant turns. The agent therefore treats the conversation budget as 8 total messages and forces a shortlist by assistant turn 6 instead of continuing to clarify too long.

## What Changed During Refinement

Some early choices were weaker than they looked:

1. Using the entire scraped catalog without filtering was risky because it included packaged "Solution" entries that are outside the assignment scope.
2. Treating the turn cap as "8 user turns" was incorrect and could fail hard evaluator checks.
3. Letting the evaluator continue after a shortlist made the local score less faithful to SHL's replay behavior.
4. The original UI was visually strong but still carried extra surface noise for a recruiter-facing demo.

The refined version fixes those points by:

- filtering the catalog to 370 in-scope entries,
- rebuilding the cleaned catalog and FAISS index,
- aligning evaluation and runtime behavior to the 8-message total cap,
- returning an exact top-10 shortlist when recommendations are shown,
- simplifying the Streamlit UI into a cleaner presentation layer for demos.

## Evaluation Approach

I kept `Recall@10` as the main retrieval metric because it matches the assignment. The local evaluator now more closely mirrors SHL's description: replay the conversation statelessly, stop when the agent returns a shortlist, and respect the total-message cap. I did not rely on happy-path spot checks alone; the design was shaped around likely automated probes such as schema compliance, off-topic refusal, non-hallucination, and over-clarification near the turn limit.

## Tools Used

AI-assisted coding was used for scaffolding and iteration, but the final design choices were reviewed and refined manually. The main external services and libraries are Groq, Sentence-Transformers, FAISS, FastAPI, and Streamlit.
