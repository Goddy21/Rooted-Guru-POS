import os
import sys
from kivy.lang import Builder

os.environ['KIVY_LOG_LEVEL'] = 'debug'

#from quickbooks import QuickBooks
#from quickbooks.objects.salesreceipt import SalesReceipt
#from quickbooks.objects.customer import Customer
#from quickbooks.objects.detailline import SalesItemLine, SalesItemLineDetail
#from quickbooks.objects.item import Item

#Q70G1700700 8F

#from session_manager.session_manager import QuickBooksSessionManager

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import re
from pymongo import MongoClient
import json
from escpos.printer import Usb, Network  
from kivy.config import Config
from datetime import datetime
from kivy.uix.tabbedpanel import TabbedPanel
from printer_form import PrinterConfigForm 
from kivy.uix.popup import Popup
from utils.paths import GURU_JPG

Config.set('kivy', 'window', 'sdl2')

#Builder.load_file('till_operator/operation.kv')
kv_path = os.path.join(os.path.dirname(__file__), 'operation.kv')
Builder.load_file(kv_path)

Builder.load_file(os.path.join(os.path.dirname(__file__), 'printer_config.kv'))

class TabbedPOS(TabbedPanel):
    pass

class OperationWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #session_manager = QuickBooksSessionManager()
        #qb_client = session_manager.get_quickbooks_client()

        self.payment_method = None  # Store selected payment method
        self.available_payment_methods = ['Cash', 'Credit Card', 'Mobile Payment']


        # QuickBooks initialization
        """
        try:
            self.qb_client = QuickBooks(
            sandbox=True,
            consumer_key=session_manager.client_id,
            consumer_secret=session_manager.client_secret,
            access_token=session_manager.access_token,
            company_id=session_manager.company_id
            )
        except Exception as e:
            print(f"Failed to initialize QuickBooks client: {e}")
            return
        """

        try:
            #mongodb://atlas-sql-672f3c5829142f0ad65fc45d-qzvb3.a.query.mongodb.net/silverpos?ssl=true&authSource=admin
            #self.client = MongoClient('mongodb+srv://Rooted-Guru:rootedguru@rooted-guru-pos.qzvb3.mongodb.net/?retryWrites=true&w=majority&appName=Rooted-Guru-POS')
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client.silverpos
            self.stocks = self.db.stocks
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            # Optionally, show a popup to notify the user

        self.cart = []
        self.qty = []
        self.total = 0.00

        # Initialize the USB printer
        try:
            #with open('printer_config.json') as f:
            def resource_path(relative_path):
                base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath('.')
                return os.path.join(base, relative_path)

            # then:
            with open(resource_path('printer_config.json')) as f:
                config = json.load(f)

            printer_type = config.get("type", "usb")

            if printer_type == "usb":
                vendor_id = int(config["vendor_id"], 16)
                product_id = int(config["product_id"], 16)
                self.printer = Usb(vendor_id, product_id)
            elif printer_type == "network":
                ip_address = config["ip"]
                self.printer = Network(ip_address)
            else:
                raise ValueError("Unsupported printer type in config")

        except Exception as e:
            print(f"[ERROR] Failed to initialize printer: {e}")
            self.printer = None 

    def on_kv_post(self, base_widget):
        self.ids.op_logo.source = GURU_JPG

    def logout(self):
        self.parent.parent.current = 'scrn_si'

    def update_purchases(self):
        print("update_purchases triggered")
        pcode = self.ids.code_inp.text.strip()
        if not pcode:
            return  

        products_container = self.ids.products

        try:
            target_code = self.stocks.find_one({'product_code': pcode})
        except Exception as e:
            print(f"Error querying MongoDB: {e}")
            return

        if target_code is None:
            print(f"Product code {pcode} not found.")
            return
        else:
            if pcode in self.cart:
                index = self.cart.index(pcode)
                self.qty[index] += 1
                # Update the qty label and total directly by accessing attributes
                product_widget = products_container.children[index]
                product_widget.qty_label.text = str(self.qty[index])
                pprice = float(target_code['product_price'])
                new_total = self.qty[index] * pprice
                product_widget.total_label.text = f"{new_total:.2f}"
                self.total += pprice
            else:
                # Add new product to cart
                self.cart.append(pcode)
                self.qty.append(1)
                self.total += float(target_code['product_price'])

                # Create a new product line in the UI
                details = ProductLine(
                    code=pcode,
                    name=target_code['product_name'],
                    qty=1,
                    disc=0.00,
                    price=target_code['product_price'],
                    total=target_code['product_price']
                )
                products_container.add_widget(details)

            self.update_preview(target_code['product_name'], target_code['product_price'])

        # Reset input fields
        self.ids.disc_inp.text = '0.00'
        self.ids.disc_perc_inp.text = '0'
        self.ids.qty_inp.text = '1'
        self.ids.price_inp.text = str(target_code['product_price'])
        self.ids.vat_inp.text = '15%'
        self.ids.total_inp.text = str(target_code['product_price'])

        # Clear the product code input for next entry
        self.ids.code_inp.text = ''
        self.ids.code_inp.focus = True

    def update_preview(self, pname, pprice):
        receipt = self.ids.receipt_preview
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        receipt_no = f"R{int(datetime.now().timestamp())}"

        # Construct receipt header if not already present
        if "Receipt No:" not in receipt.text:
            receipt.text += f"\n\nRooted Guru Sales Receipt\n\n"
            receipt.text += f"Tel: (+254)7266-100-18\n\n"
            receipt.text += f"Receipt No: {receipt_no}\n"
            receipt.text += f"Date: {date_str}\n\n"

        # Add product line to receipt
        receipt.text += f"{pname}\t x1\t\t{float(pprice):.2f}\n"

        # Update total 
        receipt.text = re.sub(r"\nTotal:.*", "", receipt.text)  
        receipt.text += f"\nTotal:\t\t\t{self.total:.2f}\n"

        # Update the current product and price display
        self.ids.cur_product.text = pname
        self.ids.cur_price.text = f"{float(pprice):.2f}"

    def select_payment_method(self, method):
        if method in self.available_payment_methods:
            self.payment_method = method
            print(f"Payment method selected: {self.payment_method}")
        else:
            print("Invalid payment method selected.")
        
        if (self.payment_method=='Cash'):
            print("Method used is cash")
        elif (self.payment_method=="Credit Card"):
            print("Method chosen is credit card")
        elif (self.payment_method=="Mobile Payment"):
            print("Method used is mobile payment")        


    def open_printer_settings(self):
        popup = Popup(
            title="Printer Configuration",
            content=PrinterConfigForm(),
            size_hint=(0.7, 0.7),
            auto_dismiss=True
        )
        popup.open()

    def print_receipt(self):
        if self.printer is None:
            print("Printer not initialized.")
            return

        receipt_text = self.ids.receipt_preview.text
        if self.payment_method:
            receipt_text += f"\nPayment Method: {self.payment_method}\n"

        try:
            self.printer.text(receipt_text)
            self.printer.cut()
            print("Receipt printed successfully.")
        except Exception as e:
            print(f"Failed to print receipt: {e}")



        # Create a new sales receipt
    def create_sales_receipt(self, customer_name, total_amount, items):
        sales_receipt = SalesReceipt()

        try:
            customers = Customer.where("DisplayName = '{0}'".format(customer_name), qb=self.qb_client)
        except Exception as e:
            print(f"Error fetching customer: {e}")
            return

        if not customers:
            customer = Customer()
            customer.DisplayName = customer_name
            customer.save(qb=self.qb_client)
        else:
            customer = customers[0]  # Fetch the first matched customer

        sales_receipt.CustomerRef = customer.to_ref()

        for item in items:
            line = SalesItemLine()
            line.Amount = item['amount']
            line.SalesItemLineDetail = SalesItemLineDetail()

            try:
                product_items = Item.where("Name = '{0}'".format(item['name']), qb=self.qb_client)
                if product_items:
                    product_item = product_items[0]  # Fetch the first matched item
                    line.SalesItemLineDetail.ItemRef = product_item.to_ref()
                else:
                    print(f"Item '{item['name']}' not found.")
                    continue  # Skip if the item is not found
            except Exception as e:
                print(f"Error fetching item '{item['name']}': {e}")
                continue  # Skip if there was an error

            sales_receipt.Line.append(line)

        try:
            sales_receipt.save(qb=self.qb_client)
        except Exception as e:
            print(f"Error saving sales receipt: {e}")



   
    def update_inventory(self, product_code, new_qty):
        item = Item.where("Sku = '{0}'".format(product_code), qb=self.qbo_client)
        if item:
            item.QtyOnHand = new_qty
            item.save(qb=qbo_client)
        else:
            print(f"Item with SKU {product_code} not found in QuickBooks.")

    def complete_transaction(self):
        if not self.cart:
            print("Cart is empty.")
            return

        # Prompt for payment method if not selected
        if not self.payment_method:
            print("Please select a payment method.")
            return

        # Generate receipt number and date
        receipt_no = f"R{int(datetime.now().timestamp())}"
        date_str = datetime.now()

        # Save transaction to database
        transaction = {
            'receipt_no': receipt_no,
            'date': date_str,
            'items': [],
            'total': self.total,
            'payment_method': self.payment_method  
        }

        # Populate transaction details
        for i, pcode in enumerate(self.cart):
            product = self.stocks.find_one({'product_code': pcode})
            if product:
                transaction['items'].append({
                    'product_code': pcode,
                    'product_name': product['product_name'],
                    'quantity': self.qty[i],
                    'price': product['product_price'],
                    'total': self.qty[i] * product['product_price']
                })

        # Insert into database
        try:
            self.db.transactions.insert_one(transaction)
            print("Transaction saved to database.")
        except Exception as e:
            print(f"Failed to save transaction: {e}")

        # Update receipt preview with payment method
        self.ids.receipt_preview.text += f"Payment Method: {self.payment_method}\n"

        # Print the receipt
        self.print_receipt()
        
        #Clear the receipt preview section
        self.ids.receipt_preview.text = 'Rooted Guru\nPoint Of Sale\nSystem\n'

       # Reset the cart, payment method, and UI
        self.reset_transaction()
        self.payment_method = None  


    def reset_transaction(self):
        self.cart.clear()
        self.qty.clear()
        self.total = 0.00
        #self.ids.receipt_preview.text = 'Rooted Guru\nPoint Of Sale\nSystem\n\nTel: (+254)-7266-100-18\nReceipt No:'+self.receipt_no+ '\nDate:'+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' \n\n'
        self.ids.cur_product.text = 'Default Product'
        self.ids.cur_price.text = '0.00'
        self.ids.products.clear_widgets()


class ProductLine(BoxLayout):
    def __init__(self, code, name, qty, disc, price, total, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 30

        # Define Labels with IDs for easy access
        self.code_label = Label(text=code, size_hint_x=.2, color=(.06, .45, .45, 1))
        self.name_label = Label(text=name, size_hint_x=.3, color=(.06, .45, .45, 1))
        self.qty_label = Label(text=str(qty), size_hint_x=.1, color=(.06, .45, .45, 1))
        self.disc_label = Label(text=f"{disc:.2f}", size_hint_x=.1, color=(.06, .45, .45, 1))
        self.price_label = Label(text=f"{price:.2f}", size_hint_x=.1, color=(.06, .45, .45, 1))
        self.total_label = Label(text=f"{total:.2f}", size_hint_x=.2, color=(.06, .45, .45, 1))

        # Add labels to the layout
        self.add_widget(self.code_label)
        self.add_widget(self.name_label)
        self.add_widget(self.qty_label)
        self.add_widget(self.disc_label)
        self.add_widget(self.price_label)
        self.add_widget(self.total_label)

class OperationApp(App):
    def build(self):
        return OperationWindow()

if __name__ == "__main__":
    oa = OperationApp()
    oa.run()
