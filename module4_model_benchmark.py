import time
import requests
import json
import csv
from datetime import datetime


# ============================================================
# PHASE 1 — MODULE 4
# MODEL FAMILIES & SELECTION
#
# REAL OLLAMA MODEL BENCHMARK
# ============================================================

OLLAMA_BASE_URL = "http://172.16.2.53:11434"

CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
SHOW_URL = f"{OLLAMA_BASE_URL}/api/show"


# ============================================================
# MODELS AVAILABLE IN YOUR OLLAMA ENVIRONMENT
# ============================================================

MODELS = [
    "gemma4",
    "qwen3.6",
    "docker-expert",
    "gemma:test",
    "gemma",
]


# ============================================================
# STANDARDIZED TEST PROMPTS
#
# SAME PROMPTS ARE USED FOR ALL MODELS
# ============================================================

TESTS = {

    "General Knowledge": """
Explain DNS to a junior network administrator.

Keep the explanation technically accurate but beginner-friendly.
""",

    "Instruction Following": """
Follow these instructions exactly:

1. Give exactly three bullet points.
2. Each bullet must contain exactly one sentence.
3. Topic: Active Directory.

Do not add an introduction or conclusion.
""",

    "Coding": """
Write a Python function that reads a CSV file,
removes duplicate rows, and reports how many
duplicates were removed.

Return only the Python code.
""",

    "Infrastructure Reasoning": """
A Windows domain client can ping the DNS server by IP address,
but internal FQDN resolution fails.

List the most likely causes and the diagnostic commands
you would use.

Do not recommend configuration changes until the cause
is identified.
""",

    "Structured Output": """
Return exactly this JSON structure:

{
  "issue": "...",
  "likely_cause": "...",
  "diagnostic_command": "..."
}

Use a DNS troubleshooting example.

Return JSON only.
""",

    "Context Understanding": """
Remember this information:

Server = DC01
IP = 192.168.1.10
Role = Active Directory Domain Controller

Now answer:

What is the hostname of the server?
What is its IP address?
What is its role?
""",

    "Creativity": """
Explain Active Directory using a simple real-world analogy
that a junior network administrator would understand.
"""
}


# ============================================================
# TEMPERATURE EXPERIMENT
# ============================================================

PARAMETER_TEST_PROMPT = """
Explain why DNS resolution can fail even when
the DNS server can be pinged by IP address.
"""

TEMPERATURES = [0.0, 0.2, 0.7, 1.0]


# ============================================================
# RESULTS STORAGE
# ============================================================

benchmark_results = []
metadata_results = []
temperature_results = []


# ============================================================
# CHECK OLLAMA
# ============================================================

def check_ollama():

    try:

        response = requests.get(
            OLLAMA_BASE_URL,
            timeout=10
        )

        response.raise_for_status()

        print("✅ Ollama is reachable.")

        return True

    except Exception as e:

        print("❌ Cannot connect to Ollama.")
        print(f"Error: {e}")

        print("\nMake sure Ollama is running and:")
        print("http://localhost:11434")

        return False


# ============================================================
# GET MODEL METADATA
# ============================================================

