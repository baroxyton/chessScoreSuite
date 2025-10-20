# chessScoreSuite

## How to Use

### Running the API

1. Clone the repository: `git clone https://github.com/baroxyton/chessScoreSuite && cd chessScoreSuite`

2. Activate the venv: `python -m venv venv && source ./venv/bin/activate`

3. Install the dependencies: `pip install -r requirements.txt`

4. Obtain a model, eg.: `mkdir models && cd models && wget https://huggingface.co/baroxyton/chess_model/resolve/main/results.sqlite && cd ..`

5. Start the API: `./api/start.sh`

6. Use via the web interface, evaluation or a different app.

### Running the Web Interface

1. Start the API

2. Locate the web interface directory: `cd chessScoreSuite/apps/explorer`

3. Install the dependencies: `npm i`

4. Start the web interface: `npm run dev`

5. Open the interface in the browser on http://localhost:5173/

### Evaluating Performance

1. Start the API

2. Locate the evaluation folder: `cd chessScoreSuite/apps/eval-model`

3. Run `main.py` with different options for different tests

4. Use scripts in `graph_results` to plot and interpret results
