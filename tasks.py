import csv
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from time import sleep
from RPA.PDF import PDF
from RPA.Archive import Archive
from shutil import rmtree

ORDER_FILE_URL = 'https://robotsparebinindustries.com/orders.csv'
ROBOT_ORDER_URL = 'https://robotsparebinindustries.com/#/robot-order'

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    
    file_name = download_orders_file()
    records = get_orders(file_name)
    order_the_robots_from_browser(records)
    archive_receipts(input_folder='output/receipts',output_path='output/receipts.zip')
    cleanup(['output/receipts','output/temp'])

    

def download_orders_file()->str:
    HTTP().download(ORDER_FILE_URL,'Orders.csv',overwrite=True)
    return 'Orders.csv'

def get_orders(file_path):
    records = []
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        records = [row for row in reader]
    return records

def order_the_robots_from_browser(records):
    browser.configure(slowmo=300)
    browser.goto(ROBOT_ORDER_URL)
    page = browser.page()
    sleep(10)
    # page.click("//button[text()='OK']")
    
    sleep(10)
    for record in records:
        submit_order_details(page,record)
        sleep(5)
        


def submit_order_details(page,record):
    page = browser.page()
    page.click("//button[text()='OK']")
    page.select_option("//select[@id='head']",record['Head'])
    page.click(f"//input[@id='id-body-{record['Body']}']")
    page.fill("//input[@placeholder='Enter the part number for the legs']",record['Legs'])
    page.fill("//input[@id='address']",record['Address'])
    page.click("//button[@id='preview']")
    capture_robot_preview(page)
    page.click("//button[@id='order']")
    
    error_occured = page.is_visible("//div[@class='alert alert-danger' and @role='alert' and contains(text(),'Error')]")
    while error_occured:
        page.click("//button[@id='order']")
        error_occured = page.is_visible("//div[@class='alert alert-danger' and @role='alert' and contains(text(),'Error')]")




    capture_order_details(page,record['Order number'])
    page.click("//button[@id='order-another']")


# External Server Error
def capture_robot_preview(page):
    page = browser.page().locator("//div[@id='robot-preview-image']").screenshot(path='output/temp/robot.jpeg')

def capture_order_details(page,order_number):
    page = browser.page()
    receipt_as_html = page.locator("//div[@id='order-completion']/div").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_as_html,'output/temp/receipt.pdf')
    pdf.add_watermark_image_to_pdf(image_path='output/temp/robot.jpeg',source_path='output/temp/receipt.pdf',output_path=f'output/receipts/receipt_{order_number}.pdf')


def archive_receipts(input_folder,output_path):
    lib = Archive()
    lib.archive_folder_with_zip(input_folder,output_path)

def cleanup(folders):
    for folder in folders:
        rmtree(folder)

