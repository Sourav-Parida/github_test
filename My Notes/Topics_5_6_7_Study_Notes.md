# AI Services — Topics 5, 6, and 7 Revision Notes

- These notes are organized as short points for quick review.
- Updated against the notebooks currently in `5_NLP`, `6_Transformer`, and `7_LLM`.
- Topic 5 coverage now includes regex, tweet/text cleaning, spam and IMDB sentiment, Word2Vec and Keras embeddings, RNN/LSTM/BiLSTM comparisons, and vector-search fundamentals.
- Topic 6 coverage now includes Transformer attention, BERT, VAEs/autoencoders, GANs, diffusion/Stable Diffusion, text-to-speech, speech-to-text, and image-question answering.
- Topic 7 coverage now includes provider APIs, tokenization, embeddings, prompting/evaluation, LangChain, RAG, safety, and software-development workflow concepts.
- Companion code notebooks are in this folder:
  - `Topic_5_NLP_Code_Summary.ipynb`
  - `Topic_6_Transformers_Generative_Models_Code_Summary.ipynb`
  - `Topic_7_LLM_Prompting_RAG_Code_Summary.ipynb`

## Topic 5 — Natural Language Processing (NLP)

### 1. NLP overview

- **NLP:** methods that help computers process and work with human language.
- **Common tasks:**
  - Classification: spam detection, sentiment, and intent.
  - Information extraction: names, places, dates, and key facts.
  - Search, translation, summarization, question answering, and text generation.
- **Corpus:** a collection of text documents.
- **Document:** one text sample or record.
- **Typical workflow:**
  1. Define the problem and labels.
  2. Collect representative data.
  3. Inspect and clean text.
  4. Split data into training, validation, and test sets.
  5. Convert text to features.
  6. Train and evaluate a model.
  7. Review errors, deploy, and monitor.

### 2. Cleaning and normalization

- Text may include HTML, URLs, extra spaces, inconsistent case, punctuation, emojis, and spelling variants.
- Common cleanup steps:
  - Remove markup when it is not useful.
  - Normalize repeated whitespace and Unicode characters.
  - Standardize case when capitalization does not matter.
  - Replace or remove URLs and other irrelevant artifacts.
- Preserve features that carry meaning:
  - Negation: `not helpful` does not mean `helpful`.
  - Punctuation, emojis, numbers, and capitalization may signal tone or intent.
- Apply the same preprocessing during training and inference.
- Fit transformations using training data only to avoid test-data leakage.

### 3. Tokenization and language processing

- **Tokenization:** splitting text into smaller units.
  - Sentence tokenization: splits into sentences.
  - Word tokenization: splits into words and punctuation.
  - Subword tokenization: splits rare words into reusable pieces; common in language models.
- **N-grams:** consecutive token sequences.
  - Unigram: one token.
  - Bigram: two tokens, e.g. `not good`.
  - Trigram: three tokens.
  - N-grams capture local word order but increase feature count.
- **Stop words:** frequent function words such as “the” and “of.”
  - Removing them may help keyword tasks.
  - Keep them when they affect meaning or task performance.
- **Stemming:** heuristic removal of word endings; may produce non-words.
- **Lemmatization:** maps a word to a dictionary form, often using grammatical context.
- **POS tagging:** assigns grammatical categories such as noun, verb, or adjective.
- **NER (Named Entity Recognition):** identifies names such as people, organizations, places, and dates.
- **Regular expressions (regex):** pattern rules for finding/replacing text such as URLs, digits, or repeated whitespace; test patterns carefully to avoid deleting useful content.
- **Word frequency:** counts how often tokens occur; can reveal common terms but does not capture meaning by itself.
- **Word cloud:** visual summary where frequent terms appear larger; useful for exploration, not a quantitative model or comparison unless settings are controlled.
- **Ambiguity types:**
  - Lexical: a word has more than one meaning.
  - Syntactic: a sentence can have multiple grammatical structures.
  - Referential: it is unclear what a pronoun or phrase refers to.
  - Context helps resolve ambiguity.

### 4. Classical text representations

- **One-hot encoding:** gives each vocabulary item its own binary position; vectors are sparse and do not express similarity between words.
- **Bag of Words (BoW):** represents a document using token counts.
  - Simple and interpretable.
  - Ignores word order and creates sparse vectors.
