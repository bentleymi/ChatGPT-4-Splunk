'''
Author: Michael Camp Bentley aka JKat54
Copyright 2022 Michael Camp Bentley

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SCRIPT NAME: openai.py
DESCRIPTION: allows splunk to query openai api
'''

exitCodes = {
    1: "Unrecognized Model: Please check the spelling of your model and try again.",
    2: "max_tokens out of bounds: Please specify an integer between 0 and 1024. To increase this limit, reach out m@ableversity.com",
    3: "temperature out of bounds: Please specify a float between 0 and 1.",
    4: "top_p out of bounds: Please specify a float between 0 and 1.",
    5: "n out of bounds: Please specify an integer between 1 and 10.",
    7: "No sessionKey found. Please make sure enableHeader and passAuth are enabled in commands.conf."
}

import splunk.Intersplunk
import splunk.mining.dcutils as dcu
import traceback
import json
import re
import os,sys
import xml.etree.ElementTree as ET
#add the app's library to the path so we can ship openai and its dependencies with the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".", "lib"))
import openai

from splunklib.client import Service

# Setup logging/logger
logger = dcu.getLogger()

# Setup namespace
namespace = "TA-openai-api"

def raiseError(e):
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))

def getOpenAIConfig(sessionKey, orgName = None, keyName = None):
    '''
    getOpenAIConfig uses the sessionKey to authenticate against the password store 
    and retrieve the api_key and org_id to be used in the openAI API queries
    '''
    try:
        service = Service(token=sessionKey)
        passwords = service.storage_passwords
        if keyName:
            response_xml = passwords.get('TA-openai-api:api_key_'+keyName)["body"]
        else:
            response_xml = passwords.get('TA-openai-api:api_key_default')["body"]
        root = ET.fromstring(str(response_xml))
        api_key = root.findall(".//*[@name='clear_password']")[0].text
        if orgName:
            response_xml = passwords.get('TA-openai-api:org_id_'+orgName)["body"]
        else:
            response_xml = passwords.get('TA-openai-api:org_id_default')["body"]
        root = ET.fromstring(str(response_xml))
        org_id = root.findall(".//*[@name='clear_password']")[0].text
        return api_key, org_id
    except Exception as e:
        raiseError(e)

