"""Make the small coach model: the MMS aligner with its linear layers stored as 8-bit
integers (dynamic quantisation), saved as TorchScript so it loads without ever
building the full-size model. About a quarter of the memory.

    python quantize.py model-int8.pt
"""
import sys

import torch
import torchaudio

out = sys.argv[1] if len(sys.argv) > 1 else "model-int8.pt"
m = torchaudio.pipelines.MMS_FA.get_model(with_star=False).eval()
q = torch.ao.quantization.quantize_dynamic(m, {torch.nn.Linear}, dtype=torch.qint8)
torch.jit.save(torch.jit.script(q), out)
print("saved", out)