- **Document-term matrix:**
  - Rows represent documents.
  - Columns represent vocabulary terms/features.
- **TF–IDF:** weights terms by their importance to a document relative to the corpus.
  - Simplified formula: `tf(t,d) × log(N / df(t))`.
  - `tf`: frequency of term `t` in document `d`.
  - `N`: total number of documents.
  - `df(t)`: number of documents containing `t`.
  - Common corpus-wide words receive less weight.
- Fit the vectorizer on training text; use the fitted vectorizer to transform validation/test text.
- **TF (term frequency):** how often a term occurs in a document (sometimes normalized by document length).
- **IDF (inverse document frequency):** downweights terms appearing in many documents.
- **Topic modeling:** unsupervised methods such as LDA look for groups of words that tend to occur together; topics need human interpretation and are not guaranteed to match true themes.

### 5. Text classification and sentiment

- **Use cases:** spam/ham, positive/negative sentiment, topic, or user-intent classification.
- **Typical pipeline:** text → vectorizer → classifier → predicted label.
- **Common baselines:**
  - Multinomial Naive Bayes: fast baseline for count or TF–IDF features.
  - Logistic regression: strong and interpretable text baseline.
  - Neural models: can learn richer representations but need more compute and validation.
- **Good evaluation practice:**
  - Split data before fitting vectorizers or other transformations.
  - Use stratified splits when classes are imbalanced.
  - Compare against a majority-class baseline.
  - Inspect a confusion matrix and individual errors.
- **Metrics:**
  - Accuracy: fraction of all predictions that are correct.
  - Precision: fraction of predicted positives that are truly positive.
  - Recall: fraction of actual positives that are found.
  - F1: harmonic mean of precision and recall.
- Choose metrics according to error costs, such as missed spam versus legitimate mail marked as spam.
- Sentiment methods include word lexicons, classical classifiers, and contextual neural models.
- Difficult cases include sarcasm, mixed sentiment, negation, and domain-specific wording.
- **SMS spam workflow:** inspect label balance → clean message text → vectorize → fit a baseline classifier → inspect false positives/negatives.
- **IMDB review workflow:** remove/normalize markup and text noise → encode/tokenize → pad or truncate sequences to a chosen length → train on training reviews → use validation for model choice → evaluate once on held-out test reviews.
- Review-length distribution matters: truncation may remove evidence; excessive padding wastes compute.
- Inspect individual predictions and a confusion matrix in addition to aggregate accuracy.

### 6. Sequence models and embeddings

- **Embedding:** dense numerical representation of a token or text span.
- Related meanings can be represented by nearby vectors.
- **Static embedding:** one representation for a word across contexts.
- **Contextual representation:** changes according to surrounding words.
- **Word2Vec:** learns word vectors from nearby-word prediction.
  - CBOW predicts a target word from its surrounding context; tends to be efficient for frequent words.
  - Skip-gram predicts surrounding context words from a target; can represent rare words well but may take longer.
- **Keras Embedding layer:** trainable lookup table that maps integer token IDs to dense vectors; embedding weights can be learned with the task or initialized from pretrained vectors.
- **RNN:** processes tokens in sequence and passes a hidden state forward.
- **LSTM:** adds gates to control what information to retain, forget, or expose.
- **Bidirectional LSTM:** reads both left-to-right and right-to-left context; useful when the whole sequence is available, but not for strictly future-blind/causal use.
- Padding and masks help batch sequences with different lengths.
- In IMDB sentiment examples, compare SimpleRNN, LSTM, and BiLSTM using the same split, preprocessing, and training settings for a fair experiment.
- Use early stopping on validation performance; compare learning curves and final test metrics rather than assuming the more complex model wins.

### 7. Semantic search and vector stores

- A vector is any ordered list of numbers; an embedding is a vector produced by a model from input data.
- Semantic search can find related meaning even when query and document use different words.
- **Retrieval workflow:**
  1. Split documents into meaningful chunks.
  2. Create an embedding for each chunk.
  3. Store vectors with metadata.
  4. Embed the user query.
  5. Rank chunks and return top-k results.
