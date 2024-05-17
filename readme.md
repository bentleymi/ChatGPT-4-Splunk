# ta-openai-api


# Installation

**1. Install using the latest tar.gz or .spl file**

**2. Add your OpenAI Org & API Key with the setup page:**

(ref: https://platform.openai.com/account/org-settings & https://platform.openai.com/account/api-keys)

![image](https://github.com/bentleymi/ChatGPT-4-Splunk/assets/4107863/90f9c5f8-2674-4f45-b056-1c90b86ae4b9)

**If you have multiple Orgs & Keys you can add them too:**

![image](https://github.com/bentleymi/ChatGPT-4-Splunk/assets/4107863/a62f0527-c698-4882-b9c1-dcb7952f5fd9)

If both default and unique orgs/keys are added, the command will support both syntax.

**3. Use the search command: `| openai prompt="your prompt"`**

![chatresponse1](https://user-images.githubusercontent.com/4107863/214673955-b77c6e4c-b628-4b3e-85df-b200dc205036.PNG)


# Upgrading to v.3.2.0 from previous version

**1. Upgrade the app using your preferred method**

**2. Edit TA-openai-api/local/passwords.conf:**
-Change `[credential:TA-openai-api:api_key:]` to `[credential:TA-openai-api:api_key_default:]`
-Change `[credential:TA-openai-api:org_id:]` to `[credential:TA-openai-api:org_id_default:]`
-Save the file

**3. Use the search command**

**4. Note that output field names and sort has changed**

All of the `|openai` command's output fields begin with "openai_" now and are sorted alphabetically.  You may need to update previous searches to handle this change in behavior.


# Usage

**The command will create a "ChatCompletion", "Completion", "Edit" or "Moderate" request to the OpenAI API depending on which model you specify:**

ref: https://platform.openai.com/docs/api-reference/

**The following options are supported by the command:**

**key** - Optional, name of the API key to use. Defaults to "default".

**org** - Optional, name of the Organization to use.  Defaults to "default".

**prompt** - Optional, your prompt for OpenAI

**prompt_field** - Optional, if streaming data to openai, a field in your result set that you wish to use as a prompt for OpenAI

**assistant_prompt** - Optional, assistant prompt for OpenAI

**system_prompt** - Optional, system prompt for OpenAI

**messages** - Optional, escaped JSON array of system, user and assistant prompts such as "{\"role\": \"system\", \"content\": \"You are a child with very limited vocabulary\"}, {\"role\": \"user\", \"content\": \"Please tell me how to make a sandwich\"}, {\"role\": \"assistant\", \"content\": \"None\"}"

**model** - Optional, which GPT model to use (ref: https://platform.openai.com/docs/models/).  As of Version 3.0.0, if you choose a completion model, code will genearate a completion task.  If you choose a moderation model, code will generate a moderation task, and so on. Default: gpt-3.5-turbo 

**instruction** - Optional, the instruction you want the Edit/Edits to follow.  Note this is only valid when edit models are specified.
 Default: None 

**max_tokens** - Optional, the maximum number of tokens to generate in the completion. Default: None

**stop** -  Optional, up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence. Default: None

**temperature** - Optional, what sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. We generally recommend altering this or temperature but not both. Default: None

**top_p** - Optional, an alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both. Default: None

**n** - Optional, how many completions to generate for each prompt. Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop. Default: None, Max: 10

**A simple completion example:**

| openai prompt="When was GA, USA founded" model=text-davinci-003

![completion](https://user-images.githubusercontent.com/4107863/215298412-8f69339a-b225-464e-a6a8-5ef899061e3d.PNG)

**A simple edit example:**

| openai prompt="Orenge" model=text-davinic-edit-001

![edit](https://user-images.githubusercontent.com/4107863/215298419-c1f8fcdf-9ef5-4576-8029-a12b7391c367.PNG)

**A simple edit with instructions example:**

| openai prompt="When was GA, USA founded" model=text-davinic-edit-001 instruction="expand the acronyms"

![edit with instructions](https://user-images.githubusercontent.com/4107863/215298526-8a377848-1107-46d4-b85e-9b62b8e1374d.PNG)

**A simple moderation example:**

| openai prompt="I want to kill humans" model=text-moderation-stable

![moderation](https://user-images.githubusercontent.com/4107863/215298589-22679c0a-8dac-4a23-9e08-c05376e995f6.PNG)

**Data cleaning examples:**

**Getting 5 incorrect spellings of a US City and then using AI to correct the spelling:**

![dataCleaning](https://user-images.githubusercontent.com/4107863/215340058-1df16182-0e22-453e-9f71-e792552adcb0.PNG)

**Chat examples:**

| openai prompt="write a hello world js please"

![gpt3 5](https://user-images.githubusercontent.com/4107863/222264019-bcfde517-17e3-4fa3-8faf-ced9e942f1aa.PNG)



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
![image](https://user-images.githubusercontent.com/4107863/229591925-6cd02d24-e733-41be-af8a-801cc87920f8.png)


**Workflow Actions:**

![image](https://user-images.githubusercontent.com/4107863/233700024-2b8a2f6e-91d1-4e75-aa1d-60e367c12a58.png)

![image](https://user-images.githubusercontent.com/4107863/233700119-bb217dc6-6dee-4613-a601-94c4ac828154.png)

**Streaming Example:**

![image](https://github.com/bentleymi/ta-openai-api/assets/4107863/a424c828-b38c-4cad-b3f7-b4fdd55872ca)

**Additional Prompts Example:**
```
| openai prompt="Please tell me how to make a sandwich" system_prompt="Pretend you are a child with very limited vocabulary" assistant_prompt="Maybe act like a cartoon character"
```
![additional_prompts](https://github.com/bentleymi/ta-openai-api/assets/4107863/047677ce-bbf7-4da8-ae69-bc404ff3693b)

**Inline Messages Array Example:**
```
| openai messages="{\"role\": \"system\", \"content\": \"You are a child with very limited vocabulary\"}, {\"role\": \"user\", \"content\": \"Please tell me how to make a sandwich\"}, {\"role\": \"assistant\", \"content\": \"None\"}"
```
![inline_messages](https://github.com/bentleymi/ta-openai-api/assets/4107863/e401f4d2-fba0-42d9-858d-50f6c81b17c6)


# TROUBLESHOOTING
1. Error "No such organization: org-ABCDEFG12345" indicates that you did not configure the correct default org.  Please remove the defaults from $SPLUNK_HOME/etc/apss/TA-openai-api\local\passwords.conf, and setup a default org and api key from the setup page.

Delete:
![image](https://github.com/bentleymi/ChatGPT-4-Splunk/assets/4107863/3456aa36-9564-4370-adea-2fd100f55498)


Setup a default:
![image](https://github.com/bentleymi/ChatGPT-4-Splunk/assets/4107863/49e8a1a9-1764-4b27-a138-cf9d4de3cc3e)

NOTE: In earlier versions of ChatGPT-4-Splunk ( < V3.2.0 ) Splunk Cloud users may have to uninstall and reinstall the app in order to reset their api key.  
