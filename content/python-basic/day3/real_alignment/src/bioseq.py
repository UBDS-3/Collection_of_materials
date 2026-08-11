from itertools import combinations
from typing import Iterable

from Bio.Align import PairwiseAligner
from Bio.Seq import Seq


def translate_dna_sequence(dna_sequence: str, stop_at_stop_codon: bool = True) -> str:
    """
    Translate a DNA sequence into a protein sequence.
    """
    cleaned = dna_sequence.upper().replace("\n", "").replace(" ", "")
    return str(Seq(cleaned).translate(to_stop=stop_at_stop_codon))


def pairwise_identity_score(seq_a: str, seq_b: str) -> float:
    """
    Compute percent identity from a global alignment between two protein sequences.
    """
    if not seq_a and not seq_b:
        return 0.0

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 1
    aligner.mismatch_score = 0
    aligner.open_gap_score = -1
    aligner.extend_gap_score = -1

    best_alignment = aligner.align(seq_a, seq_b)[0]
    matches = 0

    for (start_a, end_a), (start_b, end_b) in zip(*best_alignment.aligned):
        aligned_a = seq_a[start_a:end_a]
        aligned_b = seq_b[start_b:end_b]
        matches += sum(aa == bb for aa, bb in zip(aligned_a, aligned_b))

    return matches / max(len(seq_a), len(seq_b)) * 100.0


def all_pairwise_identity_scores(protein_records: Iterable[tuple[str, str]]) -> list[dict]:
    """
    Compute pairwise identity scores for a collection of named protein sequences.
    """
    results = []
    for (name_a, seq_a), (name_b, seq_b) in combinations(protein_records, 2):
        results.append(
            {
                "seq_a": name_a,
                "seq_b": name_b,
                "identity_score": pairwise_identity_score(seq_a, seq_b),
            }
        )
    return results
