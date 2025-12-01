import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

def read_excel_data(file_path):
    """Read and process the Excel file"""
    try:
        df = pd.read_excel(file_path)
        # Clean column names (remove extra spaces and make lowercase)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def process_orders(df):
    """Group orders by phone number and prepare messages"""
    if df is None or df.empty:
        return {}
    
    # Group by phone number (assuming there's a 'phone' column)
    # You might need to adjust the column names based on your Excel file
    grouped = df.groupby('phone')
    
    messages = {}
    for phone, group in grouped:
        if pd.isna(phone) or str(phone).strip() == '':
            continue
            
        # Format phone number (remove any non-digit characters)
        phone = ''.join(filter(str.isdigit, str(phone)))
        
        # Start building the message
        customer_name = group.iloc[0].get('name', 'Valued Customer')
        message = f"*Order Verification*\n\n"
        message += f"Dear {customer_name},\n\n"
        message += "Please verify your order details:\n\n"
        
        # Add order details
        total_amount = 0
        for _, row in group.iterrows():
            product = row.get('product', 'N/A')
            sku = row.get('sku', 'N/A')
            size = row.get('size', 'N/A')
            quantity = row.get('quantity', 1)
            price = row.get('price', 0)
            
            message += f"- {product} (SKU: {sku})\n"
            message += f"  Size: {size}, Qty: {quantity}, Price: {price * quantity:.2f}\n\n"
            total_amount += price * quantity
        
        # Add address and total
        address = group.iloc[0].get('address', 'Not provided')
        message += f"*Shipping Address:*\n{address}\n\n"
        message += f"*Total Amount: {total_amount:.2f}*\n\n"
        message += "Please reply with 'YES' to confirm your order or 'NO' if there's any mistake.\n"
        message += "Thank you for shopping with us!"
        
        messages[phone] = message
    
    return messages

def send_whatsapp_messages(messages):
    """Send messages via WhatsApp Web"""
    if not messages:
        print("No messages to send.")
        return
    
    print("Starting WhatsApp Web...")
    
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com")
        
        # Wait for user to scan QR code
        input("Please scan the QR code and press Enter after you're logged in...")
        
        for phone, message in messages.items():
            try:
                # Open chat with the phone number
                driver.get(f"https://web.whatsapp.com/send?phone={phone}")
                
                # Wait for the chat to load
                time.sleep(10)  # Adjust this delay as needed
                
                # Find the message input box
                message_box = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'))
                )
                
                # Type the message
                message_box.send_keys(message)
                
                # Find and click the send button
                send_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span'))
                )
                send_button.click()
                
                print(f"Message sent to {phone}")
                time.sleep(5)  # Wait before sending next message
                
            except Exception as e:
                print(f"Failed to send message to {phone}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Keep the browser open for 30 seconds before closing
        print("Script completed. Browser will close in 30 seconds...")
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    # Path to your Excel file
    excel_file = "Sample.xlsx"
    
    # Read and process the data
    print(f"Reading data from {excel_file}...")
    df = read_excel_data(excel_file)
    
    if df is not None:
        print("Processing orders...")
        messages = process_orders(df)
        
        if messages:
            print(f"\n--- Sample Message ---")
            print(list(messages.values())[0])  # Show first message as sample
            print("----------------------\n")
            
            confirm = input(f"Ready to send {len(messages)} messages. Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                send_whatsapp_messages(messages)
            else:
                print("Operation cancelled by user.")
        else:
            print("No valid orders found in the Excel file.")
    else:
        print("Failed to read the Excel file. Please check the file path and try again.")
