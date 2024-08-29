import json
import os
import socket
import sys
import uuid

import mlflow

sys.path.append(os.path.join(os.getcwd(), 'app'))

from jsonschema import Draft7Validator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.chatbot_features.intentionfinder import IntentionFinder
from app.settings.settings import Settings
from app.core.azure_modules import azure_ml_manager
from langfuse.decorators import langfuse_context, observe

# Load the sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Define the JSON schema
schema = {
    "type": "object",
    "properties": {
        "simplified_query": {"type": "string"},
        "sectors": {"type": "string"},
        "companies": {"type": "string"},
        "roles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string"},
                    "nb_profiles": {"type": "string"},
                    "years": {"type": ["string", "null"]},
                    "diplomas_certifications": {"type": ["string", "null"]},
                    "soft_skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "technical_skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "missions": {"type": "string"}
                },
                "required": ["role", "nb_profiles", "years", "diplomas_certifications", "soft_skills", "technical_skills", "missions"]
            }
        }
    },
    "required": ["simplified_query", "sectors", "companies", "roles"]
}

settings = Settings()
intention_finder = IntentionFinder()

def transform_dataframe_to_dict(df):
    transformed_dict = {
        'simplified_query': df['simplified_query'].iloc[0][0],
        'sectors': df['sectors'].iloc[0][0],
        'companies': df['companies'].iloc[0][0],
        'roles': []
    }

    for index, row in df.iterrows():
        role_info = {
            'role': row['roles'][0],
            'nb_profiles': row['nb_profiles'][0],
            'years': row['years'][0],
            'diplomas_certifications': row['diplomas_certifications'][0],
            'soft_skills': row['soft_skills'][0].split(','),
            'technical_skills': row['technical_skills'][0].split(','),
            'missions': row['missions'][0]
        }
        transformed_dict['roles'].append(role_info)

    return transformed_dict

def cosine_similarity_score(text1, text2):
    """Compute the cosine similarity between two texts using sentence embeddings."""
    embeddings = model.encode([text1, text2])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def count_schema_properties(schema):
    """Count the number of properties defined in the schema, including nested properties."""
    count = 0
    if "properties" in schema:
        count += len(schema["properties"])
        for key, value in schema["properties"].items():
            if value["type"] == "array" and "items" in value:
                count += count_schema_properties(value["items"])
            elif value["type"] == "object":
                count += count_schema_properties(value)
    return count

def count_instance_properties(instance):
    """Count the number of properties in the instance, including nested properties."""
    count = 0
    if isinstance(instance, dict):
        count += len(instance)
        for value in instance.values():
            if isinstance(value, dict):
                count += count_instance_properties(value)
            elif isinstance(value, list):
                for item in value:
                    count += count_instance_properties(item)
    return count

def validate_schema(instance, schema):
    """Validate the instance against the schema and count errors."""
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return len(errors)