- **Cosine similarity:** `(a · b) / (||a|| ||b||)`.
  - Near 1: vectors point in similar directions.
  - Near 0: vectors are orthogonal.
  - Below 0: vectors point in opposing directions.
  - Handle zero vectors explicitly.
- **Brute-force search:** compares against every vector; straightforward but slow at scale.
- **Approximate index:** faster for large collections, with possible loss of exactness.
- **Metadata filters:** restrict retrieval by fields such as date, department, or document type.
- **Pre-filtering:** restrict the candidate set using metadata before vector ranking; improves scope but can reduce recall if filters exclude useful items.
- **Post-filtering:** retrieve/rank first and then filter; may return too few results if many top matches are removed.
- A vector database adds persistent storage, indexing, metadata handling/filtering, and retrieval APIs around vector search; it does not automatically make embeddings or relevance correct.
- Keep a stable mapping between vector rows and document IDs/metadata; verify ordering when using a matrix-based search implementation.
- Similarity is a ranking signal, not proof of relevance; evaluate with real queries and relevance labels.

## Topic 6 — Transformers and Generative Models

### 1. Why Transformers?

- RNNs process tokens in order; long-range dependencies can be difficult to retain.
- Transformers use attention to connect tokens directly.
- Training can process sequence positions in parallel.
- Standard self-attention becomes costly for long sequences because it compares token pairs.

### 2. Self-attention and Transformer blocks

- Each token is projected into:
  - **Query (Q):** what information this token seeks.
  - **Key (K):** what information this token offers for matching.
  - **Value (V):** the information combined after matching.
- Scaled dot-product attention:
  - `softmax(QKᵀ / √dₖ)V`
  - Scaling helps keep dot products manageable for softmax.
- **Multi-head attention:** runs several attention operations in parallel so different heads can learn different relationships.
- Positional encodings/embeddings add token order because attention alone does not know sequence position.
- Transformer blocks commonly include feed-forward layers, residual connections, and normalization.
- **Causal mask:** prevents a decoder from using future tokens.
- Self-attention runs across token positions; multi-head attention learns several relationship patterns in parallel.
- At inference, decoder-only text generation is autoregressive: predict one next token, append it, and repeat until a stopping condition or token limit.

### 3. Transformer families

- **Encoder-only:**
  - Reads both left and right context.
  - Used for classification, tagging, and text representations.
- **Decoder-only:**
  - Uses causal attention to predict the next token.
  - Used for text generation.
- **Encoder-decoder:**
  - Encoder reads input; decoder generates output.
  - Used for translation and summarization.
- **Tokenizer:** converts text to token IDs, often with subword units.
- **Padding:** aligns sequence lengths in a batch.
- **Attention mask:** marks real tokens versus padding.

### 4. BERT

- **BERT:** Bidirectional Encoder Representations from Transformers.
- Encoder-only model that builds contextual representations from both directions.
- **Masked Language Modeling (MLM):** hides selected tokens and predicts them from context.
- **Tokenizer and input fields:**
  - WordPiece/subword tokens map text into vocabulary IDs; one word may become several pieces.
  - `[CLS]` commonly marks the start/sequence-level representation; `[SEP]` separates or ends segments.
  - `input_ids` are token IDs; `attention_mask` distinguishes real tokens from padding.
- **Sequence classification:** predicts one label for the whole input (e.g., sentiment).
- **Token classification:** predicts a label per token (e.g., NER); subword labels must be aligned with original word labels.
- **Sequence classification workflow:**
  1. Tokenize text.
  2. Pass token IDs and attention masks.
  3. Load a pretrained encoder with a task head.
  4. Fine-tune on labeled examples.
  5. Evaluate on held-out data.
- `[CLS]` is commonly used as a sequence-level representation for a classification head.
- `bert-base-uncased` expects lowercase text and its matching tokenizer.
- **DistilBERT:** smaller distilled model; often faster and uses less memory, with a possible quality trade-off.
- A base checkpoint contains general pretrained weights; a task-fine-tuned checkpoint has additionally been trained for a particular task.
- Smaller/optimized variants reduce model size, latency, or memory but may trade off accuracy; benchmark with the required task and hardware.
- Use the tokenizer that matches the selected checkpoint; monitor validation performance to limit overfitting.

### 5. Autoencoders and VAEs

