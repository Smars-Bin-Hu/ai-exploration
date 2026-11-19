#!/bin/bash
# Stage 1 of 2: fine-tune SoVITS (v2ProPlus) on the slices. CPU (the repo trains on CPU on Macs: MPS-trained models came
# out worse, README "macOS"). Settings: batch 4, EPOCHS (default 12), text_low_lr_rate 0.4, weights saved every 4 epochs.
set -e
G=${GSV:-$(cd "$(dirname "$0")/../../../.." && pwd)/.claude/loops/tts/gptsovits}  # the env: .venv, src, data
cd "$G/src"
EXP=${EXP:-me-v2pp}; EPOCHS=${EPOCHS:-12}; BS=${BS:-4}
mkdir -p "logs/$EXP/logs_s2_v2ProPlus" SoVITS_weights_v2ProPlus TEMP
"$G/.venv/bin/python" - <<PY
import json
d = json.load(open("GPT_SoVITS/configs/s2v2ProPlus.json"))
t = d["train"]
t.update(fp16_run=False, batch_size=$BS, epochs=$EPOCHS, text_low_lr_rate=0.4, if_save_latest=True,
         if_save_every_weights=True, save_every_epoch=4, gpu_numbers="0", grad_ckpt=False, lora_rank=32,
         pretrained_s2G="GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth",
         pretrained_s2D="GPT_SoVITS/pretrained_models/v2Pro/s2Dv2ProPlus.pth")
d["model"]["version"] = d["version"] = "v2ProPlus"
d["data"]["exp_dir"] = d["s2_ckpt_dir"] = "logs/$EXP"
d["save_weight_dir"] = "SoVITS_weights_v2ProPlus"
d["name"] = "$EXP"
json.dump(d, open("TEMP/tmp_s2.json", "w"))
PY
export PYTHONPATH="$G/src:$G/src/GPT_SoVITS"
"$G/.venv/bin/python" -s GPT_SoVITS/s2_train.py --config TEMP/tmp_s2.json
