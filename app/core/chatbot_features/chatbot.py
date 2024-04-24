"""Created on Mon Sep 18 10:57:22 2023

@author: agarc

TDL:
    - implement try/catch assert cases everywhere
    - add logging error while doing it
    -
"""
import re

import pandas as pd

from app.core.models.pg_pandasmodels import CollabPg
from app.core.models.query_pandasmodels import QueryStruct
from app.core.models.scoredprofiles_pandasmodels import ScoredChunksDF, ScoredProfilesDF
from app.core.shared_modules.gpt_backend import GptBackend
from app.core.shared_modules.tokenshandler import TokenHandler
from app.settings import settings


def _make_final_query_string(query_footer: str, query_contexts: dict) -> str:
    final_query_string = ""
    for key in query_contexts:
        final_query_string += "\n" + query_contexts[key]

    final_query_string += "\n" + query_footer
    return final_query_string


class Chatbot:
    def __init__(self) -> None:
        self.system_string = settings.chatbot_settings.chatbot_system_template
        self.context_string = settings.chatbot_settings.chatbot_context_template
        self.query_string = settings.chatbot_settings.chatbot_query_template

        # set llm chatbot engine and encoder
        self.engine = settings.chatbot_settings.chatbot_LLM_model
        # encoding name is used to compute number of tokens in context
        self.encoding_name = settings.embedder_settings.encoding_name

        # set tokens memory of the engine
        if self.engine == "gpt-4-32k":  # this model is rather expensive !
            max_tokens = 30000  # maximum token in llm context
            max_tokens_in_response = 4000  # maximum token in llm response
            buffer_tokens = 8000  # avoid over feeding tokens !
        elif self.engine == "gpt-35-turbo":
            max_tokens = 8000
            max_tokens_in_response = 500  # maximum token in llm response
            buffer_tokens = 4000  # avoid over feeding tokens !
        else:
            max_tokens = 8000
            max_tokens_in_response = 1000
            buffer_tokens = 1000
        # rest of available tokens
        self.max_token_context = max_tokens - max_tokens_in_response - buffer_tokens
        self.current_nb_tokens = 0

        # pass settings to backend
        self.llm_backend = GptBackend(self.engine, max_tokens_in_response)

        # similarity threshold to pass a chunk to the context
        self.similarity_threshold = 0.8  # 0-1 min-max

    # =============================================================================
    # user functions
    # =============================================================================

    def get_chatbot_response(
        self,
        guessintention_query: pd.DataFrame,
        candidates_chunks: pd.DataFrame,
        candidate_collabs: pd.DataFrame,
        candidates_profiles: pd.DataFrame,
    ) -> tuple[str, str] | None:
        """Format queries to fit chunks and information into template.
        Send system and query to the llm
        Args:
            guessintention_query: pd.DataFrame
            candidates_chunks: pd.DataFrame
            candidate_collabs: pd.DataFrame
            candidates_profiles: pd.DataFrame

        Returns: pd.DataFrame

        """
        self.current_nb_tokens = 0
        #Script
        #1 join profile and collabs info
        profiles_collabs = pd.merge(candidate_collabs, candidates_profiles, on="collab_id")

        #2 init
        response = ""
        compteur = 0

        #2 iteration through all profiles 
        for index,row in profiles_collabs.iterrows():

            #1 structured profile inforamtion
            #compte
            compteur += 1
            profile_compte = f"profile {compteur}"

            #get prenom nom
            prenom = row["name"]
            nom = row["surname"]

            #get collab_id
            collab_id = row["collab_id"]

            #get manager
            manager = row["manager"]

            #get dispo 
            availability_score = row["availability_score"]
            availability_date = row["assigned_until"]
            print("availability_date")
            print(type(availability_date))
            print(availability_date)

            #2 call llm to indentify the strength of the profile
            #get top k chunk
            #combien de chunk voulons nous pour construire la réponse du llm
            top_k = 3
            #df du des chunks du candidat
            candidate_chunks = candidates_chunks.loc[candidates_chunks["collab_id"] == collab_id]

            #on extrait les top_k chunks si cela est possible
            if candidate_chunks.shape[0] >= top_k:#pas de souci il y a plus de chunks que le top_k
                top_chunks = candidate_chunks["chunk_text"][:top_k]
            else:#problème il y a moins de chunks que le top_k alors on prend tout
                top_chunks = candidate_chunks["chunk_text"][:]

            #on transforme en liste
            list_top_chunks = top_chunks.to_list()
            #on récupère la user_query
            query_user = guessintention_query["user_query"].values[0][0]
            prompt = f"""
            Vous êtes un assistant d'aide au staffing.
            Vous répondez de manière courte.
            Expliquez en une phrase pourquoi {prenom} {nom} et un bon candidat pour la requête suivante {query_user}.
            Pour expliquer votre réponse vous pouvez vous appuyer sur les 5 passages du cv de {prenom} {nom} :
            {list_top_chunks}
            """
            relevant_qualities_str = self.llm_backend.send_receive_message(query=prompt, system_function="")

            #3 create profile info
            profile_info_str = f"""
            {profile_compte} :
            {prenom} {nom} \n
            disponibilité kimble : {availability_score} %
            disponible à partir du {availability_date}
            manager : {manager}
            cv : 2023-11-09 13_31_47 MOLLIEN Mathieu - CV - 202209.docx

            Qualités :
            {relevant_qualities_str}
            -------------------------------"""

            #add to response
            response += profile_info_str
        #LLM
        #self._relevant_skills(guessintention_query, candidates_chunks, candidate_collabs, candidates_profiles)
        query_string = ""
         

        return response, query_string

    # =============================================================================
    # internal functions
    # =============================================================================
    def _relevant_skills(self, 
                        guessintention_query: pd.DataFrame,
                        candidates_chunks: pd.DataFrame,
                        candidate_collabs: pd.DataFrame,
                        candidates_profiles: pd.DataFrame) -> str:
            # make system function string (contains chunks)
            system_string = self._make_system_string()
            print("")
            print(f"{system_string =}")
            # make query string
            user_query = guessintention_query.iloc[0][QueryStruct.user_query][0]
            query_string = self._make_query_string(
                user_query,
                candidates_chunks,
                candidate_collabs,
                candidates_profiles,
            )
            print("")
            print(f"{query_string =}")

            # get chatbot response
            response = self.llm_backend.send_receive_message(query_string, system_string)
            print("")
            print(f"{response =}")

    def _make_system_string(self) -> str:
        system_string = self.system_string
        # increment number of tokens in context
        self.current_nb_tokens += TokenHandler.count_tokens_from_string(
            system_string,
            self.encoding_name,
            self.engine,
        )
        return system_string

    def _make_query_string(
        self,
        user_query: str,
        candidates_chunks: pd.DataFrame,
        candidate_collabs: pd.DataFrame,
        candidates_profiles: pd.DataFrame,
    ) -> str:
        # make query footer string
        query_string_footer = self._make_query_footer(user_query, candidate_collabs)

        # make context hashmap to hold individual profile subquery
        context_placeholder = self._make_query_context_placeholder(candidates_profiles)
        # place structured data into context_placeholder
        query_structured_info = self._add_structured_info(
            candidate_collabs,
            candidates_profiles,
            context_placeholder,
        )
        # make context string
        query_contexts = self._add_chunks_info(candidates_chunks, query_structured_info)
        # make final query string
        final_query_string = _make_final_query_string(
            query_string_footer,
            query_contexts,
        )

        return final_query_string

    def _make_query_footer(
        self,
        user_query: str,
        candidate_collabs: pd.DataFrame,
    ) -> str:
        # create list of names
        profiles_names = (
            candidate_collabs[CollabPg.surname].values
            + " "
            + candidate_collabs[CollabPg.name].values
        )
        profiles_names = "\n".join(profiles_names)

        # format query
        query_string = self.query_string.format(
            query=user_query,
            profiles_names=profiles_names,
        )

        # increment number of tokens in context
        self.current_nb_tokens += TokenHandler.count_tokens_from_string(
            query_string,
            self.encoding_name,
            self.engine,
        )
        return query_string

    def _make_query_context_placeholder(
        self: str, candidate_collabs: pd.DataFrame
    ) -> dict:
        collab_ids = candidate_collabs[CollabPg.collab_id].unique()
        # query_context_placeholder
        context_placeholder = {
            collab_id: self.context_string for collab_id in collab_ids
        }
        return context_placeholder

    def _add_structured_info(
        self,
        candidate_collabs: pd.DataFrame,
        candidates_profiles: pd.DataFrame,
        context_placeholder: dict,
    ) -> dict[dict]:
        # find profiles to input in query
        collab_ids = candidate_collabs[CollabPg.collab_id].unique()
        # generate headers for each profile
        for idx, collab_id in enumerate(collab_ids):
            current_profile_df = candidates_profiles[
                candidates_profiles[ScoredProfilesDF.collab_id] == collab_id
            ]
            current_collab_df = candidate_collabs[
                candidate_collabs[ScoredProfilesDF.collab_id] == collab_id
            ]
            context_placeholder[collab_id] = context_placeholder[collab_id].format(
                surname=current_collab_df[CollabPg.surname].values[0],
                name=current_collab_df[CollabPg.name].values[0],
                roles=", ".join(current_profile_df[ScoredProfilesDF.roles].values[0]),
                sectors=", ".join(
                    current_profile_df[ScoredProfilesDF.sectors].values[0],
                ),
                company=", ".join(
                    current_profile_df[ScoredProfilesDF.companies].values[0],
                ),
                soft_skills=", ".join(
                    current_profile_df[ScoredProfilesDF.soft_skills].values[0],
                ),
                technical_skills=", ".join(
                    current_profile_df[ScoredProfilesDF.technical_skills].values[0],
                ),
                index=str(idx + 1),
                cv_recap="{cv_recap}",
            )

        # increment number of tokens in context
        self.current_nb_tokens += TokenHandler.count_tokens_from_hashmap(
            context_placeholder,
            self.encoding_name,
            self.engine,
        )
        return context_placeholder

    def _add_chunks_info(
        self,
        candidates_chunks: pd.DataFrame,
        context_placeholder: dict,
    ) -> dict:
        # remove chunks bellow similarity threshold
        filtered_chunks = candidates_chunks[
            candidates_chunks[ScoredChunksDF.semantic_score]
            >= self.similarity_threshold
        ]

        # find profiles to input in query
        collab_ids = candidates_chunks[ScoredChunksDF.collab_id].unique()
        # init placeholder for chunks text
        collab_ids_chunk_hashmap = {collab_id: "" for collab_id in collab_ids}

        while (
            self.current_nb_tokens <= self.max_token_context
            and len(filtered_chunks) > 0
        ):
            for collab_id in collab_ids:
                # filter by profile id
                current_profile_chunks = filtered_chunks[
                    filtered_chunks[ScoredChunksDF.collab_id] == collab_id
                ]
                if current_profile_chunks.empty:
                    continue
                else:
                    # find current best chunk for this profile
                    best_similarity = max(
                        current_profile_chunks[ScoredChunksDF.semantic_score],
                    )
                    # current row
                    current_row = current_profile_chunks[
                        current_profile_chunks[ScoredChunksDF.semantic_score]
                        == best_similarity
                    ]
                    # get the actual chunk
                    chunk_text = str(current_row[ScoredChunksDF.chunk_text].values[0])
                    # clean chunk
                    cleaned_chunks = re.sub(r"\n{3,}", "\n\n", chunk_text) + "\n\n"
                    # get len of chunk
                    chunk_len = TokenHandler.count_tokens_from_string(
                        cleaned_chunks,
                        self.encoding_name,
                        self.engine,
                    )
                    # check if chunk fits in context
                    if (chunk_len + self.current_nb_tokens) <= self.max_token_context:
                        # add the chunk
                        collab_ids_chunk_hashmap[collab_id] += cleaned_chunks
                        # append chunk len to context len
                        self.current_nb_tokens += chunk_len

                    # regardless we remove row from filtered chunks
                    chunk_id = current_row[ScoredChunksDF.chunk_id].values[0]
                    index = filtered_chunks[
                        filtered_chunks[ScoredChunksDF.chunk_id] == chunk_id
                    ].index
                    filtered_chunks = filtered_chunks.drop(index=index)

        # place chunks text in context_placeholder
        for collab_id in collab_ids:
            context_placeholder[collab_id] = context_placeholder[collab_id].replace(
                "{cv_recap}",
                collab_ids_chunk_hashmap[collab_id],
            )
            # remove trailing \n
            context_placeholder[collab_id] = context_placeholder[collab_id].strip("\n")

        return context_placeholder
