# ResNet-50 and Fine-Tuning

## What is ResNet-50?

ResNet-50 is a deep neural network designed for **image recognition**. It was created by Microsoft Research in 2015 and won the ImageNet competition that year -- a contest where AI systems compete to correctly classify millions of images into 1,000 categories (dogs, cars, flowers, etc.).

The "50" in the name refers to 50 layers of neurons stacked on top of each other. The "Res" stands for "residual," which refers to a clever architectural trick that makes it possible to train networks this deep.

### Why Depth Matters

Think of image recognition like reading a book:

- A **shallow** network (few layers) is like skimming headlines. It can pick up basic patterns -- edges, colors, simple shapes.
- A **deep** network (many layers) is like reading carefully. Early layers detect edges, middle layers combine edges into shapes (eyes, noses), and deeper layers recognize complex concepts (faces, expressions, manipulations).

For deepfake detection, the subtle artifacts left by AI generation are complex patterns that require deep analysis to spot. A shallow network would miss them.

### The Residual Connection

Before ResNets, very deep networks had a problem: they actually got *worse* at learning as you added more layers. This sounds counterintuitive -- more layers should mean more learning capacity, right?

The problem was called the **vanishing gradient**. During training, the learning signal gets weaker as it passes backward through many layers, like a whisper being passed through a long chain of people -- by the end, the message is lost.

ResNet solved this with **skip connections** (also called residual connections). Instead of each layer only passing its output to the next layer, it also passes its *input* directly to a layer further ahead. Think of it as:

- Without skip connections: A -> B -> C -> D (the signal must pass through every step)
- With skip connections: A -> B -> C -> D, but also A -> D directly (the signal has a shortcut)

This means even if layers B and C learn nothing useful, the signal from A still reaches D clearly. The network can never do worse than if those middle layers did not exist.

## Transfer Learning: Standing on the Shoulders of Giants

Training ResNet-50 from scratch requires:
- Millions of labeled images
- Days of computation on expensive GPUs
- Enormous amounts of energy

TrustChain-AV does not do this. Instead, it uses **transfer learning** -- starting with a ResNet-50 that has already been trained on ImageNet (1.2 million images, 1,000 categories).

### The Analogy

Imagine you want to teach someone to be a food safety inspector. You have two options:

1. **Train from scratch**: Take a newborn and teach them everything -- how to see, what colors are, what food looks like, what mold looks like, what fresh food looks like, and finally what unsafe food looks like. This takes years.

2. **Transfer learning**: Take an adult who already knows how to see, recognizes objects, understands textures and colors. Now you just teach them the specific things to look for in food safety. This takes weeks.

A ResNet-50 pre-trained on ImageNet is like the adult -- it already understands edges, textures, shapes, objects, and faces. We just need to teach it the specific thing: "What does a deepfake look like?"

## Fine-Tuning: Teaching the Old Model New Tricks

Fine-tuning is the process of taking a pre-trained model and retraining it (partially or fully) on a new, specific task. For TrustChain-AV, the new task is deepfake detection.

### The Layers of Understanding

ResNet-50's 50 layers form a hierarchy:

| Layer Group | What It Learned (from ImageNet) | Useful for Deepfakes? |
|-------------|--------------------------------|----------------------|
| **Early layers (1-10)** | Edges, corners, basic textures | Yes -- these are universal visual features |
| **Middle layers (11-35)** | Shapes, patterns, object parts | Mostly yes -- face parts, skin textures |
| **Late layers (36-49)** | High-level object recognition ("this is a dog") | Not directly -- these are too specific to ImageNet categories |
| **Final layer (50)** | Classification into 1,000 ImageNet categories | No -- we replace this entirely |

### The Fine-Tuning Strategy

Fine-tuning ResNet-50 for deepfake detection involves these conceptual steps:

**Step 1: Freeze the backbone**

"Freezing" means telling the early and middle layers: "Do not change. Keep what you learned from ImageNet." These layers already know how to detect edges, textures, and facial features -- exactly what we need.

Think of it like hiring an experienced artist to work at a forensics lab. You do not retrain them to draw -- you keep their drawing skills and teach them what forgery-specific patterns to look for.

**Step 2: Replace the classification head**

