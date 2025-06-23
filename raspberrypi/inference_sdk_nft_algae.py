from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="9k6SBo0cQlOkFConFfVR"
)

result = CLIENT.infer("1747581329747.jpg", model_id="nft-hydroponics-algae/1")
print(result)