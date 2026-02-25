#!/usr/bin/env python3
"""Generate JSON output equivalent to test/city_zip_code.html logic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence


def load_js_variable_as_json(js_path: Path, variable_name: str) -> Any:
    """Load a `var <name> = ...;` JS assignment as JSON."""
    text = js_path.read_text(encoding="utf-8")
    marker = f"var {variable_name} ="
    start = text.find(marker)
    if start == -1:
        raise ValueError(f"Variable {variable_name!r} not found in {js_path}")

    payload = text[start + len(marker) :].strip()
    if payload.endswith(";"):
        payload = payload[:-1].strip()

    return json.loads(payload)


def first_key(obj: Dict[str, Any]) -> str:
    return next(iter(obj))


def build_city_zip_output(
    province_data: Sequence[Dict[str, Any]],
    zip_code_data: Sequence[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Replicate test/city_zip_code.html behavior."""
    all_arr: List[Dict[str, str]] = []
    zip_code_object: Dict[str, str] = {}

    zip_code_state_array: List[str] = []
    zip_code_city_array: List[str] = []
    zip_code_distict_array: List[str] = []
    district_not_array: List[str] = []

    for zip_code_state in zip_code_data:
        zip_code_state_array.append(zip_code_state["name"])
        for zip_code_city in zip_code_state.get("children", []):
            zip_code_city_array.append(zip_code_city["name"])
            for zip_code_distict in zip_code_city.get("children", []):
                zip_code_distict_array.append(zip_code_distict["name"])

    for state in province_data:
        state_item = first_key(state)
        if state_item in zip_code_state_array:
            for city in state[state_item]:
                city_item = first_key(city)
                city_array = city[city_item]

                # The original JS has a branch for empty city_array that references
                # an undefined districtItem. Existing data does not hit this branch.
                if city_item in zip_code_city_array:
                    for district in city[city_item]:
                        district_item = district
                        if district_item in zip_code_distict_array:
                            for zip_code_state in zip_code_data:
                                for zip_code_city in zip_code_state.get(
                                    "children", []
                                ):
                                    for zip_code_distict in zip_code_city.get(
                                        "children", []
                                    ):
                                        if zip_code_distict["name"] == district_item:
                                            all_arr = []
                                            zip_code = zip_code_distict["zipcode"]
                                            key = f"{state_item}{city_item}{district_item}"
                                            zip_code_object[key] = zip_code
                                            all_arr.append(zip_code_object)

                        if district_item not in zip_code_distict_array:
                            for zip_code_state in zip_code_data:
                                for zip_code_city in zip_code_state.get(
                                    "children", []
                                ):
                                    if zip_code_city["name"] == city_item:
                                        all_arr = []
                                        zip_code = zip_code_city["zipcode"]
                                        key = f"{state_item}{city_item}{district_item}"
                                        zip_code_object[key] = zip_code
                                        all_arr.append(zip_code_object)

                if city_item not in zip_code_city_array:
                    for district in city[city_item]:
                        district_item = district
                        for zip_code_state in zip_code_data:
                            if zip_code_state["name"] == state_item:
                                all_arr = []
                                zip_code = zip_code_state["zipcode"]
                                key = f"{state_item}{city_item}{district_item}"
                                zip_code_object[key] = zip_code
                                all_arr.append(zip_code_object)

                if not city_array:
                    pass

        if state_item not in zip_code_state_array:
            pass

    if district_not_array:
        # Kept only to mirror the original JS variable lifecycle.
        _ = district_not_array

    return all_arr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate JSON equivalent to test/city_zip_code.html output "
            "(JSON.stringify(allArr))."
        )
    )
    parser.add_argument(
        "--province-js",
        default="test/test.js",
        help="Path to province JS file containing `var provinceJson = ...`",
    )
    parser.add_argument(
        "--zip-js",
        default="test/zip_code_data.js",
        help="Path to zip JS file containing `var zipCode = ...`",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write output JSON to this file (stdout when omitted).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    province_data = load_js_variable_as_json(Path(args.province_js), "provinceJson")
    zip_code_data = load_js_variable_as_json(Path(args.zip_js), "zipCode")
    result = build_city_zip_output(province_data, zip_code_data)
    output_text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))

    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
