from flask import Flask, render_template, request
import client
import sys

app = Flask(__name__)
warehouse = client.Client()

@app.route('/')
def index():
	return render_template('/page.html')

@app.route('/send_itens', methods=['POST'])
def send_itens():
	itens = request.get_json()
	itens_map = {}
	for item in itens.get('itens'):
		itens_map.update({
			item.get('product'): int(item.get('quantity'))
		})
	print(itens_map)
	warehouse.update_servers(itens_map)

	return 'got your message'

if __name__ == '__main__':
	# warehouse.config(sys.argv[1], int(sys.argv[2]))
	app.run(debug=True, port=5001)