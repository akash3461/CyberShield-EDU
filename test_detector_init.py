import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Attempting to import TextDetectorService...")
start = time.time()
try:
    from app.services.text_detector import TextDetectorService
    print(f"Import successful in {time.time() - start:.2f}s")
    
    print("Initializing TextDetectorService...")
    init_start = time.time()
    detector = TextDetectorService()
    print(f"Initialization successful in {time.time() - init_start:.2f}s")
    
    print("Testing analysis...")
    import asyncio
    async def test():
        res = await detector.analyze("test")
        print("Analysis test successful:", res['prediction'])
    
    asyncio.run(test())
    
except Exception as e:
    print(f"FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
