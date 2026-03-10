from datetime import datetime
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import POLICIES
from state import AgentState
from tools import fintech_search, extract_full_content
from schema import CritiqueOutput, IntelligenceBrief
from langgraph.types import interrupt

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


def truncate_notes(notes: list, max_chars: int = 60000) -> str:
    """Join notes and truncate to stay within token limits."""
    combined = "\n\n".join(notes)
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[...truncated for length...]"
    return combined


async def scout_node(state: AgentState):
    query    = state.query or ""
    market   = state.target_market or "GLOBAL"
    followups = state.follow_up_queries or []

    search_queries = followups if followups else [query]

    if not search_queries:
        print("[WARN] Scout received zero search queries.")
        return {"raw_research_notes": state.raw_research_notes}

    print(f"Scout running {len(search_queries)} queries:")
    for q in search_queries:
        print(f"  → {q}")

    new_notes = []
    for q in search_queries:
        # Step 1 — search
        results = await fintech_search.ainvoke({
            "query":    q,
            "market":   market,
            "category": "general"
        })

        # Step 2 — extract full content from top 3 URLs
        try:
            urls = [r["url"] for r in results[:3] if isinstance(r, dict) and "url" in r]
            if urls:
                full_contents = await extract_full_content.ainvoke({"urls": urls})
                full_text = "\n\n".join(
                    f"[Full Article from {urls[i]}]:\n{content[:2000]}"
                    for i, content in enumerate(full_contents)
                    if content
                )
                new_notes.append(
                    f"Query: {q}\nSnippets: {results}\n\nFull Content:\n{full_text}"
                )
            else:
                new_notes.append(f"Query: {q}\nResults: {results}")
        except Exception as e:
            print(f"[WARN] Full content extraction failed: {e}")
            new_notes.append(f"Query: {q}\nResults: {results}")

    return {
        "raw_research_notes": state.raw_research_notes + new_notes,
        "iteration_count":    state.iteration_count + 1,
        "attempted_queries":  state.attempted_queries + search_queries,
    }


async def skeptic_node(state: AgentState):
    market = state.target_market or "GLOBAL"
    policy = POLICIES.get(market, POLICIES["GLOBAL"])
    print(f"Skeptic is auditing data against {market} Policy...")

    # Filter red flags based on query relevance
    query_lower = (state.query or "").lower()
    applicable_red_flags = []
    for flag, scoped_keywords in policy.red_flag_scope.items():
        if not scoped_keywords or any(kw in query_lower for kw in scoped_keywords):
            applicable_red_flags.append(flag)

    all_attempted = state.attempted_queries or []
    attempted_section = ""
    if all_attempted:
        attempted_section = f"""
QUERIES ALREADY ATTEMPTED (do NOT repeat these):
{chr(10).join(f"  {i+1}. {q}" for i, q in enumerate(all_attempted))}
"""

    red_flag_section = (
        f"APPLICABLE RED FLAGS FOR THIS QUERY: {', '.join(applicable_red_flags)}"
        if applicable_red_flags
        else "No red flags are applicable to this query type — do not penalise for their absence."
    )

    system_prompt = f"""
You are a Senior Fintech Compliance Analyst auditing research for the {market} market.

POLICY FOCUS: {', '.join(policy.focus)}
REQUIRED SOURCES: {', '.join(policy.required_sources)}
{red_flag_section}

{attempted_section}

STEP 1 — CLASSIFY THE QUERY:
Identify the query type: regulatory | funding | news | general | other
This determines which policy rules apply.

STEP 2 — EVALUATE THE RESEARCH:
Score the research from 1 to 10:
  9 to 10 = Complete, well-sourced, directly answers the query
  7 to 8  = Mostly complete, minor gaps not critical to the core answer
  5 to 6  = Partial — key facts missing
  1 to 4  = Insufficient — core question unanswered

ALWAYS populate skeptic_notes regardless of whether should_loop is True or False.
When research passes, skeptic_notes should contain:
  - What was verified and why it's trustworthy
  - Any minor caveats or limitations worth flagging to the human
  - Source quality observations
  - Anything the human should be aware of before approving

STEP 3 — DECIDE: should_loop?

Set should_loop = FALSE (pass to human) if ANY of these are true:
  ✓ quality_score >= 7
  ✓ The query is directly and clearly answered in the research
  ✓ This is iteration {state.iteration_count} and we've already tried {len(all_attempted)} queries
    (more iterations will not improve quality)

Set should_loop = TRUE only if ALL of these are true:
  ✗ quality_score < 7
  ✗ There is a CRITICAL gap — the core question cannot be answered without it
  ✗ The gap was NOT already searched (check attempted queries above)
  ✗ A differently-phrased query is likely to yield new information

DO NOT loop back for:
  - Missing secondary/peripheral details
  - Minor source inconsistencies on non-core facts
  - Red flags that don't apply to this query type
  - Perfectionism — 70%+ complete is good enough to pass to human

Return strict JSON per the schema.
""".strip()

    structured_llm = llm.with_structured_output(CritiqueOutput)
    research_content = truncate_notes(state.raw_research_notes)

    critique = await structured_llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
Original Query: {state.query}

Research Collected So Far:
{research_content}

Iteration: {state.iteration_count} of 3 | Queries attempted: {len(all_attempted)}
""")
    ])

    print(f"Audit Score: {critique.quality_score}/10 | Loop: {critique.should_loop}")
    if not critique.should_loop:
        print("  ✓ Satisfied — forwarding to human review.")
    else:
        print(f"  ↺ Follow-ups: {critique.follow_up_queries}")

    return {
        "is_satisfactory":   not critique.should_loop,
        "follow_up_queries": critique.follow_up_queries if critique.should_loop else [],
        "skeptic_notes":     critique.skeptic_notes,
    }


def human_review(state: AgentState):
    """
    Pauses execution and asks for human validation.
    update_state() writes human_verdict, human_feedback, and follow_up_queries
    directly to AgentState before resuming — no need to read interrupt() return value.
    """
    interrupt({
        "type":          "human_review",
        "query":         state.query,
        "market":        state.target_market,
        "skeptic_notes": state.skeptic_notes,
        "iteration":     state.iteration_count,
        "message":       "Please review the skeptic's output and enter feedback."
    })

    return {}


async def writer_node(state: AgentState):
    """
    The Writer: Formats verified data into the final professional brief.
    """
    print("Synthesizer is drafting the final Intelligence Brief...")

    system_prompt = f"""
You are a world-class Financial Journalist. Create a structured Fintech Intelligence Brief.
Target Market: {state.target_market}
Current Date: {datetime.now().strftime('%Y-%m-%d')}

STRICT RULES:
- Only include stories that DIRECTLY answer the original query: {state.query}
- If a source does not directly answer the query, exclude it entirely.
- Do not infer or generalize — only report what is explicitly in the research.

Use the verified research to fill the required schema. Highlight Red Flags found by the Analyst.
""".strip()

    structured_llm = llm.with_structured_output(IntelligenceBrief)
    research_content = truncate_notes(state.raw_research_notes)

    final_report = await structured_llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Original Query: {state.query}\n\nFinal Verified Research:\n{research_content}")
    ])

    return {"final_brief": final_report}