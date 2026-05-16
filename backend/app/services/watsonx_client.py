"""Watsonx.ai client for AI-powered documentation generation"""

from typing import Optional, Dict, Any, List
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference, Embeddings
from ibm_watsonx_ai.metanames import (
    GenTextParamsMetaNames as GenParams,
    EmbedTextParamsMetaNames as EmbedParams,
)

from app.config import settings


class WatsonxClient:
    """Client for interacting with IBM watsonx.ai"""

    def __init__(self):
        self.api_key = settings.watsonx_api_key
        self.project_id = settings.watsonx_project_id
        self.url = settings.watsonx_url
        self.model_id = settings.watsonx_model_id
        self.embedding_model_id = settings.watsonx_embedding_model_id
        self.answering_model_id = settings.watsonx_answering_model_id

        self._client: Optional[APIClient] = None
        self._model: Optional[ModelInference] = None
        self._embedding_client: Optional[Embeddings] = None
        self._answering_model: Optional[ModelInference] = None

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _get_client(self) -> APIClient:
        if not self.api_key or not self.project_id:
            raise ValueError(
                "Watsonx.ai credentials not configured. "
                "Please set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env"
            )
        if self._client is None:
            credentials = Credentials(url=self.url, api_key=self.api_key)
            self._client = APIClient(credentials)
        return self._client

    def _ensure_connected(self):
        """Ensure default model client is connected (used by generate_text)."""
        client = self._get_client()
        if self._model is None:
            self._model = ModelInference(
                model_id=self.model_id,
                api_client=client,
                project_id=self.project_id,
                params={
                    GenParams.MAX_NEW_TOKENS: settings.max_tokens,
                    GenParams.TEMPERATURE: settings.temperature,
                    GenParams.TOP_P: 0.9,
                    GenParams.TOP_K: 50,
                },
            )

    def _get_embedding_client(self) -> Embeddings:
        client = self._get_client()
        if self._embedding_client is None:
            self._embedding_client = Embeddings(
                model_id=self.embedding_model_id,
                api_client=client,
                project_id=self.project_id,
                params={EmbedParams.TRUNCATE_INPUT_TOKENS: 512},
            )
        return self._embedding_client

    def _get_answering_model(self) -> ModelInference:
        client = self._get_client()
        if self._answering_model is None:
            self._answering_model = ModelInference(
                model_id=self.answering_model_id,
                api_client=client,
                project_id=self.project_id,
            )
        return self._answering_model

    # ── Public API ─────────────────────────────────────────────────────────────

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using the IBM granite-embedding model.
        Returns a list of float vectors, one per input text.
        """
        embeddings_client = self._get_embedding_client()
        try:
            return embeddings_client.embed_documents(texts=texts)
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {e}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        """
        Send a chat request to the answering model (llama-3-3-70b-instruct).
        messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
        Returns the assistant reply string.
        """
        model = self._get_answering_model()
        try:
            response = model.chat(
                messages=messages,
                params={
                    GenParams.MAX_NEW_TOKENS: max_tokens,
                    GenParams.TEMPERATURE: temperature,
                },
            )
            choices = response.get("choices", [])
            if not choices:
                raise ValueError("Empty choices in chat response")
            return choices[0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate chat response: {e}")

    def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate text using the default model (used for documentation generation)."""
        self._ensure_connected()

        params = {
            GenParams.MAX_NEW_TOKENS: max_tokens or settings.max_tokens,
            GenParams.TEMPERATURE: temperature or settings.temperature,
            GenParams.TOP_P: 0.9,
            GenParams.TOP_K: 50,
        }

        try:
            model = ModelInference(
                model_id=self.model_id,
                api_client=self._client,
                project_id=self.project_id,
                params=params,
            )
            response = model.generate_text(prompt=prompt)
            return response.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate text: {str(e)}")

    def generate_batch(
        self,
        prompts: List[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> List[str]:
        """Generate text for multiple prompts sequentially."""
        results = []
        for prompt in prompts:
            try:
                result = self.generate_text(prompt, max_tokens, temperature)
                results.append(result)
            except Exception as e:
                print(f"Warning: Failed to generate for prompt: {e}")
                results.append("")
        return results

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to watsonx.ai."""
        try:
            self._ensure_connected()
            response = self.generate_text("Hello, this is a test.", max_tokens=10)
            return {
                "status": "connected",
                "model_id": self.model_id,
                "project_id": self.project_id,
                "test_response": response,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global client instance
watsonx_client = WatsonxClient()

# Made with Bob
