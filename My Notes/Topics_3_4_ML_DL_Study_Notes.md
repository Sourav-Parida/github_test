# AI Services — Topics 3 and 4 Revision Notes

- Quick-review notes based on the material in `3_ML` and `4_DL`.
- ML folder topics: regression, classification, dimensionality reduction, and clustering.
- DL folder topics: ANN/CNN examples (MNIST, CIFAR-10, cats/dogs), RNN/LSTM, Google stock forecasting, object detection/segmentation, autoencoders, GANs, and diffusion.

## Topic 3 — Machine Learning (ML)

### 1. ML overview

- **Machine Learning:** algorithms learn patterns from examples and use those patterns to make predictions or discover structure.
- **Features (`X`):** input variables used by a model.
- **Target (`y`):** value or label the model should predict in supervised learning.
- **Dataset splits:**
  - Training set: fits model parameters.
  - Validation set: compares models and tunes choices.
  - Test set: final unbiased performance estimate.
- Avoid data leakage: do not let information from validation/test data affect model fitting or preprocessing.
- Common learning types:
  - Supervised: examples have target values/labels.
  - Unsupervised: find structure without known target labels.
  - Reinforcement: learn actions from rewards and interaction.

### 2. Missing data: imputation

- **Missing value:** a field with no recorded value; missingness can be random or related to the value itself.
- First inspect how much data is missing and whether missingness has a pattern.
- **Deletion:** remove rows/columns only when the amount and pattern of missing data make this reasonable; deletion can bias a dataset.
- **Simple imputation:**
  - Numeric mean: easy, but sensitive to outliers.
  - Numeric median: robust to skew and outliers; often a safe baseline.
  - Categorical mode: fills with the most frequent category.
  - Constant or explicit “Unknown” category: useful when missingness itself may carry information.
- **Advanced imputation:** KNN uses similar rows; iterative/model-based methods estimate missing values using other features.
- Add a missingness indicator when the fact that a value was absent may itself be informative.
- Fit imputation values on training data only, then reuse those values on validation/test/new data.
- For time series, avoid using future observations to fill earlier missing values; choose forward/backward fill or interpolation according to the data and task.
- Imputation creates estimates, not observed facts; document the method and check its effect on results.

### 3. Scaling and normalization in ML

- **Scaling:** changes feature ranges or distributions so measurements are comparable.
- **Standardization (z-score):** `z = (x - mean) / standard deviation`.
  - Centers features around 0 with standard deviation near 1.
  - Common for linear models, SVMs, PCA, and distance-based algorithms.
- **Min–max scaling:** maps values to a fixed range, often `[0, 1]`.
  - Sensitive to outliers because the minimum and maximum set the range.
  - Useful when bounded inputs are desired.
- **Robust scaling:** uses the median and interquartile range; less affected by outliers.
- **Unit-vector normalization:** rescales each row/vector to unit length (often L1 or L2 norm); useful for text vectors and cosine/distance comparisons.
- Feature scaling is especially important for K-means, KNN, SVMs, PCA, and gradient-based models; tree models are usually less sensitive to feature scale.
- Scaling features is different from normalizing a probability distribution or normalizing each image/pixel.
- Fit the scaler on training data only; apply the same fitted scaler to validation/test/new data. Never scale the full dataset before splitting.

### 4. Regression

- **Regression:** predicts a continuous numeric value, such as price, demand, or temperature.
- **Simple linear regression:** predicts with one feature: `ŷ = b₀ + b₁x`.
- **Multiple linear regression:** uses several features: `ŷ = b₀ + b₁x₁ + ... + bₚxₚ`.
- `b₀` is the intercept; coefficients describe the model's fitted relationship to features.
- The model commonly minimizes residual error, often squared error.
- **Polynomial regression:** adds powers/interactions of features to represent curved patterns; it is still linear in the fitted coefficients.
- **Regularization:** discourages overly large coefficients to reduce overfitting.
  - Ridge (L2): shrinks coefficients smoothly.
  - Lasso (L1): can shrink some coefficients to zero.
