"""Predictive segment inference router with calibrated soft membership probabilities."""

from fastapi import APIRouter, HTTPException

from apps.api.schemas.common import ResponseMetadata
from apps.api.schemas.predictions import SegmentPredictionRequest, SegmentPredictionResponse
from apps.api.services.model_service import model_service

router = APIRouter(prefix="/api/v1/predict", tags=["Segment Prediction & Inference"])


@router.post(
    "/segment",
    response_model=SegmentPredictionResponse,
    summary="Predict Buyer Segment from Portfolio Architecture Attributes",
)
async def predict_segment(request: SegmentPredictionRequest) -> SegmentPredictionResponse:
    """Predict buyer segment assignment with calibrated soft membership probabilities.

    PORTFOLIO REQUIREMENT NOTICE:
    Model B3 operates on behavioral portfolio features (unit volume, commercial share,
    tower diversification, purchase timeline). Portfolio inputs are strictly required
    because the production model was trained on them.
    """
    try:
        payload = request.model_dump()
        res = model_service.predict_segment(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {e}") from e

    metadata = ResponseMetadata(
        as_of="December 2025",
        is_unfiltered_model_space=True,
        untested_assumptions_notice=(
            "Calibrated centroid-softmax temperature beta=1.00; soft behavioral tendencies framing; "
            "classification requires behavioral portfolio attributes."
        ),
        notices=[
            "Monetary figures in INR (₹). Currency is a labeling convention and is independent of country."
        ],
    )

    return SegmentPredictionResponse(
        predicted_segment_id=res["predicted_segment_id"],
        predicted_segment_name=res["predicted_segment_name"],
        calibrated_soft_probabilities=res["calibrated_soft_probabilities"],
        temperature_beta=res["temperature_beta"],
        is_ambiguous_prediction=res["is_ambiguous_prediction"],
        portfolio_requirement_rationale=res["portfolio_requirement_rationale"],
        metadata=metadata,
    )
