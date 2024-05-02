i have been building a simple chatbot with RAG powered by local LLMs. 

why i am building my own chatbot instead of using chatGPT? 

couple things irk me about ChatGPT:

1. lack of privacy. my prompts and additional contextual data are [stored by OpenAI](https://openai.com/policies/privacy-policy), dont like that, especially bc i want to ask personal, sensitive info (ex, health info)
2. arbitrary and lazy censorship. 
3. lack of customized data ingestion pipelines. ChatGPT's inability to directly consume my notion, slack, google drive, or any local folder makes it less personally useful
4. lack of persistent memory (working on it tho). this is a difficult problem that i would love to explore more in the future: how can the accuracy and relevancy of retrieval results, given a highly diverse and large data collection? [lots](https://twitter.com/sjwhitmore/status/1776718019437490386) of [teams](https://www.rewind.ai) are [thinking](https://openai.com/index/memory-and-new-controls-for-chatgpt) [about](https://www.wired.com/story/chatgpt-memory-openai/) this [problem](https://python.langchain.com/docs/modules/memory/). i would love to explore further into this. 
5. $240 a year and not open-source, esp given the abundance of free, open-source LLM models out there today. 



what can you run a local LLM on? 

i was confused initially: *can my macbook handle running llama2 locally? rnt these very computationally and data-intensive to run? how slow will be it?*

here is my current setup

| Chipset Model    | Number of GPU | Number of CPU | RAM  | SSD   | Memory bandwidth                  |
| ---------------- | ------------- | ------------- | ---- | ----- | --------------------------------- |
| Apple M3 Pro GPU | 18-core GPU   | 12-core       | 36GB | 500GB | 150GB/s (due to lower memory bus) |

- i can run llama2 (7-billion parameter model) at ~40 tokens/second, which is a [~175 character-request](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them) per second. it 
- i can run mixtral (47B parameter model) at ~1.6 tokens/s. 
