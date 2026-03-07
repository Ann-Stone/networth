import csv
from datetime import datetime, timedelta, timezone
from flask import jsonify, request
from threading import Thread
import time
import requests
import urllib3
# from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import yfinance
import random
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from api.response_format import ResponseFormat

from app.dao.model.dashboard.fx_rate_model import FXRate
from app.dao.model.monthlyReport.journal_model import Journal
from app.dao.model.setting.credit_card_model import CreditCard
from app.dao.model.otherAsset.stock_journal_model import StockJournal
from app.dao.model.dashboard.stock_price_history_model import StockPriceHistory


def init_global_api(app):
    invoicePayload = {
        "appID": app.config['INVOICE_APP_ID'],
        "cardEncrypt": app.config['INVOICE_PASSWORD'],
        "cardNo": app.config['INVOICE_CARD_NO'],
    }

    @app.route("/global/server-alive")
    def serverAlive():
        return jsonify(ResponseFormat.true_return(ResponseFormat, True))

    @app.route("/global/check/<string:dataType>", methods=["POST"])
    def checkImportData(dataType):
        inputData = request.get_json(force=True)

        try:
            if dataType == "invoice":
                invoiceThread = Thread(
                    target=importInvoice, args=(inputData['period'], ))
                # 財政部已不支援自然人使用 API
                # Thread(
                #     target=importInvoiceFromNetwork, args=(inputData['period'], ))
                invoiceThread.start()
            elif dataType == 'stock':
                stockThread = Thread(
                    target=importStockPrice, args=(inputData['period'], ))
                stockThread.start()
            else:
                fxThread = Thread(target=importFxRate, args=(inputData['period'], ))
                fxThread.start()

            return jsonify(
                ResponseFormat.true_return(
                    ResponseFormat, None, f"{dataType} is importing..."
                )
            )

        except Exception as error:
            return jsonify(ResponseFormat.false_return(ResponseFormat, error))

    def importFxRate(period):
        with app.app_context():  # 因為新開 thread 但共用 db 所以需要指定
            datas = []

            # 取某月份最後一日
            import_date = datetime.today().date() if period == '' else datetime.strptime(
                        period, '%Y%m').replace(day=28) + timedelta(days=4)
            import_date = import_date if period == '' else import_date - \
                        timedelta(days=import_date.day)
            
            # print('123', period, int(import_date.timestamp()), f"https://mma.sinopac.com/ws/share/rate/ws_exchange.ashx?exchangeType=REMIT&_={import_date.timestamp()}")

            # 寫法一
            # response = requests.get(
            #     'https://openapi.taifex.com.tw/v1/DailyForeignExchangeRates')

            # fxRateList = response.json()
            # for rate in fxRateList:
            #     date = None
            #     usd = None  # 記錄USD/NTD，作為與台幣匯率換算的基礎
            #     for key in rate.keys():
            #         if key == 'Date':
            #             date = datetime.strptime(rate[key], "%Y%m%d")
            #         else:
            #             rawRate = key.split('/')
            #             value = float(rate[key])

            #             if rawRate[1] == 'NTD':
            #                 if rawRate[0] == 'USD':
            #                     usd = value

            #                 datas.append(
            #                     {'import_date': date, 'code': rawRate[0], 'buy_rate': value})
            #             elif rawRate[1] != 'RMB':  # RMB 已有 NTD 匯兌，所以要過濾
            #                 if rawRate[0] == 'USD':
            #                     datas.append(
            #                         {'import_date': date, 'code': rawRate[1], 'buy_rate': round(usd / value, 4)})
            #                 else:
            #                     datas.append(
            #                         {'import_date': date, 'code': rawRate[0], 'buy_rate': round(usd * value, 4)})

            response = requests.get(
                f"https://mma.sinopac.com/ws/share/rate/ws_exchange.ashx?exchangeType=REMIT&_={import_date.timestamp()}",
                verify=False
            )

            data = response.json()
            date = datetime.utcfromtimestamp(
                datetime.strptime(
                    data[0]["TitleInfo"].split("：", 1)[1].split("<br>", 1)[0],
                    "%Y-%m-%d %H:%M:%S",
                ).timestamp()
            )

            for rate in data[0]["SubInfo"]:
                hasRecorded = FXRate.queryByKey(
                    FXRate, date, rate["DataValue4"])

                if hasRecorded["recordNum"] == 0:
                    datas.append(
                        {
                            "import_date": date,
                            "code": rate["DataValue4"],
                            "buy_rate": rate["DataValue2"],
                        }
                    )

            if len(datas):
                FXRate.bulkInsert(FXRate, datas)

    # def importInvoiceFromNetwork(period):
    #     invoiceList = None
    #     invoicePayload
    #     datas = []
    #     today = datetime.today().date() if period == '' else datetime.strptime(
    #         period, '%Y%m').replace(day=28) + timedelta(days=4)

    #     today = today - timedelta(days=today.day)

    #     result = None

    #     try:
    #         invoicePayload["version"] = "0.5"
    #         invoicePayload["cardType"] = "3J0002"
    #         invoicePayload["action"] = "carrierInvChk"
    #         invoicePayload["onlyWinningInv"] = "N"
    #         invoicePayload["uuid"] = "123456"
    #         invoicePayload["expTimeStamp"] = invoicePayload["timeStamp"] = (
    #             int(datetime.now().timestamp()) + 100
    #         )
    #         invoicePayload["startDate"] = today.strftime("%Y/%m/01")
    #         invoicePayload["endDate"] = today.strftime("%Y/%m/%d")

    #         sessionInvoice = requests.Session()
            # sessionInvoice.mount('http://', HTTPAdapter(max_retries=3))
            # sessionInvoice.mount('https://', HTTPAdapter(max_retries=3))
    #         invoiceList = sessionInvoice.post(
    #             "https://api.einvoice.nat.gov.tw/PB2CAPIVAN/invServ/InvServ",
    #             params=invoicePayload,
    #             timeout=(30, 20),
    #         )

    #         if invoiceList.json()["code"] == 200:
    #             print('got all invoice list', len(
    #                 invoiceList.json()["details"]))
    #             data = {
    #                 "vesting_month": today.strftime("%Y%m"),
    #                 "action_main": "No",
    #                 "action_main_type": "No",
    #                 "action_main_table": "No",
    #                 "action_sub": "No",
    #                 "action_sub_type": "No",
    #                 "action_sub_table": "No",
    #                 "note": "",
    #             }

    #             with app.app_context():  # 因為新開 thread 但共用 db 所以需要指定
    #                 for invoice in invoiceList.json()["details"]:
    #                     hasRecorded = Journal.queryByVestingMonthAndInvoice(
    #                         Journal, data["vesting_month"], invoice["invNum"]
    #                     )

    #                     # 如果找不到相關資料才寫入
    #                     if hasRecorded is None:
    #                         data["spend_date"] = datetime.utcfromtimestamp(
    #                             int(invoice["invDate"]["time"] / 1000)
    #                         )  # 轉 UTC+0 DATE，参数要的长度是10位
    #                         data["invoice_number"] = invoice["invNum"]
    #                         data["spending"] = -int(invoice["amount"])

    #                         # 利用載具號碼找出相對應消費方式:
    #                         carrierNo = CreditCard.queryByCarrierNo(
    #                             CreditCard, invoice["cardNo"]
    #                         )
    #                         if carrierNo is None:
    #                             data["spend_way"] = "No"
    #                             data["spend_way_type"] = "No"
    #                             data["spend_way_table"] = "No"
    #                         else:
    #                             data["spend_way"] = carrierNo.id
    #                             data["spend_way_type"] = carrierNo.type
    #                             data["spend_way_table"] = carrierNo.table_name

    #                         # 取得發票消費明細
    #                         time.sleep(10)
    #                         invoicePayload["expTimeStamp"] = invoicePayload[
    #                             "timeStamp"
    #                         ] = (int(datetime.now().timestamp()) + 100)
    #                         invoicePayload["action"] = "carrierInvDetail"
    #                         invoicePayload["invNum"] = invoice["invNum"]
    #                         invoicePayload["invDate"] = datetime.fromtimestamp(
    #                             int(invoice["invDate"]["time"] / 1000)
    #                         ).strftime("%Y/%m/%d")
    #                         invoicePayload["amount"] = invoice["amount"]

    #                         invoiceDetail = sessionInvoice.post(
    #                             "https://api.einvoice.nat.gov.tw/PB2CAPIVAN/invServ/InvServ",
    #                             params=invoicePayload,
    #                             timeout=(30, 20),
    #                         )

    #                         if invoiceDetail.json()["code"] == 200:
    #                             print('one data: ', invoiceDetail)
    #                             for detail in invoiceDetail.json()["details"]:
    #                                 data[
    #                                     "note"
    #                                 ] = f"{data['note']}{detail['description']} {detail['amount']}, "

    #                             datas.append(Journal(data))
    #                             Journal.add(Journal, Journal(data))
    #                             data["note"] = ""

    #                 if len(datas):
    #                     print('added')
    #                     # Journal.bulkInsert(Journal, datas)
    #                 else:
    #                     print('done')

    #     except Exception as error:
    #         print('error: ', error)
    #         if len(datas):
    #             Journal.bulkInsert(Journal, datas)
    #         if invoiceList == None:
    #             # 如果出錯就重新執行，直到沒有錯誤為止
    #             time.sleep(30)
    #             importInvoice(period)
    #         else:
    #             print('finish')

    def importInvoice(period):
        invoiceList = None
        datas = []
        data = None
        isSkip = False
        # 資料變多再提出
        m_list = [{"name": '台灣之星', "main": '92', "main_type": 'Fixed', "main_table": 'Code', "sub": '100', "sub_type": 'Fixed', "sub_table": 'Code'},
                  {"name": '台灣大哥大', "main": '92',
                      "main_type": 'Fixed', "main_table": 'Code', "sub": '100', "sub_type": 'Fixed', "sub_table": 'Code'},
                  {"name": '台灣中油', "main": '4', "main_type": 'Floating', "main_table": 'Code', "sub": '32', "sub_type": 'Floating', "sub_table": 'Code'}]

        try:
            with app.app_context():  # 因為新開 thread 但共用 db 所以需要指定
                # 開啟 CSV 檔案
                with open('invoice.csv', newline='', encoding="utf-8") as csvfile:
                    # 讀取 CSV 檔案內容
                    rows = csv.reader(csvfile, delimiter='|')

                    for index, row in enumerate(rows):
                        # ['M', '載具名稱', '載具號碼', '發票日期', '商店統編', '商店店名', '發票號碼', '總金額', '發票狀態', '']
                        # ['D', '發票號碼', '小計', '品項名稱', '']
                        mode = row[0]
                        source = row[2]
                        invoiceMonth = row[3][:6] if mode == 'M' else ''
                        
                        if mode == 'M' or mode == 'D':
                            if mode == 'M':
                                # 每切換一次M，有資料就紀錄
                                if data is not None:
                                    datas.append(Journal(data))
                                    # Journal.add(Journal, Journal(data))
                                    data = None
                                
                                # 判斷該載具/該筆資料是否跳過
                                isSkip = True if source in app.config['INVOICE_SKIP'] or period != invoiceMonth else False
                                
                                if isSkip == False:
                                    found_values = [
                                        item for item in m_list if item.get('name', '') in row[5]]
                                    target = found_values[0] if found_values else None
                                    # 利用載具號碼找出相對應消費方式:
                                    carrierNo = CreditCard.queryByCarrierNo(
                                        CreditCard, row[2]
                                    )
                                    data = {
                                        "vesting_month": row[3][:6],
                                        "spend_way": carrierNo.id if carrierNo else "No",
                                        "spend_way_type": carrierNo.type if carrierNo else "No",
                                        "spend_way_table": carrierNo.table_name if carrierNo else "No",
                                        "action_main": target["main"] if target else "No",
                                        "action_main_type": target["main_type"] if target else "No",
                                        "action_main_table": target["main_table"] if target else "No",
                                        "action_sub": target["sub"] if target else "No",
                                        "action_sub_type": target["sub_type"] if target else "No",
                                        "action_sub_table": target["sub_table"] if target else "No",
                                        "spend_date": datetime.strptime(row[3], "%Y%m%d").replace(tzinfo=timezone.utc),
                                        "note": row[5],
                                        "invoice_number": row[6],
                                        "spending": int(row[7]) * -1
                                    }
                            else:
                                if isSkip == False:
                                    hasRecorded = Journal.queryByVestingMonthAndInvoice(
                                        Journal, data["vesting_month"], data["invoice_number"]
                                    )

                                    # 如果找不到相關資料才寫入
                                    if hasRecorded is None:
                                        # 發票消費明細
                                        data[
                                            "note"
                                        ] = f"{data['note']}\n{row[3]} {row[2]}, "
                                        
                    # 可能最後一筆是需要紀錄的
                    if data is not None:
                        datas.append(Journal(data))
                        # Journal.add(Journal, Journal(data))
                        data = None

                    if len(datas):
                        Journal.bulkInsert(Journal, datas)
                        print('added')
                    else:
                        print('done')
        except FileNotFoundError:
            print("invoice.csv was not found.")
        except Exception as error:
            print('error: ', error)

    def importStockPrice(period):
        with app.app_context():
            datas = []
            stockList = list(StockJournal.queryStockCodeList(StockJournal))  # 轉換為列表
            
            total_stocks = len(stockList)
            
            # 計算日期
            import_date = datetime.today().date() if period == '' else datetime.strptime(
                period, '%Y%m').replace(day=28) + timedelta(days=4)
            import_date = import_date if period == '' else import_date - timedelta(days=import_date.day)
            end_date = import_date + timedelta(days=1) - timedelta(seconds=1)
            
            for idx, stock in enumerate(stockList, 1):
                max_retries = 3  # 最多重試次數
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    try:
                        print(f"處理第 {idx}/{total_stocks} 支股票: {stock.stock_code}")
                        
                        stockData = yfinance.Ticker(
                            stock.stock_code + ".TW" if stock.vesting_nation == "TW" else stock.stock_code
                        )
                        
                        # 台股使用 period,美股使用日期範圍
                        if stock.vesting_nation == "TW":
                            stockPrice = stockData.history(period="1d")
                        else:
                            stockPrice = stockData.history(start=import_date, end=end_date)
                        
                        # 如果資料為空且有 previousClose,往前找
                        temp_import_date = import_date
                        attempts = 0
                        while (stockData.info.get('previousClose') is not None 
                            and stockPrice.empty 
                            and attempts < 5):  # 限制嘗試次數
                            temp_import_date = temp_import_date - timedelta(days=1)
                            stockPrice = stockData.history(start=temp_import_date, end=end_date)
                            attempts += 1
                        
                        if not stockPrice.empty:
                            fetch_date = datetime.utcfromtimestamp(
                                int(list(stockPrice["Close"].items())[0][0].timestamp())
                            )
                            
                            hasRecorded = StockPriceHistory.queryByKey(
                                StockPriceHistory, fetch_date, stock.stock_code
                            )
                            
                            if hasRecorded["recordNum"] == 0:
                                datas.append({
                                    "stock_code": stock.stock_code,
                                    "fetch_date": fetch_date,
                                    "open_price": list(stockPrice["Open"].items())[0][1],
                                    "highest_price": list(stockPrice["High"].items())[0][1],
                                    "lowest_price": list(stockPrice["Low"].items())[0][1],
                                    "close_price": list(stockPrice["Close"].items())[0][1],
                                })
                        
                        success = True
                        
                        # 每次請求後等待,避免觸發速率限制
                        # 基礎延遲 + 隨機抖動
                        base_delay = 1.5  # 基礎延遲秒數
                        jitter = random.uniform(0.5, 1.5)  # 隨機抖動
                        time.sleep(base_delay + jitter)
                        
                    except HTTPError as e:
                        if '429' in str(e) or 'Too Many Requests' in str(e):
                            retry_count += 1
                            delay = (2 ** retry_count) + random.uniform(1, 3)
                            print(f"股票 {stock.stock_code} 遇到速率限制 (重試 {retry_count}/{max_retries})，等待 {delay:.2f} 秒...")
                            time.sleep(delay)
                        elif '404' in str(e) or 'Not Found' in str(e):
                            # 404 錯誤表示股票代碼不存在，不需要重試
                            print(f"股票 {stock.stock_code} 不存在或已下市，跳過此股票")
                            break  # 直接跳出重試迴圈，處理下一支股票
                        else:
                            print(f"股票 {stock.stock_code} 發生 HTTP 錯誤: {e}")
                            break
                            
                    except Exception as error:
                        # 其他錯誤也可以考慮是否要重試
                        print(f"股票 {stock.stock_code} 發生錯誤: {error}")
                        if '404' in str(error) or 'Not Found' in str(error):
                            print(f"股票不存在，跳過")
                            break
                        
                        retry_count += 1
                        if retry_count < max_retries:
                            delay = 2 + random.uniform(0, 1)
                            print(f"等待 {delay:.2f} 秒後重試...")
                            time.sleep(delay)
                        else:
                            print(f"已達最大重試次數，跳過此股票")
                            break
                
                # 每處理 10 支股票,額外暫停一下
                if idx % 10 == 0:
                    print(f"已處理 {idx} 支股票,暫停 3 秒...")
                    time.sleep(3)
            
            # 批次寫入資料庫
            if len(datas):
                print(f"準備寫入 {len(datas)} 筆資料到資料庫")
                StockPriceHistory.bulkInsert(StockPriceHistory, datas)
            else:
                print("沒有新資料需要寫入")