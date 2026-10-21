import requests
import json
import time
import os


OLLAMA_URL = "http://172.16.2.53:11434"

CHAT_URL = f"{OLLAMA_URL}/api/chat"
SHOW_URL = f"{OLLAMA_URL}/api/show"


# ============================================================
# MODELS
# ============================================================

MODELS = [
    "gemma4",
    "qwen3.6",
    "docker-expert",
    "gemma:test",
    "gemma",
]


# ============================================================
# QWEN3.6 DIAGNOSTIC
# ============================================================

def test_model_availability(model):

    print("\n" + "=" * 70)
    print(f"MODEL AVAILABILITY TEST: {model}")
    print("=" * 70)

    try:

        response = requests.post(
            SHOW_URL,
            json={"name": model},
            timeout=30
        )

        print("HTTP Status:", response.status_code)

        if response.ok:

            data = response.json()

            print("✅ Model is accessible through Ollama API.")

            details = data.get("details", {})

            print("Family:",
                  details.get("family", "N/A"))

            print("Parameters:",
                  details.get("parameter_size", "N/A"))

            print("Quantization:",
                  details.get("quantization_level", "N/A"))

            print("Capabilities:",
                  data.get("capabilities", []))

            return True

        else:

            print("❌ Ollama returned an error.")

            print(response.text)

            return False

    except Exception as e:

        print("❌ Connection/API error:")
        print(e)

        return False


# ============================================================
# BASIC CHAT TEST
# ============================================================

def basic_chat(model):

    print("\n" + "-" * 70)
    print(f"BASIC CHAT TEST: {model}")
    print("-" * 70)

    payload = {

        "model": model,

        "messages": [
            {
                "role": "user",
                "content":
                    "Explain what DNS does in one sentence."
            }
        ],

        "stream": False,

        "options": {
            "temperature": 0.2
        }
    }

    try:

        start = time.perf_counter()

        response = requests.post(
            CHAT_URL,
            json=payload,
            timeout=300
        )

        elapsed = time.perf_counter() - start

        print("HTTP Status:", response.status_code)
        print("Latency:", round(elapsed, 2), "seconds")

        if response.ok:

            data = response.json()

            print("\nResponse:")
            print(
                data.get("message", {})
                    .get("content", "")
            )

            return True

        else:

            print("ERROR:")
            print(response.text)

            return False

    except Exception as e:

        print("ERROR:")
        print(e)

        return False


# ============================================================
# VISION TEST
# ============================================================

def vision_test(model, image_path):

    print("\n" + "=" * 70)
    print(f"VISION TEST: {model}")
    print("=" * 70)

    if not os.path.exists(image_path):

        print("❌ Image not found:")
        print(image_path)

        return

    try:

        import base64

        with open(
            image_path,
            "rb"
        ) as image_file:

            image_data = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        payload = {

            "model": model,

            "messages": [

                {
                    "role": "user",

                    "content": """
Analyze this image.

Describe:
1. What objects or elements are visible.
2. Any text that can be read.
3. The overall purpose/context of the image.

Keep the answer concise.
""",

                    "images": [
                        image_data
                    ]
                }

            ],

            "stream": False,

            "options": {
                "temperature": 0.2
            }

        }

        start = time.perf_counter()

        response = requests.post(
            CHAT_URL,
            json=payload,
            timeout=300
        )

        elapsed = time.perf_counter() - start

        print("HTTP Status:", response.status_code)
        print("Latency:", round(elapsed, 2), "seconds")

        if response.ok:

            data = response.json()

            print("\nVISION RESPONSE:")
            print(
                data.get("message", {})
                    .get("content", "")
            )

        else:

            print("❌ Vision request failed:")
            print(response.text)

    except Exception as e:

        print("❌ Vision test error:")
        print(e)


# ============================================================
# TOOL CALLING TEST
# ============================================================

def get_server_status(server_name):

    """
    Simulated infrastructure tool.

    This deliberately does NOT contact a real server.
    It demonstrates the model -> tool -> result workflow.
    """

    fake_inventory = {

        "DC01": {
            "status": "Online",
            "ip": "192.168.1.10",
            "role": "Domain Controller"
        },

        "FILE01": {
            "status": "Online",
            "ip": "192.168.1.20",
            "role": "File Server"
        }

    }

    return fake_inventory.get(
        server_name,
        {
            "status": "Unknown"
        }
    )


TOOLS = [

    {
        "type": "function",

        "function": {

            "name": "get_server_status",

            "description":
                "Get the status and details of a server.",

            "parameters": {

                "type": "object",

                "properties": {

                    "server_name": {

                        "type": "string",

                        "description":
                            "Name of the server."

                    }

                },

                "required": [
                    "server_name"
                ]

            }

        }

    }

]


def tool_calling_test(model):

    print("\n" + "=" * 70)
    print(f"TOOL CALLING TEST: {model}")
    print("=" * 70)

    payload = {

        "model": model,

        "messages": [

            {
                "role": "user",

                "content":
                    "Check the status of server DC01."
            }

        ],

        "tools": TOOLS,

        "stream": False,

        "options": {

            "temperature": 0.0

        }

    }

    try:

        response = requests.post(
            CHAT_URL,
            json=payload,
            timeout=300
        )

        print("HTTP Status:", response.status_code)

        if not response.ok:

            print("❌ Tool request failed:")
            print(response.text)

            return

        data = response.json()

        message = data.get(
            "message",
            {}
        )

        tool_calls = message.get(
            "tool_calls",
            []
        )

        if tool_calls:

            print("\n✅ MODEL REQUESTED A TOOL CALL")

            for call in tool_calls:

                function = call.get(
                    "function",
                    {}
                )

                name = function.get(
                    "name"
                )

                arguments = function.get(
                    "arguments",
                    {}
                )

                print("\nTool:", name)
                print(
                    "Arguments:",
                    json.dumps(
                        arguments,
                        indent=2
                    )
                )

                # Execute our simulated tool

                if name == "get_server_status":

                    server_name = arguments.get(
                        "server_name"
                    )

                    result = get_server_status(
                        server_name
                    )

                    print("\nTool Result:")
                    print(
                        json.dumps(
                            result,
                            indent=2
                        )
                    )

        else:

            print(
                "\n⚠️ Model did not request a tool."
            )

            print("\nModel response:")

            print(
                message.get(
                    "content",
                    ""
                )
            )

    except Exception as e:

        print("❌ Tool test error:")
        print(e)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("PHASE 1 — MODULE 4 FINAL PRACTICAL TESTS")
    print("=" * 70)

    # --------------------------------------------------------
    # QWEN + MODEL AVAILABILITY
    # --------------------------------------------------------

    print("\nMODEL AVAILABILITY")

    availability = {}

    for model in MODELS:

        availability[model] = \
            test_model_availability(model)

    # --------------------------------------------------------
    # BASIC TEST FOR QWEN
    # --------------------------------------------------------

    if availability.get("qwen3.6"):

        basic_chat("qwen3.6")

    # --------------------------------------------------------
    # VISION
    #
    # Put an image in the same directory and name it:
    #
    # module4_test_image.png
    # --------------------------------------------------------

    image_path = "module4_test_image.png"

    if availability.get("gemma4"):

        vision_test(
            "gemma4",
            image_path
        )

    # --------------------------------------------------------
    # TOOL CALLING
    # --------------------------------------------------------

    for model in MODELS:

        if availability.get(model):

            tool_calling_test(model)

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("MODULE 4 FINAL TESTS FINISHED")
    print("=" * 70)


if __name__ == "__main__":

    main()
