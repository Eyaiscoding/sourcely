# Ollama Setup Guide

## What is Ollama?

Ollama is a free, open-source tool that lets you run large language models (LLMs) locally on your computer. No API keys, no costs, complete privacy!

## Why Ollama?

✅ **100% Free** - No API costs, no subscriptions  
✅ **Privacy** - Everything runs on your machine  
✅ **No Rate Limits** - Use as much as you want  
✅ **Offline Capable** - Works without internet (after downloading models)  
✅ **Fast** - Local inference, no network latency  

## Installation

### Windows (Recommended)

1. **Download Ollama**:
   - Visit: https://ollama.ai/download
   - Click "Download for Windows"
   - Run the installer (`OllamaSetup.exe`)

2. **Verify Installation**:
   ```powershell
   ollama --version
   ```
   
   Should output something like: `ollama version 0.x.x`

3. **Ollama runs automatically** as a Windows service in the background

### macOS

```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Verify
ollama --version
```

### Linux

```bash
# Download and install
curl -fsSL https://ollama.ai/install.sh | sh

# Start the service
sudo systemctl start ollama
sudo systemctl enable ollama

# Verify
ollama --version
```

## Pulling Models

After installation, you need to download a model. We recommend **llama3.2** for this project (fast, efficient, ~2GB):

```powershell
ollama pull llama3.2
```

### Available Models (Alternatives)

| Model | Size | Speed | Quality | Recommended Use |
|-------|------|-------|---------|-----------------|
| **llama3.2** | ~2GB | ⚡⚡⚡ Fast | Good | **Recommended** - Best balance |
| llama3.1 | ~4.7GB | ⚡⚡ Medium | Better | More capable, slower |
| mistral | ~4GB | ⚡⚡ Medium | Good | Alternative to llama |
| gemma2 | ~5GB | ⚡⚡ Medium | Good | Google's model |
| llama3.1:70b | ~40GB | ⚡ Slow | Excellent | Needs powerful GPU |

**For this project, use `llama3.2` unless you have a powerful machine with GPU.**

## Verify Ollama is Running

### Check Service Status

```powershell
# List installed models
ollama list
```

Should show something like:
```
NAME            ID              SIZE    MODIFIED
llama3.2:latest abc123def456    2.0 GB  2 hours ago
```

### Test the Model

```powershell
ollama run llama3.2 "What is Kubernetes?"
```

Should generate a response about Kubernetes.

## Configuration for Sourcely

Your `.env` file should have:

```env
# LLM Configuration (FREE - using Ollama)
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

**That's it!** No API keys needed.

## Troubleshooting

### "ollama: command not found"

- **Windows**: Restart your terminal after installation
- **Mac/Linux**: Make sure Ollama is in your PATH, or run the install script again

### "Failed to connect to Ollama"

1. Check if Ollama is running:
   ```powershell
   ollama list
   ```

2. If not running:
   - **Windows**: Ollama should start automatically. Restart your computer or run `ollama serve` manually
   - **Mac/Linux**: Run `ollama serve` in a separate terminal

### "Model not found"

You need to pull the model first:
```powershell
ollama pull llama3.2
```

### Slow Generation

- **Use a smaller model**: Switch to `llama3.2` (fastest)
- **GPU acceleration**: Ollama automatically uses GPU if available (NVIDIA/AMD)
- **Close other apps**: Free up RAM and CPU

### Out of Memory

If your machine has limited RAM (<8GB):
- Use `llama3.2` (smallest, ~2GB)
- Close other applications
- Consider using a cloud-based alternative (but that won't be free)

## Performance Tips

### For Faster Responses

1. **Use GPU**: Ollama automatically detects and uses NVIDIA/AMD GPUs
2. **Smaller models**: `llama3.2` is the fastest
3. **Adjust context**: Reduce the amount of context in prompts (done automatically in our code)

### Check GPU Usage

```powershell
# See if Ollama is using GPU
ollama ps
```

## Switching Models

To use a different model:

1. **Pull the new model**:
   ```powershell
   ollama pull mistral
   ```

2. **Update your `.env` file**:
   ```env
   OLLAMA_MODEL=mistral
   ```

3. **Restart the Streamlit app**

## Uninstalling

If you need to remove Ollama:

- **Windows**: Settings → Apps → Ollama → Uninstall
- **Mac**: `brew uninstall ollama`
- **Linux**: `sudo rm /usr/local/bin/ollama`

Models are stored in:
- **Windows**: `%USERPROFILE%\.ollama`
- **Mac/Linux**: `~/.ollama`

Delete this directory to free up space.

## Cost Comparison

| Provider | Cost | Privacy | Rate Limits |
|----------|------|---------|-------------|
| **Ollama** | **$0** | ✅ Local | ❌ None |
| Claude | $15-30/month | ❌ Cloud | ✅ Yes |
| OpenAI GPT-4 | $20-30/month | ❌ Cloud | ✅ Yes |
| Groq | $0 (limited) | ❌ Cloud | ✅ Yes |

## Additional Resources

- **Official Website**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **GitHub**: https://github.com/ollama/ollama
- **Documentation**: https://github.com/ollama/ollama/tree/main/docs

## Need Help?

1. Check the official docs: https://github.com/ollama/ollama/tree/main/docs
2. Search GitHub issues: https://github.com/ollama/ollama/issues
3. Ask in the course forum

---

**Ready?** After installing Ollama and pulling `llama3.2`, run the Streamlit app:

```powershell
streamlit run agent/app.py
```

Your Sourcely agent is now **100% free**! 🎉
