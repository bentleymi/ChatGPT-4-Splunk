'''
Author: Michael Camp Bentley aka JKat54
Copyright 2023 Michael Camp Bentley

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
    2: "max_tokens out of bounds: Please specify an integer between 0 and 1024.",
    3: "temperature out of bounds: Please specify a float between 0 and 1.",
    4: "top_p out of bounds: Please specify a float between 0 and 1.",
    5: "n out of bounds: Please specify an integer between 1 and 10.",
    7: "No sessionKey found. Please make sure enableHeader and passAuth are enabled in commands.conf."
}

import splunk.Intersplunk
import splunk.mining.dcutils as dcu
import traceback
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

def getOpenAIConfig(sessionKey):
    '''
    getOpenAIConfig uses the sessionKey to authenticate against the password store 
    and retrieve the api_key and org_id to be used in the openAI API queries
    '''
    try:
        service = Service(token=sessionKey)
        passwords = service.storage_passwords
        response_xml = passwords.get('TA-openai-api:api_key')["body"]
        root = ET.fromstring(str(response_xml))
        api_key = root.findall(".//*[@name='clear_password']")[0].text
        response_xml = passwords.get('TA-openai-api:org_id')["body"]
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
        why manually specifying? because i didn'tt want to slow down the SPL query by 
        adding an additional query to the API for a list of supported models.  Should be in a conf file maybe.
        '''
        chatCompletionModelList = ("gpt-4","gpt-4-0314","gpt-4-32k","gpt-4-32k-0314","gpt-3.5-turbo","gpt-3.5-turbo-0301")
        completionModelList = ("text-davinci-001","text-davinci-002","text-davinci-003","text-curie-001","text-babbage-001","text-ada-001","davinci","curie","babbage","ada")
        editModelList = ("text-davinci-edit-001","code-davinci-edit-001")
        '''
        Embedding doesnt work in latest Splunk 9.0.5 due to numpy dependency on python version 3.8+ 
        embeddingModelList = ("text-embedding-ada-002", "text-search-ada-doc-001")
        '''
        moderationModelList = ("text-moderation-stable","text-moderation-latest")
        modelList = chatCompletionModelList + completionModelList  + editModelList + moderationModelList # + embeddingModelList
        taskList = ("chat","chatcompletion","completion","complete","edits","edit","moderations","moderate")

        '''Setting defaults for the request, to be overriden by options passed to the command'''
        max_tokens = None
        stop = None
        temperature = None
        top_p = None
        n = None

        '''Get/Set the prompt for chatgpt'''
        prompt = options.get("prompt", "How long has Michael Bentley been a member of the Splunk Trust?")

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
        openai.api_key, openai.organization = getOpenAIConfig(sessionKey)
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
                messages=[{"role": "user", "content": prompt}],
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p,
                )
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
                messages=[{"role": "user", "content": prompt}],
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p,
                )
        '''
        Now we add the response to the list of results in the splunk search pipeline, and output the data 
        '''
        results.append({"openai_prompt":str(prompt),"openai_model":model,"openai_response":response})
        splunk.Intersplunk.outputResults(results)

    except Exception as e:
        raiseError(e)

if __name__ == '__main__':
    execute()
