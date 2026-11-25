"""TeamoRouter chat node for ComfyUI.

Calls TeamoRouter's OpenAI-compatible Chat Completions endpoint
(https://api.teamorouter.com/v1/chat/completions) with only the Python standard
library. One API key reaches Claude, GPT, Gemini, DeepSeek, GLM, Kimi and Qwen
models. Use it to write or expand prompts, caption images, or translate text.
"""

import base64
import io
import json
import os
import urllib.error
import urllib.request

API_BASE = os.environ.get("TEAMOROUTER_BASE_URL", "https://api.teamorouter.com/v1").rstrip("/")
DEFAULT_MODELS = [
    "deepseek-v4-flash",
    "claude-sonnet-5-5",
    "claude-haiku-5-5",
    "gpt-6.1-sol",
    "gemini-4-neon",
    "glm-5.3",
    "kimi-k3",
    "qwen3.8-max",
]


def _api_key(value):
    key = (value or "").strip() or os.environ.get("TEAMOROUTER_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "TeamoRouter API key is missing. Set the api_key input or the TEAMOROUTER_API_KEY "
            "environment variable. Create a key at https://teamorouter.com/dashboard"
        )
    return key


def _image_to_data_url(image):
    """Convert the first image of a ComfyUI IMAGE tensor (B,H,W,C floats 0..1) to a PNG data URL."""
    from PIL import Image  # bundled with ComfyUI
    import numpy as np

    array = (image[0].cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def chat_completion(api_key, model, messages, max_tokens, temperature, timeout=300):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    request = urllib.request.Request(
        API_BASE + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "User-Agent": "comfyui-teamorouter/0.1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail).get("error", {}).get("message", detail)
        except (ValueError, AttributeError):
            pass
        if error.code == 402:
            detail += " (balance is used up; top up at https://teamorouter.com/dashboard)"
        raise RuntimeError("TeamoRouter HTTP %s: %s" % (error.code, detail)) from None
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("TeamoRouter returned no choices: %s" % json.dumps(payload)[:500])
    return choices[0].get("message", {}).get("content") or ""


class TeamoRouterChat:
    CATEGORY = "TeamoRouter"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "Write a detailed image prompt for: a lighthouse at dawn"}),
                "model": (DEFAULT_MODELS, {"default": DEFAULT_MODELS[0]}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 128000}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.05}),
            },
            "optional": {
                "system": ("STRING", {"multiline": True, "default": ""}),
                "image": ("IMAGE",),
                "custom_model": ("STRING", {"default": "", "tooltip": "Any model ID from https://teamorouter.com/models; overrides model"}),
                "api_key": ("STRING", {"default": "", "tooltip": "Leave empty to use TEAMOROUTER_API_KEY"}),
            },
        }

    def run(self, prompt, model, max_tokens, temperature, system="", image=None, custom_model="", api_key=""):
        messages = []
        if system.strip():
            messages.append({"role": "system", "content": system})
        if image is not None:
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": _image_to_data_url(image)}},
            ]
        else:
            content = prompt
        messages.append({"role": "user", "content": content})
        text = chat_completion(_api_key(api_key), custom_model.strip() or model, messages, max_tokens, temperature)
        return (text,)


NODE_CLASS_MAPPINGS = {"TeamoRouterChat": TeamoRouterChat}
NODE_DISPLAY_NAME_MAPPINGS = {"TeamoRouterChat": "TeamoRouter Chat (LLM)"}
