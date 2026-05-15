import re
import sys

print("Checking environment packages...")

try:
    import youtube_transcript_api

    print(" [PASS] youtube-transcript-api is fully resolved.")
except ImportError as e:
    print(f"❌ [FAIL] youtube-transcript-api error: {e}")

try:
    import torch

    print(f" [PASS] PyTorch is fully resolved. Version: {torch.__version__}")
    print(f"        CUDA available (GPU acceleration): {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ [FAIL] PyTorch error: {e}")

try:
    import transformers
    from transformers import pipeline

    print(
        f" [PASS] Transformers is fully resolved. Version: {transformers.__version__}"
    )

    
    print(
        "        Testing HuggingFace Dialect ID pipeline (may take a moment to load)..."
    )
    did_pipeline = pipeline(
        "text-classification",
        model="CAMeL-Lab/bert-base-arabic-camelbert-mix-did-madar-corpus26",
    )
    test_text = "هسا انا رايح ع لجامعه"
    result = did_pipeline(test_text)[0]
    print(
        f"        Dialect ID Check: '{test_text}' -> Detected: '{result['label']}' ({result['score']:.2f})"
    )
except Exception as e:
    print(f"❌ [FAIL] Transformers/Pipeline error: {e}")

try:
    from camel_tools.utils.dediac import dediac_ar
    from camel_tools.utils.normalize import normalize_alef_ar

    print(" [PASS] camel-tools normalization utilities are fully resolved.")

    
    text = "أحمد"
    normalized = normalize_alef_ar(text)
    print(f"        CAMeL Tools Normalization Check: '{text}' -> '{normalized}'")
except ImportError as e:
    print(f"❌ [FAIL] camel-tools error: {e}")

print("\nDiagnostics complete.")
