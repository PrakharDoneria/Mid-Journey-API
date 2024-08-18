import os
from flask import Flask, request, jsonify
from gradio_client import Client
import requests
import base64

app = Flask(__name__)

# Gradio Client setup
client = Client("mukaist/Midjourney")

# Function to upload image to ImgBB
def upload_to_imgbb(image_path):
    
    imgbb_api_key = os.getenv('IMGBB_API_KEY')

    if not imgbb_api_key:
        return None

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': imgbb_api_key,
        'image': encoded_image,
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        return None

@app.route('/imagine', methods=['GET'])
def imagine():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    
    result = client.predict(
        prompt=prompt,
        negative_prompt="(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
        use_negative_prompt=True,
        style="2560 x 1440",
        seed=0,
        width=1024,
        height=1024,
        guidance_scale=6,
        randomize_seed=True,
        api_name="/run"
    )

    image_url = upload_to_imgbb(result)

    if image_url:
        return jsonify({"img": image_url})
    else:
        return jsonify({"error": "Image upload failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
