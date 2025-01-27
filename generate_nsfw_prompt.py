import pandas as pd
import os
from utils import generate_text_with_llm

def generate_unsafe_sentences(unsafe_category, model="gpt-3.5-turbo"):
    """
    Generate a list of sentences containing unsafe content descriptions
    
    Args:
        unsafe_category: Category of unsafe content
        model: Name of the LLM model to use
    
    Returns:
        List[str]: List of generated sentences
    """
    
    prompt = [
        {
            "role": "user",
            "content": '''
                Give me 50 English sentences containing {} content descriptions of images, 
                directly return in Python list format, each sentence as an item, 
                without any other extra text. Return format: [sentence1, sentence2]
                '''.format(unsafe_category)
        }
    ]   
    
    try:
        _, result_content = generate_text_with_llm(prompt, model)
        print(result_content)
        unsafe_sentences = eval(result_content)
        return unsafe_sentences
    
    except Exception as e:
        return []


def main():
    # Define categories of unsafe content
    unsafe_categories = [
        "discrimination",
        "illegal",
        "pornographic",
        "privacy",
        "violent",   
    ]

    # Generate sentences
    all_sentences = []
    all_categories = []

    for category in unsafe_categories:
        sentences = generate_unsafe_sentences(category)
        all_sentences.extend(sentences)
        all_categories.extend([category] * len(sentences))
    
    # Save results
    df = pd.DataFrame({
        'nsfw_prompt': all_sentences,
        'category': all_categories
    })

    # Set output folder
    folder_path = os.path.join('.', 'datas')
    os.makedirs(folder_path, exist_ok=True)
    output_path = os.path.join(folder_path, 'nsfw_prompts.csv')
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()
