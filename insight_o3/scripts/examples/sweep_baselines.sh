#!/bin/bash

# ------------------------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------------------------

MODELS=('gpt-4o' 'gpt-5-nano' 'gpt-5-mini' 'gemini-2.5-flash')
API_BASE_URL=$OPENAI_BASE_URL
API_KEY=$OPENAI_API_KEY

JUDGE_MODEL='gpt-5-nano'
JUDGE_API_BASE_URL=$OPENAI_BASE_URL
JUDGE_API_KEY=$OPENAI_API_KEY

DATASETS=('vstar' 'hr_bench_4k' 'treebench' 'visual_probe_hard' 'mme_realworld_lite' 'o3_bench')

declare -A ANN_FILES=(
    ["vstar"]="./data/vstar_bench/vstar_bench.jsonl"
    ["hr_bench_4k"]="./data/HR-Bench/hrbench_4k.jsonl"
    ["treebench"]="./data/TreeBench/treebench.jsonl"
    ["visual_probe_hard"]="./data/VisualProbe_Hard/visual_probe_hard.jsonl"
    ["mme_realworld_lite"]="./data/MME-RealWorld-Lite/MME_RealWorld_Lite.jsonl"
    ["o3_bench"]="./data/O3-Bench/test/metadata.jsonl"
)

declare -A IMG_DIRS=(
    ["vstar"]="./data/vstar_bench"
    ["hr_bench_4k"]="./data/HR-Bench/images_4k"
    ["treebench"]="./data/TreeBench/images"
    ["visual_probe_hard"]="./data"
    ["mme_realworld_lite"]="./data/MME-RealWorld-Lite/imgs"
    ["o3_bench"]="./data/O3-Bench/test"
)

NUM_TRIALS=3


# ------------------------------------------------------------------------------------------------
# Run evaluation
# ------------------------------------------------------------------------------------------------

settings=()
for model in "${MODELS[@]}"; do
    # Model-specific settings
    if [[ "$model" == *"gpt"* ]]; then
        img_max_pixels=$((1280*1280))
    else
        img_max_pixels=$((3500*3500))
    fi

    if [[ "$model" == *"gemini"* ]]; then
        extra_args=("--separate_trial_requests")
    fi

    setting="$model"
    settings+=("$setting")

    # Run evaluation on each dataset
    for dataset in "${DATASETS[@]}"; do
        ann_file="${ANN_FILES[$dataset]}"
        image_dir="${IMG_DIRS[$dataset]}"
        eval_name="${setting}/${dataset}"

        echo "=================================================="
        echo "Running evaluation for $eval_name"
        echo "=================================================="

        python -m insight_o3.scripts.evaluate \
            --eval_name "$eval_name" \
            --model "$model" \
            --api_base_url "$API_BASE_URL" \
            --api_key "$API_KEY" \
            --img_max_pixels "$img_max_pixels" \
            --judge_model "$JUDGE_MODEL" \
            --judge_api_base_url "$JUDGE_API_BASE_URL" \
            --judge_api_key "$JUDGE_API_KEY" \
            --ann_file "$ann_file" \
            --img_dir "$image_dir" \
            --num_trials "$NUM_TRIALS" \
            "${extra_args[@]}"

        echo "Evaluation completed for $eval_name"
    done
done

echo "Sweep completed. Gathering evaluation results..."
python -m insight_o3.scripts.gather_eval_results \
    --settings "${settings[@]}" \
    --datasets "${DATASETS[@]}"