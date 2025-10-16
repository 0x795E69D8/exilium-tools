import os
import xxhash
import json
from multiprocessing import Pool, cpu_count
from datetime import datetime

CONFIG_PATH = "instances.json"  # config mapping instances to game paths
OUTPUT_DIR = "instance_states"  # folder to save per-instance states
REPORT_DIR = "reports"          # folder to save HTML reports
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def load_instances(config_path):
    if not os.path.exists(config_path):
        print(f"Instances config not found: {config_path}")
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_config_versions(config_file_path, bt_version_path):
    versions = {}
    try:
        with open(config_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    if key in ["CodeResVersion", "CacheResVersion", "DownlodBinaryData", "StcTableVersion"]:
                        versions[key] = value.strip()
    except FileNotFoundError:
        print(f"Config file not found: {config_file_path}")
    try:
        with open(bt_version_path, "r", encoding="utf-8") as f:
            versions["BTVersion"] = f.readline().strip()
    except FileNotFoundError:
        print(f"BTVersion file not found: {bt_version_path}")
    return versions


def hash_file_xxhash(filepath):
    h = xxhash.xxh64()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def file_info_worker(args):
    rel_path, full_path, old_info = args
    try:
        mtime = os.path.getmtime(full_path)
        if old_info and abs(old_info.get("mtime", 0) - mtime) < 0.0001:
            return rel_path, {"hash": old_info["hash"], "mtime": mtime}
        else:
            file_hash = hash_file_xxhash(full_path)
            return rel_path, {"hash": file_hash, "mtime": mtime}
    except Exception as e:
        print(f"Failed to process {rel_path}: {e}")
        return rel_path, None


def scan_folders(folders, old_state=None):
    all_files = []
    old_files = old_state["files"] if old_state else {}

    for folder in folders:
        if not os.path.exists(folder):
            print(f"Warning: folder not found: {folder}")
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith("_AOT.u") or file.endswith("_HUDll.u"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=os.path.dirname(folder))
                old_info = old_files.get(rel_path)
                all_files.append((rel_path, full_path, old_info))

    file_data = {}
    with Pool(cpu_count()) as pool:
        for rel_path, file_info in pool.map(file_info_worker, all_files):
            if file_info:
                file_data[rel_path] = file_info

    return file_data


def save_state(instance_name, versions, file_data):
    output_file = os.path.join(OUTPUT_DIR, f"{instance_name}_state.json")
    data = {"versions": versions, "files": file_data}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved state for {instance_name} to {output_file}")


def load_state(instance_name):
    output_file = os.path.join(OUTPUT_DIR, f"{instance_name}_state.json")
    if not os.path.exists(output_file):
        return None
    with open(output_file, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_states(old_state, new_state):
    old_files = old_state["files"] if old_state else {}
    new_files = new_state["files"]

    added = [f for f in new_files if f not in old_files]
    removed = [f for f in old_files if f not in new_files]
    modified = []
    for f in new_files:
        if f in old_files:
            old_info = old_files[f]
            new_info = new_files[f]
            if old_info["mtime"] != new_info["mtime"]:
                if old_info["hash"] != new_info["hash"]:
                    modified.append(f)

    old_versions = old_state["versions"] if old_state else {}
    new_versions = new_state["versions"]
    version_changes = {k: (old_versions.get(k), new_versions.get(k)) for k in new_versions if old_versions.get(k) != new_versions.get(k)}

    return added, removed, modified, version_changes


def export_html_report(instance_name, added, removed, modified, version_changes):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(REPORT_DIR, f"{instance_name}_report_{timestamp}.html")

    html_content = f"""
    <html>
    <head>
        <title>Game Update Report - {instance_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            table {{ border-collapse: collapse; width: 90%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #2980b9; color: white; position: sticky; top: 0; }}
            tr.added {{ background-color: #d4edda; }}
            tr.removed {{ background-color: #f8d7da; }}
            tr.modified {{ background-color: #fff3cd; }}
            details {{ margin-bottom: 10px; }}
            summary {{ cursor: pointer; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <h1>Game Update Report - {instance_name}</h1>
        <h2>Version Changes</h2>
        {generate_version_table(version_changes)}
        {generate_collapsible_file_table("Modified Files", modified, "modified")}
        {generate_collapsible_file_table("Added Files", added, "added")}
        {generate_collapsible_file_table("Removed Files", removed, "removed")}
        <p>Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </body>
    </html>
    """

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML report exported to {report_file}")


def generate_version_table(version_changes):
    if not version_changes:
        return "<p>No version changes.</p>"
    rows = "".join(f"<tr><td>{k}</td><td>{old}</td><td>{new}</td></tr>" for k, (old, new) in version_changes.items())
    return f"<table><tr><th>Version Key</th><th>Old Value</th><th>New Value</th></tr>{rows}</table>"


def generate_collapsible_file_table(title, files, row_class):
    if not files:
        return f"<p>{title}: None</p>"
    rows = "".join(f"<tr class='{row_class}'><td>{f}</td></tr>" for f in files)
    return f"""
    <details open>
        <summary>{title} ({len(files)})</summary>
        <table><tr><th>File</th></tr>{rows}</table>
    </details>
    """


if __name__ == "__main__":
    instances = load_instances(CONFIG_PATH)
    for instance_name, game_path in instances.items():
        print(f"\nProcessing instance: {instance_name} ({game_path})")

        config_file_path = os.path.join(game_path, "GF2_Exilium_Data\\LocalCache\\Data\\GameConfig.cfg")
        bt_version_path = os.path.join(game_path, "GF2_Exilium_Data\\LocalCache\\Data\\BinFile\\BT\\BTVersion.txt")
        versions = get_config_versions(config_file_path, bt_version_path)

        folders_to_track = [
            os.path.join(game_path, "GF2_Exilium_Data\\LocalCache\\Data\\AssetBundles_Windows"),
            os.path.join(game_path, "GF2_Exilium_Data\\LocalCache\\Data\\BinFile"),
            os.path.join(game_path, "GF2_Exilium_Data\\LocalCache\\Data\\ClientRes_Windows"),
            os.path.join(game_path, "GF2_Exilium_Data\\LocalCache\\Data\\Table")
        ]

        old_state = load_state(instance_name)
        file_data = scan_folders(folders_to_track, old_state)
        new_state = {"versions": versions, "files": file_data}

        if old_state:
            added, removed, modified, version_changes = compare_states(old_state, new_state)
            if added or removed or modified or version_changes:
                print("Changes since last state:")
                if version_changes:
                    for key, (old_v, new_v) in version_changes.items():
                        print(f"  {key} changed: {old_v} -> {new_v}")
                if added:
                    print("  Added:")
                    for f in added:
                        print(f"    {f}")
                if removed:
                    print("  Removed:")
                    for f in removed:
                        print(f"    {f}")
                if modified:
                    print("  Modified:")
                    for f in modified:
                        print(f"    {f}")
                export_html_report(instance_name, added, removed, modified, version_changes)
            else:
                print("No changes detected.")

        save_state(instance_name, versions, file_data)
