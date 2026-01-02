# InsightFace - Quick Start

## ✅ What's Been Updated

1. **requirements.txt** - Added InsightFace with correct onnxruntime version
2. **New Service** - `backend/services/insightface_detection.py` (400+ lines)
3. **Config Updated** - `config/config.yaml` now supports both engines
4. **API Updated** - Automatically selects engine based on config
5. **Documentation** - Complete setup guide created

## 🚀 Installation Steps

### In Your Virtual Environment:

```bash
# You're already in venv, so just run:
pip install insightface==0.7.3 onnxruntime==1.23.2

# Or reinstall everything:
pip install -r requirements.txt
```

## ⚙️ Configuration

The system is already configured to use InsightFace!

Check `config/config.yaml`:
```yaml
face_recognition:
  engine: "insightface"           # ✓ Already set
  detection_model: "buffalo_l"     # Large model (most accurate)
  recognition_threshold: 0.5       # Cosine similarity threshold
```

## 🎯 First Run

```bash
python run.py
```

**What will happen:**
1. InsightFace initializes
2. Downloads model (~200MB) to `~/.insightface/models/`
3. System starts with InsightFace engine

## 📊 Key Differences

| Metric | InsightFace | dlib |
|--------|-------------|------|
| Accuracy | **99.8%** | 99.38% |
| Speed | **2-3x faster** | Baseline |
| Embedding | **512-D** | 128-D |
| Extra Features | **Age, Gender** | None |

## 🔧 Switch Engines Anytime

### Use InsightFace (Current):
```yaml
face_recognition:
  engine: "insightface"
  detection_model: "buffalo_l"  # or buffalo_m, buffalo_s
  recognition_threshold: 0.5
```

### Switch to dlib:
```yaml
face_recognition:
  engine: "dlib"
  detection_model: "hog"  # or cnn
  recognition_threshold: 0.6
```

## 📝 Important Notes

1. **Threshold Logic is OPPOSITE:**
   - InsightFace: Higher = better match (0.5 = 50% similar)
   - dlib: Lower = better match (0.6 = 60% different)

2. **Models Auto-Download:**
   - First run downloads ~200MB
   - Cached for future use
   - Location: `~/.insightface/models/`

3. **GPU Support:**
   - Set `use_gpu: true` in config
   - Requires CUDA GPU

4. **Cannot Mix:**
   - Person registered with dlib won't work with InsightFace
   - Choose one engine and stick with it

## ✅ Verification

After starting:
```bash
# Check logs for:
[INFO] Using InsightFace engine
[INFO] InsightFace initialized with model: buffalo_l
```

## 🎉 You're Ready!

Your system now uses **state-of-the-art InsightFace** for better accuracy and performance!

For detailed info, see: **INSIGHTFACE_SETUP.md**
