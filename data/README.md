# Data preparation
Our evaluation code supports all kinds of (single-image) VQA datasets.
To evaluate on a dataset, the annotation file must be prepared in `jsonl` format as follows:
```json
{
    "image": "images/chart/1-3.png",
    "subset": "chart",
    "question": "When the company’s Solvency Ratio exceeded 5.00x for the first time, what was the change in Total Assets compared to the previous year?",
    "options": "A. −$13,046\nB. −$14,895\nC. −$14,837\nD. −$15,019\nE. −$15,967\nF. No right choice",
    "answer": "D"
}
```
The fields above are required, except that:
- The `image` field name can be replaced with `file_name` (for HuggingFace compatibility).
- The `subset` field name can be replaced with `category`.
- The `options` field is optional (required only for multiple-choice questions).

---

To facilitate reproducing the results in our paper, the `jsonl` annotation files for all the evaluation datasets used in our paper are provided under this folder.
However, you still need to download (and extract) the images from the corresponding datasets and arrange them according to the following folder structure.

```
data
├── vstar_bench
│   ├── vstar_bench.jsonl
│   ├── direct_attributes
│   │   ├── sa_10033.jpg
│   │   └── ...
│   └── relative_position
│       ├── sa_10313.jpg
│       └── ...
│
├── HR-Bench
│   ├── hrbench_4k.jsonl
│   └── images_4k
│       ├── 0.jpg
│       └── ...
│
├── TreeBench
│   ├── treebench.jsonl
│   └── images
│       ├── image_000000.jpg
│       └── ...
│
├── VisualProbe_Hard
│   ├── visual_probe_hard.jsonl
│   └── data
│       ├── visual_probe_hard_1.jpg
│       └── ...
│
├── MME-RealWorld-Lite
│   ├── MME_RealWorld_Lite.jsonl
│   └── imgs
│       ├── 000_Albania_frame00022.png
│       └── ...
│
└── O3-Bench
    └── test
        ├── metadata.jsonl
        └── images
            ├── chart
            │   ├── 1-3.png
            │   └── ...
            └── map
                ├── bus_2024_WEGO_Brochure_Summer_2.jpg
                └── ...
```
