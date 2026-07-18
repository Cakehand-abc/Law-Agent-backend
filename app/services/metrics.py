from pydantic import BaseModel

class TokenUsageLog(BaseModel):
    task_id: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_rmb: float

async def calculate_and_log_token_usage(
    task_id: str, 
    model_name: str, 
    raw_usage_dict: dict
) -> TokenUsageLog:
    prompt_tk = raw_usage_dict.get("prompt_tokens", 0)
    completion_tk = raw_usage_dict.get("completion_tokens", 0)
    total_tk = prompt_tk + completion_tk
    
    if "deepseek-v4" in model_name.lower():
        rate_prompt = 1.0 / 1000000
        rate_completion = 2.0 / 1000000
    else:
        rate_prompt = 0.5 / 1000000
        rate_completion = 1.0 / 1000000
        
    cost = (prompt_tk * rate_prompt) + (completion_tk * rate_completion)
    
    usage_log = TokenUsageLog(
        task_id=task_id,
        model_name=model_name,
        prompt_tokens=prompt_tk,
        completion_tokens=completion_tk,
        total_tokens=total_tk,
        cost_rmb=round(cost, 6)
    )
    
    # Save to db...
    return usage_log
