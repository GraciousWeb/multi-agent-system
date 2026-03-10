# import asyncio

# from graph import app
# from schema import Market


# async def run_intel_squad(query: str, market: Market):
#     initial_state = {
#         "query": query,
#         "target_market": market,
#         "raw_research_notes": [],
#         "iteration_count": 0,
#         "is_satisfactory": False,
#         "follow_up_queries": [],
#         "final_brief": None,
#         "human_verdict": None,
#         "human_feedback": None,
#     }

#     print("\nSTARTING GLOBAL FINTECH INTEL SQUAD")
#     print(f"Target Market: {market}")
#     print(f"Query: {query}")
#     print("=" * 60)

#     config = {"configurable": {"thread_id": "intel-session-1"}}

#     current_state = initial_state

#     while True:
#         interrupted = False

#         async for event in app.astream(current_state, config=config, stream_mode="updates"):

#             if "__interrupt__" in event:
#                 interrupted = True
#                 interrupt_data = event["__interrupt__"][0].value

#                 print("\n⏸ HUMAN REVIEW REQUIRED")
#                 print(f"Message:   {interrupt_data.get('message')}")
#                 print(f"Iteration: {interrupt_data.get('iteration')}")
#                 print("\nSkeptic Notes:")
#                 for note in (interrupt_data.get("skeptic_notes") or []):
#                     print(f"  - {note}")

#                 human_feedback = input(
#                     "\nEnter your feedback (approve / reject / comments): "
#                 ).strip()

#                 human_verdict = human_feedback.split()[0].lower() if human_feedback else "reject"

#                 if human_verdict == "approve":
#                      pass 
#                 elif human_verdict == "reject":
#                      pass 
#                 else:
#                     human_verdict = "comment"

#                 app.update_state(
#                     config,
#                     {
#                         "human_verdict": human_verdict,
#                         "human_feedback": human_feedback,
#                         "follow_up_queries": [human_feedback] if human_verdict in ["reject", "comment"] else [],
#                     },
#                     as_node="human_review"
#                 )
#                 break

#             for node_name, output in event.items():
#                 print(f"\n--- Node: {node_name.upper()} ---")

#                 if node_name == "scout":
#                     print(f"Scout found {len(output.get('raw_research_notes', []))} new pieces of intel.")

#                 elif node_name == "skeptic":
#                     status = "PASS" if output.get("is_satisfactory") else "FAIL"
#                     print(f"Audit Result: {status}")
#                     if not output.get("is_satisfactory"):
#                         print(f"Follow-up needed: {output.get('follow_up_queries')}")

#                 elif node_name == "writer":
#                     brief = output.get("final_brief")
#                     print("\n✨ FINAL INTELLIGENCE BRIEF ✨")
#                     print(f"Headline:         {brief.headline}")
#                     print(f"Confidence Score: {brief.confidence_score * 10:.1f}/10")
#                     print(f"\nRegulatory Radar:")
#                     for item in brief.regulatory_radar:
#                         print(f"  - {item}")
#                     print(f"\nTop Stories ({len(brief.top_stories)}):")
#                     for story in brief.top_stories:
#                         print(f"  [{story.category}] {story.company_name}")
#                         print(f"  Summary: {story.summary}")
#                         print(f"  Impact:  {story.impact_score}/10")
#                         if story.funding_amount:
#                             print(f"  Funding: {story.funding_amount}")
#                         if story.source_url:
#                             print(f"  Source:  {story.source_url}")
#                     print(f"\nSkeptic Notes:")
#                     for note in brief.skeptic_notes:
#                         print(f"  - {note}")
#                     print("=" * 60)

#         if not interrupted:
#             break

#         current_state = None


# if __name__ == "__main__":
#     test_query = "Latest on Moniepoint's 2026 expansion and new CBN agent banking rules."
#     asyncio.run(run_intel_squad(test_query, "NG"))