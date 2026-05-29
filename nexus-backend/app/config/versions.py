# Intelligence Pipeline Versioning
# Critical for replay determinism. If extraction or ontology logic changes, 
# bump these versions.

EXTRACTOR_VERSION = "v1.0.0"
NORMALIZER_VERSION = "v1.0.0"
ONTOLOGY_VERSION = "v1.0.0"

def get_current_pipeline_versions() -> dict:
    return {
        "extractor_version": EXTRACTOR_VERSION,
        "normalizer_version": NORMALIZER_VERSION,
        "ontology_version": ONTOLOGY_VERSION
    }
