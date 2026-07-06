# AI-Enhanced SDN Edge Router for Real-Time DDoS Detection and Mitigation

An SDN-based security system built with **Ryu**, **Mininet**, and **scikit-learn** that monitors flow statistics, detects high-rate DDoS behavior, and automatically installs mitigation rules on the edge switch in real time.

## Overview

This project implements an intelligent DDoS defense mechanism in a Software-Defined Networking (SDN) environment. OpenFlow flow statistics are collected by a Ryu controller, converted into traffic features, and used to support DDoS detection and mitigation logic. The project also includes offline machine learning model training and comparison using a large SDN DDoS dataset, with Decision Tree, Random Forest, and Logistic Regression evaluated for classification performance.

The runtime pipeline focuses on real-time monitoring, attack detection, and automated blocking of suspicious flows. During testing, the controller successfully detected high-rate flood traffic and installed drop rules dynamically to stop the attack.

## Features

- Real-time traffic monitoring using a Ryu SDN controller.
- Custom Mininet topology with OpenFlow 1.3 switch and multiple hosts.
- DDoS detection using flow-level traffic statistics.
- Automatic mitigation through dynamic OpenFlow drop-rule installation.
- Offline machine learning model training and evaluation.
- Comparison of Decision Tree, Random Forest, and Logistic Regression models.
- Exported evaluation results and model artifacts for analysis.

## Tech Stack

- Python 3
- Ryu Controller
- Mininet
- Open vSwitch / OpenFlow 1.3
- pandas
- numpy
- scikit-learn
- joblib

## Project Structure

```text
ai-router-project/
├── data/
│   ├── insdn.csv              # raw dataset (kept locally, not pushed if too large)
│   └── final1.csv             # cleaned dataset (kept locally, not pushed if too large)
├── notebooks/
│   └── train_model.py
├── scripts/
│   └── custom_topology.py
├── src/
│   └── controller/
│       └── monitor.py
├── results/
│   ├── model_comparison.csv
│   ├── evaluation_report.json
│   └── attack_events.csv
├── preprocess_dataset.py
├── model.pkl
├── requirements.txt
└── README.md
```

## Workflow

### 1. Preprocess dataset

```bash
python3 preprocess_dataset.py
```

This script cleans the raw dataset, creates the target label, and saves the processed file as `data/final1.csv`.

### 2. Train and evaluate models

```bash
python3 notebooks/train_model.py
```

This step:
- loads the cleaned dataset,
- trains multiple machine learning models,
- compares performance metrics,
- saves the best model as `model.pkl`,
- writes results to the `results/` folder.

### 3. Run the SDN controller

```bash
ryu-manager src/controller/monitor.py
```

The controller:
- collects flow statistics,
- computes runtime traffic features,
- detects suspicious high-rate flows,
- installs mitigation rules automatically.

### 4. Start the Mininet topology

In a second terminal:

```bash
sudo python3 scripts/custom_topology.py
```

### 5. Generate traffic in Mininet

Normal traffic:

```bash
h2 ping h1
```

Flood traffic:

```bash
h3 ping -f h1
```

The controller should detect the attack and install a drop rule for the malicious source.

## Model Results

Example model comparison from training:

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| Decision Tree | 0.999950 | 1.000000 | 0.999950 | 0.999975 | 0.999997 |
| Random Forest | 0.999210 | 0.999552 | 0.999653 | 0.999602 | 0.997157 |
| Logistic Regression | 0.997919 | 0.998399 | 0.999507 | 0.998953 | 0.917116 |

**Best model:** Decision Tree

## Runtime Demo Summary

The runtime demo showed the following successful behavior:

- Normal ICMP traffic between hosts was forwarded correctly.
- Flood traffic generated using `ping -f` produced extremely high packet-per-second rates.
- The Ryu controller flagged the flow as a DDoS attack.
- A drop rule was installed dynamically on the switch.
- Packet rate for the detected attack flow dropped to zero after mitigation.

## Current Limitation

The project currently demonstrates strong real-time rule-based detection and mitigation in the live controller. Offline machine learning training and model comparison are completed successfully, but runtime ML inference may require further feature-alignment improvements so that the exact training feature set matches the live controller feature set.

This means the project is fully functional as a real-time SDN DDoS detection and mitigation system, while ML-controller integration can be improved further in future work.

## Future Improvements

- Align runtime controller features exactly with training features for live ML inference.
- Add support for more attack types beyond ICMP flood traffic.
- Include graphical dashboards for attack visualization.
- Add latency, throughput, and mitigation-time plots.
- Extend evaluation to larger and more diverse SDN topologies.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

If Mininet and Ryu are installed through system packages or a virtual environment, ensure they are available before running the controller and topology scripts.

## Notes

- Large dataset files are intentionally kept out of GitHub when they exceed GitHub's file-size limit.
- Use the provided scripts to regenerate cleaned data and trained models locally.
- Results files in `results/` can be committed if they remain within GitHub limits.

## Author

**Vishwas**
**Urvija**
## License

This project is intended for academic, learning, and demonstration purposes.
