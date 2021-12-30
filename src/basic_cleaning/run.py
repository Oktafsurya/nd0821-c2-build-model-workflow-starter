#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Downloading artifact ...")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info(f'Read csv file from {artifact_local_path} ...')
    df = pd.read_csv(artifact_local_path)

    logger.info("Removing outliers in price column ... ")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Convert last_review column to pandas datetime ... ")
    df['last_review'] = pd.to_datetime(df['last_review'])
    df = df[idx].copy()

    # remove location outside defined latitude and longitude 
    logger.info("Removing outliers in latitude & longitude column ... ")
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    df.to_csv(args.output_artifact, index=False)

    logger.info("Uploading artifact to W&B ... ")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="The input artifact name",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="The output artifact name",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="The output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="The output artifact description",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="min price used",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="max price used",
        required=True
    )

    args = parser.parse_args()

    go(args)