- **Autoencoder structure:** `input x → encoder → latent z → decoder → reconstruction x̂`.
- The encoder compresses; the decoder reconstructs.
- Training minimizes a reconstruction loss, such as mean squared error for continuous inputs.
- Uses:
  - Dimensionality reduction.
  - Feature learning.
  - Denoising.
  - Anomaly detection using unusually high reconstruction error.
- A basic autoencoder may not have a latent space suitable for generating new samples.
- **Variational Autoencoder (VAE):** adds a probabilistic latent space and regularization to support sampling.
  - Encoder predicts latent mean `μ` and log-variance; reparameterization samples `z = μ + σ ε`, where `ε ~ N(0, I)` and `σ = exp(0.5 × log_variance)`.
  - Total loss combines reconstruction loss with KL divergence, which encourages the latent distribution to stay near a chosen prior (commonly standard normal).
  - To generate a new sample, draw a latent vector from the prior and pass it through the decoder.

### 6. Generative Adversarial Networks (GANs)

- **Generator:** maps random noise to synthetic samples.
- **Discriminator:** predicts whether samples are real or generated.
- The generator learns to fool the discriminator; the discriminator learns to detect generated samples.
- Strength: can create sharp samples and generate quickly after training.
- Challenges:
  - Training can be unstable if one network dominates.
  - **Mode collapse:** generator produces limited variety.

### 7. Diffusion models

- **Forward process:** gradually adds noise to training examples.
- **Training:** model learns to predict or remove noise.
- **Generation:** starts from random noise and repeatedly denoises.
- **Latent diffusion:** performs denoising in a compressed representation to reduce computation.
- **Text-to-image flow:**
  1. Text encoder represents the prompt.
  2. Denoising model uses prompt conditioning.
  3. Decoder turns the final latent into an image.
- More denoising steps may refine output but increase runtime.
- Guidance strength affects prompt adherence and variation.
- Negative prompts can guide output but cannot guarantee that a feature is absent.
- **Stable Diffusion components:** text encoder, latent-space denoising network, scheduler/noise schedule, and image decoder/VAE.
- Prompt wording, negative prompt, inference-step count, guidance scale, and random seed affect output; tune one setting at a time when comparing.
- The forward-noising demo illustrates adding noise; a complete generative model also needs a learned reverse-denoising process.

### 8. Audio and multimodal generative AI

- **Text-to-speech (TTS):** converts text to an audio waveform; some systems condition on a speaker embedding to control voice characteristics.
- **Speech-to-text (ASR):** transcribes spoken audio into words; quality depends on accents, background noise, and recording quality.
- **Multimodal/vision-language model:** accepts more than one modality, such as an image and a text question, and returns a text response grounded in visual input.
- Verify generated speech and image-question answers; models can mispronounce, mishear, or misidentify content.
- Check model license, safety limits, privacy, and consent before processing or generating media.

### 9. Generative model comparison

| Model | Main mechanism | Strength | Limitation |
|---|---|---|---|
| Autoencoder | Compress and reconstruct | Compact features | Latent space may not support useful generation |
| VAE | Probabilistic latent plus reconstruction | Structured sampling | Samples may be smoother |
| GAN | Generator competes with discriminator | Sharp, fast samples | Instability and mode collapse |
| Diffusion | Iterative reverse denoising | Quality and diversity | Multiple sampling steps |

- Review generated content for quality, diversity, bias, privacy, safety, licensing, and data rights.

## Topic 7 — LLMs, Prompting, LangChain, and RAG

### 1. LLM basics

- **LLM:** generates text token by token based on patterns learned during training.
- **Token:** model-specific unit such as a word, subword, punctuation mark, or other piece.
- Tokenizers differ by model family; therefore, token counts and token IDs may differ for the same text.
- Common subword approaches:
  - **BPE:** repeatedly merges frequent adjacent token pieces.
  - **Byte-level BPE:** applies BPE over byte representations and can represent arbitrary text.
  - **WordPiece:** learns subword pieces; continuation pieces may be marked with `##` in BERT tokenizers.
  - **SentencePiece:** tokenizer framework that can use BPE or Unigram and can treat whitespace consistently.
  - **Unigram:** begins with candidate pieces and learns a useful probabilistic vocabulary.
