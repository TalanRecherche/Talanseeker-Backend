from app.core.shared_modules.LLMbackend import LLMBackend
from collections import defaultdict
import os
from itertools import islice

from app.core.shared_modules.stringhandler import StringHandler
from app.core.chatbot_features.candidate import Candidates
from app.core.chatbot_features.candidate import Candidate
import pandas as pd


class DataViz:
    """class that creates the radarplot of skills based on the profile_pg
    """

    def __init__(self, settings, candidate: Candidate) -> None:
        self.settings = settings
        self.candidate = candidate

        self.df_competences = None
        self.n_top_skills = 6

        self.engine = self.settings.chatbot_ui_settings.dataviz_llm_model
        self.max_token_in_response = 300
        self.llm_backend = LLMBackend(self.engine, self.max_token_in_response)

    def get_df_competence(self):
        """compute score for each skills before plot.
        """

        # 1 on regroupe les compétences
        clusters_dict = self._cluster_skills_to_dict(self.candidate.skills)
        # 2 on compte les n occurences par compétence
        # pour chaque cluster on demande à un LLM la compétence plausible
        self.df_competences = self._get_from_llm_cluster_id(clusters_dict=clusters_dict)
        # 3 merge duplicate clusters (keys)
        self.df_competences = self._merge_duplicate_clusters(self.df_competences)
        return self.df_competences

    def _cluster_skills_to_dict(self, skills_list):
        skill_tokens = {skill: set(skill.split()) for skill in skills_list}
        clusters = defaultdict(set)

        for skill, tokens in skill_tokens.items():
            matched_skills = [s for s, t in skill_tokens.items() if tokens & t]
            clusters[frozenset(matched_skills)].update(matched_skills)

        # Naming the clusters and converting to the desired dictionary format
        cluster_dict = {}
        for idx, cluster in enumerate(clusters.values()):
            cluster_name = f"cluster_{idx + 1}"
            cluster_dict[cluster_name] = list(cluster)

        sorted_clustered_skills_dict = dict(sorted(cluster_dict.items(), key=lambda item: len(item[1]), reverse=True))

        return sorted_clustered_skills_dict

    def _get_from_llm_cluster_id(self, clusters_dict):

        list_comp = []

        # get prompt template
        system_function = self.settings.chatbot_ui_settings.dataviz_system_template

        for id_cluster, list_skills in islice(clusters_dict.items(), self.n_top_skills):
            query = str(list_skills)
            response = self.llm_backend.send_receive_message(query, system_function)

            comp = {
                "competence": response,
                "n_occurence": len(list_skills),
                "skills": list_skills
            }

            list_comp.append(comp)

        return pd.DataFrame(list_comp)

    def _merge_duplicate_clusters(self, df_competences: pd.DataFrame) -> pd.DataFrame:
        # prepare output dataframe
        df_competences_filtered = df_competences.copy(deep=True)

        # list competence clusters
        competences = df_competences["competence"].values.tolist()
        competences = [StringHandler.normalize_string(competence) for competence in competences]

        # find near-matching clusters (fuzzy string matching)
        nb = len(competences)
        similarity_tuples_list = []
        for ii in range(nb):
            for jj in range(nb):
                if StringHandler.check_similarity_string(competences[ii], competences[jj], threshold=0.8):
                    # not here we are going to match from top to bottom
                    if ii < jj:
                        similarity_tuples_list.append((ii, jj))

        # merge data from identical clusters (ii is pushed to jj)
        for ii, jj in similarity_tuples_list:
            merge_competence = df_competences.loc[jj]["skills"] + df_competences.loc[ii]["skills"]
            df_competences_filtered.at[jj, "skills"] = merge_competence

        # drop rows of identical clusters (ii gets droped, jj is kept)
        index_to_drop = [tup[0] for tup in similarity_tuples_list]
        df_competences_filtered = df_competences_filtered.drop(index_to_drop)

        return df_competences_filtered


# %%
if __name__ == "__main__":
    from app.settings import Settings

    settings = Settings()

    from app.core.chatbot_app.core.intentionfinder import IntentionFinder
    QUERY_EXAMPLE = "J'ai besoin de trois personnes junior et un manager pour une mission dans la gestion de projet en assurance"
    intention_finder = IntentionFinder(settings)
    guessIntention_query = intention_finder.guess_intention(QUERY_EXAMPLE)
    print(guessIntention_query)

    # fetch from postgres with filters based on query
    from app.core.chatbot_app.core.PGfetcher import PGfetcher
    PGfetcher = PGfetcher(settings)
    df_chunks, df_collabs, df_cvs, df_profiles = PGfetcher.fetch_all()
    print("fetched")

    # select best candidates
    from app.core.chatbot_app.core.candidatesselector import CandidatesSelector
    selector = CandidatesSelector(settings)
    chunks, collabs, cvs, profiles = selector.select_candidates(df_chunks,
                                                                df_collabs,
                                                                df_cvs,
                                                                df_profiles,
                                                                guessIntention_query)
    print("selected")

    candidates = Candidates(chunks, collabs, cvs, profiles)
    for candidate in candidates.list_candidates:
        dataviz = DataViz(settings, candidate)
        df_competences = dataviz.get_df_competence()
        print(df_competences)
