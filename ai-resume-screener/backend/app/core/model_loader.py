import gc
import json
from functools import lru_cache

import faiss
import joblib

from app.core.config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    EXPECTED_FAISS_VECTORS,
    EXPECTED_FEATURE_COUNT,
    EXPECTED_KMEANS_CLUSTERS,
    FAISS_INDEX_FILE,
    FEATURE_COLUMNS_FILE,
    IMPUTATION_VALUES_FILE,
    JOBS_FILE,
    KMEANS_FILE,
    RANDOM_FOREST_FILE,
    RESUMES_FILE,
    SKILL_NORMALIZATION_FILE,
)
from app.core.onnx_embedding import ONNXEmbeddingModel


def _load_artifact(path):
    """Load a Joblib/Pickle deployment artifact."""
    return joblib.load(path)


def _load_resumes_compact(path):
    """Load resumes while keeping only candidate_id and filename to drastically reduce RAM usage."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    compact = []
    for item in data:
        if isinstance(item, dict):
            compact.append({
                "candidate_id": item.get("candidate_id") or item.get("resume_id") or item.get("id"),
                "filename": item.get("filename") or item.get("file_name") or item.get("resume_filename") or "Resume",
            })
        else:
            compact.append(item)
    del data
    gc.collect()
    return compact


def _load_jobs_compact(path):
    """Load jobs lightweight structure for count retrieval."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    count = len(data) if isinstance(data, list) else 0
    del data
    gc.collect()
    return [{"id": i} for i in range(count)]


@lru_cache(maxsize=1)
def get_model_bundle():

    artifact_paths = {
        "resumes": RESUMES_FILE,
        "jobs": JOBS_FILE,
        "faiss_index": FAISS_INDEX_FILE,
        "random_forest": RANDOM_FOREST_FILE,
        "feature_columns": FEATURE_COLUMNS_FILE,
        "kmeans": KMEANS_FILE,
        "imputation_values": IMPUTATION_VALUES_FILE,
        "skill_normalization": SKILL_NORMALIZATION_FILE,
    }

    missing = [
        name
        for name, path in artifact_paths.items()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing deployment artifacts: "
            + ", ".join(missing)
        )

    # --------------------------------------------------------
    # JSON (Memory-optimized)
    # --------------------------------------------------------

    resumes = _load_resumes_compact(RESUMES_FILE)
    jobs = _load_jobs_compact(JOBS_FILE)

    # --------------------------------------------------------
    # FAISS
    # --------------------------------------------------------

    faiss_index = faiss.read_index(
        str(FAISS_INDEX_FILE)
    )

    # --------------------------------------------------------
    # Joblib artifacts
    # --------------------------------------------------------

    random_forest_model = _load_artifact(
        RANDOM_FOREST_FILE
    )

    feature_columns = _load_artifact(
        FEATURE_COLUMNS_FILE
    )

    kmeans_model = _load_artifact(
        KMEANS_FILE
    )

    imputation_values = _load_artifact(
        IMPUTATION_VALUES_FILE
    )

    skill_normalization = _load_artifact(
        SKILL_NORMALIZATION_FILE
    )

    # --------------------------------------------------------
    # Embedding model
    # --------------------------------------------------------

    embedding_model = ONNXEmbeddingModel()

    # Force garbage collection to free initial loading buffers
    gc.collect()

    # --------------------------------------------------------
    # Artifact validation
    # --------------------------------------------------------

    if len(feature_columns) != EXPECTED_FEATURE_COUNT:
        raise ValueError(
            f"Unexpected feature count: {len(feature_columns)}; "
            f"expected {EXPECTED_FEATURE_COUNT}"
        )

    if faiss_index.d != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Unexpected FAISS dimension: {faiss_index.d}; "
            f"expected {EMBEDDING_DIMENSION}"
        )

    if faiss_index.ntotal != EXPECTED_FAISS_VECTORS:
        raise ValueError(
            f"Unexpected FAISS vector count: {faiss_index.ntotal}; "
            f"expected {EXPECTED_FAISS_VECTORS}"
        )

    if getattr(kmeans_model, "n_clusters", None) != (
        EXPECTED_KMEANS_CLUSTERS
    ):
        raise ValueError(
            f"Unexpected KMeans cluster count: {getattr(kmeans_model, 'n_clusters', None)}; "
            f"expected {EXPECTED_KMEANS_CLUSTERS}"
        )

    embedding_dimension = (
        embedding_model.get_sentence_embedding_dimension()
    )

    if embedding_dimension != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Unexpected embedding dimension: {embedding_dimension}; "
            f"expected {EMBEDDING_DIMENSION}"
        )

    return {
        "resumes": resumes,
        "jobs": jobs,
        "faiss_index": faiss_index,
        "random_forest_model": random_forest_model,
        "feature_columns": feature_columns,
        "kmeans_model": kmeans_model,
        "imputation_values": imputation_values,
        "skill_normalization": skill_normalization,
        "embedding_model": embedding_model,
    }