- Character/word/whitespace splitting are simple demonstrations; they are not necessarily the model's real tokenizer.
- Input tokens include instructions, user content, history, and retrieved context; generated output also consumes tokens.
- **Context window:** maximum combined input/output capacity for a request.
- **Hallucination:** fluent output that may still contain incorrect or unsupported claims.
- Common message roles:
  - `system`: application-level behavior.
  - `user`: request or data.
  - `assistant`: model response.
  - `tool`: result returned from a tool.
- API formats vary by provider; conversation history usually has to be supplied or managed by the application/session.
- **One-shot generation:** sends one request and receives one output; earlier turns are unavailable unless included in the request.
- **Chat/session API:** accepts role-labelled messages and may provide a helper to manage turns; the application still needs to understand persistence and history behavior.
- Gemini, OpenAI, and Ollama expose different SDKs/endpoints and response shapes, although the shared concepts are messages, model selection, generation settings, and output.
- Ollama runs models locally; its generate-style API takes a prompt while its chat-style API uses role-labelled messages. Local execution still needs model files and compute resources.
- **Temperature:** lower values tend to be more predictable; higher values tend to be more varied. Neither ensures correctness.
- **Streaming:** returns partial output while generation continues.
- **Embedding:** vector for similarity/retrieval; it does not itself generate an answer.
- Related text embeddings can be compared with cosine similarity; use embeddings to retrieve relevant items or cluster texts, not as human-readable feature dimensions.

### 2. Prompt structure

- State the **task** clearly.
- Include necessary **context** or source material.
- Set **constraints:** scope, audience, tone, and length.
- Specify the **output format:** bullets, table, JSON schema, or another structure.
- State what to do if the answer is unknown or absent from supplied sources.
- Clear structured prompts are easier to inspect and maintain than vague instructions.

### 3. Prompting methods

- **Zero-shot prompting:**
  - Give instructions with no examples.
  - Useful for common, straightforward tasks.
  - Short and efficient; may be inconsistent if requirements are vague.
- **One-shot prompting:**
  - Provide one example input and desired output.
  - Useful when one example clarifies a label or format.
  - May not demonstrate edge cases.
- **Few-shot prompting:**
  - Provide multiple examples, ideally covering labels and difficult cases.
  - Can improve consistency without model training.
  - Uses more context tokens; poor examples can bias results.
- **Role/instruction prompting:**
  - Specify a role or behavior, such as “act as a concise code reviewer.”
  - Helps set style and priorities; does not create expertise or authority.
- **Contextual/grounded prompting:**
  - Provide trusted relevant information and direct the model to use it.
  - Ask it to say when the answer is not in the context.
  - Helps ground a response but does not guarantee faithfulness.
- **Structured/constrained prompting:**
  - Request a schema, such as JSON with named fields and allowed values.
  - Validate types, required fields, ranges, and business rules in code.
  - A prompt-only format request can still fail.
- **Task decomposition:**
  - Split a complex task into smaller, checkable steps.
  - Example: extract facts → categorize → summarize.
  - Easier to debug, but extra calls add latency and cost.
- **Chain-of-thought style prompting:**
  - Ask the model to work through a multi-step problem before answering.
  - Can help with some complex tasks, but longer reasoning can also contain errors.
  - Prefer concise explanations and verifiable intermediate results; reasoning text is not proof.
- **Self-consistency:**
  - Generate multiple candidate answers and select/aggregate consistent results.
  - Can help when answers are comparable or verifiable.
  - Uses more compute and agreement can still be wrong.

### 4. Evaluation and output validation

- For classification, use accuracy, precision, recall, F1, and a confusion matrix.
- For generated answers, assess factuality, relevance, completeness, and grounding.
- **BLEU/ROUGE:** compare word or n-gram overlap with reference text.
  - Can penalize valid paraphrases.
  - Do not establish that a response is factually correct.
- **METEOR:** includes stemming and synonym-aware matching, but still relies on reference comparisons.
- **BERTScore:** compares contextual token embeddings to estimate semantic overlap; it can be more paraphrase-aware but may miss factual errors.
- **RAGAS-style evaluation:** evaluates RAG dimensions such as retrieval relevance, faithfulness to retrieved context, and answer quality; automated scores should be checked against human judgments.
- Use human review for nuanced tasks and test realistic edge cases.
- For structured outputs:
  - Parse and validate with code or a schema/Pydantic model.
  - Handle invalid output explicitly.
  - Keep authorization and business decisions in application code.
