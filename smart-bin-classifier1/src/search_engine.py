import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import faiss
import numpy as np
from PIL import Image
import os
import json

class BinSearchSystem:
    def __init__(self, image_folder, metadata_folder):
        self.image_folder = image_folder
        self.metadata_folder = metadata_folder
        self.image_paths = [] 
        
        # Load ResNet Model (Features only)
        print("Loading AI Model...")
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.model = nn.Sequential(*list(self.model.children())[:-1]) # Remove classification layer
        self.model.eval()

        # Preprocessing
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        # FAISS Index
        self.index = faiss.IndexFlatL2(512) 

    def get_embedding(self, img_path=None, img_obj=None):
        """Generates vector from file path OR PIL image object."""
        if img_path:
            img = Image.open(img_path).convert('RGB')
        else:
            img = img_obj.convert('RGB')
            
        img_tensor = self.preprocess(img).unsqueeze(0)
        with torch.no_grad():
            vector = self.model(img_tensor)
        return vector.numpy().reshape(1, -1)

    def build_index(self):
        """Indexes all images in the data folder."""
        print("Building Index...")
        vectors = []
        files = [f for f in os.listdir(self.image_folder) if f.endswith('.jpg')]
        
        for i, fname in enumerate(files):
            path = os.path.join(self.image_folder, fname)
            try:
                vec = self.get_embedding(img_path=path)
                vectors.append(vec)
                self.image_paths.append(fname)
            except Exception as e:
                print(f"Skipping {fname}: {e}")
            
        if vectors:
            batch_vectors = np.vstack(vectors)
            self.index.add(batch_vectors)
            print(f"✅ Indexed {self.index.ntotal} images.")

    def search(self, query_img_obj):
        """Finds the closest match for an uploaded image."""
        query_vec = self.get_embedding(img_obj=query_img_obj)
        distances, indices = self.index.search(query_vec, k=1)
        
        match_index = indices[0][0]
        match_filename = self.image_paths[match_index]
        match_dist = distances[0][0]
        
        # Get Metadata
        meta_path = os.path.join(self.metadata_folder, match_filename.replace(".jpg", ".json"))
        metadata = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
                
        return match_filename, match_dist, metadata