def execute():
    try:
        # get the keywords suplied to the command
        argv = splunk.Intersplunk.win32_utf8_argv() or sys.argv

        # for each arg
        first = True
        options = {}
        pattern=re.compile("^\s*([^=]+)=(.*)")
        for arg in argv:
            if first:
                first = False
                continue
            else:
                result = pattern.match(arg)
                options[result.group(1)] = result.group(2)

        '''
        lists of acceptable values
        why manually specifying? because i didn't want to slow down the SPL query by 
        adding an additional query to the API for a list of supported models.  Should be in a conf file maybe.

        June 13th 2023 Update:    
        MODEL NAME	DISCONTINUATION DATE	REPLACEMENT MODEL
        gpt-3.5-turbo-0301	09/13/2023	gpt-3.5-turbo-0613
        gpt-4-0314	09/13/2023	gpt-4-0613
        gpt-4-32k-0314	09/13/2023	gpt-4-32k-0613
        gpt-4-32k-0613  TBD  gpt-4-turbo
        gpt-4-32k  TBD  gpt-4-turbo
        
        TBD:
        gpt-4-1106-vision-preview
        gpt-4-vision-preview
        gpt-3.5-turbo-instruct
        dall-e
        tts      
        
        Michael's method of testing many models at one time:
        
        | makeresults count=1
        | fields - _time
        | eval chatCompletionModelList=" gpt-40 gpt-4-1106-preview gpt-4-0125-preview gpt-4-turbo-preview gpt-4-turbo-2024-04-09 gpt-4-turbo gpt-4 gpt-4-0613 gpt-4-32k gpt-4-32k-0613 gpt-3.5-turbo gpt-3.5-turbo-instruct gpt-3.5-turbo-0613 gpt-3.5-turbo-0125 gpt-3.5-turbo-1106 gpt-3.5-turbo-16k gpt-3.5-turbo-16k-0613"
        | makemv chatCompletionModelList
        | mvexpand chatCompletionModelList
        | map search="|openai model=$chatCompletionModelList$"
        '''
        
        chatCompletionModelList = ("gpt-4o","gpt-4o-2024-05-13","gpt-40","gpt-4-1106-preview","gpt-4-0125-preview","gpt-4-turbo-preview","gpt-4-turbo-2024-04-09","gpt-4-turbo","gpt-4","gpt-4-0613","gpt-3.5-turbo","gpt-3.5-turbo-instruct","gpt-3.5-turbo-0613","gpt-3.5-turbo-0125","gpt-3.5-turbo-1106","gpt-3.5-turbo-16k","gpt-3.5-turbo-16k-0613")        
        completionModelList = ("text-davinci-001","text-davinci-002","text-davinci-003","text-curie-001","text-babbage-001","text-ada-001","davinci","curie","babbage","ada","babbage-002","davinci-002")
        
        editModelList = ("text-davinci-edit-001","code-davinci-edit-001")
        
        #TBD: dallEModelList = ("dall-e-3","dall-e-2")
        
        #TBD: ttsModelList = ("tts-1","tts-1-hd")
        
        '''
        Embedding doesnt work in latest Splunk 9.0.5 due to numpy dependency on python version 3.8+ 
        embeddingModelList = ("text-embedding-ada-002", "text-search-ada-doc-001")
        '''
        
        moderationModelList = ("text-moderation-stable","text-moderation-latest")
   
        modelList = chatCompletionModelList + completionModelList  + editModelList + moderationModelList # ttsModelList + embeddingModelList + dallEModelList


        '''Setting defaults for the request, to be overriden by options passed to the command'''
        max_tokens = None
        stop = None
        temperature = None
        top_p = None
        n = None

        '''
        Get/Set the user and system prompts for chatgpt
        '''

        # Do not output instruction string by default '''
        showInstruction = False

        if options.get("messages"):
            # Handle messages field
            messages = json.loads('['+options.get("messages")+']')
            showMessges = True
            prompt = None
        else:
            # No messages field given
            prompt = options.get("prompt", "How long has Michael Bentley been a member of the Splunk Trust?")

            '''The system message can be used to prime the assistant with different personalities or behaviors.'''
            system_prompt = options.get("system_prompt", "You are a very helpful assistant.")

            '''Typically, a conversation will start with a system message that tells the assistant how to behave,
            followed by alternating user and assistant messages, but you are not required to follow this format. '''
            assistant_prompt = str(options.get("assistant_prompt", None))
        
            s_prompt = {"role":"system","content":system_prompt}
            u_prompt = {"role":"user","content":prompt}
            a_prompt = {"role":"assistant","content":assistant_prompt}
            messages = []
            messages.append(s_prompt)
            messages.append(u_prompt)
            messages.append(a_prompt)

            # Do not output the messages dict by default '''
            showMessages = False


        '''
        model:
        ref: https://beta.openai.com/docs/models/gpt-3
        ID of the model to use. You can use the List models API to see all of your available models, 
        or see our Model overview for descriptions of them.
        '''
        model = options.get("model", "gpt-3.5-turbo")
        if model not in modelList:
            e = "Unrecognized Model: Please check the spelling of your model and try again.  The following models are available: "+str(modelList)
            raiseError(e)
            exit(1)
        if model == "gpt-40":
            model = "gpt-4o"
        '''
        max_tokens:
        ref: https://beta.openai.com/docs/api-reference/completions/create
        The maximum number of tokens to generate in the completion.

        The token count of your prompt plus max_tokens cannot exceed the model's context length. 
        Most models have a context length of 2048 tokens (except for the newest models, which support 4096).
        '''                
        max_tokens = int(options.get("max_tokens",1024))
        if max_tokens < 0 or max_tokens > 1024:
            e = exitCodes[2]
            raiseError(e)
            exit(2)
        '''
        ref: https://beta.openai.com/docs/api-reference/completions/create
        Up to 4 sequences where the API will stop generating further tokens. 
        The returned text will not contain the stop sequence.
        '''
        stop = options.get("stop",None)
            
        if 'temperature' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            What sampling temperature to use. Higher values means the model will take more risks. 
            Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
        
            We generally recommend altering this or top_p but not both.
            '''
            temperature = float(options['temperature'])
            if temperature < 0 or temperature > 1:
                e = exitCodes[3]
                raiseError(e)
                exit(3)

        if 'top_p' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

            We generally recommend altering this or temperature but not both.
            '''        
            top_p = float(options['top_p'])
            if top_p < 0 or top_p > 1:
                e = exitCodes[4]
                raiseError(e)
                exit(4)

        '''
        ref: https://beta.openai.com/docs/api-reference/completions/create
        How many completions to generate for each prompt. If less than 1 or greater than 10, we'll exit(5).  Playing it safe so no one puts 100 in there an exhausts their tokens.  Adjust at your own risk.
        Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.
        '''
        n = int(options.get("n",1))
        if n < 1 or n > 10:
            e = exitCodes[5]
            raiseError(e)
            exit(5)



        '''
        Get the previous search results and search settings (enables streaming support, nothing burger if results dont exist)
        '''
        results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()
        sessionKey = settings.get("sessionKey")
        if not sessionKey:
            e=exitCodes[7]
            raiseError(e)
            exit(7)

        '''
        Feature request to support multiple api keys
        '''
        orgName = None
        keyName = None
        if 'org' in options:
            orgName = options.get("org","default")
        if 'key' in options:
            keyName = options.get("key","default")
        openai.api_key, openai.organization = getOpenAIConfig(sessionKey, orgName, keyName)

        if 'prompt_field' in options and results:
            '''
            Stream the field through as the prompt instead, replaced [\n|\r]+ with \n
            '''
            prompt=re.sub(r'[\n\r]+', '\n\n', results[-1][options['prompt_field']])
        if options.get("model","") in completionModelList:
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p,
                )
        elif options.get("model","") in chatCompletionModelList:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p,
                )
            showMessages=True
        elif options.get("model","") in editModelList:
            '''
            edit endpoints require instructions, default to "Fix the Spelling Mistakes" but see if user specified instructions or instruction options first.
            '''
            instruction = options.get("instructions", options.get("instruction", "Fix the Spelling Mistakes"))
            response = openai.Edit.create(
                model=model,
                input=prompt,
                instruction=instruction,
                n=n,
                temperature=temperature,
                top_p=top_p
                )
            showInstruction = True

        elif options.get("model","") in moderationModelList:
            response = openai.Moderation.create(
                    model=model,
                    input=prompt,
                    )

        else:
            '''
            If we get here, task wasnt specified, but no errors have occured, therefore default to "chatcompletion".
            This is documented in readme.md
            '''
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p,
                )
            showMessages=True
        '''
        Now we add the response to the list of results in the splunk search pipeline, and output the data 
        '''
        result = {
            "openai_model":model,
            "openai_response":response
        }
        if showMessages:
            result["openai_prompt"] = str(messages)
        else:
            result["openai_prompt"] = str(prompt)

        if showInstruction:
            result["openai_instruction"] = str(instruction)

        if orgName == None:
            result["openai_org"] = "default"
        else:
            result["openai_org"] = str(orgName)

        if keyName == None:
            result["openai_key"] = "default"
        else:
            result["openai_key"] = str(keyName)
        resultSorted = dict(sorted(result.items()))
        results.append(resultSorted)

        splunk.Intersplunk.outputResults(results)

    except Exception as e:
        raiseError(e)

if __name__ == '__main__':
    execute()
