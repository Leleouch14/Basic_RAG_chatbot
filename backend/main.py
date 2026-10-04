import os
from vectorstore import collection
from retrival import retrieve_context
from prompt import SYSTEM_TEMPLATE
from llm import generate_answer

def choose_source():
    all_metadata = collection.get(include=["metadatas"])["metadatas"]
    sources = sorted(set(m["source"] for m in all_metadata))

    if not sources:
        print("No PDFs ingested yet.")
        return None

    print("\nAvailable PDFs:")
    for i, name in enumerate(sources, start=1):
        print(f"  {i}. {name}")

    choice = input("Pick a number: ").strip()
    try:
        return sources[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice, defaulting to first PDF.")
        return sources[0]

def main():
    print("RAG Backend loaded. Type 'exit' to quit.")
    source_filename = choose_source()
    if source_filename is None:
        return

    while True:
        question = input("\n[You]: ")
        if question.lower() in ['exit', 'quit']:
            break

        context_data = retrieve_context(question, source_filename=source_filename)

        if context_data is None:
            print("\n[Assistant]: I couldn't find this in your uploaded materials.")
            continue

        context_text = "\n\n".join([doc for doc, meta, dist in context_data])
        prompt = SYSTEM_TEMPLATE.format(context=context_text, question=question)

        answer = generate_answer(prompt)

        print(f"\n{answer}")

        print("\n[Sources]:")
        for doc, meta, dist in context_data:
            print(f"- {meta.get('source', 'Unknown')} (Page {meta.get('page', 'N/A')}) | Distance: {dist:.4f}")

if __name__ == "__main__":
    main()