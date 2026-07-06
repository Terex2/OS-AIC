from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
import operator
import asyncio

# استيراد الخدمات الجديدة
from agents.web_infiltrator import WebInfiltrator
from services.rag_service import RAGService

# تعريف حالة الوكيل
class AgentState(TypedDict):
    query: str
    context: Annotated[List[str], operator.add]
    web_content: str
    rag_results: List[dict]
    llm_response: str
    next_action: str

# تهيئة الخدمات
web_infiltrator = WebInfiltrator()
rag_service = RAGService()

async def initialize_services():
    await web_infiltrator.initialize_browser()

# العقدة 1: التخطيط الأولي
async def plan_action(state: AgentState):
    print("\n--- PLANNING INITIAL ACTION ---")
    query = state["query"]
    # منطق تخطيط أكثر تعقيداً هنا، يمكن أن يستخدم LLM لتحديد الخطوة التالية
    # بناءً على طبيعة الاستعلام، يقرر ما إذا كان يحتاج إلى بحث ويب أو RAG
    if "بحث" in query or "معلومات عن" in query or "ما هو" in query:
        next_action = "web_search"
    elif "ذاكرة" in query or "سابق" in query or "تذكر" in query:
        next_action = "rag_lookup"
    else:
        next_action = "llm_generate"
    print(f"Initial plan: {next_action}")
    return {"next_action": next_action}

# العقدة 2: البحث عبر الويب (Web Infiltrator)
async def perform_web_search(state: AgentState):
    print("\n--- PERFORMING WEB SEARCH ---")
    query = state["query"]
    # هنا يمكن استخدام LLM لتوليد استعلامات بحث أفضل أو تحديد URLs
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    web_content = await web_infiltrator.navigate_and_extract(search_url, "body")
    # يمكن هنا تحليل محتوى الويب بشكل أعمق وتلخيصه قبل إضافته للسياق
    print(f"Web content extracted (partial): {web_content[:100]}...")
    return {"web_content": web_content, "context": [f"Web Search Result: {web_content[:500]}..."]}

# العقدة 3: البحث في الذاكرة (RAG Lookup)
async def perform_rag_lookup(state: AgentState):
    print("\n--- PERFORMING RAG LOOKUP ---")
    query = state["query"]
    rag_results = rag_service.search_documents(query)
    context_from_rag = [res["text"] for res in rag_results]
    print(f"RAG results found: {len(context_from_rag)}")
    return {"rag_results": rag_results, "context": [f"RAG Context: {\n}.join(context_from_rag)"]}

# العقدة 4: توليد الاستجابة النهائية باستخدام LLM
async def generate_llm_response(state: AgentState):
    print("\n--- GENERATING LLM RESPONSE ---")
    full_context = "\n".join(state["context"])
    prompt = f"Based on the following context and query, provide a comprehensive answer:\n\nContext: {full_context}\n\nQuery: {state['query']}\n\nAnswer:"
    
    # استدعاء Ollama للحصول على استجابة ذكية
    ollama_url = "http://ollama:11434/api/generate"
    payload = {
        "model": "llama3",  # استخدام نموذج Llama 3 الذي تم تحميله
        "prompt": prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(ollama_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        result = response.json()
        llm_response = result["response"]
    except Exception as e:
        llm_response = f"Error communicating with Ollama: {e}"
    
    print(f"LLM Response (partial): {llm_response[:100]}...")
    return {"llm_response": llm_response}

# العقدة 5: إنهاء العملية
def finalize_response(state: AgentState):
    print("\n--- FINALIZING RESPONSE ---")
    return END

# بناء الرسم البياني (Graph)
workflow = StateGraph(AgentState)

workflow.add_node("plan_action", plan_action)
workflow.add_node("perform_web_search", perform_web_search)
workflow.add_node("perform_rag_lookup", perform_rag_lookup)
workflow.add_node("generate_llm_response", generate_llm_response)

workflow.set_entry_point("plan_action")

# تحديد المسارات الشرطية
workflow.add_conditional_edges(
    "plan_action",
    lambda state: state["next_action"],
    {
        "web_search": "perform_web_search",
        "rag_lookup": "perform_rag_lookup",
        "llm_generate": "generate_llm_response",
    },
)

workflow.add_edge("perform_web_search", "generate_llm_response")
workflow.add_edge("perform_rag_lookup", "generate_llm_response")
workflow.add_edge("generate_llm_response", END)

app = workflow.compile()

if __name__ == "__main__":
    async def run_test():
        await initialize_services()
        print("OS-AIC Orchestrator with Web Infiltrator and RAG initialized.")
        # Example 1: Web Search
        print("\n--- Testing Web Search ---")
        result_web = await app.ainvoke({"query": "ابحث عن أحدث أخبار الذكاء الاصطناعي"})
        print(f"Final Web Search Result: {result_web['llm_response']}")

        # Example 2: RAG Lookup (assuming some data is added to RAG service)
        rag_service.add_document("LangChain هو إطار عمل لتطوير تطبيقات تعتمد على نماذج اللغة الكبيرة.", {"source": "langchain_docs"})
        rag_service.add_document("Ollama يسمح بتشغيل نماذج اللغة الكبيرة محلياً.", {"source": "ollama_docs"})
        print("\n--- Testing RAG Lookup ---")
        result_rag = await app.ainvoke({"query": "تذكر لي معلومات عن Ollama"})
        print(f"Final RAG Result: {result_rag['llm_response']}")

        # Example 3: Direct LLM generation
        print("\n--- Testing Direct LLM ---")
        result_llm = await app.ainvoke({"query": "اكتب قصيدة قصيرة عن القمر"})
        print(f"Final LLM Result: {result_llm['llm_response']}")
        await web_infiltrator.close_browser()

    asyncio.run(run_test())
