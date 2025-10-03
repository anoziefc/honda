import asyncio
import csv
import json
import logging
import os
from pathlib import Path
from Processor.data_pipeline import DataPipeline
from Processor.checkpoint_processor import ProcessingState
# from Data_Enrichment.data_enrichment import run_enrichment as p_enrichment
from Data_Enrichment_Google.enrichment import run_enrichment as g_enrichment
from typing import List
from aiolimiter import AsyncLimiter


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("processing.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CONFIG = {
    "FILE_PATH": Path("data/TB test Run 2.csv"),
    "JSON_FILE_PATH": Path("data/TB test Run 2.json"),
    "ENRICHED_DATA_PATH": Path("data/gemini_enriched_data.json"),
    "CHECKPOINT_DIR": Path("checkpoints/"),
    "CHECKPOINT_INTERVAL": 50,
    "QUEUE_SIZE": 100,
    "MAX_CONCURRENT_REQUESTS": 10
}

def prepare_file(file_path: Path, json_file_path: Path):
    companies = []
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("Companies") or None
            website = row.get("Company Website") or None
            companies.append({"name": name, "website": website})
    with open(json_file_path, "w") as json_file:
        json.dump(companies, json_file, indent=4, ensure_ascii=False)

def append_to_json_file(new_data, filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    
    existing_data.append(new_data)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

async def runner(path, file_name, log_file, config, task_to_run, rate_limit, max_concurrent_sessions):
    ps = ProcessingState()
    pipeline = DataPipeline(ps, log_file, dataset_paths=[path], CONFIG=config)

    limiter = AsyncLimiter(*rate_limit) if rate_limit else None
    semaphore = asyncio.Semaphore(max_concurrent_sessions) if max_concurrent_sessions else None

    producer_tasks = [
        asyncio.create_task(pipeline.producer(file_name, path))
    ]

    consumer_tasks = [
        asyncio.create_task(pipeline.consumer(task_to_run, i, limiter, semaphore))
            for i in range(CONFIG["MAX_CONCURRENT_REQUESTS"])
    ]

    await asyncio.gather(*producer_tasks)

    for _ in range(CONFIG["MAX_CONCURRENT_REQUESTS"]):
        await pipeline.queue.put(None)

    await asyncio.gather(*consumer_tasks)
    return pipeline

async def stage_one(path, file_name, log_file, config, run_process, enriched_data):
    runner_instance = await runner(
        path,
        file_name,
        log_file,
        config,
        run_process,
        rate_limit=(5, 1),
        max_concurrent_sessions=CONFIG["MAX_CONCURRENT_REQUESTS"]
    )
    runner_instance.state.save_checkpoint(log_file, config)

    append_to_json_file(runner_instance.results, enriched_data)

async def main():
    dataset_paths = [
        ("TB test Run 2", CONFIG["FILE_PATH"].parent),
    ]

    file_name = dataset_paths[0][0]
    path = dataset_paths[0][1]
    enriched = CONFIG["ENRICHED_DATA_PATH"]
    prepare_file(CONFIG["FILE_PATH"], CONFIG["JSON_FILE_PATH"])

    await stage_one(path, file_name, logger, CONFIG, g_enrichment, enriched)

    return


if __name__ == "__main__":
    asyncio.run(main())
