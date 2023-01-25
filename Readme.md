# ta-openai-chatgpt

**Installation:**
**1. Install using the .spl file**
**2. Add your OpenAI Org & API Key with the setup page:**

![image](https://user-images.githubusercontent.com/4107863/214665563-7616ddbc-ef22-4289-ba6c-3829fd13746d.png)

**3. Use the search command: `|chatgpt org="YOUR_ORG_ID" prompt="your prompt"`**

![chatresponse1](https://user-images.githubusercontent.com/4107863/214673955-b77c6e4c-b628-4b3e-85df-b200dc205036.PNG)

**The command will create a "Completion" request to ChatGPT:**

ref: https://beta.openai.com/docs/api-reference/completions/create

**The following options are supported by the command:**

**org** - Default: Null - Explanation: Required, the organization ID you added with the setup page

**prompt** - Explanation: Optional, your chatGPT prompt

**engine** - Default: text-davinci-002 - Explanation: Optional, which GPT3 model to use (ref: https://beta.openai.com/docs/models/gpt-3)

**max_tokens** - Default: 1024 - Explanation: Optional, the maximum number of tokens to generate in the completion.

**stop** - Default: Null - Explanation: Optional, up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence. 

**temperature** - Default: 0.5 - Explanation:  Optional, what sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend altering this or temperature but not both.

**top_p** - Default: Null - Explanation:  Optional, an alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both.

**n** - Default: 1 - Explanation: Optional, how many completions to generate for each prompt. Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.

**A simple usage example:**
|chatgpt org="YOUR_ORG_ID"

**A complex usage example:**
|chatgpt org="YOUR_ORG_ID" prompt="The number of years it has been since alice in wonderland was written?" temperature=0 max_tokens=512 n=1 

![chatresponse2](https://user-images.githubusercontent.com/4107863/214671472-00b8dcac-b171-413f-8741-fb34a5816dca.PNG)


