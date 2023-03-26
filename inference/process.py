from typing import List

from inference.prompts import (extra_info_chain, group_chain, lookback_chain,
                               new_sum_chain, purpose_chain, synth_chain,
                               synth_combo_chain, tid_chain)


def generate_initial_bullets(news_article: str, persona: str) -> List[str]:
    """Generate initial bullets."""
