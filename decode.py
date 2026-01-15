#!/usr/bin/env python3
import base64

print("🔓 Stealth Calendar Decoder")
print("="*40)

# Paste your calendar description here
text = input("📄 Paste event description: ").strip()

# Extract base64 after "OUT:"
if "OUT:" in text:
    b64_data = text.split("OUT:")[1].split()[0].strip()
else:
    b64_data = text.strip()

# Decode
try:
    output = base64.b64decode(b64_data).decode('utf-8')
    print(f"\n✅ DECODED:\n{output}")
except:
    print("❌ Invalid base64")