The original ResNet-50 ends with a layer that classifies images into 1,000 ImageNet categories (dog, cat, car, etc.). We remove this and replace it with a new layer that outputs what we need: a single score indicating "how fake does this look?"

This is like replacing the last page of a textbook. The student has learned all the fundamentals (chapters 1-49), but instead of the original final exam (name 1,000 objects), we give them a new final exam (is this face real or fake?).

**Step 3: Train on deepfake data**

Now we feed the model a dataset of labeled examples:
- Thousands of real video frames labeled "REAL"
- Thousands of deepfake video frames labeled "FAKE"

The model adjusts only the new classification head (and optionally the last few frozen layers) to learn the patterns that distinguish real from fake.

**Step 4 (Optional): Unfreeze late layers**

After the new head has learned the basics, we can optionally "unfreeze" the last 2-3 layers of the backbone and train them too, with a very small learning rate. This allows the model to slightly adjust its high-level feature extraction to be more sensitive to deepfake-specific patterns.

This is a delicate process -- too much adjustment and the model "forgets" the useful general features it learned from ImageNet. Too little and it does not specialize enough. This balance is called the **fine-tuning trade-off**.

### Training Data: The DFDC Dataset

The model would be fine-tuned on datasets like the **Deepfake Detection Challenge (DFDC)** dataset, which contains:

- Over 100,000 video clips
- Both real and deepfake videos
- Multiple deepfake generation methods (so the model learns to spot various techniques, not just one)
- Diverse subjects (different ages, ethnicities, lighting conditions)

Having diverse training data is critical. A model trained only on high-quality deepfakes of young white males would perform poorly on other demographics or lower-quality fakes.

## How TrustChain-AV Uses ResNet-50

### Feature Extraction (Current Prototype)

In the current prototype, ResNet-50 is used as a **frozen feature extractor**:

1. Video frames are sampled at regular intervals (not every frame -- that would be too slow)
2. Each frame is resized to 224x224 pixels (the size ResNet-50 expects)
3. Pixel values are normalized using ImageNet statistics (so the model sees input in the same range it was trained on)
4. ResNet-50 processes each frame and outputs a **2048-dimensional feature vector** -- a list of 2,048 numbers that represent the visual content of that frame in abstract terms
5. These feature vectors are averaged across all sampled frames to produce a single 2048-dim vector representing the entire video's visual content
6. This vector is passed to the fusion model for the final verdict

### Why 2048 Dimensions?

Each of the 2,048 numbers captures a different aspect of the image. One might respond to smooth skin texture, another to edge sharpness around the jawline, another to lighting consistency. Individually, none of them means much. Together, they form a rich numerical fingerprint of the visual content.

Think of it like describing a person with 2,048 measurements -- height, weight, hair color, nose width, ear shape, etc. Each measurement alone is not very descriptive, but together they form a unique profile.

### Fine-Tuned Version (Future)

When fine-tuned on deepfake data, the model would directly output a "fakeness score" instead of a general feature vector. The feature vector approach is used in the prototype because fine-tuning requires:

- A labeled deepfake dataset
- GPU compute time for training
- Careful hyperparameter selection

The prototype demonstrates the architecture works with the frozen backbone, and fine-tuning is a planned enhancement.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **ResNet** | Residual Network -- a deep CNN with skip connections |
| **Pre-trained** | A model that has already been trained on a large dataset (ImageNet) |
| **Transfer Learning** | Reusing a pre-trained model's knowledge for a new task |
| **Fine-Tuning** | Partially retraining a pre-trained model on new data |
| **Freezing** | Locking layers so they do not change during training |
| **Feature Vector** | A list of numbers that represent the content of an image in abstract terms |
| **Classification Head** | The final layer(s) of a model that produce the output prediction |
| **Backbone** | The main body of the network that extracts features (everything except the head) |
| **Learning Rate** | How big the adjustment steps are during training -- smaller = more careful |
| **Vanishing Gradient** | The problem where learning signals weaken in deep networks (solved by residual connections) |

## Further Reading

- [Deepfake Detection](deepfake-detection.md) -- The broader problem this model addresses
- [Wav2Vec2](wav2vec2.md) -- The audio counterpart to ResNet-50's visual analysis
- [Multimodal Fusion](multimodal-fusion.md) -- How visual features are combined with audio features
