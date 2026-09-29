import os
from retrival import retrieve_context
from prompt import SYSTEM_TEMPLATE
from llm import generate_answer

def main():
    print("RAG Backend loaded. Type 'exit' to quit.")
    
    while True:
        question = input("\n[You]: ")
        if question.lower() in ['exit', 'quit']:
            break
            
        context_data = retrieve_context(question)
        
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