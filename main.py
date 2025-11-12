import asyncio
import json
import logging
import os

from aiolimiter import AsyncLimiter
from Data_Enrichment_Google.enrichment1 import run_enrichment as g_enrichment, compare_companies
from pathlib import Path
from Processor.checkpoint_processor import ProcessingState
from Processor.data_pipeline import DataPipeline


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("processing.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CONFIG = {
    "FILE_PATH": Path("data/companies_1.json"),
    "DATA_PATH": Path("data/new_honda_f.json"),
    "ENRICHED_DATA_PATH": Path("data/GED.json"),
    "CHECKPOINT_DIR": Path("checkpoints/"),
    "CHECKPOINT_INTERVAL": 10,
    "QUEUE_SIZE": 100,
    "MAX_CONCURRENT_REQUESTS": 10
}

def jsonl_to_json(file: Path):
    with file.open("r", encoding="utf-8") as f:
        items = [part for line in f if line.strip() for part in json.loads(line)]
    return items

async def runner(path, file_name, log_file, config, task_to_run, base_data, enriched_data, rate_limit, max_concurrent_sessions):
    ps = ProcessingState()
    pipeline = DataPipeline(ps, log_file, dataset_paths=[path], CONFIG=config)

    limiter = AsyncLimiter(*rate_limit) if rate_limit else None
    semaphore = asyncio.Semaphore(max_concurrent_sessions) if max_concurrent_sessions else None

    producer_tasks = [
        asyncio.create_task(pipeline.producer(file_name, path))
    ]

    consumer_tasks = [
        asyncio.create_task(pipeline.consumer(task_to_run, i, limiter, semaphore, base_data, enriched_data))
            for i in range(CONFIG["MAX_CONCURRENT_REQUESTS"])
    ]

    await asyncio.gather(*producer_tasks)

    for _ in range(CONFIG["MAX_CONCURRENT_REQUESTS"]):
        await pipeline.queue.put(None)

    await asyncio.gather(*consumer_tasks)
    return pipeline

async def stage_one(path, file_name, log_file, config, run_process, enriched_data, base_data):
    await runner(
        path,
        file_name,
        log_file,
        config,
        run_process,
        base_data,
        enriched_data,
        rate_limit=(10, 1),
        max_concurrent_sessions=CONFIG["MAX_CONCURRENT_REQUESTS"],
    )

async def stage_two(enriched_data, base_data, log_file, run_process):
    items = jsonl_to_json(enriched_data)
    investments = [
        {
            "name": item.get("name"),
            "uniqueness_score": item.get("uniqueness_score"),
            "relevance": item.get("relevance")
        }
        for item in items
        if "relevance" in item and isinstance(item["relevance"], str)
        and "investment" in item["relevance"].lower()
    ]
    return run_process(investments, base_data, log_file)

async def main():
    dataset_paths = [
        ("data", CONFIG["FILE_PATH"].parent),
        ("new_honda_f", CONFIG["DATA_PATH"].parent)
    ]

    file_name = dataset_paths[0][0]
    path = dataset_paths[0][1]
    enriched = CONFIG["ENRICHED_DATA_PATH"]
    honda_details = None
    honda_path = f"{dataset_paths[1][1]}/{dataset_paths[1][0]}.json"
    with open(honda_path, "r") as honda_file:
        honda_details = json.load(honda_file)
    honda_path_jsonl = honda_path.replace(".json", ".jsonl")
    os.rename(honda_path, honda_path_jsonl)
    await stage_one(path, file_name, logger, CONFIG, g_enrichment, enriched, honda_details)
    await stage_two(enriched, honda_details, logger, compare_companies)

    return


if __name__ == "__main__":
    asyncio.run(main())
