


import mimetypes
import time

from django.shortcuts import get_object_or_404, redirect

from google import genai
from google.genai import types

from .models import Damage_image_check, Insurancecompany


# =========================================================
# GOOGLE GEMINI API KEY
# =========================================================

# IMPORTANT:
# Replace this locally with your NEW rotated Gemini API key.
# Do NOT print the API key.
GOOGLE_API_KEY = ""


# =========================================================
# ANALYZE VEHICLE DAMAGE
# =========================================================

def analyze_damage(request, id):

    if request.method != "POST":
        return redirect(
            "insurance_damage_details",
            id=id
        )

    # -----------------------------------------------------
    # Get logged-in insurance company
    # -----------------------------------------------------

    insurance = get_object_or_404(
        Insurancecompany,
        USER_id=request.user.id
    )

    # -----------------------------------------------------
    # Get damage record
    # -----------------------------------------------------

    damage = get_object_or_404(
        Damage_image_check,
        id=id,
        INSURANCE=insurance
    )

    # -----------------------------------------------------
    # Check all six images
    # -----------------------------------------------------

    image_fields = [
        ("FRONT VIEW", damage.frontimage),
        ("BACK VIEW", damage.backimage),
        ("LEFT SIDE", damage.leftside),
        ("RIGHT SIDE", damage.rightsideimage),
        ("TOP VIEW", damage.topimage),
        ("BOTTOM VIEW", damage.bottumimage),
    ]

    for label, image_field in image_fields:

        if not image_field:

            damage.status = "Analysis Failed"

            damage.image_overall_damage_description = (
                f"{label} image is missing."
            )

            damage.save(
                update_fields=[
                    "status",
                    "image_overall_damage_description"
                ]
            )

            return redirect(
                "insurance_damage_details",
                id=id
            )

    # -----------------------------------------------------
    # Set processing status
    # -----------------------------------------------------

    damage.status = "Analysis Processing"

    damage.save(
        update_fields=[
            "status"
        ]
    )

    # -----------------------------------------------------
    # Gemini AI
    # -----------------------------------------------------

    try:

        print("\n======================================")
        print("STARTING GEMINI DAMAGE ANALYSIS")
        print("======================================")

        # -------------------------------------------------
        # Check API key
        # -------------------------------------------------

        if not GOOGLE_API_KEY:

            raise Exception(
                "Gemini API key is missing."
            )

        # -------------------------------------------------
        # Create Gemini client
        # -------------------------------------------------

        client = genai.Client(
            api_key=GOOGLE_API_KEY
        )

        # -------------------------------------------------
        # AI PROMPT
        # -------------------------------------------------

        prompt = """
You are an AI vehicle damage inspection assistant
for an insurance company.

You are given six photographs of the same vehicle.

The photographs represent:

1. FRONT VIEW
2. BACK VIEW
3. LEFT SIDE
4. RIGHT SIDE
5. TOP VIEW
6. BOTTOM VIEW

Analyze ALL six images carefully.

Identify ONLY damage that is clearly visible
in the photographs.

For every view identify:

- Visible damage
- Damaged vehicle part
- Damage type
- Damage severity
- Scratches
- Dents
- Cracks
- Broken components
- Paint damage
- Deformation
- Missing parts
- Other clearly visible damage

DO NOT invent damage.

If no clear damage is visible, write:

"No clearly visible damage."

Use this exact structure:

==================================================
VEHICLE DAMAGE INSPECTION REPORT
==================================================

1. FRONT VIEW
--------------------------------------------------
Damage:
Damaged Parts:
Damage Type:
Severity:
Detailed Observation:

2. BACK VIEW
--------------------------------------------------
Damage:
Damaged Parts:
Damage Type:
Severity:
Detailed Observation:

3. LEFT SIDE
--------------------------------------------------
Damage:
Damaged Parts:
Damage Type:
Severity:
Detailed Observation:

4. RIGHT SIDE
--------------------------------------------------
Damage:
Damaged Parts:
Damage Type:
Severity:
Detailed Observation:

5. TOP VIEW
--------------------------------------------------
Damage:
Damaged Parts:
Damage Type:
Severity:
Detailed Observation:

6. BOTTOM VIEW
--------------------------------------------------
Damage:
Damaged Parts:
Damage Type:
Severity:
Detailed Observation:

==================================================
OVERALL DAMAGE ASSESSMENT
==================================================

Major Damaged Areas:

Overall Severity:

Visible Damage Summary:

Potentially Affected Components:

Recommended Physical Inspection:

==================================================
FINAL SUMMARY
==================================================

Provide a concise overall summary of the
visible vehicle damage.

IMPORTANT RULES:

1. Only analyze damage visible in the photographs.
2. Do not invent hidden or internal damage.
3. Do not provide a monetary repair estimate.
4. Do not determine an insurance claim amount.
5. Do not state that the vehicle is completely safe
   or unsafe based only on photographs.
6. If an image is unclear, explicitly mention that.
7. This is a preliminary visual assessment.
8. The final assessment should be reviewed by
   an insurance professional.
"""

        # -------------------------------------------------
        # Prepare Gemini contents
        # -------------------------------------------------

        contents = []

        contents.append(prompt)

        # -------------------------------------------------
        # Add all six images
        # -------------------------------------------------

        for label, image_field in image_fields:

            print(
                f"Reading image: {label}"
            )

            image_field.open("rb")

            try:
                image_bytes = image_field.read()
            finally:
                image_field.close()

            if not image_bytes:

                raise Exception(
                    f"{label} image is empty."
                )

            mime_type, _ = mimetypes.guess_type(
                image_field.name
            )

            if not mime_type:

                mime_type = "image/jpeg"

            contents.append(
                f"\n\n===== {label} ====="
            )

            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
            )

        # -------------------------------------------------
        # Gemini model retry system
        # -------------------------------------------------

        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash"
        ]

        response = None
        last_error = None

        # -------------------------------------------------
        # Try models
        # -------------------------------------------------

        for model_name in models_to_try:

            print("\n======================================")
            print(
                f"TRYING MODEL: {model_name}"
            )
            print("======================================")

            # Try each model up to 3 times
            for attempt in range(3):

                try:

                    print(
                        f"Attempt {attempt + 1}/3"
                    )

                    print(
                        "Sending six images to Gemini..."
                    )

                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents
                    )

                    # -------------------------------------
                    # Check response
                    # -------------------------------------

                    if response and response.text:

                        print(
                            f"SUCCESS: {model_name}"
                        )

                        break

                    else:

                        raise Exception(
                            "Gemini returned an empty response."
                        )

                except Exception as e:

                    last_error = e

                    error_message = str(e)

                    print("\n--------------------------------------")
                    print("GEMINI REQUEST ERROR")
                    print("--------------------------------------")
                    print(error_message)
                    print("--------------------------------------")

                    # -------------------------------------
                    # Temporary errors
                    # -------------------------------------

                    temporary_error = (
                        "503" in error_message
                        or
                        "UNAVAILABLE" in error_message
                        or
                        "429" in error_message
                        or
                        "RESOURCE_EXHAUSTED" in error_message
                    )

                    # -------------------------------------
                    # Retry temporary errors
                    # -------------------------------------

                    if temporary_error:

                        if attempt < 2:

                            print(
                                "Temporary Gemini error."
                            )

                            print(
                                "Waiting 5 seconds..."
                            )

                            time.sleep(5)

                            continue

                        else:

                            print(
                                f"{model_name} failed "
                                "after 3 attempts."
                            )

                            break

                    # -------------------------------------
                    # Don't retry other errors
                    # -------------------------------------

                    else:

                        print(
                            "Non-retryable Gemini error."
                        )

                        raise e

            # -------------------------------------------------
            # Stop if successful
            # -------------------------------------------------

            if response and response.text:

                break

        # -------------------------------------------------
        # Final response check
        # -------------------------------------------------

        if not response or not response.text:

            if last_error:

                raise last_error

            raise Exception(
                "Gemini did not return a valid response."
            )

        # -------------------------------------------------
        # Get AI result
        # -------------------------------------------------

        result = response.text

        # -------------------------------------------------
        # Save AI result
        # -------------------------------------------------

        damage.image_overall_damage_description = result

        damage.status = "Analysis Completed"

        damage.save(
            update_fields=[
                "image_overall_damage_description",
                "status"
            ]
        )

        # -------------------------------------------------
        # Console output
        # -------------------------------------------------

        print("\n======================================")
        print("GEMINI DAMAGE ANALYSIS COMPLETED")
        print("======================================")

        print(result)

        print("======================================")

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        print("\n======================================")
        print("GEMINI DAMAGE ANALYSIS ERROR")
        print("======================================")

        print(str(e))

        print("======================================")

        damage.status = "Analysis Failed"

        damage.image_overall_damage_description = (
            "AI damage analysis could not be completed.\n\n"
            "Please try the Analyze Damage button again "
            "after a short time.\n\n"
            f"Technical Error: {str(e)}"
        )

        damage.save(
            update_fields=[
                "image_overall_damage_description",
                "status"
            ]
        )

    # -----------------------------------------------------
    # Return to damage details page
    # -----------------------------------------------------

    return redirect(
        "insurance_damage_details",
        id=id
    )