# Railway Environment Variables Setup

## Required Variables (Must Have)

1. **OPENAI_API_KEY**
   - Your OpenAI API key (starts with `sk-`)
   - ✅ Already set in your Railway config

2. **SERPER_API_KEY**
   - Your Serper API key
   - ✅ Already set in your Railway config

## Optional Variables (Recommended)

3. **MODEL**
   - OpenAI model to use (e.g., `gpt-4o-mini`)
   - ✅ Already set to `gpt-4o-mini` in your Railway config
   - This automatically sets `OPENAI_MODEL_NAME` if not explicitly set

4. **CORS_ORIGINS** (Set after Vercel deployment)
   - Comma-separated list of allowed origins
   - Format: `http://localhost:3000,http://localhost:3001,https://your-app.vercel.app`
   - ⚠️ Set this AFTER you deploy frontend to Vercel and get your Vercel URL
   - For now, defaults to: `http://localhost:3000,http://localhost:3001`

## Variables to Remove (Not Needed)

5. **DYLD_LIBRARY_PATH**
   - ❌ Remove this - it's macOS-specific
   - Railway runs on Linux, so this won't work
   - WeasyPrint will work fine on Railway without this

6. **OPENAI_MODEL_NAME**
   - ❌ Can remove - automatically set from `MODEL` variable
   - Only needed if you want to override the MODEL setting

## Your Current Setup Status

✅ **Root Directory**: `/backend` - Correct!
✅ **OPENAI_API_KEY**: Set
✅ **SERPER_API_KEY**: Set  
✅ **MODEL**: `gpt-4o-mini` - Set
⚠️ **CORS_ORIGINS**: Not set yet (will default to localhost, update after Vercel deploy)
❌ **DYLD_LIBRARY_PATH**: Remove (not needed on Railway)
❌ **OPENAI_MODEL_NAME**: Can remove (redundant with MODEL)

## Next Steps

1. **Remove unnecessary variables** (DYLD_LIBRARY_PATH, OPENAI_MODEL_NAME)
2. **Deploy to Railway** - should work with current config
3. **Deploy frontend to Vercel** - get your Vercel URL
4. **Update CORS_ORIGINS** - add your Vercel URL to the list
5. **Test the full stack** - frontend → backend communication

