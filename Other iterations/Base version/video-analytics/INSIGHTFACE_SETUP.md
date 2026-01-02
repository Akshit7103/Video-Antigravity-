# InsightFace Setup Guide

## What is InsightFace?

InsightFace is a state-of-the-art face recognition library that provides:
- **Better Accuracy**: 99.8% vs dlib's 99.38%
- **Faster Processing**: 2-3x faster than dlib
- **512-D Embeddings**: vs dlib's 128-D (more detailed)
- **Additional Features**: Age, gender estimation
- **Modern Models**: ArcFace, RetinaFace, Buffalo series

## Installation

### Step 1: Install Updated Requirements

The `requirements.txt` has been updated with:
- `insightface==0.7.3`
- `onnxruntime==1.23.2` (updated from 1.16.3)

Install in your virtual environment:

```bash
# Activate your virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install with updated onnxruntime
pip install -r requirements.txt
```

### Step 2: Configuration

The system is already configured to use InsightFace. Check `config/config.yaml`:

```yaml
face_recognition:
  # Engine: 'dlib' or 'insightface'
  engine: "insightface"

  # Model options for InsightFace:
  # - buffalo_l: Large model (most accurate, ~200MB)
  # - buffalo_m: Medium model (balanced, ~100MB)
  # - buffalo_s: Small model (fastest, ~50MB)
  detection_model: "buffalo_l"

  # Threshold for InsightFace (cosine similarity)
  # Higher = stricter (0.0 to 1.0)
  recognition_threshold: 0.5
```

### Step 3: First Run - Model Download

On first run, InsightFace will automatically download the model:

```bash
python run.py
```

Expected output:
```
Applied providers: ['CPUExecutionProvider'], with options: {...}
find model: .../.insightface/models/buffalo_l/det_10g.onnx
find model: .../.insightface/models/buffalo_l/w600k_r50.onnx
```

**Model locations:**
- Windows: `C:\Users\YourName\.insightface\models\`
- Linux/Mac: `~/.insightface/models/`

**Model sizes:**
- `buffalo_l`: ~200MB (recommended for accuracy)
- `buffalo_m`: ~100MB (good balance)
- `buffalo_s`: ~50MB (fastest)

## Usage

### Automatic Selection

The system automatically uses InsightFace based on config:

```python
# In config.yaml
face_recognition:
  engine: "insightface"  # Use InsightFace
  # OR
  engine: "dlib"         # Use dlib (fallback)
```

### Switch Between Engines

To switch back to dlib:

1. Edit `config/config.yaml`:
   ```yaml
   face_recognition:
     engine: "dlib"
     detection_model: "hog"  # or "cnn"
     recognition_threshold: 0.6
   ```

2. Restart the application

## Key Differences: InsightFace vs dlib

| Feature | InsightFace | dlib |
|---------|-------------|------|
| **Accuracy** | 99.8% | 99.38% |
| **Speed** | Faster (2-3x) | Slower |
| **Embedding Size** | 512-D | 128-D |
| **Threshold** | 0.5 (similarity) | 0.6 (distance) |
| **Threshold Logic** | Higher = more similar | Lower = more similar |
| **GPU Support** | Excellent | Limited |
| **Extra Features** | Age, gender | None |
| **Model Size** | 50-200MB | Small |
| **First Run** | Downloads models | Immediate |

## Threshold Explanation

### InsightFace (Cosine Similarity)
```
Range: 0.0 to 1.0
- 1.0 = Perfect match (same person)
- 0.9-0.99 = Very likely same person
- 0.5-0.89 = Possibly same person (threshold: 0.5)
- 0.0-0.49 = Different person

Higher value = Better match
```

### dlib (Euclidean Distance)
```
Range: 0.0 to infinity
- 0.0 = Perfect match
- 0.0-0.6 = Same person (threshold: 0.6)
- 0.6-1.0 = Possibly same person
- 1.0+ = Different person

Lower value = Better match
```

## Performance Tuning

### For Speed (CPU)
```yaml
face_recognition:
  engine: "insightface"
  detection_model: "buffalo_s"  # Small model
  recognition_threshold: 0.45   # More lenient
```

### For Accuracy
```yaml
face_recognition:
  engine: "insightface"
  detection_model: "buffalo_l"  # Large model
  recognition_threshold: 0.6    # Stricter
```

### For GPU Acceleration
```yaml
performance:
  use_gpu: true  # Enable GPU

face_recognition:
  engine: "insightface"
  detection_model: "buffalo_l"
```

**Note**: Requires CUDA-enabled GPU and `onnxruntime-gpu`

## Troubleshooting

### Issue: "No module named 'insightface'"

**Solution:**
```bash
pip install insightface==0.7.3
```

### Issue: "onnxruntime version mismatch"

**Solution:**
```bash
pip uninstall onnxruntime
pip install onnxruntime==1.23.2
```

### Issue: Models not downloading

**Solution:**
```python
# Manually trigger download
import insightface
from insightface.app import FaceAnalysis

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=-1)  # -1 for CPU
```

### Issue: "CUDAExecutionProvider not available"

This is normal if you don't have GPU. System will use CPU automatically.

**To enable GPU:**
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu==1.23.2
```

### Issue: Out of memory

**Solution:**
Use smaller model:
```yaml
detection_model: "buffalo_s"  # Instead of buffalo_l
```

## Comparison Example

### Registration with InsightFace
```
Input: 5 face images
↓
InsightFace detects faces (faster)
↓
Generates 512-D embeddings (more detailed)
↓
Average embedding calculated
↓
Stores in database (larger size)
```

### Recognition with InsightFace
```
Camera frame
↓
Detect faces (RetinaFace detector)
↓
Generate 512-D embedding
↓
Compare with stored embeddings (cosine similarity)
↓
If similarity >= 0.5: MATCH
↓
Also provides: age (~25-30), gender (male/female)
```

## Migration from dlib to InsightFace

If you have existing registrations with dlib:

### Option 1: Re-register Everyone
1. Switch to InsightFace in config
2. Delete old persons
3. Re-register with new images

### Option 2: Keep Both (Advanced)
```yaml
face_recognition:
  engine: "dlib"  # Keep existing
```

Register new persons:
```yaml
face_recognition:
  engine: "insightface"  # For new registrations
```

**Note**: You cannot mix embeddings. A person registered with dlib cannot be recognized with InsightFace and vice versa.

## Recommendations

### For Production
```yaml
face_recognition:
  engine: "insightface"
  detection_model: "buffalo_l"
  recognition_threshold: 0.55
```

### For Testing/Development
```yaml
face_recognition:
  engine: "insightface"
  detection_model: "buffalo_m"
  recognition_threshold: 0.5
```

### For Edge Devices (Limited Resources)
```yaml
face_recognition:
  engine: "insightface"
  detection_model: "buffalo_s"
  recognition_threshold: 0.45
```

## Verification

Check which engine is running:

```bash
# Start the application
python run.py

# Look for log message:
# "Using InsightFace engine" ✓
# OR
# "Using dlib engine"
```

Also check API health:
```bash
curl http://localhost:8000/api/health
```

## Benefits Summary

✅ **Better accuracy** (99.8% vs 99.38%)
✅ **2-3x faster** processing
✅ **More robust** to angles and lighting
✅ **Additional features** (age, gender)
✅ **Better GPU support**
✅ **More detailed embeddings** (512-D)
✅ **Modern architecture** (SOTA models)

---

**You're all set!** The system will now use InsightFace for superior face recognition performance.
