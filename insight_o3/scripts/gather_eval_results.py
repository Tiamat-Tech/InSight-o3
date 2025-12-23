import argparse
from pathlib import Path
import json

import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        'Gather evaluation results for given settings and datasets from <output_dir>/<setting>/<dataset>/summary_metrics.json.')
    parser.add_argument('--settings', nargs='+', required=True, help='Evaluation settings for which to gather results.')
    parser.add_argument('--datasets', nargs='+', required=True, help='Datasets for which to gather results.')
    parser.add_argument('--output_dir', type=str, default='./outputs/eval', help='Path to the eval outputs directory.')
    args = parser.parse_args()

    rows = []
    for setting in args.settings:
        row = {}
        for dataset in args.datasets:
            row[dataset] = 'N/A'
            summary_metrics_path = Path(args.output_dir) / setting / dataset / 'summary_metrics.json'
            if not summary_metrics_path.exists():
                print(f"WARNING: Summary metrics not found for {setting}/{dataset}")
                continue
            with open(summary_metrics_path, 'r') as f:
                summary_metrics = json.load(f)
            if summary_metrics['overall_success_rate']['mean'] < 1.0:
                mean = str(round(summary_metrics['overall_success_rate']['mean'] * 100, 1))
                std = str(round(summary_metrics['overall_success_rate']['std'] * 100, 1))
                print(f"WARNING: Overall success rate ({mean}±{std}) is less than 100.0 for {setting}/{dataset}")
            if summary_metrics['overall_completion_rate']['mean'] < 1.0:
                mean = str(round(summary_metrics['overall_completion_rate']['mean'] * 100, 1))
                std = str(round(summary_metrics['overall_completion_rate']['std'] * 100, 1))
                print(f"WARNING: Overall completion rate ({mean}±{std}) is less than 100.0 for {setting}/{dataset}")
            mean = str(round(summary_metrics['overall_accuracy']['mean'] * 100, 1))
            std = str(round(summary_metrics['overall_accuracy']['std'] * 100, 1))
            row[dataset] = f"{mean}±{std} @{summary_metrics.get('num_trials', 1)}"
            if len(args.datasets) == 1:
                for category in summary_metrics['category_accuracy']:
                    mean = str(round(summary_metrics['category_accuracy'][category]['mean'] * 100, 1))
                    std = str(round(summary_metrics['category_accuracy'][category]['std'] * 100, 1))
                    row[f"{dataset}-{category}"] = f"{mean}±{std} @{summary_metrics.get('num_trials', 1)}"
        rows.append(row)
    
    df = pd.DataFrame(rows, index=args.settings)
    print(df)