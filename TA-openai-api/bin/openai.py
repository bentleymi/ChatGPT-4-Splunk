### Author: Michael Camp Bentley aka JKat54
### Copyright 2023 Michael Camp Bentley
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###             http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
### SCRIPT NAME: openai.py
###

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

def getOpenAIConfig(sessionKey,organizationId):
    try:
        service = Service(token=sessionKey)
        passwords = service.storage_passwords
        response_xml = passwords.get('TA-openai-api:'+organizationId)["body"]
        root = ET.fromstring(str(response_xml))

        password = root.findall(".//*[@name='clear_password']")[0].text
        orgid = root.findall(".//*[@name='username']")[0].text
        return password, orgid
        
    except Exception as e:
        stack = traceback.format_exc()
        splunk.Intersplunk.generateErrorResults(str(e))
        logger.error(str(e) + ". Traceback: " + str(stack))

def execute():
    try:
        # get the keywords suplied to the curl command
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
        
        if 'org' in options:
            orgid = options['org']
        else:
            logger.error('You must add your orgid and api key using the setup page and reference it in your search | chatgpt org="yourORG"')
            
        if 'prompt' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            The prompt(s) to generate completions for, encoded as a string, array of strings, array of tokens, or array of token arrays.

            Note that <|endoftext|> is the document separator that the model sees during training, so if a prompt is not specified the model will generate as if from the beginning of a new document.
            '''                
            prompt = options['prompt']
        else:
            prompt = (f"How long has Michael Bentley been a member of the Splunk Trust?")

        if 'model' in options:
            '''
            ref: https://beta.openai.com/docs/models/gpt-3
            ID of the model to use. You can use the List models API to see all of your available models, or see our Model overview for descriptions of them.
            '''                
            model = str(options['model'])
        else:
            model = "text-davinci-003"
            
        if 'max_tokens' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            The maximum number of tokens to generate in the completion.

            The token count of your prompt plus max_tokens cannot exceed the model's context length. Most models have a context length of 2048 tokens (except for the newest models, which support 4096).
            '''                
            max_tokens = int(options['max_tokens'])
        else:
            max_tokens = 1024  
            
        if 'stop' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
            '''        
            stop = options['stop']
        else:
            stop = None              
            
        if 'temperature' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
        
            We generally recommend altering this or top_p but not both.
            '''
            temperature = float(options['temperature'])
        else:
            temperature = 0.5                

        if 'top_p' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

            We generally recommend altering this or temperature but not both.
            '''        
            top_p = float(options['top_p'])
        else:
            top_p = None      

        if 'n' in options:
            '''
            ref: https://beta.openai.com/docs/api-reference/completions/create
            How many completions to generate for each prompt.

            Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.
            '''               
            n = int(options['n'])
        else:
            n = 1    
            
        # get the previous search results and settings
        results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()
        sessionKey = settings.get("sessionKey")      
        openai.api_key, openai.organization = getOpenAIConfig(sessionKey, orgid)

        if 'task' in options:
            if options['task'].lower() in ("completion","complete"):
                if model not in ("text-davinci-001","text-davinci-002","text-davinci-003"):
                    model="text-davinci-003"
                response = openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    n=n,
                    stop=stop,
                    temperature=temperature,
                    top_p=top_p
                    )
            elif options['task'].lower() in ("edits","edit"):    
                if model not in ("text-davinci-edit-001","code-davinci-edit-001"):
                    model="text-davinci-edit-001"
                if 'instruction' in options:
                    instruction=options['instruction']
                else:
                    instruction="Fix the spelling mistakes"
                response = openai.Edit.create(
                    model=model,
                    input=prompt,
                    instruction=instruction,
                    n=n,
                    temperature=temperature,
                    top_p=top_p
                    )
            elif options['task'].lower() in ("moderations","moderate"):
                if model not in ("text-moderation-stable","text-moderation-latest"):
                    model="text-moderation-stable"
                response = openai.Moderation.create(
                    model=model,
                    input=prompt,
                    )
        else:
            if model not in ("text-davinci-001","text-davinci-002","text-davinci-003"):
                model="text-davinci-003"
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p
                )

        results.append({"openai_prompt":str(prompt),"openai_model":model,"openai_response":response})
        splunk.Intersplunk.outputResults(results)

    except Exception as e:
        stack = traceback.format_exc()
        splunk.Intersplunk.generateErrorResults(str(e))
        logger.error(str(e) + ". Traceback: " + str(stack))

if __name__ == '__main__':
    execute()
