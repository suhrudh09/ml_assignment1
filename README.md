# Smart Bin Classifier 📦

P Suhrudh - se22uari194

An AI-powered inventory verification system for e-commerce fulfillment centers. This project uses Computer Vision to validate whether the items inside a bin match the expected order metadata. It is built using the **Amazon Bin Image Dataset** and implements a Content-Based Image Retrieval (CBIR) approach for fast and accurate validation.

## 📌 Project Overview

[cite_start]E-commerce fulfillment relies on accurate inventory tracking[cite: 4, 5]. This tool automates the validation process by:
1.  [cite_start]**Indexing** a dataset of bin images and their metadata (ASIN, quantity, weights)[cite: 12, 32].
2.  **Analyzing** an uploaded image of a bin using a pre-trained ResNet model.
3.  **Retrieving** the most visually similar bin from the database.
4.  [cite_start]**Displaying** the verified inventory (metadata) associated with that match to confirm quantities[cite: 39, 43].

[cite_start]This solution addresses challenges such as occlusions, packaging changes (data drift), and varying bin sizes[cite: 23, 116].

## 📂 Repository Structure

```text
smart-bin-classifier/
│
├── data/                   # (Git-ignored) Stores downloaded images & JSONs
│   ├── bin-images/         
│   └── metadata/           
│
├── src/                    # Source code for backend logic
│   ├── __init__.py
│   ├── download_data.py    # Multi-threaded AWS S3 downloader
│   └── search_engine.py    # Feature extraction (ResNet) & Indexing (FAISS)
│
├── app.py                  # Streamlit Frontend Application
├── requirements.txt        # Python dependencies
└── README.md               # Project Documentation
