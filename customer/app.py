from flask import Flask, render_template, request
import client
import sys

app = Flask(__name__)
customer = client.Client()

@app.route('/')
def index():
	products = customer.get_products()
	return render_template('/page.html', products=products)

if __name__ == '__main__':
	customer.connect_to_best_server()
	app.run(debug=True)