""" Edit from Official evaluation script for v1.1 of the SQuAD dataset. """

__author__ = "Puri Phakmongkol"
__author_email__ = "me@puri.in.th"

"""
* Thai QA Metric
*
* Created date : 22/07/2021
*
+      o     +              o
    +             o     +       +
o          +
    o  +           +        +
+        o     o       +        o
-_-_-_-_-_-_-_,------,      o
_-_-_-_-_-_-_-|   /\_/\
-_-_-_-_-_-_-~|__( ^ .^)  +     +
_-_-_-_-_-_-_-""  ""
+      o         o   +       o
    +         +
o      o  _-_-_-_- Thai QA Metric - Word level by Newmm Tokenizer
    o           +
+      +     o        o      +
"""
from __future__ import print_function

import argparse
import json
import re
import string
import sys

from pythainlp.tokenize import word_tokenize
from pythainlp.util import normalize

from collections import Counter


# def normalize_answer(s):
#     """Lower text and remove punctuation, articles and extra whitespace."""

#     def remove_articles(text):
#         return re.sub(r"\b(a|an|the)\b", " ", text)

#     def remove_punc(text):
#         exclude = set(string.punctuation)
#         return "".join(ch for ch in text if ch not in exclude)

#     def lower(text):
#         return text.lower()

#     return normalize(remove_punc(lower(s))).replace('\xa0', ' ')

def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return normalize(remove_punc(lower(s.strip()))).replace('\xa0', ' ')


def f1_score(prediction, ground_truth):
    # prediction_tokens = normalize_answer(prediction).split()
    # ground_truth_tokens = normalize_answer(ground_truth).split()
    prediction_tokens = word_tokenize(normalize_answer(prediction), engine='newmm')
    ground_truth_tokens = word_tokenize(normalize_answer(ground_truth), engine='newmm')

    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def exact_match_score(prediction, ground_truth):
    return normalize_answer(prediction) == normalize_answer(ground_truth)


def metric_max_over_ground_truths(metric_fn, prediction, ground_truths):
    scores_for_ground_truths = []
    for ground_truth in ground_truths:
        score = metric_fn(prediction, ground_truth)
        scores_for_ground_truths.append(score)
    return max(scores_for_ground_truths)


def evaluate(dataset, predictions):
    f1 = exact_match = total = 0
    for article in dataset:
        for paragraph in article["paragraphs"]:
            for qa in paragraph["qas"]:
                total += 1
                if qa["id"] not in predictions:
                    message = "Unanswered question " + qa["id"] + " will receive score 0."
                    print(message, file=sys.stderr)
                    continue
                ground_truths = list(map(lambda x: x["text"], qa["answers"]))
                prediction = predictions[qa["id"]]
                exact_match += metric_max_over_ground_truths(exact_match_score, prediction, ground_truths)
                f1 += metric_max_over_ground_truths(f1_score, prediction, ground_truths)

    exact_match = 100.0 * exact_match / total
    f1 = 100.0 * f1 / total

    return {"exact_match": exact_match, "f1": f1}


if __name__ == "__main__":
    expected_version = "1.1"
    parser = argparse.ArgumentParser(description="Evaluation for SQuAD " + expected_version)
    parser.add_argument("dataset_file", help="Dataset file")
    parser.add_argument("prediction_file", help="Prediction File")
    args = parser.parse_args()
    with open(args.dataset_file) as dataset_file:
        dataset_json = json.load(dataset_file)
        if dataset_json["version"] != expected_version:
            print(
                "Evaluation expects v-" + expected_version + ", but got dataset with v-" + dataset_json["version"],
                file=sys.stderr,
            )

        dataset = dataset_json["data"]
    with open(args.prediction_file) as prediction_file:
        predictions = json.load(prediction_file)
    print(json.dumps(evaluate(dataset, predictions)))
