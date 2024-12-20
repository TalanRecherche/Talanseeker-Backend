"""Created on Thu Sep 14 13:31:50 2023

@author: agarc

"""

import pandas as pd

from app.core.chatbot_features.scorerprofiles import ScorerProfiles
from app.core.models.scoredprofiles_pandasmodels import ScoredProfilesDF


class ScorerOverall:
    """This class takes case of scoring profiles, all averaging logic bet
    chunks/keywords goes here.
    """

    def __init__(self) -> None:
        self.scorer_profiles = ScorerProfiles()

    # =============================================================================
    # user functions
    # =============================================================================

    def get_overall_scores(
            self,
            df_chunks: pd.DataFrame,
            df_profiles: pd.DataFrame,
            keywords_query: list[str],
            embedded_semantic_query: list[float],
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Scores all profiles and returns their scored dataframe (chunk and
        profiles)
        """
        # get scoring from keywords (using structured profile)
        df_profiles_scored = self.scorer_profiles.score_by_keywords(
            df_profiles,
            keywords_query,
        )
        # get semantic scores (using chunks embeddings)
        df_chunks_semantic_scored = self.scorer_profiles.score_by_semantic(
            df_chunks,
            embedded_semantic_query)
        #
        # df_chunks_semantic_scored =
        # PGfetcher.fetch_selected_chunks(
        #     df_chunks_semantic_scored)

        # df_chunks_semantic_scored = (self.
        # scorer_profiles.score_by_semantic_pg_vector(
        #     embedded_semantic_query))

        # assign embeddings scores to correct profiles
        df_profiles_scored = self.scorer_profiles.assign_scores_to_profiles(
            df_profiles_scored,
            df_chunks_semantic_scored,
        )

        # average keyword/embedding scores
        df_profiles_scored[ScoredProfilesDF.overall_score] = self._average_scores(
            df_profiles_scored,
        )

        return df_chunks_semantic_scored, df_profiles_scored

    # =============================================================================
    # internal functions
    # =============================================================================

    def _average_scores(self, df_profiles_scored: pd.DataFrame) -> pd.Series:
        alpha = 0.5
        beta = 1 - alpha

        average_col = (
                alpha * df_profiles_scored[ScoredProfilesDF.keywords_score_normalized]
                + beta * df_profiles_scored[ScoredProfilesDF.semantic_score_normalized]
        )
        return average_col
