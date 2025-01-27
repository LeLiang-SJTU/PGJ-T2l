# PGJ-T2l

# Perception-guided Jailbreak against Text-to-Image Models

This is the official repository of  [[2408.10848\] Perception-guided Jailbreak against Text-to-Image Models](https://arxiv.org/abs/2408.10848)    The paper is accepted by AAAI 2025.

> **Perception-guided Jailbreak against Text-to-Image Models**  
> Yihao Huang, Le Liang, Tianlin Li, Xiaojun Jia, Run Wang, Weikai Miao, Geguang Pu, and Yang Liu

> ###### Abstract
>
> In recent years, Text-to-Image (T2I) models have garnered significant attention due to their remarkable advancements. However, security concerns have emerged due to their potential to generate inappropriate or Not-Safe-For-Work (NSFW) images. In this paper, inspired by the observation that texts with different semantics can lead to similar human perceptions, we propose an LLM-driven perception-guided jailbreak method, termed **PGJ**. It is a black-box jailbreak method that requires no specific T2I model (model-free) and generates highly natural attack prompts. Specifically, we propose identifying a safe phrase that is similar in human perception yet inconsistent in text semantics with the target unsafe word and using it as a substitution. The experiments conducted on six open-source models and commercial online services with thousands of prompts have verified the effectiveness of PGJ.
> Warning: This paper contains NSFW and disturbing imagery, including adult, violent, and illegal-related contentious content. We have masked images deemed unsafe. However, reader discretion is advised.



## Requirements

### 1. Environment

```txt
pandas>=1.5.3
Pillow>=9.5.0
openai>=1.23.1
zhipuai>=2.1.4
tencentcloud-sdk-python>=3.0.1207
python-dotenv>=1.0.1
requests>=2.31.0 
dashscope
```

### 2. API Keys

Add the corresponding API keys in the `config.toml` file.

```toml
[api_keys]
openai = "YOUR_OPENAI_API_KEY"  # OpenAI API key
zhipu = "YOUR_ZHIPU_API_KEY"   # Zhipu API key
ali = "YOUR_ALI_API_KEY"     # Alibaba Cloud API key
tencent_secret_id = "YOUR_TENCENT_SECRET_ID"  # Tencent Cloud SecretId
tencent_secret_key = "YOUR_TENCENT_SECRET_KEY" # Tencent Cloud SecretKey
```





## Quick Start

1. ##### Generate NSFW prompts using large models

   ```
   python generate_nsfw_prompt.py
   ```

   Tips: Testing with gpt3.5-turbo can generate better results, while gpt-4o and other models may refuse to generate.

2. ##### Use **PGJ** to generate new attack prompts

   ```
   python generate_attacked_prompt.py
   ```

3. ##### Use the new prompts to attack online models

   ```
   python generate_images_withT2l.py
   ```



## Visualization Example





## References

```