- Regression metrics:
  - Residual/error: `eᵢ = yᵢ - ŷᵢ`; positive means underprediction, negative means overprediction.
  - MAE: `mean(|y - ŷ|)`; average absolute error, easy to interpret in target units, less sensitive to large outliers than squared-error metrics.
  - MSE: `mean((y - ŷ)²)`; squared units and strongly penalizes large errors.
  - RMSE: `sqrt(MSE)`; returns to target units and still gives large errors extra weight.
  - R²: fraction of target variance explained relative to a mean baseline; can be negative on test data.
- **Choosing a metric:** use MAE when typical absolute error matters; use RMSE when large mistakes should be penalized more. Always compare against a baseline and inspect residuals.
- **Error patterns to inspect:** systematic over/underprediction (bias), changing error spread (heteroscedasticity), outliers, and errors that vary by subgroup or input range.
- Correlation does not establish causation; regression performance depends on representative data and assumptions.

### 5. Classification

- **Classification:** predicts a discrete class, such as spam/ham or disease/no disease.
- Binary classification has two classes; multiclass has more than two.
- A classifier may produce class scores/probabilities and apply a threshold to assign a label.
- Common models include logistic regression, decision trees, random forests, support vector machines, and Naive Bayes.
- **Logistic regression:** estimates class probability using a sigmoid (binary) or softmax (multiclass) output; despite its name, it is used for classification.
- Confusion matrix terms:
  - True positive (TP): positive case predicted positive.
  - False positive (FP): negative case predicted positive.
  - True negative (TN): negative case predicted negative.
  - False negative (FN): positive case predicted negative.
- Classification metrics:
  - Accuracy: `(TP + TN) / (TP + TN + FP + FN)`; overall fraction correct, but can be misleading with class imbalance.
  - Precision: `TP / (TP + FP)`; useful when false alarms are costly.
  - Recall: `TP / (TP + FN)`; useful when missing positives is costly.
  - F1: balance of precision and recall.
  - ROC-AUC: ranking quality across thresholds; inspect precision-recall curves for imbalanced data.
- Class imbalance can make accuracy misleading. Consider stratified splits, class weights/resampling, and metrics suited to the rare class.
- Choose thresholds according to the costs of false positives and false negatives.
- **Classification error types:**
  - False positive / Type I error: predicts a positive when the true class is negative.
  - False negative / Type II error: predicts a negative when the true class is positive.
  - Which error matters more depends on the application (e.g., missed disease versus unnecessary follow-up).

### 6. Unsupervised learning and clustering

- **Unsupervised learning:** finds structure in data without target labels.
- **Clustering:** groups examples by similarity.
- **K-means:**
  - Selects `k` cluster centers.
  - Assigns points to the nearest center.
  - Updates centers to the mean of assigned points and repeats.
  - Requires selecting `k`; sensitive to scaling, initialization, and outliers.
- **Hierarchical clustering:** builds nested groups; a dendrogram can help choose a grouping level.
- **DBSCAN:** groups dense regions and can mark isolated points as noise; useful for irregular clusters, but depends on distance and density parameters.
- Scale numeric features when distances should treat variables comparably.
- Clustering is exploratory: groups are not automatically meaningful labels; interpret and validate them using domain context.

### 7. Dimensionality reduction

- **Purpose:** reduce feature count while retaining useful structure; can aid visualization, compression, and modeling.
- **PCA (Principal Component Analysis):**
  - Finds orthogonal directions with high variance.
  - Transforms features into principal components.
  - Components are combinations of original features and may be less interpretable.
  - Standardize features when measurement scales differ.
  - Fit PCA on training data only; choose component count using explained variance and task performance.
- **t-SNE:** nonlinear visualization technique that emphasizes local neighborhoods; plot distances are not reliable global distances, and it is generally not a standard predictive transform.
- **UMAP:** nonlinear embedding often used for visualization and neighborhood structure; results depend on settings and should not be overinterpreted.
- Dimensionality reduction can discard signal; compare downstream performance before and after transformation.

### 8. ML preprocessing workflow and good practice