def get_model_info(model_name):

    response = requests.post(
        SHOW_URL,
        json={
            "name": model_name
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# DISPLAY MODEL INFORMATION
# ============================================================

def display_model_info(model_name):

    print("\n" + "-" * 80)
    print("MODEL INFORMATION")
    print("-" * 80)

    try:

        info = get_model_info(model_name)

        details = info.get("details", {})

        model_family = details.get(
            "family",
            "N/A"
        )

        parameter_size = details.get(
            "parameter_size",
            "N/A"
        )

        quantization = details.get(
            "quantization_level",
            "N/A"
        )

        format_name = details.get(
            "format",
            "N/A"
        )

        families = details.get(
            "families",
            []
        )

        capabilities = info.get(
            "capabilities",
            []
        )

        print(f"Model:          {model_name}")
        print(f"Family:         {model_family}")
        print(f"Families:       {families}")
        print(f"Parameters:     {parameter_size}")
        print(f"Format:         {format_name}")
        print(f"Quantization:   {quantization}")

        if capabilities:

            print(
                f"Capabilities:   {', '.join(capabilities)}"
            )

        else:

            print(
                "Capabilities:   Not exposed by Ollama"
            )

        vision = (
            "YES"
            if "vision" in capabilities
            else "NO / UNKNOWN"
        )

        tools = (
            "YES"
            if "tools" in capabilities
            else "NO / UNKNOWN"
        )

        thinking = (
            "YES"
            if "thinking" in capabilities
            else "NO / UNKNOWN"
        )

        print(f"Vision:         {vision}")
        print(f"Tool Calling:   {tools}")
        print(f"Thinking:       {thinking}")

        metadata_results.append({

            "model": model_name,
            "family": model_family,
            "parameters": parameter_size,
            "format": format_name,
            "quantization": quantization,
            "capabilities": ", ".join(capabilities)

        })

        return info

    except Exception as e:

        print(
            f"⚠️ Could not retrieve metadata: {e}"
        )

        metadata_results.append({

            "model": model_name,
            "family": "N/A",
            "parameters": "N/A",
            "format": "N/A",
            "quantization": "N/A",
            "capabilities": "N/A"

        })

        return {}


# ============================================================
# RUN ONE MODEL
# ============================================================

def run_model(
    model_name,
    prompt,
    temperature=0.2
):

    payload = {

        "model": model_name,

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ],

        "stream": False,

        "options": {

            "temperature": temperature

        }

    }

    start_time = time.perf_counter()

    response = requests.post(
        CHAT_URL,
        json=payload,
        timeout=300
    )

    end_time = time.perf_counter()

    response.raise_for_status()

    data = response.json()

    latency = end_time - start_time

    message = data.get(
        "message",
        {}
    )

    answer = message.get(
        "content",
        ""
    )

    return {

        "answer": answer,

        "latency": latency,

        "prompt_tokens": data.get(
            "prompt_eval_count"
        ),

        "output_tokens": data.get(
            "eval_count"
        ),

        "total_duration": data.get(
            "total_duration"
        ),

        "load_duration": data.get(
            "load_duration"
        ),

        "prompt_eval_duration": data.get(
            "prompt_eval_duration"
        ),

        "eval_duration": data.get(
            "eval_duration"
        )

    }


# ============================================================
# RUN STANDARD BENCHMARK
# ============================================================

def run_standard_tests(model_name):

    print("\n")
    print("=" * 80)
    print(f"STANDARD BENCHMARK — {model_name}")
    print("=" * 80)

    for test_name, prompt in TESTS.items():

        print("\n")
        print(f"▶ TEST: {test_name}")
        print("-" * 80)

        try:

            result = run_model(
                model_name,
                prompt,
                temperature=0.2
            )

            print(result["answer"])

            print("\n--- PERFORMANCE ---")

            print(
                f"Latency:        "
                f"{result['latency']:.2f} sec"
            )

            print(
                f"Input tokens:   "
                f"{result['prompt_tokens']}"
            )

            print(
                f"Output tokens:  "
                f"{result['output_tokens']}"
            )

            benchmark_results.append({

                "model": model_name,

                "test": test_name,

                "latency_sec":
                    round(
                        result["latency"],
                        2
                    ),

                "input_tokens":
                    result["prompt_tokens"],

                "output_tokens":
                    result["output_tokens"]

            })

        except Exception as e:

            print(
                f"❌ Test failed: {e}"
            )

            benchmark_results.append({

                "model": model_name,

                "test": test_name,

                "latency_sec": "ERROR",

                "input_tokens": "",

                "output_tokens": ""

            })


# ============================================================
# TEMPERATURE EXPERIMENT
# ============================================================

def run_temperature_test(model_name):

    print("\n")
    print("=" * 80)
    print(
        f"TEMPERATURE EXPERIMENT — {model_name}"
    )
    print("=" * 80)

    for temperature in TEMPERATURES:

        print("\n")
        print(
            f"🌡️ Temperature = {temperature}"
        )

        print("-" * 80)

        try:

            result = run_model(

                model_name,

                PARAMETER_TEST_PROMPT,

                temperature=temperature

            )

            print(result["answer"])

            print("\n--- PERFORMANCE ---")

            print(
                f"Latency: "
                f"{result['latency']:.2f} sec"
            )

            print(
                f"Output tokens: "
                f"{result['output_tokens']}"
            )

            temperature_results.append({

                "model": model_name,

                "temperature": temperature,

                "latency_sec":
                    round(
                        result["latency"],
                        2
                    ),

                "output_tokens":
                    result["output_tokens"]

            })

        except Exception as e:

            print(
                f"❌ Temperature test failed: {e}"
            )


# ============================================================
# SAVE CSV
# ============================================================

def save_results():

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    benchmark_file = (
        f"module4_benchmark_{timestamp}.csv"
    )

    metadata_file = (
        f"module4_metadata_{timestamp}.csv"
    )

    temperature_file = (
        f"module4_temperature_{timestamp}.csv"
    )

    # --------------------------------------------------------
    # Benchmark CSV
    # --------------------------------------------------------

    if benchmark_results:

        with open(
            benchmark_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=[
                    "model",
                    "test",
                    "latency_sec",
                    "input_tokens",
                    "output_tokens"
                ]

            )

            writer.writeheader()

            writer.writerows(
                benchmark_results
            )

    # --------------------------------------------------------
    # Metadata CSV
    # --------------------------------------------------------

    if metadata_results:

        with open(
            metadata_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=[
                    "model",
                    "family",
                    "parameters",
                    "format",
                    "quantization",
                    "capabilities"
                ]

            )

            writer.writeheader()

            writer.writerows(
                metadata_results
            )

    # --------------------------------------------------------
    # Temperature CSV
    # --------------------------------------------------------

    if temperature_results:

        with open(
            temperature_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=[
                    "model",
                    "temperature",
                    "latency_sec",
                    "output_tokens"
                ]

            )

            writer.writeheader()

            writer.writerows(
                temperature_results
            )

    print("\n")
    print("=" * 80)
    print("RESULT FILES CREATED")
    print("=" * 80)

    print(f"📄 {benchmark_file}")
    print(f"📄 {metadata_file}")
    print(f"📄 {temperature_file}")


# ============================================================
# FINAL SUMMARY
# ============================================================

def display_summary():

    print("\n")
    print("=" * 100)
    print("MODULE 4 — MODEL BENCHMARK SUMMARY")
    print("=" * 100)

    print(
        f"{'MODEL':<22}"
        f"{'TEST':<28}"
        f"{'LATENCY':<12}"
        f"{'IN TOKENS':<12}"
        f"{'OUT TOKENS':<12}"
    )

    print("-" * 100)

    for row in benchmark_results:

        print(

            f"{row['model']:<22}"
            f"{row['test']:<28}"
            f"{str(row['latency_sec']):<12}"
            f"{str(row['input_tokens']):<12}"
            f"{str(row['output_tokens']):<12}"

        )

    print("=" * 100)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")

    print("=" * 80)
    print(
        "PHASE 1 — MODULE 4"
    )
    print(
        "MODEL FAMILIES & SELECTION"
    )
    print(
        "REAL OLLAMA MODEL BENCHMARK"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # STEP 1 — CHECK OLLAMA
    # --------------------------------------------------------

    if not check_ollama():

        return

    # --------------------------------------------------------
    # STEP 2 — TEST EACH MODEL
    # --------------------------------------------------------

    for model in MODELS:

        print("\n\n")

        print("=" * 80)
        print(
            f"NOW TESTING MODEL: {model}"
        )
        print("=" * 80)

        # Metadata

        model_info = display_model_info(
            model
        )

        # Capability summary

        capabilities = model_info.get(
            "capabilities",
            []
        )

        print("\n--- CAPABILITY CHECK ---")

        print(
            "Vision:       "
            + (
                "YES"
                if "vision" in capabilities
                else "NO / UNKNOWN"
            )
        )

        print(
            "Tool Calling: "
            + (
                "YES"
                if "tools" in capabilities
                else "NO / UNKNOWN"
            )
        )

        print(
            "Thinking:     "
            + (
                "YES"
                if "thinking" in capabilities
                else "NO / UNKNOWN"
            )
        )

        # Standard tests

        run_standard_tests(
            model
        )

        # Temperature tests

        run_temperature_test(
            model
        )

    # --------------------------------------------------------
    # STEP 3 — SUMMARY
    # --------------------------------------------------------

    display_summary()

    # --------------------------------------------------------
    # STEP 4 — SAVE RESULTS
    # --------------------------------------------------------

    save_results()

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("MODULE 4 PRACTICAL BENCHMARK COMPLETE")
    print("=" * 80)

    print(
        "\nNext step:"
    )

    print(
        "Review the generated CSV results "
        "and build the final Module 4 "
        "Model Selection Matrix."
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
