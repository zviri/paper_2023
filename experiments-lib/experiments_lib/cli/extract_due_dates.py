from typing import Optional, Tuple
from experiments_lib.extractors import DueDateExtractor
from pathlib import Path
from experiments_lib.models.pb.ocr_pb2 import OCRResponse
from experiments_lib.template_tools.template_matcher import TemplateMatcherFactory
from loguru import logger
import click
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd
import os


def extract_due_date(path: Path) -> Tuple[int, Optional[str]]:
    extractor = DueDateExtractor(TemplateMatcherFactory())
    response = OCRResponse()
    file_id = int(path.stem.split(".")[0])
    try:
        response.ParseFromString(path.read_bytes())
        due_date = extractor.extract(response.pages)
        return file_id, due_date
    except Exception as e:
        logger.error(f"Processing of {file_id} failed with {e}")
        return file_id, None


@click.command()
@click.argument("ocr_responses_folder", type=Path)
@click.argument("output_due_dates_path", type=Path)
def main(ocr_responses_folder: Path, output_due_dates_path):
    ocr_response_paths = list(ocr_responses_folder.iterdir())
    logger.info(f"Number of ocr responses found: {len(ocr_response_paths)}")
    with Pool() as pool:
        due_dates = list(
            tqdm(
                pool.imap(extract_due_date, ocr_response_paths),
                total=len(ocr_response_paths),
            )
        )
    due_dates_df = pd.DataFrame(due_dates, columns=["file_id", "due_date"])
    due_dates_df = due_dates_df[due_dates_df.due_date.notna()]
    percentage_found = round(len(due_dates_df) / len(ocr_response_paths) * 100, 2)
    logger.info(
        f"Number of due dates extracted: {len(due_dates_df)} ({percentage_found})"
    )
    logger.info(f"Writing output to: {output_due_dates_path}")
    os.makedirs(output_due_dates_path.parents[0], exist_ok=True)
    due_dates_df.to_parquet(output_due_dates_path)


if __name__ == "__main__":
    main()