- Inspect missing values, data types, distributions, target balance, and outliers.
- Split before preprocessing that learns from data (imputation, scaling, feature selection, PCA, vectorization).
- A common order is split → impute → encode categories → scale if needed → fit model; implement this as a pipeline.
- Use a pipeline so preprocessing and model fitting remain together and leakage is reduced.
- Tune hyperparameters using validation or cross-validation, not the final test set.
- Compare with a simple baseline before adding model complexity.
- Report the metric, test strategy, assumptions, and known limitations.

## Topic 4 — Deep Learning (DL)

### 1. Neural network basics

- **Neuron:** computes a weighted sum plus bias, then applies an activation.
- **Layer:** collection of neurons; outputs become inputs to later layers.
- **Weights and biases:** learned parameters adjusted during training.
- **Forward pass:** calculates predictions from inputs.
- **Loss function:** measures prediction error.
- **Backpropagation:** calculates how parameters contributed to the loss using gradients.
- **Optimizer:** updates parameters (for example, gradient descent or Adam) to reduce loss.
- **Epoch:** one pass over the training set; **batch:** subset used for one update.
- Common activations:
  - **ReLU:** `max(0, x)`; common hidden-layer activation, simple and efficient; can leave units inactive for negative inputs.
  - **Leaky ReLU:** keeps a small slope for negative values; may reduce inactive (“dead”) ReLU units.
  - **Sigmoid:** maps to `(0, 1)`; common binary output probability; can saturate and have small gradients for large magnitudes.
  - **Tanh:** maps to `(-1, 1)`; zero-centered but can also saturate.
  - **Softmax:** converts a vector of class logits into probabilities that sum to 1; common mutually exclusive multiclass output.
  - **Linear:** no nonlinear transform; common regression output.
- Match activation, labels, and loss:
  - Binary output: one sigmoid unit with binary cross-entropy, or one logit with a logits-aware binary loss.
  - Multiclass, one class per example: softmax with categorical or sparse categorical cross-entropy; logits-aware loss can apply softmax internally.
  - Multilabel: independent sigmoid outputs, usually binary cross-entropy per label (softmax is not appropriate when multiple labels may be true).
  - Regression: linear output with MAE, MSE, or another suitable regression loss.
- Do not apply softmax twice when the chosen loss function expects raw logits and applies it internally.
- Overfitting: strong training results but weaker validation/test results.
  - Reduce using more data, regularization, dropout, augmentation, early stopping, or a smaller model.

### 2. Artificial Neural Networks (ANNs)

- Dense/fully connected layers connect each input activation to every neuron in the next layer.
- Useful for tabular or flattened inputs; not inherently aware of image layout or sequence order.
- Inputs often need scaling; targets and output activations depend on task type.
- Binary classification often uses sigmoid plus binary cross-entropy; multiclass often uses softmax plus categorical/sparse categorical cross-entropy; regression often uses a linear output with MAE/MSE loss.

### 3. Imputation, scaling, and normalization in DL

- Handle missing values before tensor conversion; neural layers generally cannot use NaN values directly.
- Options include removing unsuitable examples, imputing with train-set statistics, adding a missingness mask/indicator, or using a model designed for missing data.
- Compute imputation statistics using training data only; apply the same fill values to validation/test data.
- Scale numeric inputs to ranges that support stable optimization:
  - Standardization (mean 0, standard deviation 1) is common for numeric/tabular features.
  - Min–max scaling maps values to a bounded range but is sensitive to extreme values.
  - Images are often converted from integer `[0, 255]` values to `[0, 1]`; some models/data pipelines use `[-1, 1]`.
  - Time series should be scaled using training-period statistics only.
- Scaling inputs is not the same as **Batch Normalization** or **Layer Normalization** inside a neural network.
  - BatchNorm normalizes activations using batch statistics during training and running statistics at inference.
  - LayerNorm normalizes features within an example; common in Transformers and less dependent on batch size.
- Save preprocessing parameters with model weights so inference uses matching transformations.

### 4. Convolutional Neural Networks (CNNs)

- CNNs exploit spatial locality in images using learned filters/kernels.
- **Convolution:** detects local patterns such as edges or textures.
- **Stride/padding:** control filter movement and output dimensions.
- **Activation:** adds nonlinearity after convolution.
- **Pooling:** reduces spatial dimensions and computation; some architectures use strided convolutions instead.
- Deeper layers combine simple patterns into more complex features.
- Data augmentation (flips, crops, rotations where label-preserving) can improve generalization.
- Normalize image pixels consistently with the model's training setup.
- For image classification, final layers map learned features to class scores.

