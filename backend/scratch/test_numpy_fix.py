import sys
import os
import json
import numpy as np
from fastapi.encoders import jsonable_encoder

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.image_detector_service import ImageDetectorService

def test_serialization():
    service = ImageDetectorService()
    
    # Mock some image bytes (a simple 10x10 gray image)
    import cv2
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, dummy_bytes = cv2.imencode('.png', dummy_img)
    image_bytes = dummy_bytes.tobytes()

    print("Running analyze...")
    try:
        # We need to wrap this in an event loop because it's async
        import asyncio
        result = asyncio.run(service.analyze(image_bytes, "test.png"))
        
        print("Analysis result keys:", result.keys())
        
        # Test serialization
        print("Testing jsonable_encoder...")
        json_compatible = jsonable_encoder(result)
        
        print("Testing json.dumps...")
        json_str = json.dumps(json_compatible)
        
        print("Success! Result is serializable.")
        # print("JSON:", json_str[:200] + "...")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serialization()
