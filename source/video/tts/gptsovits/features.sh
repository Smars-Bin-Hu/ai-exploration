#!/bin/bash
# Step 3 of README.md, round 7. GPT-SoVITS dataset steps 1a-1c for v2ProPlus on CPU: text and BERT features, HuBERT
# features and 32 kHz wavs, speaker vectors, semantic tokens. The webui's one-click "1abc" without the webui.
# Reads $GSV/data/train.list and $GSV/data/slices; writes $GSV/src/logs/$EXP.
set -e
G=${GSV:-$(cd "$(dirname "$0")/../../../.." && pwd)/.claude/loops/tts/gptsovits}  # the env: .venv, src, data
cd "$G/src"
PY="$G/.venv/bin/python"
export EXP=${EXP:-me-v2pp}
export version=v2ProPlus exp_name=$EXP opt_dir="logs/$EXP" is_half=False i_part=0 all_parts=1
export inp_text="$G/data/train.list" inp_wav_dir="$G/data/slices"
export bert_pretrained_dir=GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large
export cnhubert_base_dir=GPT_SoVITS/pretrained_models/chinese-hubert-base
export sv_path=GPT_SoVITS/pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt
export pretrained_s2G=GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth s2config_path=GPT_SoVITS/configs/s2v2ProPlus.json
export PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH="$G/src:$G/src/GPT_SoVITS"
mkdir -p "$opt_dir"
"$PY" -s GPT_SoVITS/prepare_datasets/1-get-text.py
mv "$opt_dir/2-name2text-0.txt" "$opt_dir/2-name2text.txt"
"$PY" -s GPT_SoVITS/prepare_datasets/2-get-hubert-wav32k.py
"$PY" -s GPT_SoVITS/prepare_datasets/2-get-sv.py
"$PY" -s GPT_SoVITS/prepare_datasets/3-get-semantic.py
{ echo -e "item_name\tsemantic_audio"; cat "$opt_dir/6-name2semantic-0.tsv"; } > "$opt_dir/6-name2semantic.tsv"
rm "$opt_dir/6-name2semantic-0.tsv"
wc -l "$opt_dir/2-name2text.txt" "$opt_dir/6-name2semantic.tsv"; ls "$opt_dir"
