#!/bin/bash
# Stage 2 of 2: fine-tune the GPT (text -> semantic tokens) from s1v3.ckpt, the base the v2Pro series uses. CPU, fp32.
# Settings: batch 4, EPOCHS (default 15), weights saved every 5 epochs, no DPO.
set -e
G=${GSV:-$(cd "$(dirname "$0")/../../../.." && pwd)/.claude/loops/tts/gptsovits}  # the env: .venv, src, data
cd "$G/src"
EXP=${EXP:-me-v2pp}; EPOCHS=${EPOCHS:-15}; BS=${BS:-4}
mkdir -p "logs/$EXP/logs_s1_v2ProPlus" GPT_weights_v2ProPlus TEMP
"$G/.venv/bin/python" - <<PY
import yaml
d = yaml.safe_load(open("GPT_SoVITS/configs/s1longer-v2.yaml"))
d["train"].update(precision="32", batch_size=$BS, epochs=$EPOCHS, save_every_n_epoch=5, if_save_every_weights=True,
                  if_save_latest=True, if_dpo=False, half_weights_save_dir="GPT_weights_v2ProPlus", exp_name="$EXP")
d["data"]["num_workers"] = 2
d["pretrained_s1"] = "GPT_SoVITS/pretrained_models/s1v3.ckpt"
d["train_semantic_path"] = "logs/$EXP/6-name2semantic.tsv"
d["train_phoneme_path"] = "logs/$EXP/2-name2text.txt"
d["output_dir"] = "logs/$EXP/logs_s1_v2ProPlus"
yaml.dump(d, open("TEMP/tmp_s1.yaml", "w"), default_flow_style=False)
PY
export PYTHONPATH="$G/src:$G/src/GPT_SoVITS" hz=25hz _CUDA_VISIBLE_DEVICES=0
"$G/.venv/bin/python" -s GPT_SoVITS/s1_train.py --config_file TEMP/tmp_s1.yaml