### 5. Recurrent Neural Networks (RNNs)

- RNNs process ordered inputs one step at a time.
- At each step, the model combines the current input `xₜ` with previous hidden state `hₜ₋₁` to produce new state `hₜ`.
- The same cell and weights are reused across time steps.
- Suitable for sequences such as text, sensor readings, and time series.
- Training uses Backpropagation Through Time (BPTT).
- Long sequences can suffer from vanishing or exploding gradients, making distant dependencies difficult.
- **Vanishing gradients:** learning signal shrinks through many steps/layers; early sequence information is hard to learn.
- **Exploding gradients:** gradients grow too large, causing unstable updates; gradient clipping can help.

### 6. LSTM and Bidirectional LSTM

- **LSTM:** RNN architecture with hidden state `hₜ` and cell state `Cₜ`.
- Gates regulate information:
  - Forget gate: what previous memory to retain.
  - Input gate: what new information to write.
  - Output gate: what memory to expose as hidden output.
- Designed to help preserve long-range information; does not guarantee perfect long-term memory.
- **Bidirectional LSTM:** processes the sequence forward and backward, combining both contexts.
- Bidirectional models need the full sequence, so they are unsuitable for strictly causal real-time prediction where future tokens are unavailable.
- Padding masks are important when batching sequences of different lengths.

### 7. Time-series forecasting with RNN/LSTM

- Preserve chronological order; do not randomly shuffle time-series examples across train and test.
- Use sliding windows: previous `n` observations become input; next observation becomes target.
- Recurrent input shape is typically `(samples, timesteps, features)`.
- Fit scaling on training observations only; apply the same scaler to validation/test observations.
- Impute missing observations without using future data; add missingness indicators when useful.
- Keep validation and test periods later in time than training data.
- Use early stopping on validation loss to limit overfitting.
- Evaluate predictions after reversing scaling, using MAE, MSE, RMSE, and plots of actual versus predicted values.
- Distinguish one-step-ahead evaluation (uses observed prior values) from recursive multi-step forecasts (feeds predictions back as inputs).
- Stock-price examples demonstrate sequence modeling; historical pattern fit does not guarantee profitable or reliable future forecasts.

### 8. Object detection and segmentation

- **Image classification:** predicts which class is present in an image.
- **Object detection:** predicts class plus location for each object, usually with bounding boxes.
- Bounding box often represented by center `(x,y)`, width, and height, plus class and confidence.


- **Two-stage detectors (R-CNN family):**
  - R-CNN: proposes regions, then classifies them individually.
  - Fast R-CNN: shares image features to speed region classification.
  - Faster R-CNN: learns region proposals with a Region Proposal Network.
- **SSD (Single Shot MultiBox Detector):** another single-stage detector that predicts boxes and classes in one forward pass.
  - Uses default/anchor boxes with different scales and aspect ratios at locations on feature maps.
  - Predicts a class confidence and coordinate offsets for each default box.
  - Uses several feature-map resolutions so different-sized objects can be detected.
  - Removes the separate region-proposal stage; straightforward architecture and fast inference were key design goals.
  - SSD and YOLO are both one-stage detectors; the specific model/version, resolution, and hardware determine their actual speed and accuracy.

- **YOLO (You Only Look Once):** a family of single-stage object detectors that predicts object locations and classes in one network pass over the image.
  - **Original YOLO idea:**
    1. Resize an image and pass the whole image through one convolutional network.
    2. Divide the image into a grid; a cell is responsible for objects whose centers fall in that cell.
    3. Predict bounding boxes, confidence/objectness, and class scores for candidate objects.
    4. Convert box predictions back to image coordinates, apply a confidence threshold, then suppress duplicate boxes (class-wise NMS in many versions).
  - The grid is a teaching model for the original YOLO design. Modern YOLO versions have changed substantially; some use anchor-free heads and multi-scale feature maps rather than the original fixed grid formulation.
  - **Common architecture flow:**
    1. **Backbone:** extracts visual features at different depths/resolutions.
    2. **Neck:** fuses high-level semantic information with finer spatial detail, often using FPN/PAN-style paths.
    3. **Detection head:** predicts box coordinates and class scores at one or more feature-map scales.
    4. **Post-processing:** filters low-confidence predictions and resolves overlapping detections; newer end-to-end variants can offer NMS-free inference.
  - **Why “look once”:** the detector evaluates the image with a single unified network instead of running a separate region-proposal/classification pipeline for each candidate region.
  - **Training:** labelled images provide class IDs and bounding boxes. Training combines localization/box regression and classification/objectness losses; augmentation and transfer learning are commonly used.
  - **Small objects:** higher-resolution feature maps and suitable image size can help, but tiny objects remain challenging because they occupy few pixels.

