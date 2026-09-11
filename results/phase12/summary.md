# KARZOUN-X Phase 12 Model/Resource Ablation

Experiment: `phase12-model-resource-ablation-v1`
Synthetic cases per model: **36**

| Model | Gated policy | Known preserve | Required defer | Warm mean s | tok/s | Peak RSS GiB | Model GiB | VRAM GiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| small (`qwen3:4b`) | 0.9722 | 0.9167 | 1.0000 | 8.227 | 18.602 | 4.184 | 2.960 | 2.960 |
| medium (`qwen3:8b`) | 1.0000 | 1.0000 | 1.0000 | 9.051 | 14.864 | 6.423 | 5.187 | 5.187 |
| large (`qwen3:14b-q4_K_M`) | 1.0000 | 1.0000 | 1.0000 | 26.380 | 4.730 | 10.656 | 9.456 | 6.113 |

> Phase 12 compares frozen local model choices on the same synthetic scenarios and the same Phase 11 epistemic gate.
> Measurements come from one host. Ollama-reported VRAM allocation is not a substitute for independent flight-hardware power/thermal testing.
