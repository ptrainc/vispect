"""Frozen pretrained features; identical preprocessing for training and inference."""
from functools import lru_cache
import numpy as np
from PIL import Image, ImageOps

@lru_cache(maxsize=1)
def backbone():
    import torch
    from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
    torch.set_num_threads(2)
    model = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V2)
    model.classifier = torch.nn.Identity()
    model.eval()
    return model

def embed(images):
    import torch
    from torchvision.transforms import functional as F
    tensors = []
    for image in images:
        image = ImageOps.exif_transpose(image).convert('L').convert('RGB')
        # Contain, not center-crop: do not remove edge defects.
        image = ImageOps.pad(image, (224, 224), method=Image.Resampling.BILINEAR, color=(128,128,128))
        tensors.append(F.normalize(F.to_tensor(image), [0.485,0.456,0.406], [0.229,0.224,0.225]))
    with torch.inference_mode():
        x = backbone()(torch.stack(tensors)).cpu().numpy()
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-8)

def decide(margin, similarity, gate, review_margin=0.5):
    # Distances and SVM margins are NOT calibrated probabilities.
    if similarity < gate:
        return 'TIDAK DIKENALI'
    if abs(margin) < review_margin:
        return 'PERLU REVIEW'
    return 'OK' if margin > 0 else 'NG'
