from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


MODEL_DIR = (
    Path(__file__).resolve().parents[3]
    / "deployment"
    / "embedding_model"
)

MODEL_PATH = MODEL_DIR / "model_quint8_avx2.onnx"
TOKENIZER_PATH = MODEL_DIR / "tokenizer.json"


class ONNXEmbeddingModel:

    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"ONNX model not found: {MODEL_PATH}"
            )

        if not TOKENIZER_PATH.exists():
            raise FileNotFoundError(
                f"Tokenizer not found: {TOKENIZER_PATH}"
            )

        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

        self.session = ort.InferenceSession(
            str(MODEL_PATH),
            sess_options=sess_options,
            providers=["CPUExecutionProvider"],
        )

        self.tokenizer = Tokenizer.from_file(
            str(TOKENIZER_PATH)
        )

        self.tokenizer.enable_truncation(max_length=256)
        self.tokenizer.enable_padding()

        self.dimension = 384

    def encode(
        self,
        sentences,
        convert_to_numpy=True,
        normalize_embeddings=True,
        **kwargs,
    ):
        single_input = isinstance(sentences, str)

        if single_input:
            sentences = [sentences]

        sentences = [
            text if text else ""
            for text in sentences
        ]

        encoded = self.tokenizer.encode_batch(sentences)

        input_ids = np.asarray(
            [item.ids for item in encoded],
            dtype=np.int64,
        )

        attention_mask = np.asarray(
            [item.attention_mask for item in encoded],
            dtype=np.int64,
        )

        token_type_ids = np.asarray(
            [item.type_ids for item in encoded],
            dtype=np.int64,
        )

        outputs = self.session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        token_embeddings = outputs[0]

        mask = attention_mask.astype(np.float32)
        mask = np.expand_dims(mask, axis=-1)

        summed = np.sum(
            token_embeddings * mask,
            axis=1,
        )

        counts = np.clip(
            np.sum(mask, axis=1),
            1e-9,
            None,
        )

        embeddings = summed / counts

        if normalize_embeddings:
            norms = np.linalg.norm(
                embeddings,
                axis=1,
                keepdims=True,
            )

            embeddings = embeddings / np.clip(
                norms,
                1e-12,
                None,
            )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if single_input:
            return embeddings[0]

        return embeddings

    def get_sentence_embedding_dimension(self):
        return self.dimension
