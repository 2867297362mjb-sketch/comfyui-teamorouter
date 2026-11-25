# comfyui-teamorouter

A ComfyUI node that calls [TeamoRouter](https://teamorouter.com), an OpenAI-compatible API gateway. One API key reaches Claude, GPT, Gemini, DeepSeek, GLM, Kimi and Qwen models. Use it inside a workflow to write or expand prompts, caption an input image with a vision model, or translate text.

No extra dependencies: requests use the Python standard library, and image input uses the Pillow and NumPy that ship with ComfyUI.

## Install

- ComfyUI-Manager: search for **comfyui-teamorouter**.
- Manual: `git clone https://github.com/2867297362mjb-sketch/comfyui-teamorouter` into `ComfyUI/custom_nodes/`, then restart ComfyUI.

## Set up

1. Create an API key in the [TeamoRouter dashboard](https://teamorouter.com/dashboard). Usage is billed per token from a prepaid balance.
2. Set `TEAMOROUTER_API_KEY` in the environment that starts ComfyUI, or paste the key into the node's `api_key` input. Keys in the input are saved into workflow files, so the environment variable is safer for shared workflows.

## Node: TeamoRouter Chat (LLM)

| Input | Notes |
| --- | --- |
| `prompt` | The user message. |
| `model` | A preset list of model IDs. |
| `custom_model` | Any model ID from the [model list](https://teamorouter.com/models). It overrides `model`. |
| `system` | Optional system message. |
| `image` | Optional IMAGE. The first image in the batch is sent as a PNG, so choose a vision-capable model such as `claude-sonnet-5-5` or `gpt-6.1-sol`. |
| `max_tokens`, `temperature` | Passed through to the API. |

Output: `text` (STRING). Connect it to a CLIP Text Encode node to use the result as a prompt.

`TEAMOROUTER_BASE_URL` overrides the endpoint. The default is `https://api.teamorouter.com/v1`.

## Errors

- `HTTP 401`: the key is missing or wrong.
- `HTTP 402`: the balance is used up. Top up in the dashboard.

## License

MIT. Maintained by TeamoRouter (Teamo HK Limited).
