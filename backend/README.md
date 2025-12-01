# Backend Setup Guide

## Environment Variables

The backend requires the following environment variables to be set:

### Required Variables

1. **OPENAI_API_KEY** - Your OpenAI API key (required for CrewAI)
2. **SERPER_API_KEY** - Your Serper API key (required for web search)

### Optional Variables

3. **MODEL** - OpenAI model to use (optional, defaults to CrewAI's default)
   - Recommended: `gpt-4o-mini` (fast and cost-effective)
   - Alternative: `gpt-4o` (higher quality, more expensive)
   - If not specified, CrewAI will use its default model

### Setup Instructions

1. **Create a `.env` file** in one of these locations:
   - `/backend/.env` (backend directory)
   - `/.env` (project root directory)

2. **Add your API keys** to the `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   SERPER_API_KEY=your-serper-api-key-here
   MODEL=gpt-4o-mini
   ```
   
   **Note:** The `MODEL` variable is optional. If you don't specify it, CrewAI will use its default model.

3. **Get your API keys**:
   - OpenAI: https://platform.openai.com/api-keys
   - Serper: https://serper.dev/api-key

### Example .env file

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL=gpt-4o-mini
```

**Model Options:**
- `gpt-4o-mini` - Fast and cost-effective (~$0.01-0.03 per trip) - **Recommended**
- `gpt-4o` - Higher quality but more expensive (~$0.08-0.15 per trip)
- `gpt-3.5-turbo` - Older model, less recommended
- Leave `MODEL` unset to use CrewAI's default

### Verification

The backend will automatically:
- Load `.env` from both backend and parent directories
- Validate that required keys are present
- Show clear error messages if keys are missing

### Troubleshooting

If you see "OPENAI_API_KEY is required" error:
1. Check that your `.env` file exists in the correct location
2. Verify the API keys are correct (no extra spaces or quotes)
3. Restart the backend server after creating/updating `.env`

