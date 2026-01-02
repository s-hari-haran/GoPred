"""Main entry point for portfolio optimisation."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from src.extractor import extract_data
from src.model import ProphetModel
from src.optimiser import optimize_portfolio_mean_variance
from src.processor import append_predictions, collect_recent_prices, preprocess_data
from src.settings import END_DATE, PORTFOLIO_TICKERS, START_DATE

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Local data file path
DATA_FILE = Path(__file__).parent / "data" / "predictions.json"


def save_results_to_json(result: dict[str, Any]) -> None:
    """Save optimisation results to local JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing data
    existing_data = []
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []
    
    # Prepare new record
    as_of_date = result.get("date")
    predictions = result.get("predictions", {})
    predicted_returns = result.get("predicted_returns", {})
    weights = result.get("weights", {})
    actual_prices_last_month = result.get("actual_prices_last_month", {})
    
    # Create rows for each ticker
    new_rows = []
    for ticker in predictions.keys():
        row = {
            "as_of_date": as_of_date.isoformat() if isinstance(as_of_date, date) else str(as_of_date),
            "ticker": ticker,
            "predicted_price": float(predictions.get(ticker, 0.0)),
            "predicted_return": float(predicted_returns.get(ticker, 0.0)),
            "actual_prices_last_month": actual_prices_last_month.get(ticker, []),
            "portfolio_weight": float(weights.get(ticker, 0.0)),
        }
        new_rows.append(row)
    
    # Remove old entries for the same date (update instead of duplicate)
    date_str = as_of_date.isoformat() if isinstance(as_of_date, date) else str(as_of_date)
    existing_data = [r for r in existing_data if r.get("as_of_date") != date_str]
    
    # Add new rows
    existing_data.extend(new_rows)
    
    # Save to file
    with open(DATA_FILE, "w") as f:
        json.dump(existing_data, f, indent=2)
    
    logger.info(f"Saved {len(new_rows)} predictions to {DATA_FILE}")


def run_optimisation(
    tickers: list[str],
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> dict[str, Any]:
    """
    Run portfolio optimisation: pull data, predict, calculate allocation, and log result.

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date for historical data (YYYY-MM-DD format). Defaults to START_DATE.
        end_date: End date for historical data (YYYY-MM-DD format). Defaults to END_DATE.

    Returns:
        Dictionary containing optimisation results with keys:
        - date: date object representing date optimisation was run
        - prediction_date: date object for the prediction (next day after last historical date)
        - predictions: dict[str, float] of predicted prices for each ticker
        - current_prices: dict[str, float] of current prices for each ticker
        - predicted_returns: dict[str, float] of predicted returns for each ticker
        - weights: dict[str, float] of optimal portfolio weights for each ticker

    Returns empty dict if data extraction fails.
    """

    as_of_date = pd.to_datetime(end_date).date()
    logger.info(f"Starting portfolio optimisation for tickers: {tickers} as of {as_of_date}")

    # 1. Extract historical data
    logger.info("Extracting historical data...")
    all_stock_data = extract_data(tickers, start_date=start_date, end_date=end_date)
    if not all_stock_data:
        logger.warning("No data extracted. Exiting optimisation.")
        return {}

    # 2. Preprocess historical data
    logger.info("Preprocessing data...")
    portfolio_data = preprocess_data(all_stock_data)

    # 3. Predict next step using Prophet
    logger.info("Generating predictions...")
    model = ProphetModel()
    predictions, predicted_returns = model.predict_for_tickers(portfolio_data)

    # 4. Collect actual price history for the past month
    actual_prices_last_month = collect_recent_prices(portfolio_data)

    # 5. Append predictions to historical data
    predicted_data = append_predictions(portfolio_data, predictions, predicted_returns)

    # 6. Optimise portfolio using predicted returns as expected returns
    logger.info("Calculating optimal portfolio allocation...")
    weights_dict = optimize_portfolio_mean_variance(predicted_data)

    # 7. Log results
    logger.info("Portfolio Optimisation Results")
    logger.info(f"Date: {as_of_date}")

    logger.info("\nPredicted Prices (Next Day):")
    for ticker, price in predictions.items():
        logger.info(f"  {ticker}: ${price:.2f}")

    logger.info("\nPredicted Returns:")
    for ticker, ret in predicted_returns.items():
        logger.info(f"  {ticker}: {ret * 100:.2f}%")

    logger.info("\nOptimal Portfolio Weights:")
    for ticker, weight in weights_dict.items():
        logger.info(f"  {ticker}: {weight * 100:.2f}%")

    return {
        "date": as_of_date,
        "predictions": predictions,
        "predicted_returns": predicted_returns,
        "actual_prices_last_month": actual_prices_last_month,
        "weights": weights_dict,
    }


def main() -> None:
    """Main CLI entry point - saves results to local JSON file."""
    try:
        result = run_optimisation(tickers=PORTFOLIO_TICKERS)

        if not result:
            logger.error("Optimisation returned empty result")
            sys.exit(1)

        save_results_to_json(result)
        print("\n✅ Results successfully saved! View them at http://localhost:8501")

    except Exception as e:
        logger.error(f"Error during optimisation: {e}")
        print(f"Error during optimisation: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
