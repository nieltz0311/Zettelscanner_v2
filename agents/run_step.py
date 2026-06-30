"""CLI runner that invokes an agent's process() method for one Lobster workflow step.

Lobster steps are plain shell commands with no input_mapping/output_mapping,
so data is passed between steps as JSON files (see workflow.yaml).
"""
import argparse
import importlib
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="e.g. agents.ocr_scanner")
    parser.add_argument("class_name", help="e.g. OCRScanner")
    parser.add_argument("--input", help="JSON string passed as the agent's input")
    parser.add_argument("--input-file", help="Path to a JSON file passed as the agent's input")
    parser.add_argument("--arg-key", help="Key to extract from the input JSON for process(); omit to pass the whole object")
    parser.add_argument("--output", help="Path to write the JSON result; defaults to stdout")
    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file, encoding="utf-8") as f:
            data = json.load(f)
    elif args.input:
        data = json.loads(args.input)
    else:
        data = {}

    process_arg = data[args.arg_key] if args.arg_key else data

    module = importlib.import_module(args.module)
    agent = getattr(module, args.class_name)()
    result = agent.process(process_arg)

    output = json.dumps(result, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
