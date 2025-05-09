import os

import gradio as gr

from background_replacer import replace_background

developer_mode = os.getenv('DEV_MODE', False)

DEFAULT_POSITIVE_PROMPT = "on the pavement, poolside, idyllic infinity pool, Hawaiian hilltops, commercial product photography"
DEFAULT_NEGATIVE_PROMPT = ""

EXAMPLES = [
    [
        "examples/black-sneakers-with-white-sole.jpg",
        "on the grass in Central Park, gorgeous summer day with Bethesda fountain in the background, commercial footwear product photography",
        "people, litter, trash, crowds, messy",
    ],
    [
        "examples/DIY-beard-balm.jpg",
        "on a mossy rock, white wood anemone blossoms, Loch Ken, Scotland",
        "purple, wrong proportions",
    ],
    [
        "examples/dj-making-music-on-mixer.jpg",
        "on the turntables with a packed dance floor, epic midnight edm party in Miami Beach, colorful nightlife photography",
        "disfigured, dismembered, mangled, marred",
    ],
    [
        "examples/jean-shorts-woman.jpg",
        "on the beach in Malibu, a five-star beachfront hotel in the background, stark late afternoon light near the dunes, lifestyle photography",
        "blurry background, ripples, soft focus, bokeh",
    ],
]

INTRO = """
# Shopify Image Background Replacement

[![Duplicate this Space](https://huggingface.co/datasets/huggingface/badges/resolve/main/duplicate-this-space-md.svg)](https://huggingface.co/spaces/Shopify/background-replacement?duplicate=true)
Minimum recommended hardware: Nvidia A10G large (46 GB RAM, 24 GB VRAM)

## Status
🏝️ Since the publication of this prototype, we've devoted our efforts to developing an enhanced version within Shopify's admin interface, which is now accessible to all Shopify merchants across all subscription plans. This original space is no longer maintained and runs on a CPU-only free tier. Please duplicate this space and utilize your own GPUs.

<hr>

Building an online store requires lots of high quality product and marketing images. This is an early demo of a background replacement tool built with Stable Diffusion XL that makes it easy to use your existing product images to make something new. Please be patient during peak demand. 😅

To use it, upload your product photo (.jpg or .png), then describe the background you’d like to see in place of the original. For best results follow the general pattern in the examples below:
1. ❌ _Do not_ describe your product in the prompt (ex: black sneakers)
2. ✅ Do describe the "grounding" for your product (ex: placed on a table)
3. ✅ Do describe the scene you want (ex: in a greek cottage)
4. ✅ Do describe a style of image (ex: side view commercial product photography)
5. 🤔 Optionally, describe what you want to avoid 🙅 in the negative prompt field
"""

MORE_INFO = """
### More information
- You can check our [FAQs here](https://huggingface.co/spaces/Shopify/background-replacement/blob/main/README.md#faqs)!
- We are also gathering resources from the community and sharing ideas [here](https://huggingface.co/spaces/Shopify/background-replacement/discussions).
- Shopify is on a mission to redefine commerce with AI. If you’re an AI or ML engineer looking to build the future of commerce, [join us](https://www.shopify.com/careers)!
"""


def generate(
    image,
    positive_prompt,
    negative_prompt,
    seed,
    depth_map_feather_threshold,
    depth_map_dilation_iterations,
    depth_map_blur_radius,
    progress=gr.Progress(track_tqdm=True)
):
    if image is None:
        return [None, None, None, None]

    options = {
        'seed': seed,
        'depth_map_feather_threshold': depth_map_feather_threshold,
        'depth_map_dilation_iterations': depth_map_dilation_iterations,
        'depth_map_blur_radius': depth_map_blur_radius,
    }

    return replace_background(image, positive_prompt, negative_prompt, options)


custom_css = """
    #image-upload {
        flex-grow: 1;
    }
    #params .tabs {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    #params .tabitem[style="display: block;"] {
        flex-grow: 1;
        display: flex !important;
    }
    #params .gap {
        flex-grow: 1;
    }
    #params .form {
        flex-grow: 1 !important;
    }
    #params .form > :last-child{
        flex-grow: 1;
    }
    .md ol, .md ul {
        margin-left: 1rem;
    }
    .md img {
        margin-bottom: 1rem;
    }
"""

with gr.Blocks(css=custom_css) as iface:
    gr.Markdown(INTRO)

    with gr.Row():
        with gr.Column():
            image_upload = gr.Image(
                label="Product image",
                type="pil",
                elem_id="image-upload"
            )
            caption = gr.Label(
                label="Caption",
                visible=developer_mode
            )
        with gr.Column(elem_id="params"):
            with gr.Tab('Prompts'):
                positive_prompt = gr.Textbox(
                    label="Positive Prompt: describe what you'd like to see",
                    lines=3,
                    value=DEFAULT_POSITIVE_PROMPT
                )
                negative_prompt = gr.Textbox(
                    label="Negative Prompt: describe what you want to avoid",
                    lines=3,
                    value=DEFAULT_NEGATIVE_PROMPT
                )
            if developer_mode:
                with gr.Tab('Options'):
                    seed = gr.Number(
                        label="Seed",
                        precision=0,
                        value=0,
                        elem_id="seed",
                        visible=developer_mode
                    )
                    depth_map_feather_threshold = gr.Slider(
                        label="Depth map feather threshold",
                        value=128,
                        minimum=0,
                        maximum=255,
                        visible=developer_mode
                    )
                    depth_map_dilation_iterations = gr.Number(
                        label="Depth map dilation iterations",
                        precision=0,
                        value=10,
                        minimum=0,
                        visible=developer_mode
                    )
                    depth_map_blur_radius = gr.Number(
                        label="Depth map blur radius",
                        precision=0,
                        value=10,
                        minimum=0,
                        visible=developer_mode
                    )
            else:
                seed = gr.Number(value=-1, visible=False)
                depth_map_feather_threshold = gr.Slider(
                    value=128, visible=False)
                depth_map_dilation_iterations = gr.Number(
                    precision=0, value=10, visible=False)
                depth_map_blur_radius = gr.Number(
                    precision=0, value=10, visible=False)

    # Enable this button!
    gen_button = gr.Button(
        value="Generate!", variant="primary", interactive=True)

    with gr.Tab('Results'):
        results = gr.Gallery(
            show_label=False,
            object_fit="contain",
            columns=4
        )

    if developer_mode:
        with gr.Tab('Generated'):
            generated = gr.Gallery(
                show_label=False,
                object_fit="contain",
                columns=4
            )

        with gr.Tab('Pre-processing'):
            pre_processing = gr.Gallery(
                show_label=False,
                object_fit="contain",
                columns=4
            )
    else:
        generated = gr.Gallery(visible=False)
        pre_processing = gr.Gallery(visible=False)

    gr.Examples(
        examples=EXAMPLES,
        inputs=[image_upload, positive_prompt, negative_prompt],
    )

    gr.Markdown(MORE_INFO)

    gen_button.click(
        fn=generate,
        inputs=[
            image_upload,
            positive_prompt,
            negative_prompt,
            seed,
            depth_map_feather_threshold,
            depth_map_dilation_iterations,
            depth_map_blur_radius
        ],
        outputs=[
            results,
            generated,
            pre_processing,
            caption
        ],
    )

iface.queue(max_size=10, api_open=False).launch(show_api=False)
