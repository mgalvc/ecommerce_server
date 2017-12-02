from flask import Flask, render_template, request
import client
import sys
import json

app = Flask(__name__)
location = sys.argv[1]
node_addr = (sys.argv[2], int(sys.argv[3]))
customer = client.Client(node_addr)

@app.route('/')
def index():
	products = customer.get_products()
	return render_template('/page.html', products=products)

@app.route('/get_shipping_tax', methods=['POST'])
def getShippingTax():
	itens = request.get_json()
	response = customer.get_shipping_tax(itens, location)
	return json.dumps(response)

@app.route('/proceed_checkout', methods=['POST'])
def proceedCheckout():
	msg = request.get_json()
	response = customer.proceed_checkout(msg)
	return json.dumps(response)

if __name__ == '__main__':
	customer.connect_to_best_server()
	app.run(debug=True)