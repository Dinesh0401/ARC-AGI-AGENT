"""Standalone Kaggle notebook submission entry point script."""

from submission.kaggle_runner import KaggleSubmissionRunner
from benchmark.config import DEFAULT_GAMES


def main() -> None:
    print("================ KAGGLE SUBMISSION RUNNER ================")
    runner = KaggleSubmissionRunner()
    output_path = runner.generate_submission(game_ids=DEFAULT_GAMES)
    print(f"Submission payload generated successfully: {output_path}")
    print("==========================================================")


if __name__ == "__main__":
    main()
