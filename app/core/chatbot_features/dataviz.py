from collections import defaultdict
from itertools import islice

import pandas as pd

from app.core.chatbot_features.candidate import Candidate, Candidates
from app.core.shared_modules.gpt_backend import GptBackend
from app.core.shared_modules.stringhandler import StringHandler
from app.settings.settings import Settings


class DataViz:
    """class that creates the radarplot of skills based on the profile_pg"""

    def __init__(self, settings: Settings, candidate: Candidate) -> None:
        self.settings = settings
        self.candidate = candidate

        self.df_competences = None
        self.n_top_skills = 6

        self.engine = self.settings.chatbot_ui_settings.dataviz_LLM_model
        self.max_token_in_response = 300
        self.llm_backend = GptBackend(self.engine, self.max_token_in_response)

    def get_df_competence(self) -> pd.DataFrame:
        """Compute score for each skills before plot."""
        # 1 on regroupe les compétences
        clusters_dict = self._cluster_skills_to_dict(self.candidate.skills)
        # 2 on compte les n occurences par compétence
        # pour chaque cluster on demande à un LLM la compétence plausible
        self.df_competences = self._get_from_llm_cluster_id(clusters_dict=clusters_dict)
        # 3 merge duplicate clusters (keys)
        self.df_competences = self._merge_duplicate_clusters(self.df_competences)
        return self.df_competences

    def _cluster_skills_to_dict(self, skills_list: list[str]) -> dict:
        skill_tokens = {skill: set(skill.split()) for skill in skills_list}
        clusters = defaultdict(set)

        for _, tokens in skill_tokens.items():
            matched_skills = [s for s, t in skill_tokens.items() if tokens & t]
            clusters[frozenset(matched_skills)].update(matched_skills)

        # Naming the clusters and converting to the desired dictionary format
        cluster_dict = {}
        for idx, cluster in enumerate(clusters.values()):
            cluster_name = f"cluster_{idx + 1}"
            cluster_dict[cluster_name] = list(cluster)

        sorted_clustered_skills_dict = dict(
            sorted(cluster_dict.items(), key=lambda item: len(item[1]), reverse=True),
        )

        return sorted_clustered_skills_dict

    def _get_from_llm_cluster_id(self, clusters_dict: dict) -> pd.DataFrame:
        list_comp = []

        # get prompt template
        system_function = self.settings.chatbot_ui_settings.dataviz_system_template

        for _, list_skills in islice(clusters_dict.items(), self.n_top_skills):
            query = str(list_skills)
            response = self.llm_backend.send_receive_message(query, system_function)

            comp = {
                "competence": response,
                "n_occurence": len(list_skills),
                "skills": list_skills,
            }

            list_comp.append(comp)

        return pd.DataFrame(list_comp)

    def _merge_duplicate_clusters(self, df_competences: pd.DataFrame) -> pd.DataFrame:
        # prepare output dataframe
        df_competences_filtered = df_competences.copy(deep=True)

        # list competence clusters
        competences = df_competences["competence"].values.tolist()
        competences = [
            StringHandler.normalize_string(competence) for competence in competences
        ]

        # find near-matching clusters (fuzzy string matching)
        nb = len(competences)
        similarity_tuples_list = []
        for ii in range(nb):
            for jj in range(nb):
                if (
                    StringHandler.check_similarity_string(
                        competences[ii],
                        competences[jj],
                        threshold=0.8,
                    )
                    and ii < jj
                ):
                    # We match from top to bottom
                    similarity_tuples_list.append((ii, jj))

        # merge data from identical clusters (ii is pushed to jj)
        for ii, jj in similarity_tuples_list:
            merge_competence = (
                df_competences.loc[jj]["skills"] + df_competences.loc[ii]["skills"]
            )
            df_competences_filtered.at[jj, "skills"] = merge_competence

        # drop rows of identical clusters (ii gets droped, jj is kept)
        index_to_drop = [tup[0] for tup in similarity_tuples_list]
        df_competences_filtered = df_competences_filtered.drop(index_to_drop)

        return df_competences_filtered


def get_skills_table(
    chunks: pd.DataFrame,
    collabs: pd.DataFrame,
    cvs: pd.DataFrame,
    profiles: pd.DataFrame,
) -> dict:
    skills = {}
    settings = Settings()
    candidates = Candidates(chunks, collabs, cvs, profiles)
    for candidate in candidates.list_candidates:
        dataviz = DataViz(settings, candidate)
        df_competences = dataviz.get_df_competence()
        skills[candidate.email] = df_competences
    return skills


# %%
