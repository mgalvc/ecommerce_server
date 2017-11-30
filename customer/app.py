from flask import Flask, render_template, request
import client
import sys
import json

app = Flask(__name__)
customer = client.Client()
location = sys.argv[1]

@app.route('/')
def index():
	products = customer.get_products()
	return render_template('/page.html', products=products)

@app.route('/get_shipping_tax', methods=['POST'])
def getShippingTax():
	itens = request.get_json()
	response = customer.get_shipping_tax(itens, location)
	return json.dumps(response)

if __name__ == '__main__':
	customer.connect_to_best_server()
	app.run(debug=True)