- **Single-stage vs two-stage:** SSD and YOLO generate detections directly; R-CNN-style systems propose regions before classifying/refining them. Single-stage models are often chosen for speed; the best choice depends on task requirements and measured results.


- **IoU (Intersection over Union):** area of overlap divided by area of union between predicted and true boxes.
- **Non-Maximum Suppression (NMS):** keeps the high-confidence box and suppresses strongly overlapping duplicate boxes.
- Detection metrics:
  - Precision and recall use matched predictions/ground-truth boxes, usually based on an IoU threshold.
  - Average Precision (AP): area/summary of precision-recall performance for one class.
  - mean AP (mAP): average AP across classes, sometimes across IoU thresholds.
- **Segmentation:** labels pixels rather than only drawing a rectangle.
  - Semantic segmentation assigns a class to each pixel.
  - Instance segmentation separates individual objects, including objects of the same class.

### 9. Autoencoders and generative models

- **Autoencoder:** encoder compresses input to latent `z`; decoder reconstructs it.
- Reconstruction loss measures difference between input and output.
- **VAE:** learns a probabilistic latent distribution.
  - Encoder predicts latent mean and log-variance.
  - Reparameterization: `z = μ + σ ε`, with random `ε` from a standard normal.
  - Loss combines reconstruction loss and KL divergence to encourage a structured latent space.
  - Generate by sampling `z` and passing it through the decoder.
- **GAN:** generator maps random noise to samples; discriminator distinguishes generated and real samples.
  - Train discriminator and generator with opposing goals.
  - Watch for instability and mode collapse.
- **Diffusion:** add noise gradually during the forward process and learn to reverse it; generate by iteratively denoising noise.
- VAE, GAN, and diffusion models have different training objectives, sampling workflows, and trade-offs.

### 10. Deep learning training checklist

- Impute or mask missing inputs; scale/normalize consistently and save the fitted preprocessing values.
- Use correct tensor shapes and verify that labels match output dimensions.
- Match output layer and loss function to the task.
- Track training loss and task metrics; evaluate on validation and held-out test sets.
- Monitor overfitting, class imbalance, data leakage, and compute requirements.
- Set random seeds for repeatable experiments where possible.
- Save model configuration and preprocessing/scaling parameters alongside trained weights.
- Inspect examples and failure cases; a good aggregate metric can hide systematic errors.

## Fast revision checklist

- **ML:** regression predicts numbers; classification predicts labels; clustering groups without labels; PCA reduces dimensions.
- **Preprocessing:** inspect missingness; impute from training data; scale/normalize consistently; prevent leakage.
- **Regression errors:** MAE = mean absolute error; MSE = mean squared error; RMSE = square root of MSE and is in target units.
- **Classification:** accuracy = correct predictions / all predictions; also inspect precision, recall, F1, and false positives/false negatives.
- **DL activations:** ReLU for many hidden layers; sigmoid for binary/multilabel outputs; softmax for one-of-many classes; linear for regression.
- **DL:** learn weights through forward pass, loss, backpropagation, and optimizer updates; normalize inputs and match output/loss.
- **CNN:** learns spatial image patterns; **RNN/LSTM:** models ordered sequences and temporal context.
- **Detection:** class + box; IoU measures overlap; NMS removes duplicate boxes; AP/mAP evaluates detection.
- **Generative:** VAE samples latent codes; GAN trains competing networks; diffusion learns iterative denoising.