- For generated code, inspect it and run controlled checks before use.

### 5. LangChain concepts

- LangChain composes model application components into reusable flows.
- Basic chain: `prompt template → chat model → output parser`.
- **Prompt template:** separates fixed instructions from variable inputs.
- **Model wrapper:** provides a common way to call a model.
- **Output parser:** converts model messages into strings or structured values.
- **Runnable/chain:** composes steps; parallel branches can produce independent outputs.
- Common runnable operations include:
  - `invoke`: run one input.
  - `batch`: run multiple inputs.
  - `stream`: receive output chunks progressively.
  - Lambda: wrap ordinary Python logic as a workflow step.
  - Parallel: run independent branches on the same input.
  - Passthrough/assign: preserve original input values while adding derived fields.
- **Message history:** stores conversation turns by session for follow-up requests.
- Production history needs persistence, access control, retention rules, and token-budget management.
- A direct provider SDK is often enough for a small application.

### 6. Retrieval-Augmented Generation (RAG)

- RAG retrieves external evidence and supplies it to the LLM during answer generation.
- **Indexing:**
  1. Gather documents.
  2. Split documents into chunks.
  3. Create embeddings for chunks.
  4. Store vectors with metadata.
- **Question answering:**
  1. Embed the query.
  2. Retrieve top-k relevant chunks.
  3. Optionally apply metadata filters or rerank results.
  4. Put evidence into the prompt.
  5. Generate a response and include sources where useful.
- RAG can connect answers to private or changing data, but does not guarantee accuracy.
- Retrieval quality strongly affects answer quality.
- Tune chunk size/overlap, embedding model, top-k, filters, and reranking.
- Evaluate retrieval relevance separately from answer faithfulness and completeness.
- **Brute-force search:** computes similarity to every stored vector; simple for small collections.
- **Vector index/database:** supports efficient nearest-neighbor retrieval at larger scale, persistence, and metadata filtering; index choice depends on data size and latency/recall needs.
- Pre-filter metadata before retrieval or post-filter results afterward; either choice can affect recall and the number of returned passages.

### 7. Security and reliability

- **Prompt injection:** untrusted text attempts to override instructions or manipulate tools.
- Separate untrusted content from instructions, but do not rely on prompt wording as the security boundary.
- Enforce authorization, access control, tool permissions, and validation in application code.
- Minimize sensitive data sent to providers and review retention settings.
- Plan for latency, quotas, outages, retries, and cost.
- Monitor quality and bias using representative examples.

### 8. Application development workflow (SDLC and Scrum)

- **SDLC:** discover the problem → define requirements/acceptance criteria → design → implement → test → deploy → monitor and improve.
- Work iteratively; test and stakeholder feedback can send changes back to earlier steps.
- **Scrum accountabilities:**
  - Product Owner: orders the backlog to maximize product value.
  - Scrum Master: helps the team apply Scrum and address impediments.
  - Developers: build a usable increment and manage the work needed for the sprint goal.
- **Scrum events:** Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective.
- **Scrum artifacts:** Product Backlog, Sprint Backlog, Increment.
- **Epic:** broad capability split into smaller work items.
- **User story:** “As a [user], I want [capability], so that [benefit].”
- **Acceptance criteria:** observable conditions that define successful behavior.
- Git tracks source changes; branches isolate work, commits record coherent changes, and pull requests support review/collaboration.
- Do not commit secrets such as API keys; use environment variables or approved secret storage.

## Fast revision checklist

- **NLP:** preserve meaning while cleaning; prevent leakage; inspect class errors; test retrieval relevance.
- **Transformers:** attention relates tokens; positional signals add order; BERT is bidirectional encoder-only; GPT-style models predict next tokens.
- **Generative models:** autoencoder reconstructs; GAN uses competition; diffusion denoises iteratively.
- **LLM apps:** specify task/context/format; validate output; provide needed history; retrieve evidence for RAG; enforce security in code.
- **Model evaluation:** distinguish text-overlap scores (BLEU/ROUGE) from semantic metrics and factual/grounding checks.