def evaluate_response(expected, actual):
    score = {
        "completeness": 0,
        "similarity": 0,
        "syntax": 0
    }

    # JSON schema validation for syntax score
    total_properties = count_schema_properties(schema)
    schema_errors = validate_schema(actual, schema)
    valid_properties = total_properties - schema_errors
    score['syntax'] = (valid_properties / total_properties) * 20  # Total syntax score is 20

    # Completeness
    expected_properties = count_instance_properties(expected)
    actual_properties = count_instance_properties(actual)
    score['completeness'] = min((actual_properties / expected_properties) * 20, 20)  # Total completeness score is 20

    # Penalty for too many roles
    expected_roles_count = len(expected['roles'])
    actual_roles_count = len(actual['roles'])
    if actual_roles_count > expected_roles_count:
        penalty = (actual_roles_count - expected_roles_count) / actual_roles_count * 10  # Penalty weight can be adjusted
        score['completeness'] = max(0, score['completeness'] - penalty)

    # Similarity
    similarity_score = 0

    # Compare sectors
    sector_similarity = cosine_similarity_score(expected['sectors'], actual.get('sectors', ''))
    similarity_score += sector_similarity

    # Compare companies
    company_similarity = cosine_similarity_score(expected['companies'], actual.get('companies', ''))
    similarity_score += company_similarity

    # Compare roles
    expected_roles = expected['roles']
    actual_roles = actual['roles']

    for expected_role in expected_roles:
        for actual_role in actual_roles:
            role_similarity = cosine_similarity_score(expected_role['role'], actual_role['role'])
            similarity_score += role_similarity

            if role_similarity > 0.8:

                # Check nb_profiles
                if expected_role['nb_profiles'] == actual_role['nb_profiles']:
                    similarity_score += 1

                # Check years
                if expected_role['years'] == actual_role.get('years', 'Non renseigné'):
                    similarity_score += 1

                # Check missions
                if cosine_similarity_score(expected_role['missions'], actual_role['missions']) > 0.8:
                    similarity_score += 1

                # Check soft_skills
                if cosine_similarity_score(' '.join(expected_role['soft_skills']), ' '.join(actual_role['soft_skills'])) > 0.8:
                    similarity_score += 1

                # Check technical_skills
                if cosine_similarity_score(' '.join(expected_role['technical_skills']), ' '.join(actual_role['technical_skills'])) > 0.8:
                    similarity_score += 1

    score['similarity'] = (similarity_score / ((len(expected_roles) * 6) + 2)) * 60  # 5 criteria per role + 2 (sectors and companies), total similarity score is 60

    score['total_score'] = score['completeness'] + score['similarity'] + score['syntax']
    return score

@observe()
def test_01_structured_query_format(request: any, session_id: str) -> None:
    global settings
    global intention_finder

    user_query = request.pop("user_query")
    expected_response = request
    actual_response = transform_dataframe_to_dict(intention_finder.guess_intention(user_query))

    langfuse_context.update_current_observation(
        output=actual_response
    )

    scores = evaluate_response(expected_response, actual_response)

    from langfuse import Langfuse
    langfuse = Langfuse()

    for score_k, score_v in scores.items():
        langfuse.score(
            name=score_k,
            trace_id=langfuse_context.get_current_trace_id(),
            value=score_v
        )

    langfuse_context.update_current_trace(
        name="Trace generated by test_intentionfinder python test execution",
        session_id=session_id,
        user_id=socket.gethostname(),
        tags=["pytest", "test_intentionfinder", model_name],
        metadata={
            "file": "test_eval.py"
        },
        public=True
    )

    return scores, actual_response



def custom_evaluate_function(data, session_id):
    """
    Custom evaluation function to evaluate model responses.
    """
    evaluations = []
    responses = []

    for request in data.get("requests"):
        scores, actual_response = test_01_structured_query_format(request, session_id)
        evaluations.append(scores)
        responses.append(actual_response)

    # Average the scores across all requests
    average_scores = {
        "completeness": sum(e["completeness"] for e in evaluations) / len(evaluations),
        "similarity": sum(e["similarity"] for e in evaluations) / len(evaluations),
        "syntax": sum(e["syntax"] for e in evaluations) / len(evaluations),
        "total_score": sum(e["total_score"] for e in evaluations) / len(evaluations)
    }

    return average_scores, evaluations, responses

if __name__ == "__main__":

    model_name = os.getenv("MLFLOW_MODEL")
    model_endpoint = os.getenv("MLFLOW_OPENAI_ENDPOINT")
    session_id = f"session-{uuid.uuid4()}-eval-{model_name}"
    with open('evals/data/intentionfinder_dataset.json', encoding='utf-8') as f:
        data = json.load(f)

    mlflow.set_experiment("intention_finder")
    mlflow.set_experiment_tag("model_name", model_name)

    with mlflow.start_run():

        mlflow.log_param("model_name", model_name)
        mlflow.log_param("session_id", session_id)

        average_scores, evaluation_results, responses = custom_evaluate_function(data, session_id)

        mlflow.log_metrics(average_scores)

        result = {"requests": [{**d1, "output":{**d3},"scores": {**d2}} for d1, d2, d3 in zip(data.get("requests"), evaluation_results, responses)]}

        mlflow.log_dict(result, "result.json")


    print(f"Evaluation Results: {evaluation_results}")
