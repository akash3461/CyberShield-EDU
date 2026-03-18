document.getElementById('scanBtn').addEventListener('click', async () => {
    const text = document.getElementById('inputText').value.trim();
    if (!text) return;

    const btn = document.getElementById('scanBtn');
    const resultDiv = document.getElementById('result');
    
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    resultDiv.style.display = 'none';

    try {
        const response = await fetch('http://localhost:8000/api/detect/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error('Backend offline');
        
        const data = await response.json();
        const isScam = data.prediction === 'scam';
        
        resultDiv.textContent = isScam 
            ? `🚨 Warning: ${Math.round(data.confidence * 100)}% Scam Match. ${data.reasoning[0]}`
            : `✅ Secure: ${data.recommendation}`;
        
        resultDiv.className = isScam ? 'scam' : 'safe';
        resultDiv.style.display = 'block';
    } catch (err) {
        resultDiv.textContent = '❌ Error: Ensure CyberShield backend is running on localhost:8000';
        resultDiv.className = 'scam';
        resultDiv.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Analyze Text';
    }
});
