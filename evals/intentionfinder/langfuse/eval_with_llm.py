import argparse
import os
from typing import Optional

from dotenv import load_dotenv
from langchain.evaluation import load_evaluator
from langchain.evaluation.criteria import LabeledCriteriaEvalChain
from langchain_mistralai.chat_models import ChatMistralAI

from langfuse import Langfuse


class Evaluator:

    def __init__(self) -> None:
        self.langfuse = Langfuse()
        self.langfuse.auth_check()
        self.EVAL_TYPES={
            "hallucination": True,
            "conciseness": True,
            "relevance": True,
            "coherence": True,
            "harmfulness": True,
            "maliciousness": True,
            "helpfulness": True,
            "controversiality": True,
            "misogyny": True,
            "criminality": True,
            "insensitivity": True
        }
        self.llm = ChatMistralAI(endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                     mistral_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                     temperature=0,
                    )



    def fetch_generations(self,
                          page: Optional[int] = None,
                          limit: Optional[int] = 50,
                          name: Optional[str] = None,
                          user_id: Optional[str] = None,
                          trace_id: Optional[str] = None,
                          parent_observation_id: Optional[str] = None
                        ) -> list:
        all_data = []

        if page is None:
            page = 1
            while True:
                response = self.langfuse.get_generations(
                    page=page,
                    limit=limit,
                    name=name,
                    user_id=user_id,
                    trace_id=trace_id,
                    parent_observation_id=parent_observation_id
                )
                if not response.data:
                    break

                all_data.extend(response.data)
                page += 1
        else:
            response = self.langfuse.get_generations(
                page=page,
                limit=limit,
                name=name,
                user_id=user_id,
                trace_id=trace_id,
                parent_observation_id=parent_observation_id
            )
            if response.data:
                all_data.extend(response.data)

        self.generations=all_data

    def get_evaluator_for_key(self,key: str) -> any:
        return load_evaluator("criteria", criteria=key, llm=self.llm)

    def get_hallucination_eval(self) -> any:
        criteria = {
            "hallucination": (
            "Does this submission contain information"
            " not present in the input or reference?"
            ),
        }
        llm = self.llm

        return LabeledCriteriaEvalChain.from_llm(
            llm=llm,
            criteria=criteria,
        )


    def eval_hallucination(self) -> any:

        chain = self.get_hallucination_eval()

        for generation in self.generations:
            eval_result = chain.evaluate_strings(
                prediction=generation.output,
                input=generation.input,
                reference=generation.input
            )
            print(eval_result)
            if eval_result is not None and eval_result["score"] is not None and eval_result["reasoning"] is not None:
                self.langfuse.score(name="hallucination",
                                    trace_id=generation.trace_id,
                                    observation_id=generation.id,
                                    value=eval_result["score"],
                                    comment=eval_result["reasoning"])


    def execute_eval_and_score(self) -> any:

        for generation in self.generations:
            criteria = [key for key, value in self.EVAL_TYPES.items() if value and key != "hallucination"]

            for criterion in criteria:
                eval_result = self.get_evaluator_for_key(criterion).evaluate_strings(
                    prediction=generation.output,
                    input=generation.input,
                )
                self.langfuse.score(name=criterion,
                                    trace_id=generation.trace_id,
                                    observation_id=generation.id,
                                    value=eval_result["score"],
                                    comment=eval_result["reasoning"])

        if self.EVAL_TYPES.get("hallucination") is True:
            self.eval_hallucination()

        self.langfuse.flush()


def main( page: Optional[int],
          limit: Optional[int],
          name: Optional[str],
          user_id: Optional[str],
          trace_id: Optional[str],
          parent_observation_id: Optional[str]
          ) -> None:

    load_dotenv()

    evaluator = Evaluator()
    evaluator.fetch_generations(
        page=page,
        limit=limit,
        name=name,
        user_id=user_id,
        trace_id=trace_id,
        parent_observation_id=parent_observation_id
    )
    evaluator.execute_eval_and_score()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get a list of generations in the current project matching the given parameters.")  # noqa: E501
    parser.add_argument("--page", type=int, help="Page number of the generations to return. Defaults to None.")  # noqa: E501
    parser.add_argument("--limit", type=int, help="Maximum number of generations to return. Defaults to None.")  # noqa: E501
    parser.add_argument("--name", type=str, help="Name of the generations to return. Defaults to None.")  # noqa: E501
    parser.add_argument("--user_id", type=str, help="User identifier of the generations to return. Defaults to None.")  # noqa: E501
    parser.add_argument("--trace_id", type=str, help="Trace identifier of the generations to return. Defaults to None.")  # noqa: E501
    parser.add_argument("--parent_observation_id", type=str, help="Parent observation identifier of the generations to return. Defaults to None.")  # noqa: E501

    args = parser.parse_args()

    main(args.page, args.limit, args.name, args.user_id, args.trace_id, args.parent_observation_id)
