import sys
import csv
import os
import ast
import yaml
from demo.main import run_chain
from demo.ingest import ingest
import itertools
import hashlib, json
import glob
import shutil

def load_config(config_name):
    config_path = os.path.join(os.path.dirname(__file__), "configs", f"{config_name}.yml")
    if not os.path.exists(config_path):
        print(f"Config '{config_name}' not found at {config_path}")
        sys.exit(1)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def load_testset(testset_name):
    csv_path = os.path.join(os.path.dirname(__file__), "testsets", testset_name, "set.csv")
    if not os.path.exists(csv_path):
        print(f"Testset '{testset_name}' not found at {csv_path}")
        sys.exit(1)
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)
    print(f"Loaded {len(rows)} rows from {csv_path}")
    validated_rows = []
    for row in rows:
        filenames = row.get('filenames', '')
        try:
            row['filenames'] = ast.literal_eval(filenames)
        except Exception as e:
            print(f"Error: Could not parse filenames for row id={row.get('id', '?')}: {filenames}")
            sys.exit(1)
        validated_rows.append(row)
    return validated_rows

def generate_ingest_combinations(ingest_config):
    # ingest_config: dict with keys mapping to lists of dicts
    keys = list(ingest_config.keys())
    values_lists = [ingest_config[key] for key in keys]
    combinations = []
    for combo in itertools.product(*values_lists):
        # Each combo is a tuple of dicts, one per key
        combined = {key: value for key, value in zip(keys, combo)}
        combinations.append(combined)
    return combinations


# --- Deep rag_config combination generation ---
def flatten_config(config, prefix=None):
    if prefix is None:
        prefix = []
    items = []
    for key, value in config.items():
        if isinstance(value, dict):
            items.extend(flatten_config(value, prefix + [key]))
        elif isinstance(value, list):
            items.append((prefix + [key], value))
        else:
            items.append((prefix + [key], [value]))
    return items

def set_nested(d, keys, value):
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value

def generate_deep_combinations(config):
    flat = flatten_config(config)
    if not flat:
        return [{}]
    keys, values_lists = zip(*flat)
    combinations = []
    for combo in itertools.product(*values_lists):
        result = {}
        for k, v in zip(keys, combo):
            set_nested(result, k, v)
        combinations.append(result)
    return combinations

def hash_data_files(data_dir):
        file_hashes = []
        for file_path in sorted(glob.glob(os.path.join(data_dir, '*'))):
            with open(file_path, 'rb') as f:
                file_hashes.append(hashlib.sha256(f.read()).hexdigest())
        return hashlib.sha256(''.join(file_hashes).encode()).hexdigest()


def ingest_comb(testset_name, ingest_combinations):
    wip_base = os.path.join(os.path.dirname(__file__), "results/__cache__/chromadb/__wip__")
    final_base = os.path.join(os.path.dirname(__file__), "results/__cache__/chromadb")
    # Ensure WIP folder is empty before starting
    if os.path.exists(wip_base):
        print(f"Clearing WIP folder: {wip_base}")
        shutil.rmtree(wip_base)
    os.makedirs(wip_base, exist_ok=True)

    for combo in ingest_combinations:
        data_dir = os.path.join(os.path.dirname(__file__), "testsets", testset_name, "data")
        data_hash = hash_data_files(data_dir)
        hash_input = {
            "combo": combo,
            "data_hash": data_hash
        }
        hash = hashlib.sha256(json.dumps(hash_input, sort_keys=True).encode()).hexdigest()
        wip_path = os.path.join(wip_base, hash)
        final_path = os.path.join(final_base, hash)
        if os.path.exists(final_path):
            print(f"Cache exists for {hash}, skipping ingest.")
            continue
        os.environ["CHROMA_PATH"] = wip_path
        os.environ["DOCS_DIR"] = data_dir
        os.environ["EXTRACTOR_PDF_TYPE"] = combo["pdf_extractor"]["type"]
        os.environ["CHUNKER_TYPE"] = combo["chunking"]["type"]
        ingest()
        # Move WIP to final after ingest completes
        if os.path.exists(final_path):
            shutil.rmtree(final_path)
        shutil.move(wip_path, final_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_name>")
        sys.exit(1)

    config_name = sys.argv[1]
    config = load_config(config_name)

    testset_name = config.get('testset')
    if not testset_name:
        print(f"No 'testset' field found in config for {config_name}")
        sys.exit(1)

    rows = load_testset(testset_name)

    # Ingest data into the database
    ingest_combinations = generate_ingest_combinations(config.get('ingest_config', {}))
    print(f"Generated {len(ingest_combinations)} ingest configuration combinations.")
    ingest_comb(testset_name, ingest_combinations)
    
    # loop over rag combinations
    rag_combinations = generate_deep_combinations(config.get('rag_config', {}))
    print(f"Generated {len(rag_combinations)} rag_config combinations.")

    for ingest_combo in ingest_combinations:
        for rag_combo in rag_combinations:
            hash_input = {
                "ingest": ingest_combo,
                "rag": rag_combo
            }
            hash = hashlib.sha256(json.dumps(hash_input, sort_keys=True).encode()).hexdigest()
            results_dir = os.path.join(os.path.dirname(__file__), "results", hash)
            # Create specific config in results_dir as YAML
            os.makedirs(results_dir, exist_ok=True)
            with open(os.path.join(results_dir, "config.yml"), "w") as f:
                yaml.dump({
                    "name": config_name,
                    "testset": testset_name,
                    "ingest_config": ingest_combo,
                    "rag_config": rag_combo
                }, f, sort_keys=False)

            # Set correct chromadb cache path for this combination
            chroma_cache_path = os.path.join(os.path.dirname(__file__), "results/__cache__/chromadb", hashlib.sha256(json.dumps({"combo": ingest_combo, "data_hash": hash_data_files(os.path.join(os.path.dirname(__file__), "testsets", testset_name, "data"))}, sort_keys=True).encode()).hexdigest())
            os.environ["CHROMA_PATH"] = chroma_cache_path
            os.environ["EMBEDDING_MODEL"] = rag_combo["retrieval"]["model"]["name"]
            os.environ["EMBEDDING_API_URL"] = rag_combo["retrieval"]["model"]["url"]
            os.environ["EMBEDDING_API_KEY"] = rag_combo["retrieval"]["model"]["key"]
            os.environ["RETRIEVAL_TOP_K"] = str(rag_combo["retrieval"]["top_k"])
            os.environ["LLM_MODEL"] = rag_combo["generation"]["model"]["name"]
            os.environ["LLM_API_URL"] = rag_combo["generation"]["model"]["url"]
            os.environ["LLM_API_KEY"] = rag_combo["generation"]["model"]["key"]

            # Example: set env vars or pass rag_combo to chain
            for row in rows:
                question = row["question"]
                result = run_chain(question)

                def make_json_serializable(obj):
                    if isinstance(obj, dict):
                        return {k: make_json_serializable(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [make_json_serializable(v) for v in obj]
                    elif hasattr(obj, "dict"):
                        return make_json_serializable(obj.dict())
                    elif hasattr(obj, "content"):
                        return obj.content
                    elif hasattr(obj, "__str__"):
                        return str(obj)
                    else:
                        return obj

                result_json = make_json_serializable(result)
                print(json.dumps(result_json, indent=2, ensure_ascii=False))
                # write result to a file in the results dir with the name of a hash of the row
                row_hash = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
                with open(os.path.join(results_dir, f"{row_hash}.json"), "w") as f:
                    json.dump(result_json, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
