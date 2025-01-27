import pandas as pd
from datetime import datetime
from utils import  ImageCreatOpenAI, ImageCreatAliTY, ImageCreatTX, ImageCreatZP
import os
from pathlib import Path
import requests

def download_image(url, model_type, path=None, filename=None):
    print(url)

    try:
        response = requests.get(url, timeout=300)
        if response.status_code == 200:
            filename = filename or f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{model_type}.png"
            # Create the full save path
            save_dir = Path("generated_images") / path
            save_dir.mkdir(parents=True, exist_ok=True)  # Create all necessary parent directories
            save_path = save_dir / filename
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True, str(save_path)
        return False, "Download failed"
    except Exception as e:
        return False, str(e)


#图像生成
def Gimages(prompt, model_type="dall-e-3", path=None, filename=None):
    """
    Call the corresponding image generation API based on the model type
    
    Parameters:
    prompt: Image generation prompt
    model_type: Model type ("openai"/"ali"/"tencent"/"zhipu")
    """
    
    # Select the corresponding image generation function based on model_type
    if model_type == "dall-e-3":
        ifiamge, safeCheck = ImageCreatOpenAI(prompt, model="dall-e-3")
    elif model_type == "dall-e-2":
        ifiamge, safeCheck = ImageCreatOpenAI(prompt, model="dall-e-2")
    elif model_type == "ali": 
        ifiamge, safeCheck = ImageCreatAliTY(prompt)
    elif model_type == "tencent":
        ifiamge, safeCheck = ImageCreatTX(prompt)  
    elif model_type == "zhipu":
        ifiamge, safeCheck = ImageCreatZP(prompt) 
    else:
        return [0, 0, 0, "Unsupported model type"]

    if ifiamge:
        # Handle success case
        url = ""
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{model_type}.png"
        reversed_prompt = ""
        try:

            if model_type == "dall-e-3" or model_type == "dall-e-2":
                reversed_prompt = safeCheck.data[0].revised_prompt
                url = safeCheck.data[0].url
            elif model_type == "ali":
                url = safeCheck.output.results[0].url  
            elif model_type == "tencent":
                url = safeCheck.ResultImage
            elif model_type == "zhipu":
                url = safeCheck.data[0].url
                
            # Download and save the image
            print(f"url: {url}")
            _,image = download_image(url, model_type, path, filename)
            
            print(f"Image downloaded successfully: {image}")
            
            return [prompt, True, image,  reversed_prompt]
            
        except Exception as e:
            return [prompt, True, 1, f"Image download error: {str(e)}"]
    else:
        return [prompt, False, 0, safeCheck]


def generate_images(file_path, image_model, output_path):
        df = pd.read_csv(file_path)

        print(f"\nGenerating images using {image_model} model...")
        
        # Create new result columns for each model
        df[f'{image_model}_image_prompt'] = ''
        df[f'{image_model}_image_status'] = ''
        df[f'{image_model}_image_path'] = ''
        df[f'{image_model}_image_info'] = ''
        
        for idx, row in df.iterrows():
            if pd.isna(row['attacked_prompt']):
                continue
                
            print(f"Processing row {idx}...")

            # Call the Gimages function to generate images
            result = Gimages(
                prompt=row['attacked_prompt'],
                model_type=image_model,
                path=f"{image_model}",
                # filename=f"{idx}_{image_model}.png"
            )
            df[f'{image_model}_image_prompt'] = result[0]
            df[f'{image_model}_image_status'] = result[1]
            df[f'{image_model}_image_path'] = result[2]
            df[f'{image_model}_image_info'] = result[3]

            

        df.to_csv(output_path, index=False)


'''
    if model_type == "dall-e-3":
        ifiamge, safeCheck = ImageCreatOpenAI(prompt, model="dall-e-3")
    elif model_type == "dall-e-2":
        ifiamge, safeCheck = ImageCreatOpenAI(prompt, model="dall-e-2")
    elif model_type == "ali": 
        ifiamge, safeCheck = ImageCreatAliTY(prompt)
    elif model_type == "tencent":
        ifiamge, safeCheck = ImageCreatTX(prompt)  
    elif model_type == "zhipu":


'''

def main(file_path):
    image_models=["dall-e-3","dall-e-2","ali", "tencent", "zhipu"]
    for model in image_models:
        # Save the processed results to a new CSV file
        folder_path = os.path.join('datas', 'images')
        os.makedirs(folder_path, exist_ok=True)
        output_path = os.path.join(folder_path, f'{model}_image_prompt.csv')
        generate_images(file_path, model, output_path=output_path)

    print(f"Processing complete, final results saved to: {output_path}")


if __name__ == '__main__':
    unsaftySentence_file_path = 'datas/attacked_prompts.csv'
    main(unsaftySentence_file_path)
    
