# yet another local GPT with RAG

<!-- [![yet another local GPT with RAG](https://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D2ElivLWajzA)](https://www.youtube.com/watch?v=2ElivLWajzA) -->

## why i am building my own chatbot instead of using chatGPT? 

like many others on the internet, i tried my hands at building a simple chatbot with RAG powered by local LLMs. couple things irk me about ChatGPT:

1. lack of privacy. my prompts and additional contextual data are [stored by OpenAI](https://openai.com/policies/privacy-policy), dont like that, especially bc i want to ask personal, sensitive info (ex, health info)
2. arbitrary and lazy censorship. 
3. lack of customized data ingestion pipelines. ChatGPT's inability to directly consume my notion, slack, google drive, or any local folder makes it less personally useful
4. $240 a year and not open-source, esp given the abundance of free, open-source LLM models out there today. 

i implemented a basic chatbot that fulfills the inverses of all the above. with a local LLM, all the data is now stored on my computer and I can swap in uncensored models (i.e. nous-hermes-llama2). i also integrated various surfaces (like Notion, URLs, txts) using LlamaIndex's [readers](https://llamahub.ai/) and integrations. 

if i allow my imagination to extend further, the dream applicatiomn would have these additional features:

- infinite and persistent memory. [lots](https://twitter.com/sjwhitmore/status/1776718019437490386) of [teams](https://www.rewind.ai) are [thinking](https://openai.com/index/memory-and-new-controls-for-chatgpt) [about](https://www.wired.com/story/chatgpt-memory-openai/) this [problem](https://python.langchain.com/docs/modules/memory/).
- precise retrieval of relevant information from knowledge base
- contextual reasoning based on chat history
- data pipelines to notion, slack, directories, mail, or just about anything with API access
- perform actions within permission levels



## first...can i run a local LLM on MacBook? 

| Chipset Model    | Number of GPU | Number of CPU | RAM  | SSD   | Memory bandwidth |
| ---------------- | ------------- | ------------- | ---- | ----- | ---------------- |
| Apple M3 Pro GPU | 18-core       | 12-core       | 36GB | 500GB | 150GB/s          |

i was uncertain about whether my macbook can handle running LLMs locally: *aren't these models very computationally and data-intensive to run? how hard and slow will running my own llm be?* and damn, with llama.cpp, the results are insanely fast. 

- i can run llama3 (8-billion parameter model) at ~60 tokens/second, which is a [~200 character-request](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)/second. 
- i can run mixtral (47B parameter model) at ~ **? tokens/s.** 

tldr; llama.cpp makes local LLM possible on Mac and a variety of devices using integer quantization. quantization decrease the precision in model weights to drastically decrease the memory requirements of the LLM. specifically, llama.cpp uses the [ggml](https://ggml.ai/) library to quant model down from 16-bit float to 4-bit int, which reduces the memory requirement from [13GB to 3.9GB](https://github.com/ggerganov/llama.cpp?tab=readme-ov-file#memorydisk-requirements) for a 7B parameter model. the relationship between quantization and memory is mostly linear. finbarr provides a [much better examination](https://finbarr.ca/how-is-llama-cpp-possible/) of this magical process.

[ollama](https://ollama.com/) is a wrapper / front-end for llama.cpp that abstracts away the downloading of models, prompt formatting, etc. it is the easiest way to run local LLM. i can download and run a model with just `ollama run phi3 `.



## architecture

![rag architecture](/Users/winniex/code/wyx/posts/rag_arch.png)

the main components of this RAG chatbot were:

1. local LLM server (llama3), powered by Ollama
2. chatbot frontend, powered by Streamlit
3. data ingestion/storage/retrieval/synthesis, powered by LlamaIndex 
4. local embedding generation, powered by BAAI/bge-large-en-v1.5

i will highlight a couple of challenges that i encountered in this one-week sprint; those interested in the complete implementation, take a look at the code here. 

one note is that i chose llamaindex as the primary framework for this project. 

## what I did to get more relevant, accurate responses

to achieve precise retrieval across all historical knowledge bases means that i will eventually have to rely on multiple indices. however, i made the mistake of prioritizing improving routing between multiple indices instead of improving accurate retrieval within a single document. these are two entirely different engineering problems. 

first, when does one decide to use a single index versus multiple? these are some rules that ive come across that made some sense--separate two data sources into different indices if they 

- cover different topics. 
- require different indexing strategies. note: one could create both a summary and vector index over the same data collection! 
- vary counterproductively in styles, syntax, type of content. 
  - one example is if i want to learn about crypto markets; one source is an academic paper and the other is coinbase's investor report. their differences in tone, depth and style could cause confusion if they were blended together. by separating, we can use the academic paper to provide in-depth analysis and coinbase's investor report to provide real-time market updates to the user. 
  - another good example is academic papers vs user-generated content

### improving on single-index retrieval

now that we have established the primary importance of single-index retrieval, here are a couple things I tried to improve it. at the end of v0, i am actually walking away with more questions than answer. 

1. **initial data sanitization.** cleaning, pruning, and aggregation of source data is boring but high-impact work! having helpful metadata also goes a long way. 

2. **adjusting chunk size to be more granular (256 or 512)**. LlamaIndex's default chunk size is 1024. Chunk size surprisingly mattered a lot. Since most documents I want to provide are actually pretty short, a smaller chunk size was better at zooming into specific information. given how sensitive the efficacy is to chunk size, i provided the ability to specify chunk size and chunk overlap at data collection.

   - context-aware splitting is said to improve quality significantly--would love to try!
   - didnt experiment too much with chunk overlap. does it provide as much impact? 

3. **choosing a decent, generalist embedding model**. between the open-source, high-ranking, general-purpose models on this [leaderboard](https://huggingface.co/spaces/mteb/leaderboard), i didnt see too much improvements. 

4. **post-processing with rerankers.** reranker corrects the discrepancy between similarity and relevancy. i used `FlagEmbeddingReranker(model="BAAI/bge-reranker-large")` as the reranker, and the results were...underwhelming. ultimately, rerankers are bottlenecked by the relevancy of the nodes returned by embedding-based retrieval. in the below scenario, reranker wont be able to rank the right nodes because they were not provided in the first place. 

   > Prompt: what's the first sentence in metamorphosis
   >
   > Nodes retrieved: 
   >
   > - {score: 0.59, text: "“Gregor!” shouted his sister, glowering at him and shaking her fist.  That was the first word she had spoken to him directly since his  transformation."}
   > - {score: 0.57, text: "Gregor only needed to hear the visitor’s first words of greeting and he knew who it was—the chief clerk himself."}

   i might experiment with [these](https://www.llamaindex.ai/blog/boosting-rag-picking-the-best-embedding-reranker-models-42d079022e83) embedding models and rerankers in future iterations. 

5. **query transformations** through sub-queries or rewording. didn't implement, will try for next iteration. 

i am overall dissatisfied with the relevancy and accuracy of the chatbot's answer, especially when compared to ChatGPT. building an LLM application is performance engineering. high quality in response is achieved through the diligent, boring squeeze of each component within the response pipeline. 



### improving on multi-collection retrieval

Multi-collection retrieval builds on top of single-collection retrieval. I used a LlamaIndex's router retriever to select the index(es) from which to retrieve the relevant nodes. 

```python
def build_router_retriever(self, collections):
  tools = []
  for c in collections:
      index = self.load_collection(c.name)
      tool = RetrieverTool.from_defaults(retriever=index.as_retriever(similarity_top_k=5), 
                                         description=c.metadata["description"])
      tools.append(tool)

  router_retriever = RouterRetriever.from_defaults(
    retriever_tools=tools, 
    llm=self.llm, selector=LLMMultiSelector.from_defaults(llm=self.llm)) 
  return router_retriever

collections = self.db.list_collections()
custom_retriever = self.build_router_retriever(collections)
self.chat_engine = ContextChatEngine.from_defaults(
  retriever=custom_retriever, llm=self.llm, verbose=True, system_prompt=self.prompt)

```

under the hood, the router retriever uses the LLM selector module, which essentially stuffs the metadata of each index into the LLM and asks it to pick which index(es) to use. so the metadata really matters here! 

i focused on improving the router and multi-index retrieval prematurely. given how inaccurate the single-document retrieval is at the moment, router can be as effective as the underlying index retrieval. 



## what i will do in future iterations

### setup testing and evaluation

currently, i conduct testing using three sets of data:  kafka's metamorphosis, a short story generated by chatGPT, and a paper on Nouns DAO that i wrote in college. after feeding the context into the app, i provide the corresponding questions and evaluate the responses. 

```js
tests = [
  {
    "context": "metamorphosis.txt",
    "prompt": [
      "who is the main character and what's his personality like",
      "what exactly happened to the main character"
    ]
  },
  {
    "context": "nouns_survey.txt",
    "prompt": [
      "whats the biggest problems in nouns dao",
      "summarise the report",
      "what r some projects funded by nouns governacne",
    ]
  }, 
  {
    "context": "elara_story.txt", ... 
]
```

i currently evaluate different responses to the prompts by...eyeballing and assessing them individually. i also eyeball the nodes retrieved and their relevancy scores. since LLM responses are non-deterministic and the improvements are often miniscule, the current strategy is both unsustainable and unreliable. i need a better way to discern the direction and magnitude of changes and how these changes interact with each other. 

my number one priority in v1 would be to setup automated testing pipeline that 1) feeds data directly into the app, 2) scores separate components within the stack, and 3) scores the final response. Specificially, i want a testing module that can evaluate data sanitization before chunking, chunking coherence and usefulness, accuracy of router retriever, relevancy of nodes retrieved with embedding, relevancy of nodes retrieved post-reranker, accuracy in final responses, degrees of hallunication / faithfulness to provided context. 

luckily, there seems to be [tons](https://docs.parea.ai/tutorials/getting-started-rag#evaluations-create-an-eval-metric) of [LLM](https://www.langchain.com/langsmith) [evaluation](https://docs.confident-ai.com/docs/getting-started) [solutions](https://microsoft.github.io/promptflow/how-to-guides/quick-start.html) [out](https://medium.com/data-science-at-microsoft/evaluating-llm-systems-metrics-challenges-and-best-practices-664ac25be7e5) there today! 

### further improve single-index retrieval results

i have not actually gotten around to implementing most of the optimizations in single-index retrieval.

the first thing to knock off would be a simple one: provide better data from the get-go. 

currently, im loading all text from HTML pages into a document using LangChain's `RecursiveURLLoader`, which captures some symbols (i.e. footnotes like this "books.[[5\]](https://en.wikipedia.org/wiki/Hyperion_Cantos#cite_note-5)") and references. how much improvement would cleaning out these unnecessary details provide?

im also currently using LlamaIndex's `SentenceSplitter` to split a document into chunks while trying to keep sentences and paragraphs together. is this semi-fixed-size chunking approach splitting up information at the "wrong" places, resulting in critical information loss and providing irrelevant context? when i eventually extend data types beyond text (to code, images, etc), document-aware chunking would be important to look into as well. 

the second thing i will do is to consider dropping LlamaIndex as the omnipresent framework and use vanilla python / pytorch for most of the functions. a common complaint that ive come across is that these frameworks actually overcomplicate pretty simple functions; and from my personal experience, i spent too much time building workarounds when sth does break in them. for example, router retrievers don't have a native way to scenarios when the LLM selector fails to find an index to use; i ended up having to build a custom retriever class to implement the additional logic. now that I understand how basic LLM applications work, optimizing its performance is the real step-up. using these frameworks everywhere is invisibly bulky and provides insufficient customizations.

```python
class CustomRetriever(BaseRetriever):
		...
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        try:
            nodes = self.retriever._retrieve(query_bundle)
            ...
            return nodes
        except ValueError:
            logger.error(
                "Selector cannot find relevant index for question: %s", query_bundle)
            nodes = [NodeWithScore(node=TextNode(
                id_="no_index_selected", text="There is no nodes with relevant context"))]
            return nodes

```

### forking instead of coding from scratch

there are [lots](https://www.llamaindex.ai/blog/introducing-rags-your-personalized-chatgpt-experience-over-your-data-2b9d140769b1) of open-source [RAG](https://lightning.ai/lightning-ai/studios/rag-using-llama-3-by-meta-ai?utm_source=akshay) chatbots [out](https://medium.com/rahasak/build-rag-application-using-a-llm-running-on-local-computer-with-ollama-and-langchain-e6513853fda0) [there](https://medium.com/credera-engineering/build-a-simple-rag-chatbot-with-langchain-b96b233e1b2a) today. there is even an entire subreddit dedicated to building these [local GPTs](https://www.reddit.com/r/LocalGPT/top/?t=all)! 

in particularly, [PromtEngineer/localGPT](https://github.com/PromtEngineer/localGPT/blob/main/run_localGPT.py) is implemented with minimal frameworks and directly uses llama.cpp. i would consider forking and iterating upon this repo as a base rather than starting from scratch now that i understand the skeleton of general LLM applications. 



## Conclusion

with the plethora of LLM frameworks and tools on the market today, building an basic LLM application has become obcenely easy. as open-source foundation models become leaner and better, the demand for a local ChatGPT will soon be fulfilled. the future is one in which the **operating system becomes tightly integrated with an local LLM**, allowing user to leverage LLMs to perform tasks, search more effectively, personalize their operating system, get answers to basic questions without using the internet, and so much more--with privacy and customizations. the most dangerous threat to ChatGPT today might actually be Apple and MacOS. if Apple could reinvent Spotlight into a fully functioning chat window powered by LLM, i think i would go on ChatGPT a lot less. 

given how easy it is to integrate LLM today, the "moat" question becomes ever more present. the democratization of LLMs is akin to the democratization of cloud computing back in 2010s--it is stupidly cheap/free and straightforward to incorporate LLMs into your application. i will say i am not unbullish on LLM after this, in fact, i think i have become ever more confident that this is a paradigm shift that one should lean into. the open access to cloud computing back has unleashed developers from thinking about data storage / compute power to focus on bettering user experiences. this democratization to LLMs will unleash a similar thing. now we have a tool that frees people from tasks previously deemed impossible to automate because of their non-deterministic, qualitative nature--like evaluating a textual, retrieving semantically and meaningfully similar documents, or synthesizing texts into similar categories for a recommender's algorithm. what meaningful application can we build on this backend? 

