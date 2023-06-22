import time
import requests
import openai
from flask import Flask, render_template, request, jsonify, json
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS


openai.api_key = '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'
COMPLETIONS_MODEL = "text-davinci-003"
QUESTION_COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.3,
    "max_tokens": 1000,
    "model": COMPLETIONS_MODEL,
}

auth = HTTPBasicAuth()
application = Flask(__name__)
CORS(application)
application.config['SECRET_KEY'] = 'AIFUNOCUQJOR9C20NTV2N!@#$%^&*()_.'


@application.route('/', defaults={'path': ''}, methods=['GET'])
@application.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


@application.route('/')
def index():
    return render_template('index.html')


@application.post('/presentation')
def get_presentation():
    data = request.get_json()
    print(data)
    Topic = data['topic']
    print(Topic)
    # prompt = f"""Generate a presentation on the topic of {Topic}. The generated presentation should be a list of dictionaries, where each dictionaries is representing a slide. The first dictionary of the presentation should contains Only name of the presentation, The second dictionary should only contains the table of content of the presentation.  rest of the dictionaries should have the following key-value pairs:
    # 'heading': (Specify the heading of the slide)
    # 'content': (Provide the content for the slide regarding its heading and explain it in 30 to 40 words)
    # 'image_prompt': (generate a prompt for the image, which should be relevant to the content)"""
    prompt = f"""Generate a presentation on the topic of {Topic}. The generated presentation should be a Python list of dictionaries in proper format so we can use json.loads() on it, where each dictionary represents a slide and key-value should be in double quotes. The first dictionary of the presentation should contain only the name of the presentation. The second dictionary should contain only the "table_of_contents" of the presentation. The remaining dictionaries should have the following key-value pairs:
    'heading': (Specify the heading of the slide)
    'content': (Provide the content for the slide regarding its heading and explain it in 30 to 40 words)
    'image_prompt': (Give me a descriptive and effective Stable Diffusion Prompt of 50 words to generate unique images about provided content)
    "
    """
    search_prompt = openai.Completion.create(
        prompt=prompt,
        **QUESTION_COMPLETIONS_API_PARAMS
    )
    updatedList = []

    list = search_prompt["choices"][0]["text"].strip()
    list = json.loads(list)
    for slide in list:
        # print(slide)
        if slide.get('image_prompt'):
            print('IN Main IF')
            text = slide['image_prompt']
            url = "https://stablediffusionapi.com/api/v3/text2img"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "key": 'QJkQ5OQDbmrPPuQNKOubb3DSFQkQmQm13IVVFrP9OfUFUJWm328gDlgIAQfW',
                "prompt": f"{text}"
                f" Canon EOS R3, nikon, f/1.4, ISO 200, 1/160s, 8K, RAW, unedited, symmetrical balance, in-frame, 8K",
                "negative_prompt": "((out of frame)), ((extra fingers)), mutated hands,"
                " ((poorly drawn hands)), ((poorly drawn face)),(((mutation))), (((deformed))),"
                " (((tiling))), ((naked)), ((tile)), ((fleshpile)), ((ugly)), (((abstract))), blurry,"
                " ((bad anatomy)), ((bad proportions)), ((extra limbs)), cloned face, (((skinny))), "
                "glitchy, ((extra breasts)), ((double torso)), ((extra arms)), ((extra hands)), "
                "((mangled fingers)), ((missing breasts)), (missing lips), ((ugly face)), ((fat)), "
                "((extra legs)), anime",
                "width": "512",
                "height": "512",
                "samples": "1",
                "num_inference_steps": "20",
                "seed": "",
                "guidance_scale": 7.5,
                "safety_checker": "yes",
                "webhook": "",
                "track_id": ""
            }
            while True:
                print('in WHILE TRUE to generate images')
                try:
                    response = requests.post(
                        url, json=payload, headers=headers)
                    dat = response.text
                    response_dict = json.loads(dat)
                    if response_dict['status'] == 'success':
                        output_list = response_dict['output']
                        link = output_list[0]
                        break
                    #     return jsonify(output_list[0])

                    # else:
                    #     return jsonify(response_dict['message'])
                except:
                    time.sleep(30)
                    continue
            slide['link'] = link
            slide.pop('image_prompt')
            # print(slide)
            updatedList.append(slide)

        else:
            updatedList.append(slide)
    # print(updatedList)

    return jsonify(updatedList)


if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=5000)
