import argparse
from pathlib import Path
import logging
import json

from ocr_detection.image_handler import ImageTextDetector


def parse_args():
    """
    Parse command line arguments
    """
    cli = argparse.ArgumentParser()
    cli.add_argument("--model", "-m", default="", help="OCR model.")
    cli.add_argument("--output_dir", "-o", default="", help="Directory to store JSON results.")
    cli.add_argument("--images", "-i", nargs="+", type=str, help="Filepaths to image(s) from which to extract text.")

    return cli.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not args.model:
        print("Must specify --model.")
        exit(1)

    if not args.images:
        print("Must specify at least one image.")
        exit(1)

    output_dir = Path(args.output_dir)
    try:
        detector = ImageTextDetector(logger=logging)
    except ValueError as e:
        print(e)
        exit(1)

    for image in args.images:
        prediction = detector.process_image(image, args.model, local=True)
        if output_dir:
            with open(output_dir.joinpath(Path(image).with_suffix(".json").name), "w") as out_file:
                out_file.write(json.dumps(prediction))
