import argparse
import logging

def parse_args():
    """
    Parse command line arguments
    """
    cli = argparse.ArgumentParser()
    cli.add_argument("--models", "-m", nargs="+", type=str, help="Models to download.")

    return cli.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.models:
        for model in args.models:
            if model == "keras_ocr":
                from ocr_detection.keras_ocr_model import KerasOCRPipeline
                KerasOCRPipeline(logging)
            elif model == "paddle_ocr":
                from ocr_detection.paddle_ocr_model import PaddlesOCRPipeline
                PaddlesOCRPipeline(logging)
            else:
                print(f"Invalid model: {model}")
        exit(0)
    else:
        print("Must specify --models.")
        exit(1)
