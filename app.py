from flask import Flask, request, render_template, jsonify
import openai
import git
import os

# Set your OpenAI API key
openai.api_key = 'YOUR OPENAI API KEY'

app = Flask(__name__)

def check_license_for_commercial_use_and_drug_discovery(repo_url):
    # Clone the repository
    repo_path = '/tmp/repo'
    if os.path.exists(repo_path):
        os.system(f'rm -rf {repo_path}')
    repo = git.Repo.clone_from(repo_url, repo_path)

    # Check for LICENSE or LICENSE.md file
    license_files = ['LICENSE', 'LICENSE.md']
    license_content = None
    for license_file in license_files:
        file_path = os.path.join(repo_path, license_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                license_content = f.read()
            break

    if not license_content:
        return "LICENSE file not found in the repository.", None

    # Create a prompt to analyze the license content
    prompt = f"""
    The following is the content of a LICENSE file from a Git repository. Please analyze it and determine if the license allows the user to:
    1. Use the software for commercial purposes.
    2. Use the software for drug discovery purposes.
    
    LICENSE CONTENT:
    {license_content}
    
    Provide the answer in the following format:
    1. ** Commercial Use **: Yes/No
       ** Reasoning **: [Concisely explain why or why not]
    2. ** Drug Discovery **: Yes/No
       ** Reasoning **: [Concisely explain why or why not]
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant with expertise in software licensing."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0
    )

    # Extract and return the response
    answer = response.choices[0].message.content.strip()
    return answer, license_content

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/check_license', methods=['POST'])
def check_license():
    repo_url = request.json['repo_url']
    result, license_content = check_license_for_commercial_use_and_drug_discovery(repo_url)
    return jsonify({'result': result, 'license_content': license_content})

if __name__ == '__main__':
    app.run(debug=False)