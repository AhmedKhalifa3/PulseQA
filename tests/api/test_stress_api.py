"""
API Audio Pipeline & Stress Benchmarking Test Suite.
Verifies multilingual audio synthesis and telemetry stress triggers.
"""

import pytest

from api.client import PulseApiClient
from api.schemas import SystemHealthResponse, TTSResponse


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.testrail(203)
class TestStressAndAudioApi:

    @pytest.mark.parametrize("lang", ["en", "de", "es", "fr", "ar", "ja"])
    def test_audio_tts_pipeline_multilingual(self, api_client: PulseApiClient, lang: str):
        """
        Validates real-time audio synthesis across 6 supported languages.
        Directly reflects user's TTS pipeline in 6 languages.
        """
        script = f"Testing automated speech conversion in language: {lang}"
        res = api_client.synthesize_audio(text=script, language=lang)
        assert res.status_code == 200

        data = res.json()
        model = TTSResponse(**data)
        assert model.status == "synthesized"
        assert model.language == lang
        assert model.sample_rate == 16000
        assert model.characters_processed == len(script)
        assert model.audio_base64.startswith("data:audio/wav;base64,")

    def test_audio_tts_unsupported_language_rejection(self, api_client: PulseApiClient):
        """Verifies unsupported language codes return 400 Bad Request."""
        res = api_client.synthesize_audio(text="Hello", language="klingon")
        assert res.status_code == 400
        assert "not supported" in res.json()["detail"]

    def test_system_health_telemetry_endpoint(self, api_client: PulseApiClient):
        """Validates system health telemetry API output."""
        res = api_client.get_health()
        assert res.status_code == 200

        data = res.json()
        model = SystemHealthResponse(**data)
        assert model.status == "healthy"
        assert model.memory_rss_mb > 0
        assert model.threads >= 1

    def test_controlled_memory_stress_and_cleanup(self, api_client: PulseApiClient):
        """Verifies memory allocation endpoint and subsequent cleanup cycle."""
        # Allocate 20MB
        res_alloc = api_client.stress_memory(memory_mb=20)
        assert res_alloc.status_code == 200
        assert res_alloc.json()["allocated_mb"] == 20

        # Reset memory
        res_reset = api_client.reset_memory()
        assert res_reset.status_code == 200
        assert res_reset.json()["current_chunks"] == 0
