# To view the images, please visit https://github.com/bentleymi/ta-openai-api/blob/main/readme.md

**1. Install using the latest tar.gz or .spl file**

**2. Add your OpenAI Org & API Key with the setup page:**

(ref: https://beta.openai.com/account/org-settings & https://beta.openai.com/account/api-keys)

[example image](https://user-images.githubusercontent.com/4107863/214665563-7616ddbc-ef22-4289-ba6c-3829fd13746d.png)

**3. Use the search command: `| openai prompt="your prompt"`**   NOTE: org={yourORGID} is no longer supported as of version 2.1.0

[example image](https://user-images.githubusercontent.com/4107863/214673955-b77c6e4c-b628-4b3e-85df-b200dc205036.PNG)

**The command will create a "ChatCompletion", "Completion", "Edit" or "Moderate" request to the OpenAI API depending on which model you specify:**

ref: https://beta.openai.com/docs/api-reference/

**The following options are supported by the command:**

**prompt** - Explanation: Optional, your prompt for OpenAI

**prompt_field** - Explanation: Optional, if streaming data to openai, a field in your result set that you wish to use as a prompt for OpenAI

**model** - Default: gpt-3.5-turbo - Explanation: Optional, which GPT model to use (ref: https://beta.openai.com/docs/models/).  As of Version 3.0.0, if you choose a completion model, code will genearate a completion task.  If you choose a moderation model, code will generate a moderation task, and so on.

**task** - DEPRECATED in Version 3.0.0+ | Default: chat - Explanation: Optional, the task you wish to complete from this list (Chat,Complete,Edit,Moderate)

**instruction** - Default: None - Explanation: Optional, the instruction you want the Edit/Edits to follow.  Note this is only valid when edit models are specified.

**max_tokens** - Default: None - Explanation: Optional, the maximum number of tokens to generate in the completion.

**stop** - Default: None - Explanation: Optional, up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence. 

**temperature** - Default: None - Explanation:  Optional, what sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend altering this or temperature but not both.

**top_p** - Default: None - Explanation:  Optional, an alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both.

**n** - Default: None, max 10 - Explanation: Optional, how many completions to generate for each prompt. Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.

**A simple completion example:**

| openai prompt="When was GA, USA founded" model=text-davinci-003 task=completion 

[completion example image](https://user-images.githubusercontent.com/4107863/215298412-8f69339a-b225-464e-a6a8-5ef899061e3d.PNG)

**A simple edit example:**

| openai prompt="Orenge" model=text-davinic-edit-001

[edit example image 1](https://user-images.githubusercontent.com/4107863/215298419-c1f8fcdf-9ef5-4576-8029-a12b7391c367.PNG)

**A simple edit with instructions example:**

| openai prompt="When was GA, USA founded" model=text-davinic-edit-001 instruction="expand the acronyms"

[edit example image 2](https://user-images.githubusercontent.com/4107863/215298526-8a377848-1107-46d4-b85e-9b62b8e1374d.PNG)

**A simple moderation example:**

| openai prompt="I want to kill" model=text-moderation-stable

[moderation example image](https://user-images.githubusercontent.com/4107863/215298589-22679c0a-8dac-4a23-9e08-c05376e995f6.PNG)

**Data cleaning examples:**

**Getting 5 incorrect spellings of a US City and then using AI to correct the spelling:**

[data clensing example image](https://user-images.githubusercontent.com/4107863/215340058-1df16182-0e22-453e-9f71-e792552adcb0.PNG)

**Chat examples:**

| openai prompt="write a hello world js please"

[chat example image](https://user-images.githubusercontent.com/4107863/222264019-bcfde517-17e3-4fa3-8faf-ced9e942f1aa.PNG)



**Mapping Example:**
```
`comment("Grab some data from an internal index and combine it into one field called raw")`
index=_internal sourcetype=splunk_web_access
| head 10
| rename _raw as raw
| fields raw
| mvcombine raw

`comment("Ask ChatGPT what's the best sourcetype to use for the data")`
| map [| openai model=gpt-4 prompt="What is the best Splunk sourcetype for this data? \n".$raw$]

`comment("Parse the reponse, dropping all but the value of the content field from the response message")`
| spath input=openai_response
| rename choices{}.message.content as response
| table response
```
[mapping example image](https://user-images.githubusercontent.com/4107863/229591925-6cd02d24-e733-41be-af8a-801cc87920f8.png)


**Workflow Actions:**

[workflow actions example image 1](https://user-images.githubusercontent.com/4107863/233700024-2b8a2f6e-91d1-4e75-aa1d-60e367c12a58.png)

[workflow actions example image 2](https://user-images.githubusercontent.com/4107863/233700119-bb217dc6-6dee-4613-a601-94c4ac828154.png)

**Streaming Example:**

[streaming example image](https://github.com/bentleymi/ta-openai-api/assets/4107863/a424c828-b38c-4cad-b3f7-b4fdd55872ca)
