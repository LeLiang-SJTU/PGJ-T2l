from datetime import datetime
from pathlib import Path
import toml
import pandas as pd
from openai import OpenAI
import zhipuai
import dashscope
from dashscope import ImageSynthesis  
from tencentcloud.common import credential
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models as hunyuan_models

# Load configuration file
def load_config():
    config_path = Path(__file__).parent / 'config.toml'
    if not config_path.exists():
        raise FileNotFoundError("Configuration file does not exist, please ensure the config.toml file is in the correct location")
    return toml.load(config_path)

# Initialize configuration
config = load_config()
API_KEYS = config['api_keys']
MODEL_CONFIG = config['model_config']
SYSTEM_CONFIG = config['system']

# Ensure save directories exist
Path(SYSTEM_CONFIG['image_save_path']).mkdir(exist_ok=True)
Path(SYSTEM_CONFIG['csv_save_path']).mkdir(exist_ok=True)

def check_api_key(config, model_type):
    """Check if the API key for a specific model is configured"""
    api_keys = config['api_keys']
    
    if model_type == "openai":
        return bool(api_keys.get('openai'))
    elif model_type == "zhipu":
        return bool(api_keys.get('zhipu'))
    elif model_type == "ali":
        return bool(api_keys.get('ali'))
    elif model_type == "tencent":
        return bool(api_keys.get('tencent_secret_id')) and bool(api_keys.get('tencent_secret_key'))
    
    return False

# Save generation records
def save_as_csv(prompt, model_type, status, url=None, error=None):
    """Save generation records to CSV"""
    log_file = Path(SYSTEM_CONFIG['csv_save_path']) / 'new.csv'
    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'prompt': prompt,
        'model': model_type,
        'status': status,
        'url': url,
        'error': error
    }
    df = pd.DataFrame([data])
    
    if log_file.exists():
        df.to_csv(log_file, mode='a', header=False, index=False)
    else:
        df.to_csv(log_file, index=False)

# Image generation
def ImageCreatOpenAI(prompt, model=None, **kwargs):
    """OpenAI DALL-E image generation
    Args:
        prompt (str): Prompt
        model (str, optional): Model name, default is read from the configuration file
        **kwargs: Other parameters, can include size, quality, style, n, etc.
    """
    try:
        client = OpenAI(api_key=API_KEYS['openai'])
        model = model or MODEL_CONFIG['openai_default']
        
        # Merge default parameters and user-provided parameters
        params = MODEL_CONFIG.get('model_params', {}).get('openai', {}).copy()
        params.update(kwargs)
        params.update({
            "model": model,
            "prompt": prompt,
        })
        
        response = client.images.generate(**params)
        save_as_csv(prompt, "openai", "success", response)
        return True, response
    except Exception as e:
        save_as_csv(prompt, "openai", "error", error=str(e))
        return False, str(e)

def ImageCreatZP(prompt, model=None, **kwargs):
    """Zhipu AI image generation
    Args:
        prompt (str): Prompt
        model (str, optional): Model name, default is read from the configuration file
        **kwargs: Other parameters
    """
    try:
        client = zhipuai.ZhipuAI(api_key=API_KEYS['zhipu'])
        model = model or MODEL_CONFIG['zhipu_model']
        
        
        params = MODEL_CONFIG.get('model_params', {}).get('zhipu', {}).copy()
        params.update(kwargs)
 
        response = client.images.generations(
            model=model,
            prompt=prompt,
            **params
        )
        print(response)
     
        save_as_csv(prompt, "zhipu", "success", response)
            
        return True, response

    except Exception as e:
        save_as_csv(prompt, "zhipu", "error", error=str(e))
        return False, str(e)

def ImageCreatTX(prompt, model_type="lite", **kwargs):
    """Tencent Cloud image generation
    Args:
        prompt (str): Prompt
        model_type (str): Model type, options are 'lite' 
        **kwargs: Other parameters
    Returns:
        tuple: (bool, str) - (Success, URL or error message)
    """
    try:
        cred = credential.Credential(
            API_KEYS['tencent_secret_id'],
            API_KEYS['tencent_secret_key']
        )
        client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou")
        
        if model_type.lower() == "lite":
            req = hunyuan_models.TextToImageLiteRequest()
            req.Prompt = prompt
            req.RspImgType = "url"
            
            response = client.TextToImageLite(req)
            print(response)
            
            save_as_csv(prompt, "tencent_lite", "success", response)

            return True, response
            
         
     
            
            
    except Exception as e:
        save_as_csv(prompt, f"tencent_{model_type}", "error", error=str(e))
        return False, str(e)


def ImageCreatAliTY(prompt, model=None, **kwargs):
    """Alibaba Cloud Tongyi Wanxiang image generation
    Args:
        prompt (str): Prompt
        model (str, optional): Model name, default is 'wanx-v1'
        **kwargs: Other parameters
    Returns:
        tuple: (bool, str) - (Success, URL or error message)
    """
    try:
        dashscope.api_key = API_KEYS['ali']
        model = ImageSynthesis.Models.wanx_v1
        
   
        params = {
            'model': model,
            'prompt': prompt,
            'n': 1, 
            'size': '1024*1024' 
        }
        params.update(kwargs)  
        
        response = ImageSynthesis.call(**params)
 
        save_as_csv(prompt, "ali", "success", response)
        return True, response
            
    except Exception as e:
        save_as_csv(prompt, "ali", "error", error=str(e))
        return False, str(e)

# Text generation
def generate_text_with_llm(prompt, model=None, **kwargs):
    """Generate text using different language models based on the model name
    Args:
        prompt (str): Prompt
        model (str, optional): Model name, options include 'openai' 'gpt-3.5'/'gpt-4'/gpt-4o', etc.
        **kwargs: Other parameters, such as temperature, max_tokens, etc.
    Returns:
        tuple: (success, response result)
    """
    try:
        # Get model type
        if not model:
            model = MODEL_CONFIG.get('default_text_model', 'gpt-4o')
            
        model = model.lower()
        
        # OpenAI model
        if 'gpt' in model or 'openai' in model:
            client = OpenAI(api_key=API_KEYS['openai'])
            params = MODEL_CONFIG.get('model_params', {}).get('openai', {}).copy()
            params.update(kwargs)
   
            params.update({
                'model': model ,
                'messages': prompt
            })
            response = client.chat.completions.create(**params)
            return True, response.choices[0].message.content
         
        else:
            raise ValueError(f"Unsupported model type: {model}")
            
    except Exception as e:
        save_as_csv(prompt, model, "error", error=str(e))
        return False, str(e)

if __name__ == "__main__":
    test_prompt = [{
        "role": "user",
        "content": "Please briefly introduce yourself"
    }]

    print(generate_text_with_llm(test_prompt, model="gpt-4o"))
